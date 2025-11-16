"""
Vector store operations using ChromaDB
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from src.config import settings
from src.data_loader import Document
from src.embeddings import EmbeddingGenerator

class VectorStore:
    """Vector store for document retrieval"""

    def __init__(
        self,
        collection_name: str = None,
        persist_directory: str = None,
        embedding_generator: EmbeddingGenerator = None
    ):
        self.collection_name = collection_name or settings.collection_name
        self.persist_directory = persist_directory or str(settings.vector_store_dir)
        self.embedding_generator = embedding_generator or EmbeddingGenerator()

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Customer support knowledge base"}
        )

    def add_documents(self, documents: List[Document], batch_size: int = 100):
        """Add documents to vector store in batches"""
        print(f"Adding {len(documents)} documents to vector store...")

        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            # Extract components
            contents = [doc.content for doc in batch]
            ids = [doc.doc_id for doc in batch]
            metadatas = [doc.metadata for doc in batch]

            # Generate embeddings
            print(f"Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}...")
            embeddings = self.embedding_generator.generate_embeddings(contents)

            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )

        print(f"Successfully added {len(documents)} documents")

    def search(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        top_k = top_k or settings.default_top_k

        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'score': 1 - results['distances'][0][i]  # Convert distance to similarity score
            })

        return formatted_results

    def delete_all(self):
        """Delete all documents from collection"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Customer support knowledge base"}
        )
        print(f"Deleted all documents from {self.collection_name}")

    def count(self) -> int:
        """Get number of documents in collection"""
        return self.collection.count()

    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        results = self.collection.get(
            ids=[doc_id],
            include=["documents", "metadatas"]
        )

        if not results['ids']:
            return None

        return {
            'id': results['ids'][0],
            'content': results['documents'][0],
            'metadata': results['metadatas'][0]
        }

def build_vector_store(reset: bool = False):
    """Build vector store from knowledge base"""
    from src.data_loader import KnowledgeBaseLoader

    # Initialize
    vector_store = VectorStore()

    # Check if already populated
    if vector_store.count() > 0 and not reset:
        print(f"Vector store already contains {vector_store.count()} documents")
        print("Use reset=True to rebuild")
        return vector_store

    # Reset if requested
    if reset:
        print("Resetting vector store...")
        vector_store.delete_all()

    # Load documents
    loader = KnowledgeBaseLoader()
    documents = loader.load_all()

    # Add to vector store
    vector_store.add_documents(documents)

    print(f"\nVector store built successfully!")
    print(f"Total documents: {vector_store.count()}")

    return vector_store

def main():
    """Test vector store"""
    # Build vector store
    vector_store = build_vector_store(reset=True)

    # Test search
    print("\n" + "="*50)
    print("Testing search...")
    query = "What is your return policy?"
    results = vector_store.search(query, top_k=3)

    print(f"\nQuery: {query}")
    print(f"Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.3f}")
        print(f"   Type: {result['metadata']['type']}")
        print(f"   Content: {result['content'][:150]}...")
        print()

if __name__ == "__main__":
    main()
