"""Built-in LangGraph workflows for AIMQ."""

from aimq.workflows.base import BaseWorkflow
from aimq.workflows.document import DocumentWorkflow
from aimq.workflows.multi_agent import MultiAgentWorkflow

__all__ = ["BaseWorkflow", "DocumentWorkflow", "MultiAgentWorkflow"]
