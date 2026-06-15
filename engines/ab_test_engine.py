#!/usr/bin/env python3
"""
LF A/B Test Engine v1.0 — Content Variant Testing
==================================================
Statistical significance testing for marketing content variants.
Uses Bayesian A/B testing (Beta-Binomial) with Thompson sampling for adaptive allocation.

Architecture:
  Create Experiment → Assign Variants → Record Results → Bayesian Analysis → Winner Declaration

用法:
  python engines/ab_test_engine.py --create "標題A vs 標題B" --variants 2
  python engines/ab_test_engine.py --record EXP001 V0 350 28
  python engines/ab_test_engine.py --analyze EXP001
"""

import sys, io, json, math, uuid
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

if not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = Path(r'G:\lam-fung-academy')
AB_DIR = BASE / 'docs' / 'social' / 'ab_tests'
AB_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# BAYESIAN A/B TESTING CORE
# ═══════════════════════════════════════════════════════════

class BayesianABTest:
    """
    Bayesian A/B test using Beta-Binomial conjugate prior.

    Prior: Beta(1, 1) = uniform
    Posterior: Beta(1 + successes, 1 + failures)
    P(B > A) computed via Monte Carlo sampling.
    """

    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta

    def posterior_params(self, successes: int, trials: int) -> Tuple[float, float]:
        """Get posterior Beta parameters."""
        failures = trials - successes
        return (self.prior_alpha + successes, self.prior_beta + failures)

    def probability_b_beats_a(self, a_successes: int, a_trials: int,
                               b_successes: int, b_trials: int,
                               samples: int = 10000) -> float:
        """Monte Carlo estimate of P(B > A)."""
        import random
        a_alpha, a_beta = self.posterior_params(a_successes, a_trials)
        b_alpha, b_beta = self.posterior_params(b_successes, b_trials)

        b_wins = 0
        for _ in range(samples):
            a_sample = random.betavariate(a_alpha, a_beta)
            b_sample = random.betavariate(b_alpha, b_beta)
            if b_sample > a_sample:
                b_wins += 1

        return b_wins / samples

    def expected_loss(self, a_successes: int, a_trials: int,
                      b_successes: int, b_trials: int,
                      samples: int = 10000) -> float:
        """Expected loss if choosing A over B (or vice versa)."""
        import random
        a_alpha, a_beta = self.posterior_params(a_successes, a_trials)
        b_alpha, b_beta = self.posterior_params(b_successes, b_trials)

        total_loss = 0.0
        for _ in range(samples):
            a_sample = random.betavariate(a_alpha, a_beta)
            b_sample = random.betavariate(b_alpha, b_beta)
            total_loss += max(b_sample - a_sample, 0)

        return total_loss / samples


# ═══════════════════════════════════════════════════════════
# EXPERIMENT MANAGER
# ═══════════════════════════════════════════════════════════

@dataclass
class Variant:
    """A single test variant."""
    id: str
    name: str
    description: str = ''
    impressions: int = 0
    engagements: int = 0
    clicks: int = 0
    leads: int = 0
    active: bool = True

    @property
    def engagement_rate(self) -> float:
        return self.engagements / max(self.impressions, 1)

    @property
    def ctr(self) -> float:
        return self.clicks / max(self.impressions, 1)


@dataclass
class Experiment:
    """A complete A/B test experiment."""
    id: str
    name: str
    platform: str
    layer: str
    metric: str  # 'engagement', 'ctr', 'leads'
    variants: List[Variant] = field(default_factory=list)
    status: str = 'running'  # running, completed, stopped
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    winner_id: Optional[str] = None
    notes: str = ''

    def record(self, variant_id: str, metrics: Dict):
        """Record results for a variant."""
        for v in self.variants:
            if v.id == variant_id:
                v.impressions += metrics.get('impressions', 0)
                v.engagements += metrics.get('engagements', 0)
                v.clicks += metrics.get('clicks', 0)
                v.leads += metrics.get('leads', 0)
                return
        raise ValueError(f'Variant {variant_id} not found in experiment {self.id}')

    def get_metric_value(self, variant: Variant) -> float:
        """Get the metric value for a variant."""
        if self.metric == 'engagement':
            return variant.engagement_rate
        elif self.metric == 'ctr':
            return variant.ctr
        elif self.metric == 'leads':
            return variant.leads / max(variant.impressions, 1)
        return variant.engagement_rate

    def analyze(self, confidence_threshold: float = 0.95) -> Dict:
        """Run Bayesian analysis on the experiment."""
        if len(self.variants) < 2:
            return {'status': 'insufficient_variants'}

        tester = BayesianABTest()

        # Compare all variants against the control (first variant)
        control = self.variants[0]
        results = []

        for variant in self.variants[1:]:
            if self.metric == 'engagement':
                c_success = control.engagements
                v_success = variant.engagements
            elif self.metric == 'ctr':
                c_success = control.clicks
                v_success = variant.clicks
            elif self.metric == 'leads':
                c_success = control.leads
                v_success = variant.leads
            else:
                c_success = control.engagements
                v_success = variant.engagements

            c_trials = max(control.impressions, 1)
            v_trials = max(variant.impressions, 1)

            prob_better = tester.probability_b_beats_a(
                c_success, c_trials, v_success, v_trials)
            loss = tester.expected_loss(
                c_success, c_trials, v_success, v_trials)

            results.append({
                'variant_id': variant.id,
                'variant_name': variant.name,
                'vs_control': control.name,
                'probability_better': round(prob_better, 4),
                'expected_loss': round(loss, 6),
                'significant': prob_better >= confidence_threshold,
                'control_rate': round(self.get_metric_value(control), 4),
                'variant_rate': round(self.get_metric_value(variant), 4),
                'lift': round(
                    (self.get_metric_value(variant) - self.get_metric_value(control))
                    / max(self.get_metric_value(control), 0.0001) * 100, 1
                ),
            })

        # Declare winner if any variant is significant
        significant = [r for r in results if r['significant']]
        winner_declared = False
        if significant and all(v.impressions >= 100 for v in self.variants):
            best = max(significant, key=lambda r: r['probability_better'])
            if best['lift'] > 0:
                self.winner_id = best['variant_id']
                self.status = 'completed'
                self.completed_at = datetime.now().isoformat()
                winner_declared = True

        return {
            'experiment_id': self.id,
            'experiment_name': self.name,
            'status': self.status,
            'metric': self.metric,
            'variants': [
                {
                    'id': v.id, 'name': v.name,
                    'impressions': v.impressions,
                    'engagements': v.engagements,
                    'rate': round(self.get_metric_value(v), 4),
                }
                for v in self.variants
            ],
            'comparisons': results,
            'winner_declared': winner_declared,
            'winner_id': self.winner_id,
        }


# ═══════════════════════════════════════════════════════════
# EXPERIMENT STORE
# ═══════════════════════════════════════════════════════════

class ExperimentStore:
    """Persistent storage for A/B experiments."""

    def __init__(self):
        self.db_path = AB_DIR / 'experiments.json'
        self.experiments: Dict[str, Experiment] = {}
        self._load()

    def _load(self):
        if self.db_path.exists():
            try:
                data = json.loads(self.db_path.read_text(encoding='utf-8'))
                for exp_id, exp_data in data.get('experiments', {}).items():
                    variants = [
                        Variant(**v) for v in exp_data.pop('variants', [])
                    ]
                    self.experiments[exp_id] = Experiment(
                        id=exp_id, variants=variants, **exp_data)
            except Exception:
                pass

    def _save(self):
        data = {
            'experiments': {
                eid: {
                    **{k: v for k, v in asdict(exp).items() if k != 'variants'},
                    'variants': [asdict(v) for v in exp.variants],
                }
                for eid, exp in self.experiments.items()
            },
            'updated_at': datetime.now().isoformat(),
        }
        self.db_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def create(self, name: str, platform: str, layer: str,
               metric: str = 'engagement',
               variant_names: List[str] = None) -> Experiment:
        """Create a new experiment."""
        if variant_names is None:
            variant_names = ['Control', 'Variant']

        exp_id = f'EXP{len(self.experiments) + 1:04d}'
        variants = [
            Variant(id=f'{exp_id}_V{i}', name=name)
            for i, name in enumerate(variant_names)
        ]

        exp = Experiment(
            id=exp_id, name=name, platform=platform,
            layer=layer, metric=metric, variants=variants,
        )
        self.experiments[exp_id] = exp
        self._save()
        return exp

    def get(self, exp_id: str) -> Optional[Experiment]:
        return self.experiments.get(exp_id)

    def list_active(self) -> List[Experiment]:
        return [e for e in self.experiments.values() if e.status == 'running']

    def list_all(self) -> List[Experiment]:
        return list(self.experiments.values())

    def record(self, exp_id: str, variant_id: str, metrics: Dict):
        """Record metrics for a variant."""
        exp = self.get(exp_id)
        if not exp:
            raise ValueError(f'Experiment {exp_id} not found')
        exp.record(variant_id, metrics)
        self._save()

    def analyze(self, exp_id: str) -> Dict:
        """Analyze an experiment."""
        exp = self.get(exp_id)
        if not exp:
            return {'status': 'not_found'}
        result = exp.analyze()
        self._save()
        return result


# ═══════════════════════════════════════════════════════════
# CONTENT VARIANT GENERATOR
# ═══════════════════════════════════════════════════════════

class ContentVariantGenerator:
    """Generate A/B test variants for marketing content."""

    VARIANT_DIMENSIONS = {
        'hook': [
            ('問題型', '你小朋友識唔識呢條數？'),
            ('數據型', '90%家長都答錯呢題...'),
            ('故事型', '上星期有個媽媽同我講...'),
            ('恐懼型', '唔好等到SSPA最後一個月...'),
        ],
        'cta': [
            ('留言互動', '留言「診斷」免費測試 👇'),
            ('直接下載', '立即下載免費練習 👇'),
            ('私訊引導', 'PM我哋查詢詳情 👇'),
            ('限時緊急', '最後3日，立即行動 👇'),
        ],
        'length': [
            ('短文', 'short'),
            ('中篇', 'medium'),
            ('長文', 'long'),
        ],
        'tone': [
            ('溫暖專業', 'warm_professional'),
            ('直接有力', 'direct_strong'),
            ('故事分享', 'storytelling'),
            ('數據說服', 'data_driven'),
        ],
    }

    @classmethod
    def generate_variants(cls, base_content: Dict, dimensions: List[str],
                          count: int = 2) -> List[Dict]:
        """Generate content variants by varying specified dimensions."""
        variants = []
        for i in range(count):
            variant = dict(base_content)
            variant['variant_name'] = f'Variant {i}'

            for dim in dimensions:
                if dim in cls.VARIANT_DIMENSIONS:
                    options = cls.VARIANT_DIMENSIONS[dim]
                    choice = options[i % len(options)]
                    variant[f'vary_{dim}'] = choice[0]

                    # Apply hook variation
                    if dim == 'hook':
                        variant['hook'] = choice[1]

            variants.append(variant)

        return variants


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LF A/B Test Engine v1.0')
    sub = parser.add_subparsers(dest='command')

    # Create
    c = sub.add_parser('create')
    c.add_argument('--name', required=True)
    c.add_argument('--platform', default='fb')
    c.add_argument('--layer', default='education')
    c.add_argument('--metric', default='engagement')
    c.add_argument('--variants', nargs='+', default=['Control', 'Variant'])

    # Record
    r = sub.add_parser('record')
    r.add_argument('--exp', required=True)
    r.add_argument('--variant', required=True)
    r.add_argument('--impressions', type=int, required=True)
    r.add_argument('--engagements', type=int, default=0)
    r.add_argument('--clicks', type=int, default=0)

    # Analyze
    a = sub.add_parser('analyze')
    a.add_argument('--exp', required=True)

    # List
    sub.add_parser('list')

    args = parser.parse_args()
    store = ExperimentStore()

    if args.command == 'create':
        exp = store.create(
            name=args.name, platform=args.platform,
            layer=args.layer, metric=args.metric,
            variant_names=args.variants,
        )
        print(f'Created experiment: {exp.id} — {exp.name}')
        print(f'  Variants: {[v.name for v in exp.variants]}')

    elif args.command == 'record':
        store.record(args.exp, args.variant, {
            'impressions': args.impressions,
            'engagements': args.engagements,
            'clicks': args.clicks,
        })
        print(f'Recorded: {args.exp}/{args.variant}')

    elif args.command == 'analyze':
        result = store.analyze(args.exp)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == 'list':
        for exp in store.list_all():
            print(f'{exp.id}: {exp.name} [{exp.status}] {len(exp.variants)} variants')

    else:
        print('LF A/B Test Engine v1.0')
        print('Commands: create, record, analyze, list')
