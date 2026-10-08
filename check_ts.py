import json, glob, os
# Find latest export
files = glob.glob('substack_notes_export/notes_*.json')
latest = max(files, key=os.path.getmtime)
print(f"Using: {latest}")
notes = json.load(open(latest, encoding='utf-8'))
for i, n in enumerate(notes[:5]):
    print(f'{i}: timestamp={repr(n.get("timestamp"))}')