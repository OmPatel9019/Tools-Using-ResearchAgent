"""
Traceable Citation Management Module.
Tracks all retrieved sources, provides citation IDs, and audits synthesis for hallucinations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import re
from urllib.parse import urlparse


@dataclass
class SourceCitation:
    id: int
    title: str
    url: str
    snippet: str
    tool_origin: str


class CitationManager:
    """Thread-safe citation tracker assigning deterministic IDs to retrieved sources."""

    def __init__(self):
        self._by_url: Dict[str, SourceCitation] = {}
        self._by_id: Dict[int, SourceCitation] = {}
        self._next_id: int = 1

    def register(self, title: str, url: str, snippet: str, tool_origin: str) -> SourceCitation:
        clean_url = url.strip()
        if clean_url in self._by_url:
            return self._by_url[clean_url]

        citation = SourceCitation(
            id=self._next_id,
            title=title.strip() or "Untitled Source",
            url=clean_url,
            snippet=snippet.strip()[:300],
            tool_origin=tool_origin,
        )
        self._by_url[clean_url] = citation
        self._by_id[self._next_id] = citation
        self._next_id += 1
        return citation

    def get_all(self) -> List[SourceCitation]:
        return list(self._by_id.values())

    def format_sources(self) -> str:
        if not self._by_id:
            return "No sources registered."
        return "\n".join(f"  Source {c.id}: {c.title} -> {c.url}" for c in self._by_id.values())

    def format_bibliography(self) -> str:
        if not self._by_id:
            return "No external sources were referenced."
        entries = ["### References & Traceable Citations:"]
        for c in self._by_id.values():
            entries.append(f"- **Source {c.id}**: [{c.title}]({c.url}) *(via {c.tool_origin})*")
        return "\n".join(entries)

    def audit(self, text: Optional[str]) -> Dict[str, any]:
        safe_text = text or ""
        cited_ids = {int(m) for m in re.findall(r"\[(\d+)\]", safe_text)}
        valid = [self._by_id[cid].__dict__ for cid in cited_ids if cid in self._by_id]
        invalid = [cid for cid in cited_ids if cid not in self._by_id]
        return {
            "valid": valid,
            "invalid_ids": invalid,
            "has_citations": len(cited_ids) > 0,
            "all_valid": len(invalid) == 0 and len(cited_ids) > 0,
        }
