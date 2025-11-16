"""
Planning Agent - Creates execution plans for complex queries
"""
import json
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent, AgentContext

class PlanningAgent(BaseAgent):
    """Creates step-by-step plans for query execution"""

    def __init__(self, model: str = "gpt-4-turbo-preview"):
        super().__init__(name="PlanningAgent", model=model)

    def execute(self, context: AgentContext) -> List[Dict[str, Any]]:
        """
        Create execution plan based on query and route info

        Args:
            context: Agent context

        Returns:
            Execution plan as list of steps
        """
        query = context.query
        route_info = context.route_info

        # Simple queries get simple plans
        if route_info.get('complexity') == 'simple':
            plan = [
                {"action": "retrieve", "target": query, "params": {"top_k": 5}},
                {"action": "grade", "target": "retrieved_docs"},
                {"action": "generate", "context": "graded_docs"}
            ]

            self.log_action(context, "create_simple_plan", plan)
            context.plan = plan
            return plan

        # Complex queries need detailed planning
        prompt = f"""Create a step-by-step execution plan for this query.

Query: "{query}"
Category: {route_info.get('category')}
Complexity: {route_info.get('complexity')}
Strategy: {route_info.get('suggested_strategy')}

Available actions:
- retrieve: Get documents from knowledge base (specify what to retrieve)
- grade: Evaluate document relevance
- generate: Create text response
- compare: Compare multiple pieces of information
- synthesize: Combine information from multiple sources
- validate: Check answer quality

Create a detailed plan as JSON array:
{{
    "plan": [
        {{
            "step": 1,
            "action": "...",
            "target": "...",
            "description": "...",
            "params": {{}}
        }},
        ...
    ],
    "plan_type": "single/multi_hop/comparison",
    "expected_iterations": number
}}"""

        response = self.call_llm(
            prompt=prompt,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        plan_data = json.loads(response)
        plan = plan_data.get('plan', [])

        self.log_action(context, "create_complex_plan", plan_data)
        context.plan = plan
        context.metadata['plan_type'] = plan_data.get('plan_type')

        return plan

def main():
    """Test planning agent"""
    from src.agents.router_agent import RouterAgent

    test_queries = [
        "What is your return policy?",
        "Compare return policies for electronics vs clothing",
        "I bought a laptop 25 days ago and it's defective. What are my options?"
    ]

    router = RouterAgent()
    planner = PlanningAgent()

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")

        context = AgentContext(query=query)

        # Route first
        route_info = router.execute(context)
        print(f"\nRoute: {route_info['category']} ({route_info['complexity']})")

        # Plan
        plan = planner.execute(context)
        print(f"\nPlan ({len(plan)} steps):")
        for i, step in enumerate(plan, 1):
            print(f"  {i}. {step.get('action')}: {step.get('description', step.get('target', ''))}")

if __name__ == "__main__":
    main()
