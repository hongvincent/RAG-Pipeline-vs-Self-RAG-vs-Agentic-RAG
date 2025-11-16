"""
Generation Agent - Generates high-quality responses
"""
import json
from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseAgent, AgentContext

class GenerationAgent(BaseAgent):
    """Generates responses from context"""

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(name="GenerationAgent", model=model)

    def build_context(
        self,
        documents: List[Dict[str, Any]],
        plan_step: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build context string from documents

        Args:
            documents: Context documents
            plan_step: Current plan step (for specialized formatting)

        Returns:
            Formatted context string
        """
        if not documents:
            return ""

        parts = []

        for i, doc in enumerate(documents, 1):
            parts.append(f"[Source {i}]")
            parts.append(doc['content'])

            # Add grading insights if available
            if 'grading' in doc and 'key_points' in doc['grading']:
                key_points = doc['grading']['key_points']
                if key_points:
                    parts.append(f"Key points: {', '.join(key_points)}")

            parts.append("")  # Blank line

        return "\n".join(parts)

    def execute(
        self,
        context: AgentContext,
        documents: List[Dict[str, Any]] = None,
        plan_step: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate answer

        Args:
            context: Agent context
            documents: Context documents (uses context.graded_docs if None)
            plan_step: Current plan step

        Returns:
            Generated answer
        """
        docs = documents or context.graded_docs
        query = context.query

        # Determine generation mode
        action = plan_step.get('action') if plan_step else 'generate'

        # Build context
        context_str = self.build_context(docs, plan_step)

        # Create prompts based on action
        if action == 'compare':
            system_prompt = """You are a customer support assistant.
Your task is to compare information from multiple sources and provide a clear comparison.

Guidelines:
- Compare the sources systematically
- Highlight similarities and differences
- Use specific details from each source
- Cite sources using [Source N] notation
- Present comparison in clear, organized format"""

        elif action == 'synthesize':
            system_prompt = """You are a customer support assistant.
Your task is to synthesize information from multiple sources into a coherent answer.

Guidelines:
- Combine information logically
- Resolve any contradictions
- Provide comprehensive answer
- Cite sources using [Source N] notation
- Maintain accuracy to source material"""

        else:  # generate
            system_prompt = """You are a helpful customer support assistant.

Guidelines:
- Answer based only on provided context
- Be accurate and specific
- Cite sources using [Source N] notation
- Be concise but complete
- If context is insufficient, acknowledge limitations
- Maintain professional, friendly tone"""

        if context_str:
            user_prompt = f"""Context:
{context_str}

Question: {query}

Please provide a helpful answer based on the context above."""
        else:
            # No context - conversational response
            user_prompt = query

        # Generate response
        response = self.call_llm(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1
        )

        # Log action
        self.log_action(
            context,
            f"generate_{action}",
            {"num_sources": len(docs), "answer_length": len(response)}
        )

        # Update context
        context.generated_answer = response

        return response

def main():
    """Test generation agent"""
    agent = GenerationAgent()

    # Mock context
    context = AgentContext(query="What is your return policy?")
    context.graded_docs = [
        {
            'id': 'POL001',
            'content': 'Return Policy: Items can be returned within 30 days of delivery in original condition.',
            'metadata': {'type': 'policy'},
            'grading': {
                'key_points': ['30 day return window', 'original condition required']
            }
        }
    ]

    answer = agent.execute(context)

    print(f"Query: {context.query}\n")
    print(f"Answer:\n{answer}")

if __name__ == "__main__":
    main()
