#!/usr/bin/env python3
"""
Substack Notes Scraper
Exports all notes from a Substack profile using the internal reader API.
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Note:
    entity_key: str
    note_id: str
    body: str
    body_json: dict
    timestamp: str
    edited_at: Optional[str]
    reaction_count: int
    reactions: dict
    restacks: int
    reply_count: int
    attachments: list
    url: str


class SubstackNotesScraper:
    def __init__(self, subdomain: str, user_id: int, cookies: Optional[dict] = None):
        self.subdomain = subdomain
        self.user_id = user_id
        self.base_url = f"https://{subdomain}.substack.com"
        self.api_url = f"{self.base_url}/api/v1/reader/feed/profile/{user_id}"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        if cookies:
            self.session.cookies.update(cookies)

    def fetch_page(self, cursor: Optional[str] = None) -> dict:
        params = {}
        if cursor:
            params["cursor"] = cursor
        resp = self.session.get(self.api_url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def parse_note(self, item: dict) -> Optional[Note]:
        if item.get("type") != "comment":
            return None
        ctx = item.get("context", {})
        if ctx.get("type") != "note":
            return None

        comment = item.get("comment", {})
        entity_key = item.get("entity_key", "")
        note_id = entity_key.replace("c-", "") if entity_key.startswith("c-") else entity_key
        
        # Date is in the comment object
        timestamp = comment.get("date", "") or item.get("date", "") or ctx.get("timestamp", "")

        return Note(
            entity_key=entity_key,
            note_id=note_id,
            body=comment.get("body", ""),
            body_json=comment.get("body_json", {}),
            timestamp=timestamp,
            edited_at=comment.get("edited_at") or item.get("edited_at"),
            reaction_count=item.get("reaction_count", 0),
            reactions=item.get("reactions", {}),
            restacks=item.get("restacks", 0),
            reply_count=item.get("children_count", 0),
            attachments=item.get("attachments", []),
            url=f"{self.base_url}/@koryogden/note/{note_id}",
        )

    def scrape_all(self, max_pages: int = 1000, delay: float = 0.5) -> List[Note]:
        all_notes = []
        cursor = None
        page = 0

        while page < max_pages:
            page += 1
            print(f"Fetching page {page}... (total notes: {len(all_notes)})")
            try:
                data = self.fetch_page(cursor)
            except requests.HTTPError as e:
                if e.response.status_code == 401:
                    print("Authentication required. Provide cookies.")
                    break
                raise

            items = data.get("items", [])
            page_notes = []
            for item in items:
                note = self.parse_note(item)
                if note:
                    page_notes.append(note)

            if not page_notes:
                print("No more notes found.")
                break

            all_notes.extend(page_notes)
            cursor = data.get("nextCursor")
            if not cursor:
                print("No next cursor - reached end.")
                break

            time.sleep(delay)

        return all_notes

    def export_json(self, notes: List[Note], output_path: Path):
        data = [asdict(n) for n in notes]
        output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Exported {len(notes)} notes to {output_path}")

    def export_markdown(self, notes: List[Note], output_path: Path):
        lines = ["# Substack Notes Export\n"]
        for note in notes:
            dt = note.timestamp.replace("T", " ").replace("Z", "")
            lines.append(f"## Note {note.note_id}")
            lines.append(f"**Date:** {dt}")
            lines.append(f"**URL:** {note.url}")
            lines.append(f"**Reactions:** {note.reaction_count} | **Restacks:** {note.restacks} | **Replies:** {note.reply_count}")
            lines.append("")
            lines.append(note.body)
            lines.append("\n---\n")
        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Exported {len(notes)} notes to {output_path}")

    def export_jsonl(self, notes: List[Note], output_path: Path):
        with output_path.open("w", encoding="utf-8") as f:
            for note in notes:
                f.write(json.dumps(asdict(note), ensure_ascii=False) + "\n")
        print(f"Exported {len(notes)} notes to {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scrape Substack Notes")
    parser.add_argument("--subdomain", default="koryogden", help="Substack subdomain")
    parser.add_argument("--user-id", type=int, default=41331873, help="User ID (from profile API)")
    parser.add_argument("--cookies", help="Path to JSON file with cookies")
    parser.add_argument("--max-pages", type=int, default=1000, help="Max pages to fetch")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests (seconds)")
    parser.add_argument("--output-dir", default="substack_notes_export", help="Output directory")
    parser.add_argument("--format", choices=["json", "markdown", "jsonl", "all"], default="all")
    args = parser.parse_args()

    cookies = None
    if args.cookies:
        cookies = json.loads(Path(args.cookies).read_text())

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    scraper = SubstackNotesScraper(args.subdomain, args.user_id, cookies)
    notes = scraper.scrape_all(max_pages=args.max_pages, delay=args.delay)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.format in ("json", "all"):
        scraper.export_json(notes, output_dir / f"notes_{timestamp}.json")
    if args.format in ("markdown", "all"):
        scraper.export_markdown(notes, output_dir / f"notes_{timestamp}.md")
    if args.format in ("jsonl", "all"):
        scraper.export_jsonl(notes, output_dir / f"notes_{timestamp}.jsonl")

    print(f"\nDone! Total notes: {len(notes)}")


if __name__ == "__main__":
    main()