# Release Milestone

Squash merge a milestone PR into main, tag the release, deploy to docker02, and publish a GitHub release.

This command picks up where `/finish-milestone` left off — after the milestone PR has been created and reviewed.

## Arguments

- `$ARGUMENTS` — (optional) the milestone version number (e.g., `v1.2.0`). If omitted, auto-detect from the open `milestone/*` → `main` PR.

## Workflow

1. **Find the milestone PR**:
   ```bash
   gh pr list --base main --state open --json number,title,headRefName,url
   ```
   - Filter for PRs where `headRefName` starts with `milestone/`
   - If `$ARGUMENTS` is provided, match against `milestone/$ARGUMENTS`
   - If exactly one match, use it. If zero or multiple, stop and ask the user to specify.
   - Extract the version from the branch name (e.g., `milestone/v1.2.0` → `v1.2.0`)

2. **Verify preconditions**:
   - The PR must be in a mergeable state (no conflicts)
   - The working tree must be clean (`git status --porcelain`)
   - Must be on `main` or the milestone branch
   ```bash
   gh pr view <number> --json mergeable,mergeStateStatus
   ```

3. **Pre-release validation**:

   a. If Playwright MCP is available, verify the site renders correctly from the milestone branch:
   - Navigate to `file:///path/to/site/index.html`
   - Take a screenshot and verify plan table, tabs, pairing badges all render
   - Report any JS console errors

   b. Verify pipeline output is current:
   ```bash
   python3 -c "
   import json, os, time
   plan = 'site/plan.json'
   if os.path.exists(plan):
       age_hours = (time.time() - os.path.getmtime(plan)) / 3600
       print(f'site/plan.json last modified {age_hours:.1f} hours ago')
       if age_hours > 24:
           print('WARNING: plan.json is stale — consider running /pipeline-test before release')
   "
   ```

4. **Show summary and ask for confirmation**:
   Display:
   - PR number, title, and URL
   - Number of commits that will be squash-merged
   - Version that will be tagged
   - Pre-release validation results (Playwright + staleness check)
   - Remind: "This will squash merge, tag, push, and deploy to docker02 on next `down/up` or scheduled run."

   **Ask the user to confirm before proceeding.** This is the point of no return.

5. **Switch to main and pull latest**:
   ```bash
   git checkout main
   git pull origin main
   ```

6. **Squash merge the PR**:
   ```bash
   gh pr merge <number> --squash --delete-branch
   ```
   This deletes the remote milestone branch. The `--squash` flag creates a single commit on main.

7. **Pull the merge commit**:
   ```bash
   git pull origin main
   ```

8. **Create and push a git tag**:
   ```bash
   git tag -a <version> -m "<version> — <milestone title>"
   git push origin main --tags
   ```

9. **Delete the local milestone branch** (if it still exists):
   ```bash
   git branch -d milestone/<version>
   ```

10. **Create a GitHub release**:
   - Gather closed issues from the milestone for release notes
   ```bash
   gh issue list --milestone "<full milestone title>" --state closed --json number,title
   ```
   - Create the release:
   ```bash
   gh release create <version> --title "<version> — <milestone title>" --generate-notes
   ```

11. **Close the GitHub milestone**:
    ```bash
    gh api repos/{owner}/{repo}/milestones/<milestone_number> -X PATCH -f state=closed
    ```
    Find the milestone number from the PR's milestone field or by listing milestones.

12. **Output summary**:
    - Confirm the release was published with link
    - Note that the milestone has been closed
    - Deployment reminder:
      ```text
      To deploy to production:
        ssh docker02
        cd <project-dir>
        docker compose down && docker compose up -d

      Or wait for the next scheduled run — the container will git pull
      and pick up the changes automatically.
      ```

## Important

- **Confirmation is required** before the squash merge (step 3). Do not proceed without explicit user approval.
- The version is derived from the milestone branch name, not passed as a bump level. If there's ambiguity, ask.
- If any step fails, stop immediately and report the error. Do not continue with partial state.
- This command assumes `/finish-milestone` has already been run (PR exists, CLAUDE.md updated, issues closed).
- The `--delete-branch` flag on `gh pr merge` handles remote branch cleanup. Step 8 handles local cleanup.
- This project has no CI/CD — deployment is manual via SSH to docker02 or automatic on next scheduled container run.
