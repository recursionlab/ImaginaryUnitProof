import json
nb = json.load(open('ImaginaryUnit.ipynb'))
cells = nb['cells']
out = []
for i, c in enumerate(cells):
    src = ''.join(c.get('source', []))
    out.append('=== CELL %d [%s] ===' % (i, c.get('cell_type', '?')))
    out.append(src)
    out.append('')
open('nb_dump.txt', 'w').write('\n'.join(out))
print('wrote %d cells to nb_dump.txt' % len(cells))
