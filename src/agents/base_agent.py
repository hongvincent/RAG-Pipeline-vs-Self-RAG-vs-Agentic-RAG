"""
Base agent class and context management
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from openai import OpenAI
from src.config import get_openai_api_key

@dataclass
class AgentContext:
    """Shared context across all agents"""

    # Input
    query: str
    history: List[Dict[str, str]] = field(default_factory=list)

    # Router output
    route_info: Dict[str, Any] = field(default_factory=dict)

    # Planning output
    plan: List[Dict[str, Any]] = field(default_factory=list)

    # Retrieval output
    retrieved_docs: List[Dict[str, Any]] = field(default_factory=list)

    # Grading output
    graded_docs: List[Dict[str, Any]] = field(default_factory=list)

    # Generation output
    generated_answer: Optional[str] = None

    # Validation output
    validation_results: Dict[str, Any] = field(default_factory=dict)

    # Execution trace
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_trace(self, agent_name: str, action: str, result: Any):
        """Add execution trace entry"""
        self.execution_trace.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "result": result
        })

    def get_trace_summary(self) -> str:
        """Get human-readable trace summary"""
        lines = ["\nExecution Trace:"]
        for entry in self.execution_trace:
            lines.append(
                f"  [{entry['timestamp']}] {entry['agent']}: {entry['action']}"
            )
        return "\n".join(lines)

class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, name: str, model: str = "gpt-4-turbo-preview"):
        self.name = name
        self.model = model
        self.client = OpenAI(api_key=get_openai_api_key())

    @abstractmethod
    def execute(self, context: AgentContext) -> Dict[str, Any]:
        """
        Execute agent's main task

        Args:
            context: Shared agent context

        Returns:
            Agent's output
        """
        pass

    def log_action(self, context: AgentContext, action: str, result: Any):
        """Log action to context trace"""
        context.add_trace(self.name, action, result)

    def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Call LLM with error handling

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            response_format: Response format (e.g., {"type": "json_object"})

        Returns:
            LLM response content
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        if response_format:
            kwargs["response_format"] = response_format

        response = self.client.chat.completions.create(**kwargs)

        return response.choices[0].message.content
