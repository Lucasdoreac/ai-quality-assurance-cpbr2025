# Architecture Documentation

## Project Overview

This project follows a modular architecture with clear separation of concerns.

## Structure

- **Total Files:** 21
- **Total Classes:** 47
- **Total Functions:** 202

## Key Components

### Source Code Organization
```
src/
├── domain/           # Business logic and entities
├── application/      # Use cases and application services  
├── infrastructure/   # External concerns and adapters
└── automation/       # Documentation automation system
```

### Documentation Generation
- **Modular Design:** Separate components for each doc type
- **Async Processing:** Concurrent generation of multiple docs
- **Validation:** Automatic quality checking
- **Orchestration:** Coordinated updates across all documentation

## Design Patterns

- **Clean Architecture:** Separation of concerns across layers
- **Factory Pattern:** Component initialization and configuration
- **Strategy Pattern:** Different generators for different doc types
- **Observer Pattern:** File watching and change detection

---

*Architecture documentation generated automatically on 2025-06-18 09:52:50*
