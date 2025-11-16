"""
Unit tests for Agentic RAG
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import VectorStore
from src.rag.agentic_rag import AgenticRAG
from src.agents.base_agent import AgentContext

class TestAgenticRAG:
    """Test Agentic RAG implementation"""

    @pytest.fixture
    def vector_store(self):
        """Create vector store fixture"""
        return VectorStore()

    @pytest.fixture
    def agentic_rag(self, vector_store):
        """Create Agentic RAG instance"""
        return AgenticRAG(vector_store, max_iterations=2)

    def test_initialization(self, agentic_rag):
        """Test Agentic RAG initialization"""
        assert agentic_rag is not None
        assert agentic_rag.router is not None
        assert agentic_rag.planner is not None
        assert agentic_rag.retrieval is not None
        assert agentic_rag.grading is not None
        assert agentic_rag.generation is not None
        assert agentic_rag.validation is not None

    def test_router_agent(self, agentic_rag):
        """Test router agent"""
        context = AgentContext(query="What is your return policy?")
        route_info = agentic_rag.router.execute(context)

        assert isinstance(route_info, dict)
        assert 'category' in route_info
        assert 'complexity' in route_info
        assert 'requires_retrieval' in route_info

    def test_planning_agent(self, agentic_rag):
        """Test planning agent"""
        context = AgentContext(query="What is your return policy?")
        agentic_rag.router.execute(context)
        plan = agentic_rag.planner.execute(context)

        assert isinstance(plan, list)
        assert len(plan) > 0
        assert 'action' in plan[0]

    def test_conversational_handling(self, agentic_rag):
        """Test conversational query handling"""
        context = AgentContext(query="Hello!")
        response = agentic_rag.handle_conversational(context, verbose=False)

        assert isinstance(response, str)
        assert len(response) > 0

    def test_query_simple(self, agentic_rag):
        """Test simple query"""
        result = agentic_rag.query("What is your return policy?", verbose=False)

        assert 'answer' in result
        assert 'route_info' in result
        assert 'trace' in result
        assert isinstance(result['answer'], str)

    def test_query_conversational(self, agentic_rag):
        """Test conversational query"""
        result = agentic_rag.query("Hello!", verbose=False)

        assert 'answer' in result
        assert result['requires_retrieval'] == False

    def test_query_complex(self, agentic_rag):
        """Test complex query"""
        result = agentic_rag.query(
            "Compare electronics and clothing return policies",
            verbose=False
        )

        assert 'answer' in result
        assert 'validation' in result
        assert 'plan' in result
        assert len(result['trace']) > 0

    def test_execution_trace(self, agentic_rag):
        """Test execution trace generation"""
        result = agentic_rag.query("What is your return policy?", verbose=False)

        assert 'trace' in result
        assert len(result['trace']) > 0

        # Check trace structure
        for entry in result['trace']:
            assert 'agent' in entry
            assert 'action' in entry
            assert 'result' in entry

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
