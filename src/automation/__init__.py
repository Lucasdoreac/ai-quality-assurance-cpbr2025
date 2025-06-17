"""
Automation module for AI Quality Assurance system.
Provides automatic documentation updates and monitoring capabilities.
"""

# Import components conditionally to avoid dependency issues
try:
    from .doc_generator import DocumentationGenerator
    DOC_GENERATOR_AVAILABLE = True
except ImportError:
    DocumentationGenerator = None
    DOC_GENERATOR_AVAILABLE = False

try:
    from .git_integration import GitHooksManager
    GIT_INTEGRATION_AVAILABLE = True
except ImportError:
    GitHooksManager = None
    GIT_INTEGRATION_AVAILABLE = False

try:
    from .file_watcher import AutoDocsWatcher
    FILE_WATCHER_AVAILABLE = True
except ImportError:
    AutoDocsWatcher = None
    FILE_WATCHER_AVAILABLE = False

__all__ = [
    'AutoDocsWatcher',
    'DocumentationGenerator', 
    'GitHooksManager',
    'DOC_GENERATOR_AVAILABLE',
    'GIT_INTEGRATION_AVAILABLE',
    'FILE_WATCHER_AVAILABLE'
]

__version__ = "1.0.0"