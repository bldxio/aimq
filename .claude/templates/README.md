# Knowledge Garden Templates

> Standard templates for creating consistent, well-structured documentation

## Available Templates

### Core Documentation

- **[constitution.md](constitution.md)** - Project values, principles, and non-negotiables
- **[vision.md](vision.md)** - Long-term vision and strategic direction
- **[plan.md](plan.md)** - Current work, backlog, and progress tracking

### Knowledge Base

- **[pattern.md](pattern.md)** - Reusable solutions to common problems
- **[standard.md](standard.md)** - Team conventions and best practices
- **[architecture.md](architecture.md)** - System design and decisions
- **[quick-reference.md](quick-reference.md)** - How-to guides and checklists
- **[command.md](command.md)** - Workflow automation commands

## Usage

### Creating a New Document

1. Copy the appropriate template
2. Fill in the metadata (status, date, category)
3. Replace placeholder content with your content
4. Add cross-links to related documents
5. Update the INDEX.md to include your new document

### Template Metadata

All templates include standard metadata:

```markdown
> **Status**: Active | Deprecated | Experimental
> **Last Updated**: YYYY-MM-DD
> **Category**: category-name
```

**Status values:**
- **Active**: Currently in use and maintained
- **Deprecated**: Superseded by newer approach, kept for reference
- **Experimental**: Being tested, may change or be removed

### Cross-linking

Always add a "Related" section at the end of your document:

```markdown
## Related

- [Related Doc 1](../category/related-doc-1.md) - Brief description
- [Related Doc 2](../category/related-doc-2.md) - Brief description
```

This builds the knowledge graph and helps with navigation.

## Template Guidelines

### Keep It Focused

- One topic per document
- Under 400 lines per file
- Split large topics into multiple focused documents

### Keep It Actionable

- Focus on "how-to" over "what is"
- Include code examples
- Provide clear next steps

### Keep It Current

- Update the "Last Updated" date when you make changes
- Mark deprecated content clearly
- Remove or archive obsolete information

### Keep It Connected

- Add cross-links to related topics
- Reference external documentation
- Build a knowledge graph, not isolated islands

## Customization

These templates are starting points. Adapt them to your needs:

- Add sections that make sense for your content
- Remove sections that don't apply
- Keep the core structure (metadata, overview, related)

## Related

- [GARDENING.md](../../GARDENING.md) - Knowledge garden philosophy
- [INDEX.md](../INDEX.md) - Knowledge base index
- [commands/cultivate.md](../commands/cultivate.md) - Garden maintenance
