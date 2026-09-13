# Execution workflow

Run `make spotlight DATE=MM/DD/YYYY` from the root after reviewing and committing
setup changes. Keep CSV inputs local and ignored by Git. The runner checks prerequisites, Git state, and
all CSVs before launching Codex. It snapshots all CSV hashes, byte lengths, and
record counts in a unique research/run-MM-DD-YYYY-* directory. Commands accept
American dates such as `09/15/2026` or `9/15/2026`; four-digit years are required.
Slashes become hyphens only in folder names. CSV dates remain M/D/YY.

1. Parent reads every CSV and these docs.
2. Parallel candidate_researcher agents return candidates and evidence, read-only.
3. Parent selects an unused candidate. fact_checker independently verifies facts.
4. Only after PASS, spotlight_writer drafts from verified facts.
5. fact_checker reviews the exact draft against the sources, checks every factual
   statement, and returns PASS, FAIL, or NEEDS_MORE_EVIDENCE with notes.
6. Parent saves candidate.json and report.md in the run directory. The report
   includes candidates considered, selection rationale, and sources.
7. Shell checks that research changed no CSVs, validates the bundle, appends using
   the deterministic script, and audits the result. Agents never append directly.

Supply hashes using `python3 scripts/spotlight.py hashes --candidate PATH`.
Give those exact claims and row to the reviewer. Record its actual verdict and
hashes; never invent a PASS or recycle a verdict after editing. The second review
must account for all claims in the bundle; remove unused claims before review.

If a candidate fails, try another researched candidate, at most three selections
per run. If none passes, save the failure report and stop. A missing or failing
bundle causes the launcher to exit without appending. Failed runs retain evidence.
Start a new run after review; do not blindly retry an append. Duplicate checks reject
an already appended person and snapshot checks reject stale submissions.

For an explicitly authorized interactive append, first save a snapshot with
`python3 scripts/spotlight.py snapshot --snapshot research/BEFORE.json`, prepare and
review the bundle, then invoke `python3 scripts/append_candidate.py --candidate
research/CANDIDATE.json --snapshot research/BEFORE.json --date MM/DD/YYYY`.
Audit using `python3 scripts/spotlight.py audit --snapshot research/BEFORE.json`.

Appends use an advisory lock and atomically replace the output with its original
bytes followed by one encoded CSV record. Other CSVs must remain unchanged.
External editors must not modify data during a run. The parent still has workspace
write permission: these gates detect data changes, not an adversarial parent that
alters its own validators. Review code diffs before committing implementation changes.
Review local candidate.json, report.md, and the output CSV separately. Data and
research files are ignored by Git and must not be committed. Snapshot and audit
checks protect local data independently of Git tracking.
