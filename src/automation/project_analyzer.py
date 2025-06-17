"""
Project analysis module - responsible for analyzing project structure and extracting information.
Part of the refactored documentation generation system.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class ProjectAnalyzer:
    """Analyzes project structure and extracts relevant information."""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
    
    def analyze_project(self) -> Dict[str, Any]:
        """Analyze the complete project structure."""
        info = {
            'src_files': [],
            'test_files': [],
            'config_files': [],
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'dependencies': [],
            'entry_points': [],
            'api_endpoints': [],
            'mcp_tools': [],
            'ml_models': []
        }
        
        try:
            # Analyze different components
            info.update(self._analyze_source_files())
            info.update(self._analyze_test_files())
            info.update(self._analyze_config_files())
            info.update(self._analyze_dependencies())
            info.update(self._analyze_mcp_server())
            info.update(self._analyze_entry_points())
            
        except Exception as e:
            self.logger.error(f"Error during project analysis: {e}")
        
        return info
    
    def _analyze_source_files(self) -> Dict[str, Any]:
        """Analyze source code files."""
        info = {
            'src_files': [],
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'api_endpoints': [],
            'ml_models': []
        }
        
        src_dir = self.project_root / 'src'
        if not src_dir.exists():
            return info
        
        for py_file in src_dir.rglob('*.py'):
            info['src_files'].append(py_file)
            file_info = self._analyze_python_file(py_file)
            
            info['total_lines'] += file_info['lines']
            info['total_functions'] += file_info['functions']
            info['total_classes'] += file_info['classes']
            info['api_endpoints'].extend(file_info['api_endpoints'])
            
            # Detect ML models
            if self._is_ml_model_file(py_file):
                info['ml_models'].append(py_file)
        
        return info
    
    def _analyze_test_files(self) -> Dict[str, Any]:
        """Analyze test files."""
        info = {'test_files': []}
        
        test_patterns = ['test_*.py', '*_test.py', 'tests/**/*.py']
        for pattern in test_patterns:
            for test_file in self.project_root.rglob(pattern):
                info['test_files'].append(test_file)
        
        return info
    
    def _analyze_config_files(self) -> Dict[str, Any]:
        """Analyze configuration files."""
        info = {'config_files': []}
        
        config_patterns = ['*.yaml', '*.yml', '*.json', '*.toml', '*.ini']
        for pattern in config_patterns:
            for config_file in self.project_root.rglob(pattern):
                # Skip obvious non-config files
                if not self._is_config_file(config_file):
                    continue
                info['config_files'].append(config_file)
        
        return info
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies."""
        info = {'dependencies': []}
        
        # Check various dependency files
        dep_files = [
            'requirements.txt',
            'requirements-dev.txt', 
            'pyproject.toml',
            'setup.py',
            'Pipfile'
        ]
        
        for dep_file in dep_files:
            file_path = self.project_root / dep_file
            if file_path.exists():
                deps = self._parse_dependency_file(file_path)
                info['dependencies'].extend(deps)
        
        # Remove duplicates while preserving order
        info['dependencies'] = list(dict.fromkeys(info['dependencies']))
        
        return info
    
    def _analyze_mcp_server(self) -> Dict[str, Any]:
        """Analyze MCP server configuration."""
        info = {'mcp_tools': []}
        
        mcp_file = self.project_root / 'mcp_server.py'
        if mcp_file.exists():
            tools = self._extract_mcp_tools(mcp_file)
            info['mcp_tools'] = tools
        
        return info
    
    def _analyze_entry_points(self) -> Dict[str, Any]:
        """Analyze project entry points."""
        info = {'entry_points': []}
        
        # Find main files and scripts
        entry_patterns = ['main.py', 'app.py', '__main__.py', 'cli.py']
        for pattern in entry_patterns:
            for entry_file in self.project_root.rglob(pattern):
                if self._is_entry_point(entry_file):
                    info['entry_points'].append(entry_file)
        
        return info
    
    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file."""
        info = {
            'lines': 0,
            'functions': 0,
            'classes': 0,
            'api_endpoints': [],
            'imports': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                info['lines'] = len(content.splitlines())
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    info['functions'] += 1
                    # Check for API endpoints
                    endpoints = self._extract_api_endpoints(node)
                    info['api_endpoints'].extend(endpoints)
                
                elif isinstance(node, ast.ClassDef):
                    info['classes'] += 1
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports = self._extract_imports(node)
                    info['imports'].extend(imports)
        
        except Exception as e:
            self.logger.warning(f"Error analyzing {file_path}: {e}")
        
        return info
    
    def _extract_api_endpoints(self, func_node: ast.FunctionDef) -> List[Dict[str, str]]:
        """Extract API endpoints from function decorators."""
        endpoints = []
        
        for decorator in func_node.decorator_list:
            if (isinstance(decorator, ast.Call) and 
                hasattr(decorator.func, 'attr') and 
                decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']):
                
                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                    endpoint = {
                        'method': decorator.func.attr.upper(),
                        'path': decorator.args[0].value,
                        'function': func_node.name
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_imports(self, import_node) -> List[str]:
        """Extract import statements."""
        imports = []
        
        if isinstance(import_node, ast.Import):
            for alias in import_node.names:
                imports.append(alias.name)
        elif isinstance(import_node, ast.ImportFrom):
            module = import_node.module or ''
            for alias in import_node.names:
                full_name = f"{module}.{alias.name}" if module else alias.name
                imports.append(full_name)
        
        return imports
    
    def _extract_mcp_tools(self, mcp_file: Path) -> List[Dict[str, str]]:
        """Extract MCP tools from server file."""
        tools = []
        
        try:
            with open(mcp_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use regex for simpler extraction
            tool_pattern = r'Tool\(\s*name="([^"]+)"\s*,\s*description="([^"]+)"'
            matches = re.findall(tool_pattern, content)
            
            for name, description in matches:
                tools.append({
                    'name': name,
                    'description': description
                })
        
        except Exception as e:
            self.logger.warning(f"Error extracting MCP tools: {e}")
        
        return tools
    
    def _parse_dependency_file(self, file_path: Path) -> List[str]:
        """Parse dependency file and extract package names."""
        dependencies = []
        
        try:
            if file_path.suffix == '.txt':
                dependencies = self._parse_requirements_txt(file_path)
            elif file_path.suffix == '.toml':
                dependencies = self._parse_pyproject_toml(file_path)
            elif file_path.suffix == '.py' and file_path.name == 'setup.py':
                dependencies = self._parse_setup_py(file_path)
        
        except Exception as e:
            self.logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _parse_requirements_txt(self, file_path: Path) -> List[str]:
        """Parse requirements.txt file."""
        dependencies = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (remove version specifiers)
                    package = re.split(r'[>=<!=~]', line)[0].strip()
                    if package:
                        dependencies.append(package)
        
        return dependencies
    
    def _parse_pyproject_toml(self, file_path: Path) -> List[str]:
        """Parse pyproject.toml file (simplified)."""
        dependencies = []
        
        # This is a simplified parser - in production, use tomli/tomllib
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Look for dependencies section
            deps_pattern = r'dependencies\s*=\s*\[(.*?)\]'
            match = re.search(deps_pattern, content, re.DOTALL)
            
            if match:
                deps_text = match.group(1)
                # Extract quoted strings
                quoted_deps = re.findall(r'"([^"]+)"', deps_text)
                for dep in quoted_deps:
                    package = re.split(r'[>=<!=~]', dep)[0].strip()
                    if package:
                        dependencies.append(package)
        
        return dependencies
    
    def _parse_setup_py(self, file_path: Path) -> List[str]:
        """Parse setup.py file (simplified)."""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for install_requires
            requires_pattern = r'install_requires\s*=\s*\[(.*?)\]'
            match = re.search(requires_pattern, content, re.DOTALL)
            
            if match:
                deps_text = match.group(1)
                quoted_deps = re.findall(r'["\']([^"\']+)["\']', deps_text)
                for dep in quoted_deps:
                    package = re.split(r'[>=<!=~]', dep)[0].strip()
                    if package:
                        dependencies.append(package)
        
        except Exception as e:
            self.logger.warning(f"Error parsing setup.py: {e}")
        
        return dependencies
    
    def _is_ml_model_file(self, file_path: Path) -> bool:
        """Check if file contains ML model definitions."""
        indicators = ['model', 'ml_', 'prediction', 'classifier', 'regression']
        file_name_lower = file_path.name.lower()
        
        return any(indicator in file_name_lower for indicator in indicators)
    
    def _is_config_file(self, file_path: Path) -> bool:
        """Check if file is a configuration file."""
        config_indicators = ['config', 'settings', 'env', '.env']
        file_name_lower = file_path.name.lower()
        
        # Skip obvious non-config files
        skip_patterns = ['test', 'spec', 'node_modules', '__pycache__']
        if any(pattern in str(file_path).lower() for pattern in skip_patterns):
            return False
        
        return any(indicator in file_name_lower for indicator in config_indicators)
    
    def _is_entry_point(self, file_path: Path) -> bool:
        """Check if file is a valid entry point."""
        # Skip test files and hidden directories
        if 'test' in str(file_path).lower() or '.' in str(file_path.parent).split('/')[-1]:
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for if __name__ == "__main__" pattern
                return 'if __name__ == "__main__"' in content
        except Exception:
            return False


class ProjectMetrics:
    """Calculate various project metrics."""
    
    def __init__(self, project_info: Dict[str, Any]):
        self.project_info = project_info
    
    def calculate_complexity_metrics(self) -> Dict[str, Any]:
        """Calculate project complexity metrics."""
        return {
            'total_files': len(self.project_info.get('src_files', [])),
            'total_lines': self.project_info.get('total_lines', 0),
            'total_functions': self.project_info.get('total_functions', 0),
            'total_classes': self.project_info.get('total_classes', 0),
            'functions_per_file': self._safe_divide(
                self.project_info.get('total_functions', 0),
                len(self.project_info.get('src_files', []))
            ),
            'lines_per_file': self._safe_divide(
                self.project_info.get('total_lines', 0),
                len(self.project_info.get('src_files', []))
            ),
            'api_endpoints': len(self.project_info.get('api_endpoints', [])),
            'mcp_tools': len(self.project_info.get('mcp_tools', [])),
            'test_coverage_ratio': self._calculate_test_coverage()
        }
    
    def _safe_divide(self, numerator: float, denominator: float) -> float:
        """Safely divide two numbers."""
        return round(numerator / denominator, 2) if denominator > 0 else 0.0
    
    def _calculate_test_coverage(self) -> float:
        """Calculate approximate test coverage ratio."""
        src_files = len(self.project_info.get('src_files', []))
        test_files = len(self.project_info.get('test_files', []))
        
        return self._safe_divide(test_files, src_files)