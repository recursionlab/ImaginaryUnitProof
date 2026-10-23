import adv_common as c
import json

nb = c.load_nb()
out = []
out.append(f'total cells: {len(nb["cells"])}')
for i in range(36):
    out.append(f'--- cell {i} type={c.cell_type(i)} ---')
    for ln, t in c.cell_lines(i):
        out.append(f'{ln}: {t.rstrip()}')

with open('cells_dump.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('wrote', len(out), 'lines to cells_dump.txt')
