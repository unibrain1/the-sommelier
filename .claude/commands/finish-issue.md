# Finish Issue

Squash-merge a PR, close the issue, delete the branch, and return to the milestone branch.

## Arguments

- `$ARGUMENTS` — the GitHub issue number (e.g., `16`). If omitted, infer from the current branch name (e.g., `issue/16-varietal-pairing` → `16`).

## Workflow

1. **Determine the issue number and PR**:

   If no argument is provided, extract the issue number from the current branch name:

   ```bash
   git branch --show-current
   ```

   The branch must match `issue/<number>-*`. If it doesn't, stop and ask the user for the issue number.

   Find the open PR for this issue branch:

   ```bash
   gh pr list --head "$(git branch --show-current)" --state open --json number,title,url,baseRefName
   ```

   If no PR exists, stop and tell the user to run `/commit-push-pr` first.

2. **Identify the target (base) branch**:

   The PR's `baseRefName` should be a `milestone/*` branch. Record it — this is where we'll return after merging.

3. **Run pre-merge validation**:

   a. Run pre-commit checks (ruff format/lint, pyright type checking, shellcheck, etc.):

   ```bash
   pre-commit run --all-files
   ```

   If any checks fail (including pyright type errors), report which ones and stop. Tell the user to fix the issues before merging.

   b. Determine what files changed in this branch:

   ```bash
   git diff --name-only <milestone-branch>...HEAD
   ```

   c. If any `scripts/*.py`, `pipeline.sh`, `fetch.sh`, `fetch_docker.sh`, or `entrypoint.sh` were changed, launch the **pipeline-reviewer** subagent (`.claude/agents/pipeline-reviewer.md`) to verify pipeline contract compliance. If it finds CRITICAL issues, stop and report them.

   d. If `site/index.html` or `site/style.css` were changed, use **Playwright** (if available) to verify the site renders correctly:
   - Navigate to `file:///path/to/site/index.html`
   - Take a snapshot and check that the plan table renders, tabs work, and no JS errors appear in the console

4. **Squash-merge the PR**:

   ```bash
   gh pr merge <pr-number> --squash --delete-branch
   ```

   This squash-merges into the milestone branch and deletes the issue branch (both local and remote).

5. **Close the GitHub issue**:

   ```bash
   gh issue close $ARGUMENTS --comment "Resolved via PR #<pr-number>."
   ```

6. **Return to the milestone branch**:

   ```bash
   git checkout <milestone-branch>
   git pull origin <milestone-branch>
   ```

   Clean up the local issue branch if it still exists:

   ```bash
   git branch -d issue/$ARGUMENTS-* 2>/dev/null
   ```

7. **List remaining milestone issues**:

   ```bash
   gh issue list --milestone "<milestone title>" --state open --json number,title
   ```

8. **Report results**:

   Output a summary:
   - Issue #`<number>` — closed
   - PR #`<pr-number>` — squash-merged into `<milestone-branch>`
   - Branch `issue/<number>-<slug>` — deleted
   - Now on `<milestone-branch>`
   - Remaining open issues in the milestone (from step 7)

   Suggest next steps based on remaining issues:
   - **If open issues remain**: "Run `/start-issue <next-issue-number>` to begin the next issue"
   - **If no open issues remain**: "All issues complete. Run `/finish-milestone <version>` to create the milestone PR"

## Important

- Never force-merge if pre-commit checks are failing. Always investigate and report first.
- The squash merge keeps the milestone branch history clean with one commit per issue.
- If the PR targets `main` instead of a milestone branch, warn the user — issue PRs should always target the milestone branch per the git workflow.
- If the local branch can't be deleted (e.g., you're still on it), switch to the milestone branch first.
