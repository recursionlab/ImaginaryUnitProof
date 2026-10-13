#!/usr/bin/env python3
"""
Query tool for Substack notes search index.
"""

import json
import pathlib
import sys
from typing import List, Set

INDEX_DIR = pathlib.Path("substack_notes_export/search_index")


def load_index():
    with open(INDEX_DIR / "index.json", encoding="utf-8") as f:
        notes = json.load(f)
    with open(INDEX_DIR / "inverted_index.json", encoding="utf-8") as f:
        inverted = json.load(f)
    return notes, inverted


def safe(s):
    return s.encode("ascii", "replace").decode()


def search_terms(inverted, terms: List[str], mode: str = "AND") -> Set[str]:
    """Search for notes containing terms."""
    if not terms:
        return set()
    sets = [set(inverted["terms"].get(t, [])) for t in terms]
    if mode == "AND":
        return set.intersection(*sets) if sets else set()
    else:
        return set.union(*sets) if sets else set()


def search_operators(inverted, ops: List[str], mode: str = "AND") -> Set[str]:
    sets = [set(inverted["operators"].get(o, [])) for o in ops]
    if mode == "AND":
        return set.intersection(*sets) if sets else set()
    else:
        return set.union(*sets) if sets else set()


def search_tags(inverted, tags: List[str], mode: str = "AND") -> Set[str]:
    sets = [set(inverted["tags"].get(t, [])) for t in tags]
    if mode == "AND":
        return set.intersection(*sets) if sets else set()
    else:
        return set.union(*sets) if sets else set()


def search_greek(inverted, letters: List[str], mode: str = "AND") -> Set[str]:
    sets = [set(inverted["greek"].get(g, [])) for g in letters]
    if mode == "AND":
        return set.intersection(*sets) if sets else set()
    else:
        return set.union(*sets) if sets else set()


def format_result(note_id: str, notes_dict: dict, max_body: int = 200) -> str:
    note = notes_dict[note_id]
    title = safe(note["title"] or "(no title)")
    ts = note["timestamp"][:19].replace("T", " ")
    tags = " ".join(f"[{safe(t)}]" for t in note["tags"])
    body_preview = safe(note["raw_body"][:max_body].replace("\n", " "))
    return f"{note_id} \u2014 {ts} \u2014 {tags} {title}\n  {body_preview}..."


def main():
    notes, inverted = load_index()
    notes_dict = {n["note_id"]: n for n in notes}

    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "  python query_notes.py term <term1> [term2...]     # Search formal terms (AND)"
        )
        print(
            "  python query_notes.py term-or <term1> [term2...]  # Search formal terms (OR)"
        )
        print(
            "  python query_notes.py op <op1> [op2...]           # Search operators (AND)"
        )
        print("  python query_notes.py tag <tag1> [tag2...]        # Search tags (AND)")
        print(
            "  python query_notes.py greek <Ψ> [Ω...]            # Search greek letters (AND)"
        )
        print(
            "  python query_notes.py list-terms                  # List all formal terms"
        )
        print(
            "  python query_notes.py list-ops                    # List all operators"
        )
        print("  python query_notes.py list-tags                   # List all tags")
        print(
            "  python query_notes.py list-greek                  # List all greek letters"
        )
        print("  python query_notes.py note <note_id>              # Show full note")
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    def safe(s):
        return s.encode("ascii", "replace").decode()

    if cmd == "list-terms":
        for term, ids in sorted(inverted["terms"].items(), key=lambda x: -len(x[1])):
            print(f"{safe(term)}: {len(ids)} notes")
    elif cmd == "list-ops":
        for op, ids in sorted(inverted["operators"].items(), key=lambda x: -len(x[1])):
            print(f"{safe(op)}: {len(ids)} notes")
    elif cmd == "list-tags":
        for tag, ids in sorted(inverted["tags"].items(), key=lambda x: -len(x[1])):
            print(f"{safe(tag)}: {len(ids)} notes")
    elif cmd == "list-greek":
        for g, ids in sorted(inverted["greek"].items(), key=lambda x: -len(x[1])):
            print(f"{safe(g)}: {len(ids)} notes")
    elif cmd == "note":
        if args:
            note_id = args[0]
            if note_id in notes_dict:
                n = notes_dict[note_id]
                print(f"=== {note_id} ===")
                print(f"Title: {n['title']}")
                print(f"Timestamp: {n['timestamp']}")
                print(f"URL: {n['url']}")
                print(f"Tags: {n['tags']}")
                print(f"Operators: {n['operators']}")
                print(f"Greek: {n['greek_letters']}")
                print(f"Terms: {n['formal_terms']}")
                print(f"Cross-refs: {n['cross_refs']}")
                print(f"\n--- BODY ---\n{n['raw_body']}")
            else:
                print(f"Note {note_id} not found")
    elif cmd in ("term", "term-or"):
        mode = "AND" if cmd == "term" else "OR"
        results = search_terms(inverted, args, mode)
        print(f"Found {len(results)} notes (mode={mode}):")
        for nid in sorted(results)[:20]:
            print(format_result(nid, notes_dict))
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more")
    elif cmd == "op":
        results = search_operators(inverted, args, "AND")
        print(f"Found {len(results)} notes with operators {args}:")
        for nid in sorted(results)[:20]:
            print(format_result(nid, notes_dict))
    elif cmd == "tag":
        results = search_tags(inverted, args, "AND")
        print(f"Found {len(results)} notes with tags {args}:")
        for nid in sorted(results)[:20]:
            print(format_result(nid, notes_dict))
    elif cmd == "greek":
        results = search_greek(inverted, args, "AND")
        print(f"Found {len(results)} notes with greek {args}:")
        for nid in sorted(results)[:20]:
            print(format_result(nid, notes_dict))
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
