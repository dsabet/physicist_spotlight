# Physicist Spotlight Research Agent

A Codex workflow that researches one unused scientist, verifies the evidence, writes
a short newsletter spotlight, reviews the final draft, and appends exactly one row
to a local CSV. Existing entries and historical files must remain unchanged.

## Eligible candidates

Candidates may be physicists, mathematicians, or scientists in adjacent fields.
Their work must have a substantial, reliably documented contribution to physics.
Possible applications alone are insufficient. The spotlight also needs documented
life or career experiences relevant to diversity, equity, inclusion, persistence,
discrimination, or a nontraditional path into science.

Agents must never infer personal characteristics or discrimination from names,
photos, nationality, or group membership. Every important claim needs reliable
sources. Historical entries guide writing style; they are not factual authorities.

## Requirements and setup

- Git and Make.
- Python 3.10+ on macOS/Linux. The validation scripts use the standard library.
- An installed, authenticated Codex CLI with access to the configured models.
- A clean Git working tree before launching research. Ignored local data is allowed.

After cloning, add your CSVs locally. The repository publishes only `.gitkeep`
placeholders for the data and research folders; `.gitkeep` is a conventional empty
file that lets Git retain a folder structure.

```text
.codex/
  config.toml                       Parent model and subagent defaults
  agents/
    canditate-researcher.toml        Candidate researcher (existing filename)
    fact-checker.toml                Independent fact checker
    spotlight-writer.toml           Writer
AGENTS.md                           Project rules and delegation workflow
Makefile                            Commands run from the repository root
spotlight.json                      Output path and documented name aliases
data/
  .gitkeep
  Scientist of the Week - Fa26.csv   Local current dataset
  archive/
    .gitkeep
    ...                             Local historical CSVs
research/
  .gitkeep
  run-MM-DD-YYYY-XXXXXX/             Local evidence and reports per run
scripts/                            Runner, validators, append, and audit
docs/                              Detailed policies and schemas
tests/                             Automated tests using temporary data
```

## Configure the output and aliases

`spotlight.json` contains:

```json
{
  "output": "data/Scientist of the Week - Fa26.csv",
  "aliases": {}
}
```

Place the current CSV at that path, or change `output` to another CSV inside `data/`.
The file must already exist with the current header; the workflow does not silently
create a new dataset. A header-only current CSV is allowed. Keep all available
historical CSVs beneath `data/` so duplicate checks include previous years.

Add documented alternate names to `aliases` as alternate-name-to-canonical-name
pairs when needed. The reader normalizes Unicode, capitalization, titles,
punctuation, and whitespace. Exact matches and explicit aliases reject duplicates;
close matches stop for identity review. Name matching cannot detect every alias.

## Models and reasoning effort

The configured assignments are:

| Role | Model ID | Reasoning effort |
| --- | --- | --- |
| Parent/orchestrator | `gpt-6-astra` | `medium` |
| Candidate researcher | `gpt-5.6-terra` | `medium` |
| Fact checker, including final draft review | `gpt-5.6-sol` | `medium` |
| Spotlight writer | `gpt-5.6-luna` | `medium` |
| Other subagent default | `gpt-5.6-terra` | `medium` |

Astra coordinates the full workflow. Terra balances research and tool use with cost.
Sol handles evidence judgment, while Luna writes a short entry from verified facts.
These are task-based choices, not a benchmark of this project's output quality.
See the [official model guide](https://learn.chatgpt.com/docs/models).

Set the parent `model` and `model_reasoning_effort` at the top of
`.codex/config.toml`, before any section. Subagent defaults live under `[agents]`.
Each specialist's TOML file sets its own `model` and `model_reasoning_effort`.
The subagents remain configured as read-only. Up to four subagent threads may be
open concurrently, excluding the parent. Live web search is enabled; shell-level
network access is disabled in the project configuration.

Explicit runtime overrides can supersede model defaults. These settings are not a
hard spending cap. Availability depends on your account and Codex client. Editing
configuration does not launch research; the next run reads the saved settings.

## Run the workflow

From the repository root:

```bash
make spotlight DATE=09/15/2026
```

Use the intended newsletter date in **American MM/DD/YYYY format**. `9/15/2026`
also works. A four-digit year is required; invalid dates and ISO-style command dates
are rejected before any research starts. CSV entries retain the existing M/D/YY
format, for example `9/15/26`. Run folder names use hyphens instead of slashes, such
as `research/run-09-15-2026-XXXXXX/`.

The root Makefile invokes the shell script with `bash`, so the runner does not need
an executable permission bit. The script resolves the project root before working.

| Command | Purpose |
| --- | --- |
| `make help` | List available commands |
| `make test` | Test temporary datasets and a fake model; no real research calls |
| `make validate` | Check local CSV structure and duplicate-free history |
| `make spotlight DATE=09/15/2026` | Launch research and append after passing checks |
| `make diff` | Show tracked code/configuration changes, not local CSV changes |
| `make status` | Show Git status, excluding ignored data and research |

## Research, verification, and append

1. The runner checks the date, prerequisites, clean Git state, and all CSVs. It saves
   hashes, byte lengths, and record counts in a unique run directory.
2. The parent reads the historical entries and delegates parallel discovery to
   `candidate_researcher` agents. Researchers return candidates, evidence, and URLs.
3. The parent selects an unused candidate. `fact_checker` independently checks the
   physics contribution, biographical story, dates, affiliations, and sources.
4. Only after a PASS, `spotlight_writer` drafts the entry using verified facts.
5. `fact_checker` reviews the exact final row against its evidence. Both reviews
   must PASS, and any subsequent content edit requires renewed review.
6. The parent saves the evidence bundle and selection report. It does not edit CSVs.
7. The shell checks for unexpected tracked-file or CSV changes, validates the bundle,
   and invokes the deterministic append script. It audits the result afterwards.

The append uses an advisory lock and an atomic file replacement. The replacement
contains the original bytes followed by exactly one properly encoded CSV record.
It handles quoted commas and multiline descriptions, preserves the existing UTF-8
BOM and newline convention, and checks that historical CSVs did not change.
Do not edit data externally during a run; the lock coordinates project appends.

## Expected output and review

On success, the configured local CSV contains exactly one new spotlight row. The
run directory contains:

| File | Contents |
| --- | --- |
| `before.json` | Original CSV hashes, sizes, and record counts; not a full backup |
| `candidate.json` | Exact row, claims, source URLs, evidence summaries, both verdicts, and content hashes |
| `report.md` | Candidates considered, selection rationale, and sources |

The terminal reports validation and audit results. Review the local CSV and these
research files directly. Git diff does not show ignored CSV changes. Snapshot and
audit checks verify preservation, while you review scientific accuracy and prose.
Nothing automatically commits or pushes. Back up local data and research separately.

The description is normally one accessible paragraph, roughly 120–175 words, with
scientific achievement and documented life experience both represented. The existing
examples range from 111 to 211 words; length is guidance, not a hard validation gate.
Picture may remain empty. Evidence stays in the research bundle.

## Failure handling and limitations

A successful Codex exit alone does not permit an append. Missing reports, failing
verdicts, missing evidence, stale hashes, duplicates, ambiguous names, date mismatches,
malformed CSVs, and unexpected data changes block the normal append path. Failed
runs retain available research for review. At most three researched candidates may
be tried in a run; if none passes, the agent records the reason and stops.

A repeated submission is rejected by duplicate and snapshot checks. Review a failure
before starting a new run; do not bypass gates or invent a PASS. Code validates the
structure and recorded verdicts, not the truth of sources or the independence of a
review. Hashes bind reviews to content but are not signatures. The parent still has
workspace-write access; this is not protection against an adversarial parent that
rewrites the validators themselves.

## CSV schemas and tools

Current output columns, in order:

```text
Newsletter Date,Scientist,Description,Picture
```

The first three fields are required strings; Picture is optional. Historical input
also supports `Name,Date in Newsletter,Description,Column 1`, including leading empty
records. Its name/date order is mapped in memory; historical files are not rewritten.
Unknown headers and malformed rows fail rather than being silently skipped.

`scripts/spotlight.py` contains the shared reader, alias handling, validation,
snapshots, hashes, append, and audit. Thin command wrappers are:

- `scripts/check_duplicate.py`: check history, optionally a proposed evidence bundle.
- `scripts/validate_csv.py`: validate history, optionally a proposed evidence bundle.
- `scripts/append_candidate.py`: require a reviewed bundle, original snapshot, and date.

For an explicitly intended manual append, the commands are:

```bash
python3 scripts/spotlight.py snapshot --snapshot research/BEFORE.json
# Prepare and independently review research/CANDIDATE.json before continuing.
python3 scripts/validate_csv.py --candidate research/CANDIDATE.json --date 09/15/2026
python3 scripts/append_candidate.py --candidate research/CANDIDATE.json --snapshot research/BEFORE.json --date 09/15/2026
python3 scripts/spotlight.py audit --snapshot research/BEFORE.json
```

See [CSV and evidence schema](docs/csv-schema.md) for the bundle format and
[execution workflow](docs/workflow.md) for hashes and review gates. See
[selection criteria](docs/selection-criteria.md), [source policy](docs/source-policy.md),
and [writing style](docs/writing-style.md) for editorial rules.

## Local data and GitHub

`.gitignore` excludes data and generated research while retaining `data/.gitkeep`,
`data/archive/.gitkeep`, and `research/.gitkeep`. It also ignores Python caches,
`.DS_Store`, and the append lock. Do not force-add local data or research to Git.

Older repository commits contained CSV data. Ignoring and untracking files removes
them from the current version, not older history. Removing historical copies requires
a separate history cleanup; this project has not performed that cleanup.
