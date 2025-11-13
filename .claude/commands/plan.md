---
description: Review and update the project plan
---

# Plan Helper

Manage the project plan by reviewing progress and planning next steps.

## Overview

This command helps with project planning by:
1. Reading PLAN.md and recent git history
2. Suggesting next steps based on current state
3. Recording new plans in PLAN.md
4. Keeping the plan aligned with reality
5. Helping prioritize work

## Usage

### Without Arguments
```
/plan
```
Reviews PLAN.md and git history to suggest next steps.

### With Arguments
```
/plan <description or goal>
```
Uses the input to create or update the plan in PLAN.md.

## Task List

### Mode 1: Review and Suggest (No Arguments)

When called without arguments, analyze the current state:

#### Step 1: Read PLAN.md

Load and parse the plan:
```bash
cat PLAN.md
```

Understand:
- What's marked as completed
- What's in progress
- What's planned next
- Current priorities
- Open questions

#### Step 2: Check Recent History

Review recent commits:
```bash
# Get recent commits
git log --oneline -20

# Get detailed recent changes
git log --stat -10

# Check current branch
git branch --show-current

# Check for uncommitted changes
git status --short
```

Analyze:
- What was recently completed
- What's currently being worked on
- Patterns in recent work
- Velocity and progress

#### Step 3: Assess Current State

Compare PLAN.md with reality:

**Questions to answer**:
- Is completed work marked as done in PLAN.md?
- Are there new features not in the plan?
- Has the direction changed?
- Are priorities still valid?
- What's blocking progress?

**Check for**:
- Outdated items in the plan
- Completed items not marked done
- New work not documented
- Changed priorities
- Technical debt accumulating

#### Step 4: Suggest Next Steps

Based on the analysis, suggest:

**Immediate actions** (can do now):
- Complete in-progress work
- Fix known issues
- Update documentation
- Improve test coverage

**Short-term goals** (this week):
- Next features to build
- Refactoring needed
- Technical debt to address
- Documentation to write

**Long-term vision** (this month+):
- Major features
- Architecture changes
- Performance improvements
- New capabilities

#### Step 5: Present Suggestions

Format suggestions clearly:

```
📋 Plan Review

**Current Status**:
- Branch: feature/langgraph
- Recent work: Added comprehensive test suite (82% coverage)
- Last updated: 2 hours ago

**Completed but not marked in PLAN.md**:
- ✅ Added 40 new tests
- ✅ Achieved 100% coverage for agents and workflows
- ✅ Implemented graceful error handling

**Suggested Next Steps**:

**Option A: Continue Quality Focus** (Recommended)
1. Add tests for tools/ directory (0% coverage) - 2-3 hours
2. Improve worker and queue coverage to 90%+ - 2 hours
3. Update documentation for new structure - 1 hour
**Total**: ~5 hours to reach 90%+ coverage

**Option B: New Features**
1. Implement memory/RAG integration - 1-2 days
2. Add streaming support - 4-6 hours
3. Create advanced examples - 2-3 hours
**Total**: ~2-3 days for major capabilities

**Option C: Production Ready**
1. Add observability (LangSmith/tracing) - 4-6 hours
2. Implement streaming - 4-6 hours
3. Add deployment guides - 2-3 hours
**Total**: ~2 days for production features

**My Recommendation**:
Option A - Let's get to 90%+ coverage before adding new features.
Solid foundation = confident iteration.

Should I:
1. Update PLAN.md with completed work?
2. Start on Option A?
3. Discuss a different direction?
```

### Mode 2: Create/Update Plan (With Arguments)

When given input, create or update the plan:

#### Step 1: Parse the Input

Understand what's being requested:
- New feature to plan
- Goal to achieve
- Problem to solve
- Direction to explore

#### Step 2: Research and Analyze

Gather context:
- Check if related work exists
- Look for dependencies
- Estimate complexity
- Identify risks

#### Step 3: Break Down the Work

Create a structured plan:

**Define the goal**:
- What are we trying to achieve?
- Why is this important?
- What's the success criteria?

**Identify tasks**:
- Break into concrete steps
- Estimate effort for each
- Note dependencies
- Flag risks or unknowns

**Prioritize**:
- What must be done first?
- What can be done in parallel?
- What's optional?

#### Step 4: Draft the Plan

Create a clear, actionable plan:

```markdown
## [Feature/Goal Name]

**Goal**: [Clear description of what we're building]

**Why**: [Motivation and value]

**Success Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Tasks**:

### Phase 1: Foundation (X hours)
- [ ] Task 1 - Description (estimate)
- [ ] Task 2 - Description (estimate)

### Phase 2: Implementation (Y hours)
- [ ] Task 3 - Description (estimate)
- [ ] Task 4 - Description (estimate)

### Phase 3: Polish (Z hours)
- [ ] Task 5 - Description (estimate)
- [ ] Task 6 - Description (estimate)

**Dependencies**:
- Dependency 1
- Dependency 2

**Risks**:
- Risk 1 - Mitigation strategy
- Risk 2 - Mitigation strategy

**Total Estimate**: X+Y+Z hours (~N days)
```

#### Step 5: Get Approval

Present the plan:

```
📝 Here's the plan I've drafted:

[Show the plan]

**Key Points**:
- Total effort: ~X days
- Main risks: [List]
- Dependencies: [List]
- Can start: [Yes/No, why]

**Questions for you**:
1. Does this align with your vision?
2. Is the scope right, or should we adjust?
3. Any concerns about the approach?
4. Should I add this to PLAN.md?
```

#### Step 6: Update PLAN.md

If approved, update the plan file:

**Add to appropriate section**:
- Completed work → "✅ Completed Work"
- Current work → "🎯 Current Status"
- Future work → "📋 Recommended Next Steps"

**Keep it organized**:
- Use clear headings
- Add dates
- Link related items
- Remove outdated content

**Maintain structure**:
```markdown
# Project Plan

**Last Updated**: [Date]

## ✅ Completed Work
[Recently completed items]

## 🎯 Current Status
[What's happening now]

## 📋 Recommended Next Steps
[What's coming next]

## 🤔 Open Questions
[Things to decide]
```

#### Step 7: Confirm Update

Show what changed:

```
✅ Updated PLAN.md!

**Added**:
- New feature plan in "Recommended Next Steps"
- Updated "Last Updated" date
- Marked recent work as completed

**Removed**:
- Outdated items from previous sprint

**Next**: Ready to start implementation, or should we refine the plan?
```

## Planning Best Practices

### 1. Keep Plans Current
- Update after completing work
- Review weekly
- Remove outdated items
- Adjust based on learnings

### 2. Be Realistic
- Estimate conservatively
- Account for unknowns
- Include buffer time
- Track actual vs estimated

### 3. Stay Flexible
- Plans change, that's okay
- Adapt to new information
- Reprioritize as needed
- Don't be dogmatic

### 4. Focus on Value
- Prioritize high-impact work
- Consider effort vs value
- Don't over-plan
- Ship iteratively

### 5. Communicate Clearly
- Use simple language
- Be specific about tasks
- Include context and why
- Make it easy to understand

### 6. Track Progress
- Mark completed items
- Note blockers
- Celebrate wins
- Learn from delays

## Examples

### Example 1: Review Current Plan

**Command**: `/plan`

**Output**:
```
📋 Reviewing project plan...

**Current State**:
- 82% test coverage (target: 90%)
- 4 modules at 100% coverage
- Tools directory untested

**Recent Completions** (not in PLAN.md):
- ✅ Added 40 new tests
- ✅ Improved coverage from 79% to 82%
- ✅ Fixed error handling in worker

**Recommended Next**:
1. Test tools/ directory (biggest gap)
2. Improve worker/queue to 90%
3. Then add new features

Should I update PLAN.md with these completions?
```

### Example 2: Plan New Feature

**Command**: `/plan add streaming support for agent responses`

**Output**:
```
📝 Planning streaming support...

**Goal**: Enable real-time streaming of agent responses

**Why**: Better UX for long-running agents, see progress in real-time

**Plan**:

### Phase 1: Foundation (4 hours)
- [ ] Research LangChain streaming APIs
- [ ] Design streaming interface
- [ ] Add streaming types/protocols

### Phase 2: Implementation (6 hours)
- [ ] Implement streaming in BaseAgent
- [ ] Add streaming to ReActAgent
- [ ] Add streaming to workflows
- [ ] Update queue to support streaming

### Phase 3: Testing & Docs (4 hours)
- [ ] Write streaming tests
- [ ] Create streaming example
- [ ] Update documentation

**Total**: ~14 hours (2 days)

**Dependencies**: None, can start now

**Risks**:
- LangChain streaming API might be complex
- Need to handle errors in streams

Does this look good? Should I add to PLAN.md?
```

### Example 3: Update Priorities

**Command**: `/plan shift focus to production readiness`

**Output**:
```
📝 Updating plan for production focus...

**New Priority**: Production Readiness

**Updated Plan**:

### Immediate (This Week)
1. Add observability (LangSmith integration)
2. Improve error handling and logging
3. Add health check endpoints
4. Write deployment guide

### Short-term (Next Week)
1. Add monitoring and alerting
2. Performance testing
3. Security audit
4. Load testing

### Before Launch
1. Complete documentation
2. Create runbooks
3. Set up staging environment
4. Plan rollout strategy

**Deferred** (after launch):
- New agent types
- Advanced features
- UI improvements

Should I update PLAN.md with this new direction?
```

## Error Handling

### PLAN.md Doesn't Exist
**Solution**:
- Offer to create it
- Use template structure
- Populate with current state
- Ask about goals

### Git History Unclear
**Solution**:
- Focus on PLAN.md content
- Ask user about recent work
- Review file changes
- Make best guess

### Conflicting Priorities
**Solution**:
- Present the conflict
- Explain trade-offs
- Ask user to decide
- Document decision

### Plan Too Vague
**Solution**:
- Ask clarifying questions
- Request more details
- Suggest specific tasks
- Iterate on the plan

## Reusability

This command works across:
- Any project with a PLAN.md file
- Any git repository
- Any programming language
- Any agent or AI assistant

The key is to:
- Read and understand the plan format
- Analyze git history
- Suggest actionable next steps
- Keep the plan updated

---

**Remember**: A good plan is a living document, not a rigid contract! 📋✨
