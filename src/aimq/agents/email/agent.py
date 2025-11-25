from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from ..base import BaseAgent


class EmailState(TypedDict):
    email_subject: str
    email_body: str
    assistant_name: str
    system_prompt: str
    response: str


class EmailAgent(BaseAgent):
    def __init__(
        self,
        system_prompt: str,
        assistant_name: str = "Assistant",
        model: str = "gpt-4",
        temperature: float = 0.7,
    ):
        self.assistant_name = assistant_name
        self.model = model
        super().__init__(
            tools=[],
            system_prompt=system_prompt,
            llm=model,
            temperature=temperature,
            memory=False,
        )

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(EmailState)

        workflow.add_node("generate_response", self._generate_response)

        workflow.set_entry_point("generate_response")
        workflow.add_edge("generate_response", END)

        return workflow

    def _generate_response(self, state: EmailState) -> EmailState:
        llm = ChatOpenAI(model=self.model, temperature=self.temperature)

        system_message = SystemMessage(content=state["system_prompt"])
        human_message = HumanMessage(
            content=f"""You received an email with the following details:

Subject: {state['email_subject']}

Body:
{state['email_body']}

Please generate a professional and helpful response to this email."""
        )

        response = llm.invoke([system_message, human_message])

        return {
            **state,
            "response": response.content,
        }

    def generate_response(self, email_subject: str, email_body: str, system_prompt: str) -> str:
        result = self.invoke(
            {
                "email_subject": email_subject,
                "email_body": email_body,
                "assistant_name": self.assistant_name,
                "system_prompt": system_prompt,
                "response": "",
            }
        )
        return result["response"]
