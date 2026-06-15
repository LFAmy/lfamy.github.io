#!/usr/bin/env python3
"""LF Academy CSS Propagation Script — v7.0
Replaces inline <style> block in all lecture HTML files with lf-academy-v7.css content.
Backs up original files to _backup_v6/ directory.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

BASE = Path(r"G:\lam-fung-academy")
CSS_PATH = BASE / "lf-academy-v7.css"
LECTURES_DIR = BASE / "講義"
BACKUP_DIR = BASE / "_backup_v6"

def load_css():
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        return f.read()

def update_file(filepath, css_content):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Pattern: <style> ... </style> (possibly with newlines)
    # We look for the <style> tag that contains the LF Academy CSS
    pattern = r"<style>\s*/\*.*?LF Academy.*?</style>"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        # Try simpler pattern: any <style> block
        pattern = r"<style>.*?</style>"
        match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return False, "no <style> block found"
    
    new_style = f"<style>\n{css_content}\n</style>"
    new_content = content[:match.start()] + new_style + content[match.end():]
    
    # Also update any version reference in comments
    new_content = new_content.replace("v6.0", "v7.0")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    return True, "updated"

def main():
    if not CSS_PATH.exists():
        print(f"ERROR: CSS not found at {CSS_PATH}")
        return
    
    css = load_css()
    print(f"Loaded v7.0 CSS: {len(css)} chars")
    
    # Create backup dir
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Collect all HTML files
    html_files = list(LECTURES_DIR.rglob("*.html"))
    print(f"Found {len(html_files)} HTML files in {LECTURES_DIR}")
    
    stats = {"updated": 0, "skipped": 0, "errors": 0}
    
    for fp in html_files:
        rel = fp.relative_to(BASE)
        
        # Backup
        backup_subdir = BACKUP_DIR / fp.parent.relative_to(BASE)
        backup_subdir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_subdir / fp.name
        if not backup_path.exists():
            shutil.copy2(fp, backup_path)
        
        # Update
        success, msg = update_file(fp, css)
        if success:
            stats["updated"] += 1
        else:
            stats["skipped"] += 1
            if stats["skipped"] <= 5:
                print(f"  SKIP: {rel} — {msg}")
    
    print(f"\n=== Results ===")
    print(f"Updated: {stats['updated']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Backup: {BACKUP_DIR}")
    print(f"Done at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
