"""
Main FastAPI application for AI Quality Assurance system.
Real functional system for live demonstration at Campus Party Brasil 2025.
"""
import os
import tempfile
import time
from typing import Dict, Any, List
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from .application.use_cases import AnalyzeCodeUseCase
from .infrastructure.repositories import InMemoryCodeAnalysisRepository
from .infrastructure.ml_models import DefectPredictionModel, CodeSmellDetector, TestGenerator

# Initialize FastAPI app
app = FastAPI(
    title="AI Quality Assurance System",
    description="Real AI-powered code analysis for Campus Party Brasil 2025",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize dependencies
repository = InMemoryCodeAnalysisRepository()
analyze_use_case = AnalyzeCodeUseCase(repository)
defect_model = DefectPredictionModel()
smell_detector = CodeSmellDetector()
test_generator = TestGenerator()

# Global state for demo
demo_state = {
    "analyses_count": 0,
    "total_smells_found": 0,
    "total_bugs_predicted": 0,
    "total_tests_generated": 0,
    "model_accuracy": 0.0
}


class AnalysisRequest(BaseModel):
    code: str
    filename: str = "uploaded_code.py"


class AnalysisResponse(BaseModel):
    analysis_id: str
    file_path: str
    metrics: Dict[str, Any]
    code_smells: List[Dict[str, Any]]
    defect_predictions: List[Dict[str, Any]]
    generated_tests: List[Dict[str, Any]]
    suggested_repairs: List[Dict[str, Any]]
    overall_quality_score: float
    processing_time_seconds: float


@app.on_event("startup")
async def startup_event():
    """Initialize ML models on startup."""
    global demo_state
    
    # Train defect prediction model
    print("Training defect prediction model...")
    metrics = defect_model.train_on_synthetic_data()
    demo_state["model_accuracy"] = metrics["accuracy"]
    print(f"Model trained with accuracy: {metrics['accuracy']:.2%}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main demo interface."""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Quality Assurance - Demo ao Vivo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .upload-area { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
            .demo-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .stat-value { font-size: 2em; font-weight: bold; color: #4CAF50; }
            .subagetic-highlight { background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px; margin: 20px 0; }
            .agent-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
            .agent-card { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; text-align: center; }
            .code-input { width: 100%; height: 300px; font-family: monospace; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .btn { background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #45a049; }
            .results { background: white; padding: 20px; border-radius: 10px; margin-top: 20px; }
            .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 20px 0; }
            .metric { background: #f8f9fa; padding: 10px; border-radius: 5px; text-align: center; }
            .smell-item { background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; border-radius: 3px; }
            .prediction-item { background: #f8d7da; padding: 10px; margin: 5px 0; border-left: 4px solid #dc3545; border-radius: 3px; }
            .test-item { background: #d1ecf1; padding: 10px; margin: 5px 0; border-left: 4px solid #17a2b8; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 IA na Garantia da Qualidade de Software</h1>
                <h2>Demonstração ao Vivo - Campus Party Brasil 2025</h2>
                <p>Sistema funcional real com análise de código, predição de bugs e geração automática de testes</p>
            </div>
            
            <div class="demo-stats" id="stats">
                <div class="stat-card">
                    <div class="stat-value" id="analyses-count">0</div>
                    <div>Análises Realizadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="smells-found">0</div>
                    <div>Code Smells Detectados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="bugs-predicted">0</div>
                    <div>Bugs Preditos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="tests-generated">0</div>
                    <div>Testes Gerados</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="model-accuracy">92.3%</div>
                    <div>Acurácia do Modelo ML</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">17</div>
                    <div>Ferramentas MCP</div>
                </div>
            </div>

            <div class="subagetic-highlight">
                <h3>🤖 Sistema Subagetic Multi-Agent Ativo</h3>
                <p>Análise com 4 agentes especializados para máxima qualidade e honestidade nos resultados</p>
                <div class="agent-grid">
                    <div class="agent-card">
                        <div>🎯</div>
                        <strong>COORDINATOR</strong><br>
                        <small>Orquestração</small>
                    </div>
                    <div class="agent-card">
                        <div>🧠</div>
                        <strong>ANALYZER</strong><br>
                        <small>Análise Profunda</small>
                    </div>
                    <div class="agent-card">
                        <div>⚡</div>
                        <strong>EXECUTOR</strong><br>
                        <small>Implementação</small>
                    </div>
                    <div class="agent-card">
                        <div>✅</div>
                        <strong>VALIDATOR</strong><br>
                        <small>Qualidade</small>
                    </div>
                </div>
            </div>
            
            <div class="upload-area">
                <h3>📁 Envie seu código Python para análise em tempo real</h3>
                <textarea id="code-input" class="code-input" placeholder="Cole seu código Python aqui ou use o exemplo...">
def calculate_complex_metrics(data, threshold, use_cache=True, debug=False, max_iterations=1000):
    # Exemplo de função com code smells para demonstração
    if data is None or len(data) == 0:
        return None
    
    total = 0
    count = 0
    cache = {}
    
    for i in range(len(data)):
        for j in range(len(data[i])):
            for k in range(len(data[i][j])):
                if data[i][j][k] > threshold:
                    if use_cache and str(data[i][j][k]) in cache:
                        value = cache[str(data[i][j][k])]
                    else:
                        value = data[i][j][k] * 2.5 + 10
                        if use_cache:
                            cache[str(data[i][j][k])] = value
                    
                    if debug:
                        print(f"Processing {i},{j},{k}: {data[i][j][k]} -> {value}")
                    
                    total += value
                    count += 1
                    
                    if count >= max_iterations:
                        if debug:
                            print("Max iterations reached")
                        break
    
    if count == 0:
        return 0
    
    return total / count

class DataProcessor:
    def __init__(self, config, logger, cache_manager, db_connection, api_client, file_handler):
        self.config = config
        self.logger = logger
        self.cache = cache_manager
        self.db = db_connection
        self.api = api_client
        self.files = file_handler
        self.processed_count = 0
        self.error_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
    def process_data(self, input_data):
        # Método muito longo com múltiplas responsabilidades
        self.logger.info("Starting data processing")
        
        try:
            if not self.validate_input(input_data):
                self.error_count += 1
                return None
                
            # Processar dados
            processed = self.transform_data(input_data)
            
            # Salvar no banco
            self.save_to_database(processed)
            
            # Enviar via API
            self.send_via_api(processed)
            
            # Atualizar cache
            self.update_cache(processed)
            
            # Salvar arquivo
            self.save_to_file(processed)
            
            self.processed_count += 1
            return processed
            
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            self.error_count += 1
            return None
</textarea>
                <br><br>
                <button class="btn" onclick="analyzeCode()">🚀 Analisar Código</button>
                <button class="btn" style="background: #6c757d; margin-left: 10px;" onclick="loadExample()">📝 Carregar Exemplo</button>
            </div>
            
            <div id="results" style="display: none;"></div>
        </div>
        
        <script>
            // Load stats on page load
            loadStats();
            
            function loadStats() {
                fetch('/api/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('analyses-count').textContent = data.analyses_count;
                        document.getElementById('smells-found').textContent = data.total_smells_found;
                        document.getElementById('bugs-predicted').textContent = data.total_bugs_predicted;
                        document.getElementById('tests-generated').textContent = data.total_tests_generated;
                        document.getElementById('model-accuracy').textContent = (data.model_accuracy * 100).toFixed(1) + '%';
                    });
            }
            
            function analyzeCode() {
                const code = document.getElementById('code-input').value;
                const button = event.target;
                
                if (!code.trim()) {
                    alert('Por favor, insira algum código para análise');
                    return;
                }
                
                button.textContent = '⏳ Analisando...';
                button.disabled = true;
                
                fetch('/api/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        code: code,
                        filename: 'demo_code.py'
                    })
                })
                .then(response => response.json())
                .then(data => {
                    displayResults(data);
                    loadStats(); // Update stats
                })
                .catch(error => {
                    alert('Erro na análise: ' + error.message);
                })
                .finally(() => {
                    button.textContent = '🚀 Analisar Código';
                    button.disabled = false;
                });
            }
            
            function displayResults(data) {
                const resultsDiv = document.getElementById('results');
                const metrics = data.metrics;
                
                resultsDiv.innerHTML = `
                    <h3>📊 Resultados da Análise</h3>
                    <p><strong>Tempo de processamento:</strong> ${data.processing_time_seconds.toFixed(2)}s</p>
                    <p><strong>Score de Qualidade:</strong> <span style="font-size: 1.5em; color: ${data.overall_quality_score >= 70 ? '#4CAF50' : data.overall_quality_score >= 50 ? '#ff9800' : '#f44336'};">${data.overall_quality_score.toFixed(1)}/100</span></p>
                    
                    <div class="metric-grid">
                        <div class="metric">
                            <strong>${metrics.cyclomatic_complexity}</strong><br>
                            Complexidade Ciclomática
                        </div>
                        <div class="metric">
                            <strong>${metrics.lines_of_code}</strong><br>
                            Linhas de Código
                        </div>
                        <div class="metric">
                            <strong>${metrics.number_of_methods}</strong><br>
                            Métodos
                        </div>
                        <div class="metric">
                            <strong>${metrics.maintainability_index.toFixed(1)}</strong><br>
                            Índice Manutenibilidade
                        </div>
                    </div>
                    
                    <h4>🔍 Code Smells Detectados (${data.code_smells.length})</h4>
                    ${data.code_smells.map(smell => `
                        <div class="smell-item">
                            <strong>${smell.smell_type.replace('_', ' ').toUpperCase()}</strong> 
                            (Confiança: ${(smell.confidence * 100).toFixed(1)}%)<br>
                            <em>Linha ${smell.line_start}${smell.function_name ? ' - Função: ' + smell.function_name : ''}</em><br>
                            ${smell.description}
                        </div>
                    `).join('')}
                    
                    <h4>🎯 Predições de Defeitos (${data.defect_predictions.length})</h4>
                    ${data.defect_predictions.map(pred => `
                        <div class="prediction-item">
                            <strong>${pred.function_name}</strong> - Probabilidade: ${(pred.defect_probability * 100).toFixed(1)}%<br>
                            <strong>Risco:</strong> ${pred.risk_level.toUpperCase()}<br>
                            <strong>Fatores:</strong> ${pred.contributing_factors.join(', ')}
                        </div>
                    `).join('')}
                    
                    <h4>🧪 Testes Gerados (${data.generated_tests.length})</h4>
                    ${data.generated_tests.map(test => `
                        <div class="test-item">
                            <strong>${test.test_name}</strong> para função <em>${test.function_name}</em><br>
                            <details>
                                <summary>Ver código do teste</summary>
                                <pre style="background: #f8f9fa; padding: 10px; border-radius: 3px; margin-top: 10px;">${test.test_code}</pre>
                            </details>
                        </div>
                    `).join('')}
                    
                    <h4>🔧 Reparos Sugeridos (${data.suggested_repairs.length})</h4>
                    ${data.suggested_repairs.map(repair => `
                        <div style="background: #e2e3e5; padding: 10px; margin: 5px 0; border-left: 4px solid #6c757d; border-radius: 3px;">
                            <strong>Linha ${repair.line_start}-${repair.line_end}:</strong> ${repair.issue_description}<br>
                            <strong>Sugestão:</strong> ${repair.suggested_fix}
                        </div>
                    `).join('')}
                `;
                
                resultsDiv.style.display = 'block';
                resultsDiv.scrollIntoView({ behavior: 'smooth' });
            }
            
            function loadExample() {
                // The example is already in the textarea
                alert('Exemplo carregado! Este código contém vários code smells para demonstração.');
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_code(request: AnalysisRequest):
    """Analyze code and return comprehensive results."""
    global demo_state
    
    try:
        # Execute analysis
        result = await analyze_use_case.execute(request.filename, request.code)
        
        # Update demo statistics
        demo_state["analyses_count"] += 1
        demo_state["total_smells_found"] += len(result.code_smells)
        demo_state["total_bugs_predicted"] += len(result.defect_predictions)
        demo_state["total_tests_generated"] += len(result.generated_tests)
        
        # Convert to response format
        return AnalysisResponse(
            analysis_id="demo_analysis",
            file_path=result.file_path,
            metrics={
                "cyclomatic_complexity": result.metrics.cyclomatic_complexity,
                "lines_of_code": result.metrics.lines_of_code,
                "number_of_methods": result.metrics.number_of_methods,
                "number_of_attributes": result.metrics.number_of_attributes,
                "depth_of_inheritance": result.metrics.depth_of_inheritance,
                "coupling_between_objects": result.metrics.coupling_between_objects,
                "lack_of_cohesion": result.metrics.lack_of_cohesion,
                "halstead_difficulty": result.metrics.halstead_difficulty,
                "halstead_volume": result.metrics.halstead_volume,
                "maintainability_index": result.metrics.maintainability_index
            },
            code_smells=[
                {
                    "smell_type": smell.smell_type.value,
                    "severity": smell.severity.value,
                    "line_start": smell.line_start,
                    "line_end": smell.line_end,
                    "function_name": smell.function_name,
                    "class_name": smell.class_name,
                    "description": smell.description,
                    "confidence": smell.confidence,
                    "metrics": smell.metrics
                } for smell in result.code_smells
            ],
            defect_predictions=[
                {
                    "function_name": pred.function_name,
                    "defect_probability": pred.defect_probability,
                    "confidence": pred.confidence,
                    "risk_level": pred.risk_level.value,
                    "contributing_factors": pred.contributing_factors,
                    "metrics_used": pred.metrics_used
                } for pred in result.defect_predictions
            ],
            generated_tests=[
                {
                    "function_name": test.function_name,
                    "test_name": test.test_name,
                    "test_code": test.test_code,
                    "test_type": test.test_type,
                    "coverage_target": test.coverage_target,
                    "expected_assertions": test.expected_assertions,
                    "complexity_score": test.complexity_score
                } for test in result.generated_tests
            ],
            suggested_repairs=[
                {
                    "line_start": repair.line_start,
                    "line_end": repair.line_end,
                    "issue_description": repair.issue_description,
                    "suggested_fix": repair.suggested_fix,
                    "fix_type": repair.fix_type,
                    "confidence": repair.confidence,
                    "validation_status": repair.validation_status
                } for repair in result.suggested_repairs
            ],
            overall_quality_score=result.overall_quality_score,
            processing_time_seconds=result.processing_time_seconds
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and analyze a Python file."""
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Only Python files are supported")
    
    # Read file content
    content = await file.read()
    code = content.decode('utf-8')
    
    # Analyze using the same endpoint
    request = AnalysisRequest(code=code, filename=file.filename)
    return await analyze_code(request)


@app.get("/api/stats")
async def get_demo_stats():
    """Get current demo statistics."""
    return demo_state


@app.get("/api/model-info")
async def get_model_info():
    """Get information about the ML models."""
    feature_importance = defect_model.get_feature_importance()
    
    return {
        "defect_prediction_model": {
            "type": "Random Forest Classifier",
            "features": defect_model.feature_names,
            "feature_importance": feature_importance,
            "is_trained": defect_model.is_trained,
            "accuracy": demo_state["model_accuracy"]
        },
        "code_smell_detector": {
            "type": "Rule-based with ML enhancements",
            "supported_smells": [
                "long_method", "large_class", "long_parameter_list",
                "high_complexity", "god_object"
            ]
        },
        "test_generator": {
            "type": "AST-based intelligent generator",
            "test_types": ["unit", "property", "edge_case", "error_handling"]
        }
    }


@app.get("/presentation")
async def presentation():
    """Redirect to presentation slides."""
    return HTMLResponse("""
    <script>
        window.location.href = '/presentation/index.html';
    </script>
    """)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)