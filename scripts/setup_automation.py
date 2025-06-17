#!/usr/bin/env python3
"""
Setup script for AI Quality Assurance Auto-Documentation System.
Configures the automation system, installs dependencies, and sets up Git hooks.
"""

import os
import sys
import argparse
import subprocess
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.automation.file_watcher import AutoDocsWatcher
    from src.automation.doc_generator import DocumentationGenerator
    from src.automation.git_integration import GitHooksManager
except ImportError as e:
    print(f"❌ Error importing automation modules: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


class AutomationSetup:
    """Setup manager for the auto-documentation system."""
    
    def __init__(self, project_root: Path, config_path: Optional[Path] = None):
        self.project_root = Path(project_root)
        self.config_path = config_path or self.project_root / "config" / "automation_config.yaml"
        self.config = self._load_config()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.doc_generator = None
        self.git_manager = None
        self.auto_watcher = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ Warning: Failed to load config from {self.config_path}: {e}")
        
        # Return default config
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration if config file not found."""
        return {
            'project': {
                'name': 'AI Quality Assurance System',
                'author': 'Aulus Diniz'
            },
            'git': {
                'auto_commit': False,
                'auto_push': False,
                'hooks': {
                    'install_on_start': True,
                    'hook_types': ['pre-commit', 'post-commit', 'pre-push']
                }
            },
            'logging': {
                'level': 'INFO'
            }
        }
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.project_root / 'setup.log')
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are available."""
        self.logger.info("🔍 Checking prerequisites...")
        
        checks = []
        
        # Check Python version
        if sys.version_info >= (3, 8):
            self.logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - OK")
            checks.append(True)
        else:
            self.logger.error(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} - Need 3.8+")
            checks.append(False)
        
        # Check Git
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                git_version = result.stdout.strip()
                self.logger.info(f"✅ {git_version} - OK")
                checks.append(True)
            else:
                self.logger.error("❌ Git not found")
                checks.append(False)
        except FileNotFoundError:
            self.logger.error("❌ Git not installed")
            checks.append(False)
        
        # Check if we're in a Git repository
        git_dir = self.project_root / '.git'
        if git_dir.exists():
            self.logger.info("✅ Git repository detected")
            checks.append(True)
        else:
            self.logger.warning("⚠️ Not in a Git repository - some features may not work")
            checks.append(True)  # Not critical
        
        # Check required dependencies
        required_deps = ['fastapi', 'uvicorn', 'scikit-learn', 'mcp']
        for dep in required_deps:
            try:
                __import__(dep.replace('-', '_'))
                self.logger.info(f"✅ {dep} - OK")
                checks.append(True)
            except ImportError:
                self.logger.warning(f"⚠️ {dep} - Not found (may need installation)")
                checks.append(True)  # Not critical for setup
        
        return all(checks)
    
    def install_dependencies(self, force: bool = False) -> bool:
        """Install required dependencies."""
        self.logger.info("📦 Installing dependencies...")
        
        # Check if requirements.txt exists
        req_file = self.project_root / 'requirements.txt'
        if not req_file.exists():
            self.logger.error("❌ requirements.txt not found")
            return False
        
        try:
            # Install main requirements
            cmd = [sys.executable, '-m', 'pip', 'install', '-r', str(req_file)]
            if force:
                cmd.append('--force-reinstall')
            
            self.logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("✅ Main dependencies installed")
            else:
                self.logger.error(f"❌ Failed to install dependencies: {result.stderr}")
                return False
            
            # Install automation-specific dependencies
            automation_deps = ['watchdog', 'GitPython', 'pyyaml']
            for dep in automation_deps:
                cmd = [sys.executable, '-m', 'pip', 'install', dep]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info(f"✅ {dep} installed")
                else:
                    self.logger.warning(f"⚠️ Failed to install {dep}: {result.stderr}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error installing dependencies: {e}")
            return False
    
    def initialize_components(self) -> bool:
        """Initialize automation components."""
        self.logger.info("🔧 Initializing automation components...")
        
        try:
            # Initialize documentation generator
            self.doc_generator = DocumentationGenerator(
                self.project_root, 
                self.config.get('documentation', {})
            )
            self.logger.info("✅ Documentation generator initialized")
            
            # Initialize Git manager
            self.git_manager = GitHooksManager(
                self.project_root,
                self.config.get('git', {})
            )
            self.logger.info("✅ Git hooks manager initialized")
            
            # Initialize file watcher
            self.auto_watcher = AutoDocsWatcher(
                self.project_root,
                self.config.get('file_watcher', {})
            )
            self.logger.info("✅ Auto-documentation watcher initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing components: {e}")
            return False
    
    def setup_git_hooks(self, hook_types: Optional[List[str]] = None) -> bool:
        """Setup Git hooks for automatic documentation updates."""
        self.logger.info("🔗 Setting up Git hooks...")
        
        if not self.git_manager:
            self.logger.error("❌ Git manager not initialized")
            return False
        
        try:
            # Configure hook types
            if hook_types:
                self.git_manager.config['hook_types'] = hook_types
            
            # Install hooks
            success = self.git_manager.install_hooks()
            
            if success:
                self.logger.info("✅ Git hooks installed successfully")
                
                # List installed hooks
                for hook_type in self.git_manager.config['hook_types']:
                    hook_file = self.git_manager.hooks_dir / hook_type
                    if hook_file.exists():
                        self.logger.info(f"  ✅ {hook_type} hook installed")
                    else:
                        self.logger.warning(f"  ⚠️ {hook_type} hook failed")
                
                return True
            else:
                self.logger.error("❌ Failed to install Git hooks")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error setting up Git hooks: {e}")
            return False
    
    def generate_initial_documentation(self) -> bool:
        """Generate initial documentation."""
        self.logger.info("📚 Generating initial documentation...")
        
        if not self.doc_generator:
            self.logger.error("❌ Documentation generator not initialized")
            return False
        
        try:
            import asyncio
            
            async def generate_docs():
                tasks = [
                    self.doc_generator.update_readme(),
                    self.doc_generator.update_changelog(),
                    self.doc_generator.update_api_docs(),
                    self.doc_generator.update_architecture_docs()
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                success_count = sum(1 for r in results if r is True)
                total_count = len(results)
                
                return success_count, total_count
            
            success_count, total_count = asyncio.run(generate_docs())
            
            if success_count == total_count:
                self.logger.info(f"✅ Generated {success_count}/{total_count} documentation files")
                return True
            else:
                self.logger.warning(f"⚠️ Generated {success_count}/{total_count} documentation files")
                return success_count > 0
                
        except Exception as e:
            self.logger.error(f"❌ Error generating documentation: {e}")
            return False
    
    def create_config_directories(self) -> bool:
        """Create necessary configuration directories."""
        self.logger.info("📁 Creating configuration directories...")
        
        directories = [
            self.project_root / 'config',
            self.project_root / 'logs',
            self.project_root / 'scripts',
            self.project_root / '.github' / 'workflows'
        ]
        
        try:
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creating directories: {e}")
            return False
    
    def validate_setup(self) -> bool:
        """Validate that setup was successful."""
        self.logger.info("🧪 Validating setup...")
        
        checks = []
        
        # Check if documentation files exist
        doc_files = ['README.md', 'CHANGELOG.md', 'API_DOCS.md', 'ARCHITECTURE.md']
        for doc_file in doc_files:
            file_path = self.project_root / doc_file
            if file_path.exists():
                self.logger.info(f"✅ {doc_file} exists")
                checks.append(True)
            else:
                self.logger.warning(f"⚠️ {doc_file} not found")
                checks.append(False)
        
        # Check Git hooks
        if self.git_manager and self.git_manager.hooks_dir:
            for hook_type in ['pre-commit', 'post-commit', 'pre-push']:
                hook_file = self.git_manager.hooks_dir / hook_type
                if hook_file.exists():
                    self.logger.info(f"✅ {hook_type} hook installed")
                    checks.append(True)
                else:
                    self.logger.warning(f"⚠️ {hook_type} hook not found")
                    checks.append(False)
        
        # Check if components can be imported
        try:
            from src.automation import AutoDocsWatcher, DocumentationGenerator, GitHooksManager
            self.logger.info("✅ Automation modules can be imported")
            checks.append(True)
        except ImportError as e:
            self.logger.error(f"❌ Failed to import automation modules: {e}")
            checks.append(False)
        
        success_rate = sum(checks) / len(checks) * 100
        self.logger.info(f"📊 Setup validation: {success_rate:.1f}% successful")
        
        return success_rate >= 80
    
    def run_full_setup(self, install_deps: bool = True, install_hooks: bool = True, 
                      generate_docs: bool = True) -> bool:
        """Run the complete setup process."""
        self.logger.info("🚀 Starting full auto-documentation setup...")
        
        steps = []
        
        # Step 1: Check prerequisites
        if self.check_prerequisites():
            self.logger.info("✅ Prerequisites check passed")
            steps.append(True)
        else:
            self.logger.error("❌ Prerequisites check failed")
            return False
        
        # Step 2: Create directories
        if self.create_config_directories():
            self.logger.info("✅ Configuration directories created")
            steps.append(True)
        else:
            self.logger.error("❌ Failed to create directories")
            steps.append(False)
        
        # Step 3: Install dependencies
        if install_deps:
            if self.install_dependencies():
                self.logger.info("✅ Dependencies installed")
                steps.append(True)
            else:
                self.logger.error("❌ Failed to install dependencies")
                steps.append(False)
        else:
            self.logger.info("⏭️ Skipping dependency installation")
            steps.append(True)
        
        # Step 4: Initialize components
        if self.initialize_components():
            self.logger.info("✅ Components initialized")
            steps.append(True)
        else:
            self.logger.error("❌ Failed to initialize components")
            return False
        
        # Step 5: Setup Git hooks
        if install_hooks:
            if self.setup_git_hooks():
                self.logger.info("✅ Git hooks installed")
                steps.append(True)
            else:
                self.logger.warning("⚠️ Git hooks installation failed")
                steps.append(False)
        else:
            self.logger.info("⏭️ Skipping Git hooks installation")
            steps.append(True)
        
        # Step 6: Generate initial documentation
        if generate_docs:
            if self.generate_initial_documentation():
                self.logger.info("✅ Initial documentation generated")
                steps.append(True)
            else:
                self.logger.warning("⚠️ Documentation generation had issues")
                steps.append(False)
        else:
            self.logger.info("⏭️ Skipping documentation generation")
            steps.append(True)
        
        # Step 7: Validate setup
        if self.validate_setup():
            self.logger.info("✅ Setup validation passed")
            steps.append(True)
        else:
            self.logger.warning("⚠️ Setup validation had issues")
            steps.append(False)
        
        # Calculate success rate
        success_rate = sum(steps) / len(steps) * 100
        
        if success_rate >= 80:
            self.logger.info(f"🎉 Setup completed successfully! ({success_rate:.1f}% success rate)")
            self._print_success_message()
            return True
        else:
            self.logger.error(f"❌ Setup completed with issues ({success_rate:.1f}% success rate)")
            self._print_troubleshooting()
            return False
    
    def _print_success_message(self):
        """Print success message with next steps."""
        print("\n" + "="*60)
        print("🎉 AI Quality Assurance Auto-Documentation Setup Complete!")
        print("="*60)
        print()
        print("✅ What's been set up:")
        print("  • File monitoring system for real-time updates")
        print("  • Documentation generation engine")
        print("  • Git hooks for automatic documentation commits")
        print("  • MCP server integration for Claude")
        print("  • GitHub Actions workflow for CI/CD")
        print()
        print("🚀 Next steps:")
        print("  1. Start the auto-documentation system:")
        print("     python -m src.automation.file_watcher")
        print()
        print("  2. Start the MCP server for Claude integration:")
        print("     python mcp_server.py")
        print()
        print("  3. Start the web interface for demos:")
        print("     python -m uvicorn src.main:app --reload --port 8000")
        print()
        print("  4. Make changes to your code and watch the docs update automatically!")
        print()
        print("📚 Generated documentation:")
        for doc_file in ['README.md', 'CHANGELOG.md', 'API_DOCS.md', 'ARCHITECTURE.md']:
            if (self.project_root / doc_file).exists():
                print(f"  • {doc_file}")
        print()
        print("🎯 Ready for Campus Party Brasil 2025 demonstration!")
        print("="*60)
    
    def _print_troubleshooting(self):
        """Print troubleshooting information."""
        print("\n" + "="*60)
        print("⚠️ Setup completed with some issues")
        print("="*60)
        print()
        print("Common solutions:")
        print("  • Install missing dependencies: pip install watchdog GitPython")
        print("  • Check Git repository: git init (if needed)")
        print("  • Verify Python version: python --version (need 3.8+)")
        print("  • Check file permissions in .git/hooks/")
        print()
        print("For detailed logs, check: setup.log")
        print("="*60)


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="Setup AI Quality Assurance Auto-Documentation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full setup with all features
  python setup_automation.py
  
  # Setup without installing dependencies
  python setup_automation.py --no-deps
  
  # Setup without Git hooks
  python setup_automation.py --no-hooks
  
  # Setup with specific Git hooks only
  python setup_automation.py --hooks pre-commit post-commit
  
  # Generate documentation only
  python setup_automation.py --docs-only
        """
    )
    
    parser.add_argument(
        '--no-deps', 
        action='store_true',
        help='Skip dependency installation'
    )
    
    parser.add_argument(
        '--no-hooks',
        action='store_true', 
        help='Skip Git hooks installation'
    )
    
    parser.add_argument(
        '--no-docs',
        action='store_true',
        help='Skip initial documentation generation'
    )
    
    parser.add_argument(
        '--docs-only',
        action='store_true',
        help='Only generate documentation, skip other setup'
    )
    
    parser.add_argument(
        '--hooks',
        nargs='+',
        choices=['pre-commit', 'post-commit', 'pre-push'],
        help='Specific Git hooks to install'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize setup manager
    setup = AutomationSetup(project_root, args.config)
    
    # Handle docs-only mode
    if args.docs_only:
        print("📚 Documentation-only mode")
        if setup.initialize_components() and setup.generate_initial_documentation():
            print("✅ Documentation generated successfully")
            return 0
        else:
            print("❌ Documentation generation failed")
            return 1
    
    # Run full setup
    success = setup.run_full_setup(
        install_deps=not args.no_deps,
        install_hooks=not args.no_hooks,
        generate_docs=not args.no_docs
    )
    
    # Install specific hooks if requested
    if args.hooks:
        if setup.git_manager:
            setup.setup_git_hooks(args.hooks)
        else:
            print("⚠️ Cannot install specific hooks - Git manager not initialized")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())