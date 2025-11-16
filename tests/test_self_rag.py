"""
Unit tests for Self RAG
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import VectorStore
from src.rag.self_rag import SelfRAG

class TestSelfRAG:
    """Test Self RAG implementation"""

    @pytest.fixture
    def vector_store(self):
        """Create vector store fixture"""
        return VectorStore()

    @pytest.fixture
    def self_rag(self, vector_store):
        """Create Self RAG instance"""
        return SelfRAG(vector_store, max_iterations=2)

    def test_initialization(self, self_rag):
        """Test Self RAG initialization"""
        assert self_rag is not None
        assert self_rag.vector_store is not None
        assert self_rag.max_iterations == 2

    def test_should_retrieve(self, self_rag):
        """Test retrieval decision"""
        # Question that needs retrieval
        result = self_rag.should_retrieve("What is your return policy?")
        assert isinstance(result, dict)
        assert 'needs_retrieval' in result
        assert result['needs_retrieval'] == True

        # Greeting that doesn't need retrieval
        result = self_rag.should_retrieve("Hello!")
        assert result['needs_retrieval'] == False

    def test_grade_documents(self, self_rag):
        """Test document grading"""
        query = "What is your return policy?"
        docs = self_rag.vector_store.search(query, top_k=5)
        graded = self_rag.grade_documents(query, docs)

        assert isinstance(graded, list)
        assert len(graded) <= len(docs)
        if len(graded) > 0:
            assert 'grading' in graded[0]
            assert 'is_relevant' in graded[0]['grading']

    def test_generate_answer(self, self_rag):
        """Test answer generation"""
        query = "What is your return policy?"
        docs = self_rag.vector_store.search(query, top_k=3)
        answer = self_rag.generate_answer(query, docs)

        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_evaluate_answer(self, self_rag):
        """Test answer evaluation"""
        query = "What is your return policy?"
        docs = self_rag.vector_store.search(query, top_k=3)
        answer = self_rag.generate_answer(query, docs)
        evaluation = self_rag.evaluate_answer(query, answer, docs)

        assert isinstance(evaluation, dict)
        assert 'grounded' in evaluation
        assert 'useful' in evaluation
        assert 'complete' in evaluation
        assert 'overall_quality' in evaluation

    def test_query_with_retrieval(self, self_rag):
        """Test query that requires retrieval"""
        result = self_rag.query("What is your return policy?", verbose=False)

        assert 'answer' in result
        assert 'evaluation' in result
        assert 'retrieval_decision' in result
        assert result['retrieval_decision']['needs_retrieval'] == True

    def test_query_without_retrieval(self, self_rag):
        """Test conversational query"""
        result = self_rag.query("Hello", verbose=False)

        assert 'answer' in result
        assert result['retrieval_decision']['needs_retrieval'] == False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
