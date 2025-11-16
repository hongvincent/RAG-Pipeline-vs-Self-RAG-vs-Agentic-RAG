"""
Unit tests for Traditional RAG
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import VectorStore
from src.rag.traditional_rag import TraditionalRAG

class TestTraditionalRAG:
    """Test Traditional RAG implementation"""

    @pytest.fixture
    def vector_store(self):
        """Create vector store fixture"""
        return VectorStore()

    @pytest.fixture
    def rag(self, vector_store):
        """Create RAG instance"""
        return TraditionalRAG(vector_store)

    def test_initialization(self, rag):
        """Test RAG initialization"""
        assert rag is not None
        assert rag.vector_store is not None
        assert rag.reranker is not None

    def test_retrieve(self, rag):
        """Test document retrieval"""
        query = "What is your return policy?"
        docs = rag.retrieve(query)

        assert isinstance(docs, list)
        assert len(docs) > 0
        assert 'content' in docs[0]
        assert 'metadata' in docs[0]

    def test_rerank(self, rag):
        """Test document reranking"""
        query = "What is your return policy?"
        docs = rag.retrieve(query)
        reranked = rag.rerank(query, docs)

        assert isinstance(reranked, list)
        assert len(reranked) <= len(docs)
        assert 'rerank_score' in reranked[0]

    def test_generate(self, rag):
        """Test answer generation"""
        query = "What is your return policy?"
        docs = rag.retrieve(query)
        reranked = rag.rerank(query, docs)
        result = rag.generate(query, reranked)

        assert 'answer' in result
        assert 'sources' in result
        assert isinstance(result['answer'], str)
        assert len(result['answer']) > 0

    def test_query_end_to_end(self, rag):
        """Test complete query pipeline"""
        query = "How long does shipping take?"
        result = rag.query(query, verbose=False)

        assert 'answer' in result
        assert 'sources' in result
        assert 'model' in result
        assert isinstance(result['answer'], str)
        assert len(result['sources']) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
