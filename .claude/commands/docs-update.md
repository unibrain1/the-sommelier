# /docs-update

Update project documentation by auditing CLAUDE.md and docs/ against the current codebase.
Makes all changes on a branch. Does not merge or push.

---

## Steps

### 0. Set up a working branch

- Confirm you are starting from the main branch. If not, switch to main first.
- Pull the latest changes from origin/main
- Create a new branch called `docs/docs-update`
- All changes should be made on this branch

### 1. Audit CLAUDE.md against the codebase

Read `CLAUDE.md` in full and compare it against the current codebase. Check whether any sections are outdated, incomplete, or missing:

**Directory Structure**

- Walk the project root and compare against the documented directory structure
- Check for new files, renamed files, removed files, or new directories
- Verify descriptions of each file/directory are accurate

**Pipeline Flow**

- Read `pipeline.sh`, `fetch.sh`, `fetch_docker.sh`, and `entrypoint.sh`
- Verify the documented pipeline flow matches the actual implementation
- Check for new steps, changed order, or removed steps

**Scripts**

- List all files in `scripts/` and verify each is documented
- For each script, check that its described purpose matches its actual implementation
- Verify shared utilities in `wine_utils.py` are accurately documented

**Plan Generation Rules**

- Read `scripts/generate_plan.py` and compare against documented rules
- Check for new rules, changed thresholds, or removed logic

**Pairing Engine**

- Read `scripts/wine_keywords.py` and `scripts/pairing.py`
- Verify documented pairing logic matches implementation
- Check for new keywords, scoring changes, or new pairing outcomes

**Docker & Deployment**

- Read `Dockerfile`, `docker-compose.yml`, `entrypoint.sh`, `nginx.conf`
- Verify deployment documentation is accurate
- Check for new environment variables, changed ports, or new services

**Site/Frontend**

- Read `site/index.html` and `site/style.css`
- Verify the data/presentation/style architecture description is accurate
- Check for new JSON data files or changed rendering logic

### 2. Update CLAUDE.md

For each section that is outdated, incomplete, or missing:

- If a section already exists and is accurate, preserve it as-is
- If a section exists but is outdated or incomplete, update it
- If a section is missing entirely, add it
- Do not change the voice, formatting style, or structure unless something is clearly broken
- Make targeted, minimal edits — do not rewrite unchanged sections

### 3. Audit docs/menu-guide.md

- Read `docs/menu-guide.md` and compare against `scripts/wine_keywords.py` and `scripts/pairing.py`
- Verify that documented keywords, formatting rules, and examples match the current implementation
- Update any outdated sections

### 4. Check for undocumented configuration

- Read `.env.sample` and verify all environment variables are documented in CLAUDE.md
- Read `scripts/plan_config.py.sample` and verify it's referenced accurately
- Check `docker-compose.yml` for any undocumented configuration

### 5. Run quality checks

```bash
pre-commit run --all-files
```

This runs ruff format/lint, pyright type checking, shellcheck, and other checks. Fix any issues before proceeding.

### 6. Commit the changes

- Stage all modified files
- Write a commit message: `docs: update project documentation [date]`
- Commit to the `docs/docs-update` branch
- Do not push — leave that for manual review

### 7. Report what was done

- List every file modified
- For each file: summarize what changed and why
- Note the branch name and commit hash
- Remind the user to review and merge when ready
