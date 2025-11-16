# Quick Start Guide

Get started with RAG Pipeline in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- 2GB free disk space (for models and vector store)

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd RAG-Pipeline-vs-Self-RAG-vs-Agentic-RAG

# Run setup script
./setup.sh
```

The script will:
1. Install dependencies
2. Create .env file
3. Build vector store

### Option 2: Manual Setup

```bash
# Install dependencies
pip install openai python-dotenv chromadb sentence-transformers pydantic pydantic-settings

# Setup environment
cp .env.example .env
nano .env  # Add your OpenAI API key

# Build vector store
export PYTHONPATH=.
python src/vector_store.py
```

## Your First Query

### Traditional RAG

```bash
# Using Makefile (recommended)
make demo-traditional

# Or directly
export PYTHONPATH=.
python examples/01_traditional_rag_demo.py
```

Example output:
```
Query: What is your return policy?

Step 1: Retrieving top 10 documents...
Retrieved 10 documents

Step 2: Reranking to top 3 documents...
Reranked to 3 documents

Step 3: Generating answer...

Answer:
Based on our return policy [Source 1], you can return items within
30 days of delivery for electronics and home goods, or 60 days for
clothing and footwear. Items must be in original condition with tags
attached and original packaging.
```

### Self RAG (with quality checking)

```bash
make demo-self
```

See self-evaluation in action:
- Retrieval decision
- Document grading
- Answer quality metrics
- Iterative improvement

### Agentic RAG (multi-agent system)

```bash
make demo-agentic
```

Watch agents collaborate:
- Router classifies query
- Planner creates execution plan
- Specialized agents execute
- Validator checks quality

## Quick Examples

### Python API

```python
from src.vector_store import VectorStore
from src.rag.traditional_rag import TraditionalRAG

# Initialize
vector_store = VectorStore()
rag = TraditionalRAG(vector_store)

# Query
result = rag.query("What is your return policy?")
print(result['answer'])
```

### Self RAG with Metrics

```python
from src.rag.self_rag import SelfRAG

self_rag = SelfRAG(vector_store, max_iterations=3)
result = self_rag.query("Can I return electronics after 30 days?")

print(f"Answer: {result['answer']}")
print(f"Quality: {result['evaluation']['overall_quality']}")
print(f"Grounded: {result['evaluation']['grounded']['score']:.2f}")
print(f"Iterations: {result['iterations']}")
```

### Agentic RAG for Complex Queries

```python
from src.rag.agentic_rag import AgenticRAG

agentic = AgenticRAG(vector_store)
result = agentic.query("Compare electronics and clothing return policies")

print(f"Answer: {result['answer']}")
print(f"Category: {result['route_info']['category']}")
print(f"Quality: {result['validation']['overall_quality']}")
```

## Sample Queries to Try

### Simple (All Systems)
- "What is your return policy?"
- "How long does shipping take?"
- "Tell me about the UltraBook Pro 15"
- "Do you ship internationally?"

### Medium Complexity (Self RAG works best)
- "Can I return electronics after 30 days if they're defective?"
- "What's the difference between standard and express shipping?"
- "How do I return an item without original packaging?"

### Complex (Agentic RAG excels)
- "Compare return policies for electronics vs clothing"
- "I bought a laptop 25 days ago and it stopped working. What are my options considering both return policy and warranty?"
- "Calculate shipping cost for international delivery to Japan"

## Understanding the Output

### Traditional RAG Output
```python
{
    'answer': str,           # Generated answer
    'sources': list,         # Source documents used
    'model': str,           # Model name
    'num_sources': int      # Number of sources
}
```

### Self RAG Output
```python
{
    'answer': str,
    'evaluation': {         # Quality metrics
        'overall_quality': str,
        'grounded': {...},
        'useful': {...},
        'complete': {...}
    },
    'sources': list,
    'iterations': int,      # Improvement iterations
    'trace': list          # Execution trace
}
```

### Agentic RAG Output
```python
{
    'answer': str,
    'route_info': {        # Routing decision
        'category': str,
        'complexity': str,
        'strategy': str
    },
    'plan': list,          # Execution plan
    'validation': {...},   # Quality validation
    'sources': list,
    'iterations': int,
    'trace': list         # Agent execution trace
}
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

**Solution**: Set PYTHONPATH
```bash
export PYTHONPATH=.
```

### "OPENAI_API_KEY not found"

**Solution**: Check .env file
```bash
# Verify .env exists
cat .env

# Should contain:
OPENAI_API_KEY=sk-...
```

### "Vector store is empty"

**Solution**: Build vector store
```bash
make build-vector-store
# or
PYTHONPATH=. python src/vector_store.py
```

### "Rate limit exceeded"

**Solution**: Wait or upgrade API tier
- Free tier: Lower rate limits
- Paid tier: Higher rate limits
- Use `OPENAI_FAST_MODEL=gpt-3.5-turbo` in .env to reduce costs

## Next Steps

### Learn More
- Read [README.md](README.md) for detailed documentation
- Check [claude.md](claude.md) for implementation details
- Review [agents.md](agents.md) for agent architecture

### Customize
- Modify knowledge base in `data/knowledge_base/`
- Adjust configuration in `.env`
- Add custom agents in `src/agents/`

### Experiment
- Try different queries
- Compare system performance
- Analyze execution traces
- Tune parameters (top_k, temperature, etc.)

### Contribute
- See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- Submit issues and pull requests
- Share your improvements

## Performance Tips

### Speed Optimization
1. Use `OPENAI_FAST_MODEL=gpt-3.5-turbo` for faster responses
2. Reduce `top_k` retrieval count
3. Limit `max_iterations` in Self RAG

### Cost Optimization
1. Use GPT-3.5 instead of GPT-4
2. Reduce `max_tokens` in generation
3. Cache frequent queries
4. Batch similar queries

### Quality Optimization
1. Use GPT-4 for complex queries
2. Increase `top_k` retrieval
3. Enable more iterations in Self RAG
4. Fine-tune reranking threshold

## Support

- GitHub Issues: Report bugs
- Discussions: Ask questions
- Documentation: Check docs/
- Examples: Review examples/

Happy RAG building! 🚀
