# Agent Configuration Hierarchy - Context-Aware Instructions

**Status**: 🌱 Core Feature
**Priority**: High - Needed for multi-agent chat
**Complexity**: Medium
**Estimated Effort**: 2-3 days

---

## What

A system for loading agent instructions from multiple sources and merging them into a single configuration. Agents receive context-aware instructions based on their workspace, channel, and role.

### Instruction Hierarchy (Most Specific → Least Specific)

1. **Participant Instructions** - Agent's role in THIS channel
2. **Channel Settings** - Instructions for primary agent in channel
3. **Membership Instructions** - Agent's job description in THIS workspace
4. **Profile Instructions** - Agent's personality/base instructions
5. **System Prompt** - Base agent behavior

---

## Why

### Business Value
- **Context-Aware Agents**: Same agent behaves differently in different contexts
- **Flexible Configuration**: Configure at multiple levels
- **Role-Based Behavior**: Agents adapt to their role
- **Easy Management**: Change behavior without changing code

### Technical Value
- **Separation of Concerns**: Instructions separate from agent logic
- **Testable**: Easy to test different configurations
- **Extensible**: Easy to add new instruction sources

---

## Architecture

### Instruction Sources

```
System Prompt (hardcoded)
    ↓
Profile Instructions (agent personality)
    ↓
Membership Instructions (workspace job description)
    ↓
Channel Settings (primary agent instructions)
    ↓
Participant Instructions (channel-specific role)
    ↓
Final Merged Instructions
```

### Example Hierarchy

```yaml
# System Prompt (base)
You are a helpful AI assistant.

# Profile Instructions (personality)
You are friendly, concise, and love using emojis! 🎉
You specialize in customer support.

# Membership Instructions (job description in workspace)
You are the customer support agent for Acme Corp.
Help users with billing, technical issues, and general questions.
Escalate complex issues to human support.

# Channel Instructions (primary agent in #support)
This is the #support channel. Prioritize urgent issues.
Response time goal: <5 minutes.
Use the ticket system for tracking.

# Participant Instructions (role in this channel)
You are the "Tier 1 Support" agent in this channel.
Handle basic questions and password resets.
Escalate billing issues to @billing-agent.
Escalate technical issues to @tech-agent.
```

**Final Prompt**: Merge all instructions with most specific taking precedence.

---

## Technical Design

### Configuration Model

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentConfig:
    """Complete agent configuration"""

    # Identity
    agent_id: str
    workspace_id: str
    channel_id: str

    # Instructions (merged)
    system_prompt: str
    personality: Optional[str] = None
    job_description: Optional[str] = None
    channel_instructions: Optional[str] = None
    role_instructions: Optional[str] = None

    # Merged final prompt
    final_prompt: str = ""

    # Metadata
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000

    def merge_instructions(self) -> str:
        """Merge all instructions into final prompt"""

        parts = [self.system_prompt]

        if self.personality:
            parts.append(f"\n## Personality\n{self.personality}")

        if self.job_description:
            parts.append(f"\n## Job Description\n{self.job_description}")

        if self.channel_instructions:
            parts.append(f"\n## Channel Guidelines\n{self.channel_instructions}")

        if self.role_instructions:
            parts.append(f"\n## Your Role\n{self.role_instructions}")

        return "\n".join(parts)
```

### Configuration Loader

```python
async def load_agent_config(
    agent_id: str,
    workspace_id: str,
    channel_id: str
) -> AgentConfig:
    """Load hierarchical agent configuration"""

    # 1. Load profile (base personality)
    profile = await db.profiles.get(agent_id)

    # 2. Load membership (workspace job description)
    membership = await db.memberships.find_one({
        "profile_id": agent_id,
        "workspace_id": workspace_id
    })

    # 3. Load channel settings (primary agent instructions)
    channel = await db.channels.get(channel_id)

    # 4. Load participant (channel-specific role)
    participant = await db.participants.find_one({
        "profile_id": agent_id,
        "channel_id": channel_id
    })

    # Build config
    config = AgentConfig(
        agent_id=agent_id,
        workspace_id=workspace_id,
        channel_id=channel_id,
        system_prompt=profile.system_prompt or DEFAULT_SYSTEM_PROMPT,
        personality=profile.instructions,
        job_description=membership.instructions if membership else None,
        channel_instructions=(
            channel.primary_agent_instructions
            if channel.primary_agent_id == agent_id
            else None
        ),
        role_instructions=participant.instructions if participant else None,
        model=profile.model or "gpt-4o",
        temperature=profile.temperature or 0.7,
        max_tokens=profile.max_tokens or 2000
    )

    # Merge instructions
    config.final_prompt = config.merge_instructions()

    return config
```

### Database Schema Extensions

```sql
-- Add instructions to profiles
ALTER TABLE profiles ADD COLUMN instructions TEXT;
ALTER TABLE profiles ADD COLUMN system_prompt TEXT;
ALTER TABLE profiles ADD COLUMN model VARCHAR(50) DEFAULT 'gpt-4o';
ALTER TABLE profiles ADD COLUMN temperature FLOAT DEFAULT 0.7;
ALTER TABLE profiles ADD COLUMN max_tokens INTEGER DEFAULT 2000;

-- Add instructions to memberships
ALTER TABLE memberships ADD COLUMN instructions TEXT;

-- Add instructions to channels
ALTER TABLE channels ADD COLUMN primary_agent_id UUID REFERENCES profiles(id);
ALTER TABLE channels ADD COLUMN primary_agent_instructions TEXT;

-- Add instructions to participants
ALTER TABLE participants ADD COLUMN instructions TEXT;
```

---

## Implementation

### Phase 1: Basic Loading (Day 1)

**Tasks**:
1. Create `AgentConfig` model
2. Implement `load_agent_config()`
3. Add database schema extensions
4. Write tests for loading

**Deliverable**: Can load configuration from all sources

### Phase 2: Instruction Merging (Day 2)

**Tasks**:
1. Implement `merge_instructions()`
2. Test merging logic
3. Add override rules (most specific wins)
4. Test with real examples

**Deliverable**: Instructions merge correctly

### Phase 3: Configuration Management (Day 3)

**Tasks**:
1. Add configuration caching
2. Add configuration validation
3. Add configuration UI helpers
4. Document configuration system

**Deliverable**: Production-ready configuration system

---

## Dependencies

### Existing Features
- ✅ Profiles table
- ✅ Memberships table
- ✅ Channels table
- ✅ Participants table

### Required Features
- ⚠️ Schema extensions (instructions columns)
- ⚠️ Configuration loader
- ⚠️ Instruction merging logic

### Nice-to-Have
- 🔮 Configuration UI (manage instructions)
- 🔮 Configuration templates (reusable configs)
- 🔮 Configuration versioning (track changes)
- 🔮 Configuration testing (preview before applying)

---

## Open Questions

1. **Merge Strategy**: How to handle conflicts?
   - Most specific wins (current approach)
   - Concatenate all (may be verbose)
   - Allow explicit overrides
   - Configurable per instruction?

2. **Instruction Format**: Plain text or structured?
   - Plain text (simple, flexible)
   - Markdown (formatted, readable)
   - YAML/JSON (structured, parseable)
   - Mixed (different formats for different sources)?

3. **Caching**: How long to cache configurations?
   - Per request (no caching, always fresh)
   - Per session (cache for duration of conversation)
   - Time-based (cache for N minutes)
   - Invalidate on change?

4. **Validation**: How to validate instructions?
   - No validation (flexible, risky)
   - Length limits (prevent abuse)
   - Content filtering (prevent harmful instructions)
   - LLM-based validation (check for conflicts)?

5. **Defaults**: What if no instructions provided?
   - Use system prompt only (minimal)
   - Use sensible defaults (helpful)
   - Require instructions (strict)
   - Configurable?

---

## Success Metrics

- ✅ Configuration loads correctly 100% of time
- ✅ Instructions merge in correct order
- ✅ Most specific instructions take precedence
- ⚡ Configuration loading <100ms (with caching)
- 🎯 Agents behave according to configuration (user feedback)

---

## Related Ideas

- [Message Routing & Triage](./message-routing-triage.md) - Uses primary agent config
- [Agent Response Workflows](./agent-response-workflows.md) - Uses full config
- [Multi-Agent Group Chat](./multi-agent-group-chat.md) - Overall vision

---

## Examples

### Example 1: Support Agent in Different Channels

```python
# In #general channel
config_general = await load_agent_config(
    agent_id="support-agent",
    workspace_id="acme-corp",
    channel_id="general"
)
# Personality: Friendly, helpful
# Role: General questions only

# In #support channel
config_support = await load_agent_config(
    agent_id="support-agent",
    workspace_id="acme-corp",
    channel_id="support"
)
# Personality: Friendly, helpful
# Role: Tier 1 support, handle tickets
# Channel: Prioritize urgent issues

# Same agent, different behavior!
```

### Example 2: Merged Instructions

```python
config = await load_agent_config(
    agent_id="agent-123",
    workspace_id="workspace-456",
    channel_id="channel-789"
)

print(config.final_prompt)
# Output:
# You are a helpful AI assistant.
#
# ## Personality
# You are friendly, concise, and love using emojis! 🎉
#
# ## Job Description
# You are the customer support agent for Acme Corp.
# Help users with billing, technical issues, and general questions.
#
# ## Channel Guidelines
# This is the #support channel. Prioritize urgent issues.
#
# ## Your Role
# You are the "Tier 1 Support" agent in this channel.
# Handle basic questions. Escalate complex issues.
```

### Example 3: Minimal Configuration

```python
# Agent with only profile instructions
config = await load_agent_config(
    agent_id="simple-agent",
    workspace_id="workspace-123",
    channel_id="channel-456"
)

print(config.final_prompt)
# Output:
# You are a helpful AI assistant.
#
# ## Personality
# You are a friendly chatbot.
```

---

**Last Updated**: 2025-11-13
**Status**: Ready to implement - enables context-aware agents
