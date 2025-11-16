"""
Data loader for knowledge base documents
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from src.config import settings

@dataclass
class Document:
    """Document with content and metadata"""
    content: str
    metadata: Dict[str, Any]
    doc_id: str = ""

    def __post_init__(self):
        if not self.doc_id and 'id' in self.metadata:
            self.doc_id = self.metadata['id']

class KnowledgeBaseLoader:
    """Load and process knowledge base documents"""

    def __init__(self, kb_dir: Path = None):
        self.kb_dir = kb_dir or settings.knowledge_base_dir

    def load_json_file(self, file_path: Path) -> List[Dict]:
        """Load a JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_products(self) -> List[Document]:
        """Load product documents"""
        products = self.load_json_file(self.kb_dir / "products.json")
        documents = []

        for product in products:
            # Create rich text representation
            content = f"""
Product: {product['name']}
Category: {product['category']}
Price: ${product['price']}
Description: {product['description']}
Specifications: {product.get('specifications', 'N/A')}
Warranty: {product.get('warranty', 'No warranty')}
Return Period: {product.get('return_period', 'Standard return policy applies')}
            """.strip()

            documents.append(Document(
                content=content,
                metadata={
                    'id': product['id'],
                    'category': product['category'],
                    'type': 'product',
                    'name': product['name'],
                    'price': product['price']
                },
                doc_id=product['id']
            ))

        return documents

    def load_policies(self) -> List[Document]:
        """Load policy documents"""
        policies = self.load_json_file(self.kb_dir / "policies.json")
        documents = []

        for policy in policies:
            content = f"""
Policy: {policy['title']}
Category: {policy['category']}
Details: {policy['content']}
            """.strip()

            documents.append(Document(
                content=content,
                metadata={
                    'id': policy['id'],
                    'category': policy['category'],
                    'type': 'policy',
                    'title': policy['title']
                },
                doc_id=policy['id']
            ))

        return documents

    def load_shipping(self) -> List[Document]:
        """Load shipping documents"""
        shipping_docs = self.load_json_file(self.kb_dir / "shipping.json")
        documents = []

        for doc in shipping_docs:
            content = f"""
Shipping Information: {doc['title']}
Category: {doc['category']}
Details: {doc['content']}
            """.strip()

            documents.append(Document(
                content=content,
                metadata={
                    'id': doc['id'],
                    'category': doc['category'],
                    'type': 'shipping',
                    'title': doc['title']
                },
                doc_id=doc['id']
            ))

        return documents

    def load_faq(self) -> List[Document]:
        """Load FAQ documents"""
        faqs = self.load_json_file(self.kb_dir / "faq.json")
        documents = []

        for faq in faqs:
            content = f"""
Question: {faq['question']}
Category: {faq['category']}
Answer: {faq['answer']}
            """.strip()

            documents.append(Document(
                content=content,
                metadata={
                    'id': faq['id'],
                    'category': faq['category'],
                    'type': 'faq',
                    'question': faq['question']
                },
                doc_id=faq['id']
            ))

        return documents

    def load_all(self) -> List[Document]:
        """Load all knowledge base documents"""
        all_docs = []

        print("Loading products...")
        all_docs.extend(self.load_products())

        print("Loading policies...")
        all_docs.extend(self.load_policies())

        print("Loading shipping information...")
        all_docs.extend(self.load_shipping())

        print("Loading FAQs...")
        all_docs.extend(self.load_faq())

        print(f"Loaded {len(all_docs)} documents total")
        return all_docs

def main():
    """Test data loader"""
    loader = KnowledgeBaseLoader()
    docs = loader.load_all()

    print(f"\nSample documents:")
    for doc in docs[:3]:
        print(f"\n{'-'*50}")
        print(f"ID: {doc.doc_id}")
        print(f"Type: {doc.metadata['type']}")
        print(f"Content preview: {doc.content[:200]}...")

if __name__ == "__main__":
    main()
