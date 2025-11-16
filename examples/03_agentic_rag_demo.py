"""
Demo: Agentic RAG with Multi-Agent Decision Making

This demonstrates Agentic RAG with:
1. Router Agent (query classification)
2. Planning Agent (creates execution plan)
3. Retrieval Agent (intelligent retrieval)
4. Grading Agent (document evaluation)
5. Generation Agent (answer creation)
6. Validation Agent (quality verification)
7. Adaptive execution flow
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import VectorStore, build_vector_store
from src.rag.agentic_rag import AgenticRAG

def main():
    print("="*70)
    print("AGENTIC RAG DEMO")
    print("="*70)

    # Build/load vector store
    print("\nInitializing vector store...")
    vector_store = VectorStore()

    if vector_store.count() == 0:
        print("Building vector store from knowledge base...")
        vector_store = build_vector_store()
    else:
        print(f"Vector store loaded: {vector_store.count()} documents")

    # Initialize Agentic RAG
    print("\nInitializing Agentic RAG with multi-agent system...")
    agentic_rag = AgenticRAG(vector_store, max_iterations=3)

    # Test queries demonstrating agent capabilities
    test_queries = [
        {
            "query": "Hello! How can you help me?",
            "description": "Greeting - tests router's conversational detection"
        },
        {
            "query": "What is your return policy?",
            "description": "Simple query - tests basic agent coordination"
        },
        {
            "query": "Can I return electronics after 30 days if they're defective?",
            "description": "Medium complexity - tests planning and validation"
        },
        {
            "query": "Compare the return policies for electronics and clothing items",
            "description": "Complex comparison - tests multi-hop reasoning"
        },
        {
            "query": "I bought a laptop 25 days ago and it stopped working. Considering both the return policy and warranty, what are my best options?",
            "description": "Very complex - tests full agent capabilities"
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
        result = agentic_rag.query(test['query'], verbose=True)

        # Show routing decision
        print(f"\n🎯 Routing Decision:")
        route = result['route_info']
        print(f"   Category: {route['category']}")
        print(f"   Complexity: {route['complexity']}")
        print(f"   Strategy: {route['suggested_strategy']}")
        print(f"   Confidence: {route['confidence']:.2f}")

        # Show plan if available
        if 'plan' in result and result['plan']:
            print(f"\n📋 Execution Plan:")
            for j, step in enumerate(result['plan'], 1):
                action = step.get('action', 'unknown')
                desc = step.get('description', step.get('target', ''))
                print(f"   {j}. {action}: {desc}")

        # Show validation if available
        if 'validation' in result:
            print(f"\n✓ Validation Results:")
            val = result['validation']
            print(f"   Overall Quality: {val['overall_quality']}")
            print(f"   Valid: {val['is_valid']}")
            print(f"   Recommendation: {val['recommendation']}")

        # Show execution metrics
        print(f"\n📊 Execution Metrics:")
        print(f"   Iterations: {result.get('iterations', 0)}")
        print(f"   Sources used: {len(result.get('sources', []))}")
        print(f"   Agent calls: {len(result.get('trace', []))}")

        # Show agent execution trace
        print(f"\n🤖 Agent Execution Trace:")
        trace = result.get('trace', [])
        agent_counts = {}
        for entry in trace:
            agent = entry['agent']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        for agent, count in agent_counts.items():
            print(f"   {agent}: {count} call(s)")

        # Show sources if available
        if result.get('sources'):
            print(f"\n📚 Information Sources:")
            for j, source in enumerate(result['sources'][:3], 1):
                doc_type = source['metadata']['type']
                title = source['metadata'].get('title', source['metadata'].get('name', 'N/A'))
                grading = source.get('grading', {})
                relevance = grading.get('relevance_score', 0)
                print(f"   [{j}] {doc_type}: {title}")
                if relevance:
                    print(f"       Relevance: {relevance:.2f}")

        # Wait for user
        if i < len(test_queries):
            input("\n⏎ Press Enter to continue to next query...")

    # Show detailed trace for last query
    print(f"\n{'='*70}")
    print("DETAILED EXECUTION TRACE (Last Query)")
    print("="*70)
    agentic_rag.print_trace(result)

    print(f"\n{'='*70}")
    print("DEMO COMPLETED")
    print("="*70)
    print("""
Agentic RAG Characteristics:
✓ Multi-agent architecture
✓ Intelligent query routing
✓ Dynamic planning
✓ Adaptive execution
✓ Quality validation
✓ Complex reasoning capabilities

Advantages over Self RAG:
✓ Better handling of complex queries
✓ More sophisticated decision-making
✓ Specialized agents for different tasks
✓ Can handle multi-hop reasoning
✓ Modular and extensible

Trade-offs:
⚠ More LLM calls (higher cost)
⚠ Longer execution time
⚠ More complex implementation
✓ BUT: Superior quality for complex queries

Best Use Cases:
• Complex customer support scenarios
• Multi-step reasoning tasks
• Comparison and analysis queries
• Scenarios requiring high accuracy
    """)

if __name__ == "__main__":
    main()
