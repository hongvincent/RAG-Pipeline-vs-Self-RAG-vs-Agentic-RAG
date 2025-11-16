"""
Agentic RAG Implementation with Multi-Agent Decision Making

Flow:
1. Router Agent → Classify query
2. Planning Agent → Create execution plan
3. Execute plan with specialized agents:
   - Retrieval Agent
   - Grading Agent
   - Generation Agent
4. Validation Agent → Verify quality
5. Adaptive actions based on validation
"""
from typing import Dict, Any, List, Optional
from src.agents.base_agent import AgentContext
from src.agents.router_agent import RouterAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.grading_agent import GradingAgent
from src.agents.generation_agent import GenerationAgent
from src.agents.validation_agent import ValidationAgent
from src.vector_store import VectorStore
from src.reranker import DocumentReranker

class AgenticRAG:
    """Agentic RAG with intelligent multi-agent orchestration"""

    def __init__(
        self,
        vector_store: VectorStore,
        reranker: DocumentReranker = None,
        max_iterations: int = 3
    ):
        """
        Initialize Agentic RAG

        Args:
            vector_store: Vector store for retrieval
            reranker: Document reranker
            max_iterations: Maximum refinement iterations
        """
        self.vector_store = vector_store
        self.reranker = reranker or DocumentReranker()
        self.max_iterations = max_iterations

        # Initialize agents
        self.router = RouterAgent()
        self.planner = PlanningAgent()
        self.retrieval = RetrievalAgent(vector_store, reranker)
        self.grading = GradingAgent()
        self.generation = GenerationAgent()
        self.validation = ValidationAgent()

    def handle_conversational(
        self,
        context: AgentContext,
        verbose: bool = False
    ) -> str:
        """
        Handle conversational queries without retrieval

        Args:
            context: Agent context
            verbose: Print steps

        Returns:
            Response
        """
        if verbose:
            print("  → Conversational mode (no retrieval needed)")

        response = """Hello! I'm your customer support assistant. I can help you with:
- Product information
- Return and refund policies
- Shipping information
- Order tracking
- Account questions
- Technical support

How can I assist you today?"""

        context.generated_answer = response
        return response

    def execute_plan(
        self,
        context: AgentContext,
        verbose: bool = False
    ) -> str:
        """
        Execute the planned steps

        Args:
            context: Agent context
            verbose: Print steps

        Returns:
            Generated answer
        """
        plan = context.plan

        if verbose:
            print(f"\nExecuting {len(plan)} step plan:")

        for i, step in enumerate(plan, 1):
            action = step.get('action')

            if verbose:
                print(f"\n  Step {i}: {action}")

            if action == 'retrieve':
                docs = self.retrieval.execute(context, step)
                if verbose:
                    print(f"    Retrieved {len(docs)} documents")

            elif action == 'grade':
                docs = self.grading.execute(context)
                if verbose:
                    print(f"    Graded: {len(docs)} relevant documents")

            elif action in ['generate', 'compare', 'synthesize']:
                answer = self.generation.execute(context, plan_step=step)
                if verbose:
                    print(f"    Generated answer ({len(answer)} chars)")

            else:
                if verbose:
                    print(f"    Skipping unknown action: {action}")

        return context.generated_answer

    def query(
        self,
        query: str,
        conversation_history: List[Dict[str, str]] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Execute Agentic RAG pipeline

        Args:
            query: User query
            conversation_history: Previous conversation
            verbose: Print detailed execution steps

        Returns:
            Complete response with answer and metadata
        """
        # Initialize context
        context = AgentContext(
            query=query,
            history=conversation_history or []
        )

        if verbose:
            print(f"\n{'='*70}")
            print("AGENTIC RAG PIPELINE")
            print(f"{'='*70}\n")
            print(f"Query: {query}\n")

        # Step 1: Route query
        if verbose:
            print("Agent: Router")
            print("Action: Classifying query and determining strategy...")

        route_info = self.router.execute(context)

        if verbose:
            print(f"  Category: {route_info['category']}")
            print(f"  Complexity: {route_info['complexity']}")
            print(f"  Requires Retrieval: {route_info['requires_retrieval']}")
            print(f"  Strategy: {route_info['suggested_strategy']}")

        # Step 2: Handle conversational queries
        if not route_info['requires_retrieval']:
            answer = self.handle_conversational(context, verbose)

            if verbose:
                print(f"\n{'='*70}")
                print("FINAL ANSWER:")
                print(f"{'='*70}")
                print(answer)
                print(f"{'='*70}\n")

            return {
                'answer': answer,
                'route_info': route_info,
                'requires_retrieval': False,
                'trace': context.execution_trace
            }

        # Step 3: Plan execution
        if verbose:
            print(f"\nAgent: Planner")
            print("Action: Creating execution plan...")

        plan = self.planner.execute(context)

        if verbose:
            print(f"  Plan type: {context.metadata.get('plan_type', 'standard')}")
            print(f"  Steps: {len(plan)}")

        # Iterative refinement loop
        best_answer = None
        best_validation = None
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            if verbose:
                print(f"\n{'─'*70}")
                print(f"ITERATION {iteration}")
                print(f"{'─'*70}")

            # Step 4: Execute plan
            if verbose:
                print("\nPhase: Execution")

            answer = self.execute_plan(context, verbose)

            if not answer:
                if verbose:
                    print("  ⚠ No answer generated")
                break

            # Step 5: Validate answer
            if verbose:
                print(f"\nAgent: Validator")
                print("Action: Validating answer quality...")

            validation = self.validation.execute(context, answer)

            if verbose:
                print(f"  Quality: {validation['overall_quality']}")
                print(f"  Valid: {validation['is_valid']}")
                print(f"  Recommendation: {validation['recommendation']}")

            # Track best answer
            if best_validation is None or validation['is_valid']:
                best_answer = answer
                best_validation = validation

            # Decide next action
            recommendation = validation['recommendation']

            if recommendation == 'accept' or validation['is_valid']:
                if verbose:
                    print(f"\n  ✓ Answer accepted (iteration {iteration})")
                break

            elif recommendation == 'retrieve_more':
                if verbose:
                    print(f"\n  → Retrieving additional context...")

                # Retrieve more with expanded query
                additional_docs = self.retrieval.execute(
                    context,
                    plan_step={'action': 'retrieve', 'target': query}
                )

                # Merge with existing docs (deduplicated in retrieval agent)
                if verbose:
                    print(f"    Added {len(additional_docs)} more documents")

            elif recommendation == 'regenerate':
                if verbose:
                    print(f"\n  ↻ Regenerating answer...")
                # Will regenerate in next iteration
                continue

            else:
                # Other recommendations or reached max iterations
                if verbose:
                    print(f"\n  → Using best available answer")
                break

        # Use best answer
        final_answer = best_answer or context.generated_answer
        final_validation = best_validation or context.validation_results

        if verbose:
            print(f"\n{'='*70}")
            print("FINAL ANSWER:")
            print(f"{'='*70}")
            print(final_answer)
            print(f"\nQuality: {final_validation.get('overall_quality', 'N/A')}")
            print(f"Iterations: {iteration}")
            print(f"Sources: {len(context.graded_docs)}")
            print(f"{'='*70}\n")

        return {
            'answer': final_answer,
            'validation': final_validation,
            'route_info': route_info,
            'plan': plan,
            'sources': context.graded_docs,
            'iterations': iteration,
            'trace': context.execution_trace
        }

    def print_trace(self, result: Dict[str, Any]):
        """
        Print execution trace

        Args:
            result: Query result with trace
        """
        print(f"\n{'='*70}")
        print("EXECUTION TRACE")
        print(f"{'='*70}")

        for entry in result.get('trace', []):
            print(f"[{entry['timestamp']}]")
            print(f"  Agent: {entry['agent']}")
            print(f"  Action: {entry['action']}")
            print(f"  Result: {entry['result']}")
            print()

def main():
    """Test Agentic RAG"""
    from src.vector_store import VectorStore

    print("Initializing Agentic RAG...")
    vector_store = VectorStore()

    if vector_store.count() == 0:
        print("Vector store is empty. Please run vector_store.py first.")
        return

    agentic_rag = AgenticRAG(vector_store)

    # Test queries with different complexities
    test_queries = [
        "Hello!",  # Conversational
        "What is your return policy?",  # Simple
        "Can I return electronics after 30 days if they're defective?",  # Medium
        "Compare the return policies for electronics and clothing items",  # Complex
    ]

    for query in test_queries:
        result = agentic_rag.query(query, verbose=True)

        print("\n" + "="*70)
        print("RESULT SUMMARY")
        print("="*70)
        print(f"Category: {result['route_info']['category']}")
        print(f"Iterations: {result.get('iterations', 0)}")
        if 'validation' in result:
            print(f"Quality: {result['validation']['overall_quality']}")

        input("\nPress Enter for next query...")

if __name__ == "__main__":
    main()
