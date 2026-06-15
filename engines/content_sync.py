#!/usr/bin/env python3
"""LF Academy Content Sync Engine v1.0 — Auto-sync main→EN→AK→Student"""
import os, re, json, hashlib, time
from pathlib import Path
from datetime import datetime

BASE = Path(r"G:\lam-fung-academy\講義")
SYNC_STATE = Path(r"G:\lam-fung-academy\.sync_state.json")

def hash_file(path):
    """Return MD5 hash of file content."""
    return hashlib.md5(path.read_bytes()).hexdigest()

def load_sync_state():
    """Load last-known state of all lecture files."""
    if SYNC_STATE.exists():
        return json.loads(SYNC_STATE.read_text())
    return {}

def save_sync_state(state):
    SYNC_STATE.write_text(json.dumps(state, indent=2))

def scan_changes():
    """Scan all lecture files and return list of changes since last sync."""
    prev_state = load_sync_state()
    current_state = {}
    changes = {"new": [], "modified": [], "deleted": [], "total": 0}
    
    grades = ["P3", "P4", "P5", "P6"]
    
    for grade in grades:
        gdir = BASE / grade
        if not gdir.exists():
            continue
        
        main_files = [f for f in gdir.glob("*.html") 
                      if not any(s in f.stem for s in ["_AK", "_EN", "_學生", "_答案"])]
        
        for mf in main_files:
            rel = str(mf.relative_to(BASE))
            h = hash_file(mf)
            mtime = mf.stat().st_mtime
            size = mf.stat().st_size
            
            current_state[rel] = {"hash": h, "mtime": mtime, "size": size}
            
            if rel not in prev_state:
                changes["new"].append(rel)
            elif prev_state[rel]["hash"] != h:
                changes["modified"].append(rel)
        
        changes["total"] += len(main_files)
    
    # Detect deletions
    for rel in prev_state:
        if rel not in current_state:
            changes["deleted"].append(rel)
    
    return changes, current_state

def get_sync_status():
    """Return detailed sync status for all lectures."""
    changes, _ = scan_changes()
    
    grades = ["P3", "P4", "P5", "P6"]
    status = {}
    
    for grade in grades:
        gdir = BASE / grade
        if not gdir.exists():
            continue
        
        main_files = {f.stem: f for f in gdir.glob("*.html") 
                      if not any(s in f.stem for s in ["_AK", "_EN", "_學生", "_答案"])}
        
        grade_status = {"total": len(main_files), "en_synced": 0, "ak_synced": 0, "stu_synced": 0}
        
        for stem, mf in main_files.items():
            en_path = mf.parent / (stem + "_EN.html")
            ak_path = mf.parent / (stem + "_AK.html")
            stu_path = mf.parent / (stem + "_學生.html")
            
            if en_path.exists():
                ratio = en_path.stat().st_size / mf.stat().st_size
                if ratio >= 0.80:
                    grade_status["en_synced"] += 1
            
            if ak_path.exists():
                grade_status["ak_synced"] += 1
            
            if stu_path.exists():
                grade_status["stu_synced"] += 1
        
        status[grade] = grade_status
    
    return {
        "changes": changes,
        "status": status,
        "timestamp": datetime.now().isoformat(),
    }

def mark_synced():
    """Save current state after successful sync."""
    _, current_state = scan_changes()
    save_sync_state(current_state)
    return {"status": "synced", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        result = get_sync_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif len(sys.argv) > 1 and sys.argv[1] == "--mark":
        result = mark_synced()
        print(json.dumps(result))
    else:
        changes, _ = scan_changes()
        print(f"New: {len(changes['new'])} | Modified: {len(changes['modified'])} | Deleted: {len(changes['deleted'])}")
