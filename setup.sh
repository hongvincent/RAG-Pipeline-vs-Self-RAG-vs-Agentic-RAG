#!/bin/bash

# Setup script for RAG Pipeline Project

echo "================================================"
echo "RAG Pipeline Setup Script"
echo "================================================"

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment (optional but recommended)
read -p "Do you want to create a virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install openai python-dotenv chromadb sentence-transformers pydantic pydantic-settings tiktoken

echo ""
echo "================================================"
echo "Setup Environment Variables"
echo "================================================"

# Check if .env exists
if [ -f .env ]; then
    echo ".env file already exists"
else
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OpenAI API key"
    echo "   Open .env and replace 'your-openai-api-key-here' with your actual key"
    echo ""
fi

echo ""
echo "================================================"
echo "Build Vector Store"
echo "================================================"
read -p "Do you want to build the vector store now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Building vector store..."
    export PYTHONPATH=.
    python src/vector_store.py
fi

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your OpenAI API key"
echo "2. Run demos:"
echo "   export PYTHONPATH=."
echo "   python examples/01_traditional_rag_demo.py"
echo "   python examples/02_self_rag_demo.py"
echo "   python examples/03_agentic_rag_demo.py"
echo ""
