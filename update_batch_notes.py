import json, glob, os, pathlib

# Find latest export
export_files = glob.glob("substack_notes_export/notes_*.json")
latest_export = max(export_files, key=os.path.getmtime)
notes = json.load(open(latest_export, encoding="utf-8"))
notes_by_id = {n["note_id"]: n for n in notes}

# Update individual notes in batch folders
batch_dir = pathlib.Path("substack_notes_export/batches")
for batch_folder in batch_dir.glob("batch_*"):
    for note_file in batch_folder.glob("*.md"):
        if note_file.name == "INDEX.md":
            continue
        note_id = note_file.stem
        if note_id in notes_by_id:
            note = notes_by_id[note_id]
            content = note_file.read_text(encoding="utf-8")
            # Find the first --- separator and everything after it
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].lstrip("\n")
            else:
                body = content
            
            # Write new clean format
            new_content = f"""# Note {note_id}
**Date:** {note['timestamp'][:19].replace('T', ' ')}
**URL:** {note['url']}
**Reactions:** {note['reaction_count']} | **Restacks:** {note['restacks']} | **Replies:** {note['reply_count']}
---

{body}"""
            note_file.write_text(new_content, encoding="utf-8")

print("Updated all batch note files with clean timestamps")