"""
Validate training data quality before training.

Detects common issues:
- Label noise (queries not matching documents)
- Domain mismatches
- Insufficient overlap
- Too short documents

Usage:
    python scripts/validate_training_data_quality.py \
        --data data/finetuning/e5_training_data.json \
        --output data/finetuning/e5_training_data_cleaned.json
"""

import sys
from pathlib import Path
import json
import argparse
from typing import List, Dict, Tuple
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))


class TrainingDataValidator:
    """Validate training data quality."""
    
    def __init__(self, min_overlap: float = 0.2, min_doc_words: int = 50):
        """
        Initialize validator.
        
        Args:
            min_overlap: Minimum keyword overlap (0.2 = 20%)
            min_doc_words: Minimum document length in words
        """
        self.min_overlap = min_overlap
        self.min_doc_words = min_doc_words
        
        # Domain keywords for classification
        self.sebi_keywords = {'sebi', 'regulation', 'adjudication', 'penalty', 
                             'pmla', 'lodr', 'pit', 'pfutp', 'violation', 'compliance'}
        self.amlsim_keywords = {'transaction', 'account', 'aml', 'money laundering',
                               'fan-out', 'fan-in', 'pattern', 'fraud', 'suspicious'}
    
    def classify_domain(self, text: str) -> str:
        """Classify text domain (SEBI, AMLSim, or unknown)."""
        text_lower = text.lower()
        
        sebi_score = sum(1 for kw in self.sebi_keywords if kw in text_lower)
        amlsim_score = sum(1 for kw in self.amlsim_keywords if kw in text_lower)
        
        if sebi_score > amlsim_score and sebi_score > 0:
            return 'sebi'
        elif amlsim_score > sebi_score and amlsim_score > 0:
            return 'amlsim'
        else:
            return 'unknown'
    
    def calculate_overlap(self, query: str, doc: str) -> float:
        """Calculate keyword overlap between query and document."""
        query_words = set(query.lower().split())
        doc_words = set(doc.lower().split())
        
        if len(query_words) == 0:
            return 0.0
        
        overlap = len(query_words & doc_words) / len(query_words)
        return overlap
    
    def validate_pair(self, pair: Dict) -> Tuple[bool, str]:
        """
        Validate a single training pair.
        
        Returns:
            (is_valid, reason)
        """
        query = pair['query']
        positive_doc = pair['positive']['text']
        
        # Check 1: Keyword overlap
        overlap = self.calculate_overlap(query, positive_doc)
        if overlap < self.min_overlap:
            return False, f"Low overlap: {overlap:.1%} < {self.min_overlap:.1%}"
        
        # Check 2: Domain mismatch
        query_domain = self.classify_domain(query)
        doc_domain = self.classify_domain(positive_doc)
        
        if query_domain != 'unknown' and doc_domain != 'unknown':
            if query_domain != doc_domain:
                return False, f"Domain mismatch: query={query_domain}, doc={doc_domain}"
        
        # Check 3: Document too short
        doc_words = len(positive_doc.split())
        if doc_words < self.min_doc_words:
            return False, f"Document too short: {doc_words} words < {self.min_doc_words}"
        
        # Check 4: Query too short
        if len(query) < 15:
            return False, f"Query too short: {len(query)} chars"
        
        # Check 5: Generic query without specifics
        generic_patterns = ['what is', 'explain', 'show me', 'tell me']
        if any(pattern in query.lower() for pattern in generic_patterns):
            if len(query.split()) < 5:
                return False, "Generic query without specifics"
        
        return True, "OK"
    
    def validate_dataset(self, 
                        input_file: str,
                        output_file: str = None) -> Dict:
        """
        Validate entire training dataset.
        
        Returns:
            Validation statistics
        """
        print("=" * 70)
        print("TRAINING DATA VALIDATION")
        print("=" * 70)
        
        # Load data
        print(f"\nLoading: {input_file}")
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        training_pairs = data['training_pairs']
        print(f"Total pairs: {len(training_pairs)}")
        
        # Validate each pair
        valid_pairs = []
        invalid_pairs = []
        reasons = Counter()
        
        print("\nValidating pairs...")
        for i, pair in enumerate(training_pairs):
            if (i + 1) % 100 == 0:
                print(f"  Validated {i+1}/{len(training_pairs)}...")
            
            is_valid, reason = self.validate_pair(pair)
            
            if is_valid:
                valid_pairs.append(pair)
            else:
                invalid_pairs.append(pair)
                reasons[reason] += 1
        
        # Statistics
        print("\n" + "=" * 70)
        print("VALIDATION RESULTS")
        print("=" * 70)
        print(f"Valid pairs: {len(valid_pairs)} ({len(valid_pairs)/len(training_pairs)*100:.1f}%)")
        print(f"Invalid pairs: {len(invalid_pairs)} ({len(invalid_pairs)/len(training_pairs)*100:.1f}%)")
        
        if reasons:
            print(f"\nReasons for rejection:")
            for reason, count in reasons.most_common():
                print(f"  • {reason}: {count}")
        
        # Save cleaned data if output specified
        if output_file:
            output_data = data.copy()
            output_data['training_pairs'] = valid_pairs
            output_data['metadata']['validation_date'] = str(Path(__file__).stat().st_mtime)
            output_data['metadata']['original_pairs'] = len(training_pairs)
            output_data['metadata']['valid_pairs'] = len(valid_pairs)
            output_data['metadata']['removed_pairs'] = len(invalid_pairs)
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"\nCleaned data saved to: {output_file}")
        
        return {
            'total': len(training_pairs),
            'valid': len(valid_pairs),
            'invalid': len(invalid_pairs),
            'reasons': dict(reasons)
        }


def main():
    parser = argparse.ArgumentParser(description="Validate training data quality")
    parser.add_argument('--data', type=str,
                       default='data/finetuning/e5_training_data.json',
                       help='Input training data')
    parser.add_argument('--output', type=str,
                       default=None,
                       help='Output cleaned data (optional)')
    parser.add_argument('--min-overlap', type=float, default=0.2,
                       help='Minimum keyword overlap (default: 0.2)')
    parser.add_argument('--min-doc-words', type=int, default=50,
                       help='Minimum document words (default: 50)')
    
    args = parser.parse_args()
    
    validator = TrainingDataValidator(
        min_overlap=args.min_overlap,
        min_doc_words=args.min_doc_words
    )
    
    stats = validator.validate_dataset(
        input_file=args.data,
        output_file=args.output
    )
    
    print("\n" + "=" * 70)
    if stats['valid'] / stats['total'] > 0.8:
        print("[OK] Training data quality is good (>80% valid)")
    elif stats['valid'] / stats['total'] > 0.6:
        print("[WARNING] Training data quality is moderate (60-80% valid)")
    else:
        print("[ERROR] Training data quality is poor (<60% valid)")
        print("        Consider regenerating training data")
    print("=" * 70)


if __name__ == "__main__":
    main()

