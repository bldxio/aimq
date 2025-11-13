---
description: Research topics and add new knowledge to the garden
---

# Level Up Helper

Research topics on the web and add new knowledge to the knowledge garden.

## Overview

This command helps expand knowledge by:
1. Identifying topics from conversation or arguments
2. Researching the topic on the web
3. Summarizing findings
4. Evaluating relevance to the project
5. Adding valuable insights to the knowledge garden

## Usage

### Without Arguments
```
/levelup
```
Identifies topics from the conversation and researches them.

### With Arguments
```
/levelup <topic>
```
Researches the specified topic and considers adding to the knowledge garden.

## Task List

### Step 1: Identify Research Topic

**If no arguments provided**:
- Review recent conversation
- Identify knowledge gaps
- Note unfamiliar concepts
- Find areas to deepen understanding
- List technologies or patterns mentioned

**If arguments provided**:
- Parse the topic
- Clarify scope
- Identify specific questions
- Determine research goals

### Step 2: Formulate Research Questions

Before searching, define what to learn:

**Technical topics**:
- What is it?
- How does it work?
- When to use it?
- Best practices?
- Common pitfalls?
- Alternatives?

**Patterns/Practices**:
- What problem does it solve?
- How to implement it?
- When is it appropriate?
- What are the trade-offs?
- Real-world examples?

**Tools/Libraries**:
- What does it do?
- How to use it?
- Integration patterns?
- Performance characteristics?
- Comparison with alternatives?

### Step 3: Research the Topic

Use web search to gather information:

```
Search queries to try:
- "[topic] best practices"
- "[topic] tutorial"
- "[topic] vs alternatives"
- "[topic] common mistakes"
- "[topic] production use"
- "[topic] [language] implementation"
```

**Look for**:
- Official documentation
- Authoritative blog posts
- Stack Overflow discussions
- GitHub repositories
- Conference talks
- Academic papers (if relevant)

**Prioritize**:
- Recent content (last 2 years)
- Authoritative sources
- Practical examples
- Real-world experience
- Community consensus

### Step 4: Synthesize Findings

Organize what you learned:

**Key Concepts**:
- Core ideas
- Important terminology
- Fundamental principles

**Practical Knowledge**:
- How to implement
- Code examples
- Configuration
- Integration patterns

**Best Practices**:
- Recommended approaches
- Common patterns
- Things to avoid
- Performance tips

**Trade-offs**:
- Advantages
- Disadvantages
- When to use
- When not to use

### Step 5: Summarize for Review

Present findings clearly:

```
🚀 Research Summary: [Topic]

**What I Learned**:

## Overview
[Brief explanation of the topic]

## Key Concepts
- Concept 1: [explanation]
- Concept 2: [explanation]
- Concept 3: [explanation]

## Best Practices
1. [Practice 1]
2. [Practice 2]
3. [Practice 3]

## Implementation Example
```[language]
[Code example]
```

## When to Use
- Scenario 1
- Scenario 2

## When NOT to Use
- Scenario 1
- Scenario 2

## Trade-offs
**Pros**:
- Advantage 1
- Advantage 2

**Cons**:
- Disadvantage 1
- Disadvantage 2

## Alternatives
- Alternative 1: [brief comparison]
- Alternative 2: [brief comparison]

**Sources**:
- [Link 1]
- [Link 2]
- [Link 3]

---

**Relevance to Our Project**:
[How this applies to current work]

**Should we add this to the knowledge garden?**
```

### Step 6: Evaluate Relevance

Assess if this should be added:

**High relevance** (definitely add):
- Directly applicable to current work
- Solves a known problem
- Fills a knowledge gap
- Aligns with project goals
- Team will use this

**Medium relevance** (consider adding):
- Potentially useful
- Related to project domain
- Good to know
- Might use in future
- Educational value

**Low relevance** (probably skip):
- Not applicable to project
- Too theoretical
- Already well-known
- Doesn't fit project needs
- Better alternatives exist

### Step 7: Determine Location

If adding to knowledge garden, choose where:

**Patterns** (`.claude/patterns/`):
- Implementation patterns
- Design patterns
- Code structures
- Reusable solutions

**Standards** (`.claude/standards/`):
- Best practices
- Conventions
- Guidelines
- Team agreements

**Architecture** (`.claude/architecture/`):
- System design
- Technology choices
- Integration patterns
- Design decisions

**Quick References** (`.claude/quick-references/`):
- How-to guides
- Checklists
- Troubleshooting
- Common tasks

### Step 8: Create Knowledge Garden Entry

Format the content appropriately:

**Pattern format**:
```markdown
# [Pattern Name]

## Overview
[What this pattern is]

## Problem
[What problem it solves]

## Solution
[How to implement it]

## Example
```[language]
[Code example]
```

## When to Use
- [Scenario 1]
- [Scenario 2]

## When NOT to Use
- [Scenario 1]
- [Scenario 2]

## Trade-offs
**Pros**: [advantages]
**Cons**: [disadvantages]

## Alternatives
- [Alternative 1]
- [Alternative 2]

## References
- [Source 1]
- [Source 2]

## Related
- [Related pattern 1]
- [Related pattern 2]
```

### Step 9: Confirm Addition

Show what will be added:

```
✅ Ready to add to knowledge garden!

**File**: .claude/patterns/circuit-breaker.md

**Content Preview**:
# Circuit Breaker Pattern

## Overview
Prevents cascading failures by stopping requests to failing services.

## Problem
When a service fails, continued requests waste resources and slow down the system.

## Solution
[Full content...]

**This will help us**:
- Improve resilience
- Handle service failures gracefully
- Prevent cascading failures

**Related to**:
- Retry logic pattern
- Error handling standard
- Resilience architecture

Should I add this to the knowledge garden?
```

### Step 10: Suggest Application

After adding, suggest how to use it:

```
🎯 How to Apply This:

**Immediate opportunities**:
1. Add circuit breaker to external API calls
2. Implement in worker job processing
3. Use for database connections

**Next steps**:
1. Choose a circuit breaker library
2. Implement in one service first
3. Monitor and tune thresholds
4. Roll out to other services

Want me to help implement this?
```

## Research Strategies

### Strategy 1: Official Documentation First
- Start with official docs
- Understand the basics
- Learn the intended use
- See official examples

### Strategy 2: Community Wisdom
- Check Stack Overflow
- Read blog posts
- Watch conference talks
- Learn from others' experience

### Strategy 3: Code Examples
- Find real implementations
- Study open source projects
- See production usage
- Learn practical patterns

### Strategy 4: Comparative Analysis
- Compare with alternatives
- Understand trade-offs
- See when each is best
- Make informed choices

## Best Practices

### 1. Verify Information
- Check multiple sources
- Prefer authoritative sources
- Look for consensus
- Note disagreements

### 2. Focus on Practical
- Prioritize actionable knowledge
- Include code examples
- Show real-world usage
- Make it applicable

### 3. Capture Context
- Note when information is from
- Include source links
- Explain relevance
- Document assumptions

### 4. Keep It Concise
- Summarize key points
- Don't copy-paste everything
- Focus on essentials
- Link to details

### 5. Make It Discoverable
- Use clear titles
- Add good descriptions
- Link related content
- Use consistent structure

### 6. Stay Current
- Prefer recent information
- Note version-specific details
- Update as things change
- Mark outdated content

## Examples

### Example 1: Research from Conversation

**Command**: `/levelup`

**Output**:
```
🚀 Identifying topics to research...

**From conversation**:
- Circuit breaker pattern (mentioned but not detailed)
- LangSmith observability (considering for project)
- Exponential backoff (using but could optimize)

**Which should I research?**
1. Circuit breaker pattern - High priority
2. LangSmith observability - Medium priority
3. Exponential backoff - Low priority (we know this)

I recommend researching circuit breaker pattern first.
Should I proceed?
```

### Example 2: Research Specific Topic

**Command**: `/levelup circuit breaker pattern`

**Output**:
```
🚀 Researching: Circuit Breaker Pattern

**Searching...**
- Official patterns documentation
- Martin Fowler's article
- Implementation examples
- Python libraries

**Summary**:

## What It Is
A pattern that prevents cascading failures by stopping requests to failing services after a threshold is reached.

## How It Works
1. **Closed**: Normal operation, requests pass through
2. **Open**: Threshold exceeded, requests fail fast
3. **Half-Open**: Testing if service recovered

## Implementation (Python)
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60
)

@breaker
def call_external_api():
    return requests.get(api_url)
```

## Best Practices
- Set appropriate thresholds
- Monitor circuit state
- Log state changes
- Have fallback behavior

## When to Use
- External API calls
- Database connections
- Microservice communication
- Any unreliable dependency

## Trade-offs
**Pros**: Prevents cascading failures, fast failure
**Cons**: Adds complexity, needs tuning

**Relevance**: HIGH
- We call external APIs (Supabase, Mistral)
- Would improve resilience
- Aligns with our stability focus

**Should I add this to .claude/patterns/?**
```

### Example 3: Deep Dive Research

**Command**: `/levelup LangSmith observability for LangChain`

**Output**:
```
🚀 Deep Dive: LangSmith Observability

**Research findings**:

## What Is LangSmith
LangChain's observability platform for debugging, testing, and monitoring LLM applications.

## Key Features
1. **Tracing**: See every LLM call and chain step
2. **Debugging**: Inspect inputs/outputs at each step
3. **Testing**: Create test datasets and evaluate
4. **Monitoring**: Track performance and costs

## Setup (Python)
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"

# That's it! Auto-traces all LangChain calls
```

## Benefits for Our Project
- Debug agent reasoning steps
- Monitor token usage and costs
- Test agent behavior
- Track performance over time

## Costs
- Free tier: 5k traces/month
- Pro: $39/month for 50k traces
- Enterprise: Custom pricing

## Alternatives
- OpenTelemetry (more complex)
- Custom logging (less features)
- LangFuse (open source alternative)

## Recommendation
**Add to project**: YES
- Easy to integrate (2 env vars)
- Huge debugging value
- Free tier sufficient for dev
- Aligns with observability goals

**Should I**:
1. Add to .claude/architecture/observability.md?
2. Add setup guide to .claude/quick-references/?
3. Both?
```

## Error Handling

### No Clear Topic
**Solution**:
- Review conversation
- Ask user for topic
- Suggest common topics
- List knowledge gaps

### Research Yields Little
**Solution**:
- Try different search terms
- Broaden the search
- Check if topic is too niche
- Ask user for sources

### Conflicting Information
**Solution**:
- Note the conflict
- Present both views
- Explain context for each
- Recommend based on project needs

### Too Much Information
**Solution**:
- Focus on essentials
- Prioritize practical knowledge
- Summarize key points
- Link to full sources

## Reusability

This command works across:
- Any topic or domain
- Any programming language
- Any project type
- Any agent or AI assistant

The key is to:
- Research effectively
- Synthesize clearly
- Evaluate relevance
- Document well

---

**Remember**: Every new thing learned makes us stronger! 🚀📚✨
