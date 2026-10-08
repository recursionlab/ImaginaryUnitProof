import json
notes = json.load(open('substack_notes_export/notes_20261008_142058.json', encoding='utf-8'))
for i, n in enumerate(notes[:3]):
    print(f'--- Note {i} ---')
    print(f'body_json keys: {n["body_json"].keys() if n["body_json"] else "empty"}')
    if n["body_json"] and "content" in n["body_json"]:
        print(f'content: {n["body_json"]["content"][:2]}')