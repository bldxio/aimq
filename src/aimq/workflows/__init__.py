"""Built-in workflows and workflow utilities for AIMQ."""

from aimq.workflows.base import BaseWorkflow
from aimq.workflows.decorators import workflow
from aimq.workflows.document import DocumentWorkflow
from aimq.workflows.multi_agent import MultiAgentWorkflow
from aimq.workflows.states import WorkflowState

__all__ = ["workflow", "WorkflowState", "BaseWorkflow", "DocumentWorkflow", "MultiAgentWorkflow"]
