"""
Embedding generation using OpenAI
"""
from typing import List
from openai import OpenAI
from src.config import settings, get_openai_api_key

class EmbeddingGenerator:
    """Generate embeddings using OpenAI API"""

    def __init__(self, model: str = None):
        self.model = model or settings.openai_embedding_model
        self.client = OpenAI(api_key=get_openai_api_key())

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        # Replace newlines with spaces for better embedding quality
        text = text.replace("\n", " ").strip()

        if not text:
            raise ValueError("Cannot generate embedding for empty text")

        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )

        return response.data[0].embedding

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch processing)"""
        if not texts:
            return []

        # Clean texts
        cleaned_texts = [text.replace("\n", " ").strip() for text in texts]

        # Filter empty texts
        non_empty_texts = [t for t in cleaned_texts if t]

        if not non_empty_texts:
            raise ValueError("No non-empty texts to embed")

        # OpenAI allows batch embedding requests
        response = self.client.embeddings.create(
            input=non_empty_texts,
            model=self.model
        )

        return [item.embedding for item in response.data]

def main():
    """Test embedding generation"""
    generator = EmbeddingGenerator()

    # Test single embedding
    text = "What is your return policy?"
    embedding = generator.generate_embedding(text)
    print(f"Generated embedding of length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")

    # Test batch embeddings
    texts = [
        "How long does shipping take?",
        "Do you ship internationally?",
        "What payment methods do you accept?"
    ]
    embeddings = generator.generate_embeddings(texts)
    print(f"\nGenerated {len(embeddings)} embeddings")

if __name__ == "__main__":
    main()
