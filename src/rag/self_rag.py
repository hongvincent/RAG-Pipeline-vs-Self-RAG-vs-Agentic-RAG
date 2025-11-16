"""
Self RAG Implementation with Self-Checking and Self-Improvement

Flow:
1. Query → Retrieval Decision
2. Retrieval (if needed) → Documents
3. Relevance Grading → Filter documents
4. Generation → Initial answer
5. Self-Evaluation:
   - Is supported by documents?
   - Is useful?
   - Is complete?
6. Decision:
   - If good → Return
   - If needs improvement → Regenerate
   - If needs more context → Retrieve again
"""
import json
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from src.config import settings, get_openai_api_key
from src.vector_store import VectorStore
from src.reranker import DocumentReranker

class SelfRAG:
    """Self RAG with self-checking and adaptive retrieval"""

    def __init__(
        self,
        vector_store: VectorStore,
        reranker: DocumentReranker = None,
        model: str = None,
        max_iterations: int = 3
    ):
        """
        Initialize Self RAG

        Args:
            vector_store: Vector store for retrieval
            reranker: Document reranker
            model: OpenAI model name
            max_iterations: Maximum self-improvement iterations
        """
        self.vector_store = vector_store
        self.reranker = reranker or DocumentReranker()
        self.model = model or settings.openai_chat_model
        self.max_iterations = max_iterations

        self.client = OpenAI(api_key=get_openai_api_key())

    def should_retrieve(self, query: str) -> Dict[str, Any]:
        """
        Decide if retrieval is needed for this query

        Args:
            query: User query

        Returns:
            Decision with reasoning
        """
        prompt = f"""Analyze this customer query and determine if external knowledge retrieval is needed.

Query: "{query}"

Some queries can be answered with general knowledge or are just greetings/small talk.
Others require specific information from our knowledge base.

Respond in JSON format:
{{
    "needs_retrieval": true/false,
    "reasoning": "explanation",
    "query_type": "product_question/policy_question/greeting/general_conversation/technical_support"
}}"""

        response = self.client.chat.completions.create(
            model=settings.openai_fast_model,  # Use faster model for decision
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result

    def grade_documents(
        self,
        query: str,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Grade each document for relevance to query

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            Filtered list of relevant documents
        """
        relevant_docs = []

        for doc in documents:
            prompt = f"""Grade the relevance of this document to the query.

Query: "{query}"

Document:
{doc['content'][:500]}

Is this document relevant to answering the query?
Respond in JSON format:
{{
    "is_relevant": true/false,
    "relevance_score": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""

            response = self.client.chat.completions.create(
                model=settings.openai_fast_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            grading = json.loads(response.choices[0].message.content)

            # Add grading to document
            doc['grading'] = grading

            # Keep if relevant
            if grading['is_relevant']:
                relevant_docs.append(doc)

        return relevant_docs

    def generate_answer(
        self,
        query: str,
        context_docs: List[Dict[str, Any]]
    ) -> str:
        """
        Generate answer from context documents

        Args:
            query: User query
            context_docs: Context documents

        Returns:
            Generated answer
        """
        if not context_docs:
            # No context - general response
            system_prompt = "You are a helpful customer support assistant."
            user_prompt = query
        else:
            # Build context
            context_parts = []
            for i, doc in enumerate(context_docs, 1):
                context_parts.append(f"[Source {i}]")
                context_parts.append(doc['content'])
                context_parts.append("")

            context = "\n".join(context_parts)

            system_prompt = """You are a customer support assistant. Answer based on the provided context.

Guidelines:
- Use only information from context
- Cite sources using [Source N]
- Be accurate and specific
- If context is insufficient, say so clearly"""

            user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )

        return response.choices[0].message.content

    def evaluate_answer(
        self,
        query: str,
        answer: str,
        context_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Self-evaluate the generated answer

        Args:
            query: Original query
            answer: Generated answer
            context_docs: Context documents used

        Returns:
            Evaluation results
        """
        # Build context summary
        context_summary = "\n".join([
            f"Source {i}: {doc['content'][:200]}..."
            for i, doc in enumerate(context_docs, 1)
        ])

        prompt = f"""Evaluate this answer across three dimensions:

Query: "{query}"

Context Sources:
{context_summary}

Generated Answer:
{answer}

Evaluate:
1. GROUNDED: Is the answer supported by the context sources? Are there any unsupported claims?
2. USEFUL: Does the answer actually address the user's question?
3. COMPLETE: Is the answer complete or is important information missing?

Respond in JSON format:
{{
    "grounded": {{
        "score": 0.0-1.0,
        "is_acceptable": true/false,
        "issues": ["list of unsupported claims if any"]
    }},
    "useful": {{
        "score": 0.0-1.0,
        "is_acceptable": true/false,
        "issues": ["list of issues if any"]
    }},
    "complete": {{
        "score": 0.0-1.0,
        "is_acceptable": true/false,
        "missing": ["list of missing information if any"]
    }},
    "overall_quality": "excellent/good/needs_improvement/poor",
    "recommendation": "accept/regenerate/retrieve_more/rewrite_query"
}}"""

        response = self.client.chat.completions.create(
            model=settings.openai_fast_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        evaluation = json.loads(response.choices[0].message.content)
        return evaluation

    def query(self, query: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Execute Self RAG with iterative improvement

        Args:
            query: User query
            verbose: Print detailed steps

        Returns:
            Final answer with execution trace
        """
        trace = []

        if verbose:
            print(f"\n{'='*60}")
            print("SELF RAG PIPELINE")
            print(f"{'='*60}\n")
            print(f"Query: {query}\n")

        # Step 1: Decide if retrieval is needed
        if verbose:
            print("Step 1: Determining if retrieval is needed...")

        retrieval_decision = self.should_retrieve(query)
        trace.append({"step": "retrieval_decision", "result": retrieval_decision})

        if verbose:
            print(f"  Needs retrieval: {retrieval_decision['needs_retrieval']}")
            print(f"  Reasoning: {retrieval_decision['reasoning']}")

        context_docs = []

        if retrieval_decision['needs_retrieval']:
            # Step 2: Retrieve documents
            if verbose:
                print(f"\nStep 2: Retrieving documents...")

            retrieved_docs = self.vector_store.search(query, top_k=10)
            trace.append({"step": "retrieval", "num_docs": len(retrieved_docs)})

            if verbose:
                print(f"  Retrieved {len(retrieved_docs)} documents")

            # Step 3: Grade documents
            if verbose:
                print(f"\nStep 3: Grading document relevance...")

            context_docs = self.grade_documents(query, retrieved_docs)
            trace.append({"step": "grading", "relevant_docs": len(context_docs)})

            if verbose:
                print(f"  {len(context_docs)} documents are relevant")

            # Rerank relevant documents
            if context_docs:
                context_docs = self.reranker.rerank(query, context_docs, top_k=3)

        # Self-improvement loop
        best_answer = None
        best_evaluation = None
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            if verbose:
                print(f"\n{'='*40}")
                print(f"Iteration {iteration}")
                print(f"{'='*40}")
                print(f"Step: Generating answer...")

            # Generate answer
            answer = self.generate_answer(query, context_docs)

            if verbose:
                print(f"\nGenerated answer preview:")
                print(f"  {answer[:200]}...")

            # Evaluate answer
            if verbose:
                print(f"\nStep: Evaluating answer quality...")

            evaluation = self.evaluate_answer(query, answer, context_docs)
            trace.append({
                "iteration": iteration,
                "step": "generation_and_evaluation",
                "evaluation": evaluation
            })

            if verbose:
                print(f"  Overall quality: {evaluation['overall_quality']}")
                print(f"  Grounded: {evaluation['grounded']['score']:.2f}")
                print(f"  Useful: {evaluation['useful']['score']:.2f}")
                print(f"  Complete: {evaluation['complete']['score']:.2f}")
                print(f"  Recommendation: {evaluation['recommendation']}")

            # Store best answer
            if best_evaluation is None or \
               evaluation['overall_quality'] in ['excellent', 'good']:
                best_answer = answer
                best_evaluation = evaluation

            # Decide next action
            if evaluation['recommendation'] == 'accept':
                if verbose:
                    print(f"\n✓ Answer accepted!")
                break

            elif evaluation['recommendation'] == 'regenerate':
                if verbose:
                    print(f"\n↻ Regenerating with stricter guidelines...")
                # Will regenerate in next iteration
                continue

            elif evaluation['recommendation'] == 'retrieve_more':
                if verbose:
                    print(f"\n→ Retrieving additional context...")

                # Retrieve more documents with modified query
                additional_docs = self.vector_store.search(
                    query,
                    top_k=5
                )
                # Add new docs that aren't already in context
                existing_ids = {doc['id'] for doc in context_docs}
                new_docs = [
                    doc for doc in additional_docs
                    if doc['id'] not in existing_ids
                ]
                context_docs.extend(new_docs[:2])
                continue

            else:
                # Accept current best
                break

        # Use best answer if final iteration didn't produce better
        if best_answer:
            final_answer = best_answer
            final_evaluation = best_evaluation
        else:
            final_answer = answer
            final_evaluation = evaluation

        if verbose:
            print(f"\n{'='*60}")
            print("FINAL ANSWER:")
            print(f"{'='*60}")
            print(final_answer)
            print(f"\nIterations: {iteration}")
            print(f"Quality: {final_evaluation['overall_quality']}")
            print(f"Sources used: {len(context_docs)}")
            print(f"{'='*60}\n")

        return {
            'answer': final_answer,
            'evaluation': final_evaluation,
            'sources': context_docs,
            'iterations': iteration,
            'trace': trace,
            'retrieval_decision': retrieval_decision
        }

def main():
    """Test Self RAG"""
    from src.vector_store import VectorStore

    print("Initializing Self RAG...")
    vector_store = VectorStore()

    if vector_store.count() == 0:
        print("Vector store is empty. Please run vector_store.py first.")
        return

    self_rag = SelfRAG(vector_store)

    # Test queries
    test_queries = [
        "Hello!",  # Greeting - should not retrieve
        "What is your return policy?",  # Should retrieve
        "Can I return electronics after 30 days if defective?",  # Complex - may need iteration
        "Compare return policies for electronics vs clothing"  # Very complex
    ]

    for query in test_queries:
        result = self_rag.query(query, verbose=True)
        input("\nPress Enter for next query...")

if __name__ == "__main__":
    main()
