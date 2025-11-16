# Contributing to RAG Pipeline Project

Thank you for your interest in contributing to this educational RAG implementation project!

## Development Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd RAG-Pipeline-vs-Self-RAG-vs-Agentic-RAG
```

### 2. Install Dependencies

Using the setup script:
```bash
./setup.sh
```

Or manually:
```bash
pip install openai python-dotenv chromadb sentence-transformers pydantic pydantic-settings tiktoken
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 4. Build Vector Store

```bash
export PYTHONPATH=.
python src/vector_store.py
```

## Project Structure

```
src/
├── config.py              # Configuration management
├── data_loader.py         # Knowledge base loading
├── embeddings.py          # OpenAI embeddings
├── vector_store.py        # ChromaDB operations
├── reranker.py            # Document reranking
├── rag/
│   ├── traditional_rag.py # Traditional RAG
│   ├── self_rag.py        # Self RAG
│   └── agentic_rag.py     # Agentic RAG
└── agents/
    ├── base_agent.py      # Base agent class
    ├── router_agent.py    # Query routing
    ├── planning_agent.py  # Plan creation
    ├── retrieval_agent.py # Document retrieval
    ├── grading_agent.py   # Document grading
    ├── generation_agent.py # Answer generation
    └── validation_agent.py # Quality validation
```

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write docstrings for all functions and classes
- Keep functions focused and single-purpose

Example:
```python
def retrieve_documents(
    self,
    query: str,
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """
    Retrieve documents from vector store

    Args:
        query: User query string
        top_k: Number of documents to retrieve

    Returns:
        List of documents with metadata
    """
    pass
```

### Adding New Features

#### Adding a New Agent

1. Create file in `src/agents/`
2. Inherit from `BaseAgent`
3. Implement `execute()` method
4. Add tests in `tests/`

Example:
```python
from src.agents.base_agent import BaseAgent, AgentContext

class MyNewAgent(BaseAgent):
    def __init__(self, model: str = "gpt-3.5-turbo"):
        super().__init__(name="MyNewAgent", model=model)

    def execute(self, context: AgentContext) -> Dict[str, Any]:
        # Your implementation
        result = self.call_llm("Your prompt")
        self.log_action(context, "my_action", result)
        return result
```

#### Extending Knowledge Base

1. Add JSON file to `data/knowledge_base/`
2. Update `src/data_loader.py` to load new data
3. Rebuild vector store

### Testing

Run tests before submitting:
```bash
# All tests
make test

# Specific component
make test-loader
make test-vector
make test-agents

# Run pytest directly
PYTHONPATH=. pytest tests/ -v
```

### Documentation

Update documentation when:
- Adding new features
- Changing APIs
- Modifying configuration options

Files to update:
- `README.md` - User-facing documentation
- `claude.md` - Implementation plan
- `agents.md` - Agent architecture
- Inline docstrings

## Contribution Workflow

### 1. Create Issue

- Describe the feature or bug
- Provide examples if applicable
- Tag appropriately

### 2. Create Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Make Changes

- Write code following guidelines
- Add tests
- Update documentation

### 4. Test Thoroughly

```bash
# Run all tests
make test

# Run demos to verify
make demo-all

# Test manually
PYTHONPATH=. python examples/01_traditional_rag_demo.py
```

### 5. Commit

```bash
git add .
git commit -m "feat: add new feature description"
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Create pull request with:
- Clear description
- Test results
- Documentation updates

## Ideas for Contributions

### New Features

1. **Memory Agent**: Add conversation history management
2. **Tool Agent**: Integrate external tools (calculator, web search)
3. **Parallel Retrieval**: Implement concurrent retrieval
4. **Streaming Responses**: Add streaming support
5. **Evaluation Metrics**: Implement automated quality metrics

### Improvements

1. **Caching**: Add LLM response caching
2. **Rate Limiting**: Implement API rate limiting
3. **Error Recovery**: Better error handling and recovery
4. **Logging**: Structured logging with levels
5. **Performance**: Optimize vector search and reranking

### Documentation

1. **Tutorial Videos**: Create video tutorials
2. **Blog Posts**: Write detailed explanations
3. **Architecture Diagrams**: Create visual diagrams
4. **Best Practices**: Document RAG best practices

### Knowledge Base

1. **More Categories**: Add new product categories
2. **Multilingual**: Add support for other languages
3. **Domain-Specific**: Create domain-specific knowledge bases
4. **Synthetic Data**: Generate synthetic Q&A pairs

## Questions?

- Open an issue for questions
- Check existing documentation
- Review code examples in `examples/`

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on learning and improvement
- Help others learn

Thank you for contributing! 🎉
