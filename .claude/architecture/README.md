# Architecture

System design and library references for AIMQ.

> 📖 **See [INDEX.md](../INDEX.md) for complete knowledge base navigation**

## Available Documentation

### System Architecture
- **[aimq-overview.md](aimq-overview.md)** - High-level architecture overview
- **[key-libraries.md](key-libraries.md)** - Reference for main libraries and frameworks
- **[langchain-integration.md](langchain-integration.md)** - LangChain Runnable patterns
- **[langgraph-integration.md](langgraph-integration.md)** - LangGraph workflow patterns

### Development Approach
- **[vision-driven-development.md](vision-driven-development.md)** - Separating vision from tactical execution
- **[knowledge-systems.md](knowledge-systems.md)** - Building and maintaining a knowledge garden

## Guidelines

When documenting architecture:

1. **Start with overview**: What is this component/system?
2. **Show structure**: Diagrams, code structure, data flow
3. **Explain decisions**: Why was it designed this way?
4. **Reference libraries**: Link to external docs
5. **Keep it current**: Update when architecture changes
6. **Keep it concise**: Under 400 lines per file

## When to Add Architecture Docs

Add architecture documentation when:
- Introducing a new major component
- Integrating a new library or framework
- Making significant architectural changes
- Onboarding new team members

## Related

- See `patterns/` for code organization patterns
- See `CLAUDE.md` for comprehensive technical documentation
- See `README.md` for user-facing documentation
