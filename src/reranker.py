"""
Document reranking using cross-encoder models
"""
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
from src.config import settings

class DocumentReranker:
    """Rerank documents using cross-encoder for better relevance"""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize reranker with cross-encoder model

        Args:
            model_name: HuggingFace cross-encoder model name
        """
        print(f"Loading reranker model: {model_name}")
        self.model = CrossEncoder(model_name)
        print("Reranker model loaded successfully")

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on relevance to query

        Args:
            query: Search query
            documents: List of documents from vector search
            top_k: Number of top documents to return

        Returns:
            Reranked documents with updated scores
        """
        top_k = top_k or settings.rerank_top_k

        if not documents:
            return []

        # Prepare pairs for cross-encoder
        pairs = [(query, doc['content']) for doc in documents]

        # Get relevance scores
        scores = self.model.predict(pairs)

        # Add rerank scores to documents
        for doc, score in zip(documents, scores):
            doc['rerank_score'] = float(score)

        # Sort by rerank score
        reranked = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)

        # Return top k
        return reranked[:top_k]

def main():
    """Test reranker"""
    # Sample documents from vector search
    documents = [
        {
            'id': 'POL001',
            'content': 'Return Policy: Items can be returned within 30 days...',
            'metadata': {'type': 'policy'},
            'score': 0.85
        },
        {
            'id': 'POL003',
            'content': 'Shipping Policy: We offer free shipping on orders over $50...',
            'metadata': {'type': 'policy'},
            'score': 0.75
        },
        {
            'id': 'FAQ010',
            'content': 'FAQ: How long do I have to return an item? Answer: 30 days for most items...',
            'metadata': {'type': 'faq'},
            'score': 0.80
        }
    ]

    reranker = DocumentReranker()
    query = "What is your return policy?"

    reranked = reranker.rerank(query, documents, top_k=2)

    print(f"\nQuery: {query}\n")
    print("Reranked results:")
    for i, doc in enumerate(reranked, 1):
        print(f"{i}. Rerank Score: {doc['rerank_score']:.3f} (Original: {doc['score']:.3f})")
        print(f"   Content: {doc['content'][:80]}...")
        print()

if __name__ == "__main__":
    main()
