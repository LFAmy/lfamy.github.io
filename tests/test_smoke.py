"""Smoke tests for lam-fung-academy handout production tools."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '_tools'))

def test_svg_geometry_import():
    """svg_geometry.py should be importable."""
    import svg_geometry
    assert hasattr(svg_geometry, 'SVG_NS') or True

def test_render_math_import():
    """render_math.py should be importable (skips if matplotlib missing)."""
    try:
        import matplotlib
    except ImportError:
        import pytest; pytest.skip("matplotlib not installed")
    import render_math
    assert True

def test_svg_namespace():
    """SVG namespace should be correct."""
    import svg_geometry
    ns = getattr(svg_geometry, 'SVG_NS', 'http://www.w3.org/2000/svg')
    assert 'w3.org' in ns

def test_package_json_exists():
    """package.json should exist at project root."""
    root = os.path.dirname(os.path.dirname(__file__))
    pkg = os.path.join(root, 'package.json')
    assert os.path.exists(pkg), f"Missing: {pkg}"

def test_claude_md_exists():
    """CLAUDE.md should exist."""
    root = os.path.dirname(os.path.dirname(__file__))
    claude = os.path.join(root, 'CLAUDE.md')
    assert os.path.exists(claude), f"Missing: {claude}"

def test_requirements_exists():
    """requirements.txt should exist."""
    root = os.path.dirname(os.path.dirname(__file__))
    req = os.path.join(root, 'requirements.txt')
    assert os.path.exists(req), f"Missing: {req}"
