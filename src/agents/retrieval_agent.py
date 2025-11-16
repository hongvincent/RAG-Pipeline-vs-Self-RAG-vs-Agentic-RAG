"""
Retrieval Agent - Handles intelligent document retrieval
"""
import json
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent, AgentContext
from src.vector_store import VectorStore
from src.reranker import DocumentReranker

class RetrievalAgent(BaseAgent):
    """Intelligent retrieval with query formulation"""

    def __init__(
        self,
        vector_store: VectorStore,
        reranker: DocumentReranker = None,
        model: str = "gpt-3.5-turbo"
    ):
        super().__init__(name="RetrievalAgent", model=model)
        self.vector_store = vector_store
        self.reranker = reranker or DocumentReranker()

    def formulate_queries(
        self,
        original_query: str,
        plan_step: Dict[str, Any]
    ) -> List[str]:
        """
        Formulate search queries for retrieval

        Args:
            original_query: Original user query
            plan_step: Current plan step

        Returns:
            List of search queries
        """
        target = plan_step.get('target', original_query)

        # For simple cases, use target directly
        if plan_step.get('action') == 'retrieve' and not plan_step.get('multi_query'):
            return [target]

        # For complex cases, decompose into sub-queries
        prompt = f"""Generate 1-3 focused search queries to retrieve information.

Original query: "{original_query}"
Current step: {plan_step.get('description', plan_step.get('action'))}
Target: {target}

Generate specific search queries that will find relevant information in a knowledge base.
Each query should be a clear, focused search phrase.

Respond in JSON format:
{{
    "queries": ["query 1", "query 2", ...],
    "reasoning": "why these queries"
}}"""

        response = self.call_llm(
            prompt=prompt,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        result = json.loads(response)
        return result.get('queries', [target])

    def execute(
        self,
        context: AgentContext,
        plan_step: Dict[str, Any] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Execute retrieval

        Args:
            context: Agent context
            plan_step: Current plan step
            top_k: Number of documents to retrieve

        Returns:
            Retrieved documents
        """
        # Formulate queries
        if plan_step:
            queries = self.formulate_queries(context.query, plan_step)
        else:
            queries = [context.query]

        all_docs = []
        seen_ids = set()

        # Retrieve for each query
        for query in queries:
            docs = self.vector_store.search(query, top_k=top_k)

            # Deduplicate
            for doc in docs:
                if doc['id'] not in seen_ids:
                    all_docs.append(doc)
                    seen_ids.add(doc['id'])

        # Rerank if multiple documents
        if len(all_docs) > 3:
            all_docs = self.reranker.rerank(
                context.query,
                all_docs,
                top_k=min(10, len(all_docs))
            )

        # Log action
        self.log_action(
            context,
            "retrieve_documents",
            {
                "queries": queries,
                "num_retrieved": len(all_docs)
            }
        )

        # Update context
        context.retrieved_docs = all_docs

        return all_docs

def main():
    """Test retrieval agent"""
    from src.vector_store import VectorStore

    vector_store = VectorStore()

    if vector_store.count() == 0:
        print("Vector store is empty. Run vector_store.py first.")
        return

    agent = RetrievalAgent(vector_store)

    test_cases = [
        {
            "query": "What is your return policy?",
            "plan_step": {"action": "retrieve", "target": "return policy"}
        },
        {
            "query": "Compare electronics vs clothing returns",
            "plan_step": {
                "action": "retrieve",
                "target": "return policies",
                "description": "Get both electronics and clothing return policies",
                "multi_query": True
            }
        }
    ]

    for case in test_cases:
        print(f"\n{'='*50}")
        print(f"Query: {case['query']}")

        context = AgentContext(query=case['query'])
        docs = agent.execute(context, case['plan_step'])

        print(f"\nRetrieved {len(docs)} documents:")
        for i, doc in enumerate(docs[:3], 1):
            print(f"  {i}. {doc['metadata']['type']}: {doc['content'][:80]}...")
            print(f"     Score: {doc.get('score', 0):.3f}")

if __name__ == "__main__":
    main()
