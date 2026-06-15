#!/usr/bin/env python3
'''
LF Enrichment Engine v1.0 — AI智能講義系統核心
整合172講義enrichment數據，提供SSPA挑戰題、陷阱卡、思維提示、跨級參考
供 tutor_engine, mark_engine, hk_exam_engine 調用
'''
import sys, io, json, os, re
from pathlib import Path
from functools import lru_cache

try:
    if not isinstance(sys.stdout, io.TextIOWrapper) and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except: pass

BASE = Path(r'G:\lam-fung-academy')
HANDOUT_DIR = BASE / '講義'

class EnrichmentEngine:
    '''AI講義智能增強引擎'''
    
    def __init__(self):
        self._cache = {}
        self._index = self._build_index()
    
    def _build_index(self):
        '''建立全部 enrichment 索引'''
        index = {}
        for grade_dir in HANDOUT_DIR.iterdir():
            if not grade_dir.is_dir(): continue
            grade = grade_dir.name
            for f in grade_dir.iterdir():
                if not f.name.endswith('_enrichment.json'): continue
                lecture_id = f.name.replace('_enrichment.json', '')
                index[lecture_id] = {'grade': grade, 'path': str(f)}
        return index
    
    @lru_cache(maxsize=128)
    def load(self, lecture_id):
        '''載入指定講義的 enrichment'''
        if lecture_id not in self._index:
            return None
        fpath = self._index[lecture_id]['path']
        try:
            with open(fpath, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except:
            return None
    
    def get_traps(self, lecture_id, count=3):
        '''獲取陷阱卡（優先 advanced_traps，fallback traps）'''
        data = self.load(lecture_id)
        if not data: return []
        
        traps = data.get('advanced_traps', data.get('traps', []))
        if not traps: return []
        
        # Normalize format
        result = []
        for t in traps[:count]:
            if isinstance(t, dict):
                result.append({
                    'wrong': t.get('wrong', t.get('description', '')),
                    'why_wrong': t.get('why_wrong', ''),
                    'right': t.get('right', ''),
                    'note': t.get('note', '')
                })
        return result
    
    def get_challenges(self, lecture_id, count=3):
        '''獲取SSPA挑戰題'''
        data = self.load(lecture_id)
        if not data: return []
        
        challenges = data.get('sspa_challenges', data.get('challenge_questions', data.get('挑戰題', [])))
        if not challenges: return []
        
        result = []
        for c in challenges[:count]:
            if isinstance(c, dict):
                result.append({
                    'question': c.get('question', c.get('題目', '')),
                    'answer': c.get('answer', c.get('答案', '')),
                    'solution': c.get('solution', c.get('解析', '')),
                    'marks': c.get('marks', c.get('分數', 0))
                })
        return result
    
    def get_thinking_tip(self, lecture_id):
        '''獲取思維提示'''
        data = self.load(lecture_id)
        if not data: return ''
        
        tip = data.get('thinking_tip', data.get('思維提示', ''))
        if isinstance(tip, dict):
            tip = tip.get('description', tip.get('內容', str(tip)))
        return tip if isinstance(tip, str) else ''
    
    def get_cross_ref(self, lecture_id):
        '''獲取跨級參考'''
        data = self.load(lecture_id)
        if not data: return ''
        return data.get('cross_grade_ref', '')
    
    def get_enrichment_summary(self, lecture_id):
        '''獲取完整 enrichment 摘要（供AI提示詞使用）'''
        data = self.load(lecture_id)
        if not data: return {}
        
        return {
            'lecture_id': lecture_id,
            'grade': self._index.get(lecture_id, {}).get('grade', ''),
            'traps_count': len(data.get('advanced_traps', data.get('traps', []))),
            'challenges_count': len(data.get('sspa_challenges', data.get('challenge_questions', []))),
            'thinking_tip': self.get_thinking_tip(lecture_id),
            'cross_grade_ref': self.get_cross_ref(lecture_id),
            'sample_challenge': self.get_challenges(lecture_id, 1)[0] if self.get_challenges(lecture_id, 1) else None
        }
    
    def search_by_topic(self, keyword, grades=None):
        '''按關鍵詞搜索相關講義'''
        results = []
        target_grades = grades or ['P3', 'P4', 'P5', 'P6']
        
        for lecture_id, info in self._index.items():
            if info['grade'] not in target_grades:
                continue
            if keyword in lecture_id:
                data = self.load(lecture_id)
                if data:
                    results.append({
                        'lecture_id': lecture_id,
                        'grade': info['grade'],
                        'summary': self.get_enrichment_summary(lecture_id)
                    })
        return results
    
    def stats(self):
        '''統計信息'''
        grades = {}
        for lecture_id, info in self._index.items():
            g = info['grade']
            if g not in grades:
                grades[g] = {'total': 0, 'with_sspa': 0, 'with_traps': 0}
            grades[g]['total'] += 1
            
            data = self.load(lecture_id)
            if data:
                if data.get('sspa_challenges'):
                    grades[g]['with_sspa'] += 1
                if data.get('advanced_traps'):
                    grades[g]['with_traps'] += 1
        
        total_enr = sum(g['total'] for g in grades.values())
        return {
            'total_enrichments': total_enr,
            'grades': grades
        }

# CLI interface
if __name__ == '__main__':
    engine = EnrichmentEngine()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'stats':
            stats = engine.stats()
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        elif cmd == 'search' and len(sys.argv) > 2:
            results = engine.search_by_topic(sys.argv[2])
            for r in results:
                print(f"[{r['grade']}] {r['lecture_id']}")
        elif cmd == 'challenges' and len(sys.argv) > 2:
            challenges = engine.get_challenges(sys.argv[2])
            for i, c in enumerate(challenges):
                print(f"\nQ{i+1}: {c['question']}")
                print(f"A: {c['answer']}")
        elif cmd == 'traps' and len(sys.argv) > 2:
            traps = engine.get_traps(sys.argv[2])
            for i, t in enumerate(traps):
                print(f"\nTrap {i+1}:")
                print(f"  Wrong: {t['wrong'][:80]}...")
                print(f"  Right: {t['right'][:80]}...")
        elif cmd == 'summary' and len(sys.argv) > 2:
            summary = engine.get_enrichment_summary(sys.argv[2])
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            lecture_id = sys.argv[1]
            summary = engine.get_enrichment_summary(lecture_id)
            print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        stats = engine.stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))

print('EnrichmentEngine v1.0 loaded')
