#!/usr/bin/env python3
"""
LF Image Brief Engine v1.0 — Visual Content Spec Generator
===========================================================
Generates platform-optimized image briefs for AI image generation tools
(DALL-E, Midjourney, Stable Diffusion, Eachlabs, etc.)

Each brief includes: composition, colors, typography, dimensions, style guide.

用法:
  python engines/image_brief_engine.py --post "T4陷阱解密" --platform ig
  python engines/image_brief_engine.py --batch calendar.json --platforms fb,ig,xhs
  python engines/image_brief_engine.py --styles
"""

import sys, io, json, random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

if not isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = Path(r'G:\lam-fung-academy')
BRIEF_DIR = BASE / 'docs' / 'social' / 'image_briefs'
BRIEF_DIR.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════
# PLATFORM IMAGE SPECS
# ═══════════════════════════════════════════════════════════

PLATFORM_SPECS = {
    'fb': {
        'feed':      (1200, 630, '1.91:1', 'landscape'),
        'story':     (1080, 1920, '9:16', 'portrait'),
        'carousel':  (1080, 1080, '1:1', 'square'),
        'cover':     (1640, 856, '1.91:1', 'landscape'),
    },
    'ig': {
        'feed':      (1080, 1080, '1:1', 'square'),
        'story':     (1080, 1920, '9:16', 'portrait'),
        'reels':     (1080, 1920, '9:16', 'portrait'),
        'carousel':  (1080, 1080, '1:1', 'square'),
    },
    'xhs': {
        'feed':      (1080, 1440, '3:4', 'portrait'),
        'cover':     (1080, 1440, '3:4', 'portrait'),
        'carousel':  (1080, 1440, '3:4', 'portrait'),
    },
}

# ═══════════════════════════════════════════════════════════
# BRAND STYLE GUIDE
# ═══════════════════════════════════════════════════════════

BRAND = {
    'colors': {
        'primary':   '#1A3C6D',  # Deep navy blue
        'secondary': '#C9A84C',  # Gold
        'accent':    '#DC2626',  # Alert red (for traps/warnings)
        'success':   '#10B981',  # Green (for progress)
        'bg_light':  '#F3F4F6',  # Light gray background
        'bg_dark':   '#0F172A',  # Dark background
        'text':      '#1A1A1A',
        'text_light': '#F1F5F9',
    },
    'fonts': {
        'heading': 'Noto Serif HK Bold',
        'body':    'Noto Sans HK Regular',
        'accent':  'Noto Sans HK Bold',
        'fallback': 'system-ui, sans-serif',
    },
    'mascot': '數學陷阱偵探（放大鏡 + 問號）',
    'style': 'Clean, modern, Hong Kong edtech — warm but professional',
    'no_go': [
        '過度鮮艷的漸層', '誇張3D效果', '太多emoji',
        '卡通風格（除非是兒童向內容）', '純文字無圖形',
    ],
}

# ═══════════════════════════════════════════════════════════
# LAYER-SPECIFIC VISUAL STYLES
# ═══════════════════════════════════════════════════════════

LAYER_VISUALS = {
    'education': {
        'style': 'Clean infographic, chalkboard or notebook texture',
        'colors': [BRAND['colors']['primary'], '#FFFFFF', BRAND['colors']['accent']],
        'elements': ['math symbols', 'diagrams', 'step-by-step arrows', 'formulas'],
        'composition': 'Centered equation or diagram with explanatory labels',
        'prompt_keywords': 'infographic, educational, clean, organized, chalkboard style',
    },
    'social_proof': {
        'style': 'Before/after comparison, testimonial card',
        'colors': [BRAND['colors']['primary'], BRAND['colors']['secondary'], '#FFFFFF'],
        'elements': ['score comparison', 'student photo placeholder', 'progress bars', 'star ratings'],
        'composition': 'Split layout: left=before (dim), right=after (bright)',
        'prompt_keywords': 'testimonial, before after, progress, achievement, warm lighting',
    },
    'engagement': {
        'style': 'Bold quiz/poll design, gamified look',
        'colors': [BRAND['colors']['primary'], '#F59E0B', BRAND['colors']['accent']],
        'elements': ['question marks', 'A/B/C buttons', 'countdown timer', 'score reveal'],
        'composition': 'Large centered question with answer options below',
        'prompt_keywords': 'quiz, interactive, bold, gamified, question mark, playful',
    },
    'urgency': {
        'style': 'Countdown timer, calendar, high contrast',
        'colors': [BRAND['colors']['accent'], '#1A1A1A', '#FFFFFF'],
        'elements': ['countdown numbers', 'calendar pages', 'clock', 'alert badge', 'exclamation mark'],
        'composition': 'Large countdown number dominating the frame',
        'prompt_keywords': 'urgent, countdown, calendar, deadline, bold, attention-grabbing',
    },
    'personality': {
        'style': 'Warm, personal photo-style, behind-the-scenes',
        'colors': ['#FEF3C7', BRAND['colors']['primary'], '#374151'],
        'elements': ['teacher at desk', 'classroom setting', 'handwritten notes', 'coffee cup'],
        'composition': 'Natural, candid-style framing with warm tones',
        'prompt_keywords': 'authentic, warm, teacher, classroom, candid, personal story',
    },
    'reels': {
        'style': 'Bold thumbnail with text overlay, YouTube-style',
        'colors': [BRAND['colors']['primary'], '#EC4899', '#FFFFFF'],
        'elements': ['play button', 'arrow', 'text overlay', 'reaction face', 'bold title'],
        'composition': 'Central focal point with large text overlay, high contrast',
        'prompt_keywords': 'thumbnail, bold text, youtube style, high contrast, eye-catching',
    },
    'differentiation': {
        'style': 'Comparison table, side-by-side, clean corporate',
        'colors': [BRAND['colors']['primary'], '#EF4444', '#10B981'],
        'elements': ['comparison table', 'vs icon', 'check marks', 'cross marks', 'arrow'],
        'composition': 'Left=competitor (red/cross), Right=LF (green/check)',
        'prompt_keywords': 'comparison, vs, side by side, professional, clean, corporate',
    },
}

# ═══════════════════════════════════════════════════════════
# IMAGE BRIEF GENERATOR
# ═══════════════════════════════════════════════════════════

class ImageBriefGenerator:
    """Generate platform and layer-specific image generation briefs."""

    def __init__(self, seed: int = None):
        self.rng = random.Random(seed)

    def generate(self, platform: str, layer: str, topic: str,
                 format_type: str = 'feed',
                 title: str = '', cta: str = '') -> Dict:
        """Generate a complete image brief."""
        specs = PLATFORM_SPECS.get(platform, {}).get(format_type,
                     PLATFORM_SPECS.get(platform, {}).get('feed', (1080, 1080, '1:1', 'square')))
        visual = LAYER_VISUALS.get(layer, LAYER_VISUALS['education'])

        width, height, ratio, orientation = specs

        brief = {
            'platform': platform,
            'format': format_type,
            'layer': layer,
            'topic': topic,
            'title': title,
            'cta': cta,
            'specs': {
                'width': width, 'height': height,
                'ratio': ratio, 'orientation': orientation,
                'resolution': f'{width}x{height}px',
            },
            'style': {
                'description': visual['style'],
                'colors': visual['colors'],
                'elements': visual['elements'],
                'composition': visual['composition'],
                'typography': {
                    'heading_font': BRAND['fonts']['heading'],
                    'body_font': BRAND['fonts']['body'],
                    'heading_size': f'{int(height * 0.06)}px',
                    'body_size': f'{int(height * 0.03)}px',
                },
            },
            'prompts': self._generate_prompts(platform, layer, topic, visual, specs),
            'brand': {
                'colors': BRAND['colors'],
                'mascot': BRAND['mascot'],
                'no_go': BRAND['no_go'],
            },
        }

        return brief

    def _generate_prompts(self, platform: str, layer: str, topic: str,
                          visual: Dict, specs: tuple) -> Dict:
        """Generate prompts for different AI image tools."""
        width, height, ratio, orientation = specs
        keywords = visual['prompt_keywords']
        colors = ', '.join(visual['colors'])

        return {
            'dalle': (
                f'A {orientation} social media graphic for Hong Kong education brand. '
                f'{visual["style"]}. Topic: {topic}. '
                f'Color palette: {colors}. '
                f'Elements: {", ".join(visual["elements"][:3])}. '
                f'Composition: {visual["composition"]}. '
                f'Clean professional design with Chinese text space. '
                f'Aspect ratio {ratio}. No photorealistic faces. '
                f'Brand style: {BRAND["style"]}.'
            ),
            'midjourney': (
                f'{keywords}, {visual["style"]}, '
                f'{orientation} format, aspect ratio {ratio.split(":")[0]}:{ratio.split(":")[1]}, '
                f'Hong Kong education brand, topic: {topic}, '
                f'colors: {colors}, clean design, '
                f'--ar {ratio.replace(":", ":")} --style raw --no photorealistic faces text-heavy'
            ),
            'stable_diffusion': (
                f'{visual["style"]}, {keywords}, {orientation} image, '
                f'Hong Kong tutoring brand graphic for "{topic}", '
                f'color scheme {colors}, '
                f'{", ".join(visual["elements"][:2])}, '
                f'clean professional, educational infographic'
            ),
        }

    def generate_batch(self, posts: List[Dict],
                       format_type: str = 'feed') -> List[Dict]:
        """Generate briefs for a batch of posts."""
        briefs = []
        for post in posts:
            brief = self.generate(
                platform=post.get('platform', 'fb'),
                layer=post.get('layer', 'education'),
                topic=post.get('title', '數學教學'),
                format_type=format_type,
                title=post.get('title', ''),
                cta=post.get('cta', ''),
            )
            brief['post_id'] = post.get('date', '') + '_' + post.get('platform', '')
            briefs.append(brief)
        return briefs

    def export_briefs(self, briefs: List[Dict],
                      output_path: Path = None) -> Path:
        """Export briefs as interactive HTML gallery."""
        if output_path is None:
            output_path = BRIEF_DIR / f'briefs_{datetime.now().strftime("%Y%m%d")}.html'

        cards = ''
        for b in briefs:
            specs = b['specs']
            style = b['style']
            cards += f'''
            <div class="brief-card">
              <div class="brief-header">
                <span class="brief-platform">{b['platform'].upper()}</span>
                <span class="brief-format">{b['format']}</span>
                <span class="brief-layer">{b['layer']}</span>
              </div>
              <div class="brief-topic">{b['topic'][:60]}</div>
              <div class="brief-specs">{specs['width']}x{specs['height']}px · {specs['ratio']} · {specs['orientation']}</div>
              <div class="brief-style">{style['description'][:100]}...</div>
              <div class="brief-colors">
                {''.join(f'<span class="color-swatch" style="background:{c}" title="{c}"></span>' for c in style['colors'])}
              </div>
              <div class="brief-elements">{", ".join(style['elements'][:3])}</div>
              <details><summary>DALL-E Prompt</summary>
                <pre class="prompt-text">{b['prompts']['dalle'][:300]}</pre>
              </details>
            </div>'''

        html = f'''<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>霖楓學苑 · 圖片生成簡報</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+HK:wght@400;500;700;900&family=JetBrains+Mono&display=swap');
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans HK',sans-serif;background:#F8F9FA;color:#1A1A1A;font-size:14px;padding:20px}}
.container{{max-width:1400px;margin:0 auto}}
h1{{font-size:28px;text-align:center;margin-bottom:24px;color:#1A3C6D}}
.brief-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(400px,1fr));gap:16px}}
.brief-card{{background:white;border-radius:12px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}}
.brief-header{{display:flex;gap:8px;margin-bottom:8px}}
.brief-platform{{background:#1A3C6D;color:white;padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700}}
.brief-format{{background:#F3F4F6;padding:2px 8px;border-radius:4px;font-size:10px}}
.brief-layer{{background:#FEF3C7;padding:2px 8px;border-radius:4px;font-size:10px}}
.brief-topic{{font-size:16px;font-weight:900;margin-bottom:8px}}
.brief-specs{{font-size:11px;color:#6B7280;margin-bottom:8px}}
.brief-style{{font-size:12px;color:#374151;margin-bottom:8px}}
.brief-colors{{display:flex;gap:6px;margin-bottom:8px}}
.color-swatch{{width:20px;height:20px;border-radius:4px;border:1px solid #E5E7EB}}
.brief-elements{{font-size:11px;color:#C9A84C;margin-bottom:8px}}
.prompt-text{{font-size:11px;font-family:'JetBrains Mono',monospace;background:#F3F4F6;padding:8px;border-radius:6px;white-space:pre-wrap;line-height:1.5}}
details{{margin-top:8px}}
summary{{font-size:11px;color:#1A3C6D;cursor:pointer;font-weight:700}}
</style>
</head><body><div class="container">
<h1>霖楓學苑 · AI 圖片生成簡報</h1>
<p style="text-align:center;color:#6B7280;margin-bottom:24px">
  {len(briefs)} briefs · {datetime.now().strftime('%Y-%m-%d %H:%M')}
</p>
<div class="brief-grid">{cards}</div>
</div></body></html>'''

        output_path.write_text(html, encoding='utf-8')
        return output_path


# ═══════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LF Image Brief Engine v1.0')
    parser.add_argument('--post', help='Post topic/title')
    parser.add_argument('--platform', default='ig', choices=['fb', 'ig', 'xhs'])
    parser.add_argument('--layer', default='education')
    parser.add_argument('--format', default='feed')
    parser.add_argument('--batch', help='Path to calendar JSON for batch generation')
    parser.add_argument('--styles', action='store_true', help='Show visual style guide')
    parser.add_argument('--output', help='Output HTML path')

    args = parser.parse_args()
    gen = ImageBriefGenerator(seed=42)

    if args.styles:
        print('Visual Style Guide by Layer:')
        for layer, visual in LAYER_VISUALS.items():
            print(f'\n  {layer}:')
            print(f'    Style: {visual["style"]}')
            print(f'    Colors: {visual["colors"]}')
            print(f'    Elements: {visual["elements"]}')

    elif args.batch:
        try:
            data = json.loads(Path(args.batch).read_text(encoding='utf-8'))
            posts = data.get('posts', [])
            briefs = gen.generate_batch(posts[:10])  # limit to 10 for speed
            print(f'Generated {len(briefs)} briefs from {len(posts)} posts')

            out = gen.export_briefs(briefs,
                output_path=Path(args.output) if args.output else None)
            print(f'HTML: {out}')
        except Exception as e:
            print(f'Error: {e}')

    elif args.post:
        brief = gen.generate(
            platform=args.platform, layer=args.layer,
            topic=args.post, format_type=args.format,
        )
        print(json.dumps(brief, ensure_ascii=False, indent=2))

    else:
        # Demo: generate 3 sample briefs
        demo_posts = [
            {'platform': 'fb', 'layer': 'education', 'title': 'T4陷阱：除數漏寫0'},
            {'platform': 'ig', 'layer': 'social_proof', 'title': '40分→85分真實故事'},
            {'platform': 'xhs', 'layer': 'urgency', 'title': 'SSPA最後90日衝刺'},
        ]
        briefs = gen.generate_batch(demo_posts)
        for b in briefs:
            print(f'\n[{b["platform"].upper()}] {b["layer"]}: {b["topic"]}')
            print(f'  Specs: {b["specs"]["resolution"]} {b["specs"]["ratio"]}')
            print(f'  Style: {b["style"]["description"][:80]}...')
            print(f'  Colors: {b["style"]["colors"]}')
