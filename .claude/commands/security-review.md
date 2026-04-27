---
description: Run a security review of recent code changes (injection, path traversal, secret exposure, shell safety)
---

# Security Review

Perform a comprehensive security audit of recent code changes in this project.

## Steps

1. **Identify changed files**: Run `git diff --name-only` to find modified files
   (both staged and unstaged). If no uncommitted changes exist, compare the
   current branch against its base branch using `git diff --name-only main...HEAD`.

2. **Filter to relevant files**: Focus on `.py`, `.js`, `.sh`, and `.html` files. Skip
   documentation and static assets unless they contain security-relevant code.

3. **Launch the security-reviewer agent** via the Agent tool with
   `subagent_type: "security-reviewer"`. Provide it with:
   - The list of changed files
   - The full diff (`git diff` output or `git diff main...HEAD`)
   - Instructions to read and review each changed file completely
   - Project context: Python pipeline scripts that call external APIs (CellarTracker,
     Google Calendar), shell scripts that invoke `op`, `curl`, `ssh`, and `claude`;
     JS frontend that renders JSON data from generated files

4. **Report results**: Present the security-reviewer agent's findings to the
   user. If critical or high severity issues are found, recommend fixing them
   before proceeding.

## When to Use

- Before creating a commit or pull request
- After implementing features that handle credentials, shell commands, external
  API calls, or user-visible output
- As a final check before release
