# Physicist Spotlight Research Agent

A Codex workflow for researching one unused physicist or scientist/mathematician
whose work substantially influenced physics and whose documented life illustrates
inclusion, persistence, discrimination, or a nontraditional path into science.

The parent coordinates read-only researchers, a fact checker, and a writer.
Python validates their saved evidence bundle and appends exactly one record.
The final written paragraph receives a second fact-check review before append.

## Setup

Requires Git, Python 3.10+ on macOS/Linux, and an installed, authenticated Codex CLI.
Project agent definitions live in `.codex/agents/`. Read `AGENTS.md` and `docs/`.

The current CSV is configured in `spotlight.json`. Historical CSVs remain under
`data/archive/`. All CSV inputs must be tracked so Git can show resulting changes.
Review and commit the initial data and implementation before an autonomous run.
No command in this project automatically commits changes.

```bash
make test
make validate
make spotlight DATE=2026-09-15
make diff
make status
```

Use your intended newsletter date. A run requires a clean Git state, including
untracked files. The runner creates `research/run-*/before.json`, `candidate.json`,
and `report.md`. Review the evidence, exact prose, validation output, and Git diff
before committing the CSV and research records. Research artifacts are not ignored.

## Components

- `scripts/spotlight.py`: CSV parsing, name checks, evidence gates, snapshots, atomic append, audit.
- `scripts/check_duplicate.py`: validate duplicate-free history, optionally a candidate bundle.
- `scripts/validate_csv.py`: validate data, optionally a reviewed candidate bundle.
- `scripts/append_candidate.py`: append with a snapshot, bundle, and explicit date.
- `scripts/run_spotlight.sh`: preflight, research dispatch, validation, append, audit.
- `tests/`: temporary-data tests, including failures and preservation of original bytes.

See `docs/csv-schema.md` for evidence JSON and historical schema handling,
`docs/workflow.md` for review gates and interactive commands,
`docs/source-policy.md` for factual requirements, and `docs/writing-style.md` for prose.

The code validates structure and recorded verdicts, not historical truth. Independent
source review and human editorial review remain necessary. Alias detection is not
complete identity resolution; close matches stop for review. Files must not be edited
externally during a run. Failed runs keep their research records for inspection.
