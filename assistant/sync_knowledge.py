"""Regenerate knowledge.md from _pages/about.md and _config.yml.

Can be run standalone (python sync_knowledge.py) or imported by the agent tool.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ABOUT_PATH = REPO_ROOT / "_pages" / "about.md"
CONFIG_PATH = REPO_ROOT / "_config.yml"
KNOWLEDGE_PATH = Path(__file__).resolve().parent / "knowledge.md"


def _strip_front_matter(text: str) -> str:
    """Remove Jekyll YAML front matter (--- ... ---)."""
    return re.sub(r"^---\n.*?---\n", "", text, count=1, flags=re.DOTALL)


def _strip_liquid_tags(text: str) -> str:
    """Remove Liquid template tags ({% ... %} and {{ ... }})."""
    text = re.sub(r"\{%.*?%\}", "", text)
    text = re.sub(r"\{\{.*?\}\}", "", text)
    return text


def _strip_html(text: str) -> str:
    """Simplify HTML tags to plain text, keeping link hrefs."""
    text = re.sub(r'<a\s+href="([^"]*)"[^>]*>(.*?)</a>', r"\2 (\1)", text)
    text = re.sub(r"<img\s[^>]*>", "", text)
    text = re.sub(r"<div[^>]*>", "", text)
    text = re.sub(r"</div>", "", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text


def _clean_about(raw: str) -> str:
    """Process about.md into clean readable text."""
    text = _strip_front_matter(raw)
    text = _strip_liquid_tags(text)
    text = _strip_html(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_author_config(config: dict) -> str:
    """Extract author info from _config.yml into readable text."""
    author = config.get("author", {})
    lines = ["## Author Profile (from site config)"]

    field_map = {
        "name": "Name",
        "bio": "Bio",
        "location": "Location",
        "email": "Email",
        "github": "GitHub",
        "linkedin": "LinkedIn",
        "orcid": "ORCID",
        "googlescholar": "Google Scholar",
        "cv": "CV",
    }

    for key, label in field_map.items():
        val = author.get(key)
        if val and not val.startswith(("AUTHOR_", "GOOGLE_SCHOLAR")):
            lines.append(f"- {label}: {val}")

    site_desc = config.get("description", "")
    if site_desc:
        lines.append(f"- Title/Role: {site_desc}")

    return "\n".join(lines)


def generate_knowledge() -> str:
    """Generate knowledge.md content from source files."""
    about_raw = ABOUT_PATH.read_text(encoding="utf-8")
    about_clean = _clean_about(about_raw)

    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    author_section = _extract_author_config(config)

    homepage_url = f"https://{config.get('repository', '').replace('/', '.github.io', 1)}"

    knowledge = (
        f"# Van-Tuan Le - Personal Information\n\n"
        f"{author_section}\n"
        f"- Homepage: {homepage_url}\n\n"
        f"---\n\n"
        f"## Content from Homepage\n\n"
        f"{about_clean}\n"
    )
    return knowledge


def sync() -> Path:
    """Regenerate knowledge.md and return the path."""
    content = generate_knowledge()
    KNOWLEDGE_PATH.write_text(content, encoding="utf-8")
    return KNOWLEDGE_PATH


if __name__ == "__main__":
    path = sync()
    print(f"Knowledge base updated: {path}")
