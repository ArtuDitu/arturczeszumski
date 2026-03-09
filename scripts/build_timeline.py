#!/usr/bin/env python3
"""
build_timeline.py

Reads CV YAML data (CV/data/employment.yml and CV/data/education.yml) and
generates _includes/timeline-en.html for inclusion in resume.qmd.

Run automatically as a Quarto pre-render step. The CV data is the source of
truth; this script keeps the webpage timeline in sync without manual editing.
"""

import html
import re
import yaml
from pathlib import Path

MONTH_MAP = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
}


def parse_start_date(date_label: str) -> tuple:
    """Return (year, month) for sorting newest-first."""
    start = date_label.strip().split(' - ')[0].strip()
    m = re.match(r'([A-Za-z]{3})\s+(\d{4})', start)
    if m:
        return (int(m.group(2)), MONTH_MAP.get(m.group(1), 0))
    m = re.match(r'^(\d{4})$', start)
    if m:
        return (int(m.group(1)), 0)
    return (0, 0)


def extract_country(location: str):
    """Return the country portion of a single-country location, else None."""
    if not location or ' / ' in location:
        return None
    parts = location.rsplit(',', 1)
    return parts[-1].strip() if len(parts) == 2 else None


def make_title(role: str, org: str, location: str) -> str:
    role = html.escape((role or '').strip())
    org = (org or '').strip()
    country = extract_country(location or '')
    title = f"{role} · {html.escape(org)}" if org else role
    if country:
        title += f" ({html.escape(country)})"
    return title


def render_item(title: str, date_label: str, tags: list, highlights: list) -> str:
    chips = '\n'.join(f'<span class="chip">{html.escape(t)}</span>' for t in tags)
    bullets = '\n'.join(f'<li>{html.escape(h)}</li>' for h in highlights)
    return (
        '<div class="timeline-item reveal">\n'
        '<div class="timeline-skills">\n'
        '<div class="chip-wrap">\n'
        f'{chips}\n'
        '</div>\n'
        '</div>\n'
        '<div class="timeline-center">\n'
        '<div class="timeline-node"></div>\n'
        f'{html.escape(date_label)}\n'
        '</div>\n'
        '<div class="timeline-content">\n'
        f'<h3>{title}</h3>\n'
        '<ul>\n'
        f'{bullets}\n'
        '</ul>\n'
        '</div>\n'
        '</div>'
    )


def main():
    root = Path(__file__).resolve().parent.parent
    cv_data = root / 'CV' / 'data'

    with open(cv_data / 'employment.yml', encoding='utf-8') as f:
        employment = yaml.safe_load(f) or []
    with open(cv_data / 'education.yml', encoding='utf-8') as f:
        education = yaml.safe_load(f) or []

    items = []
    yaml_index = 0

    for e in employment:
        date_label = e.get('date_label', '')
        items.append({
            'sort_key': parse_start_date(date_label),
            'is_present': 'present' in date_label.lower(),
            'yaml_index': yaml_index,
            'date_label': date_label,
            'title': make_title(
                e.get('role', ''),
                e.get('organization', ''),
                e.get('location', ''),
            ),
            'tags': e.get('tags', []),
            'highlights': e.get('highlights', []),
        })
        yaml_index += 1

    for ed in education:
        date_label = ed.get('date_label', '')
        items.append({
            'sort_key': parse_start_date(date_label),
            'is_present': 'present' in date_label.lower(),
            'yaml_index': yaml_index,
            'date_label': date_label,
            'title': make_title(
                ed.get('degree', ''),
                ed.get('institution', ''),
                ed.get('location', ''),
            ),
            'tags': ed.get('tags', []),
            'highlights': ed.get('highlights', []),
        })
        yaml_index += 1

    # Current jobs (containing "Present") keep their YAML file order so the
    # author controls which role appears first. Past jobs are sorted by start
    # date newest-first. Current jobs always appear above past jobs.
    def sort_key(item):
        if item['is_present']:
            return (0, item['yaml_index'], 0, 0)
        year, month = item['sort_key']
        return (1, -year, -month, 0)

    items.sort(key=sort_key)

    rendered = '\n\n'.join(
        render_item(i['title'], i['date_label'], i['tags'], i['highlights'])
        for i in items
    )
    timeline_html = f'<div class="timeline">\n{rendered}\n</div>\n'

    out_path = root / '_includes' / 'timeline-en.html'
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(timeline_html, encoding='utf-8')
    print(f'[build_timeline] {len(items)} entries → {out_path.relative_to(root)}')


if __name__ == '__main__':
    main()
