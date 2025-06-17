# ⚡ Instalação Rápida - 5 Minutos
## Sistema AI Quality Assurance + Auto-Documentação

> **🎯 Objetivo:** Ter o sistema funcionando em 5 minutos para análise de código real

---

## 📋 **PRÉ-REQUISITOS (Verificar Primeiro)**

```bash
# ✅ Python 3.8 ou superior
python3 --version
# Deve mostrar: Python 3.8.x ou superior

# ✅ Git instalado
git --version
# Deve mostrar versão do git

# ✅ pip funcionando
pip --version
# Deve mostrar versão do pip
```

**Se algum comando falhar, instale primeiro:**
- **Python:** https://python.org/downloads
- **Git:** https://git-scm.com/downloads

---

## 🚀 **INSTALAÇÃO AUTOMÁTICA**

### **Passo 1: Baixar o Sistema**
```bash
# Clonar repositório
git clone https://github.com/SEU_USUARIO/aulus.git
cd aulus

# Ir para branch com sistema completo
git checkout main
```

### **Passo 2: Instalar Dependências**
```bash
# Instalar todas as dependências necessárias
pip install -r requirements.txt

# OU instalar manualmente se der erro:
pip install fastapi uvicorn scikit-learn numpy pandas matplotlib
pip install anthropic openai watchdog pytest requests httpx 
pip install python-multipart aiofiles jinja2 pydantic rich
```

### **Passo 3: Verificar Instalação**
```bash
# Teste rápido - deve imprimir "✅ Sistema OK!"
python teste_rapido.py
```

---

## 🎯 **EXECUÇÃO - DUAS OPÇÕES**

### **OPÇÃO A: Interface Web (Recomendado para Primeira Vez)**

```bash
# Iniciar servidor web
python -m src.main

# Abrir navegador em:
# http://localhost:8000
```

**🎉 Pronto! Você verá:**
- 📊 Dashboard com estatísticas em tempo real
- 📝 Área para colar código Python
- 🔍 Análise automática de qualidade
- 📚 Documentação sendo gerada

### **OPÇÃO B: Ferramentas MCP (Para Usuários Claude)**

```bash
# Iniciar servidor MCP
python mcp_server_enhanced.py

# Usar com Claude Desktop ou CLI
# 13 ferramentas disponíveis para análise
```

---

## 🧪 **TESTE IMEDIATO - 30 SEGUNDOS**

### **Teste 1: Código Simples**
1. Abra http://localhost:8000
2. Cole este código na área de texto:

```python
def calcular_area(largura, altura):
    """Calcula área de retângulo."""
    return largura * altura

def processar_lista(numeros):
    """Processa lista de números."""
    resultado = []
    for num in numeros:
        if num > 0:
            resultado.append(num * 2)
    return resultado
```

3. Clique "🚀 Analisar Código"
4. **Resultado esperado:** Score alto (80-90+), poucos problemas

### **Teste 2: Código com Problemas**
Cole este código para ver a IA detectando problemas:

```python
def funcao_com_problemas(a, b, c, d, e, f, g, h, i, j):
    # Muitos parâmetros - será detectado
    total = 0
    for i in range(1000):
        for j in range(1000):
            if a > b:
                if c > d:
                    if e > f:
                        total += 1
    return total
```

**Resultado esperado:** Score baixo, code smells detectados automaticamente

---

## 📊 **O QUE VOCÊ VERÁ**

### **Métricas Automáticas:**
- ✅ **Score de Qualidade** (0-100)
- ✅ **Complexidade Ciclomática**
- ✅ **Índice de Manutenibilidade**
- ✅ **Métricas Halstead**

### **Problemas Detectados:**
- 🔍 **Code Smells** (Long Method, Large Class, etc.)
- 🎯 **Predições de Defeito** com probabilidades
- ⚠️ **Sugestões de Melhoria** automáticas

### **Geração Automática:**
- 🧪 **Testes Unitários** criados automaticamente
- 📚 **Documentação** atualizada em tempo real
- 📝 **README** inteligente do projeto

---

## 🔧 **TROUBLESHOOTING**

### **Erro: "Módulo não encontrado"**
```bash
# Verificar se está na pasta correta
pwd
ls -la src/

# Adicionar ao PYTHONPATH
export PYTHONPATH=$PWD
```

### **Erro: "Porta 8000 em uso"**
```bash
# Usar porta diferente
python -m src.main --port 8001

# OU matar processo
lsof -ti:8000 | xargs kill -9
```

### **Erro: Dependências**
```bash
# Instalar uma por vez se der erro em lote
pip install fastapi
pip install uvicorn
pip install scikit-learn
# etc...
```

### **Performance Lenta**
```bash
# Se estiver lento:
# 1. Testar com código menor primeiro
# 2. Verificar RAM disponível
# 3. Fechar outros programas pesados
```

---

## 📱 **DEMO AUTOMÁTICA**

Se quiser ver tudo funcionando automaticamente:

```bash
# Executar demo completa (2 minutos)
python demo.py

# Vai mostrar:
# - Análise de código bom
# - Análise de código problemático  
# - Geração de documentação
# - Estatísticas finais
```

---

## 📧 **PRÓXIMOS PASSOS**

### **Teste com Código Real da Empresa:**
1. 📁 **Copie código Python** atual da empresa
2. 🔍 **Analise com o sistema**
3. 📊 **Compare resultados** com ferramentas atuais
4. 💰 **Calcule ROI** potencial

### **Demonstrar para Equipe:**
1. 🎥 **Grave screencast** da análise
2. 📊 **Mostre métricas** para outros desenvolvedores
3. 🧪 **Teste geração automática** de testes
4. 📚 **Demonstre auto-documentação** em ação

### **Avaliação Técnica:**
1. 🔧 **Integração** com CI/CD atual
2. 📈 **Customização** para padrões da empresa
3. 🎯 **Métricas específicas** do negócio
4. 🚀 **Roadmap** de implementação

---

## ✅ **CHECKLIST DE SUCESSO**

Após seguir este guia, você deve ter:

- [ ] ✅ Sistema rodando em http://localhost:8000
- [ ] 📊 Dashboard mostrando estatísticas
- [ ] 🔍 Análise de código funcionando
- [ ] 🧪 Testes sendo gerados automaticamente  
- [ ] 📚 Documentação sendo criada
- [ ] 🎯 Predições de defeito aparecendo
- [ ] 💡 Sugestões de melhoria sendo exibidas

**Se todos os itens estão ✅, o sistema está pronto para análise profissional!**

---

## 🆘 **SUPORTE**

**Se tiver problemas:**

1. 📋 Verificar se seguiu todos os pré-requisitos
2. 🔄 Reinstalar dependências: `pip install -r requirements.txt --force-reinstall`
3. 🧪 Testar com código exemplo primeiro
4. 📞 Contatar equipe de desenvolvimento

**Sistema testado em:**
- ✅ Windows 10/11
- ✅ macOS Big Sur+  
- ✅ Ubuntu 20.04+
- ✅ Python 3.8, 3.9, 3.10, 3.11

---

**🏆 Resultado Final:** Sistema revolucionário de análise de código funcionando localmente em 5 minutos!