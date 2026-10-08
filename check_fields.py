import json
notes = json.load(open('substack_notes_export/notes_20261008_142058.json', encoding='utf-8'))
for i, n in enumerate(notes[:3]):
    print(f'--- Note {i} ---')
    for k, v in n.items():
        if v and isinstance(v, str) and len(v) < 100:
            print(f'  {k}: {v}')