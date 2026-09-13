# Physicist Spotlight Research Agent

This repository uses **OpenAI Codex and specialized subagents** to research and draft short biographical spotlights about physicists, mathematicians, and related scientists whose lives or careers highlight diversity, equity, inclusion, persistence, discrimination, or nontraditional paths into science.

The system searches publicly available sources, checks candidates against people used in previous years, verifies biographical claims, writes a new entry in the style of previous entries, validates the resulting data, and appends the approved entry to the project CSV.

The goal is to automate the repetitive parts of the research process while keeping the final result traceable and reviewable.

---

## What Counts as an Eligible Candidate?

Candidates do not have to formally hold the title of **physicist**.

A person may be selected if they:

- worked primarily as a physicist;
- made an important contribution directly to physics;
- developed mathematics that became foundational to an important area of physics; or
- worked in another scientific field but made a clearly documented contribution to physical theory or our understanding of physical phenomena.

For example, a mathematician such as **Emmy Noether** is within scope because Noether's theorem is foundational to modern theoretical physics.

The candidate should also have a documented aspect of their life or career relevant to the purpose of the project. Examples might include:

- discrimination or exclusion;
- an underrepresented background;
- a nontraditional education;
- entering science unusually late;
- immigration or displacement;
- socioeconomic barriers;
- disability;
- major career interruptions;
- barriers to obtaining an education or scientific position;
- unusual routes into physics or mathematics; or
- other well-documented experiences relevant to diversity, equity, inclusion, or persistence.

These characteristics must be supported by reliable sources. Agents should **never infer sensitive personal characteristics from a name, photograph, nationality, or other indirect information.**

---

# How It Works

The project uses a small collection of specialized Codex agents.

```text
                    ┌──────────────────────┐
                    │     Parent Agent     │
                    │     AGENTS.md        │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       Candidate Researcher         Candidate Researcher
                 │                           │
                 └─────────────┬─────────────┘
                               │
                               ▼
                     Candidate Selection
                               │
                               ▼
                       ┌──────────────┐
                       │ Fact Checker │
                       └──────┬───────┘
                              │
                            PASS
                              │
                              ▼
                    ┌──────────────────┐
                    │ Spotlight Writer │
                    └────────┬─────────┘
                             │
                             ▼
                       Proposed Entry
                             │
                             ▼
                      CSV Validation
                             │
                             ▼
                      Append to CSV
```

The research and fact-checking agents are read-only.

Only the parent workflow should perform the final append after validation succeeds.

---

# Repository Structure

The repository is organized approximately as follows:

```text
.
├── AGENTS.md
├── README.md
│
├── .codex/
│   ├── config.toml
│   └── agents/
│       ├── candidate-researcher.toml
│       ├── fact-checker.toml
│       └── spotlight-writer.toml
│
├── data/
│   ├── physicists.csv
│   └── archive/
│       ├── physicists-2024.csv
│       ├── physicists-2025.csv
│       └── ...
│
├── docs/
│   ├── selection-criteria.md
│   ├── source-policy.md
│   ├── writing-style.md
│   └── csv-schema.md
│
├── scripts/
│   ├── check_duplicate.py
│   ├── validate_csv.py
│   └── append_candidate.py
│
└── research/
    └── .gitkeep
```

### `AGENTS.md`

Contains the top-level instructions Codex follows when working in this repository.

It defines the overall research and validation workflow and tells the parent agent when to delegate work to the specialized subagents.

### `.codex/agents/`

Contains the specialized Codex agents.

#### `candidate-researcher.toml`

Searches for possible candidates and returns structured evidence and sources.

Multiple candidate researchers can run in parallel.

#### `fact-checker.toml`

Independently checks the selected candidate and determines whether the claims are sufficiently supported.

The candidate must receive a `PASS` before an entry is written.

#### `spotlight-writer.toml`

Takes verified research and writes an entry matching the style of previous years.

The writer should not introduce new facts that were not present in the verified research.

### `data/`

Contains the current dataset and historical datasets.

Historical files are important because they allow Codex to:

1. avoid selecting someone who has already been used;
2. understand the expected writing style; and
3. understand the CSV format.

### `docs/`

Contains detailed instructions that would otherwise make `AGENTS.md` unnecessarily large.

### `scripts/`

Contains deterministic checks for operations that should not depend on an LLM, such as duplicate detection and CSV validation.

---

# Requirements

You will need:

- Git
- Python 3
- OpenAI Codex CLI
- access to Codex through your OpenAI/ChatGPT account

Install Codex CLI using the official OpenAI installer or package manager.

For an npm installation, Codex can be installed with:

```bash
npm install --global @openai/codex
```

Verify that Codex is available:

```bash
codex --version
```

---

# Initial Setup

Clone the repository and enter it:

```bash
git clone <repository>
cd <repository>
```

Place the existing spotlight CSVs in `data/`.

For example:

```text
data/
├── physicists.csv
└── archive/
    ├── physicists-2024.csv
    └── physicists-2025.csv
```

Previous years should remain available because the agents use them both for duplicate detection and as writing examples.

---

## Codex Configuration

Project-specific Codex configuration lives in:

```text
.codex/config.toml
```

A typical configuration for this project is:

```toml
sandbox_mode = "workspace-write"
approval_policy = "on-request"
web_search = "live"

[agents]
enabled = true
max_concurrent_threads_per_session = 4
default_subagent_reasoning_effort = "medium"

[sandbox_workspace_write]
network_access = false
```

The research agents have their own permissions defined in `.codex/agents/`.

Research and fact-checking agents should normally use:

```toml
sandbox_mode = "read-only"
```

This prevents a research agent from modifying the dataset while investigating candidates.

---

# Running the Project

## Recommended: Interactive Run

Start from the repository root:

```bash
codex
```

The first time Codex is run, follow the login instructions presented by the CLI.

Once Codex starts, give it a task such as:

```text
Find one new person for this year's physicist spotlight.

Follow the complete workflow in AGENTS.md.

Use multiple candidate_researcher agents in parallel.

Candidates may be physicists or mathematicians/scientists whose work made
a substantial and well-documented contribution to physics.

Check every historical CSV before selecting someone.

Have the fact_checker independently verify the selected candidate.

Only continue if the fact checker returns PASS.

Have the spotlight_writer produce the final entry using the style of the
historical entries.

Run all duplicate and CSV validation checks before modifying the dataset.

Append exactly one entry to the current CSV.

At the end, report:
- candidates considered;
- the candidate selected;
- why they were selected;
- evidence supporting the physics connection;
- evidence supporting the biographical story;
- sources used;
- the final spotlight text;
- validation results; and
- the final git diff.
```

Codex will read `AGENTS.md` and use the project-scoped agents under `.codex/agents/`.

---

# What a Normal Run Should Do

A successful run should follow this sequence.

### 1. Inspect existing data

Codex reads the historical CSV files and determines:

- which people have already been used;
- the expected CSV schema;
- the approximate length of each spotlight;
- the tone and writing style; and
- the balance between scientific and biographical information.

### 2. Search for candidates

Multiple `candidate_researcher` agents search independently.

Researchers may use sources such as:

- Wikipedia for initial discovery;
- universities;
- national laboratories;
- professional scientific societies;
- oral-history archives;
- scientific institutions;
- museums;
- published interviews; and
- reputable historical or biographical sources.

Each researcher returns several candidates rather than immediately writing an entry.

### 3. Select the best candidate

The parent agent compares the candidates based on:

- importance or relevance to physics;
- quality of the biographical story;
- relevance to the purpose of the project;
- quality of available sources; and
- whether the person has already appeared in the dataset.

### 4. Independently verify the candidate

The selected candidate is sent to the `fact_checker`.

The fact checker verifies both:

1. the person's contribution to physics; and
2. the biographical facts that make the person relevant to this project.

The fact checker returns one of:

```text
PASS
FAIL
NEEDS_MORE_EVIDENCE
```

Only `PASS` should allow the workflow to continue.

### 5. Write the spotlight

The verified evidence is sent to the `spotlight_writer`.

The writer reads the previous entries and `docs/writing-style.md` before producing the new entry.

The writer should not introduce unsupported facts or exaggerate the role of adversity in the person's life.

The person's scientific work should remain an important part of the spotlight.

### 6. Validate the proposed entry

Before editing the production CSV, the workflow runs the deterministic validation scripts.

For example:

```bash
python scripts/check_duplicate.py
python scripts/validate_csv.py
```

If the project uses a structured intermediate file, the final append may look like:

```bash
python scripts/append_candidate.py candidate.json
```

The exact arguments should match the implementation of the scripts in this repository.

### 7. Review the result

After the append, validation should be run again.

Finally, inspect the change:

```bash
git diff
```

The expected diff should contain exactly one newly appended spotlight entry and no unexpected modifications to existing records.

---

# Running Non-Interactively

Codex also supports non-interactive tasks through `codex exec`.

For example:

```bash
codex exec "Find one new physicist spotlight candidate and follow the complete workflow in AGENTS.md. Append exactly one entry only after fact checking and validation pass. Report the evidence, sources, validation results, and final diff."
```

Interactive execution is recommended while developing or changing the workflow because it makes it easier to inspect research and proposed changes before accepting them.

Non-interactive execution is more useful once the process is stable.

---

# Before Every Run

It is a good idea to begin from a clean Git state.

Check:

```bash
git status
```

Commit any existing work before running the agent.

For example:

```bash
git add .
git commit -m "Checkpoint before spotlight research"
```

This makes it easy to inspect or revert the agent's changes.

---

# After Every Run

Inspect the result:

```bash
git diff
```

Check that:

- exactly one intended record was added;
- no historical rows changed;
- the candidate was not previously used;
- important biographical claims have citations or source records;
- the scientific contribution is accurately described;
- sensitive characteristics were not inferred;
- the prose matches the style of previous entries; and
- CSV validation passes.

If everything looks correct:

```bash
git add data/physicists.csv
git commit -m "Add physicist spotlight"
```

---

# Source Policy

Wikipedia is useful for **discovery**, but it should generally not be the only source supporting important biographical claims.

Prefer primary or institutionally curated sources when available.

A rough source hierarchy is:

### Strong sources

- oral-history archives;
- universities;
- national laboratories;
- professional scientific societies;
- government scientific institutions;
- Nobel Prize biographies;
- interviews with the scientist;
- archival collections.

### Useful secondary sources

- major museums;
- reputable encyclopedias;
- scholarly biographies;
- major newspapers and magazines;
- Wikipedia articles with strong citations.

### Sources to avoid

- unsourced blogs;
- SEO-generated biography sites;
- social-media speculation;
- AI-generated biographies;
- pages that do not identify where their claims came from.

Sensitive or potentially controversial claims should receive particularly careful verification.

---

# Avoiding Unsupported DEI Claims

This project is interested in scientists whose experiences may help illustrate diversity, equity, inclusion, persistence, or nontraditional paths into science.

That does **not** mean agents should attempt to classify people themselves.

Agents must not infer characteristics such as:

- race;
- ethnicity;
- religion;
- disability;
- sexual orientation;
- socioeconomic status;
- gender identity; or
- experiences of discrimination

from photographs, names, nationalities, institutions, or other indirect evidence.

If such information appears in a spotlight, it must be explicitly documented by a credible source.

Likewise, an agent should not assume someone experienced discrimination simply because they belonged to a historically underrepresented group.

---

# Mathematicians and Other Scientists

Mathematicians and scientists outside physics may be included when the connection to physics is substantial and documented.

For these candidates, the research should explicitly answer:

> What did this person contribute that mattered to physics?

The answer should be specific.

For example, saying:

> This mathematician's work has applications in physics.

is generally insufficient.

A stronger case would establish that a theorem, formalism, mathematical structure, or method became foundational to areas such as:

- quantum mechanics;
- quantum field theory;
- relativity;
- statistical mechanics;
- condensed-matter physics;
- particle physics;
- astrophysics; or
- another identifiable area of physics.

---

# Updating the Writing Style

Historical entries should be the primary guide for style.

If the historical dataset changes substantially, ask Codex to regenerate the style guide:

```text
Analyze all historical spotlight entries under data/archive/.

Determine the typical:
- word count;
- paragraph structure;
- tone;
- amount of scientific detail;
- amount of biographical detail;
- use of dates;
- treatment of adversity and identity; and
- recurring stylistic conventions.

Update docs/writing-style.md with your findings.

Do not modify any CSV files.
```

Review the resulting style guide before committing it.

---

# Safety and Human Review

This project uses AI-assisted web research.

The generated entry should therefore be considered a **research draft until reviewed by a human**.

In particular, manually inspect:

- claims concerning discrimination;
- claims about personal identity;
- descriptions of historical events;
- descriptions of scientific contributions;
- quotations;
- dates;
- institutional affiliations; and
- statements derived from only one source.

The agent workflow is intended to reduce mundane research and formatting work, not eliminate editorial responsibility.

---

# Development Philosophy

The project separates tasks according to what they are best suited for.

Use language models for:

```text
search
↓
interpretation
↓
comparison
↓
fact checking
↓
writing
```

Use deterministic code for:

```text
duplicate detection
↓
schema checking
↓
CSV parsing
↓
validation
↓
final append
```

This separation makes the workflow easier to inspect, test, and rerun safely.

---

# Quick Start

For an existing installation, the entire process is roughly:

```bash
git clone <repository>
cd <repository>

git status

codex
```

Then tell Codex:

```text
Find one new person for this year's physicist spotlight.

Follow AGENTS.md and use the configured subagents.

Do not append anything unless independent fact checking and all validation
checks pass.

Append exactly one entry and show me the final evidence and git diff.
```

Review the result:

```bash
git diff
```

If it looks correct:

```bash
git add data/physicists.csv
git commit -m "Add physicist spotlight"
```
