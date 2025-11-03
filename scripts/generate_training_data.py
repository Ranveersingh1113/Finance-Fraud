"""
Generate substantial training data for E5 embedding fine-tuning.

This script automatically generates 500-1000 training pairs from:
1. Existing ChromaDB documents
2. Document metadata (titles, types, keywords)
3. Synthetic query generation

Usage:
    python scripts/generate_training_data.py --output data/finetuning/e5_training_data.json
"""

import sys
from pathlib import Path
import json
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Tuple
import random
from datetime import datetime
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))


class TrainingDataGenerator:
    """Generate training data from ChromaDB for embedding fine-tuning."""
    
    def __init__(self, target_pairs: int = 1000):
        self.target_pairs = target_pairs
        self.chroma_client = chromadb.PersistentClient(
            path="./data/chroma_db",
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get all collections
        self.collections = {}
        for col in self.chroma_client.list_collections():
            self.collections[col.name] = col
            print(f"✓ Loaded collection: {col.name} ({col.count()} documents)")
    
    def generate_query_from_metadata(self, metadata: Dict, document_text: str) -> List[str]:
        """
        Generate multiple query variations from document metadata.
        
        Returns list of synthetic queries for this document.
        """
        queries = []
        
        # From title
        if 'title' in metadata and metadata['title']:
            title = metadata['title']
            queries.append(f"What is {title}?")
            queries.append(f"Explain {title}")
            queries.append(title)  # Direct title search
        
        # From document type
        doc_type = metadata.get('document_type', '')
        if doc_type == 'regulation':
            queries.append(f"What are the regulations about {metadata.get('title', 'this topic')}?")
        elif doc_type == 'case':
            queries.append(f"Show me cases about {metadata.get('title', 'this violation')}") 
        
        # From violation types
        violations = metadata.get('violation_types', '')
        if violations:
            viol_list = violations.split(',') if isinstance(violations, str) else []
            for v in viol_list[:2]:  # First 2 violations
                v = v.strip()
                queries.append(f"What are SEBI penalties for {v}?")
                queries.append(f"{v} regulations")
        
        # From keywords
        keywords = metadata.get('keywords', '')
        if keywords:
            kw_list = keywords.split(',') if isinstance(keywords, str) else []
            if len(kw_list) >= 2:
                # Combine 2 keywords
                queries.append(f"{kw_list[0].strip()} and {kw_list[1].strip()}")
        
        # From document content (first 100 words)
        words = document_text.split()[:100]
        content_sample = ' '.join(words)
        
        # Extract key phrases for query
        if 'insider trading' in content_sample.lower():
            queries.append("What is insider trading?")
            queries.append("SEBI insider trading regulations")
        
        if 'money laundering' in content_sample.lower():
            queries.append("What is money laundering?")
            queries.append("Money laundering detection")
        
        if 'market manipulation' in content_sample.lower():
            queries.append("What is market manipulation?")
            queries.append("PFUTP regulations")
        
        # Remove duplicates and empty
        queries = list(set([q for q in queries if q and len(q) > 5]))
        
        return queries[:5]  # Max 5 queries per document
    
    def create_training_pairs(self) -> List[Dict]:
        """
        Create training pairs: (query, positive_doc, negative_docs)
        """
        all_training_pairs = []
        
        for collection_name, collection in self.collections.items():
            print(f"\n Processing {collection_name}...")
            
            # Get all documents from collection
            try:
                data = collection.get(
                    include=['documents', 'metadatas'],
                    limit=collection.count()
                )
            except Exception as e:
                print(f"  ✗ Error loading {collection_name}: {e}")
                continue
            
            num_docs = len(data['ids'])
            print(f"  • Found {num_docs} documents")
            
            # For each document, generate queries
            for i in range(num_docs):
                doc_id = data['ids'][i]
                doc_text = data['documents'][i]
                metadata = data['metadatas'][i]
                
                # Generate queries for this document
                queries = self.generate_query_from_metadata(metadata, doc_text)
                
                if not queries:
                    continue
                
                # This document is the POSITIVE example
                positive_doc = {
                    'id': doc_id,
                    'text': doc_text[:1000],  # First 1000 chars
                    'metadata': metadata
                }
                
                # Sample NEGATIVE examples from same collection
                # (documents that are NOT this one)
                negative_indices = [j for j in range(num_docs) if j != i]
                negative_samples = random.sample(
                    negative_indices, 
                    min(5, len(negative_indices))
                )
                
                negative_docs = []
                for neg_idx in negative_samples:
                    negative_docs.append({
                        'id': data['ids'][neg_idx],
                        'text': data['documents'][neg_idx][:1000],
                        'metadata': data['metadatas'][neg_idx]
                    })
                
                # Create training pair for each query
                for query in queries:
                    all_training_pairs.append({
                        'query': query,
                        'positive': positive_doc,
                        'negatives': negative_docs,
                        'source_collection': collection_name,
                        'doc_type': metadata.get('document_type', 'unknown')
                    })
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    print(f"  • Processed {i+1}/{num_docs} documents...")
            
            print(f"  ✓ Generated {len([p for p in all_training_pairs if p['source_collection'] == collection_name])} pairs from {collection_name}")
        
        return all_training_pairs
    
    def add_expert_queries(self) -> List[Dict]:
        """
        Add expert-crafted queries for important domain concepts.
        These ensure coverage of key topics.
        """
        expert_queries = [
            # Insider trading
            "What are SEBI penalties for insider trading violations?",
            "Explain SEBI PIT regulations 2015",
            "What is UPSI (Unpublished Price Sensitive Information)?",
            "How does SEBI define insider trading?",
            "Prohibition of insider trading rules",
            
            # Money laundering
            "What is money laundering?",
            "Explain the three stages of money laundering",
            "PMLA money laundering definition",
            "How to detect money laundering patterns?",
            "AML compliance requirements",
            
            # Market manipulation
            "What is PFUTP?",
            "SEBI market manipulation regulations",
            "Fraudulent and unfair trade practices examples",
            "How to detect market manipulation?",
            
            # LODR
            "What are SEBI LODR requirements?",
            "Listing obligations and disclosure requirements",
            "LODR compliance for listed companies",
            
            # Transaction patterns
            "What is fan-out transaction pattern?",
            "Explain fan-in money flow",
            "How to detect fraud rings in transactions?",
            "Circular money flow patterns",
            "Structuring and smurfing detection",
            
            # General fraud
            "What are red flags for financial fraud?",
            "How to identify suspicious transactions?",
            "AML typologies and patterns",
            "Financial fraud detection methods",
        ]
        
        # For expert queries, we'll retrieve documents later
        return expert_queries
    
    def generate_dataset(self) -> Dict:
        """Generate complete training dataset."""
        print("=" * 70)
        print("TRAINING DATA GENERATION FOR FIN-E5")
        print("=" * 70)
        print(f"Target: {self.target_pairs} training pairs\n")
        
        # Step 1: Generate from existing documents
        print("[1/3] Generating pairs from ChromaDB documents...")
        document_pairs = self.create_training_pairs()
        print(f"✓ Generated {len(document_pairs)} document-based pairs")
        
        # Step 2: Add expert queries
        print("\n[2/3] Adding expert-crafted queries...")
        expert_queries = self.add_expert_queries()
        print(f"✓ Added {len(expert_queries)} expert queries")
        
        # For expert queries, retrieve top documents as positives
        expert_pairs = []
        for query in expert_queries:
            # Search in all collections
            for col_name, collection in self.collections.items():
                try:
                    results = collection.query(
                        query_texts=[query],
                        n_results=5,
                        include=['documents', 'metadatas', 'distances']
                    )
                    
                    if results['ids'][0]:
                        # Top result is positive
                        positive = {
                            'id': results['ids'][0][0],
                            'text': results['documents'][0][0][:1000],
                            'metadata': results['metadatas'][0][0]
                        }
                        
                        # Rest are negatives
                        negatives = []
                        for i in range(1, min(5, len(results['ids'][0]))):
                            negatives.append({
                                'id': results['ids'][0][i],
                                'text': results['documents'][0][i][:1000],
                                'metadata': results['metadatas'][0][i]
                            })
                        
                        expert_pairs.append({
                            'query': query,
                            'positive': positive,
                            'negatives': negatives,
                            'source_collection': col_name,
                            'doc_type': 'expert_query'
                        })
                        break  # Found in this collection, move to next query
                
                except Exception as e:
                    continue
        
        print(f"✓ Created {len(expert_pairs)} expert query pairs")
        
        # Step 3: Combine and shuffle
        print("\n[3/3] Combining and shuffling dataset...")
        all_pairs = document_pairs + expert_pairs
        random.shuffle(all_pairs)
        
        # Limit to target if we have too many
        if len(all_pairs) > self.target_pairs:
            all_pairs = all_pairs[:self.target_pairs]
            print(f"✓ Trimmed to {self.target_pairs} pairs")
        
        # Create dataset structure
        dataset = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'target_pairs': self.target_pairs,
                'actual_pairs': len(all_pairs),
                'base_model': 'intfloat/e5-base-v2',
                'target_model': 'fin-e5',
                'collections': list(self.collections.keys()),
                'statistics': {
                    'document_based_pairs': len(document_pairs),
                    'expert_query_pairs': len(expert_pairs),
                    'total': len(all_pairs)
                }
            },
            'training_pairs': all_pairs
        }
        
        return dataset
    
    def save_dataset(self, dataset: Dict, output_file: str):
        """Save dataset to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print("\n" + "=" * 70)
        print("DATASET GENERATION COMPLETE")
        print("=" * 70)
        print(f"\nTotal pairs: {dataset['metadata']['actual_pairs']}")
        print(f"  • Document-based: {dataset['metadata']['statistics']['document_based_pairs']}")
        print(f"  • Expert queries: {dataset['metadata']['statistics']['expert_query_pairs']}")
        print(f"\nSaved to: {output_path}")
        print(f"File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
        print("\n" + "=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print(f"1. Review the data (optional):")
        print(f"   Open {output_file} and spot-check quality")
        print(f"\n2. Run fine-tuning:")
        print(f"   python scripts/finetune_e5_model.py --train --data {output_file}")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Generate training data for E5 fine-tuning")
    parser.add_argument('--output', type=str,
                       default='data/finetuning/e5_training_data.json',
                       help='Output file path')
    parser.add_argument('--target-pairs', type=int, default=1000,
                       help='Target number of training pairs (default: 1000)')
    
    args = parser.parse_args()
    
    generator = TrainingDataGenerator(target_pairs=args.target_pairs)
    dataset = generator.generate_dataset()
    generator.save_dataset(dataset, args.output)


if __name__ == "__main__":
    main()

