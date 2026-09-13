#!/usr/bin/env bash

set -euo pipefail

# Always run from the repository root, regardless of where this script
# was invoked from.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "Physicist Spotlight Research Workflow"
echo "====================================="
echo

# Basic sanity checks.
if ! command -v codex >/dev/null 2>&1; then
    echo "Error: Codex CLI is not installed or is not available on PATH."
    echo
    echo "Install it with:"
    echo "  npm install --global @openai/codex"
    exit 1
fi

if [ ! -f "AGENTS.md" ]; then
    echo "Error: AGENTS.md was not found in the repository root."
    exit 1
fi

if [ ! -d "data" ]; then
    echo "Error: data/ directory was not found."
    exit 1
fi

# Protect against accidentally starting an autonomous run on top of
# uncommitted work.
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Error: The Git working tree contains modified tracked files."
    echo
    echo "Commit or stash your changes before running the spotlight workflow."
    echo
    git status --short
    exit 1
fi

# Also warn about untracked files, but do not necessarily block the run.
UNTRACKED="$(git ls-files --others --exclude-standard)"

if [ -n "$UNTRACKED" ]; then
    echo "Warning: The repository contains untracked files:"
    echo "$UNTRACKED"
    echo
fi

PROMPT=$(cat <<'EOF'
Find one new person for this year's physicist spotlight.

Follow all instructions in AGENTS.md and the documentation referenced by it.

Use the configured subagents and complete the full research, verification,
writing, validation, and append workflow.

RESEARCH

Run multiple candidate_researcher subagents in parallel.

Candidates may include:

- physicists;
- mathematicians whose work made a substantial and well-documented
  contribution to physics; or
- scientists in adjacent fields whose work substantially influenced physics.

Search all historical CSV files before selecting a candidate. Do not select
any person who has already appeared in the dataset.

Researchers should return several possible candidates with sources and
evidence rather than immediately drafting an entry.

CANDIDATE SELECTION

Compare the candidates and select the strongest one based on:

1. importance or relevance of the person's work to physics;
2. quality of the documented biographical story;
3. relevance to diversity, equity, inclusion, persistence, discrimination,
   or a nontraditional path into science;
4. quality and reliability of available sources; and
5. confirmation that the candidate has not appeared previously.

Do not infer sensitive personal characteristics from names, photographs,
nationality, institutions, or other indirect evidence.

FACT CHECKING

Send the selected candidate to the fact_checker.

The fact checker must independently verify:

- the person's contribution to physics;
- the facts supporting the biographical story;
- important dates and affiliations;
- the reliability of the sources; and
- that the candidate does not already appear in any historical CSV.

Only continue if the fact_checker returns PASS.

If the verdict is FAIL or NEEDS_MORE_EVIDENCE, do not append that candidate.

Instead, select another researched candidate and repeat fact checking if a
sufficiently strong alternative exists.

WRITING

After fact checking passes, send only the verified facts and evidence to the
spotlight_writer.

The spotlight_writer must:

- read docs/writing-style.md;
- examine historical examples;
- match the approximate length, structure, tone, and level of technical detail;
- explain the person's contribution to physics;
- describe the relevant biographical story accurately and respectfully; and
- introduce no unsupported facts.

VALIDATION

Before modifying the production CSV:

- run the duplicate checker;
- verify the CSV schema;
- verify all required fields;
- preserve existing column order and encoding; and
- run any other validation scripts described in AGENTS.md.

Use the project's deterministic append script if one exists.

Do not manually rewrite existing CSV records.

Append exactly one new entry.

After appending, run the validation suite again.

FINAL REPORT

At the end of the task, report:

1. the candidates considered;
2. the candidate selected;
3. why the candidate was selected;
4. evidence establishing the person's contribution to physics;
5. evidence supporting the relevant biographical story;
6. all important sources used;
7. the final spotlight text;
8. the validation results;
9. the files changed; and
10. the final git diff.

Do not commit the changes to Git. Leave the result for human review.
EOF
)

echo "Starting Codex..."
echo

codex exec "$PROMPT"

echo
echo "====================================="
echo "Codex run complete."
echo
echo "Review the changes carefully:"
echo
echo "  git diff"
echo
echo "  git status"
echo
echo "Do not commit the result until the new entry and its sources have been"
echo "reviewed by a human."