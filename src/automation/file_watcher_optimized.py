#!/usr/bin/env python3
"""
Optimized File Watcher for AI Quality Assurance Auto-Documentation System.
Implements performance improvements recommended by Sourcery AI.
"""

import os
import sys
import time
import threading
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class OptimizedEventHandler(FileSystemEventHandler):
    """Optimized event handler with better performance."""
    
    def __init__(self, doc_generator, config: Dict[str, Any]):
        self.doc_generator = doc_generator
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Performance optimizations
        self._last_update = {}
        self._update_lock = threading.Lock()
        self._debounce_time = config.get('debounce_time', 2.0)
        
        # File filters
        self.watch_extensions = config.get('watch_extensions', ['.py', '.md', '.txt', '.yaml', '.yml'])
        self.ignore_patterns = config.get('ignore_patterns', ['__pycache__', '.git', '.pytest_cache', 'node_modules'])
    
    def _should_process_file(self, file_path: str) -> bool:
        """Determine if file should be processed."""
        path = Path(file_path)
        
        # Check extension
        if path.suffix not in self.watch_extensions:
            return False
        
        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if pattern in str(path):
                return False
        
        return True
    
    def _is_debounced(self, file_path: str) -> bool:
        """Check if file change should be debounced."""
        with self._update_lock:
            now = time.time()
            last_time = self._last_update.get(file_path, 0)
            
            if now - last_time < self._debounce_time:
                return True
            
            self._last_update[file_path] = now
            return False
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            if not self._is_debounced(event.src_path):
                self._handle_file_change(event.src_path, 'modified')
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and self._should_process_file(event.src_path):
            self._handle_file_change(event.src_path, 'created')
    
    def _handle_file_change(self, file_path: str, event_type: str):
        """Handle file changes asynchronously."""
        self.logger.info(f"File {event_type}: {file_path}")
        
        # Run documentation update in background thread
        def update_docs():
            try:
                asyncio.run(self._update_documentation(file_path))
            except Exception as e:
                self.logger.error(f"Error updating documentation for {file_path}: {e}")
        
        thread = threading.Thread(target=update_docs, daemon=True)
        thread.start()
    
    async def _update_documentation(self, file_path: str):
        """Update documentation based on file changes."""
        try:
            if hasattr(self.doc_generator, 'update_all_docs'):
                await self.doc_generator.update_all_docs()
            else:
                # Fallback to individual updates
                tasks = []
                if hasattr(self.doc_generator, 'update_readme'):
                    tasks.append(self.doc_generator.update_readme())
                if hasattr(self.doc_generator, 'update_changelog'):
                    tasks.append(self.doc_generator.update_changelog())
                
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    
        except Exception as e:
            self.logger.error(f"Documentation update failed: {e}")


class OptimizedAutoDocsWatcher:
    """Optimized auto-documentation watcher with better resource management."""
    
    def __init__(self, project_root: Path, config: Optional[Dict[str, Any]] = None):
        self.project_root = Path(project_root)
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Threading components
        self._stop_event = threading.Event()
        self._observer = None
        self._event_handler = None
        
        # Initialize documentation generator
        self._init_doc_generator()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the watcher."""
        return {
            'watch_extensions': ['.py', '.md', '.txt', '.yaml', '.yml', '.json'],
            'ignore_patterns': ['__pycache__', '.git', '.pytest_cache', 'node_modules', 'logs'],
            'debounce_time': 2.0,
            'documentation': {
                'auto_commit': False,
                'auto_push': False
            }
        }
    
    def _init_doc_generator(self):
        """Initialize documentation generator."""
        try:
            from src.automation.doc_generator import DocumentationGenerator
            self.doc_generator = DocumentationGenerator(
                self.project_root,
                self.config.get('documentation', {})
            )
            self.logger.info("Documentation generator initialized")
        except ImportError as e:
            self.logger.error(f"Failed to import DocumentationGenerator: {e}")
            self.doc_generator = None
    
    def start(self) -> bool:
        """Start the file watcher."""
        if not self.doc_generator:
            self.logger.error("Cannot start watcher - no documentation generator")
            return False
        
        try:
            # Clear stop event
            self._stop_event.clear()
            
            # Initialize observer and event handler
            self._observer = Observer()
            self._event_handler = OptimizedEventHandler(self.doc_generator, self.config)
            
            # Schedule watching for project directory
            self._observer.schedule(
                self._event_handler,
                str(self.project_root),
                recursive=True
            )
            
            # Start observer
            self._observer.start()
            
            self.logger.info(f"Started watching: {self.project_root}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start watcher: {e}")
            return False
    
    def stop(self):
        """Stop the file watcher."""
        self.logger.info("Stopping file watcher...")
        
        # Signal stop
        self._stop_event.set()
        
        # Stop observer
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5.0)
            self._observer = None
        
        self.logger.info("File watcher stopped")
    
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._observer is not None and self._observer.is_alive()
    
    def wait_for_stop(self, timeout: Optional[float] = None):
        """
        Wait for stop signal efficiently.
        
        This replaces the inefficient time.sleep(1) loop with an event-based approach.
        """
        self._stop_event.wait(timeout)


class WatcherManager:
    """Manager for multiple watcher instances."""
    
    def __init__(self):
        self.watchers: Dict[str, OptimizedAutoDocsWatcher] = {}
        self.logger = logging.getLogger(__name__)
    
    def add_watcher(self, name: str, project_path: Path, config: Optional[Dict[str, Any]] = None) -> bool:
        """Add a new watcher instance."""
        try:
            watcher = OptimizedAutoDocsWatcher(project_path, config)
            if watcher.start():
                self.watchers[name] = watcher
                self.logger.info(f"Added watcher '{name}' for {project_path}")
                return True
            else:
                self.logger.error(f"Failed to start watcher '{name}'")
                return False
        except Exception as e:
            self.logger.error(f"Error adding watcher '{name}': {e}")
            return False
    
    def remove_watcher(self, name: str) -> bool:
        """Remove a watcher instance."""
        if name in self.watchers:
            self.watchers[name].stop()
            del self.watchers[name]
            self.logger.info(f"Removed watcher '{name}'")
            return True
        return False
    
    def stop_all(self):
        """Stop all watchers."""
        for name in list(self.watchers.keys()):
            self.remove_watcher(name)
    
    def get_status(self) -> Dict[str, bool]:
        """Get status of all watchers."""
        return {name: watcher.is_running() for name, watcher in self.watchers.items()}


def create_optimized_auto_docs_watcher(project_path: str, config: Optional[Dict[str, Any]] = None) -> OptimizedAutoDocsWatcher:
    """Factory function to create an optimized auto-docs watcher."""
    return OptimizedAutoDocsWatcher(Path(project_path), config)


def main():
    """
    Main function with optimized event handling.
    
    This version eliminates the inefficient time.sleep(1) loop identified by Sourcery AI.
    """
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
    
    logger = logging.getLogger(__name__)
    
    # Create and start watcher
    watcher = create_optimized_auto_docs_watcher(project_path)
    
    try:
        if watcher.start():
            logger.info(f"Optimized AutoDocsWatcher started for project: {project_path}")
            print(f"Optimized AutoDocsWatcher started for project: {project_path}")
            print("Press Ctrl+C to stop...")
            
            # OPTIMIZATION: Replace inefficient time.sleep(1) loop with event-based waiting
            # This addresses the Sourcery AI recommendation about unnecessary time.sleep()
            watcher.wait_for_stop()
            
        else:
            logger.error("Failed to start OptimizedAutoDocsWatcher")
            print("Failed to start OptimizedAutoDocsWatcher")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nStopping OptimizedAutoDocsWatcher...")
        logger.info("Received interrupt signal")
        watcher.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        watcher.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()