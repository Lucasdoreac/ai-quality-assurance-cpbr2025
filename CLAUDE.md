# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Quality Assurance Auto-Documentation System - A real functional system that demonstrates AI-powered code analysis with automatic documentation generation. Built for Campus Party Brasil 2025 demonstration.

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Setup secure automation system
python scripts/setup_automation_secure.py

# Install pre-commit hooks (optional)
pre-commit install
```

### Running the Application
```bash
# Start FastAPI web server
python -m uvicorn src.main:app --reload --port 8000

# Start MCP server for Claude integration
python mcp_server.py

# Test documentation generation
python test_auto_docs.py
```

### Testing
```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_security_fixes.py
pytest tests/test_content_validation.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Development Tools
```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/

# Test import of main components
python3 -c "from src.automation.documentation_orchestrator import DocumentationOrchestrator; print('✅ Import successful')"
```

## Architecture

### Core System Architecture
```
src/
├── domain/           # Business entities and domain logic
├── application/      # Use cases and application services
├── infrastructure/   # External integrations (ML models, repositories)
└── automation/       # Auto-documentation system ⭐
```

### Auto-Documentation System (Key Component)
The system uses a modular, orchestrated approach with 6 specialized classes:

1. **DocumentationOrchestrator** (`src/automation/documentation_orchestrator.py`) - Main coordinator
2. **ProjectAnalyzer** (`src/automation/project_analyzer.py`) - Code analysis and metrics
3. **ReadmeGenerator** (`src/automation/readme_generator.py`) - README.md generation
4. **ChangelogGenerator** (`src/automation/changelog_generator.py`) - CHANGELOG.md management
5. **TemplateManager** (`src/automation/template_manager.py`) - External template handling
6. **FileWatcherOptimized** (`src/automation/file_watcher_optimized.py`) - Performance-optimized file monitoring

### Security Implementation
- **SecureSubprocessRunner** in `scripts/setup_automation_secure.py` uses `shlex.escape()` for command injection prevention
- All subprocess calls are sanitized and validated

## Key Configuration

### Main Configuration File
`config/automation_config.yaml` - Complete system configuration including:
- File watching patterns and ignore rules
- Documentation generation settings
- Git integration settings
- MCP server configuration
- Performance and logging settings

### Entry Points
- **Web Interface**: `src/main.py` (FastAPI application)
- **MCP Server**: `mcp_server.py` (Claude integration)
- **Auto-Documentation**: `scripts/setup_automation_secure.py`

## Important Implementation Details

### Dependencies Stack
- **Web**: FastAPI, Uvicorn
- **ML**: scikit-learn, numpy, pandas
- **Documentation**: Jinja2, PyYAML
- **MCP**: mcp, anthropic
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Security**: cryptography, shlex (built-in)

### File Structure Patterns
- Tests in `tests/` directory with `test_*.py` naming
- All automation classes in `src/automation/`
- Templates in `src/automation/templates/`
- Configuration in `config/`
- Scripts in `scripts/`

### Current Status
- **Branch**: `enhanced-auto-docs-system` 
- **Status**: CodeRabbit and Sourcery AI recommendations implemented with real modular classes
- **Achievement**: GitHub Actions now uses real implementations instead of fake inline script
- **Quality System**: Subagetic framework implemented with honest quality reporting (no fake scores)

## Critical Notes for Development

### Testing Imports Before Changes
Always test that the modular components can be imported:
```bash
python3 -c "
from src.automation.documentation_orchestrator import DocumentationOrchestrator
from src.automation.project_analyzer import ProjectAnalyzer
from scripts.setup_automation_secure import SecureSubprocessRunner
print('✅ All imports successful')
"
```

### GitHub Actions Integration
The workflow (`.github/workflows/auto-docs.yml`) now uses real implementations including DocumentationOrchestrator, SecureSubprocessRunner, and modular classes. This proves to CodeRabbit and Sourcery AI that their recommendations were actually implemented, not just mentioned.

### MCP Server Integration
The system provides MCP tools for Claude integration. The server exposes various code analysis and documentation tools through the MCP protocol.

### Auto-Documentation Trigger
The system monitors file changes and automatically updates documentation. Key files that trigger updates:
- Any `.py` file in `src/`
- Test files (`test_*.py`)
- Configuration files (`.yaml`, `.json`)
- Requirements and setup files
## 🤖 **INSTRUÇÃO OBRIGATÓRIA**: Sistema Subagetic Multi-Agente

### **SEMPRE USE SUBAGENTES** para garantir qualidade de entrega
Claude Code deve OBRIGATORIAMENTE usar o sistema de subagentes dinâmicos para todas as tarefas complexas neste projeto. Isso garante qualidade, validação e entrega confiável.

### Arquitetura Obrigatória
**NUNCA trabalhe sozinho em tarefas complexas - SEMPRE decomponha em 4 agentes:**

### Architecture
```
┌─────────────────────────────────────────────────────────┐
│                COORDINATOR AGENT                        │
│  • Task decomposition & orchestration                  │
│  • Self-prompting iteration control                    │
│  • Cross-agent communication hub                       │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐ ┌────────▼────────┐ ┌──────▼──────┐
│ ANALYZER AGENT │ │ EXECUTOR AGENT  │ │ VALIDATOR   │
│ • Problem      │ │ • Code/solution │ │ • Quality   │
│   analysis     │ │   generation    │ │   assurance │
│ • Pattern      │ │ • Implementation│ │ • Testing   │
│   recognition  │ │ • Optimization  │ │ • Feedback  │
└────────────────┘ └─────────────────┘ └─────────────┘
```

### Self-Prompting Mechanism
Each agent maintains:
- Context memory for learning retention
- Self-evaluation criteria for quality assessment
- Iterative improvement prompts for continuous enhancement
- Cross-agent feedback loops for collaborative learning

### Agent Roles and Self-Prompting Templates

#### Coordinator Agent
```python
COORDINATOR_SELF_PROMPT = """
Role: Task orchestration and workflow management

Self-Prompting Questions:
- "How can I better decompose this complex task?"
- "What dependencies exist between subtasks?"
- "Am I allocating work optimally across agents?"
- "What have I learned from previous iterations?"

Responsibilities:
- Initial task decomposition
- Agent work allocation  
- Progress monitoring
- Cross-agent communication
- Iteration control and refinement
"""
```

#### Analyzer Agent
```python
ANALYZER_SELF_PROMPT = """
Role: Deep problem analysis and pattern recognition

Self-Prompting Questions:
- "What underlying patterns am I detecting?"
- "Have I considered all problem dimensions?"
- "What assumptions might be limiting my analysis?"
- "How can I improve my analytical framework?"

Responsibilities:
- Problem space exploration
- Constraint identification
- Pattern recognition
- Risk analysis
- Solution space mapping
"""
```

#### Executor Agent
```python
EXECUTOR_SELF_PROMPT = """
Role: Solution implementation and optimization

Self-Prompting Questions:
- "Is this the most elegant solution approach?"
- "Have I considered performance implications?"
- "What alternative implementations exist?"
- "How can I make this more maintainable?"

Responsibilities:
- Code/solution generation
- Implementation optimization
- Resource efficiency
- Scalability considerations
- Documentation generation
"""
```

#### Validator Agent
```python
VALIDATOR_SELF_PROMPT = """
Role: Quality assurance and testing

Self-Prompting Questions:
- "What edge cases have I missed?"
- "Are my test scenarios comprehensive?"
- "How can I strengthen validation criteria?"
- "What failure modes should I anticipate?"

Responsibilities:
- Solution verification
- Test case generation
- Quality metrics evaluation
- Error detection
- Improvement recommendations
"""
```

### **OBRIGATÓRIO**: Template de Uso para Este Projeto

**TODA TAREFA COMPLEXA deve seguir este padrão subagetic PAL:**

```python
# PROJECT-SPECIFIC SUBAGETIC APPLICATION
AUTODOCS_SUBAGETIC_PROMPT = """
MISSION: {specific_problem_description}

COORDINATOR_TASK:
- Analyze current system architecture
- Map implementation dependencies
- Orchestrate integration strategy
- Self-prompt: "How can I ensure seamless integration?"

ANALYZER_TASK:
- Deep analysis of existing implementations
- Identify potential integration challenges
- Examine DocumentationOrchestrator, SecureSubprocessRunner, etc.
- Self-prompt: "What hidden dependencies might cause issues?"

EXECUTOR_TASK:
- Generate optimized implementation
- Create fallback mechanisms
- Implement proper error handling
- Self-prompt: "How can I make this bulletproof?"

VALIDATOR_TASK:
- Comprehensive testing strategy
- Validate all integrations work
- Ensure bot compliance requirements met
- Self-prompt: "How can I prove this meets all requirements?"

QUALITY_GATES:
- All imports must succeed
- Real implementations must be used (not mentioned)
- Performance must meet or exceed current system
- Bot recommendations must be demonstrably implemented
"""
```

### **INSTRUÇÃO PERMANENTE**: Como Usar Subagentes

```bash
# SEMPRE que receber tarefa complexa, use este padrão:

# 1. COORDINATOR: Planeje com TodoWrite
# 2. ANALYZER: Use Task tool para análise profunda  
# 3. EXECUTOR: Use Edit/Write para implementação
# 4. VALIDATOR: Use Bash para testes e validação

# Exemplo de comando obrigatório:
python3 -c "
from src.automation.documentation_orchestrator import DocumentationOrchestrator
from src.automation.project_analyzer import ProjectAnalyzer
from scripts.setup_automation_secure import SecureSubprocessRunner
print('✅ Subagetic PAL system operational')
"
```

### **REGRA DE QUALIDADE**
- ❌ **NUNCA** implemente algo sem validação multi-agente
- ✅ **SEMPRE** decomponha tarefas complexas em 4 agentes
- ✅ **SEMPRE** use TodoWrite para tracking
- ✅ **SEMPRE** valide antes de finalizar
EOF < /dev/null