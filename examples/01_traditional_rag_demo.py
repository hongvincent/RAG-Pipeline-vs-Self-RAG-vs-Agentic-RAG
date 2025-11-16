"""
Demo: Traditional RAG Pipeline

This demonstrates the traditional RAG approach:
1. Query → Embedding
2. Vector Search → Top K documents
3. Reranking → Top N documents
4. LLM Generation → Answer
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import VectorStore, build_vector_store
from src.rag.traditional_rag import TraditionalRAG

def main():
    print("="*70)
    print("TRADITIONAL RAG DEMO")
    print("="*70)

    # Build/load vector store
    print("\nInitializing vector store...")
    vector_store = VectorStore()

    if vector_store.count() == 0:
        print("Building vector store from knowledge base...")
        vector_store = build_vector_store()
    else:
        print(f"Vector store loaded: {vector_store.count()} documents")

    # Initialize Traditional RAG
    print("\nInitializing Traditional RAG pipeline...")
    rag = TraditionalRAG(vector_store)

    # Test queries
    test_queries = [
        {
            "query": "What is your return policy?",
            "description": "Simple policy question"
        },
        {
            "query": "Tell me about the UltraBook Pro 15",
            "description": "Product information query"
        },
        {
            "query": "How long does shipping take?",
            "description": "Shipping question"
        },
        {
            "query": "Do you ship internationally?",
            "description": "International shipping question"
        },
        {
            "query": "Can I return clothing items?",
            "description": "Category-specific return question"
        }
    ]

    print("\n" + "="*70)
    print("RUNNING TEST QUERIES")
    print("="*70)

    for i, test in enumerate(test_queries, 1):
        print(f"\n{'─'*70}")
        print(f"Test Query {i}/{len(test_queries)}")
        print(f"Description: {test['description']}")
        print(f"{'─'*70}\n")

        # Run query
        result = rag.query(test['query'], verbose=True)

        # Show metadata
        print(f"\n📊 Metadata:")
        print(f"   Model: {result['model']}")
        print(f"   Sources used: {result['num_sources']}")
        print(f"   Answer length: {len(result['answer'])} characters")

        # Show sources
        print(f"\n📚 Sources:")
        for j, source in enumerate(result['sources'], 1):
            print(f"   [{j}] {source['metadata']['type']}: {source['metadata'].get('title', source['metadata'].get('name', 'N/A'))}")

        # Wait for user
        if i < len(test_queries):
            input("\n⏎ Press Enter to continue to next query...")

    print(f"\n{'='*70}")
    print("DEMO COMPLETED")
    print("="*70)
    print("""
Traditional RAG Characteristics:
✓ Straightforward pipeline
✓ Fast execution
✓ Consistent behavior
✓ Good for simple queries

Limitations:
✗ No self-checking
✗ Fixed retrieval count
✗ No query adaptation
✗ May miss nuances in complex queries
    """)

if __name__ == "__main__":
    main()
