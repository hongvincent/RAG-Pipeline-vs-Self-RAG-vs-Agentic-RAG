#!/bin/bash

# Demo runner script

export PYTHONPATH=.

echo "================================================"
echo "RAG Systems Demo"
echo "================================================"
echo ""
echo "Select which demo to run:"
echo "1. Traditional RAG"
echo "2. Self RAG"
echo "3. Agentic RAG"
echo "4. Run all demos"
echo "5. Build vector store"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "Running Traditional RAG demo..."
        python examples/01_traditional_rag_demo.py
        ;;
    2)
        echo "Running Self RAG demo..."
        python examples/02_self_rag_demo.py
        ;;
    3)
        echo "Running Agentic RAG demo..."
        python examples/03_agentic_rag_demo.py
        ;;
    4)
        echo "Running all demos..."
        python examples/01_traditional_rag_demo.py
        echo ""
        echo "Press Enter to continue to Self RAG demo..."
        read
        python examples/02_self_rag_demo.py
        echo ""
        echo "Press Enter to continue to Agentic RAG demo..."
        read
        python examples/03_agentic_rag_demo.py
        ;;
    5)
        echo "Building vector store..."
        python src/vector_store.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
