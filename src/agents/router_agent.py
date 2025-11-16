"""
Router Agent - Classifies queries and determines processing strategy
"""
import json
from typing import Dict, Any
from src.agents.base_agent import BaseAgent, AgentContext

class RouterAgent(BaseAgent):
    """Routes queries to appropriate handlers"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        super().__init__(name="RouterAgent", model=model)

    def execute(self, context: AgentContext) -> Dict[str, Any]:
        """
        Classify query and determine processing strategy

        Args:
            context: Agent context with query

        Returns:
            Routing decision
        """
        query = context.query

        prompt = f"""Analyze this customer support query and classify it.

Query: "{query}"

Determine:
1. Category: product_info, policy, order_tracking, technical_support, shipping, general_conversation, out_of_scope
2. Complexity: simple (straightforward lookup), medium (requires some reasoning), complex (multi-step or comparison)
3. Whether retrieval from knowledge base is needed
4. Suggested strategy: direct (simple retrieval), multi_hop (multiple retrievals), comparison (compare sources), conversational (no retrieval needed)

Respond in JSON format:
{{
    "category": "...",
    "complexity": "simple/medium/complex",
    "requires_retrieval": true/false,
    "suggested_strategy": "...",
    "reasoning": "brief explanation",
    "confidence": 0.0-1.0
}}"""

        response = self.call_llm(
            prompt=prompt,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        route_info = json.loads(response)

        # Log action
        self.log_action(context, "route_query", route_info)

        # Update context
        context.route_info = route_info

        return route_info

def main():
    """Test router agent"""
    test_queries = [
        "Hello!",
        "What is your return policy?",
        "Compare electronics and clothing return policies",
        "Track my order #12345"
    ]

    router = RouterAgent()

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")

        context = AgentContext(query=query)
        result = router.execute(context)

        print(f"\nCategory: {result['category']}")
        print(f"Complexity: {result['complexity']}")
        print(f"Requires Retrieval: {result['requires_retrieval']}")
        print(f"Strategy: {result['suggested_strategy']}")
        print(f"Reasoning: {result['reasoning']}")

if __name__ == "__main__":
    main()
