# Start Issue

Begin work on a GitHub issue by creating an issue branch off the current milestone branch.

## Arguments

- `$ARGUMENTS` — the GitHub issue number (e.g., `16`)

## Workflow

1. **Verify we're on a milestone branch**:

   ```bash
   git branch --show-current
   ```

   The current branch must match `milestone/*`. If not, check if there is exactly one local `milestone/*` branch and switch to it. If there are zero or multiple, stop and ask the user to run `/start-milestone` first or specify which milestone branch to use.

2. **Ensure clean working tree**:

   ```bash
   git status --porcelain
   ```

   If there are uncommitted changes, stop and ask the user to commit or stash first.

3. **Fetch the issue details** from GitHub:

   ```bash
   gh issue view $ARGUMENTS --json number,title,body,milestone,labels
   ```

   If the issue doesn't exist, stop and report the error.

4. **Derive a short slug** from the issue title:
   - Lowercase the title
   - Take the first 4-5 meaningful words
   - Replace spaces and special characters with hyphens
   - Example: `Add varietal-aware pairing for sparkling wines` → `varietal-pairing-sparkling`

5. **Create the issue branch** from the current milestone branch:

   ```bash
   git checkout -b issue/$ARGUMENTS-<slug>
   git push -u origin issue/$ARGUMENTS-<slug>
   ```

6. **Update the GitHub issue**:

   ```bash
   gh issue edit $ARGUMENTS --add-label "in progress" --add-assignee @me
   ```

   Create the "in progress" label first if it doesn't exist (use `#0075CA` blue).

7. **In parallel**, do both of the following:

   **a) Develop an implementation plan** by launching the following agents in parallel to collaborate as a team:

   - **senior-architect** — Analyze the issue and identify which files need to change, architectural concerns, potential side effects, and the safest approach. Consider the pipeline flow (fetch → generate → notes → compare → publish) and the data/presentation/style separation.
   - **pipeline-reviewer** (subagent, `.claude/agents/pipeline-reviewer.md`) — **If the issue touches any file in `scripts/`, `pipeline.sh`, `fetch.sh`, `fetch_docker.sh`, or `entrypoint.sh`**: review the proposed changes against the pipeline contract (JSON schemas, execution order, error handling, shared utilities). Skip this agent if the issue only touches `site/` or `docs/`.
   - **senior-test-engineer** — Determine what tests are needed and manual verification steps. Identify edge cases specific to this issue. Include `/pipeline-test` as a verification step in the testing strategy. **If the issue touches `scripts/pairing.py` or `scripts/wine_keywords.py`**, include `/pairing-audit` as a pre- and post-implementation check. **If the issue has a bug label**, also perform a bug escape analysis: Why wasn't this bug caught? What test coverage gap allowed it? Are there similar untested code paths?
   - **technical-documentation-writer** — Identify what documentation needs updating using this requirements matrix:

     | Change Type | Documentation to Update |
     | --- | --- |
     | Pipeline flow changes | CLAUDE.md pipeline section |
     | New scripts or files | CLAUDE.md directory structure |
     | New environment variables | CLAUDE.md, .env.sample |
     | Plan generation rule changes | CLAUDE.md plan rules section |
     | Pairing engine changes | CLAUDE.md pairing engine section |
     | Docker/deployment changes | CLAUDE.md deployment section |
     | Menu parsing changes | docs/menu-guide.md |

   - **senior-product-manager** — Review the issue's acceptance criteria. Flag any ambiguity in the requirements and suggest clarifying questions if needed.
   - **software-developer** — Scout the specific code locations that need changes. Identify the exact functions, files, and line numbers to modify.

   Synthesize all agent outputs into a single **Implementation Plan** with these sections:
   - **Files to modify** — list of files with what changes are needed in each
   - **Implementation steps** — ordered list of code changes to make
   - **Testing strategy** — what to test and how. Always include `/pipeline-test` for end-to-end validation. If the issue touches pairing logic, include `/pairing-audit` before and after. If the issue touches `site/`, include Playwright visual verification (navigate to `site/index.html`, check rendering, verify tabs work, check console for JS errors).
   - **Documentation updates** — what docs need changing (use the documentation requirements matrix above)
   - **Risks & open questions** — anything that needs user input before proceeding
   - **Pipeline review** (if pipeline-reviewer was launched) — summary of contract compliance findings
   - **Escape Analysis** (bug-labeled issues only) — include three subsections:
     - *Root Cause*: What caused the bug and why it wasn't caught
     - *Testing Gap*: What tests were missing or insufficient
     - *Preventive Measures*: What will prevent recurrence

8. **Output the plan and summary** showing:
   - The issue branch name
   - The issue title and body (for context while working)
   - The full implementation plan from step 7
   - If the issue has a bug label, include the Escape Analysis section and remind the user to include it in the PR description
   - The milestone branch it will merge back into
   - Instructions: "Review the plan above, then say 'go' to begin implementation or ask questions to refine the plan."

9. **Implement the plan** (after user says 'go'):

   Launch agents in parallel to implement the approved plan:

   - **software-developer** agents — Launch one or more instances in parallel to implement code changes. Partition work by file or subsystem to avoid conflicts. Provide each agent with the relevant subset of the implementation plan.
   - **senior-test-engineer** — Write tests based on the testing strategy if applicable. Launch separate instances for different test scopes if the scope warrants it.
   - **technical-documentation-writer** — Update any documentation identified in the plan (CLAUDE.md, docs/menu-guide.md, .env.sample). Only launch if documentation updates were identified.

   After all implementation agents complete:

   - Run quality checks (ruff format/lint, pyright type checking, shellcheck, etc.):

     ```bash
     pre-commit run --all-files
     ```

     If pyright reports type errors, fix them before proceeding — especially in scoring functions that pass floats and dicts.

   - Launch **pipeline-reviewer** subagent (`.claude/agents/pipeline-reviewer.md`) for final review if any pipeline scripts were changed. Address any issues raised.
   - Launch **senior-architect** agent for final code review of all changed files. Address any issues raised.
   - If the issue touched pairing logic, run `/pairing-audit` to verify no coverage regressions.

10. **Hand off to the user**:

    Output a summary of what was implemented, then provide next steps:

    ```text
    Implementation complete for issue #$ARGUMENTS. Next steps:
    1. Review the changes: `git diff`
    2. `/pipeline-test`   — Run full pipeline and validate outputs
    3. `/simplify`        — Clean up the code (optional)
    4. `/commit`          — Commit your changes
    5. `/commit-push-pr`  — Push and create a PR targeting `milestone/<version>`
    6. `/finish-issue`    — Squash-merge and close the issue
    ```

## Important

- The PR created by `/commit-push-pr` must target the **milestone branch**, not `main`. Remind the user of this when outputting the summary.
- Launch all five agents in parallel for speed — they are analyzing the same issue independently.
- The plan is a proposal — wait for user approval before writing any code.
- For bug-labeled issues, the escape analysis should inform the testing strategy — ensure the preventive measures are implemented as part of the test plan.
