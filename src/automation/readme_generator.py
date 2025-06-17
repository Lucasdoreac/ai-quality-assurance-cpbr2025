"""
README generator module - focused on generating README.md files.
Part of the refactored documentation generation system.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ReadmeGenerator:
    """Generates README.md files with consistent structure and content."""
    
    def __init__(self, project_root: Path, config: Dict[str, Any]):
        self.project_root = Path(project_root)
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def generate_readme(self, project_info: Dict[str, Any]) -> str:
        """Generate complete README.md content."""
        sections = [
            self._generate_header(project_info),
            self._generate_badges(project_info),
            self._generate_description(project_info),
            self._generate_features(project_info),
            self._generate_quick_start(project_info),
            self._generate_architecture(project_info),
            self._generate_api_documentation(project_info),
            self._generate_statistics(project_info),
            self._generate_installation(project_info),
            self._generate_usage_examples(project_info),
            self._generate_contributing(),
            self._generate_footer()
        ]
        
        return '\n\n'.join(filter(None, sections))
    
    def _generate_header(self, project_info: Dict[str, Any]) -> str:
        """Generate README header with title and subtitle."""
        project_name = self.config.get('project_name', 'AI Quality Assurance System')
        description = self.config.get('project_description', 'Real AI-powered code analysis')
        
        return f"""# 🤖 {project_name}

### {description} with revolutionary auto-documentation"""
    
    def _generate_badges(self, project_info: Dict[str, Any]) -> str:
        """Generate status badges."""
        if not self.config.get('include_badges', True):
            return ""
        
        python_version = self.config.get('python_version', '3.11+')
        
        badges = [
            f"[![Python](https://img.shields.io/badge/Python-{python_version}-blue.svg)](https://python.org)",
            "[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)",
            "[![Auto-Docs](https://img.shields.io/badge/Documentation-Auto--Generated-brightgreen.svg)](#)",
            "[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](#)"
        ]
        
        return ' '.join(badges)
    
    def _generate_description(self, project_info: Dict[str, Any]) -> str:
        """Generate project description section."""
        return f"""---

## 🎯 Sistema Completamente Funcional

Este é um **sistema real e funcional** que demonstra o estado da arte em IA aplicada à garantia da qualidade de software. Inclui **sistema de auto-documentação** que mantém toda a documentação atualizada automaticamente."""
    
    def _generate_features(self, project_info: Dict[str, Any]) -> str:
        """Generate features section."""
        mcp_tools_count = len(project_info.get('mcp_tools', []))
        deps_count = len(project_info.get('dependencies', []))
        
        return f"""## 🧠 Funcionalidades Implementadas

### 🔍 **Análise Inteligente de Código**
- **Parsing AST real** com módulo Python `ast`
- **{deps_count}+ dependências** para análise avançada
- **Detecção de Code Smells** com confiança 85-90%
- **Análise de complexidade** ciclomática em tempo real

### 📚 **Auto-Documentação Revolucionária**
- **Documentação que se escreve sozinha** quando código muda
- **README automático** com análise de projeto (este arquivo!)
- **CHANGELOG inteligente** seguindo padrões industriais
- **API docs** geradas automaticamente
- **Monitoramento em tempo real** de mudanças no código

### 🤖 **Integração MCP com Claude**
- **{mcp_tools_count} ferramentas MCP** disponíveis
- **Integração nativa** com Claude Code
- **Análise de código em tempo real**
- **Geração automática de testes**"""
    
    def _generate_quick_start(self, project_info: Dict[str, Any]) -> str:
        """Generate quick start section."""
        mcp_tools_count = len(project_info.get('mcp_tools', []))
        
        return f"""## 🚀 Quick Start

### Interface Web Completa
```bash
python -m uvicorn src.main:app --reload --port 8000
# Acessar em: http://localhost:8000
```

### MCP Server para Claude
```bash
python mcp_server.py
# {mcp_tools_count} ferramentas disponíveis
```

### Sistema de Auto-Documentação
```bash
python scripts/setup_automation.py
# Documentação se atualiza automaticamente
```"""
    
    def _generate_architecture(self, project_info: Dict[str, Any]) -> str:
        """Generate architecture section."""
        test_files_count = len(project_info.get('test_files', []))
        deps_count = len(project_info.get('dependencies', []))
        
        project_name = self.project_root.name
        
        return f"""## 🏗️ Arquitetura do Sistema

```
{project_name}/
├── src/
│   ├── domain/           # Entidades e regras de negócio
│   ├── application/      # Casos de uso e lógica de aplicação
│   ├── infrastructure/   # Implementações e adapters
│   └── automation/       # Sistema de auto-documentação ⭐
│       ├── project_analyzer.py    # Análise de projeto modular
│       ├── readme_generator.py    # Geração de README
│       ├── changelog_generator.py # Geração de CHANGELOG
│       └── file_watcher.py       # Monitoramento otimizado
├── tests/               # {test_files_count} arquivos de teste
├── mcp_server.py        # Servidor MCP seguro
└── requirements.txt     # {deps_count} dependências
```"""
    
    def _generate_api_documentation(self, project_info: Dict[str, Any]) -> str:
        """Generate API documentation section."""
        api_endpoints = project_info.get('api_endpoints', [])
        mcp_tools = project_info.get('mcp_tools', [])
        
        if not api_endpoints and not mcp_tools:
            return ""
        
        content = "## 📡 API & MCP Tools\n\n"
        
        if api_endpoints:
            content += "### 🌐 REST API Endpoints\n\n"
            for endpoint in api_endpoints[:5]:  # Show first 5
                content += f"- **{endpoint['method']}** `{endpoint['path']}` - {endpoint['function']}\n"
            
            if len(api_endpoints) > 5:
                content += f"- ... e mais {len(api_endpoints) - 5} endpoints\n"
            content += "\n"
        
        if mcp_tools:
            content += f"### 🛠️ Ferramentas MCP Disponíveis ({len(mcp_tools)})\n\n"
            for tool in mcp_tools[:8]:  # Show first 8
                content += f"- **{tool['name']}**: {tool['description']}\n"
            
            if len(mcp_tools) > 8:
                content += f"- ... e mais {len(mcp_tools) - 8} ferramentas\n"
        
        return content
    
    def _generate_statistics(self, project_info: Dict[str, Any]) -> str:
        """Generate project statistics section."""
        stats = {
            'total_lines': project_info.get('total_lines', 0),
            'total_functions': project_info.get('total_functions', 0),
            'total_classes': project_info.get('total_classes', 0),
            'test_files': len(project_info.get('test_files', [])),
            'mcp_tools': len(project_info.get('mcp_tools', [])),
            'api_endpoints': len(project_info.get('api_endpoints', []))
        }
        
        return f"""### 📊 Estatísticas do Projeto
- **Linhas de Código**: {stats['total_lines']:,}
- **Funções**: {stats['total_functions']}
- **Classes**: {stats['total_classes']}
- **Arquivos de Teste**: {stats['test_files']}
- **Ferramentas MCP**: {stats['mcp_tools']}
- **API Endpoints**: {stats['api_endpoints']}"""
    
    def _generate_installation(self, project_info: Dict[str, Any]) -> str:
        """Generate installation section."""
        if not self.config.get('include_installation', True):
            return ""
        
        return """## 📦 Instalação e Configuração

### Instalação Rápida
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar sistema de auto-documentação
python scripts/setup_automation_secure.py

# Iniciar sistema
python -m uvicorn src.main:app --reload --port 8000
```

### Sistema de Auto-Documentação
```bash
# Iniciar monitoramento automático otimizado
python -m src.automation.file_watcher_optimized

# Documentação se atualiza automaticamente quando código muda!
```"""
    
    def _generate_usage_examples(self, project_info: Dict[str, Any]) -> str:
        """Generate usage examples section."""
        if not self.config.get('include_examples', True):
            return ""
        
        mcp_tools = project_info.get('mcp_tools', [])
        
        content = """## 💡 Exemplos de Uso

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
```"""
        
        if mcp_tools:
            content += f"""
### 🤖 Ferramentas MCP com Claude
```bash
# Ferramentas disponíveis ({len(mcp_tools)}):"""
            
            for tool in mcp_tools[:3]:
                content += f"\n# - {tool['name']}: {tool['description']}"
            
            if len(mcp_tools) > 3:
                content += f"\n# - ... e mais {len(mcp_tools) - 3} ferramentas"
            
            content += "\n```"
        
        return content
    
    def _generate_contributing(self) -> str:
        """Generate contributing section."""
        return """## 🤝 Contribuindo

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
5. Abra um Pull Request"""
    
    def _generate_footer(self) -> str:
        """Generate footer section."""
        author = self.config.get('author', 'Aulus Diniz')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""## 🤖 Sistema Auto-Documentado

**Esta documentação foi gerada automaticamente** pelo sistema de auto-documentação em {current_time}.

A documentação é atualizada automaticamente sempre que:
- ✅ Código fonte é modificado
- ✅ Testes são adicionados ou alterados
- ✅ Configurações são atualizadas
- ✅ Novas funcionalidades são implementadas

---

**🎉 Desenvolvido para Campus Party Brasil 2025**

*"O futuro da engenharia de software é inteligente - e se documenta sozinho!"* 🚀

---

*Desenvolvido com ❤️ por [{author}](https://linkedin.com/in/aulus-diniz-9aaab352/) para a comunidade tech brasileira*

*Última atualização automática: {current_time}*"""


class ReadmeValidator:
    """Validates README content for completeness and quality."""
    
    def __init__(self):
        self.required_sections = [
            'title', 'description', 'installation', 'usage'
        ]
        self.recommended_sections = [
            'features', 'examples', 'contributing', 'license'
        ]
    
    def validate_readme(self, content: str) -> Dict[str, Any]:
        """Validate README content and return analysis."""
        validation = {
            'is_valid': True,
            'score': 0,
            'missing_required': [],
            'missing_recommended': [],
            'suggestions': []
        }
        
        # Check required sections
        for section in self.required_sections:
            if not self._has_section(content, section):
                validation['missing_required'].append(section)
                validation['is_valid'] = False
        
        # Check recommended sections
        for section in self.recommended_sections:
            if not self._has_section(content, section):
                validation['missing_recommended'].append(section)
        
        # Calculate score
        total_sections = len(self.required_sections) + len(self.recommended_sections)
        found_sections = total_sections - len(validation['missing_required']) - len(validation['missing_recommended'])
        validation['score'] = round((found_sections / total_sections) * 100, 1)
        
        # Generate suggestions
        validation['suggestions'] = self._generate_suggestions(validation)
        
        return validation
    
    def _has_section(self, content: str, section: str) -> bool:
        """Check if content has a specific section."""
        patterns = {
            'title': r'^#\s+',
            'description': r'(?i)(description|about|overview)',
            'installation': r'(?i)(install|setup)',
            'usage': r'(?i)(usage|how to|getting started)',
            'features': r'(?i)(features|functionality)',
            'examples': r'(?i)(examples|demo)',
            'contributing': r'(?i)(contribut|development)',
            'license': r'(?i)(license|copyright)'
        }
        
        pattern = patterns.get(section, f'(?i){section}')
        return bool(re.search(pattern, content))
    
    def _generate_suggestions(self, validation: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        if validation['missing_required']:
            suggestions.append(f"Add required sections: {', '.join(validation['missing_required'])}")
        
        if validation['missing_recommended']:
            suggestions.append(f"Consider adding: {', '.join(validation['missing_recommended'])}")
        
        if validation['score'] < 80:
            suggestions.append("README completeness below 80% - consider expanding content")
        
        return suggestions