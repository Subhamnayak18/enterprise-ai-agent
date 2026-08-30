from dataclasses import dataclass
from pathlib import Path
import re

from app.core.config import get_settings


@dataclass
class Document:
    text: str
    metadata: dict


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    metadata = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata, parts[2].lstrip()


def load_documents(path: Path | None = None) -> list[Document]:
    base = path or get_settings().documents_path
    documents = []
    if not Path(base).exists():
        return documents
    for file in sorted(Path(base).rglob("*")):
        if file.suffix.lower() not in {".md", ".txt"} or "uploads/.gitkeep" in str(file):
            continue
        text = file.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(text)
        metadata = {
            "document_name": frontmatter.get("document_name", file.stem.replace("_", " ").title()),
            "document_type": frontmatter.get("document_type", "policy"),
            "department": frontmatter.get("department", "Operations"),
            "policy_version": frontmatter.get("policy_version", "1.0"),
            "effective_date": frontmatter.get("effective_date", "2026-01-01"),
            "source": str(file.relative_to(base)),
        }
        documents.append(Document(text=body, metadata=metadata))
    return documents
