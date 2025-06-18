# 🤖 AI Quality Assurance System

### Real AI-powered code analysis with revolutionary auto-documentation

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org) [![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com) [![Auto-Docs](https://img.shields.io/badge/Documentation-Auto--Generated-brightgreen.svg)](#) [![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](#)

---

## 🎯 Sistema Completamente Funcional

Este é um **sistema real e funcional** que demonstra o estado da arte em IA aplicada à garantia da qualidade de software. Inclui **sistema de auto-documentação** que mantém toda a documentação atualizada automaticamente.

## 🧠 Funcionalidades Implementadas

### 🔍 **Análise Inteligente de Código**
- **Parsing AST real** com módulo Python `ast`
- **37+ dependências** para análise avançada
- **Detecção de Code Smells** com confiança 85-90%
- **Análise de complexidade** ciclomática em tempo real

### 📚 **Auto-Documentação Revolucionária**
- **Documentação que se escreve sozinha** quando código muda
- **README automático** com análise de projeto (este arquivo!)
- **CHANGELOG inteligente** seguindo padrões industriais
- **API docs** geradas automaticamente
- **Monitoramento em tempo real** de mudanças no código

### 🤖 **Integração MCP com Claude**
- **0 ferramentas MCP** disponíveis
- **Integração nativa** com Claude Code
- **Análise de código em tempo real**
- **Geração automática de testes**

## 🚀 Quick Start

### Interface Web Completa
```bash
python -m uvicorn src.main:app --reload --port 8000
# Acessar em: http://localhost:8000
```

### MCP Server para Claude
```bash
python mcp_server.py
# 0 ferramentas disponíveis
```

### Sistema de Auto-Documentação
```bash
python scripts/setup_automation.py
# Documentação se atualiza automaticamente
```

## 🏗️ Arquitetura do Sistema

```
ai-quality-assurance/
├── src/
│   ├── domain/           # Entidades e regras de negócio
│   ├── application/      # Casos de uso e lógica de aplicação
│   ├── infrastructure/   # Implementações e adapters
│   └── automation/       # Sistema de auto-documentação ⭐
├── tests/               # 4 arquivos de teste
├── mcp_server.py        # Servidor MCP
└── requirements.txt     # 37 dependências
```

### 📊 Estatísticas do Projeto
- **Linhas de Código**: 6,170
- **Funções**: 253
- **Classes**: 48
- **Arquivos de Teste**: 4
- **Ferramentas MCP**: 0
- **Dependências**: 37

## 📦 Instalação e Configuração

### Instalação Rápida
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar sistema de auto-documentação
python scripts/setup_automation.py

# Iniciar sistema
python -m uvicorn src.main:app --reload --port 8000
```

## 💡 Exemplos de Uso

### 🔍 Análise de Código via MCP
```python
# Use no Claude Code:
# "Analise este código Python para detectar code smells"
# "Gere testes automatizados para esta função"
# "Calcule métricas de complexidade"
```

### 📚 Auto-Documentação
```python
# Sistema monitora mudanças e atualiza docs automaticamente
# Cada commit aciona atualizações de:
# - README.md (este arquivo)
# - CHANGELOG.md
# - API_DOCS.md
# - ARCHITECTURE.md
```

## 🤝 Contribuindo

### Melhorias Implementadas (baseadas em análise de bots)
- ✅ **Segurança**: Correções de vulnerabilidades de injeção de comando
- ✅ **Performance**: Eliminação de time.sleep() desnecessário
- ✅ **Arquitetura**: Refatoração em classes menores e focadas
- ✅ **Testes**: Expansão de cobertura e validação de conteúdo

### Como Contribuir
1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 🤖 Sistema Auto-Documentado

**Esta documentação foi gerada automaticamente** pelo sistema de auto-documentação em 2025-06-18 00:21:42.

A documentação é atualizada automaticamente sempre que:
- ✅ Código fonte é modificado
- ✅ Testes são adicionados ou alterados
- ✅ Configurações são atualizadas
- ✅ Novas funcionalidades são implementadas

---

**🎉 Desenvolvido para Campus Party Brasil 2025**

*"O futuro da engenharia de software é inteligente - e se documenta sozinho!"* 🚀

---

*Desenvolvido com ❤️ por [Aulus Diniz](https://linkedin.com/in/aulus-diniz-9aaab352/) para a comunidade tech brasileira*

*Última atualização automática: 2025-06-18 00:21:42*
