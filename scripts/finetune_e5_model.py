"""
Fine-tune E5 embedding model for financial fraud detection domain.

Creates Fin-E5: Domain-adapted E5 model for SEBI regulations, AML, and fraud patterns.

Usage:
    # Train with generated data
    python scripts/finetune_e5_model.py --train --data data/finetuning/e5_training_data.json
    
    # Evaluate trained model
    python scripts/finetune_e5_model.py --evaluate
    
    # Export for production
    python scripts/finetune_e5_model.py --export
"""

import sys
from pathlib import Path
import json
import argparse
from typing import List, Dict
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import InformationRetrievalEvaluator
from torch.utils.data import DataLoader
import torch

# Device configuration
try:
    from src.core.device_config import get_device_string
    device = get_device_string()
except ImportError:
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class E5FineTuner:
    """Fine-tune E5 embedding model for financial domain."""
    
    def __init__(self,
                 base_model: str = "intfloat/e5-base-v2",
                 training_data_file: str = "./data/finetuning/e5_training_data.json",
                 output_dir: str = "./models/fin-e5"):
        """
        Initialize E5 fine-tuner.
        
        Args:
            base_model: Base E5 model
            training_data_file: Path to generated training data
            output_dir: Where to save Fin-E5
        """
        self.base_model_name = base_model
        self.training_data_file = Path(training_data_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.device = device
    
    def _estimate_memory_requirement(self, batch_size: int) -> float:
        """
        Estimate GPU memory requirement.
        
        E5-base: ~440MB model
        + batch_size * sequence_length * hidden_dim * 4 bytes (forward pass)
        + gradients (2x model size)
        + optimizer state (2x model size)
        """
        model_size_gb = 0.44  # E5-base model size
        activation_gb = (batch_size * 512 * 768 * 4) / 1e9  # Activations
        optimizer_gb = model_size_gb * 2  # Adam optimizer
        gradient_gb = model_size_gb
        
        total = model_size_gb + activation_gb + optimizer_gb + gradient_gb
        return total * 1.2  # Add 20% buffer
    
    def load_training_data(self) -> List[InputExample]:
        """
        Load and convert training data to sentence-transformers format.
        
        Returns:
            List of InputExample objects
        """
        logger.info(f"\nLoading training data from {self.training_data_file}")
        
        if not self.training_data_file.exists():
            raise FileNotFoundError(f"Training data not found: {self.training_data_file}")
        
        with open(self.training_data_file, 'r') as f:
            data = json.load(f)
        
        metadata = data.get('metadata', {})
        training_pairs = data.get('training_pairs', [])
        
        logger.info(f"Dataset info:")
        logger.info(f"  • Total pairs: {len(training_pairs)}")
        logger.info(f"  • Collections: {', '.join(metadata.get('collections', []))}")
        
        # Convert to InputExample format
        training_examples = []
        
        for pair in training_pairs:
            query = pair['query']
            positive_doc = pair['positive']['text']
            
            # Add positive pair
            training_examples.append(
                InputExample(texts=[query, positive_doc], label=1.0)
            )
            
            # Add negative pairs
            for neg_doc_info in pair['negatives'][:3]:  # Use top 3 negatives
                neg_doc = neg_doc_info['text']
                training_examples.append(
                    InputExample(texts=[query, neg_doc], label=0.0)
                )
        
        logger.info(f"Created {len(training_examples)} training examples")
        logger.info(f"  • Positive pairs: ~{len(training_pairs)}")
        logger.info(f"  • Negative pairs: ~{len(training_examples) - len(training_pairs)}")
        
        return training_examples
    
    def create_evaluation_set(self, examples: List[InputExample]) -> InformationRetrievalEvaluator:
        """
        Create evaluation set from training examples.
        
        Uses 20% of data for evaluation.
        """
        # Split: 80% train, 20% eval
        split_idx = int(0.8 * len(examples))
        eval_examples = examples[split_idx:]
        
        logger.info(f"\nCreating evaluation set from {len(eval_examples)} examples")
        
        # Convert to evaluation format
        queries = {}
        corpus = {}
        relevant_docs = {}
        
        query_id = 0
        doc_id = 0
        query_to_id = {}
        
        for example in eval_examples:
            q_text, doc_text = example.texts
            label = example.label
            
            # Add query (avoid duplicates)
            if q_text not in query_to_id:
                q_key = f"q{query_id}"
                queries[q_key] = q_text
                query_to_id[q_text] = q_key
                query_id += 1
            else:
                q_key = query_to_id[q_text]
            
            # Add document
            d_key = f"d{doc_id}"
            corpus[d_key] = doc_text
            doc_id += 1
            
            # Mark as relevant if positive
            if label > 0.5:
                if q_key not in relevant_docs:
                    relevant_docs[q_key] = set()
                relevant_docs[q_key].add(d_key)
        
        logger.info(f"Evaluation set: {len(queries)} unique queries, {len(corpus)} documents")
        
        return InformationRetrievalEvaluator(
            queries=queries,
            corpus=corpus,
            relevant_docs=relevant_docs,
            name='fin_e5_eval',
            show_progress_bar=True
        )
    
    def train(self,
              epochs: int = 4,
              batch_size: int = 16,
              warmup_steps: int = 500,
              max_seq_length: int = 512):
        """
        Train Fin-E5 model.
        
        Args:
            epochs: Number of training epochs
            batch_size: Training batch size (16 for E5 on 6GB GPU)
            warmup_steps: Learning rate warmup steps
            max_seq_length: Maximum sequence length
        """
        logger.info("\n" + "=" * 70)
        logger.info("STARTING FIN-E5 TRAINING")
        logger.info("=" * 70)
        
        # Load base E5 model
        logger.info(f"\nLoading base model: {self.base_model_name}")
        logger.info("This may take a few minutes for first download...")
        
        self.model = SentenceTransformer(self.base_model_name, device=self.device)
        self.model.max_seq_length = max_seq_length
        
        logger.info(f"✓ Model loaded")
        logger.info(f"  • Dimensions: {self.model.get_sentence_embedding_dimension()}")
        logger.info(f"  • Max sequence length: {self.model.max_seq_length}")
        
        # Load training data
        training_examples = self.load_training_data()
        
        # Split train/eval
        split_idx = int(0.8 * len(training_examples))
        train_examples = training_examples[:split_idx]
        
        logger.info(f"\nDataset split:")
        logger.info(f"  • Training: {len(train_examples)} examples")
        logger.info(f"  • Evaluation: {len(training_examples) - split_idx} examples")
        
        # Create data loader
        train_dataloader = DataLoader(
            train_examples,
            batch_size=batch_size,
            shuffle=True
        )
        
        # Define loss function
        # MultipleNegativesRankingLoss is optimal for retrieval
        train_loss = losses.MultipleNegativesRankingLoss(self.model)
        
        # Create evaluator
        evaluator = self.create_evaluation_set(training_examples)
        
        # Check GPU memory
        if torch.cuda.is_available():
            gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info(f"\nGPU Memory:")
            logger.info(f"  • Total: {gpu_mem:.2f} GB")
            logger.info(f"  • Required (estimated): {self._estimate_memory_requirement(batch_size):.2f} GB")
            if gpu_mem < 6.0:
                logger.warning(f"  ⚠️  Low GPU memory! Consider --batch-size 8")
        
        # Training configuration
        logger.info(f"\nTraining configuration:")
        logger.info(f"  • Epochs: {epochs}")
        logger.info(f"  • Batch size: {batch_size}")
        logger.info(f"  • Warmup steps: {warmup_steps}")
        logger.info(f"  • Device: {self.device}")
        logger.info(f"  • Loss: MultipleNegativesRankingLoss")
        logger.info(f"  • Max seq length: {max_seq_length}")
        
        # Estimate training time
        steps_per_epoch = len(train_dataloader)
        total_steps = steps_per_epoch * epochs
        logger.info(f"\nTraining steps:")
        logger.info(f"  • Steps per epoch: {steps_per_epoch}")
        logger.info(f"  • Total steps: {total_steps}")
        logger.info(f"  • Estimated time: {total_steps * 0.5 / 60:.1f}-{total_steps * 1.0 / 60:.1f} minutes")
        
        logger.info(f"\n" + "=" * 70)
        logger.info("TRAINING STARTED - This will take several hours")
        logger.info("=" * 70)
        
        # Train
        self.model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=epochs,
            warmup_steps=warmup_steps,
            output_path=str(self.output_dir),
            evaluation_steps=500,  # Evaluate every 500 steps
            evaluator=evaluator,
            show_progress_bar=True,
            save_best_model=True,
            checkpoint_path=str(self.output_dir / 'checkpoints'),
            checkpoint_save_steps=1000
        )
        
        logger.info("\n" + "=" * 70)
        logger.info("✓ TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Model saved to: {self.output_dir}")
        
        # Save training metadata
        training_info = {
            'base_model': self.base_model_name,
            'output_model': 'fin-e5',
            'training_date': datetime.now().isoformat(),
            'epochs': epochs,
            'batch_size': batch_size,
            'warmup_steps': warmup_steps,
            'max_seq_length': max_seq_length,
            'num_training_examples': len(train_examples),
            'device': str(self.device),
            'model_dimension': self.model.get_sentence_embedding_dimension()
        }
        
        with open(self.output_dir / 'training_info.json', 'w') as f:
            json.dump(training_info, f, indent=2)
        
        logger.info(f"Training metadata saved")
        logger.info("=" * 70)
    
    def evaluate(self):
        """Evaluate trained Fin-E5 model."""
        logger.info("\n" + "=" * 70)
        logger.info("EVALUATING FIN-E5 MODEL")
        logger.info("=" * 70)
        
        if not self.output_dir.exists():
            raise FileNotFoundError(f"Fin-E5 model not found: {self.output_dir}")
        
        logger.info(f"Loading Fin-E5 from {self.output_dir}")
        self.model = SentenceTransformer(str(self.output_dir), device=self.device)
        
        # Load training data for evaluation
        training_examples = self.load_training_data()
        
        # Use last 20% as test set
        split_idx = int(0.8 * len(training_examples))
        test_examples = training_examples[split_idx:]
        
        # Create evaluator
        evaluator = self.create_evaluation_set(test_examples)
        
        logger.info("\nRunning evaluation...")
        scores = evaluator(self.model)
        
        logger.info("\nEvaluation Results:")
        logger.info("=" * 70)
        for metric, score in sorted(scores.items()):
            logger.info(f"  {metric}: {score:.4f}")
        logger.info("=" * 70)
        
        # Save results
        results = {
            'evaluation_date': datetime.now().isoformat(),
            'model_path': str(self.output_dir),
            'scores': scores
        }
        
        results_file = self.output_dir / 'evaluation_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\nResults saved to: {results_file}")
    
    def export_for_deployment(self):
        """Export Fin-E5 for production deployment."""
        logger.info("\n" + "=" * 70)
        logger.info("EXPORTING FIN-E5 FOR DEPLOYMENT")
        logger.info("=" * 70)
        
        if not self.output_dir.exists():
            raise FileNotFoundError(f"Fin-E5 model not found: {self.output_dir}")
        
        # Load model
        logger.info(f"Loading Fin-E5 from {self.output_dir}")
        model = SentenceTransformer(str(self.output_dir))
        
        # Export directory
        export_dir = Path("./models/deployed/fin-e5-v1")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        logger.info(f"Exporting to {export_dir}")
        model.save(str(export_dir))
        
        # Create deployment guide
        deployment_info = {
            'model_name': 'fin-e5-v1',
            'base_model': 'intfloat/e5-base-v2',
            'export_date': datetime.now().isoformat(),
            'dimensions': model.get_sentence_embedding_dimension(),
            'max_seq_length': model.max_seq_length,
            'usage': {
                'load': f"model = SentenceTransformer('{export_dir}')",
                'encode': "embeddings = model.encode(['your queries'])",
                'integration': f"""
# Update src/core/advanced_rag_engine.py line ~97:
# OLD: self.embedding_model = SentenceTransformer('all-MiniLM-L12-v2', device=self.device)
# NEW: self.embedding_model = SentenceTransformer('{export_dir}', device=self.device)
"""
            },
            'next_steps': [
                "1. Update code to use Fin-E5",
                "2. Rebuild ChromaDB with new embeddings (REQUIRED!):",
                "   python rebuild_sebi_chromadb.py",
                "3. Test system",
                "4. Compare metrics with baseline"
            ]
        }
        
        with open(export_dir / 'deployment_info.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        logger.info("✓ Fin-E5 exported successfully")
        logger.info(f"✓ Location: {export_dir}")
        logger.info("\n" + "=" * 70)
        logger.info("DEPLOYMENT INSTRUCTIONS")
        logger.info("=" * 70)
        logger.info("\n1. Update your code:")
        logger.info(f"   Edit src/core/advanced_rag_engine.py line ~97:")
        logger.info(f"   self.embedding_model = SentenceTransformer('{export_dir}', device=self.device)")
        logger.info("\n2. Rebuild ChromaDB (CRITICAL!):")
        logger.info("   python rebuild_sebi_chromadb.py")
        logger.info("   (This rebuilds all embeddings with Fin-E5)")
        logger.info("\n3. Test the system:")
        logger.info("   python scripts/measure_baseline_performance.py")
        logger.info("\n4. Compare results:")
        logger.info("   python scripts/compare_model_performance.py \\")
        logger.info("       baseline_metrics_results.json \\")
        logger.info("       fin_e5_metrics_results.json")
        logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Fine-tune E5 model for financial domain")
    
    # Actions
    parser.add_argument('--train', action='store_true',
                       help='Train Fin-E5 model')
    parser.add_argument('--evaluate', action='store_true',
                       help='Evaluate trained Fin-E5')
    parser.add_argument('--export', action='store_true',
                       help='Export for production deployment')
    
    # Training parameters
    parser.add_argument('--data', type=str,
                       default='./data/finetuning/e5_training_data.json',
                       help='Path to training data')
    parser.add_argument('--epochs', type=int, default=4,
                       help='Number of epochs (default: 4)')
    parser.add_argument('--batch-size', type=int, default=16,
                       help='Batch size (default: 16 for E5)')
    parser.add_argument('--warmup-steps', type=int, default=500,
                       help='Warmup steps (default: 500)')
    parser.add_argument('--max-seq-length', type=int, default=512,
                       help='Max sequence length (default: 512)')
    
    # Model parameters
    parser.add_argument('--base-model', type=str,
                       default='intfloat/e5-base-v2',
                       help='Base E5 model')
    parser.add_argument('--output-dir', type=str,
                       default='./models/fin-e5',
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Initialize fine-tuner
    finetuner = E5FineTuner(
        base_model=args.base_model,
        training_data_file=args.data,
        output_dir=args.output_dir
    )
    
    # Execute actions
    if args.train:
        finetuner.train(
            epochs=args.epochs,
            batch_size=args.batch_size,
            warmup_steps=args.warmup_steps,
            max_seq_length=args.max_seq_length
        )
    
    if args.evaluate:
        finetuner.evaluate()
    
    if args.export:
        finetuner.export_for_deployment()
    
    if not (args.train or args.evaluate or args.export):
        parser.print_help()
        print("\n" + "=" * 70)
        print("EXAMPLE USAGE")
        print("=" * 70)
        print("\n1. Generate training data first:")
        print("   python scripts/generate_training_data.py")
        print("\n2. Train Fin-E5:")
        print("   python scripts/finetune_e5_model.py --train")
        print("\n3. Evaluate:")
        print("   python scripts/finetune_e5_model.py --evaluate")
        print("\n4. Export for production:")
        print("   python scripts/finetune_e5_model.py --export")
        print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

