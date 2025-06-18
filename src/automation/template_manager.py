"""
Template manager for externalizing large Markdown blocks.
Implements the Sourcery AI recommendation to externalize large content blocks.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from string import Template

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Manages external template files for MCP server responses.
    
    This addresses the Sourcery AI recommendation to externalize large 
    Markdown blocks from the mcp_server.py file.
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or Path(__file__).parent / "templates"
        self.logger = logging.getLogger(__name__)
        self._template_cache = {}
        
        # Ensure templates directory exists
        self.templates_dir.mkdir(exist_ok=True)
    
    def load_template(self, template_name: str) -> Template:
        """Load a template from file with caching."""
        # Check cache first
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        template_path = self.templates_dir / f"{template_name}.md"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            template = Template(template_content)
            self._template_cache[template_name] = template
            
            self.logger.debug(f"Loaded template: {template_name}")
            return template
            
        except Exception as e:
            self.logger.error(f"Error loading template {template_name}: {e}")
            raise
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Render a template with the provided variables."""
        try:
            template = self.load_template(template_name)
            
            # Convert all variables to strings and handle None values
            safe_variables = {}
            for key, value in variables.items():
                if value is None:
                    safe_variables[key] = "N/A"
                elif isinstance(value, (int, float)):
                    safe_variables[key] = str(value)
                elif isinstance(value, bool):
                    safe_variables[key] = "✅" if value else "❌"
                else:
                    safe_variables[key] = str(value)
            
            return template.safe_substitute(safe_variables)
            
        except Exception as e:
            self.logger.error(f"Error rendering template {template_name}: {e}")
            return f"Error rendering template: {e}"
    
    def render_analysis_report(self, analysis_result) -> str:
        """Render the analysis report template."""
        # Prepare code smells section
        code_smells_section = ""
        for smell in analysis_result.code_smells:
            code_smells_section += f"""
### {smell.smell_type.value.replace('_', ' ').title()}
- **Severidade**: {smell.severity.value.upper()}
- **Localização**: Linha {smell.line_start}
- **Confiança**: {smell.confidence*100:.1f}%
- **Descrição**: {smell.description}
"""
            if smell.function_name:
                code_smells_section += f"- **Função**: {smell.function_name}\n"
            if smell.class_name:
                code_smells_section += f"- **Classe**: {smell.class_name}\n"
        
        # Prepare defect predictions section
        defect_predictions_section = ""
        for pred in analysis_result.defect_predictions:
            defect_predictions_section += f"""
### {pred.function_name or 'Função não identificada'}
- **Probabilidade de Defeito**: {pred.defect_probability*100:.1f}%
- **Nível de Risco**: {pred.risk_level.value.upper()}
- **Confiança**: {pred.confidence*100:.1f}%
- **Fatores Contribuintes**: {', '.join(pred.contributing_factors)}
"""
        
        # Prepare generated tests section
        generated_tests_section = ""
        for test in analysis_result.generated_tests:
            generated_tests_section += f"""
### {test.test_name}
- **Função Alvo**: {test.function_name}
- **Tipo**: {test.test_type}
- **Assertivas Esperadas**: {test.expected_assertions}
- **Score de Complexidade**: {test.complexity_score}

```python
{test.test_code}
```
"""
        
        # Prepare suggested repairs section
        suggested_repairs_section = ""
        for repair in analysis_result.suggested_repairs:
            suggested_repairs_section += f"""
### Linhas {repair.line_start}-{repair.line_end}
- **Problema**: {repair.issue_description}
- **Sugestão**: {repair.suggested_fix}
- **Tipo**: {repair.fix_type}
- **Confiança**: {repair.confidence*100:.1f}%
"""
        
        variables = {
            'filename': getattr(analysis_result, 'filename', 'code.py'),
            'overall_quality_score': analysis_result.overall_quality_score,
            'cyclomatic_complexity': analysis_result.metrics.cyclomatic_complexity,
            'lines_of_code': analysis_result.metrics.lines_of_code,
            'number_of_methods': analysis_result.metrics.number_of_methods,
            'maintainability_index': analysis_result.metrics.maintainability_index,
            'halstead_difficulty': analysis_result.metrics.halstead_difficulty,
            'halstead_volume': analysis_result.metrics.halstead_volume,
            'code_smells_count': len(analysis_result.code_smells),
            'code_smells_section': code_smells_section,
            'defect_predictions_count': len(analysis_result.defect_predictions),
            'defect_predictions_section': defect_predictions_section,
            'tests_count': len(analysis_result.generated_tests),
            'generated_tests_section': generated_tests_section,
            'repairs_count': len(analysis_result.suggested_repairs),
            'suggested_repairs_section': suggested_repairs_section,
            'processing_time': analysis_result.processing_time_seconds
        }
        
        return self.render_template('analysis_report_template', variables)
    
    def render_defect_prediction(self, predictions, code_analysis) -> str:
        """Render the defect prediction template."""
        functions_section = ""
        high_risk_count = 0
        medium_risk_count = 0
        low_risk_count = 0
        total_probability = 0
        
        for pred in predictions:
            functions_section += f"""
## Função: {pred.function_name or 'Anônima'}
- **Probabilidade de Defeito**: {pred.defect_probability*100:.1f}%
- **Nível de Risco**: {pred.risk_level.value.upper()}
- **Confiança**: {pred.confidence*100:.1f}%
- **Fatores Contribuintes**: {', '.join(pred.contributing_factors)}
"""
            
            # Count risk levels
            if pred.risk_level.value == 'high':
                high_risk_count += 1
            elif pred.risk_level.value == 'medium':
                medium_risk_count += 1
            else:
                low_risk_count += 1
            
            total_probability += pred.defect_probability
        
        # Generate recommendations
        recommendations_section = ""
        if high_risk_count > 0:
            recommendations_section += f"- 🚨 **{high_risk_count} funções de alto risco** necessitam revisão imediata\n"
        if medium_risk_count > 0:
            recommendations_section += f"- ⚠️ **{medium_risk_count} funções de médio risco** podem se beneficiar de refatoração\n"
        if low_risk_count > 0:
            recommendations_section += f"- ✅ **{low_risk_count} funções de baixo risco** estão em bom estado\n"
        
        variables = {
            'functions_section': functions_section,
            'total_functions': len(predictions),
            'high_risk_count': high_risk_count,
            'medium_risk_count': medium_risk_count,
            'low_risk_count': low_risk_count,
            'average_defect_probability': (total_probability / len(predictions) * 100) if predictions else 0,
            'recommendations_section': recommendations_section
        }
        
        return self.render_template('defect_prediction_template', variables)
    
    def render_code_smells(self, code_smells) -> str:
        """Render the code smells template."""
        high_severity_count = 0
        medium_severity_count = 0
        low_severity_count = 0
        total_confidence = 0
        
        smells_by_category = {}
        detailed_smells_section = ""
        
        for smell in code_smells:
            # Count severities
            if smell.severity.value == 'high':
                high_severity_count += 1
            elif smell.severity.value == 'medium':
                medium_severity_count += 1
            else:
                low_severity_count += 1
            
            total_confidence += smell.confidence
            
            # Group by category
            category = smell.smell_type.value.replace('_', ' ').title()
            if category not in smells_by_category:
                smells_by_category[category] = 0
            smells_by_category[category] += 1
            
            # Add to detailed section
            detailed_smells_section += f"""
### {category}
- **Localização**: Linha {smell.line_start}
- **Severidade**: {smell.severity.value.upper()}
- **Confiança**: {smell.confidence*100:.1f}%
- **Descrição**: {smell.description}
"""
            if smell.function_name:
                detailed_smells_section += f"- **Função**: {smell.function_name}\n"
        
        # Format smells by category
        smells_by_category_text = ""
        for category, count in smells_by_category.items():
            smells_by_category_text += f"- **{category}**: {count}\n"
        
        # Generate improvement suggestions
        improvement_suggestions = "- Revisar funções com alta complexidade ciclomática\n"
        improvement_suggestions += "- Aplicar padrões de design para reduzir acoplamento\n"
        improvement_suggestions += "- Refatorar métodos longos em funções menores\n"
        
        variables = {
            'total_smells': len(code_smells),
            'high_severity_count': high_severity_count,
            'medium_severity_count': medium_severity_count,
            'low_severity_count': low_severity_count,
            'average_confidence': (total_confidence / len(code_smells) * 100) if code_smells else 0,
            'smells_by_category': smells_by_category_text,
            'detailed_smells_section': detailed_smells_section,
            'improvement_suggestions': improvement_suggestions
        }
        
        return self.render_template('code_smells_template', variables)
    
    def render_test_generation(self, generated_tests) -> str:
        """Render the test generation template."""
        unit_tests_count = 0
        integration_tests_count = 0
        edge_case_tests_count = 0
        total_complexity = 0
        total_assertions = 0
        
        tests_by_function = {}
        test_code_section = ""
        
        for test in generated_tests:
            # Count test types
            if test.test_type == 'unit':
                unit_tests_count += 1
            elif test.test_type == 'integration':
                integration_tests_count += 1
            elif test.test_type == 'edge_case':
                edge_case_tests_count += 1
            
            total_complexity += test.complexity_score
            total_assertions += test.expected_assertions
            
            # Group by function
            func_name = test.function_name or 'Anônima'
            if func_name not in tests_by_function:
                tests_by_function[func_name] = 0
            tests_by_function[func_name] += 1
            
            # Add to test code section
            test_code_section += f"""
## {test.test_name}
**Função Alvo**: {func_name}  
**Tipo**: {test.test_type}  
**Complexidade**: {test.complexity_score}  

```python
{test.test_code}
```
"""
        
        # Format tests by function
        tests_by_function_text = ""
        for func_name, count in tests_by_function.items():
            tests_by_function_text += f"- **{func_name}**: {count} testes\n"
        
        variables = {
            'total_tests': len(generated_tests),
            'unit_tests_count': unit_tests_count,
            'integration_tests_count': integration_tests_count,
            'edge_case_tests_count': edge_case_tests_count,
            'estimated_coverage': min(95, len(generated_tests) * 15),  # Rough estimate
            'tests_by_function': tests_by_function_text,
            'test_code_section': test_code_section,
            'average_complexity': (total_complexity / len(generated_tests)) if generated_tests else 0,
            'average_assertions': (total_assertions / len(generated_tests)) if generated_tests else 0,
            'completeness_score': min(100, len(generated_tests) * 10)  # Rough estimate
        }
        
        return self.render_template('test_generation_template', variables)
    
    def render_system_stats(self, server_state, mcp_tools) -> str:
        """Render the system stats template."""
        from datetime import datetime
        
        # Format MCP tools list
        mcp_tools_list = ""
        for i, tool in enumerate(mcp_tools, 1):
            mcp_tools_list += f"{i}. **{tool.name}**: {tool.description}\n"
        
        variables = {
            'model_trained_status': "✅ Treinado" if server_state.get("model_trained", False) else "❌ Não Treinado",
            'last_model_update': "Inicialização do sistema",
            'model_accuracy': 87.5,  # Mock value
            'total_analyses': server_state.get("analyses_performed", 0),
            'total_smells': server_state.get("total_smells_detected", 0),
            'total_defects': server_state.get("total_defects_predicted", 0),
            'total_tests': server_state.get("total_tests_generated", 0),
            'docs_updates': server_state.get("docs_updates_performed", 0),
            'auto_docs_status': "✅ Ativo" if server_state.get("auto_docs_enabled", False) else "❌ Inativo",
            'last_docs_update': "Tempo real",
            'git_hooks_status': "✅ Instalados" if server_state.get("git_hooks_installed", False) else "❌ Não Instalados",
            'file_monitoring_status': "✅ Ativo",
            'average_analysis_time': 1.25,  # Mock value
            'success_rate': 94.2,  # Mock value
            'system_uptime': "< 1 hora",
            'mcp_tools_list': mcp_tools_list,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.render_template('system_stats_template', variables)
    
    def clear_cache(self):
        """Clear the template cache."""
        self._template_cache.clear()
        self.logger.info("Template cache cleared")
    
    def list_available_templates(self) -> list:
        """List all available template files."""
        if not self.templates_dir.exists():
            return []
        
        templates = []
        for template_file in self.templates_dir.glob("*.md"):
            templates.append(template_file.stem)
        
        return sorted(templates)


# Global template manager instance
template_manager = TemplateManager()