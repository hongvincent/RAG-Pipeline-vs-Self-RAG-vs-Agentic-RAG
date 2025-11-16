"""
Validation Agent - Validates answer quality before returning to user
"""
import json
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent, AgentContext

class ValidationAgent(BaseAgent):
    """Validates generated answers"""

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(name="ValidationAgent", model=model)

    def execute(
        self,
        context: AgentContext,
        answer: str = None
    ) -> Dict[str, Any]:
        """
        Validate answer quality

        Args:
            context: Agent context
            answer: Answer to validate (uses context.generated_answer if None)

        Returns:
            Validation results
        """
        answer = answer or context.generated_answer

        if not answer:
            return {
                "is_valid": False,
                "issues": ["No answer generated"],
                "recommendation": "regenerate"
            }

        # Build source summary
        sources = context.graded_docs or []
        source_summary = "\n".join([
            f"Source {i}: {doc['content'][:200]}..."
            for i, doc in enumerate(sources, 1)
        ])

        prompt = f"""Validate this answer across multiple dimensions.

Query: "{context.query}"

Sources Used:
{source_summary if source_summary else "No sources (conversational response)"}

Generated Answer:
{answer}

Evaluate:
1. GROUNDED: Is answer supported by sources? Any hallucinations?
2. COMPLETE: Does it fully answer the question?
3. USEFUL: Is it helpful to the user?
4. ACCURATE: Are specific details (prices, dates, etc.) correct?
5. CLARITY: Is it clear and well-organized?

Respond in JSON:
{{
    "grounded": {{
        "score": 0.0-1.0,
        "is_acceptable": true/false,
        "issues": ["list any unsupported claims"]
    }},
    "complete": {{
        "score": 0.0-1.0,
        "is_acceptable": true/false,
        "missing": ["list missing information"]
    }},
    "useful": {{
        "score": 0.0-1.0,
        "is_acceptable": true/false,
        "issues": ["list any usefulness issues"]
    }},
    "accurate": {{
        "score": 0.0-1.0,
        "is_acceptable": true/false,
        "errors": ["list any inaccuracies"]
    }},
    "clarity": {{
        "score": 0.0-1.0,
        "is_acceptable": true/false,
        "issues": ["list clarity issues"]
    }},
    "overall_quality": "excellent/good/acceptable/poor",
    "is_valid": true/false,
    "recommendation": "accept/regenerate/retrieve_more/clarify_query",
    "reasoning": "overall assessment"
}}"""

        response = self.call_llm(
            prompt=prompt,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        validation = json.loads(response)

        # Log action
        self.log_action(
            context,
            "validate_answer",
            {
                "overall_quality": validation.get('overall_quality'),
                "is_valid": validation.get('is_valid'),
                "recommendation": validation.get('recommendation')
            }
        )

        # Update context
        context.validation_results = validation

        return validation

def main():
    """Test validation agent"""
    agent = ValidationAgent()

    # Mock context
    context = AgentContext(query="What is your return policy?")
    context.graded_docs = [
        {
            'id': 'POL001',
            'content': 'Return Policy: Items can be returned within 30 days of delivery in original condition with tags attached.',
            'metadata': {'type': 'policy'}
        }
    ]
    context.generated_answer = """Based on our return policy [Source 1], you can return items within 30 days of delivery.
Items must be in original condition with all tags attached."""

    validation = agent.execute(context)

    print(f"Query: {context.query}\n")
    print(f"Validation Results:")
    print(f"  Overall Quality: {validation['overall_quality']}")
    print(f"  Is Valid: {validation['is_valid']}")
    print(f"  Recommendation: {validation['recommendation']}")
    print(f"  Reasoning: {validation['reasoning']}")

    print(f"\nDetailed Scores:")
    for dimension in ['grounded', 'complete', 'useful', 'accurate', 'clarity']:
        if dimension in validation:
            print(f"  {dimension.capitalize()}: {validation[dimension]['score']:.2f} - {validation[dimension]['is_acceptable']}")

if __name__ == "__main__":
    main()
