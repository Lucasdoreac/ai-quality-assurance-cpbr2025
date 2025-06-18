#!/usr/bin/env python3
"""
Security tests to validate fixes for vulnerabilities identified by CodeRabbit and Sourcery AI.
"""

import pytest
import subprocess
import tempfile
import shlex
from pathlib import Path
from unittest.mock import patch, Mock
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.setup_automation_secure import SecureSubprocessRunner, AutomationSetup
except ImportError:
    # Handle case where secure version doesn't exist yet
    SecureSubprocessRunner = None
    AutomationSetup = None


class TestSecurityFixes:
    """Test security improvements and vulnerability fixes."""
    
    def test_secure_subprocess_runner_exists(self):
        """Test that SecureSubprocessRunner class exists."""
        assert SecureSubprocessRunner is not None, "SecureSubprocessRunner should be implemented"
    
    def test_secure_subprocess_runner_initialization(self):
        """Test SecureSubprocessRunner can be initialized."""
        if SecureSubprocessRunner is None:
            pytest.skip("SecureSubprocessRunner not available")
        
        runner = SecureSubprocessRunner()
        assert runner is not None
    
    def test_safe_run_with_list_command(self):
        """Test safe_run method with list command (no shell injection risk)."""
        if SecureSubprocessRunner is None:
            pytest.skip("SecureSubprocessRunner not available")
        
        runner = SecureSubprocessRunner()
        
        # Test with safe command
        cmd = ['python', '--version']
        result = runner.safe_run(cmd)
        
        assert result is not None
        assert hasattr(result, 'returncode')
        assert hasattr(result, 'stdout')
        assert hasattr(result, 'stderr')
    
    def test_safe_run_prevents_shell_injection(self):
        """Test that safe_run prevents shell injection attempts."""
        if SecureSubprocessRunner is None:
            pytest.skip("SecureSubprocessRunner not available")
        
        runner = SecureSubprocessRunner()
        
        # Test that shell is always False
        with patch('subprocess.run') as mock_run:
            cmd = ['echo', 'test']
            runner.safe_run(cmd)
            
            # Verify subprocess.run was called with shell=False
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[1]['shell'] is False
    
    def test_safe_run_rejects_non_list_commands(self):
        """Test that safe_run rejects non-list commands."""
        if SecureSubprocessRunner is None:
            pytest.skip("SecureSubprocessRunner not available")
        
        runner = SecureSubprocessRunner()
        
        # Test with string command (potential injection risk)
        with pytest.raises(ValueError, match="Command must be a list"):
            runner.safe_run("echo 'test'")
    
    def test_dependency_validation(self):
        """Test dependency validation against allowed lists."""
        if AutomationSetup is None:
            pytest.skip("AutomationSetup not available")
        
        setup = AutomationSetup(Path.cwd())
        
        # Test allowed dependency
        assert setup._validate_dependency('watchdog') is True
        assert setup._validate_dependency('GitPython') is True
        
        # Test disallowed dependency
        assert setup._validate_dependency('malicious-package') is False
        assert setup._validate_dependency('unknown-dep') is False
    
    def test_dependency_validation_with_version_specifiers(self):
        """Test dependency validation with version specifiers."""
        if AutomationSetup is None:
            pytest.skip("AutomationSetup not available")
        
        setup = AutomationSetup(Path.cwd())
        
        # Test with version specifiers
        assert setup._validate_dependency('watchdog>=2.0.0') is True
        assert setup._validate_dependency('GitPython==3.1.0') is True
        assert setup._validate_dependency('fastapi~=0.95.0') is True
    
    def test_path_resolution_security(self):
        """Test that paths are resolved securely."""
        if AutomationSetup is None:
            pytest.skip("AutomationSetup not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            setup = AutomationSetup(Path(temp_dir))
            
            # Verify project_root is resolved to absolute path
            assert setup.project_root.is_absolute()
            assert setup.project_root.resolve() == Path(temp_dir).resolve()
    
    def test_logging_configuration_security(self):
        """Test that logging is configured securely."""
        if AutomationSetup is None:
            pytest.skip("AutomationSetup not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            setup = AutomationSetup(Path(temp_dir))
            
            # Verify log directory is created safely
            log_dir = setup.project_root / 'logs'
            assert log_dir.exists()
            assert log_dir.is_dir()
    
    def test_config_loading_handles_malformed_files(self):
        """Test that config loading handles malformed files safely."""
        if AutomationSetup is None:
            pytest.skip("AutomationSetup not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create malformed config file
            config_dir = temp_path / 'config'
            config_dir.mkdir()
            config_file = config_dir / 'automation_config.yaml'
            
            # Write malformed YAML
            with open(config_file, 'w') as f:
                f.write("invalid: yaml: content: [")
            
            # Should not crash, should use default config
            setup = AutomationSetup(temp_path, config_file)
            assert setup.config is not None
            assert 'project' in setup.config


class TestFileWatcherOptimizations:
    """Test file watcher performance optimizations."""
    
    def test_file_watcher_optimized_exists(self):
        """Test that optimized file watcher module exists."""
        try:
            from src.automation.file_watcher_optimized import OptimizedAutoDocsWatcher
            assert OptimizedAutoDocsWatcher is not None
        except ImportError:
            pytest.fail("OptimizedAutoDocsWatcher should be available")
    
    def test_no_inefficient_sleep_loops(self):
        """Test that file watcher doesn't use inefficient sleep loops."""
        try:
            from src.automation.file_watcher_optimized import main
            import inspect
            
            # Get source code of main function
            source = inspect.getsource(main)
            
            # Should not contain time.sleep(1) in a loop
            assert 'time.sleep(1)' not in source, "Inefficient sleep loop found"
            
            # Should use event-based waiting
            assert 'wait_for_stop' in source or 'Event' in source, "Should use event-based waiting"
            
        except ImportError:
            pytest.fail("Optimized file watcher should be available")
    
    def test_event_based_waiting(self):
        """Test that event-based waiting is implemented."""
        try:
            from src.automation.file_watcher_optimized import OptimizedAutoDocsWatcher
            
            # Create watcher instance
            watcher = OptimizedAutoDocsWatcher(Path.cwd())
            
            # Verify wait_for_stop method exists
            assert hasattr(watcher, 'wait_for_stop'), "Event-based waiting should be implemented"
            
        except ImportError:
            pytest.fail("OptimizedAutoDocsWatcher should be available")


class TestModularRefactoring:
    """Test that modular refactoring was implemented correctly."""
    
    def test_project_analyzer_exists(self):
        """Test that ProjectAnalyzer was separated from DocumentationGenerator."""
        try:
            from src.automation.project_analyzer import ProjectAnalyzer
            assert ProjectAnalyzer is not None
        except ImportError:
            pytest.fail("ProjectAnalyzer should be separated into its own module")
    
    def test_readme_generator_exists(self):
        """Test that ReadmeGenerator was separated."""
        try:
            from src.automation.readme_generator import ReadmeGenerator
            assert ReadmeGenerator is not None
        except ImportError:
            pytest.fail("ReadmeGenerator should be separated into its own module")
    
    def test_changelog_generator_exists(self):
        """Test that ChangelogGenerator was separated."""
        try:
            from src.automation.changelog_generator import ChangelogGenerator
            assert ChangelogGenerator is not None
        except ImportError:
            pytest.fail("ChangelogGenerator should be separated into its own module")
    
    def test_documentation_orchestrator_exists(self):
        """Test that DocumentationOrchestrator coordinates the components."""
        try:
            from src.automation.documentation_orchestrator import DocumentationOrchestrator
            assert DocumentationOrchestrator is not None
        except ImportError:
            pytest.fail("DocumentationOrchestrator should coordinate separated components")
    
    def test_event_handler_separation(self):
        """Test that event handling was separated from file watcher."""
        try:
            from src.automation.event_handler import SmartEventHandler
            assert SmartEventHandler is not None
        except ImportError:
            pytest.fail("SmartEventHandler should be separated from file watcher")
    
    def test_watcher_manager_separation(self):
        """Test that watcher management was separated."""
        try:
            from src.automation.watcher_manager import WatcherManager
            assert WatcherManager is not None
        except ImportError:
            pytest.fail("WatcherManager should be separated into its own module")


class TestTemplateExternalization:
    """Test that Markdown templates were externalized."""
    
    def test_template_manager_exists(self):
        """Test that TemplateManager was created."""
        try:
            from src.automation.template_manager import TemplateManager
            assert TemplateManager is not None
        except ImportError:
            pytest.fail("TemplateManager should be available")
    
    def test_template_files_exist(self):
        """Test that template files were created."""
        templates_dir = Path(__file__).parent.parent / 'src' / 'automation' / 'templates'
        
        expected_templates = [
            'analysis_report_template.md',
            'defect_prediction_template.md',
            'code_smells_template.md',
            'test_generation_template.md',
            'system_stats_template.md'
        ]
        
        for template in expected_templates:
            template_path = templates_dir / template
            assert template_path.exists(), f"Template {template} should exist"
    
    def test_template_loading(self):
        """Test that templates can be loaded."""
        try:
            from src.automation.template_manager import TemplateManager
            
            templates_dir = Path(__file__).parent.parent / 'src' / 'automation' / 'templates'
            if not templates_dir.exists():
                pytest.skip("Templates directory not found")
            
            manager = TemplateManager(templates_dir)
            
            # Test loading a template
            try:
                template = manager.load_template('analysis_report_template')
                assert template is not None
            except FileNotFoundError:
                pytest.skip("Template files not available")
                
        except ImportError:
            pytest.fail("TemplateManager should be available")
    
    def test_template_rendering(self):
        """Test that templates can be rendered with variables."""
        try:
            from src.automation.template_manager import TemplateManager
            
            templates_dir = Path(__file__).parent.parent / 'src' / 'automation' / 'templates'
            if not templates_dir.exists():
                pytest.skip("Templates directory not found")
            
            manager = TemplateManager(templates_dir)
            
            # Test rendering with variables
            variables = {
                'filename': 'test.py',
                'overall_quality_score': 85.5,
                'cyclomatic_complexity': 3,
                'lines_of_code': 100
            }
            
            try:
                result = manager.render_template('analysis_report_template', variables)
                assert 'test.py' in result
                assert '85.5' in result
            except FileNotFoundError:
                pytest.skip("Template files not available")
                
        except ImportError:
            pytest.fail("TemplateManager should be available")


class TestErrorHandlingImprovements:
    """Test improved error handling and resilience."""
    
    def test_graceful_import_errors(self):
        """Test that import errors are handled gracefully."""
        # This test ensures that missing dependencies don't crash the system
        
        # Mock a missing module
        with patch.dict('sys.modules', {'non_existent_module': None}):
            try:
                # This should not crash
                from src.automation.documentation_orchestrator import DocumentationOrchestrator
                orchestrator = DocumentationOrchestrator(Path.cwd())
                assert orchestrator is not None
            except ImportError:
                # ImportError is acceptable for missing dependencies
                pass
            except Exception as e:
                pytest.fail(f"Should handle missing dependencies gracefully, got: {e}")
    
    def test_file_operation_error_handling(self):
        """Test that file operations handle errors gracefully."""
        try:
            from src.automation.project_analyzer import ProjectAnalyzer
            
            # Test with non-existent directory
            analyzer = ProjectAnalyzer(Path('/non/existent/path'))
            
            # Should not crash
            result = analyzer.analyze_project()
            assert isinstance(result, dict)
            
        except ImportError:
            pytest.skip("ProjectAnalyzer not available")
    
    def test_malformed_file_handling(self):
        """Test handling of malformed Python files."""
        try:
            from src.automation.project_analyzer import ProjectAnalyzer
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create malformed Python file
                malformed_file = temp_path / 'malformed.py'
                with open(malformed_file, 'w') as f:
                    f.write("def incomplete_function(\n# Missing closing parenthesis")
                
                analyzer = ProjectAnalyzer(temp_path)
                
                # Should handle malformed files gracefully
                result = analyzer._analyze_python_file(malformed_file)
                assert isinstance(result, dict)
                
        except ImportError:
            pytest.skip("ProjectAnalyzer not available")


class TestContentValidation:
    """Test content validation and quality checks."""
    
    def test_readme_validation(self):
        """Test README content validation."""
        try:
            from src.automation.readme_generator import ReadmeValidator
            
            validator = ReadmeValidator()
            
            # Test valid README content
            valid_content = """
# Test Project

This is a test project description.

## Installation

pip install test

## Usage

Run the application.
"""
            
            validation = validator.validate_readme(valid_content)
            assert validation['is_valid'] is True
            assert validation['score'] > 0
            
            # Test invalid README (missing required sections)
            invalid_content = "# Test"
            
            validation = validator.validate_readme(invalid_content)
            assert validation['score'] < 100
            assert len(validation['missing_required']) > 0
            
        except ImportError:
            pytest.skip("ReadmeValidator not available")
    
    def test_changelog_validation(self):
        """Test CHANGELOG content validation."""
        try:
            from src.automation.changelog_generator import ChangelogValidator
            
            validator = ChangelogValidator()
            
            # Test valid changelog content
            valid_content = """
# Changelog

## [Unreleased] - 2025-01-01

### Added
- New feature

### Fixed
- Bug fix
"""
            
            validation = validator.validate_changelog(valid_content)
            assert validation['is_valid'] is True
            assert validation['compliance_score'] > 0
            
        except ImportError:
            pytest.skip("ChangelogValidator not available")
    
    def test_metrics_calculation(self):
        """Test project metrics calculation."""
        try:
            from src.automation.project_analyzer import ProjectMetrics
            
            # Mock project info
            project_info = {
                'src_files': ['file1.py', 'file2.py'],
                'total_lines': 200,
                'total_functions': 10,
                'total_classes': 3,
                'test_files': ['test1.py'],
                'api_endpoints': [],
                'mcp_tools': []
            }
            
            metrics = ProjectMetrics(project_info)
            complexity_metrics = metrics.calculate_complexity_metrics()
            
            assert 'total_files' in complexity_metrics
            assert 'functions_per_file' in complexity_metrics
            assert 'lines_per_file' in complexity_metrics
            assert complexity_metrics['total_files'] == 2
            assert complexity_metrics['functions_per_file'] == 5.0
            
        except ImportError:
            pytest.skip("ProjectMetrics not available")


def run_security_tests():
    """Run all security tests."""
    import subprocess
    import sys
    
    # Run pytest on this file
    result = subprocess.run([
        sys.executable, '-m', 'pytest', __file__, '-v'
    ], capture_output=True, text=True)
    
    print("Security Tests Results:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)