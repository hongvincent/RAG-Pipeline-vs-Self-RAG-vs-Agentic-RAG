.PHONY: help install build-vector-store test demo-traditional demo-self demo-agentic demo-all clean

PYTHONPATH := .

help:
	@echo "RAG Pipeline - Makefile Commands"
	@echo "================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install          - Install all dependencies"
	@echo "  make setup            - Run full setup (install + build vector store)"
	@echo ""
	@echo "Data Commands:"
	@echo "  make build-vector-store - Build the vector store from knowledge base"
	@echo ""
	@echo "Demo Commands:"
	@echo "  make demo-traditional - Run Traditional RAG demo"
	@echo "  make demo-self        - Run Self RAG demo"
	@echo "  make demo-agentic     - Run Agentic RAG demo"
	@echo "  make demo-all         - Run all demos"
	@echo ""
	@echo "Test Commands:"
	@echo "  make test             - Run all tests"
	@echo "  make test-loader      - Test data loader"
	@echo "  make test-vector      - Test vector store"
	@echo "  make test-agents      - Test individual agents"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean            - Clean temporary files"
	@echo "  make format           - Format code with black"
	@echo ""

install:
	pip install --upgrade pip
	pip install openai python-dotenv chromadb sentence-transformers pydantic pydantic-settings tiktoken

setup: install
	@echo "Checking for .env file..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from template"; \
		echo "⚠️  Please edit .env and add your OpenAI API key"; \
	fi
	@make build-vector-store

build-vector-store:
	PYTHONPATH=. python src/vector_store.py

demo-traditional:
	PYTHONPATH=. python examples/01_traditional_rag_demo.py

demo-self:
	PYTHONPATH=. python examples/02_self_rag_demo.py

demo-agentic:
	PYTHONPATH=. python examples/03_agentic_rag_demo.py

demo-all: demo-traditional demo-self demo-agentic

test-loader:
	PYTHONPATH=. python src/data_loader.py

test-vector:
	PYTHONPATH=. python src/vector_store.py

test-embeddings:
	PYTHONPATH=. python src/embeddings.py

test-reranker:
	PYTHONPATH=. python src/reranker.py

test-router:
	PYTHONPATH=. python src/agents/router_agent.py

test-planning:
	PYTHONPATH=. python src/agents/planning_agent.py

test-agents: test-router test-planning

test: test-loader test-embeddings test-reranker test-agents

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage

format:
	black src/ examples/
