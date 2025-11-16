"""
Grading Agent - Evaluates document relevance and quality
"""
import json
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent, AgentContext

class GradingAgent(BaseAgent):
    """Grades documents for relevance and quality"""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        super().__init__(name="GradingAgent", model=model)

    def grade_document(
        self,
        query: str,
        document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Grade a single document

        Args:
            query: User query
            document: Document to grade

        Returns:
            Grading result
        """
        prompt = f"""Grade this document's relevance to the query.

Query: "{query}"

Document:
{document['content'][:600]}

Evaluate:
1. Relevance: Does it help answer the query?
2. Completeness: Does it provide sufficient information?
3. Specificity: Is it specific or too generic?

Respond in JSON:
{{
    "is_relevant": true/false,
    "relevance_score": 0.0-1.0,
    "reasoning": "brief explanation",
    "key_points": ["point 1", "point 2", ...]
}}"""

        response = self.call_llm(
            prompt=prompt,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        grading = json.loads(response)
        return grading

    def execute(
        self,
        context: AgentContext,
        documents: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Grade documents for relevance

        Args:
            context: Agent context
            documents: Documents to grade (uses context.retrieved_docs if None)

        Returns:
            Filtered list of relevant documents
        """
        docs_to_grade = documents or context.retrieved_docs

        if not docs_to_grade:
            return []

        relevant_docs = []

        for doc in docs_to_grade:
            # Grade document
            grading = self.grade_document(context.query, doc)

            # Add grading to document
            doc['grading'] = grading

            # Keep if relevant
            if grading['is_relevant'] and grading['relevance_score'] > 0.5:
                relevant_docs.append(doc)

        # Log action
        self.log_action(
            context,
            "grade_documents",
            {
                "total_docs": len(docs_to_grade),
                "relevant_docs": len(relevant_docs)
            }
        )

        # Update context
        context.graded_docs = relevant_docs

        return relevant_docs

def main():
    """Test grading agent"""
    agent = GradingAgent()

    # Mock documents
    context = AgentContext(query="What is your return policy?")
    context.retrieved_docs = [
        {
            'id': 'POL001',
            'content': 'Return Policy: We offer hassle-free returns within 30 days...',
            'metadata': {'type': 'policy'}
        },
        {
            'id': 'SHIP001',
            'content': 'Shipping: Standard shipping takes 5-7 days...',
            'metadata': {'type': 'shipping'}
        }
    ]

    graded = agent.execute(context)

    print(f"Graded {len(graded)} relevant documents:")
    for doc in graded:
        print(f"\n{doc['id']}:")
        print(f"  Relevant: {doc['grading']['is_relevant']}")
        print(f"  Score: {doc['grading']['relevance_score']}")
        print(f"  Reasoning: {doc['grading']['reasoning']}")

if __name__ == "__main__":
    main()
