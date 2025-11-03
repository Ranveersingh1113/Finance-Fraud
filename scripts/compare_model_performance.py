"""
Compare baseline vs fine-tuned model performance.

Usage:
    python scripts/compare_model_performance.py baseline.json finetuned.json
"""

import json
import sys
from typing import Dict, Any


def load_results(filepath: str) -> Dict[str, Any]:
    """Load results from JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {filepath}")
        sys.exit(1)


def calculate_improvement(baseline: float, finetuned: float) -> tuple:
    """Calculate absolute and relative improvement."""
    absolute = finetuned - baseline
    relative = (absolute / baseline * 100) if baseline > 0 else 0
    return absolute, relative


def print_comparison(baseline_data: Dict, finetuned_data: Dict):
    """Print detailed comparison."""
    print("\n" + "=" * 80)
    print("MODEL PERFORMANCE COMPARISON")
    print("=" * 80)
    
    baseline_summary = baseline_data.get('summary', {})
    finetuned_summary = finetuned_data.get('summary', {})
    
    # Precision comparison
    baseline_prec = baseline_summary.get('avg_precision_at_10', 0)
    finetuned_prec = finetuned_summary.get('avg_precision_at_10', 0)
    prec_abs, prec_rel = calculate_improvement(baseline_prec, finetuned_prec)
    
    print("\n📊 PRECISION@10")
    print(f"  Baseline:   {baseline_prec:.3f}")
    print(f"  Fine-tuned: {finetuned_prec:.3f}")
    print(f"  Change:     {prec_abs:+.3f} ({prec_rel:+.1f}%)")
    
    if prec_rel > 10:
        print(f"  ✅ SIGNIFICANT IMPROVEMENT")
    elif prec_rel > 5:
        print(f"  ⚡ MODERATE IMPROVEMENT")
    elif prec_rel > 0:
        print(f"  🟡 SLIGHT IMPROVEMENT")
    else:
        print(f"  ❌ NO IMPROVEMENT - May need different approach")
    
    # MRR comparison
    baseline_mrr = baseline_summary.get('avg_mrr', 0)
    finetuned_mrr = finetuned_summary.get('avg_mrr', 0)
    mrr_abs, mrr_rel = calculate_improvement(baseline_mrr, finetuned_mrr)
    
    print("\n📊 MEAN RECIPROCAL RANK (MRR)")
    print(f"  Baseline:   {baseline_mrr:.3f}")
    print(f"  Fine-tuned: {finetuned_mrr:.3f}")
    print(f"  Change:     {mrr_abs:+.3f} ({mrr_rel:+.1f}%)")
    
    # Latency comparison
    baseline_latency = baseline_summary.get('latency_stats', {}).get('mean', 0)
    finetuned_latency = finetuned_summary.get('latency_stats', {}).get('mean', 0)
    
    if baseline_latency > 0 and finetuned_latency > 0:
        latency_abs = finetuned_latency - baseline_latency
        latency_rel = (latency_abs / baseline_latency * 100)
        
        print("\n⚡ LATENCY")
        print(f"  Baseline:   {baseline_latency:.2f}s")
        print(f"  Fine-tuned: {finetuned_latency:.2f}s")
        print(f"  Change:     {latency_abs:+.2f}s ({latency_rel:+.1f}%)")
        
        if latency_rel < -10:
            print(f"  ⚠️ WARNING: Significant slowdown")
        elif latency_rel > 10:
            print(f"  ⚠️ WARNING: Unexpected speedup (check config)")
    
    # Per-query comparison
    print("\n" + "=" * 80)
    print("PER-QUERY BREAKDOWN")
    print("=" * 80)
    
    baseline_details = baseline_data.get('detailed_results', [])
    finetuned_details = finetuned_data.get('detailed_results', [])
    
    if len(baseline_details) == len(finetuned_details):
        print(f"\n{'Query':<50} {'Baseline':<12} {'Fine-tuned':<12} {'Change':<10}")
        print("-" * 84)
        
        for i, (base, ft) in enumerate(zip(baseline_details, finetuned_details)):
            query = base.get('query', '')[:47] + "..."
            base_prec = base.get('precision', 0)
            ft_prec = ft.get('precision', 0)
            change = ft_prec - base_prec
            change_str = f"{change:+.2f}"
            
            emoji = "✅" if change > 0.1 else "⚡" if change > 0 else "🟡" if change == 0 else "❌"
            print(f"{query:<50} {base_prec:<12.3f} {ft_prec:<12.3f} {change_str:<10} {emoji}")
    
    # Overall recommendation
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    if prec_rel > 15:
        print("\n✅ EXCELLENT RESULTS")
        print("   → Fine-tuning provided significant improvement")
        print("   → Deploy fine-tuned model to production")
        print("   → Consider fine-tuning reranker next for further gains")
    elif prec_rel > 10:
        print("\n⚡ GOOD RESULTS")
        print("   → Fine-tuning helped noticeably")
        print("   → Deploy fine-tuned model to production")
        print("   → Monitor user feedback for further improvements")
    elif prec_rel > 5:
        print("\n🟡 MODERATE RESULTS")
        print("   → Some improvement, but may not justify complexity")
        print("   → Consider A/B testing before full deployment")
        print("   → Investigate if more training data would help")
    else:
        print("\n❌ INSUFFICIENT IMPROVEMENT")
        print("   → Fine-tuning did not help significantly")
        print("   → Possible issues:")
        print("      • Not enough training data")
        print("      • Training data not representative")
        print("      • Model architecture not suitable")
        print("   → Try: Reranker fine-tuning or hybrid search (BM25 + semantic)")
    
    # Cost-benefit analysis
    print("\n" + "=" * 80)
    print("COST-BENEFIT ANALYSIS")
    print("=" * 80)
    
    queries_per_day = 1000  # Estimate
    seconds_saved_per_query = 10 * prec_abs  # Assume 10s per irrelevant doc avoided
    hours_saved_per_day = (queries_per_day * seconds_saved_per_query) / 3600
    
    print(f"\nAssuming {queries_per_day} queries/day:")
    print(f"  • Precision improvement: {prec_rel:.1f}%")
    print(f"  • Irrelevant docs avoided per query: ~{prec_abs * 10:.1f}")
    print(f"  • User time saved per day: ~{hours_saved_per_day:.1f} hours")
    print(f"  • Monthly impact: ~{hours_saved_per_day * 30:.0f} hours")
    
    print("\n" + "=" * 80)


def main():
    """Main comparison function."""
    if len(sys.argv) != 3:
        print("Usage: python scripts/compare_model_performance.py baseline.json finetuned.json")
        sys.exit(1)
    
    baseline_file = sys.argv[1]
    finetuned_file = sys.argv[2]
    
    print(f"\n📂 Loading baseline results from: {baseline_file}")
    baseline_data = load_results(baseline_file)
    
    print(f"📂 Loading fine-tuned results from: {finetuned_file}")
    finetuned_data = load_results(finetuned_file)
    
    print_comparison(baseline_data, finetuned_data)
    
    print("\n✅ Comparison complete!\n")


if __name__ == "__main__":
    main()

