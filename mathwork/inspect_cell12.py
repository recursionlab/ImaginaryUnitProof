import adv_common as ac

nb = ac.load_nb()
for i, c in enumerate(nb["cells"]):
    src = "".join(c.get("source", []))
    lines = src.splitlines()
    first = lines[0][:80] if lines else "(empty)"
    print(f"idx={i:2d}  type={c['cell_type']:8s}  {first}")

print("=" * 60)
print("CELL 12 (0-based) source:")
print("=" * 60)
lines = ac.cell_lines(12)
for lineno, text in lines:
    print(f"{lineno:4d}: {text}", end="")
