import json, sys
nb = json.load(open("ImaginaryUnit.ipynb"))
cells = nb["cells"]
for i, c in enumerate(cells[:5]):
    src = "".join(c.get("source", []))
    print(f"=== CELL {i} [{c.get('cell_type','?')}] ===")
    print(src)
    print()
