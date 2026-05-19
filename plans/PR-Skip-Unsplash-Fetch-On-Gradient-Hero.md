# PR-Skip-Unsplash-Fetch-On-Gradient-Hero

## Why this slice exists

Closes issue #16. Observed during PR #15 testing on Olney Heating &
Air Conditioning (theme `minimal` -> hero shape `gradient`): the
build fetched and saved a hero image
(`outputs/builds/olney-heating-air-conditioning/images/hero.jpg`,
credited to Iain Feeney), then rendered a `hero-gradient` section
that doesn't reference the image. The photo sits unused.

Cost is small but real for every gradient build:

- ~3 sec of Unsplash request + download latency.
- A few hundred KB of disk space in `outputs/<slug>/images/`.
- ~1 Unsplash API call against the free-tier rate limit (50/hr).
- The unused photo gets deployed inside the Vercel bundle.

If Unsplash is unavailable and the build falls through to Flux,
gradient builds pay ~$0.05 in OpenRouter token cost for an image
the harness already decided to throw away.

Root cause: `build.py:main()` runs hero acquisition unconditionally
when `--skip-image-gen` isn't passed. It doesn't consult
`_computed_hero_shape` (which the harness sets two steps earlier).

## Scope (this PR)

1. Add a short-circuit branch in `build.py:main()`'s hero
   acquisition block: when `prospect.get("_computed_hero_shape") ==
   "gradient"`, log the skip reason and bypass both Unsplash and
   Flux. The branch sits between the existing `--skip-image-gen`
   check and the existing Unsplash-first / Flux-fallback ladder.

### Files touched

- `build.py` (~7 LOC: one branch + log line)
- `plans/PR-Skip-Unsplash-Fetch-On-Gradient-Hero.md` (new, ~75 LOC, this file)

## Mechanism

Three-way branch on the hero acquisition path:

```python
if "--skip-image-gen" in sys.argv:
    # Existing path: operator-forced skip.
    print("[*] Skipping hero image generation due to --skip-image-gen flag.")
elif prospect.get("_computed_hero_shape") == "gradient":
    # New: harness selected a hero shape that renders no photo.
    # Skip the fetch to save a network round-trip + disk space.
    print("[*] Skipping hero image generation: _computed_hero_shape='gradient' renders no photo.")
else:
    # Existing Unsplash -> Flux acquisition block, unchanged.
    ...
```

The new branch reads the harness's `_computed_hero_shape` value
that was set earlier in `main()` (after `select_theme` and
`select_palette`). This is data-driven; the LLM is not involved
in the decision.

## Intentional

- This does not change `select_hero_shape()` behavior or the
  theme -> hero coupling table. Shape selection remains deterministic
  and theme-driven; the optimization only suppresses a wasted
  side-effect.
- This does not introduce a code path that picks `gradient` based
  on image-availability (e.g. "fall back to gradient when
  Unsplash fails"). That would re-introduce non-determinism in
  the layout decision, which PR #15's hero coupling explicitly
  guards against. Slice 3a's design treats hero shape as a pure
  function of theme; this PR preserves that.
- This does not unset or clean up the unused
  `outputs/<slug>/images/hero.jpg` from a prior non-gradient
  build of the same prospect. The unused photo from a previous
  run is a one-time disk artifact; rerunning a gradient build now
  simply doesn't add a new one. Cleanup tooling for stale build
  artifacts is a separate concern.

## Deferred

- Same optimization for other future "no photo" hero shapes if
  they get added in slice 3b or later. The branch logic is
  trivially extensible to a set membership check
  (`"_computed_hero_shape" in NO_PHOTO_SHAPES`), but with only one
  no-photo shape today the membership-check form is over-engineered.
- A `--force-image-gen` flag to override the new skip and fetch
  a photo for gradient prospects anyway (e.g. for designers who
  want the photo for use elsewhere on the page). Not a real
  demand signal today; can be added later if the use case
  surfaces.

## Verification

- `bash scripts/local_pr_review.sh` -> passed (worktree-clean,
  `git diff --check` on the proposed range, plan-doc presence).
- Olney Heating build with image gen enabled previously logged:
  ```
  [*] Searching Unsplash for hero: query='hvac technician'
  [+] Saved Unsplash hero to: outputs/builds/olney-heating-air-conditioning/images/hero.jpg
  [*] Unsplash credit: Iain Feeney (https://unsplash.com/@lockefeener)
  ```
  Post-fix the same invocation logs the new skip reason and
  emits no Unsplash search / credit lines. The rendered HTML
  remains a gradient hero with no `background-image` on the
  section (visually unchanged from the PR #15 baseline).
- Plumber and electrician builds (non-gradient hero shapes)
  still fetch heroes via the existing Unsplash path -- spot-check
  Drees Plumbing's stdout for the unchanged Unsplash credit line
  and `images/hero.jpg` presence.

## Estimated diff size

| Area | Estimated LOC |
|---|---:|
| `build.py` (one branch + log) | ~7 |
| `plans/PR-Skip-Unsplash-Fetch-On-Gradient-Hero.md` (this file) | ~75 |
| **Total** | **~82** |

Well under the 400 LOC soft budget.
