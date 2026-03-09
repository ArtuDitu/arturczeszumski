# CV Pipeline

This project uses **Quarto + structured YAML data + BibLaTeX** to generate a polished PDF CV from maintainable source files. Quarto was chosen because it is already available in the environment, works cleanly with LaTeX-quality PDF output, and lets the content stay separated from the layout. The design layer is custom rather than based on a stock template.

## Project Structure

- `cv.qmd`: main rendering document that defines section order.
- `_quarto.yml`: single-command build configuration.
- `data/profile.yml`: header, bio, contact details, and focus areas.
- `data/employment.yml`: experience timeline entries.
- `data/education.yml`: education timeline entries.
- `data/talks.yml`: structured public talks list.
- `data/teaching.yml`: teaching experience entries.
- `data/awards.yml`: awards and grants entries.
- `data/publications.yml`: publication groups and selected BibTeX keys.
- `data/review_notes.yml`: unresolved conflicts extracted from legacy CVs.
- `bib/publications.bib`: source bibliography used for publication rendering.
- `theme/preamble.tex`: visual system, typography, timeline, and bibliography styling.
- `scripts/build_cv.py`: pre-render step that turns YAML and BibTeX selections into LaTeX fragments.
- `scripts/extract_legacy_cvs.py`: optional helper to re-extract text from legacy PDFs into `build/legacy_text/`.
- `output/`: rendered PDF output.

## Why This Stack

- Structured data is easy to edit and version-control.
- Quarto provides a stable, one-command build entry point.
- LaTeX gives reliable PDF layout and strong typography.
- Publications stay sourced from the `.bib` file and can be regrouped by editing only `data/publications.yml`.

## Editing Content

- Update name, bio, contact details, and focus areas in `data/profile.yml`.
- Add or edit jobs in `data/employment.yml`.
- Add or edit degrees in `data/education.yml`.
- Add or edit talks in `data/talks.yml`.
- Add or edit teaching entries in `data/teaching.yml`.
- Add or edit awards in `data/awards.yml`.
- Change publication groupings or inclusion in `data/publications.yml`.
- Review unresolved date/contact issues in `data/review_notes.yml`.

Each timeline entry is self-contained. Adding a new role or degree should only require appending one YAML object to the relevant file.

## Rebuild the CV

Run:

```bash
quarto render cv.qmd
```

The generated PDF will be written to:

- `output/cv.pdf`

Quarto also keeps an intermediate `.tex` file in `output/` for debugging layout issues.

## Publications

Publication formatting is driven by `bib/publications.bib`. The build script reads `data/publications.yml`, extracts the selected BibTeX entries into grouped temporary `.bib` files under `build/bib/`, and the PDF uses BibLaTeX to format them consistently.

To add a publication:

1. Add the entry to `bib/publications.bib`.
2. Add its BibTeX key to the appropriate group in `data/publications.yml`.
3. Re-render with `quarto render cv.qmd`.

## Legacy Extraction Helper

If you want to revisit the older PDFs and compare them again, run:

```bash
python3 scripts/extract_legacy_cvs.py
```

That writes extracted text and detected URLs to `build/legacy_text/`.

## Dependencies

- Quarto
- TeX Live with `lualatex` and `biber`
- Python 3 with `PyYAML`

## Manual Review Still Needed

The current normalized data includes explicit review notes for:

- preferred primary email/contact details
- current public location
- Legia role dating and whether it should be split
- exact University of Bielefeld end month
- exact duration of the KANSEI visit
- completeness of the public talks list
