"""
Mine hard negatives using current model embeddings.

Hard negatives are documents that are semantically similar to the query
but not actually relevant. This is critical for training quality.

Usage:
    # First, train a base model or use existing
    python scripts/mine_hard_negatives.py \
        --training-data data/finetuning/e5_training_data.json \
        --base-model intfloat/e5-base-v2 \
        --output data/finetuning/e5_training_data_with_hard_negs.json
"""

import sys
from pathlib import Path
import json
import argparse
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from sentence_transformers import util
import torch

sys.path.insert(0, str(Path(__file__).parent.parent))


class HardNegativeMiner:
    """Mine hard negative examples using model embeddings."""
    
    def __init__(self, base_model: str = "intfloat/e5-base-v2"):
        """
        Initialize hard negative miner.
        
        Args:
            base_model: Model to use for similarity calculation
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Loading model for hard negative mining: {base_model}")
        print(f"Device: {self.device}")
        self.model = SentenceTransformer(base_model, device=self.device)
        print("[OK] Model loaded")
    
    def mine_hard_negatives(self, 
                           query: str, 
                           positive_doc: str,
                           candidate_docs: List[str],
                           k_hard: int = 5,
                           k_easy: int = 2) -> List[str]:
        """
        Mine hard negatives using semantic similarity.
        
        Args:
            query: Query text
            positive_doc: Positive document (exclude this)
            candidate_docs: All candidate documents
            k_hard: Number of hard negatives (similar but wrong)
            k_easy: Number of easy negatives (clearly different)
            
        Returns:
            List of negative documents (hard + easy)
        """
        # Remove positive doc from candidates
        candidates = [doc for doc in candidate_docs if doc != positive_doc]
        
        if len(candidates) < k_hard + k_easy:
            return candidates
        
        # Encode query and all candidates
        query_emb = self.model.encode(query, convert_to_tensor=True)
        candidate_embs = self.model.encode(candidates, convert_to_tensor=True)
        
        # Compute similarities
        similarities = util.cos_sim(query_emb, candidate_embs)[0]
        
        # Get top-k similar documents (hard negatives)
        # These are similar to query but not the positive
        top_indices = similarities.argsort(descending=True)
        
        hard_negatives = []
        easy_negatives = []
        
        # Get hard negatives (top-k similar, excluding positive)
        for idx in top_indices:
            if len(hard_negatives) >= k_hard:
                break
            doc = candidates[idx]
            if doc != positive_doc:
                hard_negatives.append((doc, float(similarities[idx])))
        
        # Get easy negatives (bottom-k similar, clearly different)
        bottom_indices = similarities.argsort(descending=False)
        for idx in bottom_indices[:k_easy]:
            doc = candidates[idx]
            if doc != positive_doc:
                easy_negatives.append((doc, float(similarities[idx])))
        
        # Return just the documents
        return [doc for doc, _ in hard_negatives + easy_negatives]
    
    def process_training_data(self, 
                            training_data_file: str,
                            output_file: str,
                            k_hard: int = 5,
                            k_easy: int = 2):
        """
        Process training data to add model-based hard negatives.
        
        Args:
            training_data_file: Input training data
            output_file: Output file with hard negatives
            k_hard: Number of hard negatives per query
            k_easy: Number of easy negatives per query
        """
        print("=" * 70)
        print("HARD NEGATIVE MINING")
        print("=" * 70)
        
        # Load training data
        print(f"\nLoading training data: {training_data_file}")
        with open(training_data_file, 'r') as f:
            data = json.load(f)
        
        training_pairs = data['training_pairs']
        print(f"Found {len(training_pairs)} training pairs")
        
        # Collect all documents for mining
        all_docs = []
        doc_to_text = {}
        for pair in training_pairs:
            pos_doc = pair['positive']['text']
            all_docs.append(pos_doc)
            doc_to_text[pos_doc] = pos_doc
            
            for neg in pair['negatives']:
                neg_text = neg['text']
                if neg_text not in doc_to_text:
                    all_docs.append(neg_text)
                    doc_to_text[neg_text] = neg_text
        
        print(f"Total unique documents: {len(all_docs)}")
        
        # Mine hard negatives for each pair
        print("\nMining hard negatives...")
        improved_pairs = []
        
        for i, pair in enumerate(training_pairs):
            if (i + 1) % 50 == 0:
                print(f"  Processed {i+1}/{len(training_pairs)} pairs...")
            
            query = pair['query']
            positive_doc = pair['positive']['text']
            
            # Mine hard negatives
            hard_negatives = self.mine_hard_negatives(
                query=query,
                positive_doc=positive_doc,
                candidate_docs=all_docs,
                k_hard=k_hard,
                k_easy=k_easy
            )
            
            # Convert to proper format
            hard_neg_docs = []
            for neg_text in hard_negatives:
                # Find original negative doc structure
                for orig_neg in pair['negatives']:
                    if orig_neg['text'] == neg_text:
                        hard_neg_docs.append(orig_neg)
                        break
                else:
                    # Create new negative doc structure
                    hard_neg_docs.append({
                        'text': neg_text,
                        'metadata': {}
                    })
            
            # Update pair with hard negatives
            improved_pair = pair.copy()
            improved_pair['negatives'] = hard_neg_docs
            improved_pair['hard_negatives_mined'] = True
            improved_pairs.append(improved_pair)
        
        # Save improved data
        output_data = data.copy()
        output_data['training_pairs'] = improved_pairs
        output_data['metadata']['hard_negatives_mined'] = True
        output_data['metadata']['k_hard'] = k_hard
        output_data['metadata']['k_easy'] = k_easy
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print("\n" + "=" * 70)
        print("HARD NEGATIVE MINING COMPLETE")
        print("=" * 70)
        print(f"Processed: {len(improved_pairs)} pairs")
        print(f"Hard negatives per pair: {k_hard}")
        print(f"Easy negatives per pair: {k_easy}")
        print(f"Saved to: {output_file}")
        print("\nNext step: Retrain model with improved data")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Mine hard negatives using model embeddings")
    parser.add_argument('--training-data', type=str,
                       default='data/finetuning/e5_training_data.json',
                       help='Input training data file')
    parser.add_argument('--output', type=str,
                       default='data/finetuning/e5_training_data_with_hard_negs.json',
                       help='Output file with hard negatives')
    parser.add_argument('--base-model', type=str,
                       default='intfloat/e5-base-v2',
                       help='Model to use for similarity')
    parser.add_argument('--k-hard', type=int, default=5,
                       help='Number of hard negatives per query')
    parser.add_argument('--k-easy', type=int, default=2,
                       help='Number of easy negatives per query')
    
    args = parser.parse_args()
    
    miner = HardNegativeMiner(base_model=args.base_model)
    miner.process_training_data(
        training_data_file=args.training_data,
        output_file=args.output,
        k_hard=args.k_hard,
        k_easy=args.k_easy
    )


if __name__ == "__main__":
    main()

