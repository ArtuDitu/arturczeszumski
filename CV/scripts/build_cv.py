from __future__ import annotations

from pathlib import Path
import re
import textwrap
import yaml


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
BUILD_DIR = ROOT / "build"
BIB_BUILD_DIR = BUILD_DIR / "bib"


def load_yaml(name: str):
    with (DATA_DIR / name).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def latex_escape(value: str) -> str:
    if value is None:
        return ""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def href(url: str, label: str) -> str:
    safe_url = url.replace("%", r"\%").replace("#", r"\#")
    return rf"\href{{{safe_url}}}{{{latex_escape(label)}}}"


def render_tags(tags: list[str]) -> str:
    return "".join(rf"\cvtag{{{latex_escape(tag)}}}" for tag in tags)


def render_list(items: list[str]) -> str:
    body = "\n".join(rf"  \item {latex_escape(item)}" for item in items)
    return "\\begin{itemize}\n" + body + "\n\\end{itemize}"


def render_contact(contact: dict) -> str:
    value = latex_escape(contact["value"])
    if contact.get("link"):
        value = href(contact["link"], contact["value"])
    icon = latex_escape(contact.get("icon", "circle"))
    return rf"\contactitem{{\faIcon{{{icon}}}}}{{{value}}}"


def render_header(profile: dict) -> str:
    contacts = "\n".join(render_contact(item) for item in profile["contacts"])
    focus = render_tags(profile["focus"])
    return textwrap.dedent(
        f"""
        \\begin{{minipage}}[t]{{0.44\\textwidth}}
        \\vspace{{0pt}}
        {{\\cvnamestyle {latex_escape(profile["name"])}}}\\\\[0.35em]
        {{\\cvheadlinestyle {latex_escape(profile["headline"])}}}\\\\[1.15em]
        {contacts}
        \\end{{minipage}}
        \\hfill
        \\begin{{minipage}}[t]{{0.52\\textwidth}}
        \\vspace{{0pt}}
        \\HeaderLogo{{logo.png}}
        \\vspace{{0.85em}}
        \\begin{{cvprofilebox}}
        {latex_escape(profile["profile"])}

        \\vspace{{0.8em}}
        {focus}
        \\end{{cvprofilebox}}
        \\end{{minipage}}

        \\vspace{{1.5em}}
        """
    ).strip() + "\n"


def timeline_marker(position: str) -> str:
    markers = {
        "only": r"\TimelineGlyphOnly",
        "first": r"\TimelineGlyphFirst",
        "middle": r"\TimelineGlyphMiddle",
        "last": r"\TimelineGlyphLast",
    }
    return markers[position]


def render_timeline_left(
    title: str,
    org: str,
    location: str,
    date_label: str,
    category: str | None,
) -> str:
    meta = latex_escape(location)
    if category:
        meta += rf" \textbullet\ {latex_escape(category)}"
    return (
        r"\begin{minipage}[t]{\linewidth}"
        + "\n"
        + rf"{{\cvdaterange {latex_escape(date_label)}}}\par"
        + "\n"
        + rf"{{\cvitemtitle {latex_escape(title)}}}\par"
        + "\n"
        + rf"{{\cvitemorg {latex_escape(org)}}}\par"
        + "\n"
        + rf"{{\cvitemmeta {meta}}}"
        + "\n\\end{minipage}"
    )


def render_timeline_right(highlights: list[str], tags: list[str]) -> str:
    return (
        r"\begin{TimelineDetailWrap}"
        + "\n"
        + r"\begin{cvdetailbox}"
        + "\n"
        + render_list(highlights)
        + "\n\\vspace{0.3em}\n"
        + render_tags(tags)
        + "\n\\end{cvdetailbox}"
        + "\n\\end{TimelineDetailWrap}"
    )


def render_timeline(entries: list[dict], title_key: str, org_key: str) -> str:
    blocks = []
    total = len(entries)
    for index, entry in enumerate(entries):
        if total == 1:
            position = "only"
        elif index == 0:
            position = "first"
        elif index == total - 1:
            position = "last"
        else:
            position = "middle"
        left = render_timeline_left(
            entry[title_key],
            entry[org_key],
            entry["location"],
            entry["date_label"],
            entry.get("category"),
        )
        right = render_timeline_right(entry["highlights"], entry["tags"])
        blocks.append(rf"\TimelineEntry{{{timeline_marker(position)}}}{{{left}}}{{{right}}}")
    return "\\begin{cvtimeline}\n" + "\n\n".join(blocks) + "\n\\end{cvtimeline}\n"


MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def parse_partial_date(value: str) -> tuple[int, int, int]:
    text = value.strip().lower()
    if not text:
        return (0, 0, 0)
    if "present" in text:
        return (9999, 12, 31)
    month = 0
    for key, number in MONTHS.items():
        if re.search(rf"\b{key}\b", text):
            month = number
            break
    years = [int(match) for match in re.findall(r"\b(?:19|20)\d{2}\b", text)]
    if years:
        return (max(years), month, 1)
    return (0, month, 0)


def render_talks(talks: list[dict]) -> str:
    ordered_talks = sorted(
        talks,
        key=lambda talk: parse_partial_date(str(talk.get("sort_date", talk["date_label"]))),
        reverse=True,
    )
    blocks = []
    for talk in ordered_talks:
        meta = f"{talk['event']} | {talk['location']}"
        if talk.get("organizer"):
            meta = f"{talk['event']} | {talk['organizer']} | {talk['location']}"
        extra = ""
        if talk.get("note"):
            extra += rf"\par{{\footnotesize\color{{cvmuted}} {latex_escape(talk['note'])}}}"
        if talk.get("link"):
            extra += rf"\par{{\footnotesize {href(talk['link'], talk['link'])}}}"
        blocks.append(
            textwrap.dedent(
                f"""
                \\begin{{talkbox}}
                \\begin{{tabularx}}{{\\linewidth}}{{@{{}}p{{0.18\\linewidth}}X@{{}}}}
                {{\\cvdaterange {latex_escape(talk["date_label"])}}} & {{\\cvtalktitle {latex_escape(talk["title"])}}}\\\\[-0.15em]
                {{\\footnotesize\\color{{cvaccent}}\\sffamily {latex_escape(talk["type"])}}} & {{\\cvtalkmeta {latex_escape(meta)}}}{extra}
                \\end{{tabularx}}
                \\end{{talkbox}}
                """
            ).strip()
        )
    blocks.append(r"\sectionnote{Additionally, I have presented more than 30 posters at scientific meetings.}")
    return "\n\n".join(blocks) + "\n"


def parse_year_range(value: str) -> tuple[int, int, int]:
    text = value.strip()
    if not text:
        return (0, 0, 0)
    match = re.search(r"\b(19|20)\d{2}\s*/\s*(\d{2,4})\b", text)
    if match:
        start_year = int(match.group(0).split("/")[0])
        end_part = match.group(2)
        if len(end_part) == 2:
            century = str(start_year)[:2]
            end_year = int(century + end_part)
        else:
            end_year = int(end_part)
        return (end_year, 12, 31)
    years = [int(match) for match in re.findall(r"\b(?:19|20)\d{2}\b", text)]
    if years:
        return (max(years), 12, 31)
    return parse_partial_date(text)


def render_teaching(teaching: list[dict]) -> str:
    ordered_teaching = sorted(teaching, key=lambda entry: parse_year_range(str(entry["year"])), reverse=True)
    blocks = [r"\sectionnote{I have supervised more than 30 BSc and MSc theses.}"]
    for entry in ordered_teaching:
        meta_parts = [entry["university"]]
        if entry.get("level"):
            meta_parts.append(entry["level"])
        meta = " | ".join(meta_parts)
        blocks.append(
            textwrap.dedent(
                f"""
                \\begin{{talkbox}}
                \\begin{{tabularx}}{{\\linewidth}}{{@{{}}p{{0.18\\linewidth}}X@{{}}}}
                {{\\cvdaterange {latex_escape(entry["year"])}}} & {{\\cvtalktitle {latex_escape(entry["course"])}}}\\\\[-0.15em]
                & {{\\cvtalkmeta {latex_escape(meta)}}}
                \\end{{tabularx}}
                \\end{{talkbox}}
                """
            ).strip()
        )
    return "\n\n".join(blocks) + "\n"


def render_awards(awards: list[dict]) -> str:
    ordered_awards = sorted(awards, key=lambda entry: parse_partial_date(str(entry["date"])), reverse=True)
    blocks = []
    for entry in ordered_awards:
        meta_parts = []
        if entry.get("event"):
            meta_parts.append(entry["event"])
        if entry.get("location"):
            meta_parts.append(entry["location"])
        meta = " | ".join(meta_parts)
        extra = ""
        if entry.get("description"):
            extra = rf"\par{{\footnotesize\color{{cvmuted}} {latex_escape(entry['description'])}}}"
        blocks.append(
            textwrap.dedent(
                f"""
                \\begin{{talkbox}}
                \\begin{{tabularx}}{{\\linewidth}}{{@{{}}p{{0.18\\linewidth}}X@{{}}}}
                {{\\cvdaterange {latex_escape(entry["date"])}}} & {{\\cvtalktitle {latex_escape(entry["title"])}}}\\\\[-0.15em]
                & {{\\cvtalkmeta {latex_escape(meta)}}}{extra}
                \\end{{tabularx}}
                \\end{{talkbox}}
                """
            ).strip()
        )
    return "\n\n".join(blocks) + "\n"


def split_bib_entries(text: str) -> dict[str, str]:
    entries = {}
    index = 0
    length = len(text)
    while index < length:
        at_pos = text.find("@", index)
        if at_pos == -1:
            break
        brace_pos = text.find("{", at_pos)
        if brace_pos == -1:
            break
        depth = 1
        cursor = brace_pos + 1
        while cursor < length and depth:
            char = text[cursor]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            cursor += 1
        entry = text[at_pos:cursor].strip()
        key_part = text[brace_pos + 1 : text.find(",", brace_pos)]
        entries[key_part.strip()] = entry
        index = cursor
    return entries


def render_publications(config: dict) -> str:
    source_bib = (ROOT / "bib" / "publications.bib").read_text(encoding="utf-8")
    entries = split_bib_entries(source_bib)
    sections = []

    for group in config["groups"]:
        bib_path = BIB_BUILD_DIR / f"{group['file_slug']}.bib"
        selected_entries = []
        missing = []
        for key in group["keys"]:
            if key in entries:
                selected_entries.append(entries[key])
            else:
                missing.append(key)
        bib_path.write_text("\n\n".join(selected_entries).strip() + "\n", encoding="utf-8")
        if missing:
            raise SystemExit(f"Missing bibliography keys for group {group['title']}: {', '.join(missing)}")
        sections.append(
            textwrap.dedent(
                f"""
                \\subsection*{{{latex_escape(group["title"])}}}
                \\begin{{refsection}}[{latex_escape(str(bib_path.relative_to(ROOT)))}]
                \\nocite{{*}}
                \\printbibliography[heading=none]
                \\end{{refsection}}
                """
            ).strip()
        )
    return "\n\n".join(sections) + "\n"


def render_review_notes(notes: list[dict]) -> str:
    lines = ["# Manual Review Notes", ""]
    for note in notes:
        lines.append(f"## {note['topic']}")
        lines.append(f"- Status: {note['status']}")
        lines.append(f"- Current choice: {note['current_choice']}")
        for detail in note["notes"]:
            lines.append(f"- {detail}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    BUILD_DIR.mkdir(exist_ok=True)
    BIB_BUILD_DIR.mkdir(exist_ok=True)

    profile = load_yaml("profile.yml")
    employment = load_yaml("employment.yml")
    education = load_yaml("education.yml")
    talks = load_yaml("talks.yml")
    teaching = load_yaml("teaching.yml")
    awards = load_yaml("awards.yml")
    publications = load_yaml("publications.yml")
    review_notes = load_yaml("review_notes.yml")

    write(BUILD_DIR / "generated-title.tex", render_header(profile))
    write(BUILD_DIR / "generated-experience.tex", render_timeline(employment, "role", "organization"))
    write(BUILD_DIR / "generated-education.tex", render_timeline(education, "degree", "institution"))
    write(BUILD_DIR / "generated-talks.tex", render_talks(talks))
    write(BUILD_DIR / "generated-teaching.tex", render_teaching(teaching))
    write(BUILD_DIR / "generated-awards.tex", render_awards(awards))
    write(BUILD_DIR / "generated-publications.tex", render_publications(publications))
    write(BUILD_DIR / "review-notes.md", render_review_notes(review_notes))


if __name__ == "__main__":
    main()
