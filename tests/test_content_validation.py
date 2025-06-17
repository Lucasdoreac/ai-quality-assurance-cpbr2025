#!/usr/bin/env python3
"""
Content validation tests - validates actual content quality and correctness.
Addresses the CodeRabbit recommendation for content validation tests.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
import sys
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDocumentationContentValidation:
    """Test that generated documentation has correct content."""
    
    def test_readme_content_accuracy(self):
        """Test that README content accurately reflects project state."""
        try:
            from src.automation.readme_generator import ReadmeGenerator
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create mock project structure
                src_dir = temp_path / 'src'
                src_dir.mkdir()
                
                # Create a simple Python file
                py_file = src_dir / 'test_module.py'
                py_file.write_text("""
def test_function():
    '''A test function'''
    pass

class TestClass:
    '''A test class'''
    def method(self):
        pass
""")
                
                # Mock project info
                project_info = {
                    'src_files': [py_file],
                    'total_lines': 10,
                    'total_functions': 2,
                    'total_classes': 1,
                    'test_files': [],
                    'dependencies': ['pytest', 'fastapi'],
                    'mcp_tools': [
                        {'name': 'test_tool', 'description': 'A test tool'}
                    ],
                    'api_endpoints': []
                }
                
                config = {
                    'project_name': 'Test Project',
                    'author': 'Test Author'
                }
                
                generator = ReadmeGenerator(temp_path, config)
                
                # Generate README
                readme_content = asyncio.run(generator.generate_readme(project_info))
                
                # Validate content accuracy
                assert 'Test Project' in readme_content
                assert 'Test Author' in readme_content
                assert '2' in readme_content  # total_functions
                assert '1' in readme_content  # total_classes
                assert '10' in readme_content  # total_lines
                assert 'test_tool' in readme_content
                assert 'A test tool' in readme_content
                
        except ImportError:
            pytest.skip("ReadmeGenerator not available")
    
    def test_changelog_content_completeness(self):
        """Test that CHANGELOG content is complete and well-formatted."""
        try:
            from src.automation.changelog_generator import ChangelogGenerator
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                project_info = {
                    'total_functions': 15,
                    'total_classes': 5,
                    'test_files': ['test1.py', 'test2.py'],
                    'dependencies': ['fastapi', 'pytest', 'uvicorn'],
                    'mcp_tools': [
                        {'name': 'analyze_code', 'description': 'Analyze code quality'},
                        {'name': 'generate_tests', 'description': 'Generate unit tests'}
                    ]
                }
                
                config = {'changelog_format': 'keepachangelog'}
                generator = ChangelogGenerator(temp_path, config)
                
                # Generate changelog
                changelog_content = asyncio.run(generator.generate_changelog(project_info))
                
                # Validate content completeness
                assert '# Changelog' in changelog_content
                assert 'keepachangelog.com' in changelog_content
                assert 'semver.org' in changelog_content
                assert '[Unreleased]' in changelog_content
                assert '### ✨ Features' in changelog_content
                assert '### 🔧 Technical' in changelog_content
                assert '### 📊 Metrics' in changelog_content
                assert '15 funções' in changelog_content
                assert '5 classes' in changelog_content
                assert '2 arquivos de teste' in changelog_content
                
                # Validate date format
                date_pattern = r'\d{4}-\d{2}-\d{2}'
                assert re.search(date_pattern, changelog_content), "Should contain valid date format"
                
        except ImportError:
            pytest.skip("ChangelogGenerator not available")
    
    def test_template_variable_substitution(self):
        """Test that template variables are correctly substituted."""
        try:
            from src.automation.template_manager import TemplateManager
            
            # Mock template content
            with tempfile.TemporaryDirectory() as temp_dir:
                templates_dir = Path(temp_dir) / 'templates'
                templates_dir.mkdir()
                
                # Create test template
                test_template = templates_dir / 'test_template.md'
                test_template.write_text("""
# Test Report for {filename}

Quality Score: {quality_score}
Functions: {function_count}
Classes: {class_count}
""")
                
                manager = TemplateManager(templates_dir)
                
                # Test variable substitution
                variables = {
                    'filename': 'test_module.py',
                    'quality_score': 87.5,
                    'function_count': 10,
                    'class_count': 3
                }
                
                result = manager.render_template('test_template', variables)
                
                # Validate substitution
                assert 'test_module.py' in result
                assert '87.5' in result
                assert '10' in result  # function_count
                assert '3' in result   # class_count
                
                # Ensure no unsubstituted variables remain
                assert '{' not in result or '}' not in result
                
        except ImportError:
            pytest.skip("TemplateManager not available")
    
    def test_api_documentation_accuracy(self):
        """Test that API documentation accurately reflects endpoints."""
        try:
            from src.automation.documentation_orchestrator import DocumentationOrchestrator
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Mock project with API endpoints
                project_info = {
                    'api_endpoints': [
                        {'method': 'GET', 'path': '/users', 'function': 'get_users'},
                        {'method': 'POST', 'path': '/users', 'function': 'create_user'},
                        {'method': 'GET', 'path': '/health', 'function': 'health_check'}
                    ],
                    'mcp_tools': [
                        {'name': 'analyze_code', 'description': 'Analyze code for issues'},
                        {'name': 'generate_tests', 'description': 'Generate unit tests'}
                    ]
                }
                
                orchestrator = DocumentationOrchestrator(temp_path)
                
                # Generate API documentation content
                api_content = orchestrator._generate_api_docs_content(
                    project_info['api_endpoints'],
                    project_info['mcp_tools']
                )
                
                # Validate API endpoint documentation
                assert 'GET /users' in api_content
                assert 'POST /users' in api_content
                assert 'GET /health' in api_content
                assert 'get_users' in api_content
                assert 'create_user' in api_content
                assert 'health_check' in api_content
                
                # Validate MCP tools documentation
                assert 'analyze_code' in api_content
                assert 'generate_tests' in api_content
                assert 'Analyze code for issues' in api_content
                assert 'Generate unit tests' in api_content
                
        except ImportError:
            pytest.skip("DocumentationOrchestrator not available")


class TestErrorScenarioHandling:
    """Test handling of error scenarios in documentation generation."""
    
    def test_missing_project_files(self):
        """Test behavior when project files are missing."""
        try:
            from src.automation.project_analyzer import ProjectAnalyzer
            
            # Test with empty directory
            with tempfile.TemporaryDirectory() as temp_dir:
                analyzer = ProjectAnalyzer(Path(temp_dir))
                result = analyzer.analyze_project()
                
                # Should handle gracefully
                assert isinstance(result, dict)
                assert result.get('src_files', []) == []
                assert result.get('total_lines', 0) == 0
                assert result.get('total_functions', 0) == 0
                
        except ImportError:
            pytest.skip("ProjectAnalyzer not available")
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted or unreadable files."""
        try:
            from src.automation.project_analyzer import ProjectAnalyzer
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create files with various issues
                src_dir = temp_path / 'src'
                src_dir.mkdir()
                
                # Corrupted Python file
                corrupted_file = src_dir / 'corrupted.py'
                corrupted_file.write_bytes(b'\x00\x01\x02\x03')  # Binary data
                
                # File with encoding issues
                encoding_file = src_dir / 'encoding.py'
                encoding_file.write_bytes('def test(): pass # ção'.encode('latin1'))
                
                analyzer = ProjectAnalyzer(temp_path)
                result = analyzer.analyze_project()
                
                # Should handle without crashing
                assert isinstance(result, dict)
                
        except ImportError:
            pytest.skip("ProjectAnalyzer not available")
    
    def test_permission_denied_scenarios(self):
        """Test handling of permission denied scenarios."""
        try:
            from src.automation.project_analyzer import ProjectAnalyzer
            import os
            import stat
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create protected directory
                protected_dir = temp_path / 'protected'
                protected_dir.mkdir()
                
                # Create file and remove read permissions
                protected_file = protected_dir / 'secret.py'
                protected_file.write_text('def secret(): pass')
                
                # Remove read permission (on Unix systems)
                if hasattr(os, 'chmod'):
                    try:
                        os.chmod(protected_file, 0o000)
                        
                        analyzer = ProjectAnalyzer(temp_path)
                        result = analyzer.analyze_project()
                        
                        # Should handle gracefully
                        assert isinstance(result, dict)
                        
                        # Restore permissions for cleanup
                        os.chmod(protected_file, 0o644)
                    except (OSError, PermissionError):
                        # Skip on systems where permission changes aren't supported
                        pass
                
        except ImportError:
            pytest.skip("ProjectAnalyzer not available")
    
    def test_large_file_handling(self):
        """Test handling of very large files."""
        try:
            from src.automation.event_handler import FileFilter
            
            config = {}
            file_filter = FileFilter(config)
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create large file
                large_file = temp_path / 'large.py'
                large_content = 'print("x")' * 1000000  # Very large file
                large_file.write_text(large_content)
                
                # Should reject very large files
                should_process = file_filter.should_process_file(str(large_file))
                assert should_process is False, "Very large files should be filtered out"
                
        except ImportError:
            pytest.skip("FileFilter not available")


class TestContentQualityMetrics:
    """Test quality metrics and validation of generated content."""
    
    def test_readme_quality_scoring(self):
        """Test README quality scoring system."""
        try:
            from src.automation.readme_generator import ReadmeValidator
            
            validator = ReadmeValidator()
            
            # High quality README
            high_quality_readme = """
# Awesome Project

## Description
This is a comprehensive project that does amazing things.

## Installation
pip install awesome-project

## Usage
Run the project with awesome-project --help

## Features
- Feature 1
- Feature 2

## Examples
Here are some examples...

## Contributing
We welcome contributions!

## License
MIT License
"""
            
            validation = validator.validate_readme(high_quality_readme)
            assert validation['score'] >= 80, f"High quality README should score >=80, got {validation['score']}"
            assert validation['is_valid'] is True
            
            # Low quality README
            low_quality_readme = "# Project\n\nSome text."
            
            validation = validator.validate_readme(low_quality_readme)
            assert validation['score'] < 50, f"Low quality README should score <50, got {validation['score']}"
            
        except ImportError:
            pytest.skip("ReadmeValidator not available")
    
    def test_changelog_compliance_scoring(self):
        """Test CHANGELOG compliance scoring."""
        try:
            from src.automation.changelog_generator import ChangelogValidator
            
            validator = ChangelogValidator()
            
            # High compliance changelog
            compliant_changelog = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-01-01

### Added
- New feature implementation

### Changed
- Updated dependencies

### Fixed
- Bug fix for user authentication

### Security
- Security patch for vulnerability
"""
            
            validation = validator.validate_changelog(compliant_changelog)
            assert validation['compliance_score'] >= 80, f"Compliant changelog should score >=80, got {validation['compliance_score']}"
            
            # Low compliance changelog
            low_compliance_changelog = """
# Changes

- Made some changes
- Fixed stuff
"""
            
            validation = validator.validate_changelog(low_compliance_changelog)
            assert validation['compliance_score'] < 50, f"Non-compliant changelog should score <50, got {validation['compliance_score']}"
            
        except ImportError:
            pytest.skip("ChangelogValidator not available")
    
    def test_project_metrics_accuracy(self):
        """Test accuracy of calculated project metrics."""
        try:
            from src.automation.project_analyzer import ProjectMetrics
            
            # Precise project info
            project_info = {
                'src_files': ['file1.py', 'file2.py', 'file3.py'],  # 3 files
                'total_lines': 300,
                'total_functions': 15,
                'total_classes': 6,
                'test_files': ['test1.py'],  # 1 test file
                'api_endpoints': [{'path': '/api/v1'}, {'path': '/health'}],  # 2 endpoints
                'mcp_tools': [{'name': 'tool1'}, {'name': 'tool2'}, {'name': 'tool3'}]  # 3 tools
            }
            
            metrics = ProjectMetrics(project_info)
            calculated = metrics.calculate_complexity_metrics()
            
            # Verify exact calculations
            assert calculated['total_files'] == 3
            assert calculated['total_lines'] == 300
            assert calculated['total_functions'] == 15
            assert calculated['total_classes'] == 6
            assert calculated['functions_per_file'] == 5.0  # 15/3
            assert calculated['lines_per_file'] == 100.0    # 300/3
            assert calculated['api_endpoints'] == 2
            assert calculated['mcp_tools'] == 3
            assert calculated['test_coverage_ratio'] == 0.33  # 1 test file / 3 src files
            
        except ImportError:
            pytest.skip("ProjectMetrics not available")


class TestIdempotencyValidation:
    """Test that documentation generation is idempotent."""
    
    def test_readme_generation_idempotency(self):
        """Test that generating README multiple times produces same result."""
        try:
            from src.automation.readme_generator import ReadmeGenerator
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                project_info = {
                    'src_files': [temp_path / 'test.py'],
                    'total_lines': 100,
                    'total_functions': 5,
                    'total_classes': 2,
                    'test_files': [],
                    'dependencies': ['pytest'],
                    'mcp_tools': [{'name': 'test_tool', 'description': 'Test'}],
                    'api_endpoints': []
                }
                
                config = {'project_name': 'Test'}
                generator = ReadmeGenerator(temp_path, config)
                
                # Generate README twice
                first_result = asyncio.run(generator.generate_readme(project_info))
                second_result = asyncio.run(generator.generate_readme(project_info))
                
                # Remove timestamps for comparison
                first_clean = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'TIMESTAMP', first_result)
                second_clean = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'TIMESTAMP', second_result)
                
                assert first_clean == second_clean, "README generation should be idempotent"
                
        except ImportError:
            pytest.skip("ReadmeGenerator not available")
    
    def test_changelog_generation_idempotency(self):
        """Test that generating CHANGELOG multiple times produces consistent results."""
        try:
            from src.automation.changelog_generator import ChangelogGenerator
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                project_info = {
                    'total_functions': 10,
                    'total_classes': 3,
                    'test_files': ['test1.py'],
                    'dependencies': ['pytest', 'fastapi'],
                    'mcp_tools': [{'name': 'analyze', 'description': 'Analyze code'}]
                }
                
                config = {'changelog_format': 'keepachangelog'}
                generator = ChangelogGenerator(temp_path, config)
                
                # Generate CHANGELOG twice on same date
                first_result = asyncio.run(generator.generate_changelog(project_info))
                second_result = asyncio.run(generator.generate_changelog(project_info))
                
                # Remove timestamps for comparison
                first_clean = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'TIMESTAMP', first_result)
                second_clean = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', 'TIMESTAMP', second_result)
                
                # Should have same structure and content
                assert first_clean == second_clean, "CHANGELOG generation should be idempotent"
                
        except ImportError:
            pytest.skip("ChangelogGenerator not available")


def run_content_validation_tests():
    """Run all content validation tests."""
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, '-m', 'pytest', __file__, '-v', '--tb=short'
    ], capture_output=True, text=True)
    
    print("Content Validation Tests Results:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_content_validation_tests()
    sys.exit(0 if success else 1)