---
description: Explore topics from the knowledge garden
---

# Focus Helper

Dive deep into topics from the knowledge garden to understand patterns, standards, and architecture.

## Overview

This command helps explore the knowledge garden by:
1. Identifying topics from recent conversation
2. Finding related content in the knowledge garden
3. Presenting relevant patterns and standards
4. Connecting related concepts
5. Helping apply knowledge to current work

## Usage

### Without Arguments
```
/focus
```
Identifies topics from the conversation and explores them in the knowledge garden.

### With Arguments
```
/focus <topic>
```
Explores the specified topic in the knowledge garden.

## Task List

### Step 1: Identify Topics

**If no arguments provided**:
- Review recent conversation
- Extract key topics and concepts
- Identify technical terms
- Note patterns mentioned
- List technologies discussed

**If arguments provided**:
- Parse the topic
- Identify related keywords
- Expand to related concepts

### Step 2: Search Knowledge Garden

Look for related content:

```bash
# Search all knowledge garden files
rg -i "topic" .claude/

# Search specific categories
rg -i "topic" .claude/patterns/
rg -i "topic" .claude/standards/
rg -i "topic" .claude/architecture/
rg -i "topic" .claude/quick-references/

# List files that might be relevant
fd -e md . .claude/ | rg -i "topic"
```

### Step 3: Gather Related Content

For each match found:
- Read the full file
- Extract relevant sections
- Note related links
- Identify connected topics

### Step 4: Organize Findings

Group content by category:

**Patterns**:
- Code patterns related to topic
- Design patterns
- Implementation approaches

**Standards**:
- Best practices
- Conventions
- Guidelines

**Architecture**:
- Design decisions
- System structure
- Integration points

**Quick References**:
- How-to guides
- Troubleshooting
- Common tasks

### Step 5: Present Findings

Show relevant knowledge:

```
🔍 Exploring: [Topic]

**Found in Knowledge Garden**:

## Patterns
📁 .claude/patterns/error-handling.md
- Graceful error handling in workers
- Catch and log, don't crash
- Example: [code snippet]

📁 .claude/patterns/retry-logic.md
- Exponential backoff for retries
- Max retry limits
- Example: [code snippet]

## Standards
📁 .claude/standards/error-logging.md
- Always log errors with context
- Include stack traces
- Use structured logging

## Architecture
📁 .claude/architecture/worker-design.md
- Workers are resilient by design
- No exception re-raising
- Graceful degradation

## Quick References
📁 .claude/quick-references/debugging-workers.md
- How to debug worker issues
- Common problems and solutions
- Troubleshooting checklist

**Related Topics**:
- Logging
- Monitoring
- Resilience
- Testing

Would you like me to:
1. Dive deeper into any of these?
2. Show code examples?
3. Explain how to apply this?
```

### Step 6: Connect the Dots

Show relationships between topics:

```
🕸️ Knowledge Graph:

Error Handling
├── Related Patterns
│   ├── Retry Logic
│   ├── Circuit Breaker
│   └── Graceful Degradation
├── Related Standards
│   ├── Error Logging
│   ├── Exception Handling
│   └── Testing Error Paths
└── Related Architecture
    ├── Worker Design
    ├── Resilience Strategy
    └── Monitoring Setup

**Key Connections**:
- Error handling requires good logging (see error-logging.md)
- Workers use graceful error handling (see worker-design.md)
- All error paths should be tested (see testing.md)
```

### Step 7: Provide Context

Explain how this applies to current work:

```
💡 How This Applies:

**Current Context**:
- We're working on worker stability
- Recent commits added error handling
- Tests verify graceful degradation

**Relevant Knowledge**:
1. **Pattern**: Graceful Error Handling
   - Matches what we just implemented
   - Confirms our approach is sound
   - Suggests additional improvements

2. **Standard**: Error Logging
   - We should add structured logging
   - Include context in error messages
   - Set up log aggregation

3. **Architecture**: Worker Design
   - Documents our design decisions
   - Explains trade-offs we made
   - Guides future changes

**Next Steps**:
- Apply error logging standard
- Add monitoring (see monitoring.md)
- Document our implementation
```

### Step 8: Suggest Deep Dives

Offer to explore further:

```
🎯 Want to go deeper?

I can explore:
1. **Retry Logic Pattern** - How to implement robust retries
2. **Monitoring Setup** - How to observe worker health
3. **Testing Error Paths** - How to test error handling
4. **Circuit Breaker Pattern** - Advanced resilience

Which interests you?
```

## Search Strategies

### Strategy 1: Keyword Search
Search for exact terms:
```bash
rg -i "error handling" .claude/
rg -i "testing" .claude/
rg -i "architecture" .claude/
```

### Strategy 2: Concept Search
Search for related concepts:
```bash
# For "error handling", also search:
rg -i "exception" .claude/
rg -i "resilience" .claude/
rg -i "failure" .claude/
```

### Strategy 3: File Name Search
Look for relevant files:
```bash
fd -e md error .claude/
fd -e md test .claude/
fd -e md worker .claude/
```

### Strategy 4: Link Following
Follow references in files:
- Read linked documents
- Explore related topics
- Build knowledge graph
- Find connections

## Presentation Formats

### Format 1: Summary View
Quick overview of findings:
```
🔍 Topic: Error Handling

**Found**: 5 documents
- 2 patterns
- 2 standards
- 1 architecture doc

**Key Insights**:
- Always catch and log
- Never crash the worker
- Test error paths

**Related**: logging, testing, monitoring
```

### Format 2: Detailed View
Full content with examples:
```
🔍 Deep Dive: Error Handling

## Pattern: Graceful Error Handling
[Full pattern content]

## Standard: Error Logging
[Full standard content]

## Example from Codebase
[Actual code example]

## How to Apply
[Step-by-step guidance]
```

### Format 3: Graph View
Visual relationships:
```
🕸️ Knowledge Graph

Error Handling ─┬─ Patterns
                │   ├─ Retry Logic
                │   └─ Circuit Breaker
                ├─ Standards
                │   ├─ Logging
                │   └─ Testing
                └─ Architecture
                    └─ Worker Design
```

### Format 4: Checklist View
Actionable items:
```
✅ Error Handling Checklist

Based on knowledge garden:
- [ ] Catch exceptions in worker loop
- [ ] Log errors with context
- [ ] Add retry logic for transient failures
- [ ] Test error paths
- [ ] Monitor error rates
- [ ] Document error handling strategy
```

## Best Practices

### 1. Start Broad, Then Narrow
- Begin with general search
- Identify relevant areas
- Dive deep into specifics
- Connect back to context

### 2. Follow the Links
- Read referenced documents
- Explore related topics
- Build understanding
- See the big picture

### 3. Apply to Current Work
- Connect knowledge to task
- Show practical application
- Suggest next steps
- Make it actionable

### 4. Update as You Learn
- Note gaps in knowledge
- Suggest additions
- Update outdated content
- Keep garden fresh

### 5. Share Insights
- Explain what you found
- Show connections
- Provide context
- Make it useful

## Examples

### Example 1: Focus from Conversation

**Command**: `/focus`

**Output**:
```
🔍 Analyzing conversation for topics...

**Topics Identified**:
- Error handling
- Testing
- Worker design
- Coverage

**Searching knowledge garden...**

## Error Handling
Found 3 documents:

📁 patterns/graceful-error-handling.md
- Catch and log, don't crash
- Matches our recent implementation ✅

📁 standards/error-logging.md
- Structured logging with context
- We should add this 💡

📁 architecture/worker-design.md
- Documents our design decisions
- Explains why we don't re-raise ✅

## Testing
Found 2 documents:

📁 standards/testing.md
- Mock external dependencies ✅
- We're following this

📁 patterns/testing-mocks.md
- Specific mock patterns
- Could improve our tests 💡

**Summary**:
- Our approach aligns with knowledge garden ✅
- Found 2 improvement opportunities 💡
- All patterns documented

Want to explore any topic deeper?
```

### Example 2: Focus on Specific Topic

**Command**: `/focus testing patterns`

**Output**:
```
🔍 Exploring: Testing Patterns

**Found in Knowledge Garden**:

## Patterns
📁 patterns/testing-mocks.md
```python
# Mock external services
@pytest.fixture
def mock_supabase(mocker):
    return mocker.patch('module.supabase_client')

def test_with_mock(mock_supabase):
    mock_supabase.query.return_value = []
    result = function_under_test()
    assert result == expected
```

📁 patterns/parametrized-tests.md
```python
@pytest.mark.parametrize("input,expected", [
    ("a", "A"),
    ("hello", "HELLO"),
])
def test_multiple_cases(input, expected):
    assert transform(input) == expected
```

## Standards
📁 standards/testing.md
- Aim for 80%+ coverage
- Test happy path and errors
- Keep tests fast (<1s each)
- Mock external dependencies

## Quick References
📁 quick-references/pytest-guide.md
- Common pytest patterns
- Fixture examples
- Troubleshooting tips

**How This Applies**:
- We're using these patterns ✅
- Could add more parametrized tests 💡
- Coverage is good (82%) ✅

**Related Topics**:
- Mocking
- Coverage
- Test organization
- CI/CD

Want to see examples from our codebase?
```

### Example 3: Focus with Application

**Command**: `/focus worker error handling`

**Output**:
```
🔍 Exploring: Worker Error Handling

**Knowledge Garden**:

## Pattern: Graceful Error Handling
**Problem**: Workers crash on job errors
**Solution**: Catch exceptions, log, continue

```python
def process_job(job):
    try:
        # Process the job
        result = do_work(job)
        return result
    except Exception as e:
        # Log but don't crash
        logger.error(f"Job failed: {e}", exc_info=True)
        return None
```

## Architecture: Worker Design
**Decision**: Workers never re-raise exceptions
**Rationale**: System stability over error propagation
**Trade-off**: Must monitor logs for errors

## Standard: Error Logging
**Guideline**: Always log with context
```python
logger.error(
    "Job processing failed",
    extra={
        "job_id": job.id,
        "error": str(e),
        "stack_trace": traceback.format_exc()
    }
)
```

**Your Implementation** (from recent commit):
```python
# From src/aimq/worker.py
except Exception as e:
    logger.error(f"Task failed: {e}")
    # Don't re-raise - keep worker running
```

**Comparison**:
- ✅ Catches exceptions
- ✅ Logs errors
- ✅ Doesn't re-raise
- 💡 Could add structured logging
- 💡 Could add job context

**Suggested Improvements**:
1. Add structured logging (see error-logging.md)
2. Include job ID in logs
3. Add error metrics (see monitoring.md)

Want me to implement these improvements?
```

## Error Handling

### Topic Not Found
**Solution**:
- Search with broader terms
- Check spelling
- List available topics
- Suggest related topics

### Too Many Results
**Solution**:
- Narrow the search
- Prioritize by relevance
- Group by category
- Show summary first

### Outdated Content
**Solution**:
- Note the discrepancy
- Suggest updating
- Use current code as truth
- Add to garden maintenance

### No Clear Application
**Solution**:
- Explain the concept
- Show general examples
- Ask about use case
- Suggest when it applies

## Reusability

This command works across:
- Any project with a knowledge garden
- Any topic or domain
- Any programming language
- Any agent or AI assistant

The key is to:
- Search effectively
- Present clearly
- Connect to context
- Make it actionable

---

**Remember**: The knowledge garden is your guide - explore it often! 🔍🌱✨
