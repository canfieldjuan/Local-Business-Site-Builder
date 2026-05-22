# PR: Add-Readme

## Why this slice exists

The repo has no `README.md`. A first-time visitor to the GitHub page sees only a file listing with no explanation of what the project does, how to run either pipeline, or what the reference files are for. This PR closes that gap.

The content was written code-first: every claim was verified against `pipeline.py`, `build.py`, `lib/clients.py`, `lib/images.py`, `lib/deploy.py`, `lib/email.py`, and the `examples/` prospect template before being committed to the document. No doc-only sources were used.

## Scope (this PR)

1. Add `README.md` at the repo root covering both pipelines, all CLI flags, the prospect JSON schema, the theme catalog, the reference file inventory, the model constants, the output directory layout, the fabrication discipline, and the contributing workflow.
2. Add this plan doc.

### Files touched

- `README.md` (new)
- `plans/PR-Add-Readme.md` (new)

## Mechanism

Static documentation — no runtime behavior changes. `README.md` is a standard GitHub Markdown file; GitHub renders it automatically on the repo landing page.

All factual claims are pinned to their source location:

| Claim | Source |
|---|---|
| Model names (`claude-haiku-4.5`, `claude-sonnet-4.5`, `flux.2-max`) | `lib/clients.py` L60–65 |
| Playwright thin-content threshold (8 000 chars) | `pipeline.py` L77 |
| Enrichment priority ≤ 2, six page types | `pipeline.py` L24–25, L169 |
| Deterministic hash slices `[:8]` / `[8:16]` / `[16:24]` | `build.py` L386, L351, L233 |
| Hero shape → theme coupling table | `build.py` L243–251 |
| Email draft `[VERCEL_URL_PLACEHOLDER]` validation | `build.py` L703–709 |
| `email_drafts/` sibling-dir separation | `build.py` L39–43, L687 |
| Placeholder nullify vs warn field lists | `build.py` L55–69 |
| Required prospect fields | `build.py` L51 |
| Six themes + `KNOWN_THEMES` | `build.py` L162–170 |
| Prompt caching only in `build.py` | `build.py` L488–505 (absent in `pipeline.py`) |

## Intentional

- **No architecture diagrams.** The ASCII pipeline flows in each section are sufficient for the scope of a first README; a Mermaid diagram adds maintenance surface with no proportional gain.
- **No "badges" (CI, coverage, license).** The repo has no CI pipeline or test suite today (`CLAUDE.md` line 29: "No tests, linter, or build step exist in this repo."). Adding placeholder badges would be misleading.
- **Prompt caching section is `build.py`-only.** `pipeline.py` does not send `cache_control`; documenting it there would be a fabrication bug.

## Deferred

- A `CONTRIBUTING.md` with a fuller contributor guide — deferred until there is more than one contributor or the workflow grows beyond AGENTS.md.
- Badges / CI status — deferred until a test suite lands.

## Verification

No code changes → no build or grep verification required. Spot-checks run:

```bash
# README is valid UTF-8 and renders locally
cat README.md | wc -l   # 192 lines

# Confirmed untracked only -- no accidental edits to existing files
git status
# On branch main -- Untracked files: README.md, plans/PR-Add-Readme.md
```

## Estimated diff size

2 new files, ~0 deletions. README ≈ 200 LOC, plan doc ≈ 70 LOC. Well within the 400 LOC budget.
