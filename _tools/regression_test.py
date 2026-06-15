
"""
LF Academy Regression Test Suite v1.0
Based on: Shiplight AI Regression + LMS KPIs (Thirst/Totara) + Khan Academy A/B
Features: risk-based prioritization, trend tracking, KPI dashboard, self-baselining
"""
import sys, io, os, re, json, time, argparse
from datetime import datetime
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'G:\lam-fung-academy\講義'
TOOLS = r'G:\lam-fung-academy\_tools'

# Risk weights
RISK = {
    'CRITICAL': 3,  # Visible AI markers, broken HTML
    'HIGH': 2,       # Missing MathJax, broken SVGs
    'MEDIUM': 1,     # Missing WHYBOX, learning objectives
    'LOW': 0,        # Cosmetic issues
}

def collect_all_metrics():
    metrics = {}
    for grade in ['P3','P4','P5','P6']:
        gd = os.path.join(BASE, grade)
        for root, dirs, files in os.walk(gd):
            for f in files:
                if not f.endswith('.html') or 'index' in f.lower(): continue
                fp = os.path.join(root, f)
                for enc in ['utf-8','utf-8-sig','latin-1']:
                    try:
                        with open(fp, 'r', encoding=enc) as fh: c = fh.read()
                        break
                    except: continue
                
                rel = os.path.relpath(fp, BASE)
                visible = re.sub(r'<!--.*?-->', '', c, flags=re.DOTALL)
                
                m = {
                    'grade': grade,
                    'size_kb': round(len(c)/1024, 1),
                    'div_ok': len(re.findall(r'<div[\s>]', c)) == len(re.findall(r'</div>', c)),
                    'mathjax': 'MathJax' in c,
                    'frac_ok': not (r'\frac' in c and 'mathjax' not in c.lower()),
                    'svg_refs_ok': True,  # checked below
                    'no_visible_ai': '🤖' not in visible,
                    'has_whybox': 'WHY BOX' in c,
                    'has_learning_obj': '學習目標' in c or 'Learning Objective' in c,
                    'has_sspa': 'SSPA' in c,
                    'has_story': '故事情境' in c,
                    'has_provenance': 'AI-enhanced' in c,
                }
                
                # Check SVG refs
                svg_refs = re.findall(r'src="([^"]*\.svg)"', c)
                svg_dir = os.path.join(BASE, '_svg')
                for ref in svg_refs:
                    svg_name = os.path.basename(ref)
                    if not os.path.exists(os.path.join(svg_dir, svg_name)):
                        m['svg_refs_ok'] = False
                        break
                
                metrics[rel] = m
    return metrics

def run_regression(baseline_path=None):
    current = collect_all_metrics()
    
    # Load baseline if exists
    baseline = None
    if baseline_path and os.path.exists(baseline_path):
        with open(baseline_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            baseline = {k: v for k, v in data.get('metrics', {}).items()}
    
    # Score each file
    results = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': [], 'PASS': []}
    scores = defaultdict(int)
    
    for rel, m in current.items():
        issues = []
        
        if not m['no_visible_ai']:
            issues.append(('CRITICAL', 'VISIBLE_AI'))
        if not m['div_ok']:
            issues.append(('CRITICAL', 'DIV_IMBALANCE'))
        if not m['frac_ok']:
            issues.append(('HIGH', 'FRAC_NO_MATHJAX'))
        if not m['svg_refs_ok']:
            issues.append(('HIGH', 'BROKEN_SVG'))
        if not m['has_whybox']:
            issues.append(('MEDIUM', 'NO_WHYBOX'))
        if not m['has_learning_obj']:
            issues.append(('MEDIUM', 'NO_LEARNING_OBJ'))
        
        if not issues:
            results['PASS'].append(rel)
        else:
            max_risk = max(RISK[i[0]] for i in issues)
            for risk_level, _ in issues:
                results[risk_level].append(rel)
            scores[m['grade']] += max_risk
    
    # KPI Dashboard
    total = len(current)
    passing = len(results['PASS'])
    
    print('=' * 60)
    print('  LF Academy Regression Test Suite')
    print('  Time: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('=' * 60)
    print('')
    
    # Risk summary
    print('--- Risk-Based Results ---')
    for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        count = len(results[level])
        icon = '🔴' if count > 0 else '🟢'
        print(icon + ' ' + level + ': ' + str(count) + ' files')
    print('🟢 PASS: ' + str(passing) + '/' + str(total) + ' (' + str(round(passing/total*100)) + '%)')
    
    # KPI Dashboard
    print('')
    print('--- KPI Dashboard ---')
    kpis = {
        '結構完整性': round(sum(1 for m in current.values() if m['div_ok'])/total*100),
        '數學渲染': round(sum(1 for m in current.values() if m['frac_ok'])/total*100),
        '無可見AI': round(sum(1 for m in current.values() if m['no_visible_ai'])/total*100),
        'WHY BOX': round(sum(1 for m in current.values() if m['has_whybox'])/total*100),
        '學習目標': round(sum(1 for m in current.values() if m['has_learning_obj'])/total*100),
        'SSPA標記': round(sum(1 for m in current.values() if m['has_sspa'])/total*100),
        '故事情境': round(sum(1 for m in current.values() if m['has_story'])/total*100),
        'AI來源': round(sum(1 for m in current.values() if m['has_provenance'])/total*100),
    }
    
    for kpi, value in kpis.items():
        bar = '█' * (value // 10) + '░' * (10 - value // 10)
        status = '✅' if value >= 90 else ('⚠️' if value >= 70 else '❌')
        print(status + ' ' + kpi.ljust(8) + ': ' + str(value).rjust(3) + '% ' + bar)
    
    # Per-grade risk score (lower is better)
    print('')
    print('--- Per-Grade Risk Score (lower=better) ---')
    for grade in ['P3','P4','P5','P6']:
        gfiles = sum(1 for m in current.values() if m['grade'] == grade)
        gscore = scores.get(grade, 0)
        avg_risk = round(gscore / gfiles, 2) if gfiles > 0 else 0
        print('  ' + grade + ': score=' + str(gscore) + ' | avg_risk=' + str(avg_risk) + ' | files=' + str(gfiles))
    
    # Trend vs baseline
    if baseline:
        print('')
        print('--- Trend vs Baseline ---')
        for kpi in ['div_ok', 'frac_ok', 'no_visible_ai', 'has_whybox', 'has_learning_obj']:
            curr_val = round(sum(1 for m in current.values() if m[kpi])/total*100)
            base_val = round(sum(1 for m in baseline.values() if m.get(kpi, False))/len(baseline)*100) if baseline else 0
            delta = curr_val - base_val
            sign = '+' if delta >= 0 else ''
            print('  ' + kpi + ': ' + str(base_val) + '% -> ' + str(curr_val) + '% (' + sign + str(delta) + 'pp)')
    
    # Save current as baseline
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    snapshot = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_files': total,
        'passing': passing,
        'passing_pct': round(passing/total*100),
        'kpis': kpis,
        'risk_summary': {k: len(v) for k, v in results.items()},
        'metrics': {k: v for k, v in current.items()}
    }
    
    snapshot_path = os.path.join(TOOLS, 'regression_' + timestamp + '.json')
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    
    # Update latest pointer
    latest_path = os.path.join(TOOLS, 'regression_latest.json')
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    
    print('')
    print('Snapshot saved: regression_' + timestamp + '.json')
    print('Latest: regression_latest.json')
    
    # Exit code
    critical_count = len(results['CRITICAL'])
    return critical_count == 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', type=str, default=None)
    args = parser.parse_args()
    ok = run_regression(args.baseline)
    sys.exit(0 if ok else 1)
