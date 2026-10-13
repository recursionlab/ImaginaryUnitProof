#!/usr/bin/env python3
"""Read-only inventory for Case Xi-001 source files.

This script intentionally does NOT create, overwrite, append to, or rename any file.
It fails closed when the authoritative Word/Excel files are missing or ambiguous.
Run in Colab with: python SAFE_SOURCE_PREFLIGHT.py --root /content
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import sys
from pathlib import Path


def unique_match(root: Path, token: str, suffix: str) -> Path | None:
    matches = sorted(p for p in root.rglob(f"*{suffix}")
                     if token.casefold() in p.name.casefold() and p.is_file())
    if len(matches) == 0:
        print(f"MISSING: no *{token}*{suffix} found under {root}")
        return None
    if len(matches) > 1:
        print(f"AMBIGUOUS: {len(matches)} matches for *{token}*{suffix}:")
        for p in matches:
            print(f"  - {p}")
        return None
    return matches[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='/content', help='Directory to scan (default: /content)')
    parser.add_argument('--output', default='', help='Optional JSON report path; must not overwrite source files')
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"ERROR: root is not a directory: {root}")
        return 2

    missing_libs = [name for name in ('docx', 'openpyxl') if importlib.util.find_spec(name) is None]
    if missing_libs:
        print('MISSING LIBRARIES:', ', '.join(missing_libs))
        print('In a notebook cell, install only what is missing: %pip install python-docx openpyxl')
        print('No files have been created or changed.')
        return 3

    doc_path = unique_match(root, 'Master_Docket', '.docx')
    xlsx_path = unique_match(root, 'Tracking_Register', '.xlsx')
    if doc_path is None or xlsx_path is None:
        print('STOP: authoritative source pair not established; refusing to reconstruct a baseline from excerpts.')
        return 4

    import docx
    import openpyxl
    doc = docx.Document(str(doc_path))
    wb = openpyxl.load_workbook(str(xlsx_path), read_only=True, data_only=False)

    report = {
        'read_only': True,
        'word_path': str(doc_path),
        'word_paragraphs': len(doc.paragraphs),
        'word_tables': len(doc.tables),
        'word_headings': [p.text for p in doc.paragraphs if p.style.name.startswith('Heading')],
        'excel_path': str(xlsx_path),
        'sheets': {},
    }
    for name in wb.sheetnames:
        ws = wb[name]
        active_rows = sum(1 for row in ws.iter_rows(values_only=True) if any(v is not None for v in row))
        report['sheets'][name] = {'dimensions': ws.calculate_dimension(), 'active_rows': active_rows}
        if name in {'Decision Log', 'Change Log'}:
            report['sheets'][name]['headers'] = [v for v in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
    wb.close()

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.output:
        out = Path(args.output).expanduser().resolve()
        if out in {doc_path, xlsx_path}:
            print('ERROR: report output path collides with a source file; refusing to write.')
            return 5
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Wrote inventory report only: {out}")
    print('READ-ONLY inventory complete. Source documents were not modified.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
