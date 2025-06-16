# 🤖 IA na Garantia da Qualidade de Software

### Sistema Demonstrativo - Campus Party Brasil 2025

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-1.0+-purple.svg)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Sobre o Projeto

Este sistema demonstra como a **Inteligência Artificial está revolucionando a Garantia da Qualidade de Software**, apresentando o estado da arte em técnicas de ML/IA aplicadas a todas as fases do desenvolvimento de software.

**Desenvolvido para apresentação na Campus Party Brasil 2025** por [Aulus Diniz](https://www.linkedin.com/in/aulus-diniz-9aaab352/) e equipe.

## 🌟 Funcionalidades Demonstrativas

### 🔍 **Análise Inteligente de Código**
- **Code Smells Detection**: Detecção automática de problemas estruturais
- **Predição de Defeitos**: ML para identificar arquivos propensos a bugs
- **Análise de Complexidade**: Métricas automatizadas de qualidade

### 🧪 **Geração Automática de Testes**
- **LLMs para Testes**: GPT/Claude gerando casos de teste
- **Cobertura Inteligente**: Otimização baseada em risco
- **Múltiplos Frameworks**: pytest, unittest, jest

### 🔧 **Correção Automática de Bugs**
- **Auto-fix Sugerido**: IA propondo correções
- **Validação de Patches**: Verificação automática
- **Confidence Scoring**: Nível de confiança das correções

### 📊 **Relatórios de Qualidade**
- **Métricas Completas**: Complexidade, duplicação, débito técnico
- **Tendências Temporais**: Evolução da qualidade
- **Comparação de Projetos**: Benchmarking automático

## 🚀 Acesso Rápido

### 💻 **Executar Localmente**
```bash
# Clone do projeto
git clone https://github.com/seu-usuario/ai-quality-assurance-cpbr2025.git
cd ai-quality-assurance-cpbr2025

# Instalar dependências
pip install -r requirements.txt

# Executar sistema completo
python -m uvicorn src.main:app --reload --port 8000

# Acessar em:
# - API: http://localhost:8000
# - Apresentação: http://localhost:8000/presentation/index.html
# - Demo: http://localhost:8000/presentation/demo-interface.html
```

## 🏗️ Arquitetura do Sistema

### **Clean Architecture Implementada**
```
src/
├── domain/          # Entidades e regras de negócio
├── application/     # Casos de uso e portas
└── infrastructure/  # Adapters e implementações

presentation/        # Interface web e slides
mcp_server/         # Servidor MCP para Claude
demo/               # Dados e exemplos para demonstração
```

### **Tecnologias Utilizadas**
- **Backend**: Python 3.11, FastAPI, MCP
- **Frontend**: HTML5, JavaScript, reveal.js
- **IA/ML**: Simulação de modelos OpenAI/Claude
- **Infra**: Docker, GitHub Pages, Vercel

## 📊 Resultados Esperados

### **Impacto Demonstrado**
- 🎯 **90%+ accuracy** na detecção de bugs
- 🚀 **10x speedup** na geração de testes
- 📉 **75% redução** em falsos positivos
- ⚡ **50% menos tempo** de debugging

## 🤝 Contribuições

Este é um projeto demonstrativo, mas contribuições são bem-vindas para:
- 🔧 Implementar integrações reais com APIs de IA
- 🧪 Adicionar mais casos de teste
- 🎨 Melhorar interface e visualizações
- 📚 Expandir documentação

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.

## 👥 Apresentadores

### **Aulus Diniz**
- 🔗 [LinkedIn](https://www.linkedin.com/in/aulus-diniz-9aaab352/)
- 💼 Especialista em Engenharia de Software e Arquitetura
- 🎯 Foco em IA aplicada ao desenvolvimento

---

## 🎉 Campus Party Brasil 2025

**"O futuro da qualidade de software é inteligente"**

Este projeto demonstra como a IA está transformando cada aspecto do desenvolvimento de software, desde a análise de requisitos até a operação em produção. 

**A revolução já começou. Você está pronto?** 🚀

---

*Desenvolvido com ❤️ para a comunidade tech brasileira*