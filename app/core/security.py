from pathlib import Path

ALLOWED_DOCUMENT_SUFFIXES = {".md", ".txt"}
INJECTION_MARKERS = (
    "ignore previous instructions",
    "ignore system instructions",
    "reveal system prompt",
    "developer message",
    "system message",
)


def safe_filename(name: str) -> str:
    return Path(name).name.replace(" ", "_")


def contains_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in INJECTION_MARKERS)


def sanitize_retrieved_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if contains_prompt_injection(line):
            lines.append("[Potential prompt-injection text removed from retrieved data]")
        else:
            lines.append(line)
    return "\n".join(lines)
