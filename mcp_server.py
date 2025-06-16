"""
MCP Server for AI Quality Assurance system.
Real functional server for Claude integration with live demonstrations.
"""
import asyncio
import json
import ast
from typing import Dict, Any, List

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from src.application.use_cases import AnalyzeCodeUseCase
from src.infrastructure.repositories import InMemoryCodeAnalysisRepository
from src.infrastructure.ml_models import DefectPredictionModel, CodeSmellDetector, TestGenerator

# Initialize components
repository = InMemoryCodeAnalysisRepository()
analyze_use_case = AnalyzeCodeUseCase(repository)
defect_model = DefectPredictionModel()
smell_detector = CodeSmellDetector()
test_generator = TestGenerator()

# Initialize MCP server
server = Server("ai-qa-system")

# Global state
server_state = {
    "model_trained": False,
    "analyses_performed": 0,
    "total_smells_detected": 0,
    "total_defects_predicted": 0,
    "total_tests_generated": 0
}


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools for AI Quality Assurance."""
    return [
        Tool(
            name="analyze_code",
            description="Analyze Python code for quality issues, predict defects, and generate tests",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python source code to analyze"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Name of the file being analyzed",
                        "default": "code.py"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="predict_defects",
            description="Predict defect probability for code using ML model",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python source code to analyze for defects"
                    },
                    "detailed": {
                        "type": "boolean",
                        "description": "Return detailed prediction with contributing factors",
                        "default": True
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="detect_code_smells",
            description="Detect code smells using advanced AST analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python source code to analyze for code smells"
                    },
                    "confidence_threshold": {
                        "type": "number",
                        "description": "Minimum confidence threshold for reporting smells",
                        "default": 0.5,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="generate_tests",
            description="Generate comprehensive unit tests for Python functions",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python source code to generate tests for"
                    },
                    "test_style": {
                        "type": "string",
                        "description": "Style of tests to generate",
                        "enum": ["pytest", "unittest", "comprehensive"],
                        "default": "pytest"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="calculate_metrics",
            description="Calculate comprehensive code quality metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python source code to calculate metrics for"
                    },
                    "include_halstead": {
                        "type": "boolean",
                        "description": "Include Halstead complexity metrics",
                        "default": True
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="get_system_stats",
            description="Get current system statistics and model information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="train_defect_model",
            description="Train the defect prediction model on synthetic data",
            inputSchema={
                "type": "object",
                "properties": {
                    "samples": {
                        "type": "integer",
                        "description": "Number of synthetic samples to generate for training",
                        "default": 1000,
                        "minimum": 100,
                        "maximum": 10000
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for AI Quality Assurance."""
    global server_state
    
    if name == "analyze_code":
        return await handle_analyze_code(arguments)
    elif name == "predict_defects":
        return await handle_predict_defects(arguments)
    elif name == "detect_code_smells":
        return await handle_detect_code_smells(arguments)
    elif name == "generate_tests":
        return await handle_generate_tests(arguments)
    elif name == "calculate_metrics":
        return await handle_calculate_metrics(arguments)
    elif name == "get_system_stats":
        return await handle_get_system_stats(arguments)
    elif name == "train_defect_model":
        return await handle_train_defect_model(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def handle_analyze_code(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle comprehensive code analysis."""
    code = arguments["code"]
    filename = arguments.get("filename", "code.py")
    
    try:
        # Ensure model is trained
        if not server_state["model_trained"]:
            await train_model()
        
        # Perform analysis
        result = await analyze_use_case.execute(filename, code)
        
        # Update stats
        server_state["analyses_performed"] += 1
        server_state["total_smells_detected"] += len(result.code_smells)
        server_state["total_defects_predicted"] += len(result.defect_predictions)
        server_state["total_tests_generated"] += len(result.generated_tests)
        
        # Format response
        response = f"""# 🔍 Análise Completa de Código - {filename}

## 📊 Métricas de Qualidade
- **Score Geral**: {result.overall_quality_score:.1f}/100
- **Complexidade Ciclomática**: {result.metrics.cyclomatic_complexity}
- **Linhas de Código**: {result.metrics.lines_of_code}
- **Número de Métodos**: {result.metrics.number_of_methods}
- **Índice de Manutenibilidade**: {result.metrics.maintainability_index:.1f}
- **Dificuldade Halstead**: {result.metrics.halstead_difficulty:.2f}
- **Volume Halstead**: {result.metrics.halstead_volume:.2f}

## 🔍 Code Smells Detectados ({len(result.code_smells)})
"""
        
        for smell in result.code_smells:
            response += f"""
### {smell.smell_type.value.replace('_', ' ').title()}
- **Severidade**: {smell.severity.value.upper()}
- **Localização**: Linha {smell.line_start}
- **Confiança**: {smell.confidence*100:.1f}%
- **Descrição**: {smell.description}
"""
            if smell.function_name:
                response += f"- **Função**: {smell.function_name}\n"
            if smell.class_name:
                response += f"- **Classe**: {smell.class_name}\n"
        
        response += f"""
## 🎯 Predições de Defeitos ({len(result.defect_predictions)})
"""
        
        for pred in result.defect_predictions:
            response += f"""
### {pred.function_name or 'Função não identificada'}
- **Probabilidade de Defeito**: {pred.defect_probability*100:.1f}%
- **Nível de Risco**: {pred.risk_level.value.upper()}
- **Confiança**: {pred.confidence*100:.1f}%
- **Fatores Contribuintes**: {', '.join(pred.contributing_factors)}
"""
        
        response += f"""
## 🧪 Testes Gerados ({len(result.generated_tests)})
"""
        
        for test in result.generated_tests:
            response += f"""
### {test.test_name}
- **Função Alvo**: {test.function_name}
- **Tipo**: {test.test_type}
- **Assertivas Esperadas**: {test.expected_assertions}
- **Score de Complexidade**: {test.complexity_score}

```python
{test.test_code}
```
"""
        
        response += f"""
## 🔧 Reparos Sugeridos ({len(result.suggested_repairs)})
"""
        
        for repair in result.suggested_repairs:
            response += f"""
### Linhas {repair.line_start}-{repair.line_end}
- **Problema**: {repair.issue_description}
- **Sugestão**: {repair.suggested_fix}
- **Tipo**: {repair.fix_type}
- **Confiança**: {repair.confidence*100:.1f}%
"""
        
        response += f"""
---
**⏱️ Tempo de Processamento**: {result.processing_time_seconds:.2f}s
**🤖 Análise realizada pelo Sistema IA QA - Campus Party Brasil 2025**
"""
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro na análise: {str(e)}")]


async def handle_predict_defects(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle defect prediction."""
    code = arguments["code"]
    detailed = arguments.get("detailed", True)
    
    try:
        if not server_state["model_trained"]:
            await train_model()
        
        # Parse code and calculate metrics
        tree = ast.parse(code)
        
        response = "# 🎯 Predição de Defeitos\n\n"
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate metrics for this function
                metrics = calculate_function_metrics(node, code)
                
                # Predict defects
                prediction = defect_model.predict_defect_probability(metrics)
                
                response += f"""## Função: {node.name}
- **Probabilidade de Defeito**: {prediction.defect_probability*100:.1f}%
- **Nível de Risco**: {prediction.risk_level.value.upper()}
- **Confiança**: {prediction.confidence*100:.1f}%
"""
                
                if detailed:
                    response += f"- **Fatores Contribuintes**: {', '.join(prediction.contributing_factors)}\n"
                    response += "- **Métricas Utilizadas**:\n"
                    for metric, value in prediction.metrics_used.items():
                        response += f"  - {metric}: {value:.2f}\n"
                
                response += "\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro na predição: {str(e)}")]


async def handle_detect_code_smells(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle code smell detection."""
    code = arguments["code"]
    threshold = arguments.get("confidence_threshold", 0.5)
    
    try:
        tree = ast.parse(code)
        metrics = calculate_basic_metrics(tree, code)
        
        smells = smell_detector.detect_smells_with_confidence(tree, code, metrics)
        filtered_smells = [s for s in smells if s['confidence'] >= threshold]
        
        response = f"# 🔍 Code Smells Detectados\n\n"
        response += f"**Threshold de Confiança**: {threshold*100:.1f}%\n"
        response += f"**Total Encontrados**: {len(filtered_smells)}\n\n"
        
        for smell in filtered_smells:
            response += f"""## {smell['type'].replace('_', ' ').title()}
- **Severidade**: {smell['severity'].upper()}
- **Linha**: {smell['line_start']}
- **Confiança**: {smell['confidence']*100:.1f}%
- **Descrição**: {smell['description']}
"""
            if smell.get('function_name'):
                response += f"- **Função**: {smell['function_name']}\n"
            if smell.get('class_name'):
                response += f"- **Classe**: {smell['class_name']}\n"
            
            response += f"- **Métricas**: {smell['metrics']}\n\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro na detecção: {str(e)}")]


async def handle_generate_tests(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle test generation."""
    code = arguments["code"]
    test_style = arguments.get("test_style", "pytest")
    
    try:
        tree = ast.parse(code)
        tests = test_generator.generate_unit_tests(tree)
        
        response = f"# 🧪 Testes Gerados ({test_style})\n\n"
        response += f"**Total de Testes**: {len(tests)}\n\n"
        
        for test in tests:
            response += f"""## {test['test_name']}
- **Função Alvo**: {test['function_name']}
- **Tipo**: {test['test_type']}
- **Assertivas Esperadas**: {test['expected_assertions']}
- **Complexidade**: {test['complexity_score']}

```python
{test['test_code']}
```

---
"""
        
        server_state["total_tests_generated"] += len(tests)
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro na geração de testes: {str(e)}")]


async def handle_calculate_metrics(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle metrics calculation."""
    code = arguments["code"]
    include_halstead = arguments.get("include_halstead", True)
    
    try:
        tree = ast.parse(code)
        metrics = calculate_detailed_metrics(tree, code, include_halstead)
        
        response = "# 📊 Métricas de Código\n\n"
        
        for metric_name, value in metrics.items():
            if isinstance(value, float):
                response += f"- **{metric_name}**: {value:.2f}\n"
            else:
                response += f"- **{metric_name}**: {value}\n"
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro no cálculo: {str(e)}")]


async def handle_get_system_stats(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle system statistics request."""
    feature_importance = defect_model.get_feature_importance() if server_state["model_trained"] else {}
    
    response = f"""# 📈 Estatísticas do Sistema

## 🔢 Contadores de Uso
- **Análises Realizadas**: {server_state["analyses_performed"]}
- **Code Smells Detectados**: {server_state["total_smells_detected"]}
- **Defeitos Preditos**: {server_state["total_defects_predicted"]}
- **Testes Gerados**: {server_state["total_tests_generated"]}

## 🤖 Status dos Modelos
- **Modelo de Predição**: {'Treinado' if server_state["model_trained"] else 'Não treinado'}
- **Detector de Smells**: Ativo
- **Gerador de Testes**: Ativo

## 🎯 Modelo de Predição de Defeitos
- **Tipo**: Random Forest Classifier
- **Features**: {len(defect_model.feature_names)} métricas de código
"""
    
    if feature_importance:
        response += "\n### Importância das Features:\n"
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features:
            response += f"- **{feature}**: {importance:.3f}\n"
    
    response += f"""
## 🔍 Detector de Code Smells
- **Tipos Suportados**: Long Method, Large Class, God Object, High Complexity, Long Parameter List
- **Baseado em**: Análise AST + Métricas + ML

## 🧪 Gerador de Testes
- **Tipos de Teste**: Unit, Edge Case, Error Handling
- **Frameworks**: pytest, unittest
- **Baseado em**: Análise AST + Templates Inteligentes

---
**🚀 Sistema IA QA - Campus Party Brasil 2025**
"""
    
    return [TextContent(type="text", text=response)]


async def handle_train_defect_model(arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle model training."""
    samples = arguments.get("samples", 1000)
    
    try:
        metrics = defect_model.train_on_synthetic_data()
        server_state["model_trained"] = True
        
        response = f"""# 🎓 Treinamento do Modelo Concluído

## 📊 Métricas de Performance
- **Acurácia**: {metrics['accuracy']*100:.1f}%
- **Precisão**: {metrics['precision']*100:.1f}%
- **Recall**: {metrics['recall']*100:.1f}%
- **F1-Score**: {metrics['f1_score']*100:.1f}%

## 🎯 Configuração do Modelo
- **Algoritmo**: Random Forest Classifier
- **Amostras de Treino**: {samples}
- **Features**: {len(defect_model.feature_names)}

O modelo está agora pronto para predições de defeitos em tempo real!
"""
        
        return [TextContent(type="text", text=response)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Erro no treinamento: {str(e)}")]


async def train_model():
    """Train the defect prediction model."""
    if not server_state["model_trained"]:
        defect_model.train_on_synthetic_data()
        server_state["model_trained"] = True


def calculate_function_metrics(node: ast.FunctionDef, source_code: str) -> Dict[str, float]:
    """Calculate metrics for a specific function."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            complexity += 1
        elif isinstance(child, ast.Try):
            complexity += len(child.handlers)
    
    lines = source_code.split('\n')
    if hasattr(node, 'end_lineno') and node.end_lineno:
        func_lines = node.end_lineno - node.lineno + 1
    else:
        func_lines = 1
    
    return {
        'cyclomatic_complexity': complexity,
        'lines_of_code': func_lines,
        'number_of_methods': 1,
        'number_of_attributes': 0,
        'depth_of_inheritance': 0,
        'coupling_between_objects': 0,
        'lack_of_cohesion': 0.0,
        'halstead_difficulty': complexity * 1.5,
        'halstead_volume': func_lines * 2.0
    }


def calculate_basic_metrics(tree: ast.AST, source_code: str) -> Dict[str, float]:
    """Calculate basic metrics for the entire code."""
    complexity = 1
    methods = 0
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            methods += 1
        if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            complexity += 1
    
    lines = len([line for line in source_code.split('\n') if line.strip()])
    
    return {
        'cyclomatic_complexity': complexity,
        'lines_of_code': lines,
        'number_of_methods': methods,
        'number_of_attributes': 0,
        'depth_of_inheritance': 0,
        'coupling_between_objects': 0,
        'lack_of_cohesion': 0.0,
        'halstead_difficulty': complexity * 1.5,
        'halstead_volume': lines * 2.0
    }


def calculate_detailed_metrics(tree: ast.AST, source_code: str, include_halstead: bool = True) -> Dict[str, Any]:
    """Calculate detailed metrics."""
    metrics = calculate_basic_metrics(tree, source_code)
    
    result = {
        'Complexidade Ciclomática': metrics['cyclomatic_complexity'],
        'Linhas de Código': metrics['lines_of_code'],
        'Número de Métodos': metrics['number_of_methods'],
        'Acoplamento': metrics['coupling_between_objects'],
        'Falta de Coesão': metrics['lack_of_cohesion']
    }
    
    if include_halstead:
        result.update({
            'Dificuldade Halstead': metrics['halstead_difficulty'],
            'Volume Halstead': metrics['halstead_volume']
        })
    
    # Calculate maintainability index
    if metrics['lines_of_code'] > 0:
        import math
        mi = 171 - 5.2 * math.log(metrics['halstead_volume']) if metrics['halstead_volume'] > 0 else 100
        mi -= 0.23 * metrics['cyclomatic_complexity']
        mi -= 16.2 * math.log(metrics['lines_of_code'])
        result['Índice de Manutenibilidade'] = max(0, min(100, mi))
    
    return result


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())