from __future__ import annotations

from pathlib import Path
import re

from Foundation import NSURL
from Quartz import PDFDocument


ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "old_CVs"
TARGET_DIR = ROOT / "build" / "legacy_text"
URL_PATTERN = re.compile(r"https?://[^\s)>]+")


def extract_text(path: Path) -> str:
    url = NSURL.fileURLWithPath_(str(path.resolve()))
    document = PDFDocument.alloc().initWithURL_(url)
    if document is None:
        raise RuntimeError(f"Could not load {path}")
    parts = []
    for page_index in range(document.pageCount()):
        page = document.pageAtIndex_(page_index)
        if page is not None and page.string():
            parts.append(str(page.string()))
    return "\n".join(parts).strip() + "\n"


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    url_lines = []
    for pdf_path in sorted(SOURCE_DIR.glob("*.pdf")):
        text = extract_text(pdf_path)
        (TARGET_DIR / f"{pdf_path.stem}.txt").write_text(text, encoding="utf-8")
        url_lines.append(f"## {pdf_path.name}")
        unique_urls = sorted(set(URL_PATTERN.findall(text)))
        if unique_urls:
            url_lines.extend(f"- {url}" for url in unique_urls)
        else:
            url_lines.append("- No URLs detected in extracted text.")
        url_lines.append("")
    (TARGET_DIR / "detected-urls.md").write_text("\n".join(url_lines).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
