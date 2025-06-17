"""
Git integration system for automatic documentation updates.
Handles git hooks, automatic commits, and repository management.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import shutil
import tempfile

try:
    import git
    from git import Repo, InvalidGitRepositoryError
    GIT_PYTHON_AVAILABLE = True
except ImportError:
    git = None
    Repo = None
    InvalidGitRepositoryError = Exception
    GIT_PYTHON_AVAILABLE = False

logger = logging.getLogger(__name__)


class GitHooksManager:
    """Manages Git hooks and automated Git operations for documentation updates."""
    
    def __init__(self, project_root: Path, config: Optional[Dict[str, Any]] = None):
        self.project_root = Path(project_root)
        self.config = config or self._default_config()
        self.repo = None
        self.hooks_dir = None
        
        # Initialize Git repository
        self._initialize_repo()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for Git integration."""
        return {
            'auto_commit': False,
            'auto_push': False,
            'commit_message_template': 'docs: Auto-update documentation for {file}',
            'commit_author_name': 'Auto-Docs Bot',
            'commit_author_email': 'auto-docs@ai-qa-system.local',
            'branch_name': 'main',  # or 'master'
            'install_hooks': True,
            'hook_types': ['pre-commit', 'post-commit', 'pre-push'],
            'docs_files_pattern': ['*.md', '*.rst', 'docs/**/*'],
            'exclude_files': ['.git/**/*', '__pycache__/**/*', '*.pyc'],
            'max_commit_frequency': 300,  # seconds between auto-commits
            'batch_documentation_updates': True
        }
    
    def _initialize_repo(self):
        """Initialize or connect to Git repository."""
        try:
            if GIT_PYTHON_AVAILABLE:
                self.repo = Repo(self.project_root)
                self.hooks_dir = Path(self.repo.git_dir) / 'hooks'
                logger.info(f"Connected to Git repository at {self.project_root}")
            else:
                # Fallback to subprocess
                git_dir = self.project_root / '.git'
                if git_dir.exists():
                    self.hooks_dir = git_dir / 'hooks'
                    logger.info("Using subprocess for Git operations (GitPython not available)")
                else:
                    logger.warning("No Git repository found")
                    
        except InvalidGitRepositoryError:
            logger.warning(f"No Git repository found at {self.project_root}")
        except Exception as e:
            logger.error(f"Error initializing Git repository: {e}")
    
    def install_hooks(self) -> bool:
        """Install Git hooks for automatic documentation updates."""
        if not self.hooks_dir or not self.hooks_dir.exists():
            logger.error("Git hooks directory not found")
            return False
        
        try:
            success_count = 0
            
            for hook_type in self.config['hook_types']:
                if self._install_hook(hook_type):
                    success_count += 1
            
            logger.info(f"Installed {success_count}/{len(self.config['hook_types'])} Git hooks")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to install Git hooks: {e}")
            return False
    
    def _install_hook(self, hook_type: str) -> bool:
        """Install a specific Git hook."""
        try:
            hook_file = self.hooks_dir / hook_type
            hook_content = self._generate_hook_content(hook_type)
            
            # Backup existing hook if it exists
            if hook_file.exists():
                backup_file = hook_file.with_suffix('.backup')
                shutil.copy2(hook_file, backup_file)
                logger.info(f"Backed up existing {hook_type} hook to {backup_file}")
            
            # Write new hook
            with open(hook_file, 'w', encoding='utf-8') as f:
                f.write(hook_content)
            
            # Make executable
            hook_file.chmod(0o755)
            
            logger.info(f"Installed {hook_type} hook")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install {hook_type} hook: {e}")
            return False
    
    def _generate_hook_content(self, hook_type: str) -> str:
        """Generate content for a specific hook type."""
        python_executable = shutil.which('python3') or shutil.which('python')
        project_root = self.project_root.absolute()
        
        base_content = f"""#!/bin/bash
# Auto-generated Git hook for AI Quality Assurance documentation system
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Change to project directory
cd "{project_root}"

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

"""
        
        if hook_type == 'pre-commit':
            content = base_content + f'''
# Pre-commit hook: Validate documentation and run quick checks
echo "🔍 Running pre-commit documentation checks..."

# Check if documentation is up to date
{python_executable} -c "
import sys
sys.path.append('{project_root}')
from src.automation.git_integration import GitHooksManager
from pathlib import Path

manager = GitHooksManager(Path('{project_root}'))
if not manager.validate_documentation_status():
    print('⚠️  Documentation may be outdated. Consider running manual update.')
    # Don't fail the commit, just warn
    sys.exit(0)
else:
    print('✅ Documentation is up to date')
    sys.exit(0)
"

echo "✅ Pre-commit checks completed"
'''
        
        elif hook_type == 'post-commit':
            content = base_content + f'''
# Post-commit hook: Update documentation after commit
echo "📚 Updating documentation after commit..."

# Run documentation update
{python_executable} -c "
import asyncio
import sys
sys.path.append('{project_root}')
from src.automation.doc_generator import DocumentationGenerator
from pathlib import Path

async def update_docs():
    try:
        generator = DocumentationGenerator(Path('{project_root}'))
        
        # Update key documentation
        await generator.update_readme()
        await generator.update_changelog()
        
        print('✅ Documentation updated successfully')
        return True
    except Exception as e:
        print(f'⚠️  Documentation update failed: {{e}}')
        return False

# Run the update
result = asyncio.run(update_docs())
sys.exit(0 if result else 1)
"

echo "📚 Post-commit documentation update completed"
'''
        
        elif hook_type == 'pre-push':
            content = base_content + f'''
# Pre-push hook: Final documentation validation
echo "🚀 Running pre-push documentation validation..."

# Ensure all documentation is committed
if git diff --name-only HEAD | grep -E "\\.(md|rst)$"; then
    echo "⚠️  Documentation files have uncommitted changes:"
    git diff --name-only HEAD | grep -E "\\.(md|rst)$"
    echo "Please commit documentation changes before pushing."
    exit 1
fi

echo "✅ Pre-push validation completed"
'''
        
        else:
            content = base_content + f'''
# Generic hook for {hook_type}
echo "🔧 Running {hook_type} hook..."
echo "✅ {hook_type} hook completed"
'''
        
        return content
    
    def uninstall_hooks(self) -> bool:
        """Remove installed Git hooks."""
        if not self.hooks_dir:
            return False
        
        try:
            removed_count = 0
            
            for hook_type in self.config['hook_types']:
                hook_file = self.hooks_dir / hook_type
                if hook_file.exists():
                    # Check if it's our hook
                    with open(hook_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'Auto-generated Git hook for AI Quality Assurance' in content:
                        hook_file.unlink()
                        removed_count += 1
                        
                        # Restore backup if it exists
                        backup_file = hook_file.with_suffix('.backup')
                        if backup_file.exists():
                            shutil.move(backup_file, hook_file)
                            logger.info(f"Restored backup for {hook_type} hook")
            
            logger.info(f"Removed {removed_count} Git hooks")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall Git hooks: {e}")
            return False
    
    async def auto_commit_docs(self, commit_message: Optional[str] = None) -> bool:
        """Automatically commit documentation changes."""
        if not self.config['auto_commit']:
            return False
        
        try:
            # Check for documentation changes
            changed_docs = self._get_changed_documentation_files()
            
            if not changed_docs:
                logger.debug("No documentation changes to commit")
                return True
            
            # Prepare commit message
            if not commit_message:
                if len(changed_docs) == 1:
                    commit_message = f"docs: Auto-update {changed_docs[0]}"
                else:
                    commit_message = f"docs: Auto-update {len(changed_docs)} documentation files"
            
            # Stage documentation files
            if GIT_PYTHON_AVAILABLE and self.repo:
                for doc_file in changed_docs:
                    self.repo.index.add([str(doc_file)])
                
                # Commit with custom author
                author_name = self.config['commit_author_name']
                author_email = self.config['commit_author_email']
                
                commit = self.repo.index.commit(
                    commit_message,
                    author=git.Actor(author_name, author_email)
                )
                
                logger.info(f"Auto-committed documentation: {commit.hexsha[:8]}")
                return True
            
            else:
                # Fallback to subprocess
                return await self._subprocess_commit(changed_docs, commit_message)
            
        except Exception as e:
            logger.error(f"Failed to auto-commit documentation: {e}")
            return False
    
    async def _subprocess_commit(self, files: List[Path], message: str) -> bool:
        """Commit using subprocess (fallback)."""
        try:
            # Stage files
            for file in files:
                subprocess.run(['git', 'add', str(file)], 
                             cwd=self.project_root, check=True)
            
            # Commit
            author = f"{self.config['commit_author_name']} <{self.config['commit_author_email']}>"
            subprocess.run(['git', 'commit', '-m', message, '--author', author],
                         cwd=self.project_root, check=True)
            
            logger.info(f"Auto-committed documentation via subprocess")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e}")
            return False
    
    async def auto_push_docs(self) -> bool:
        """Automatically push documentation changes."""
        if not self.config['auto_push']:
            return False
        
        try:
            if GIT_PYTHON_AVAILABLE and self.repo:
                origin = self.repo.remote('origin')
                branch = self.config['branch_name']
                origin.push(branch)
                
                logger.info(f"Auto-pushed documentation to {branch}")
                return True
            
            else:
                # Fallback to subprocess
                branch = self.config['branch_name']
                subprocess.run(['git', 'push', 'origin', branch],
                             cwd=self.project_root, check=True)
                
                logger.info(f"Auto-pushed documentation via subprocess")
                return True
            
        except Exception as e:
            logger.error(f"Failed to auto-push documentation: {e}")
            return False
    
    def _get_changed_documentation_files(self) -> List[Path]:
        """Get list of changed documentation files."""
        changed_files = []
        
        try:
            if GIT_PYTHON_AVAILABLE and self.repo:
                # Get unstaged and staged changes
                for item in self.repo.index.diff(None):  # Unstaged
                    file_path = Path(item.a_path)
                    if self._is_documentation_file(file_path):
                        changed_files.append(file_path)
                
                for item in self.repo.index.diff('HEAD'):  # Staged
                    file_path = Path(item.a_path)
                    if self._is_documentation_file(file_path):
                        changed_files.append(file_path)
            
            else:
                # Fallback to subprocess
                try:
                    # Get unstaged changes
                    result = subprocess.run(['git', 'diff', '--name-only'],
                                          cwd=self.project_root, 
                                          capture_output=True, text=True, check=True)
                    
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            file_path = Path(line)
                            if self._is_documentation_file(file_path):
                                changed_files.append(file_path)
                    
                    # Get staged changes
                    result = subprocess.run(['git', 'diff', '--cached', '--name-only'],
                                          cwd=self.project_root,
                                          capture_output=True, text=True, check=True)
                    
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            file_path = Path(line)
                            if self._is_documentation_file(file_path):
                                changed_files.append(file_path)
                
                except subprocess.CalledProcessError:
                    logger.warning("Failed to get changed files via git")
        
        except Exception as e:
            logger.error(f"Error getting changed documentation files: {e}")
        
        # Remove duplicates
        return list(set(changed_files))
    
    def _is_documentation_file(self, file_path: Path) -> bool:
        """Check if a file is a documentation file."""
        # Check patterns
        for pattern in self.config['docs_files_pattern']:
            if file_path.match(pattern):
                return True
        
        # Check extensions
        if file_path.suffix in {'.md', '.rst', '.txt'}:
            return True
        
        # Check specific files
        if file_path.name in {'README.md', 'CHANGELOG.md', 'API_DOCS.md', 'ARCHITECTURE.md'}:
            return True
        
        return False
    
    def validate_documentation_status(self) -> bool:
        """Validate that documentation is up to date."""
        try:
            # Check if there are uncommitted documentation changes
            changed_docs = self._get_changed_documentation_files()
            
            if changed_docs:
                logger.warning(f"Found {len(changed_docs)} uncommitted documentation files")
                return False
            
            # Check if documentation files are recent
            # (This is a simple check - you could make it more sophisticated)
            readme_path = self.project_root / 'README.md'
            if readme_path.exists():
                readme_mtime = readme_path.stat().st_mtime
                
                # Check if any source file is newer than README
                src_dir = self.project_root / 'src'
                if src_dir.exists():
                    for py_file in src_dir.rglob('*.py'):
                        if py_file.stat().st_mtime > readme_mtime:
                            logger.warning(f"Source file {py_file} is newer than README.md")
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating documentation status: {e}")
            return False
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get current Git repository status."""
        status = {
            'has_repo': False,
            'current_branch': None,
            'uncommitted_changes': 0,
            'documentation_changes': 0,
            'last_commit': None,
            'hooks_installed': False
        }
        
        try:
            if GIT_PYTHON_AVAILABLE and self.repo:
                status['has_repo'] = True
                status['current_branch'] = self.repo.active_branch.name
                status['uncommitted_changes'] = len(list(self.repo.index.diff(None)))
                status['documentation_changes'] = len(self._get_changed_documentation_files())
                
                if self.repo.head.commit:
                    status['last_commit'] = {
                        'hash': self.repo.head.commit.hexsha[:8],
                        'message': self.repo.head.commit.message.strip(),
                        'author': str(self.repo.head.commit.author),
                        'date': self.repo.head.commit.committed_datetime.isoformat()
                    }
            
            # Check hooks
            if self.hooks_dir:
                hooks_installed = 0
                for hook_type in self.config['hook_types']:
                    hook_file = self.hooks_dir / hook_type
                    if hook_file.exists():
                        hooks_installed += 1
                
                status['hooks_installed'] = hooks_installed > 0
                status['hooks_count'] = hooks_installed
        
        except Exception as e:
            logger.error(f"Error getting Git status: {e}")
        
        return status
    
    def create_documentation_branch(self, branch_name: str = 'auto-docs') -> bool:
        """Create a separate branch for documentation updates."""
        try:
            if GIT_PYTHON_AVAILABLE and self.repo:
                # Create new branch from current HEAD
                new_branch = self.repo.create_head(branch_name)
                new_branch.checkout()
                
                logger.info(f"Created and switched to documentation branch: {branch_name}")
                return True
            
            else:
                # Fallback to subprocess
                subprocess.run(['git', 'checkout', '-b', branch_name],
                             cwd=self.project_root, check=True)
                
                logger.info(f"Created documentation branch via subprocess: {branch_name}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to create documentation branch: {e}")
            return False
    
    async def cleanup_old_documentation_commits(self, max_age_days: int = 30) -> int:
        """Clean up old automatic documentation commits."""
        # This is a placeholder for a more advanced feature
        # that would squash or clean up old auto-generated commits
        return 0


# Convenience functions
def setup_git_automation(project_root: str, config: Optional[Dict[str, Any]] = None) -> GitHooksManager:
    """Set up Git automation for a project."""
    manager = GitHooksManager(Path(project_root), config)
    
    if manager.config['install_hooks']:
        manager.install_hooks()
    
    return manager


def validate_git_setup(project_root: str) -> Dict[str, Any]:
    """Validate Git setup for auto-documentation."""
    manager = GitHooksManager(Path(project_root))
    return manager.get_git_status()


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        if len(sys.argv) > 1:
            project_path = sys.argv[1]
        else:
            project_path = os.getcwd()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Test Git integration
        manager = GitHooksManager(Path(project_path))
        
        print("Git Status:", manager.get_git_status())
        
        if '--install-hooks' in sys.argv:
            print("Installing Git hooks...")
            if manager.install_hooks():
                print("✅ Git hooks installed successfully")
            else:
                print("❌ Failed to install Git hooks")
        
        if '--test-commit' in sys.argv:
            print("Testing auto-commit...")
            result = await manager.auto_commit_docs("test: Auto-documentation test")
            if result:
                print("✅ Auto-commit test successful")
            else:
                print("❌ Auto-commit test failed")
    
    asyncio.run(main())