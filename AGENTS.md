# AGENTS.md -- Local-Business-Site-Builder PR workflow

This file is the **PR-shape contract** every change in this repo
ships against. Ported (with LBSB-specific adaptations) from
`canfieldjuan/ATLAS/AGENTS.md`, which is the canonical reference
across Juan's repos. When the two disagree, ATLAS wins -- this
document is intentionally a subset.

LBSB today runs single-session: one Claude Code session builds
each PR, and GitHub's Copilot bot provides the independent second
read. The reviewer-session pattern that ATLAS uses (a separate
Claude session that audits each PR with BLOCKER / MAJOR / NIT /
LGTM verdicts) is intentionally deferred -- see Deferred in
`plans/PR-Adopt-Atlas-Workflow.md`.

---

## 1. PR shape

Every non-trivial change ships as a single PR with the following
artifacts:

### 1a. Plan doc (`plans/PR-<Slice-Name>.md`)

Required sections, in this order:

| Section | Purpose |
|---|---|
| **Why this slice exists** | What's broken / what's missing / what audit item this closes. Tie to a prior plan, an LBSB issue, or a concrete user request. |
| **Scope (this PR)** | The narrow surface this PR touches. Numbered list of intent. List of files in a "Files touched" subsection. |
| **Mechanism** | Short prose (and code stub if helpful) explaining *how* the change works -- enough that a reviewer doesn't have to reverse-engineer it from the diff. |
| **Intentional** | Things that look wrong but aren't -- explicit trade-offs and rejected alternatives ("no inline cross-reference at each tier subhead because the strong intro scope language does the work"). Saves reviewer cycles. |
| **Deferred** | Things explicitly punted to a follow-up slice. Each item should name the future PR or describe what would unlock it. |
| **Verification** | The specific commands the builder ran locally + their pass counts. Reviewer (Copilot or human) can reproduce. |
| **Estimated diff size** | LOC budget; flag if approaching 400 LOC. |

### 1b. PR body

Mirror the plan-doc framing in the PR description:

```
Plan: plans/PR-<Slice-Name>.md

<one-paragraph why>

## Intentional
- ...

## Deferred
- ...

## Verification
- ...

## Diff size
N files, +X / -Y
```

### 1c. Commit message

Same `Plan: ...` lead line + `Intentional` / `Deferred` sections
as the PR body. Squash-merge collapses to one canonical commit at
merge time.

### 1d. Diff budget

Target **<400 LOC** per PR. Soft cap; over-budget PRs ship if the
slice is genuinely indivisible, but the plan doc must justify the
overage in **Why this slice exists**.

### 1e. Branch naming

`claude/pr-<slice-name>` for builder branches (lowercase, kebab).
`claude/<topic>` for non-PR scratch.

If a future Codex or other-assistant session opens PRs in this
repo, follow the ATLAS convention of `<assistant>/pr-<slice-name>`
to keep per-assistant lanes legible.

### 1f. Open as draft

For LBSB v1, opening as draft is optional -- Copilot reviews
non-drafts automatically, which is what we want. If a separate
Claude reviewer session is added later (per ATLAS's pattern),
move to "open as draft until reviewer LGTM."

---

## 2. Builder workflow

### 2a. Plan first

Open `plans/PR-<Slice-Name>.md` and write the full plan doc
**before** any code change. The plan is the contract; the code is
the implementation of the contract.

If the plan changes mid-implementation (you discovered something
the plan missed), update the plan doc in the same commit. The
plan and code ship together.

### 2b. LBSB-specific guardrails (the fabrication discipline)

This repo's defining constraint is **never fabricate prospect
facts**. The pipeline produces sales-asset websites for real
small-business prospects; a fabricated review count, certification,
or business-practice claim is a credibility-breaking bug.

Before pushing any change that touches `references/*.md`,
`build.py`, `lib/`, or anything that flows into the generated
HTML, the builder runs at least one fixture build and confirms:

```bash
./venv/bin/python build.py examples/prospect-plumber-template.json \
    --skip-image-gen --skip-email-draft --skip-deploy

# Inspect the rendered HTML:
grep -cE '\[TRUST_TRAILER\]|\[SERVICE_PROMISE\]|\[TRADE_DISPLAY\]|\[CITY\]|\[YEARS\]|\[SERVICE_AREA\]' \
    outputs/builds/drees-plumbing-inc/index.html
# Expect: 0 (placeholder leak check)

grep -ciE 'Upfront Flat-Rate|Surprise Fees|Free Estimates|Owner Answers' \
    outputs/builds/drees-plumbing-inc/index.html
# Expect: 0 (fabricated-claim regression check from issue #10)
```

If either grep returns non-zero, the prompt drift is the bug --
fix it before pushing. The placeholder architecture (PR #6) and
the Why-Choose-Us fabrication guard (PR #13) are the load-bearing
discipline; regressions there are the highest-priority defects.

### 2c. Local review before PR

Before opening or updating a PR, the builder runs the mechanical
local review bundle:

```bash
bash scripts/local_pr_review.sh
```

v1 checks: worktree-clean, `git diff --check`, plan-doc-presence
(at least one `plans/PR-*.md` touched in the diff). The fuller
ATLAS bundle (pre-push audit wrapper + plan/code consistency
audit) is deferred -- see `plans/PR-Adopt-Atlas-Workflow.md`.

### 2d. Tests

LBSB has no formal test suite today. The verification commands in
each PR's plan doc replace the unit-test row: each PR names the
specific build + grep + visual-spot-check sequence that proves
the change works.

If a `tests/` directory is added in a future slice (e.g. unit
tests for `select_theme` / `select_palette` / `select_hero_shape`
in `build.py`), this section grows to match ATLAS's 3d.

---

## 3. Reviewer expectations (today: GitHub Copilot bot)

Copilot reviews PRs automatically within ~1-2 minutes of `gh pr
create` per the memory at
`~/.claude/projects/.../memory/feedback_pr_review_workflow.md`.
Builder addresses Copilot comments in fix-up commits on the same
branch -- never force-push.

When the LBSB reviewer-session pattern lands (deferred), this
section grows to mirror ATLAS section 2 (BLOCKER / MAJOR / NIT /
LGTM verdict shape + independent verification template).

---

## 4. Within-session agent routing

**Reasoning stays in main; retrieval goes to a subagent.
Synthesis stays with whoever has to act on the answer (almost
always main).** Ported verbatim from ATLAS AGENTS.md section 5
because the principle is repo-agnostic.

### 4a. The decision

Two questions before opening a file or kicking off a search:

1. *Will I edit this file in-session?* -> Main, direct `Read`
   (need exact line numbers).
2. *Does this need judgment* (quality, design trade-off,
   root-cause)? -> Main only.

If neither, route by shape:

| Shape | Where | Why |
|---|---|---|
| Read-only, >400 lines, no edits planned | `Explore` subagent | Pure retrieval; summary lands in main context, raw file does not |
| Reading 3+ files just to orient | `Explore` subagent | Width without depth -- the subagent's strength |
| "Find every caller of X" / "where is Y defined" | `grep`/`find` via Bash | Regex match, no LLM needed |
| Scaffold multi-file boilerplate (tests, configs, fixtures) | `general-purpose` subagent | Write-capable, separate context window |
| Architectural decision / debugging / refactor plan | Main only | Needs holistic judgment |
| Code review verdict | Main only | Verdict requires judgment, not a summary |

The boundary that matters most: **judgment vs lookup.**

### 4b. Routing anti-patterns

- **Asking a subagent for a judgment call** ("is this design
  right?"). The subagent doesn't have full session context and
  the answer is just deferred judgment the main session has to
  redo.
- **Sequencing N orthogonal `Explore` calls** instead of firing
  them in parallel.
- **Using `Explore` on a <400-line file you're about to edit
  anyway.** Just `Read` it directly.
- **Letting a subagent compose the final user-facing answer.**
  Synthesis is a main-session job.

---

## 5. Anti-patterns

Things that should **never** appear in a PR:

- **Drive-by formatting changes** unrelated to the slice.
  Format-only diffs ship as their own slice.
- **Plan doc that arrives in a follow-up commit.** Plan and
  implementation ship together.
- **"While I was here..." cleanups** that aren't in the plan.
  Add a Deferred item and move on.
- **Bypassing CI / hooks with `--no-verify`** unless the user
  explicitly authorizes.
- **Force-pushing** to a PR branch. Always fix-up commit, even
  for typo fixes. The user has a global guardrail against
  force-push.
- **Fabricating prospect facts.** The defining LBSB sin. Any
  generated content (headline, subhead, benefit card, form
  trust line, badge, hero copy) must trace back to either a
  verified `prospect.*` field, a verified `prospect.service_promises`
  entry, or the safe-generic positioning category in 07. If you
  can't name the gating field, the content is a fabrication
  bug -- fix the prompt, don't ship the build.
- **Skipping the build verification in 2b** on PRs that touch
  the prompt or generation pipeline.
- **Marketing tone in PR body / commit message.** Audit-log
  calibrated, not "Done." or "Shipped." or "Verified end-to-end."
  Name the exact commands run; let the reader judge.

---

## 6. References

- `plans/` -- per-slice plan docs (one per PR).
- `scripts/local_pr_review.sh` -- mechanical pre-push bundle.
- `CLAUDE.md` -- project-level Claude Code guidance.
- `references/06-build-prompt.md` -- the from-scratch HTML
  generation prompt.
- `references/07-industry-defaults.md` -- trade defaults
  knowledge base (the fabrication guard's data source).
- `references/09-themes.md` -- theme catalog with per-theme
  typography + hero-shape coupling.
- `~/.claude/projects/.../memory/feedback_atlas_pr_ruleset.md` --
  the persistent memory entry that captures this contract for
  cross-session continuity.
- `canfieldjuan/ATLAS/AGENTS.md` -- the canonical workflow doc
  this is ported from. Consult it for anything this file doesn't
  cover (reviewer-session bootstrap, package-specific guardrails,
  multi-agent extensions).
