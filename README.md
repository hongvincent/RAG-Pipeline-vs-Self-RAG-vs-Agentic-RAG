# RAG Pipeline vs Self RAG vs Agentic RAG

A comprehensive implementation and comparison of three different RAG (Retrieval-Augmented Generation) approaches using a realistic e-commerce customer support scenario.

## 📚 Overview

This project implements and demonstrates three different RAG architectures:

1. **Traditional RAG** - Straightforward retrieval and generation pipeline
2. **Self RAG** - RAG with self-checking and adaptive retrieval
3. **Agentic RAG** - Multi-agent system with intelligent decision-making

All three systems are built on a realistic **e-commerce customer support knowledge base** with products, policies, shipping information, and FAQs.

## 🏗️ Architecture Comparison

### Traditional RAG
```
Query → Embedding → Vector Search → Reranking → LLM Generation → Answer
```
- **Pros**: Fast, simple, predictable
- **Cons**: No self-checking, fixed retrieval, may miss nuances

### Self RAG
```
Query → Retrieval Decision → Retrieval → Relevance Grading → Generation
      ↓                                                        ↓
  Self-Evaluation ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ┘
      ↓
  Decision: Accept / Regenerate / Retrieve More
```
- **Pros**: Self-checking, adaptive, quality metrics
- **Cons**: More LLM calls, slower

### Agentic RAG
```
Query → Router Agent → Planning Agent → Execution (Retrieval, Grading, Generation)
                                             ↓
                                      Validation Agent
                                             ↓
                                      Adaptive Actions
```
- **Pros**: Sophisticated reasoning, handles complex queries, modular
- **Cons**: Most LLM calls, slowest, complex implementation

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd RAG-Pipeline-vs-Self-RAG-vs-Agentic-RAG
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. Build the vector store:
```bash
python src/vector_store.py
```

### Running Demos

#### Traditional RAG Demo
```bash
python examples/01_traditional_rag_demo.py
```

#### Self RAG Demo
```bash
python examples/02_self_rag_demo.py
```

#### Agentic RAG Demo
```bash
python examples/03_agentic_rag_demo.py
```

## 📁 Project Structure

```
RAG-Pipeline-vs-Self-RAG-vs-Agentic-RAG/
├── claude.md                      # Implementation plan
├── agents.md                      # Agent architecture design
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables
├── data/
│   ├── knowledge_base/           # Knowledge base documents
│   │   ├── products.json         # 20 product descriptions
│   │   ├── policies.json         # 15 policy documents
│   │   ├── shipping.json         # 15 shipping documents
│   │   └── faq.json              # 20 FAQ entries
│   └── vector_store/             # ChromaDB storage (auto-generated)
├── src/
│   ├── config.py                 # Configuration management
│   ├── data_loader.py            # Knowledge base loader
│   ├── embeddings.py             # OpenAI embeddings
│   ├── vector_store.py           # ChromaDB vector store
│   ├── reranker.py               # Cross-encoder reranking
│   ├── rag/
│   │   ├── traditional_rag.py    # Traditional RAG
│   │   ├── self_rag.py           # Self RAG
│   │   └── agentic_rag.py        # Agentic RAG
│   └── agents/
│       ├── base_agent.py         # Base agent & context
│       ├── router_agent.py       # Query classification
│       ├── planning_agent.py     # Execution planning
│       ├── retrieval_agent.py    # Intelligent retrieval
│       ├── grading_agent.py      # Document grading
│       ├── generation_agent.py   # Answer generation
│       └── validation_agent.py   # Quality validation
└── examples/
    ├── 01_traditional_rag_demo.py
    ├── 02_self_rag_demo.py
    └── 03_agentic_rag_demo.py
```

## 💡 Key Features

### Knowledge Base
- **70 documents** across 4 categories
- **Products**: Electronics, clothing, home & garden, sports
- **Policies**: Returns, warranties, refunds, privacy
- **Shipping**: Methods, costs, international
- **FAQs**: Common customer questions

### Technical Stack
- **LLM**: OpenAI GPT-4 / GPT-3.5 Turbo
- **Embeddings**: text-embedding-3-small
- **Vector Store**: ChromaDB (persistent, local)
- **Reranking**: Cross-encoder (ms-marco-MiniLM)
- **Framework**: LangChain components
- **Data Validation**: Pydantic

### Advanced Features

#### Traditional RAG
- Vector similarity search
- Cross-encoder reranking
- Source citations
- Configurable top-k

#### Self RAG
- Intelligent retrieval decision
- Document relevance grading
- Multi-dimensional answer evaluation
- Iterative improvement (up to 3 iterations)
- Confidence scoring

#### Agentic RAG
- 6 specialized agents
- Query routing and classification
- Dynamic execution planning
- Multi-hop reasoning
- Quality validation
- Execution tracing
- Adaptive action selection

## 📊 Example Queries

### Simple Queries (All Systems)
```python
"What is your return policy?"
"How long does shipping take?"
"Tell me about the UltraBook Pro 15"
```

### Medium Complexity (Self RAG, Agentic RAG)
```python
"Can I return electronics after 30 days if they're defective?"
"What's the difference between standard and express shipping?"
```

### Complex Queries (Agentic RAG Excels)
```python
"Compare return policies for electronics vs clothing"
"I bought a laptop 25 days ago and it stopped working. What are my options?"
```

## 🔧 Usage Examples

### Traditional RAG
```python
from src.vector_store import VectorStore
from src.rag.traditional_rag import TraditionalRAG

vector_store = VectorStore()
rag = TraditionalRAG(vector_store)

result = rag.query("What is your return policy?", verbose=True)
print(result['answer'])
```

### Self RAG
```python
from src.vector_store import VectorStore
from src.rag.self_rag import SelfRAG

vector_store = VectorStore()
self_rag = SelfRAG(vector_store, max_iterations=3)

result = self_rag.query(
    "Can I return electronics after 30 days if defective?",
    verbose=True
)

print(f"Answer: {result['answer']}")
print(f"Quality: {result['evaluation']['overall_quality']}")
print(f"Iterations: {result['iterations']}")
```

### Agentic RAG
```python
from src.vector_store import VectorStore
from src.rag.agentic_rag import AgenticRAG

vector_store = VectorStore()
agentic_rag = AgenticRAG(vector_store, max_iterations=3)

result = agentic_rag.query(
    "Compare electronics and clothing return policies",
    verbose=True
)

print(f"Answer: {result['answer']}")
print(f"Category: {result['route_info']['category']}")
print(f"Quality: {result['validation']['overall_quality']}")
agentic_rag.print_trace(result)
```

## 📈 Performance Comparison

| Metric | Traditional RAG | Self RAG | Agentic RAG |
|--------|----------------|----------|-------------|
| **Speed** | ⚡⚡⚡ Fast (2-3s) | ⚡⚡ Medium (4-6s) | ⚡ Slow (6-10s) |
| **Cost** | 💰 Low | 💰💰 Medium | 💰💰💰 High |
| **Simple Queries** | ✅ Excellent | ✅ Excellent | ✅ Excellent |
| **Complex Queries** | ⚠️ Fair | ✅ Good | ✅✅ Excellent |
| **Self-Correction** | ❌ None | ✅ Yes | ✅✅ Advanced |
| **Adaptability** | ❌ Fixed | ✅ Adaptive | ✅✅ Highly Adaptive |

## 🎯 When to Use Each System

### Traditional RAG
- Simple Q&A applications
- High-volume, low-latency requirements
- Budget constraints
- Straightforward retrieval tasks

### Self RAG
- Need quality assurance
- Varied query complexity
- Some budget flexibility
- Want confidence scores

### Agentic RAG
- Complex reasoning required
- Multi-step queries
- Comparison and analysis tasks
- Quality is priority over speed
- Budget allows for multiple LLM calls

## 🧪 Testing

Run individual component tests:
```bash
# Test data loader
python src/data_loader.py

# Test vector store
python src/vector_store.py

# Test embeddings
python src/embeddings.py

# Test reranker
python src/reranker.py

# Test individual agents
python src/agents/router_agent.py
python src/agents/planning_agent.py
```

## 📖 Documentation

For detailed information, see:
- [`claude.md`](claude.md) - Comprehensive implementation plan
- [`agents.md`](agents.md) - Agent architecture and design

## 🤝 Contributing

This is an educational project demonstrating different RAG approaches. Feel free to:
- Experiment with different models
- Add new agent types
- Extend the knowledge base
- Implement new evaluation metrics

## 📝 License

MIT License - Feel free to use this code for learning and experimentation.

## 🙏 Acknowledgments

- OpenAI for GPT models and embeddings
- ChromaDB for vector storage
- Sentence Transformers for reranking
- LangChain for RAG components

## 📧 Questions?

This project demonstrates:
- How to build production-ready RAG systems
- Differences between RAG architectures
- Multi-agent AI systems
- Self-checking and validation patterns
- Knowledge base design

Perfect for learning advanced RAG techniques!

---

**Built with ❤️ to demonstrate RAG system evolution from simple to sophisticated**
