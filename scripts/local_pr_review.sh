#!/usr/bin/env bash
# Run the local mechanical review bundle before opening or updating a PR
# in canfieldjuan/Local-Business-Site-Builder.
#
# Ported (simplified) from canfieldjuan/ATLAS/scripts/local_pr_review.sh.
# See AGENTS.md section 2c for the full builder workflow this is part of,
# and plans/PR-Adopt-Atlas-Workflow.md for what's deferred from the ATLAS
# version (pre-push audit wrapper, plan/code consistency Python audit).
#
# Checks (v1, in order):
#   1. Worktree clean        -- so committed-diff checks cannot silently
#                               ignore uncommitted edits. Skip with
#                               --allow-dirty for an advisory partial run.
#   2. git diff --check      -- whitespace / merge-marker damage.
#   3. Plan-doc presence     -- at least one plans/PR-*.md must be
#                               added-or-modified in the diff vs base.
#                               The plan-doc contract is the load-bearing
#                               part of the ATLAS workflow; a PR with no
#                               plan doc skips review by design and is
#                               always wrong unless explicitly exempted.

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

base_ref="origin/main"
base_ref_set=0
allow_dirty=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --allow-dirty)
            allow_dirty=1
            shift
            ;;
        --help|-h)
            cat <<'EOF'
Usage: bash scripts/local_pr_review.sh [--allow-dirty] [base-ref]

Run the local mechanical review bundle before opening or updating a PR.
By default, the worktree must be clean so committed-diff checks cannot
silently ignore uncommitted edits.

  base-ref         Defaults to origin/main. Pass an explicit ref to
                   compare against a different base (e.g. for a stacked PR).
  --allow-dirty    Skip the worktree-clean guard. The diff checks still
                   run, but they only see committed changes. Use only for
                   advisory partial runs while drafting a slice.
EOF
            exit 0
            ;;
        --*)
            echo "local_pr_review.sh: unknown option: $1" >&2
            exit 2
            ;;
        *)
            if [ "$base_ref_set" -eq 1 ]; then
                echo "local_pr_review.sh: multiple base refs supplied" >&2
                exit 2
            fi
            base_ref="$1"
            base_ref_set=1
            shift
            ;;
    esac
done

failures=0

run_check() {
    local label="$1"
    shift
    echo
    echo "==> $label"
    if "$@"; then
        echo "    PASS"
    else
        echo "    FAIL"
        failures=$((failures + 1))
    fi
}

if ! git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
    echo "local_pr_review.sh: base ref not found: $base_ref" >&2
    echo "fetch trunk first, or pass an explicit base ref" >&2
    exit 2
fi

if [ "$allow_dirty" -ne 1 ] && [ -n "$(git status --porcelain)" ]; then
    echo "local_pr_review.sh: worktree has uncommitted changes." >&2
    echo "Commit or stash them before running local review, or pass --allow-dirty for a partial/advisory run." >&2
    echo >&2
    git status --short >&2
    exit 1
fi

base="$(git merge-base HEAD "$base_ref")"

echo "local PR review"
echo "base ref: $base_ref"
echo "merge base: $base"
echo
echo "changed files:"
git diff --name-status "$base"...HEAD || true

run_check "git diff --check" git diff --check

plan_doc_count=$(
    git diff --name-only --diff-filter=AM "$base"...HEAD -- 'plans/PR-*.md' 2>/dev/null |
        grep -c . || true
)

echo
echo "==> Plan-doc presence ($plan_doc_count plan(s) touched)"
if [ "$plan_doc_count" -ge 1 ]; then
    echo "    PASS"
else
    echo "    FAIL -- no plans/PR-*.md added or modified vs $base_ref."
    echo "             Every PR ships its plan doc. See AGENTS.md section 1a."
    failures=$((failures + 1))
fi

echo
if [ "$failures" -eq 0 ]; then
    echo "local PR review passed"
    echo
    echo "Next: open the PR. Title format: 'Plan: PR-<Slice-Name>'."
    echo "      Body mirrors the plan doc -- see AGENTS.md section 1b."
    exit 0
fi

echo "$failures local review check(s) failed"
exit 1
