# Start Milestone

Begin work on a milestone by creating a milestone branch from main.

## Arguments

- `$ARGUMENTS` — the milestone version number (e.g., `v1.2.0`)

## Workflow

1. **Validate the milestone exists** on GitHub:

   ```bash
   gh api repos/:owner/:repo/milestones --jq '.[] | select(.title | startswith("'"$ARGUMENTS"'"))'
   ```

   If not found, stop and report the error.

2. **Ensure clean working tree**:

   ```bash
   git status --porcelain
   ```

   If there are uncommitted changes, stop and ask the user to commit or stash first.

3. **Create the milestone branch from main**:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b milestone/$ARGUMENTS
   git push -u origin milestone/$ARGUMENTS
   ```

4. **List the milestone's open issues** for context:

   ```bash
   gh issue list --milestone "<full milestone title>" --state open --json number,title,labels,body
   ```

5. **Recommend an issue order** by analyzing all the issues and determining the best sequence to address them. Consider:
   - **Dependencies** — issues that other issues depend on should come first (e.g., a data model change before a feature that uses it)
   - **Severity** — CRITICAL before HIGH before MEDIUM before LOW
   - **Shared code paths** — group issues that touch the same files to minimize merge conflicts
   - **Foundation first** — pipeline/utility changes before site/presentation changes

   Present the recommended order as a numbered list with a brief rationale for each position.

   Additionally, flag issues that warrant special tools:
   - Issues touching `CLAUDE.md` scope: new scripts, pipeline flow, env vars, deployment, plan rules, pairing engine
   - Issues touching `scripts/pairing.py` or `scripts/wine_keywords.py`: recommend running `/pairing-audit` before and after implementation
   - Issues touching any `scripts/*.py` or pipeline shell scripts: the `pipeline-reviewer` subagent will be launched automatically during `/start-issue`

6. **Output a summary** showing:
   - The milestone branch name
   - The recommended issue order (from step 5)
   - Any special tool recommendations per issue (from flagging above)
   - Instructions: "Use `/start-issue <number>` to begin work on the first issue"
