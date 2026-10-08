import json, pathlib
data = json.load(open('substack_notes_export/notes_20261008_142058.json', encoding='utf-8'))
out = pathlib.Path('substack_notes_export/individual_notes')
out.mkdir(exist_ok=True)
for note in data:
    fname = out / f'{note["note_id"]}.md'
    fname.write_text(f'# Note {note["note_id"]}\n\n**Date:** {note["timestamp"]}\n\n**URL:** {note["url"]}\n\n**Reactions:** {note["reaction_count"]} | **Restacks:** {note["restacks"]} | **Replies:** {note["reply_count"]}\n\n---\n\n{note["body"]}', encoding='utf-8')
print(f'Created {len(data)} files in {out}')