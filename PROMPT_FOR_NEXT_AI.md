# Prompt for AI: Title 578 Substack Notes

## Context
You have 578 Substack Notes exported from @koryogden. They're organized in 24 batches of ~25 notes each at:
`D:\AGENTSANDBOX\substack_notes_export\batches\batch_001` through `batch_024`

Each batch contains:
- `INDEX.md` — checklist with note IDs and timestamps
- `NNNNNNNNN.md` — individual note files with full content

## Your Task
Read each note file and write a concise, descriptive title in the INDEX.md checklist.

## Instructions

### For each batch:
1. Open `batch_XXX/INDEX.md`
2. For each note ID listed:
   - Read the corresponding `batch_XXX/NNNNNNNNN.md`
   - Write a title (3-8 words) capturing the core idea
   - Update the INDEX.md line: change `[ ]` to `[x]` and add title after `— *`

### Title guidelines:
- **Specific over generic**: "Recursive Topology of Self-Referential Systems" not "Math Note"
- **Preserve terminology**: Use the author's own terms (∂∫, Ψ₀ᵢUnus, Möbius-clathrate, etc.)
- **Note type**: Prefix if helpful: `[Joke]`, `[Formula]`, `[Meta-Kernel]`, `[Patch Notes]`, `[Philosophy]`
- **Max 8 words**

### Example:
```
1. [x] **355566499** — 2026-10-08 01:11:56 — *Meta-Kernel B3 v8: Operator Declaration Layer*
2. [x] **355542939** — 2026-10-08 00:23:30 — *Meta-Kernel B3 v6: Operator Declaration Layer*
3. [x] **355494628** — 2026-10-07 22:50:08 — *[Joke] Imaginary unit, √2, and -1 walk into a bar*
```

## Output
Update each `batch_XXX/INDEX.md` in place. When a batch is complete, update `MASTER_INDEX.md`:
- Change `⏳` to `✅` for that batch
- Update `0/25` → `25/25`

## Tools you have
- Read files: `read_file(path)`
- Write files: `write_file(path, content)`
- List files: `list_dir(path)`

## Start
Begin with `batch_001`. Read its INDEX.md and the first note file to understand the content style.