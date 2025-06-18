"""
Documentation orchestrator - coordinates all documentation generation components.
This replaces the monolithic DocumentationGenerator with a modular, focused approach.
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .project_analyzer import ProjectAnalyzer, ProjectMetrics
from .readme_generator import ReadmeGenerator, ReadmeValidator
from .changelog_generator import ChangelogGenerator, VersionManager, ChangelogValidator
from .subagetic_orchestrator import enhance_documentation_with_subagetic

logger = logging.getLogger(__name__)


class DocumentationOrchestrator:
    """
    Orchestrates all documentation generation activities.
    
    This class replaces the monolithic DocumentationGenerator and implements
    the separation of concerns recommended by Sourcery AI.
    """
    
    def __init__(self, project_root: Path, config: Optional[Dict[str, Any]] = None):
        self.project_root = Path(project_root)
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize modular components
        self._init_components()
        
        # Track documentation state
        self.last_update = None
        self.generation_stats = {
            'total_updates': 0,
            'successful_updates': 0,
            'failed_updates': 0,
            'last_error': None
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for documentation orchestrator."""
        return {
            'project_name': 'AI Quality Assurance System',
            'project_description': 'Real AI-powered code analysis for quality assurance',
            'author': 'Aulus Diniz',
            'license': 'MIT',
            'python_version': '3.11+',
            'documentation_types': ['readme', 'changelog', 'api_docs', 'architecture'],
            'auto_validate': True,
            'auto_commit': False,
            'quality_threshold': 80,
            'readme_template': 'ai_project',
            'changelog_format': 'keepachangelog'
        }
    
    def _init_components(self):
        """Initialize all documentation generation components."""
        try:
            # Core analysis component
            self.project_analyzer = ProjectAnalyzer(self.project_root)
            self.logger.info("Project analyzer initialized")
            
            # Generator components
            self.readme_generator = ReadmeGenerator(self.project_root, self.config)
            self.changelog_generator = ChangelogGenerator(self.project_root, self.config)
            self.logger.info("Documentation generators initialized")
            
            # Validator components
            if self.config.get('auto_validate', True):
                self.readme_validator = ReadmeValidator()
                self.changelog_validator = ChangelogValidator()
                self.logger.info("Documentation validators initialized")
            
            # Version management
            self.version_manager = VersionManager(self.project_root)
            self.logger.info("Version manager initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            raise
    
    async def update_all_documentation(self, force: bool = False, use_subagetic: bool = True) -> Dict[str, bool]:
        """
        Update all documentation types with optional subagetic enhancement.
        
        Args:
            force: Force update even if no changes detected
            use_subagetic: Use subagetic multi-agent system for enhanced quality
            
        Returns:
            Dictionary with update results for each documentation type
        """
        if use_subagetic:
            self.logger.info("🤖 Starting documentation update with Subagetic Multi-Agent System")
            subagetic_result = await enhance_documentation_with_subagetic(
                self.project_root, 
                "Comprehensive documentation update with quality assurance"
            )
            self.logger.info(f"Subagetic quality score: {subagetic_result.get('overall_quality', 0.0):.2f}")
        else:
            self.logger.info("Starting comprehensive documentation update")
        
        start_time = datetime.now()
        results = {}
        
        try:
            # Analyze project first
            project_info = await self._analyze_project()
            self.logger.info(f"Project analysis completed - {len(project_info.get('src_files', []))} files analyzed")
            
            # Get documentation types to update
            doc_types = self.config.get('documentation_types', ['readme', 'changelog'])
            
            # Create update tasks
            tasks = []
            for doc_type in doc_types:
                task = self._create_update_task(doc_type, project_info, force)
                tasks.append((doc_type, task))
            
            # Execute all updates concurrently
            task_results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            # Process results
            for (doc_type, _), result in zip(tasks, task_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error updating {doc_type}: {result}")
                    results[doc_type] = False
                    self.generation_stats['failed_updates'] += 1
                else:
                    results[doc_type] = result
                    if result:
                        self.generation_stats['successful_updates'] += 1
                    else:
                        self.generation_stats['failed_updates'] += 1
            
            # Update statistics
            self.generation_stats['total_updates'] += 1
            self.last_update = datetime.now()
            
            duration = (self.last_update - start_time).total_seconds()
            success_count = sum(1 for r in results.values() if r)
            
            self.logger.info(f"Documentation update completed in {duration:.2f}s - {success_count}/{len(results)} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error during documentation update: {e}")
            self.generation_stats['failed_updates'] += 1
            self.generation_stats['last_error'] = str(e)
            return {doc_type: False for doc_type in self.config.get('documentation_types', [])}
    
    async def _analyze_project(self) -> Dict[str, Any]:
        """Analyze project and return comprehensive information."""
        try:
            # Run project analysis
            loop = asyncio.get_event_loop()
            project_info = await loop.run_in_executor(
                None, 
                self.project_analyzer.analyze_project
            )
            
            # Calculate metrics
            metrics = ProjectMetrics(project_info)
            project_info['metrics'] = metrics.calculate_complexity_metrics()
            
            # Add version information
            current_version = self.version_manager.get_current_version()
            project_info['version'] = current_version
            
            return project_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing project: {e}")
            return {}
    
    def _create_update_task(self, doc_type: str, project_info: Dict[str, Any], force: bool):
        """Create update task for specific documentation type."""
        if doc_type == 'readme':
            return self._update_readme(project_info, force)
        elif doc_type == 'changelog':
            return self._update_changelog(project_info, force)
        elif doc_type == 'api_docs':
            return self._update_api_docs(project_info, force)
        elif doc_type == 'architecture':
            return self._update_architecture_docs(project_info, force)
        else:
            self.logger.warning(f"Unknown documentation type: {doc_type}")
            return self._dummy_task(False)
    
    async def _update_readme(self, project_info: Dict[str, Any], force: bool = False) -> bool:
        """Update README.md file."""
        try:
            self.logger.info("Generating README.md content")
            
            # Generate README content
            readme_content = await self.readme_generator.generate_readme(project_info)
            
            # Validate content if enabled
            if self.config.get('auto_validate', True):
                validation = self.readme_validator.validate_readme(readme_content)
                
                if not validation['is_valid'] and not force:
                    self.logger.warning(f"README validation failed: {validation['missing_required']}")
                    return False
                
                if validation['score'] < self.config.get('quality_threshold', 80):
                    self.logger.warning(f"README quality score: {validation['score']}%")
            
            # Write README file
            readme_path = self.project_root / 'README.md'
            
            # Check if update is needed
            if not force and readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                if self._content_similar(existing_content, readme_content):
                    self.logger.info("README.md - no significant changes detected")
                    return True
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            self.logger.info(f"README.md updated successfully ({len(readme_content)} characters)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating README: {e}")
            return False
    
    async def _update_changelog(self, project_info: Dict[str, Any], force: bool = False) -> bool:
        """Update CHANGELOG.md file."""
        try:
            self.logger.info("Generating CHANGELOG.md content")
            
            # Get version information
            version_info = {}  # Could be populated from git history
            
            # Generate changelog content
            changelog_content = await self.changelog_generator.generate_changelog(
                project_info, 
                version_info
            )
            
            # Validate content if enabled
            if self.config.get('auto_validate', True):
                validation = self.changelog_validator.validate_changelog(changelog_content)
                
                if not validation['is_valid'] and not force:
                    self.logger.warning(f"Changelog validation failed: {validation['issues']}")
                    return False
            
            # Write CHANGELOG file
            changelog_path = self.project_root / 'CHANGELOG.md'
            
            # Check if update is needed
            if not force and changelog_path.exists():
                with open(changelog_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
                
                if self._content_similar(existing_content, changelog_content):
                    self.logger.info("CHANGELOG.md - no significant changes detected")
                    return True
            
            with open(changelog_path, 'w', encoding='utf-8') as f:
                f.write(changelog_content)
            
            self.logger.info(f"CHANGELOG.md updated successfully ({len(changelog_content)} characters)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating CHANGELOG: {e}")
            return False
    
    async def _update_api_docs(self, project_info: Dict[str, Any], force: bool = False) -> bool:
        """Update API documentation."""
        try:
            self.logger.info("Generating API documentation")
            
            api_endpoints = project_info.get('api_endpoints', [])
            mcp_tools = project_info.get('mcp_tools', [])
            
            if not api_endpoints and not mcp_tools:
                self.logger.info("No API endpoints or MCP tools found - skipping API docs")
                return True
            
            # Generate API documentation content
            api_content = self._generate_api_docs_content(api_endpoints, mcp_tools)
            
            # Write API documentation
            api_docs_path = self.project_root / 'API_DOCS.md'
            with open(api_docs_path, 'w', encoding='utf-8') as f:
                f.write(api_content)
            
            self.logger.info(f"API_DOCS.md updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating API docs: {e}")
            return False
    
    async def _update_architecture_docs(self, project_info: Dict[str, Any], force: bool = False) -> bool:
        """Update architecture documentation."""
        try:
            self.logger.info("Generating architecture documentation")
            
            # Generate architecture documentation
            arch_content = self._generate_architecture_content(project_info)
            
            # Write architecture documentation
            arch_path = self.project_root / 'ARCHITECTURE.md'
            with open(arch_path, 'w', encoding='utf-8') as f:
                f.write(arch_content)
            
            self.logger.info("ARCHITECTURE.md updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating architecture docs: {e}")
            return False
    
    def _generate_api_docs_content(self, api_endpoints: List[Dict], mcp_tools: List[Dict]) -> str:
        """Generate API documentation content."""
        content = """# API Documentation

## REST API Endpoints

"""
        
        if api_endpoints:
            for endpoint in api_endpoints:
                content += f"### {endpoint['method']} {endpoint['path']}\n\n"
                content += f"**Function:** `{endpoint['function']}`\n\n"
                content += "**Description:** Auto-generated API endpoint\n\n"
        else:
            content += "No REST API endpoints found.\n\n"
        
        content += "## MCP Tools\n\n"
        
        if mcp_tools:
            for tool in mcp_tools:
                content += f"### {tool['name']}\n\n"
                content += f"**Description:** {tool['description']}\n\n"
        else:
            content += "No MCP tools found.\n\n"
        
        content += f"""
---

*Documentation generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return content
    
    def _generate_architecture_content(self, project_info: Dict[str, Any]) -> str:
        """Generate architecture documentation content."""
        total_files = len(project_info.get('src_files', []))
        total_classes = project_info.get('total_classes', 0)
        
        return f"""# Architecture Documentation

## Project Overview

This project follows a modular architecture with clear separation of concerns.

## Structure

- **Total Files:** {total_files}
- **Total Classes:** {total_classes}
- **Total Functions:** {project_info.get('total_functions', 0)}

## Key Components

### Source Code Organization
```
src/
├── domain/           # Business logic and entities
├── application/      # Use cases and application services  
├── infrastructure/   # External concerns and adapters
└── automation/       # Documentation automation system
```

### Documentation Generation
- **Modular Design:** Separate components for each doc type
- **Async Processing:** Concurrent generation of multiple docs
- **Validation:** Automatic quality checking
- **Orchestration:** Coordinated updates across all documentation

## Design Patterns

- **Clean Architecture:** Separation of concerns across layers
- **Factory Pattern:** Component initialization and configuration
- **Strategy Pattern:** Different generators for different doc types
- **Observer Pattern:** File watching and change detection

---

*Architecture documentation generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def _content_similar(self, content1: str, content2: str, similarity_threshold: float = 0.95) -> bool:
        """Check if two content strings are similar enough to skip update."""
        # Simple similarity check - in production, could use more sophisticated comparison
        if len(content1) == 0 or len(content2) == 0:
            return False
        
        # Remove timestamps and dynamic content for comparison
        clean1 = self._clean_content_for_comparison(content1)
        clean2 = self._clean_content_for_comparison(content2)
        
        # Calculate simple similarity ratio
        if len(clean1) == 0 and len(clean2) == 0:
            return True
        
        max_len = max(len(clean1), len(clean2))
        min_len = min(len(clean1), len(clean2))
        
        similarity = min_len / max_len if max_len > 0 else 0
        
        return similarity >= similarity_threshold
    
    def _clean_content_for_comparison(self, content: str) -> str:
        """Clean content for similarity comparison."""
        import re
        
        # Remove timestamps
        content = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '', content)
        
        # Remove dynamic numbers that change frequently
        content = re.sub(r'\b\d+\b', '', content)
        
        # Remove extra whitespace
        content = ' '.join(content.split())
        
        return content
    
    async def _dummy_task(self, result: bool) -> bool:
        """Dummy task for unknown documentation types."""
        await asyncio.sleep(0.1)  # Simulate async work
        return result
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get documentation generation statistics."""
        return {
            **self.generation_stats,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'success_rate': (
                self.generation_stats['successful_updates'] / 
                max(1, self.generation_stats['total_updates'])
            ) * 100
        }
    
    async def validate_all_documentation(self) -> Dict[str, Dict[str, Any]]:
        """Validate all existing documentation files."""
        validation_results = {}
        
        # Validate README
        readme_path = self.project_root / 'README.md'
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            validation_results['readme'] = self.readme_validator.validate_readme(readme_content)
        
        # Validate CHANGELOG
        changelog_path = self.project_root / 'CHANGELOG.md'
        if changelog_path.exists():
            with open(changelog_path, 'r', encoding='utf-8') as f:
                changelog_content = f.read()
            validation_results['changelog'] = self.changelog_validator.validate_changelog(changelog_content)
        
        return validation_results


class DocumentationScheduler:
    """Schedules and manages periodic documentation updates."""
    
    def __init__(self, orchestrator: DocumentationOrchestrator):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(__name__)
        self._scheduled_tasks = []
        self._running = False
    
    async def schedule_periodic_updates(self, interval_seconds: int = 300):
        """Schedule periodic documentation updates."""
        self._running = True
        
        while self._running:
            try:
                await asyncio.sleep(interval_seconds)
                
                if self._running:
                    self.logger.info("Running scheduled documentation update")
                    await self.orchestrator.update_all_documentation()
                    
            except Exception as e:
                self.logger.error(f"Error in scheduled update: {e}")
    
    def stop_scheduling(self):
        """Stop periodic updates."""
        self._running = False
        self.logger.info("Documentation scheduling stopped")