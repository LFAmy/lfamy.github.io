#!/usr/bin/env python3
"""
LF Marketing System — Persistent Verification Suite
====================================================
AI-first engineering: required regression coverage for touched domains.
Run: python -m pytest tests/test_marketing.py -v
Or:   python tests/test_marketing.py
"""
import sys, io, json, os, unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / 'engines'))
sys.path.insert(0, str(BASE / 'scripts'))
sys.path.insert(0, str(BASE / 'fb_strategy'))

# ═══════════════════════════════════════
# Test infrastructure
# ═══════════════════════════════════════

class MarketingTestBase(unittest.TestCase):
    """Base with fixtures and helpers."""

    @classmethod
    def setUpClass(cls):
        from marketing_brain import MarketingBrain
        cls.brain = MarketingBrain()
        cls.ctx = cls.brain.get_time_context()

    def assertValidPost(self, post):
        """Assert a post dict has all required fields."""
        required = ['title', 'body', 'cta', 'platform', 'layer', 'hashtags']
        for field in required:
            self.assertIn(field, post, f'Missing field: {field}')
        self.assertIsInstance(post['title'], str)
        self.assertIsInstance(post['body'], str)
        self.assertGreater(len(post['body']), 10, 'Body too short')
        self.assertIn(post['platform'], ('fb', 'ig', 'xhs'))
        self.assertIn(post['layer'], (
            'education', 'social_proof', 'engagement',
            'urgency', 'personality', 'reels', 'differentiation',
        ))


# ═══════════════════════════════════════
# 1. Core Brain Tests
# ═══════════════════════════════════════

class TestMarketingBrain(MarketingTestBase):
    """Core orchestrator behavior."""

    def test_initialization(self):
        """Brain initializes with all subsystems."""
        self.assertIsNotNone(self.brain)
        report = self.brain.scan()
        self.assertIsInstance(report, dict)
        self.assertIn('platforms', report)
        self.assertIn('engines', report)
        self.assertIn('fingerprints', report)

    def test_time_context(self):
        """Time context returns valid calendar data."""
        ctx = self.brain.get_time_context()
        self.assertIn('month', ctx)
        self.assertIn('phase', ctx)
        self.assertIn('days_to_sspa', ctx)
        self.assertIn('urgency', ctx)
        self.assertTrue(1 <= ctx['urgency'] <= 10)
        self.assertGreater(ctx['days_to_sspa'], 0)

    def test_sspa_countdown_accuracy(self):
        """SSPA countdown shrinks closer to May."""
        ctx_may = self.brain.get_time_context(datetime(2026, 5, 1))
        ctx_jul = self.brain.get_time_context(datetime(2026, 7, 1))
        self.assertLess(ctx_may['days_to_sspa'], 30)
        self.assertGreater(ctx_jul['days_to_sspa'], 300)

    def test_academic_calendar_coverage(self):
        """All 12 months have calendar entries."""
        from marketing_brain import ACADEMIC_CALENDAR
        for m in range(1, 13):
            self.assertIn(m, ACADEMIC_CALENDAR)

    def test_calendar_urgency_scale(self):
        """Urgency values are in valid range."""
        from marketing_brain import ACADEMIC_CALENDAR
        for m, cal in ACADEMIC_CALENDAR.items():
            self.assertTrue(1 <= cal['urgency'] <= 10,
                           f'Month {m} urgency {cal["urgency"]} out of range')

    def test_generate_empty_platforms(self):
        """Empty platform list returns 0 posts."""
        cal = self.brain.generate_calendar(platforms=[], days=1, use_ai=False)
        self.assertEqual(cal['total_posts'], 0)

    def test_generate_zero_days(self):
        """Zero days returns 0 posts."""
        cal = self.brain.generate_calendar(platforms=['fb'], days=0, use_ai=False)
        self.assertEqual(cal['total_posts'], 0)

    def test_generate_none_platforms_defaults_all(self):
        """None platforms defaults to all 3."""
        cal = self.brain.generate_calendar(platforms=None, days=1, use_ai=False)
        self.assertEqual(cal['total_posts'], 3)

    def test_generate_single_platform(self):
        """Single platform generates correct count."""
        for plat in ('fb', 'ig', 'xhs'):
            cal = self.brain.generate_calendar(platforms=[plat], days=1, use_ai=False)
            self.assertEqual(cal['total_posts'], 1, f'Failed for {plat}')

    def test_generate_multi_day(self):
        """Multi-day generates correct post count."""
        cal = self.brain.generate_calendar(platforms=['fb', 'ig', 'xhs'], days=7, use_ai=False)
        self.assertEqual(cal['total_posts'], 21)

    def test_all_posts_have_valid_structure(self):
        """Every generated post passes structural validation."""
        cal = self.brain.generate_calendar(
            platforms=['fb', 'ig', 'xhs'], days=7, use_ai=False)
        for post in cal['posts']:
            self.assertValidPost(post)

    def test_quality_report_structure(self):
        """Quality report has required fields."""
        cal = self.brain.generate_calendar(platforms=['fb'], days=1, use_ai=False)
        qc = cal['quality']
        self.assertIn('total', qc)
        self.assertIn('passed', qc)
        self.assertIn('failed', qc)
        self.assertIn('by_platform', qc)
        self.assertIn('details', qc)

    def test_html_export_creates_file(self):
        """HTML export creates a non-empty file."""
        cal = self.brain.generate_calendar(platforms=['fb'], days=1, use_ai=False)
        out = BASE / 'docs' / 'social' / '_test_export.html'
        path = self.brain.export_html(cal, out)
        self.assertTrue(path.exists())
        self.assertGreater(path.stat().st_size, 1000)
        content = path.read_text(encoding='utf-8')
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('</html>', content)
        path.unlink()  # cleanup

    def test_dashboard_returns_complete_data(self):
        """Dashboard returns all required sections."""
        dash = self.brain.dashboard()
        self.assertIn('health', dash)
        self.assertIn('optimization', dash)
        self.assertIn('platforms', dash)
        self.assertIn('layers', dash)
        self.assertIn('stats', dash)

    def test_optimize_returns_recommendations(self):
        """Optimize returns per-platform recommendations."""
        opt = self.brain.optimize()
        self.assertIn('recommendations', opt)
        self.assertIn('cross_platform_insights', opt)


# ═══════════════════════════════════════
# 2. QualityGate Tests
# ═══════════════════════════════════════

class TestQualityGate(unittest.TestCase):
    """Content quality validation."""

    @classmethod
    def setUpClass(cls):
        from marketing_brain import QualityGate
        cls.QG = QualityGate

    def _make_post(self, body='', cta='', platform='fb', layer='education'):
        return {'platform': platform, 'layer': layer, 'body': body, 'cta': cta}

    def test_valid_post_passes(self):
        """A well-formed post passes all checks."""
        body = ('每年暑假我地都會見到大量學生喺數學課題出錯，' * 8 +
                '留言診斷免費幫佢測試 👇')
        post = self._make_post(body=body, cta='留言診斷免費測試')
        passed, checks = self.QG.validate(post)
        self.assertTrue(passed, f'Checks: {checks}')
        for name, result in checks.items():
            self.assertTrue(result, f'Check {name} failed')

    def test_no_chinese_fails(self):
        """Post without Chinese characters fails has_chinese."""
        post = self._make_post(body='English only post without any Chinese.')
        passed, checks = self.QG.validate(post)
        self.assertFalse(passed)
        self.assertFalse(checks['has_chinese'])

    def test_too_short_fails(self):
        """Post below min_length fails."""
        post = self._make_post(body='短')
        passed, checks = self.QG.validate(post)
        self.assertFalse(passed)
        self.assertFalse(checks['min_length'])

    def test_no_cta_fails(self):
        """Post without CTA keywords fails."""
        body = '每年暑假我地都會見到大量學生喺數學課題出錯。' * 6
        post = self._make_post(body=body, cta='')
        passed, checks = self.QG.validate(post)
        # Should fail has_cta since neither body nor cta have keywords
        self.assertFalse(checks['has_cta'])

    def test_cta_in_cta_field_passes(self):
        """CTA keyword in cta field (not body) still passes."""
        body = '每年暑假我地都會見到大量學生喺數學課題出錯。' * 6
        post = self._make_post(body=body, cta='留言診斷免費測試 👇')
        passed, checks = self.QG.validate(post)
        self.assertTrue(checks['has_cta'],
                       'has_cta should pass when cta field has keywords')

    def test_empty_body_fails(self):
        """Empty body fails multiple checks."""
        post = self._make_post(body='', cta='')
        passed, checks = self.QG.validate(post)
        self.assertFalse(passed)

    def test_banned_words_fail(self):
        """Post with banned words fails."""
        body = ('每年暑假我地都會見到大量學生喺數學課題出錯。' * 6 +
                'This is a revolutionary game-changer!')
        post = self._make_post(body=body)
        passed, checks = self.QG.validate(post)
        self.assertFalse(checks.get('no_banned', True))

    def test_batch_validation(self):
        """Batch validation reports correct counts."""
        good = self._make_post(
            body='每年暑假我地都會見到大量學生喺數學課題出錯。' * 8 +
                 '留言診斷免費測試 👇',
            cta='留言診斷免費測試')
        bad = self._make_post(body='Short')
        report = self.QG.validate_batch([good, bad])
        self.assertEqual(report['total'], 2)
        self.assertEqual(report['passed'], 1)
        self.assertEqual(report['failed'], 1)

    def test_per_platform_length_requirements(self):
        """Each platform has appropriate length thresholds."""
        body_medium = '每年暑假我地都會見到大量學生。' * 4  # ~80 chars
        # IG (short, min 60): should pass
        post_ig = self._make_post(body=body_medium, platform='ig')
        _, checks_ig = self.QG.validate(post_ig)
        self.assertTrue(checks_ig['min_length'],
                       f'IG should pass with {len(body_medium)} chars')

        # FB (long, min 100): should fail with ~80 chars
        post_fb = self._make_post(body=body_medium, platform='fb')
        _, checks_fb = self.QG.validate(post_fb)
        self.assertFalse(checks_fb['min_length'],
                        f'FB should fail with {len(body_medium)} chars')


# ═══════════════════════════════════════
# 3. ContentFingerprinter Tests
# ═══════════════════════════════════════

class TestFingerprinter(unittest.TestCase):
    """Content deduplication."""

    def setUp(self):
        from marketing_brain import ContentFingerprinter
        self.fp = ContentFingerprinter()

    def test_init_empty(self):
        """New fingerprinter has fingerprints loaded."""
        self.assertIsInstance(self.fp.count(), int)

    def test_detects_duplicate(self):
        """Same text is detected as duplicate after registration."""
        text = 'unique test content for fingerprinting'
        self.assertFalse(self.fp.is_duplicate(text))
        self.fp.register(text)
        self.assertTrue(self.fp.is_duplicate(text))

    def test_different_texts_not_duplicate(self):
        """Different texts are not duplicates."""
        self.fp.register('first unique content')
        self.assertFalse(self.fp.is_duplicate('second unique content'))

    def test_persistence(self):
        """Fingerprints survive save/load cycle."""
        self.fp.register('persistent content test')
        self.fp.save()
        from marketing_brain import ContentFingerprinter
        fp2 = ContentFingerprinter(self.fp.db_path)
        self.assertGreaterEqual(fp2.count(), 1)


# ═══════════════════════════════════════
# 4. MAB Optimizer Tests
# ═══════════════════════════════════════

class TestMABOptimizer(unittest.TestCase):
    """Multi-armed bandit content optimization."""

    def setUp(self):
        from marketing_brain import MABContentOptimizer
        self.mab = MABContentOptimizer()

    def test_init_empty(self):
        """New MAB has no arms."""
        self.assertEqual(len(self.mab.arms), 0)

    def test_update_creates_arm(self):
        """Update creates a new arm."""
        self.mab.update('fb', 'education', 0.8)
        self.assertEqual(len(self.mab.arms), 1)
        self.assertIn('fb:education', self.mab.arms)

    def test_multiple_updates_aggregate(self):
        """Multiple updates to same arm aggregate."""
        self.mab.update('fb', 'education', 0.8)
        self.mab.update('fb', 'education', 0.7)
        arm = self.mab.arms['fb:education']
        self.assertEqual(arm['trials'], 2)
        self.assertAlmostEqual(arm['total_reward'], 1.5)

    def test_optimal_mix_ranks_by_performance(self):
        """Higher-performing layers rank higher."""
        # Many trials to reduce Thompson sampling variance
        for _ in range(10):
            self.mab.update('fb', 'education', 0.85)
        for _ in range(10):
            self.mab.update('fb', 'social_proof', 0.15)
        optimal = self.mab.get_optimal_mix('fb', top_n=2)
        self.assertEqual(len(optimal), 2)
        self.assertEqual(optimal[0]['layer'], 'education')

    def test_cross_platform_insights(self):
        """Insights aggregate across platforms."""
        self.mab.update('fb', 'education', 0.8)
        self.mab.update('ig', 'reels', 0.9)
        self.mab.update('xhs', 'education', 0.6)
        insights = self.mab.get_cross_platform_insights()
        self.assertEqual(len(insights), 3)

    def test_serialization_roundtrip(self):
        """MAB state survives serialization."""
        self.mab.update('fb', 'education', 0.8)
        self.mab.update('ig', 'reels', 0.9)
        data = self.mab.to_dict()
        from marketing_brain import MABContentOptimizer
        mab2 = MABContentOptimizer.from_dict(data)
        self.assertEqual(len(mab2.arms), 2)

    def test_empty_mab_returns_empty(self):
        """Empty MAB returns empty results gracefully."""
        self.assertEqual(self.mab.get_optimal_mix('fb'), [])
        self.assertEqual(self.mab.get_cross_platform_insights(), {})

    def test_sampling_stability(self):
        """Thompson sampling produces values in [0,1]."""
        self.mab.update('fb', 'education', 0.5)
        for _ in range(20):
            sample = self.mab.sample('fb', 'education')
            self.assertTrue(0.0 <= sample <= 1.0,
                           f'Sample {sample} out of [0,1] range')


# ═══════════════════════════════════════
# 5. AI Content Generator Tests
# ═══════════════════════════════════════

class TestAIContentGenerator(unittest.TestCase):
    """Template fallback and AI generation."""

    @classmethod
    def setUpClass(cls):
        from marketing_brain import AIContentGenerator, MarketingBrain
        cls.gen = AIContentGenerator()
        cls.ctx = MarketingBrain().get_time_context()

    def test_all_layers_have_fallback(self):
        """Every content layer has a fallback template."""
        from marketing_brain import LAYERS
        for layer_name in LAYERS:
            post = self.gen._fallback_template('fb', layer_name, 'test', self.ctx)
            self.assertTrue(post.get('body'), f'No body for layer {layer_name}')
            self.assertTrue(post.get('title'), f'No title for layer {layer_name}')
            self.assertTrue(post.get('cta'), f'No CTA for layer {layer_name}')

    def test_unknown_layer_falls_back(self):
        """Unknown layer name falls back to education template."""
        post = self.gen._fallback_template('fb', 'nonexistent', 'test', self.ctx)
        self.assertTrue(post.get('body'))

    def test_all_platforms_have_templates(self):
        """Each platform gets a valid template."""
        for plat in ('fb', 'ig', 'xhs'):
            post = self.gen._fallback_template(plat, 'education', 'test', self.ctx)
            self.assertTrue(post.get('body'), f'No template for {plat}')

    def test_deepseek_check(self):
        """DeepSeek health check runs without error."""
        available = self.gen._check_ai()
        self.assertIsInstance(available, bool)

    def test_prompt_contains_platform_info(self):
        """Generated prompts include platform-specific instructions."""
        prompt = self.gen._build_prompt(
            'fb', 'education', 'test topic', self.ctx,
            {'name': 'Facebook', 'tone': 'test', 'audience': 'test',
             'content_length': 'long', 'hashtag_style': 'few_targeted'},
            {'icon': 'test', 'goal': 'test', 'psychology': ['P1_焦慮']})
        self.assertIn('Facebook', prompt)
        self.assertIn('test topic', prompt)


# ═══════════════════════════════════════
# 6. CrossPlatformAdapter Tests
# ═══════════════════════════════════════

class TestCrossPlatformAdapter(unittest.TestCase):
    """Platform-aware content adaptation."""

    def setUp(self):
        from marketing_brain import CrossPlatformAdapter
        self.adapter = CrossPlatformAdapter()

    def test_adapt_sets_platform_fields(self):
        """Adapter sets platform-specific metadata."""
        post = {'body': 'test', 'hashtags': '#test', 'platform': 'fb'}
        adapted = self.adapter.adapt_post(post, 'ig')
        self.assertEqual(adapted['platform'], 'ig')
        self.assertEqual(adapted['platform_name'], 'Instagram')

    def test_adapt_ig_adds_branded_hashtags(self):
        """IG gets branded hashtags added."""
        post = {'body': 'test', 'hashtags': '#test'}
        adapted = self.adapter.adapt_post(post, 'ig')
        self.assertIn('霖楓學苑', adapted.get('hashtags', ''))

    def test_adapt_xhs_adds_localized_hashtags(self):
        """XHS gets localized hashtags added."""
        post = {'body': 'test', 'hashtags': '#test'}
        adapted = self.adapter.adapt_post(post, 'xhs')
        self.assertIn('香港媽媽', adapted.get('hashtags', ''))


# ═══════════════════════════════════════
# 7. Config Consistency Tests
# ═══════════════════════════════════════

class TestConfigConsistency(unittest.TestCase):
    """Configuration validation."""

    def test_platform_configs_complete(self):
        """All platforms have required config keys."""
        from marketing_brain import PLATFORMS
        required = ['name', 'color', 'icon', 'tone', 'audience',
                    'content_length', 'best_times', 'best_days',
                    'post_freq', 'hashtag_style', 'image_ratio', 'content_mix']
        for plat_id, cfg in PLATFORMS.items():
            for key in required:
                self.assertIn(key, cfg, f'{plat_id} missing {key}')

    def test_content_mix_sums_to_one(self):
        """Each platform's content mix sums to approximately 1.0."""
        from marketing_brain import PLATFORMS
        for plat_id, cfg in PLATFORMS.items():
            total = sum(cfg['content_mix'].values())
            self.assertAlmostEqual(total, 1.0, delta=0.01,
                                  msg=f'{plat_id} mix sums to {total}')

    def test_layer_psych_triggers_exist(self):
        """Every psychology trigger referenced by layers exists."""
        from marketing_brain import LAYERS, PSYCHOLOGY_TRIGGERS
        for layer_name, cfg in LAYERS.items():
            for trigger in cfg['psychology']:
                self.assertIn(trigger, PSYCHOLOGY_TRIGGERS,
                             f'{layer_name} references unknown trigger {trigger}')

    def test_best_times_format(self):
        """Best times are in HH:MM format."""
        from marketing_brain import PLATFORMS
        import re
        time_pat = re.compile(r'^\d{2}:\d{2}$')
        for plat_id, cfg in PLATFORMS.items():
            for t in cfg['best_times']:
                self.assertTrue(time_pat.match(t),
                               f'{plat_id} bad time format: {t}')

    def test_best_days_in_range(self):
        """Best days are valid weekday numbers (0-6)."""
        from marketing_brain import PLATFORMS
        for plat_id, cfg in PLATFORMS.items():
            for d in cfg['best_days']:
                self.assertTrue(0 <= d <= 6,
                               f'{plat_id} bad day: {d}')


# ═══════════════════════════════════════
# 8. IG Content Engine Tests
# ═══════════════════════════════════════

class TestIGContentEngine(unittest.TestCase):
    """Instagram content generation."""

    @classmethod
    def setUpClass(cls):
        from ig_content_engine import (
            ReelsScriptGenerator, StoryGenerator,
            CarouselGenerator, FeedPostGenerator,
            IGCalendarGenerator, HASHTAG_PYRAMID,
            generate_hashtags,
        )
        cls.Reels = ReelsScriptGenerator
        cls.Story = StoryGenerator
        cls.Carousel = CarouselGenerator
        cls.Feed = FeedPostGenerator
        cls.IGCal = IGCalendarGenerator
        cls.HASHTAG_PYRAMID = HASHTAG_PYRAMID
        cls.gen_hashtags = generate_hashtags

    def test_reels_generates_complete_script(self):
        """Reels script has all required fields."""
        reel = self.Reels.generate()
        self.assertIn('hook', reel)
        self.assertIn('structure', reel)
        self.assertIn('visual_direction', reel)
        self.assertIn('caption', reel)
        self.assertIn('hashtags', reel)
        self.assertIsInstance(reel['total_seconds'], int)

    def test_reels_batch_correct_count(self):
        """Reels batch generates requested count."""
        for count in (1, 3, 5):
            batch = self.Reels.generate_batch(count)
            self.assertEqual(len(batch), count)

    def test_story_generates_content(self):
        """Story generates non-empty content."""
        story = self.Story.generate()
        self.assertTrue(story.get('content'))
        self.assertIn('format', story)
        self.assertEqual(story['format'], 'story')

    def test_story_week_generates_7(self):
        """Story week generates 7 stories."""
        week = self.Story.generate_week()
        self.assertEqual(len(week), 7)

    def test_carousel_has_minimum_slides(self):
        """Carousel has at least 5 slides."""
        carousel = self.Carousel.generate()
        self.assertGreaterEqual(carousel['slides_count'], 5)

    def test_carousel_batch_correct_count(self):
        """Carousel batch generates requested count."""
        batch = self.Carousel.generate_batch(3)
        self.assertEqual(len(batch), 3)

    def test_feed_post_has_all_fields(self):
        """Feed post has all required fields."""
        feed = self.Feed.generate()
        self.assertIn('title', feed)
        self.assertIn('body', feed)
        self.assertIn('cta', feed)
        self.assertIn('hashtags', feed)

    def test_ig_calendar_week(self):
        """IG calendar generates a full week."""
        cal = self.IGCal()
        week = cal.generate_week()
        self.assertGreater(week['total_posts'], 0)
        self.assertIn('by_format', week)
        self.assertEqual(week['platform'], 'ig')

    def test_hashtag_pyramid_has_categories(self):
        """Hashtag pyramid has all required categories."""
        for cat in ('branded', 'niche', 'broad', 'trending'):
            self.assertIn(cat, self.HASHTAG_PYRAMID)
            self.assertGreater(len(self.HASHTAG_PYRAMID[cat]), 0)

    def test_generate_hashtags_count(self):
        """Hashtag generator respects count parameter."""
        for count in (5, 8, 12):
            tags = self.__class__.gen_hashtags(count)
            tag_list = tags.split()
            self.assertLessEqual(len(tag_list), count)
            # All tags start with #
            for tag in tag_list:
                self.assertTrue(tag.startswith('#'))


# ═══════════════════════════════════════
# 9. State Persistence Tests
# ═══════════════════════════════════════

class TestStatePersistence(MarketingTestBase):
    """State save/load cycle."""

    def test_save_load_cycle(self):
        """State survives save and reload."""
        self.brain.record_engagement('fb', 'education', 1000, 80)
        self.brain._save_state()

        from marketing_brain import MarketingBrain
        brain2 = MarketingBrain()
        self.assertGreaterEqual(len(brain2.mab.arms), 1)

    def test_fingerprints_persist(self):
        """Fingerprints survive save/load."""
        self.brain.fingerprinter.register('persistence test content')
        self.brain.fingerprinter.save()

        from marketing_brain import MarketingBrain
        brain2 = MarketingBrain()
        self.assertGreaterEqual(brain2.fingerprinter.count(), 1)


# ═══════════════════════════════════════
# 10. Edge Case & Regression Tests
# ═══════════════════════════════════════

class TestEdgeCases(MarketingTestBase):
    """Boundary conditions and regression prevention."""

    def test_large_calendar_no_crash(self):
        """30-day calendar across 3 platforms (90 posts) doesn't crash."""
        cal = self.brain.generate_calendar(
            platforms=['fb', 'ig', 'xhs'], days=30, use_ai=False)
        self.assertEqual(cal['total_posts'], 90)

    def test_rapid_fingerprint_registration(self):
        """100 rapid fingerprint registrations work correctly."""
        for i in range(100):
            self.brain.fingerprinter.register(f'unique-{i}')
        self.assertGreaterEqual(self.brain.fingerprinter.count(), 100)

    def test_calendar_layer_cycling(self):
        """Calendar cycles through all 7 layers over 7 days."""
        cal = self.brain.generate_calendar(platforms=['fb'], days=7, use_ai=False)
        layers_seen = set(p['layer'] for p in cal['posts'])
        self.assertEqual(len(layers_seen), 7,
                        f'Expected all 7 layers, got {layers_seen}')

    def test_all_posts_have_unique_content(self):
        """No two posts have identical body text."""
        cal = self.brain.generate_calendar(
            platforms=['fb', 'ig', 'xhs'], days=7, use_ai=False)
        # Check per-platform uniqueness (adapter modifies bodies)
        for plat in ('fb', 'ig', 'xhs'):
            plat_bodies = [p['body'] for p in cal['posts'] if p['platform'] == plat]
            self.assertEqual(len(plat_bodies), len(set(plat_bodies)),
                            f'Duplicate bodies in {plat}')

# ═══════════════════════════════════════
# Runner
# ═══════════════════════════════════════

if __name__ == '__main__':
    # Use unittest runner for consistent output
    unittest.main(verbosity=2)
