# Human-in-the-Loop - Pause & Resume with Checkpointing

**Status**: 🌱 Future Feature
**Priority**: Medium
**Complexity**: Medium
**Estimated Effort**: 1 week

---

## What

Enable agents to pause execution, ask humans for input, and resume where they left off using LangGraph's checkpointing system. This creates a collaborative workflow where agents and humans work together.

### Key Features

- **Agent Questions**: Agents can ask clarifying questions
- **Approval Workflows**: Agents request approval before actions
- **Human Feedback**: Humans can correct or guide agents
- **Pause & Resume**: Checkpoint state, wait for input, resume
- **Timeout Handling**: Auto-resume or cancel after timeout
- **Multi-Turn Interaction**: Multiple back-and-forth exchanges

---

## Why

### Business Value
- **Accuracy**: Humans verify critical decisions
- **Trust**: Users feel in control
- **Learning**: Agents improve from human feedback
- **Compliance**: Required for sensitive operations

### Technical Value
- **LangGraph Native**: Built-in checkpoint support
- **Flexible**: Works with any agent type
- **Reliable**: State persists across restarts
- **Scalable**: Handles many concurrent pauses

---

## Architecture

### Flow

```
Agent starts execution
    ↓
Agent needs human input
    ↓
[Pause & Checkpoint]
    ├─ Save state to Supabase
    ├─ Create "question" message
    └─ Wait for response
    ↓
Human responds
    ↓
[Resume from Checkpoint]
    ├─ Load state from Supabase
    ├─ Inject human response
    └─ Continue execution
    ↓
Agent completes task
```

### Message Types

```python
class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT_QUESTION = "agent_question"  # New: Agent asking human
    HUMAN_RESPONSE = "human_response"  # New: Human answering agent
```

---

## Technical Design

### Agent Interruption

```python
from langchain.schema import HumanMessage, AIMessage
from langgraph.checkpoint import Checkpoint

class InterruptableAgent(ReActAgent):
    """Agent that can pause for human input"""

    async def run(self, messages: List[Message], checkpoint: Optional[Checkpoint] = None):
        # Check if resuming from checkpoint
        if checkpoint and checkpoint.metadata.get("waiting_for_human"):
            # Find human response
            human_response = self._find_human_response(messages, checkpoint)
            if not human_response:
                # Still waiting
                return AgentResponse(
                    status="waiting",
                    checkpoint=checkpoint
                )

            # Resume with human response
            return await self._resume_with_response(human_response, checkpoint)

        # Normal execution
        return await super().run(messages, checkpoint)

    async def ask_human(self, question: str, context: Dict) -> str:
        """Pause execution and ask human a question"""

        # Create checkpoint
        checkpoint = await self.save_checkpoint(
            metadata={
                "waiting_for_human": True,
                "question": question,
                "context": context,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Create question message
        await create_message(
            workspace_id=self.workspace_id,
            channel_id=self.channel_id,
            author_id=self.agent_id,
            reply_to_id=self.current_message_id,
            content=question,
            role="agent_question",
            metadata={
                "checkpoint_id": checkpoint.id,
                "requires_response": True
            }
        )

        # Raise interrupt to pause execution
        raise AgentInterrupt(
            checkpoint=checkpoint,
            question=question
        )
```

### Resume Workflow

```python
@workflow
class ResumeAgentWorkflow(BaseWorkflow):
    """Resume agent after human response"""

    async def run(self, message: Message):
        # Check if this is a response to an agent question
        if message.reply_to_id:
            parent = await db.messages.get(message.reply_to_id)

            if parent.role == "agent_question":
                # Get checkpoint ID
                checkpoint_id = parent.metadata.get("checkpoint_id")

                # Load checkpoint
                checkpoint = await load_checkpoint(checkpoint_id)

                # Resume agent with human response
                agent = await load_agent(parent.author_id)

                # Add human response to messages
                messages = await load_thread_messages(message.thread_id)

                # Continue execution
                response = await agent.run(
                    messages=messages,
                    checkpoint=checkpoint
                )

                # Post response
                await create_message(
                    workspace_id=message.workspace_id,
                    channel_id=message.channel_id,
                    author_id=parent.author_id,
                    reply_to_id=message.id,
                    content=response.content,
                    role="assistant"
                )
```

### Approval Tool

```python
from langchain.tools import BaseTool

class RequestApprovalTool(BaseTool):
    """Tool for agents to request human approval"""

    name = "request_approval"
    description = "Request human approval before taking an action"

    async def _arun(
        self,
        action: str,
        reason: str,
        details: Dict
    ) -> str:
        """Request approval"""

        # Format approval request
        question = f"""
        I'd like to {action}.

        Reason: {reason}

        Details:
        {json.dumps(details, indent=2)}

        Do you approve? (yes/no)
        """

        # Pause and ask
        response = await self.agent.ask_human(question, {
            "action": action,
            "reason": reason,
            "details": details
        })

        # Parse response
        if response.lower().strip() in ["yes", "y", "approve", "approved"]:
            return "approved"
        else:
            return "denied"

# Use in agent
class ApprovalRequiredAgent(InterruptableAgent):
    """Agent that requires approval for sensitive actions"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)

        # Add approval tool
        self.tools.append(RequestApprovalTool(agent=self))

    async def execute_action(self, action: str, params: Dict):
        """Execute action with approval"""

        # Request approval
        approval = await self.tools["request_approval"](
            action=action,
            reason=f"Executing {action}",
            details=params
        )

        if approval == "approved":
            # Execute action
            return await self._do_action(action, params)
        else:
            return "Action denied by user"
```

### Timeout Handling

```python
@worker.task("check_agent_timeouts")
async def check_agent_timeouts():
    """Check for agents waiting too long for human response"""

    # Find messages waiting for response
    waiting_messages = await db.messages.find({
        "role": "agent_question",
        "metadata.requires_response": True,
        "created_at": {"$lt": datetime.utcnow() - timedelta(hours=24)}
    })

    for message in waiting_messages:
        checkpoint_id = message.metadata.get("checkpoint_id")

        # Load checkpoint
        checkpoint = await load_checkpoint(checkpoint_id)

        # Check timeout policy
        timeout_action = checkpoint.metadata.get("timeout_action", "cancel")

        if timeout_action == "cancel":
            # Cancel agent execution
            await create_message(
                workspace_id=message.workspace_id,
                channel_id=message.channel_id,
                author_id=message.author_id,
                reply_to_id=message.id,
                content="Request timed out. Cancelling operation.",
                role="system"
            )

            # Mark checkpoint as cancelled
            await update_checkpoint(checkpoint_id, status="cancelled")

        elif timeout_action == "auto_approve":
            # Auto-approve and resume
            await create_message(
                workspace_id=message.workspace_id,
                channel_id=message.channel_id,
                author_id="system",
                reply_to_id=message.id,
                content="yes",
                role="human_response",
                metadata={"auto_approved": True}
            )

            # Resume agent
            await enqueue_resume_agent(message.id)

        elif timeout_action == "escalate":
            # Notify admins
            await notify_admins(
                workspace_id=message.workspace_id,
                message=f"Agent question timed out: {message.content}"
            )
```

### Multi-Turn Interaction

```python
class ConversationalAgent(InterruptableAgent):
    """Agent that can have multi-turn conversations with humans"""

    async def clarify_requirements(self, task: str) -> Dict:
        """Ask multiple questions to clarify requirements"""

        questions = [
            "What is the primary goal of this task?",
            "Are there any constraints I should be aware of?",
            "What format would you like the output in?"
        ]

        answers = {}
        for question in questions:
            answer = await self.ask_human(question, {
                "task": task,
                "previous_answers": answers
            })
            answers[question] = answer

        return answers

    async def iterative_refinement(self, draft: str) -> str:
        """Refine output based on human feedback"""

        while True:
            # Show draft
            feedback = await self.ask_human(
                f"Here's my draft:\n\n{draft}\n\nWhat would you like me to change? (or say 'looks good')",
                {"draft": draft}
            )

            if "looks good" in feedback.lower():
                return draft

            # Refine based on feedback
            draft = await self.refine_draft(draft, feedback)
```

---

## Dependencies

### Existing Features
- ✅ LangGraph checkpointing
- ✅ Supabase checkpoint storage
- ✅ Message threading (reply_to_id)
- ✅ Agent execution system

### Required Features
- ⚠️ Agent interrupt handling
- ⚠️ Resume workflow
- ⚠️ Timeout checking (cron job)
- ⚠️ New message roles (agent_question, human_response)

### Nice-to-Have
- 🔮 Approval UI (buttons for yes/no)
- 🔮 Timeout configuration per agent
- 🔮 Escalation workflows
- 🔮 Approval history/audit log

---

## Implementation Phases

### Phase 1: Basic Pause/Resume (Week 1)
- [ ] Add agent interrupt mechanism
- [ ] Implement checkpoint-based pausing
- [ ] Create resume workflow
- [ ] Add new message roles
- [ ] Test basic pause/resume

### Phase 2: Approval Tool (Week 1)
- [ ] Implement RequestApprovalTool
- [ ] Add approval parsing
- [ ] Test approval workflows
- [ ] Add approval examples

### Phase 3: Timeout Handling (Week 1)
- [ ] Implement timeout checker
- [ ] Add timeout policies (cancel, auto-approve, escalate)
- [ ] Test timeout scenarios
- [ ] Add timeout configuration

### Phase 4: Polish (Week 1)
- [ ] Add multi-turn interaction support
- [ ] Improve error handling
- [ ] Add observability
- [ ] Create documentation

---

## Open Questions

1. **Timeout Duration**: How long to wait for human response?
   - 1 hour? 24 hours? Configurable?
   - Different timeouts for different actions?

2. **Timeout Action**: What to do on timeout?
   - Cancel (safe, may frustrate users)
   - Auto-approve (risky, convenient)
   - Escalate (balanced, requires admin)
   - Configurable per agent/action?

3. **Notification**: How to notify humans of questions?
   - In-app only?
   - Email?
   - Push notifications?
   - Configurable?

4. **Approval UI**: How to make approvals easy?
   - Text response ("yes"/"no")
   - Buttons in UI
   - Slash commands (/approve, /deny)
   - All of the above?

5. **Concurrent Pauses**: Can agent pause multiple times?
   - Yes (complex, flexible)
   - No (simple, limited)
   - Max N pauses per execution?

6. **Checkpoint Cleanup**: When to delete old checkpoints?
   - After completion
   - After timeout
   - After N days
   - Never (for audit)

---

## Success Metrics

- ✅ Agents can pause and resume reliably
- ✅ Checkpoints persist across restarts
- ✅ Timeouts handled correctly
- ⚡ Resume latency <2 seconds
- ⚡ No checkpoint corruption

---

## Related Ideas

- [Multi-Agent Group Chat](./multi-agent-group-chat.md) - Uses pause/resume for questions
- [Supabase Realtime Streaming](./supabase-realtime-streaming.md) - Stream questions to users

---

## Examples

### Example 1: Approval for Deletion

```python
agent: "I found 150 old files to delete. Should I proceed?"
user: "yes"
agent: "Deleted 150 files. Done!"
```

### Example 2: Clarification

```python
agent: "I need to send an email. Who should I send it to?"
user: "Send it to the engineering team"
agent: "Should I include attachments?"
user: "Yes, include the report"
agent: "Email sent to engineering team with report attached!"
```

### Example 3: Iterative Refinement

```python
agent: "Here's a draft email: [draft]. What do you think?"
user: "Make it more formal"
agent: "Here's the revised version: [draft2]. Better?"
user: "Perfect!"
agent: "Email sent!"
```

---

**Last Updated**: 2025-11-13
**Status**: Planning - exciting for collaborative workflows
