# AIMQ Demos

This directory contains working demonstrations of AIMQ features. Each demo is self-contained with its own README, test scripts, and worker implementations.

## Available Demos

### 📧 [Email Processing](./email-processing/)

AI-powered email processing system with intelligent routing and automated responses.

**Features:**
- Resend webhook integration
- Workspace/channel routing (subdomain → workspace, user → channel)
- AI agent responses using LangChain + OpenAI
- Attachment handling
- Thread support

**Quick Start:**
```bash
cd demos/email-processing
./test_full_flow.py
```

## Demo vs Examples

**Demos** (`demos/`) - Complete, runnable demonstrations of features:
- Full workflow implementations
- Test scripts and verification
- Documentation and setup guides
- Meant to showcase capabilities

**Examples** (`examples/`) - Code-focused learning resources:
- Minimal, focused code samples
- Teaching specific concepts
- Building blocks for your own implementations
- Meant for developers to learn from

## Adding a New Demo

1. Create a subdirectory: `demos/your-feature/`
2. Add a README.md with:
   - Overview and architecture
   - Setup instructions
   - Demo scenarios
   - Verification steps
3. Include test scripts and worker implementations
4. Update this index

## Running Demos

Most demos require:
- Supabase running locally (`supabase start`)
- Environment variables configured (`.env`)
- Dependencies installed (`uv sync`)

See each demo's README for specific requirements.
