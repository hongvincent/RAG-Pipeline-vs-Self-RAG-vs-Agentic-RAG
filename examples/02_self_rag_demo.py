"""
Demo: Self RAG with Self-Checking

This demonstrates Self RAG with:
1. Retrieval decision (is retrieval needed?)
2. Document grading (relevance filtering)
3. Answer generation
4. Self-evaluation (quality checking)
5. Adaptive improvement (regenerate/retrieve more)
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import VectorStore, build_vector_store
from src.rag.self_rag import SelfRAG

def main():
    print("="*70)
    print("SELF RAG DEMO")
    print("="*70)

    # Build/load vector store
    print("\nInitializing vector store...")
    vector_store = VectorStore()

    if vector_store.count() == 0:
        print("Building vector store from knowledge base...")
        vector_store = build_vector_store()
    else:
        print(f"Vector store loaded: {vector_store.count()} documents")

    # Initialize Self RAG
    print("\nInitializing Self RAG pipeline...")
    self_rag = SelfRAG(vector_store, max_iterations=3)

    # Test queries with different characteristics
    test_queries = [
        {
            "query": "Hello!",
            "description": "Greeting - should NOT trigger retrieval"
        },
        {
            "query": "What is your return policy?",
            "description": "Simple policy question - should retrieve and answer"
        },
        {
            "query": "Can I return electronics after 30 days if they're defective?",
            "description": "Complex policy question - may need multiple iterations"
        },
        {
            "query": "What's the difference between standard and express shipping?",
            "description": "Comparison question - requires synthesis"
        },
        {
            "query": "I bought a laptop 25 days ago and it's not working. What are my options?",
            "description": "Complex scenario - needs warranty + return policy info"
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
        result = self_rag.query(test['query'], verbose=True)

        # Show metadata
        print(f"\n📊 Self RAG Metrics:")
        print(f"   Retrieval triggered: {result['retrieval_decision']['needs_retrieval']}")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Final quality: {result['evaluation']['overall_quality']}")

        # Show evaluation details
        eval_result = result['evaluation']
        print(f"\n📈 Quality Evaluation:")
        print(f"   Grounded: {eval_result['grounded']['score']:.2f} ({'✓' if eval_result['grounded']['is_acceptable'] else '✗'})")
        print(f"   Useful: {eval_result['useful']['score']:.2f} ({'✓' if eval_result['useful']['is_acceptable'] else '✗'})")
        print(f"   Complete: {eval_result['complete']['score']:.2f} ({'✓' if eval_result['complete']['is_acceptable'] else '✗'})")

        # Show sources if retrieval was used
        if result['sources']:
            print(f"\n📚 Sources ({len(result['sources'])} documents):")
            for j, source in enumerate(result['sources'], 1):
                relevance = source.get('grading', {}).get('relevance_score', 0)
                print(f"   [{j}] {source['metadata']['type']} (relevance: {relevance:.2f})")

        # Show improvement trace
        print(f"\n🔄 Improvement Trace:")
        for trace in result['trace']:
            if 'iteration' in trace:
                print(f"   Iteration {trace['iteration']}: {trace['evaluation']['overall_quality']} → {trace['evaluation']['recommendation']}")

        # Wait for user
        if i < len(test_queries):
            input("\n⏎ Press Enter to continue to next query...")

    print(f"\n{'='*70}")
    print("DEMO COMPLETED")
    print("="*70)
    print("""
Self RAG Characteristics:
✓ Intelligent retrieval decision
✓ Document relevance filtering
✓ Self-evaluation of answers
✓ Iterative improvement
✓ Quality metrics

Advantages over Traditional RAG:
✓ Better quality control
✓ Adaptive retrieval
✓ Handles conversational queries
✓ Provides confidence scores

Limitations:
✗ More LLM calls (higher cost)
✗ Slower execution
✗ Still follows linear flow
    """)

if __name__ == "__main__":
    main()
