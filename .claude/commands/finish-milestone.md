# Finish Milestone

Create a PR to merge a completed milestone branch into main.

## Arguments

- `$ARGUMENTS` — the milestone version number (e.g., `v1.2.0`)

## Workflow

1. **Verify the milestone branch exists**:

   ```bash
   git branch -a | grep "milestone/$ARGUMENTS"
   ```

   If not found, stop and report the error.

2. **Check for open issues** still in the milestone:

   ```bash
   gh issue list --milestone "<full milestone title>" --state open --json number,title
   ```

   If there are open issues, warn the user and list them. Ask if they want to proceed anyway or finish the remaining issues first.

3. **Switch to the milestone branch and ensure it's up to date**:

   ```bash
   git checkout milestone/$ARGUMENTS
   git pull origin milestone/$ARGUMENTS
   ```

4. **Gather all merged PRs** that targeted the milestone branch for the PR body:

   ```bash
   gh pr list --base milestone/$ARGUMENTS --state merged --json number,title,url
   ```

5. **Get the full diff** against main:

   ```bash
   git log main..milestone/$ARGUMENTS --oneline
   ```

6. **Run final validation on the milestone branch**:

   a. Run pre-commit checks (ruff format/lint, pyright type checking, shellcheck, etc.):

   ```bash
   pre-commit run --all-files
   ```

   b. Determine what files changed in this milestone:

   ```bash
   git diff --name-only main...milestone/$ARGUMENTS
   ```

   c. If any pipeline scripts changed, launch the **pipeline-reviewer** subagent (`.claude/agents/pipeline-reviewer.md`) for a final contract compliance review.

   d. If pairing engine files changed (`scripts/pairing.py` or `scripts/wine_keywords.py`), note in the PR body that `/pairing-audit` should be run after merge.

   e. If site files changed, use **Playwright** (if available) to verify the site renders correctly:
   - Navigate to `file:///path/to/site/index.html`
   - Verify plan table renders, tabs work, pairing badges display, no JS console errors

7. **Update CLAUDE.md** if needed:

   Review `CLAUDE.md` against the milestone's changes. Check whether any updates are needed for:
   - New scripts or files added to the directory structure
   - Changes to pipeline flow
   - New environment variables
   - Changed plan generation rules or pairing engine logic
   - New deployment steps or Docker changes
   - New conventions or important patterns

   If updates are needed, make targeted edits and commit:

   ```bash
   git add CLAUDE.md
   git commit -m "docs: update CLAUDE.md for $ARGUMENTS milestone changes"
   ```

8. **Create the PR** targeting `main`:

   ```bash
   gh pr create \
     --base main \
     --head milestone/$ARGUMENTS \
     --title "$ARGUMENTS — <milestone name>" \
     --body "$(cat <<'EOF'
   ## Summary

   <1-2 sentence description of the milestone's purpose>

   ## Issues Resolved

   <List each merged PR with its issue number, title, and link>

   <!-- Fill from step 4 data: one line per merged PR -->
   - #<number> — <title> (PR #<pr_number>)

   ## Test Plan

   - [ ] All issue PRs were reviewed and merged
   - [ ] `/pipeline-test` passes (full pipeline + JSON validation)
   - [ ] Site renders properly (`/pipeline-test` includes Playwright check if available)
   - [ ] `/pairing-audit` shows no coverage regressions (if pairing engine changed)
   - [ ] Docker build succeeds: `docker compose build`

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

   Fill in the actual issue list and PR numbers from the data gathered in step 4.

9. **Suggest next steps**:
   - "Use `/review-pr` to review the milestone PR before merging"
   - "After merging, run `/release-milestone $ARGUMENTS` to tag, deploy, and clean up"
