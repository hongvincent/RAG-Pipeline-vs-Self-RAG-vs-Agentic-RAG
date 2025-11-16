"""
Traditional RAG Pipeline Implementation

Flow:
1. Query → Embedding
2. Vector Search → Top K documents
3. Reranking → Top N documents
4. LLM Generation → Answer
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI
from src.config import settings, get_openai_api_key
from src.vector_store import VectorStore
from src.reranker import DocumentReranker

class TraditionalRAG:
    """Traditional RAG pipeline with retrieval, reranking, and generation"""

    def __init__(
        self,
        vector_store: VectorStore,
        reranker: DocumentReranker = None,
        model: str = None,
        top_k: int = None,
        rerank_k: int = None
    ):
        """
        Initialize Traditional RAG

        Args:
            vector_store: Vector store for retrieval
            reranker: Document reranker (optional)
            model: OpenAI model name
            top_k: Number of documents to retrieve
            rerank_k: Number of documents after reranking
        """
        self.vector_store = vector_store
        self.reranker = reranker or DocumentReranker()
        self.model = model or settings.openai_chat_model
        self.top_k = top_k or settings.default_top_k
        self.rerank_k = rerank_k or settings.rerank_top_k

        self.client = OpenAI(api_key=get_openai_api_key())

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve documents from vector store

        Args:
            query: User query

        Returns:
            List of retrieved documents
        """
        results = self.vector_store.search(query, top_k=self.top_k)
        return results

    def rerank(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rerank documents for better relevance

        Args:
            query: User query
            documents: Retrieved documents

        Returns:
            Reranked documents
        """
        reranked = self.reranker.rerank(query, documents, top_k=self.rerank_k)
        return reranked

    def generate(self, query: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate answer using LLM

        Args:
            query: User query
            context_docs: Context documents

        Returns:
            Generated answer with metadata
        """
        # Build context from documents
        context_parts = []
        for i, doc in enumerate(context_docs, 1):
            context_parts.append(f"[Source {i}]")
            context_parts.append(doc['content'])
            context_parts.append("")

        context = "\n".join(context_parts)

        # Create prompt
        system_prompt = """You are a helpful customer support assistant for an e-commerce company.
Your job is to answer customer questions accurately based on the provided context.

Guidelines:
- Use only the information from the provided context
- Be concise but complete
- Cite sources using [Source N] notation
- If the context doesn't contain enough information to answer fully, say so
- Maintain a professional, friendly tone
- Provide specific details (prices, timeframes, etc.) when available"""

        user_prompt = f"""Context:
{context}

Customer Question: {query}

Please provide a helpful answer based on the context above."""

        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )

        answer = response.choices[0].message.content

        return {
            'answer': answer,
            'sources': context_docs,
            'model': self.model,
            'num_sources': len(context_docs)
        }

    def query(self, query: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Execute complete RAG pipeline

        Args:
            query: User query
            verbose: Print intermediate steps

        Returns:
            Complete response with answer and metadata
        """
        if verbose:
            print(f"\n{'='*60}")
            print("TRADITIONAL RAG PIPELINE")
            print(f"{'='*60}\n")
            print(f"Query: {query}\n")

        # Step 1: Retrieve
        if verbose:
            print(f"Step 1: Retrieving top {self.top_k} documents...")

        retrieved_docs = self.retrieve(query)

        if verbose:
            print(f"Retrieved {len(retrieved_docs)} documents")
            for i, doc in enumerate(retrieved_docs[:3], 1):
                print(f"  {i}. {doc['metadata']['type']}: {doc['content'][:80]}...")

        # Step 2: Rerank
        if verbose:
            print(f"\nStep 2: Reranking to top {self.rerank_k} documents...")

        reranked_docs = self.rerank(query, retrieved_docs)

        if verbose:
            print(f"Reranked to {len(reranked_docs)} documents")
            for i, doc in enumerate(reranked_docs, 1):
                print(f"  {i}. Rerank score: {doc.get('rerank_score', 0):.3f}")

        # Step 3: Generate
        if verbose:
            print(f"\nStep 3: Generating answer...")

        result = self.generate(query, reranked_docs)

        if verbose:
            print(f"\n{'='*60}")
            print("ANSWER:")
            print(f"{'='*60}")
            print(result['answer'])
            print(f"\n(Used {result['num_sources']} sources)")
            print(f"{'='*60}\n")

        return result

def main():
    """Test Traditional RAG"""
    from src.vector_store import VectorStore

    print("Initializing Traditional RAG...")
    vector_store = VectorStore()

    if vector_store.count() == 0:
        print("Vector store is empty. Please run vector_store.py first to build it.")
        return

    rag = TraditionalRAG(vector_store)

    # Test queries
    test_queries = [
        "What is your return policy?",
        "How long does shipping take?",
        "Tell me about the UltraBook Pro 15 laptop",
        "Do you ship internationally?"
    ]

    for query in test_queries:
        result = rag.query(query, verbose=True)
        input("\nPress Enter to continue to next query...")

if __name__ == "__main__":
    main()
