# CSV and evidence schema

`spotlight.json` defines the sole output path and optional alias-to-canonical-name
mapping. The default output is `data/Scientist of the Week - Fa26.csv`.

Output columns, in order: Newsletter Date, Scientist, Description, Picture.
Command dates use MM/DD/YYYY, such as `09/15/2026` (single-digit months/days also
work). A four-digit year is required for command input.

All CSV values are strings. The first three must be nonempty. Dates use M/D/YY and must
be real calendar dates matching the requested newsletter date. Picture is optional.
CSV is UTF-8; preserve its existing BOM, newline convention, and all previous bytes.

Historical readers accept the current header and the legacy header
`Name,Date in Newsletter,Description,Column 1`, skipping empty records. Legacy names
and dates are reordered only in memory. Unknown headers and malformed rows fail.

Names are compared after Unicode normalization, case folding, title and punctuation
removal, whitespace normalization, and explicit aliases. Close matches stop for
identity review. This cannot identify every alias; researchers must check identity.
Record documented aliases in spotlight.json before a run. Do not guess equivalence.

## candidate.json

Use this shape (placeholder hashes must be replaced following actual reviews):

```json
{
  "row": {
    "Newsletter Date": "9/15/26",
    "Scientist": "Example Scientist",
    "Description": "The final verified paragraph.",
    "Picture": ""
  },
  "claims": [
    {"id": "p1", "kind": "physics", "text": "Specific scientific contribution",
     "sources": [{"url": "https://example.org/biography", "evidence": "Source evidence summary"}]},
    {"id": "b1", "kind": "biography", "text": "Documented biographical experience",
     "sources": [{"url": "https://example.org/interview", "evidence": "Source evidence summary"}]}
  ],
  "fact_check": {
    "verdict": "PASS", "reviewer": "fact_checker", "notes": "Independent verification findings",
    "claims_sha256": "HASH"
  },
  "draft_check": {
    "verdict": "PASS", "reviewer": "fact_checker", "notes": "Review of every factual statement in the exact draft",
    "claims_sha256": "HASH", "row_sha256": "HASH",
    "supported_claim_ids": ["p1", "b1"]
  }
}
```

Hashes bind reviews to canonical JSON: sorted keys, Unicode unescaped, compact
separators, UTF-8, SHA-256. Use the hashes command in workflow.md. Hashes detect
changed content; they are not signatures or proof that factual verification occurred.
