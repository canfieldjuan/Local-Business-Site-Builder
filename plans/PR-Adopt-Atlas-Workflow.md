# PR-Adopt-Atlas-Workflow

## Why this slice exists

User reviewed canfieldjuan/ATLAS PRs #629 / #631 / #632 / #635 on
2026-05-19 and observed that this repo
(canfieldjuan/Local-Business-Site-Builder) had drifted from the
plan-driven PR-shape contract documented in ATLAS's `AGENTS.md`.

Recent LBSB PRs (#7 through #15) shipped with informal narrative
bodies (`## Summary` / `## File map` / `## Test plan`) instead of
ATLAS's structured `Plan: plans/PR-<name>.md` framing with
`Intentional` / `Deferred` / `Verification` / `Diff size`
sections. The reviewer (Copilot in this repo today, possibly a
separate Claude reviewer session later) had to reverse-engineer
each PR's intentional trade-offs from prose rather than reading
them from a fixed contract.

User explicitly directed: **"Yes -- mirror ATLAS exactly"** for
future PRs, and **"Only prospective"** for retrofit scope (PR #15
is the last informal-style PR; from this slice onward every new
PR ships with the ATLAS contract). This slice is the bootstrap
that adds the contract and its supporting infrastructure to LBSB.

## Scope (this PR)

1. Add `AGENTS.md` at the repo root -- LBSB-adapted port of
   ATLAS's `AGENTS.md`. The PR-shape contract (sections 1, 6),
   builder workflow (3a, 3c), and within-session agent routing
   (5a, 5d) port near-verbatim. ATLAS-specific bits (per-package
   guardrails for `extracted_content_pipeline`, mcp drift
   audits, reviewer-session bootstrap) are dropped because LBSB
   doesn't have those substrates yet; AGENTS.md notes them as
   deferred.
2. Add `plans/PR-Adopt-Atlas-Workflow.md` -- this file. First
   plan doc in the new `plans/` directory; subsequent slices add
   one per PR.
3. Add `scripts/local_pr_review.sh` -- LBSB-simplified port of
   ATLAS's mechanical local-review bundle. v1 runs three checks:
   worktree-clean, `git diff --check`, and "at least one
   `plans/PR-*.md` touched in the diff" (the plan-doc presence
   check). ATLAS's plan/code consistency Python audit
   (`scripts/audit_plan_code_consistency.py`) is deferred.

### Files touched

- `AGENTS.md` (new, ~280 LOC)
- `plans/PR-Adopt-Atlas-Workflow.md` (new, this file, ~90 LOC)
- `scripts/local_pr_review.sh` (new, ~80 LOC; executable)

## Mechanism

The bootstrap is self-evidencing: this PR itself follows the
contract it introduces. The PR title is `Plan:
PR-Adopt-Atlas-Workflow`, the branch is
`claude/pr-adopt-atlas-workflow`, the body mirrors the plan-doc
sections, and `scripts/local_pr_review.sh` is runnable against
this very diff before push.

No runtime code changes. No prompt changes. No `build.py`,
`lib/`, or `references/*` edits in this slice. Everything is
process / contract / supporting tooling.

## Intentional

- This does not change any LLM prompt, generation pipeline, or
  user-facing build behavior. The skill produces the same output
  before and after this PR.
- This does not retrofit PR #15 (still open at time of writing)
  to the new style. User explicitly chose "Only prospective."
- AGENTS.md is intentionally LBSB-shaped, not a verbatim copy of
  ATLAS's. ATLAS's references to `extracted_content_pipeline`,
  `atlas_brain` manifest sync, MCP port audits, and the
  reviewer-session bootstrap block (`AUDITOR_PROMPT.md`,
  REVIEWER_BOOTSTRAP) are dropped because LBSB has none of those
  substrates. The LBSB-specific guardrails (fabrication discipline
  via the `[TRUST_TRAILER]` / `[SERVICE_PROMISE]` placeholders,
  the deterministic harness selection layer in `build.py`, the
  trade-default ruleset in `07-industry-defaults.md`) are
  documented as the local equivalents.
- `scripts/local_pr_review.sh` v1 runs three checks only; ATLAS's
  fuller bundle (pre-push audit wrapper + plan/code consistency
  Python audit + audit-script-fixture rule) is named in Deferred
  rather than ported now. The three checks here catch the most
  common pre-push failures (dirty worktree, whitespace
  corruption, missing plan doc) and are enough to seat the
  workflow.

## Deferred

- `AUDITOR_PROMPT.md` and the reviewer-session bootstrap block
  (ATLAS AGENTS.md section 8). LBSB doesn't have a separate
  Claude reviewer session yet -- the GitHub-Copilot bot review
  is the current second pair of eyes. Adding the reviewer-session
  workflow makes sense once the build skill is in prospect-pitch
  production and PRs warrant deeper independent audit.
- `scripts/audit_plan_code_consistency.py` -- ATLAS's Python
  audit that verifies each plan doc's "Files touched" list
  matches the actual diff. v2 follow-up; not blocking for the
  bootstrap.
- `scripts/install_local_pr_hook.sh` -- ATLAS's installer for
  the optional pre-push git hook. Nice-to-have; user can opt in
  later by hand if they want.
- Retrofitting older PRs (#7-#15) to the new style. Explicit
  user "Only prospective" directive.
- An LBSB-shaped `BUILD_SPEC.md` / `CANONICAL.md` /
  `INTEGRATION_MAP.md` set (the supporting docs ATLAS's AGENTS.md
  cross-references). LBSB doesn't have multiple competing
  implementations to disambiguate, and the existing
  `CLAUDE.md` + `references/*.md` already serve the role those
  ATLAS docs play.

## Verification

- `git diff --check` -> passed.
- `bash scripts/local_pr_review.sh` -> passed (catches: worktree
  clean, no whitespace damage, at least one `plans/PR-*.md`
  touched in this diff).
- `chmod +x scripts/local_pr_review.sh` applied; script is
  executable.
- Plan-doc presence: this file (`plans/PR-Adopt-Atlas-Workflow.md`)
  exists with all seven sections (Why / Scope / Mechanism /
  Intentional / Deferred / Verification / Estimated diff size)
  per the AGENTS.md contract being introduced.
- Self-evidencing: this PR's body and commit message mirror the
  plan-doc framing (`Plan:` lead line + `## Intentional` /
  `## Deferred` / `## Verification` / `## Diff size`).

## Estimated diff size

| Area | Estimated LOC |
|---|---:|
| `AGENTS.md` | ~280 |
| `plans/PR-Adopt-Atlas-Workflow.md` (this file) | ~90 |
| `scripts/local_pr_review.sh` | ~80 |
| **Total** | **~450** |

Marginally over the 400 LOC soft budget. Justified: this is a
one-time workflow-bootstrap PR that introduces the contract
itself; the three artifacts are inseparable because the plan-doc
contract, AGENTS.md spec, and local review tool all reference
each other and need to ship in one slice for the bootstrap to be
coherent. Subsequent slices should respect the budget.
