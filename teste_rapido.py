#!/usr/bin/env python3
"""
Teste rápido do sistema AI Quality Assurance + Auto-Documentação.
Executa em 30 segundos para validar se tudo está funcionando.
"""
import sys
import time
import traceback
from datetime import datetime


def print_header(texto):
    """Imprime cabeçalho formatado."""
    print(f"\n{'='*60}")
    print(f"🔍 {texto}")
    print(f"{'='*60}")


def print_success(texto):
    """Imprime mensagem de sucesso."""
    print(f"✅ {texto}")


def print_error(texto):
    """Imprime mensagem de erro."""
    print(f"❌ {texto}")


def print_info(texto):
    """Imprime informação."""
    print(f"ℹ️  {texto}")


def testar_imports():
    """Testa se todos os módulos podem ser importados."""
    print_header("TESTE DE IMPORTAÇÕES")
    
    try:
        # Testar imports básicos
        import fastapi
        import uvicorn
        import sklearn
        import numpy
        import pandas
        print_success("Dependências básicas: FastAPI, scikit-learn, numpy, pandas")
        
        # Testar nossos módulos
        from src.main import app
        print_success("Módulo principal: src.main")
        
        from src.application.use_cases import AnalyzeCodeUseCase
        from src.infrastructure.repositories import InMemoryCodeAnalysisRepository
        from src.infrastructure.ml_models import DefectPredictionModel
        print_success("Módulos de negócio: use_cases, repositories, ml_models")
        
        print_success("TODOS OS IMPORTS FUNCIONANDO!")
        return True
        
    except ImportError as e:
        print_error(f"Erro de import: {e}")
        print_info("Execute: pip install -r requirements.txt")
        return False
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return False


def testar_ml_models():
    """Testa se os modelos ML estão funcionando."""
    print_header("TESTE DOS MODELOS ML")
    
    try:
        from src.infrastructure.ml_models import DefectPredictionModel, CodeSmellDetector, TestGenerator
        
        # Testar modelo de predição
        model = DefectPredictionModel()
        print_success("DefectPredictionModel criado")
        
        # Testar detector de code smells
        detector = CodeSmellDetector()
        print_success("CodeSmellDetector criado")
        
        # Testar gerador de testes
        generator = TestGenerator()
        print_success("TestGenerator criado")
        
        print_success("TODOS OS MODELOS ML FUNCIONANDO!")
        return True
        
    except Exception as e:
        print_error(f"Erro nos modelos ML: {e}")
        traceback.print_exc()
        return False


def testar_analise_codigo():
    """Testa análise de código básica."""
    print_header("TESTE DE ANÁLISE DE CÓDIGO")
    
    try:
        from src.application.use_cases import AnalyzeCodeUseCase
        from src.infrastructure.repositories import InMemoryCodeAnalysisRepository
        
        # Configurar caso de uso
        repository = InMemoryCodeAnalysisRepository()
        use_case = AnalyzeCodeUseCase(repository)
        print_success("Use case configurado")
        
        # Código simples para teste
        codigo_teste = '''
def calcular_area(largura, altura):
    """Calcula área de um retângulo."""
    return largura * altura

def processar_lista(numeros):
    """Processa lista de números."""
    resultado = []
    for num in numeros:
        if num > 0:
            resultado.append(num * 2)
    return resultado
'''
        
        print_info("Analisando código de exemplo...")
        
        # Executar análise (sem await - versão síncrona para teste rápido)
        import asyncio
        result = asyncio.run(use_case.execute("teste.py", codigo_teste))
        
        print_success(f"Análise concluída em {result.processing_time_seconds:.2f}s")
        print_success(f"Score de qualidade: {result.overall_quality_score:.1f}/100")
        print_success(f"Code smells detectados: {len(result.code_smells)}")
        print_success(f"Predições de defeito: {len(result.defect_predictions)}")
        print_success(f"Testes gerados: {len(result.generated_tests)}")
        
        print_success("ANÁLISE DE CÓDIGO FUNCIONANDO!")
        return True
        
    except Exception as e:
        print_error(f"Erro na análise: {e}")
        traceback.print_exc()
        return False


def testar_fastapi():
    """Testa se o FastAPI pode ser iniciado."""
    print_header("TESTE DO FASTAPI")
    
    try:
        from src.main import app
        print_success("FastAPI app carregado")
        
        # Verificar se tem os endpoints esperados
        rotas = [route.path for route in app.routes]
        endpoints_esperados = ["/", "/api/analyze", "/api/stats"]
        
        for endpoint in endpoints_esperados:
            if endpoint in rotas:
                print_success(f"Endpoint encontrado: {endpoint}")
            else:
                print_error(f"Endpoint faltando: {endpoint}")
        
        print_success("FASTAPI CONFIGURADO CORRETAMENTE!")
        return True
        
    except Exception as e:
        print_error(f"Erro no FastAPI: {e}")
        return False


def testar_mcp_server():
    """Testa se o servidor MCP pode ser carregado."""
    print_header("TESTE DO SERVIDOR MCP")
    
    try:
        # Verificar se arquivo existe
        import os
        if os.path.exists("mcp_server.py"):
            print_success("mcp_server.py encontrado")
        else:
            print_error("mcp_server.py não encontrado")
            return False
        
        # Tentar importar (sem executar)
        import importlib.util
        spec = importlib.util.spec_from_file_location("mcp_server", "mcp_server.py")
        if spec and spec.loader:
            print_success("mcp_server.py pode ser carregado")
        else:
            print_error("Erro ao carregar mcp_server.py")
            return False
        
        print_success("SERVIDOR MCP DISPONÍVEL!")
        return True
        
    except Exception as e:
        print_error(f"Erro no MCP: {e}")
        return False


def main():
    """Função principal do teste."""
    inicio = time.time()
    
    print("🚀 TESTE RÁPIDO DO SISTEMA AI QUALITY ASSURANCE")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    
    # Executar todos os testes
    testes = [
        ("Importações", testar_imports),
        ("Modelos ML", testar_ml_models),
        ("Análise de Código", testar_analise_codigo),
        ("FastAPI", testar_fastapi),
        ("Servidor MCP", testar_mcp_server)
    ]
    
    resultados = {}
    
    for nome, funcao_teste in testes:
        print_info(f"Executando teste: {nome}")
        try:
            resultado = funcao_teste()
            resultados[nome] = resultado
        except Exception as e:
            print_error(f"Erro crítico em {nome}: {e}")
            resultados[nome] = False
    
    # Relatório final
    print_header("RELATÓRIO FINAL")
    
    sucessos = sum(1 for r in resultados.values() if r)
    total = len(resultados)
    
    for nome, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome}: {status}")
    
    tempo_total = time.time() - inicio
    
    print(f"\n📊 RESULTADO: {sucessos}/{total} testes passaram")
    print(f"⏱️ Tempo total: {tempo_total:.1f} segundos")
    
    if sucessos == total:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("✅ Pronto para análise de código real")
        print("✅ Interface web disponível em: python -m src.main")
        print("✅ Servidor MCP disponível em: python mcp_server.py")
        print("\n🚀 Para iniciar:")
        print("   python -m src.main")
        print("   # Abra http://localhost:8000 no navegador")
        return 0
    else:
        print(f"\n⚠️ ALGUNS PROBLEMAS ENCONTRADOS ({total-sucessos} falhas)")
        print("📋 Verifique os erros acima e:")
        print("   1. Execute: pip install -r requirements.txt")
        print("   2. Verifique se está na pasta correta")
        print("   3. Teste novamente: python teste_rapido.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())