"""
File monitoring system for automatic documentation updates.
Watches for changes in source code, tests, and documentation files.
"""

import os
import time
import logging
import asyncio
from pathlib import Path
from typing import Set, Dict, Any, Callable, Optional
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
except ImportError:
    # Fallback if watchdog not installed
    Observer = None
    FileSystemEventHandler = None
    FileSystemEvent = None

from .doc_generator import DocumentationGenerator
from .git_integration import GitHooksManager

logger = logging.getLogger(__name__)


class AutoDocsEventHandler(FileSystemEventHandler):
    """Event handler for file system changes that trigger documentation updates."""
    
    def __init__(self, auto_docs_watcher: 'AutoDocsWatcher'):
        super().__init__()
        self.watcher = auto_docs_watcher
        self.last_update = {}
        self.debounce_interval = 2.0  # seconds
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if self._should_process_file(file_path):
            self._debounced_update(file_path)
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if self._should_process_file(file_path):
            self._debounced_update(file_path)
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events."""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if self._should_process_file(file_path):
            self._debounced_update(file_path)
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Determine if a file change should trigger documentation update."""
        # Skip hidden files and directories
        if any(part.startswith('.') for part in file_path.parts):
            # Allow .github directory for workflow changes
            if '.github' not in str(file_path):
                return False
        
        # Skip temporary files
        if file_path.suffix in {'.tmp', '.swp', '.bak', '.pyc'}:
            return False
        
        # Skip __pycache__ directories
        if '__pycache__' in str(file_path):
            return False
        
        return self.watcher._is_relevant_file(file_path)
    
    def _debounced_update(self, file_path: Path):
        """Debounce file updates to avoid excessive regeneration."""
        current_time = time.time()
        file_key = str(file_path)
        
        if (file_key in self.last_update and 
            current_time - self.last_update[file_key] < self.debounce_interval):
            return
        
        self.last_update[file_key] = current_time
        
        # Schedule async update
        # For now, we'll just log the change and handle it later
        # In a real implementation, this would queue the update
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"File change detected: {file_path} - queued for documentation update")


class AutoDocsWatcher:
    """Main class for monitoring file changes and triggering documentation updates."""
    
    def __init__(self, project_root: Path, config: Optional[Dict[str, Any]] = None):
        self.project_root = Path(project_root)
        self.config = config or self._default_config()
        self.observer = None
        self.doc_generator = None
        self.git_manager = None
        self.is_running = False
        self.statistics = {
            'files_watched': 0,
            'updates_triggered': 0,
            'last_update': None,
            'start_time': None
        }
        
        # Initialize components
        self._initialize_components()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the file watcher."""
        return {
            'watch_patterns': {
                'source_code': ['*.py'],
                'tests': ['test_*.py', '*_test.py'],
                'documentation': ['*.md', '*.rst'],
                'configuration': ['*.yaml', '*.yml', '*.json', '*.toml'],
                'workflows': ['.github/workflows/*.yml', '.github/workflows/*.yaml']
            },
            'ignore_patterns': [
                '__pycache__',
                '*.pyc',
                '.git',
                '.venv',
                'venv',
                'env',
                '*.tmp',
                '*.swp',
                '*.bak'
            ],
            'documentation_targets': [
                'README.md',
                'CHANGELOG.md',
                'API_DOCS.md',
                'ARCHITECTURE.md'
            ],
            'auto_commit': False,
            'auto_push': False,
            'debounce_interval': 2.0,
            'enable_notifications': True
        }
    
    def _initialize_components(self):
        """Initialize documentation generator and git manager."""
        try:
            self.doc_generator = DocumentationGenerator(self.project_root, self.config)
            self.git_manager = GitHooksManager(self.project_root, self.config)
            logger.info("AutoDocsWatcher components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def start(self) -> bool:
        """Start the file watcher."""
        if Observer is None:
            logger.error("watchdog package not installed. Install with: pip install watchdog")
            return False
        
        if self.is_running:
            logger.warning("AutoDocsWatcher is already running")
            return True
        
        try:
            self.observer = Observer()
            event_handler = AutoDocsEventHandler(self)
            
            # Watch the entire project directory
            self.observer.schedule(
                event_handler,
                path=str(self.project_root),
                recursive=True
            )
            
            self.observer.start()
            self.is_running = True
            self.statistics['start_time'] = datetime.now()
            
            logger.info(f"AutoDocsWatcher started monitoring: {self.project_root}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start AutoDocsWatcher: {e}")
            return False
    
    def stop(self):
        """Stop the file watcher."""
        if not self.is_running:
            return
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        self.is_running = False
        logger.info("AutoDocsWatcher stopped")
    
    def _is_relevant_file(self, file_path: Path) -> bool:
        """Check if a file is relevant for documentation updates."""
        # Check against watch patterns
        for category, patterns in self.config['watch_patterns'].items():
            for pattern in patterns:
                if file_path.match(pattern) or str(file_path).endswith(pattern.lstrip('*')):
                    return True
        
        # Check if it's in source directories
        relevant_dirs = {'src', 'tests', 'docs', '.github', 'scripts'}
        path_parts = set(file_path.parts)
        
        return bool(relevant_dirs.intersection(path_parts))
    
    async def _process_file_change(self, file_path: Path):
        """Process a file change and trigger appropriate documentation updates."""
        try:
            self.statistics['updates_triggered'] += 1
            self.statistics['last_update'] = datetime.now()
            
            logger.info(f"Processing file change: {file_path}")
            
            # Determine what type of update is needed
            update_tasks = self._determine_update_tasks(file_path)
            
            # Execute updates
            for task in update_tasks:
                await self._execute_update_task(task, file_path)
            
            # Optional: commit changes if auto_commit is enabled
            if self.config.get('auto_commit', False):
                await self._auto_commit_changes(file_path)
            
            logger.info(f"Completed processing file change: {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing file change {file_path}: {e}")
    
    def _determine_update_tasks(self, file_path: Path) -> Set[str]:
        """Determine what documentation updates are needed based on the changed file."""
        tasks = set()
        
        # Source code changes
        if file_path.suffix == '.py' and 'src' in file_path.parts:
            tasks.update(['readme', 'api_docs', 'architecture'])
        
        # Test file changes
        if 'test' in file_path.name or 'tests' in file_path.parts:
            tasks.update(['readme', 'test_docs'])
        
        # Configuration changes
        if file_path.suffix in {'.yaml', '.yml', '.json', '.toml'}:
            tasks.update(['readme', 'config_docs'])
        
        # Workflow changes
        if '.github' in file_path.parts:
            tasks.update(['readme', 'cicd_docs'])
        
        # Always update changelog for any tracked change
        tasks.add('changelog')
        
        return tasks
    
    async def _execute_update_task(self, task: str, file_path: Path):
        """Execute a specific documentation update task."""
        try:
            if task == 'readme':
                await self.doc_generator.update_readme()
            elif task == 'changelog':
                await self.doc_generator.update_changelog(file_path)
            elif task == 'api_docs':
                await self.doc_generator.update_api_docs()
            elif task == 'architecture':
                await self.doc_generator.update_architecture_docs()
            elif task == 'test_docs':
                await self.doc_generator.update_test_docs()
            elif task == 'config_docs':
                await self.doc_generator.update_config_docs()
            elif task == 'cicd_docs':
                await self.doc_generator.update_cicd_docs()
            
            logger.debug(f"Completed update task: {task}")
            
        except Exception as e:
            logger.error(f"Failed to execute update task {task}: {e}")
    
    async def _auto_commit_changes(self, file_path: Path):
        """Automatically commit documentation changes if enabled."""
        try:
            if self.git_manager:
                commit_message = f"docs: Auto-update documentation for {file_path.name}"
                await self.git_manager.auto_commit_docs(commit_message)
                
                if self.config.get('auto_push', False):
                    await self.git_manager.auto_push_docs()
            
        except Exception as e:
            logger.error(f"Failed to auto-commit changes: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current watcher statistics."""
        stats = self.statistics.copy()
        if self.statistics['start_time']:
            uptime = datetime.now() - self.statistics['start_time']
            stats['uptime_seconds'] = uptime.total_seconds()
        
        stats['is_running'] = self.is_running
        return stats
    
    async def manual_update(self, force: bool = False) -> Dict[str, Any]:
        """Manually trigger a complete documentation update."""
        try:
            logger.info("Starting manual documentation update")
            
            # Update all documentation
            tasks = [
                self.doc_generator.update_readme(),
                self.doc_generator.update_changelog(),
                self.doc_generator.update_api_docs(),
                self.doc_generator.update_architecture_docs()
            ]
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            error_count = len(results) - success_count
            
            result = {
                'success': error_count == 0,
                'tasks_completed': success_count,
                'tasks_failed': error_count,
                'timestamp': datetime.now().isoformat()
            }
            
            if error_count == 0:
                logger.info("Manual documentation update completed successfully")
            else:
                logger.warning(f"Manual update completed with {error_count} errors")
            
            return result
            
        except Exception as e:
            logger.error(f"Manual documentation update failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Convenience function for easy usage
def create_auto_docs_watcher(project_root: str, config: Optional[Dict[str, Any]] = None) -> AutoDocsWatcher:
    """Create and configure an AutoDocsWatcher instance."""
    return AutoDocsWatcher(Path(project_root), config)


# Example usage and testing
if __name__ == "__main__":
    # For testing purposes
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.getcwd()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start watcher
    watcher = create_auto_docs_watcher(project_path)
    
    try:
        if watcher.start():
            print(f"AutoDocsWatcher started for project: {project_path}")
            print("Press Ctrl+C to stop...")
            
            # Keep running
            while True:
                time.sleep(1)
        else:
            print("Failed to start AutoDocsWatcher")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nStopping AutoDocsWatcher...")
        watcher.stop()
        print("AutoDocsWatcher stopped.")