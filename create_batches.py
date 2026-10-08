#!/usr/bin/env python3
"""
Batch notes into groups of 25 for manual titling.
Creates batch folders with index files for tracking progress.
"""

import json
import pathlib
import shutil
from datetime import datetime

BATCH_SIZE = 25
SOURCE_DIR = pathlib.Path("substack_notes_export/individual_notes")
OUTPUT_DIR = pathlib.Path("substack_notes_export/batches")
MANIFEST_FILE = OUTPUT_DIR / "MANIFEST.json"

def create_batches():
    # Load all notes - use latest export
    import glob, os
    export_files = glob.glob("substack_notes_export/notes_*.json")
    notes_file = max(export_files, key=os.path.getmtime)
    print(f"Using export: {notes_file}")
    notes = json.load(open(notes_file, encoding="utf-8"))
    
    # Sort by timestamp (newest first)
    notes.sort(key=lambda n: n["timestamp"], reverse=True)
    
    # Clean output dir
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)
    
    manifest = {
        "created": datetime.now().isoformat(),
        "total_notes": len(notes),
        "batch_size": BATCH_SIZE,
        "batches": []
    }
    
    for i in range(0, len(notes), BATCH_SIZE):
        batch_num = i // BATCH_SIZE + 1
        batch_notes = notes[i:i + BATCH_SIZE]
        
        batch_dir = OUTPUT_DIR / f"batch_{batch_num:03d}"
        batch_dir.mkdir()
        
        # Copy notes to batch folder
        for note in batch_notes:
            src = SOURCE_DIR / f'{note["note_id"]}.md'
            dst = batch_dir / f'{note["note_id"]}.md'
            if src.exists():
                shutil.copy2(src, dst)
        
        # Create index file for this batch
        index_path = batch_dir / "INDEX.md"
        lines = [f"# Batch {batch_num:03d} ({len(batch_notes)} notes)\n"]
        lines.append(f"**Progress:** 0/{len(batch_notes)} titled\n")
        first_ts = batch_notes[0]['timestamp'][:19].replace('T', ' ')
        last_ts = batch_notes[-1]['timestamp'][:19].replace('T', ' ')
        lines.append(f"**Date range:** {last_ts} → {first_ts}\n")
        lines.append("---\n")
        
        for j, note in enumerate(batch_notes, 1):
            status = "[ ]"
            title = ""  # To be filled manually
            ts = note['timestamp'][:19].replace('T', ' ')
            lines.append(f"{j:2d}. {status} **{note['note_id']}** — {ts} — *{title}*")
        
        index_path.write_text("\n".join(lines), encoding="utf-8")
        
        manifest["batches"].append({
            "batch": batch_num,
            "folder": str(batch_dir),
            "count": len(batch_notes),
            "start_id": batch_notes[0]["note_id"],
            "end_id": batch_notes[-1]["note_id"],
            "titled": 0,
            "completed": False
        })
    
    # Write manifest
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    
    # Create master index
    master_index = OUTPUT_DIR / "MASTER_INDEX.md"
    lines = ["# Notes Titling Project\n"]
    lines.append(f"**Total:** {len(notes)} notes in {len(manifest['batches'])} batches of ~{BATCH_SIZE}\n")
    lines.append(f"**Created:** {manifest['created']}\n")
    lines.append("---\n")
    
    for b in manifest["batches"]:
        status = "✅" if b["completed"] else "⏳"
        lines.append(f"- {status} **Batch {b['batch']:03d}** — {b['count']} notes — {b['titled']}/{b['count']} titled — [{b['folder']}]({b['folder']}/INDEX.md)")
    
    master_index.write_text("\n".join(lines), encoding="utf-8")
    
    print(f"Created {len(manifest['batches'])} batches in {OUTPUT_DIR}")
    print(f"Master index: {master_index}")

if __name__ == "__main__":
    create_batches()