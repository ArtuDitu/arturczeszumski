# Bilingual Quarto Personal Website (EN/PL)

Modern static website scaffold for a cognitive neuroscientist in professional football.

## Prerequisites

- [Quarto CLI](https://quarto.org/docs/get-started/)
- GitHub repository with `main` branch

## Local development

```bash
quarto preview
```

Build once:

```bash
quarto render
```

## Deployment (GitHub Pages)

This repo includes `.github/workflows/deploy.yml`.

1. Push to `main`.
2. The workflow renders the site and publishes to `gh-pages`.
3. In repository settings, set Pages source to `Deploy from a branch` and select `gh-pages`.

Before publishing, update `_quarto.yml`:

- `website.site-url: https://[GITHUB-USERNAME].github.io/[REPOSITORY]`

## Content structure

- English pages at root (`/`, `/about/`, `/publications/`, `/blog/`, `/resume/`, `/contact/`)
- Polish pages under `/pl/` (`/pl/`, `/pl/o-mnie/`, `/pl/publikacje/`, `/pl/blog/`, `/pl/cv/`, `/pl/kontakt/`)

## Updating publications

Publication data source files:

- `assets/publications.bib`
- `assets/publications_extra.yml`

Steps:

1. Add/modify BibTeX entries in `assets/publications.bib`.
2. Ensure each BibTeX key has optional links/tags in `assets/publications_extra.yml`.
3. Rebuild (`quarto render`) and verify filter behavior on EN/PL publications pages.

## Placeholder content to replace

- `[FULL NAME]`
- `[CURRENT ROLE]`
- `[CLUB/ORG]`
- `[EMAIL]`
- `[LINKEDIN URL]`
- `[GOOGLE SCHOLAR URL]`
- `[GITHUB URL]`
- `[ORCID URL]`

## Notes

- No backend form included (static-only hosting).
- `assets/cv.pdf` is a placeholder and should be replaced with your real CV PDF.
