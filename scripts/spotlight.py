"""Standard-library CSV checks and the sole production append operation."""
import argparse
import csv
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["Newsletter Date", "Scientist", "Description", "Picture"]
LEGACY = ["Name", "Date in Newsletter", "Description", "Column 1"]


def parse_newsletter_date(value):
    """Accept American command-line dates with a four-digit year."""
    if not re.fullmatch(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}", value):
        raise ValueError("Use an American date: MM/DD/YYYY (for example 09/15/2026)")
    try:
        return datetime.strptime(value, "%m/%d/%Y").date()
    except ValueError:
        raise ValueError("Newsletter date must be a real date in MM/DD/YYYY format") from None


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def normalize(name):
    name = unicodedata.normalize("NFKC", name).casefold().strip()
    name = re.sub(r"^(?:(?:dr|dra|prof|professor|physicist)\.?\s+)+", "", name)
    return " ".join("".join(c for c in name if not unicodedata.category(c).startswith("P")).split())


def settings(root):
    config = json.loads((root / "spotlight.json").read_text())
    output = (root / config["output"]).resolve()
    if not output.is_relative_to((root / "data").resolve()) or output.suffix != ".csv":
        raise ValueError("Output must be a CSV inside data/")
    aliases = {normalize(k): normalize(v) for k, v in config["aliases"].items()}
    for key in aliases:
        canonical(key, aliases)
    return output, aliases


def canonical(name, aliases):
    name = normalize(name)
    seen = set()
    while name in aliases:
        if name in seen:
            raise ValueError("Alias cycle")
        seen.add(name)
        name = aliases[name]
    return name


def validate_row(row):
    if set(row) != set(FIELDS) or any(not isinstance(v, str) for v in row.values()):
        raise ValueError("Row must contain exactly the four documented string fields")
    for field in FIELDS[:3]:
        if not row[field].strip():
            raise ValueError(f"Missing {field}")
    if not normalize(row["Scientist"]):
        raise ValueError("Empty scientist name")
    datetime.strptime(row["Newsletter Date"], "%m/%d/%y")


def read_csv(path, raw=None):
    raw = path.read_bytes() if raw is None else raw
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True))
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows or rows[0] not in (FIELDS, LEGACY):
        raise ValueError(f"{path}: unknown or missing CSV header")
    header = rows[0]
    result = []
    for number, values in enumerate(rows[1:], 2):
        if len(values) != 4:
            raise ValueError(f"{path}: record {number} has {len(values)} columns")
        if header == LEGACY:
            values = [values[1], values[0], values[2], values[3]]
        row = dict(zip(FIELDS, values))
        validate_row(row)
        result.append(row)
    return header, result


def inventory(root):
    output, aliases = settings(root)
    paths = sorted((root / "data").rglob("*.csv"))
    if not output.is_file() or not paths:
        raise ValueError("Configured output or historical CSVs are missing")
    people = {}
    for path in paths:
        header, rows = read_csv(path)
        if path.resolve() == output and header != FIELDS:
            raise ValueError("Output must use the current schema")
        for row in rows:
            key = canonical(row["Scientist"], aliases)
            if key in people:
                raise ValueError(f"Duplicate scientist {row['Scientist']}: {people[key]} and {path}")
            people[key] = str(path)
    return people


def check_name(root, name):
    people = inventory(root)
    _, aliases = settings(root)
    key = canonical(name, aliases)
    if key in people:
        raise ValueError(f"Scientist already used: {name} ({people[key]})")
    similar = difflib.get_close_matches(key, people, n=3, cutoff=0.86)
    if similar:
        raise ValueError(f"Ambiguous name match; review identity before proceeding: {similar}")


def validate_bundle(root, bundle, date=None):
    row = bundle["row"]
    validate_row(row)
    check_name(root, row["Scientist"])
    if date and datetime.strptime(row["Newsletter Date"], "%m/%d/%y").date() != parse_newsletter_date(date):
        raise ValueError("Draft newsletter date differs from requested date")
    claims = bundle["claims"]
    if not isinstance(claims, list) or not claims:
        raise ValueError("Evidence claims are required")
    ids = set()
    for claim in claims:
        if not isinstance(claim["id"], str) or not claim["id"] or claim["id"] in ids:
            raise ValueError("Claim IDs must be unique nonempty strings")
        ids.add(claim["id"])
        if claim["kind"] not in ("physics", "biography") or not claim["text"].strip() or not claim["sources"]:
            raise ValueError("Each claim needs a kind, text, and sources")
        for source in claim["sources"]:
            if not re.match(r"https?://[^/\s]+", source["url"]) or not source["evidence"].strip():
                raise ValueError("Each source needs a URL and supporting evidence")
    if {c["kind"] for c in claims} != {"physics", "biography"}:
        raise ValueError("Both physics and biography evidence are required")
    facts = bundle["fact_check"]
    draft = bundle["draft_check"]
    for check in (facts, draft):
        if check["verdict"] != "PASS" or check["reviewer"] != "fact_checker" or not check["notes"].strip():
            raise ValueError("Both reviews must PASS with fact_checker notes")
    if facts["claims_sha256"] != digest(claims) or draft["claims_sha256"] != digest(claims):
        raise ValueError("Evidence changed after review")
    if draft["row_sha256"] != digest(row):
        raise ValueError("Draft changed after review")
    if set(draft["supported_claim_ids"]) != ids:
        raise ValueError("Draft review must account for all supplied claims")
    return row


def snapshot(root):
    inventory(root)
    return {str(p.relative_to(root)): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                                     "size": p.stat().st_size,
                                     "rows": len(read_csv(p)[1])}
            for p in sorted((root / "data").rglob("*.csv"))}


def unchanged(root, before):
    if snapshot(root) != before:
        raise ValueError("CSV data changed during research; refusing append")


def audit(root, before):
    after = snapshot(root)
    output, _ = settings(root)
    target = str(output.relative_to(root.resolve()))
    if set(before) != set(after):
        raise ValueError("CSV file set changed")
    for path, old in before.items():
        if path != target:
            if after[path] != old:
                raise ValueError(f"Historical CSV changed: {path}")
        else:
            raw = output.read_bytes()
            if hashlib.sha256(raw[:old["size"]]).hexdigest() != old["sha256"] or after[path]["rows"] != old["rows"] + 1:
                raise ValueError("Output must preserve original bytes and add exactly one row")


def append(root, bundle, before, date=None):
    # OS releases this advisory lock on crashes. All project appends use this path.
    import fcntl
    with (root / ".spotlight.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        unchanged(root, before)
        row = validate_bundle(root, bundle, date)
        output, _ = settings(root)
        original = output.read_bytes()
        ending = "\r\n" if b"\r\n" in original else "\n"
        buffer = io.StringIO(newline="")
        csv.writer(buffer, lineterminator=ending).writerow([row[k] for k in FIELDS])
        separator = b"" if original.endswith((b"\n", b"\r")) else ending.encode()
        proposed = original + separator + buffer.getvalue().encode("utf-8")
        if len(read_csv(output, proposed)[1]) != len(read_csv(output, original)[1]) + 1:
            raise ValueError("Append did not produce exactly one record")
        temp = None
        try:
            with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as stream:
                temp = Path(stream.name)
                stream.write(proposed)
                stream.flush()
                os.fsync(stream.fileno())
            temp.chmod(output.stat().st_mode & 0o777)
            unchanged(root, before)
            os.replace(temp, output)
            audit(root, before)
        finally:
            if temp and temp.exists():
                temp.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "duplicates", "snapshot", "unchanged", "append", "audit", "hashes", "date"])
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--date", help="Newsletter date in MM/DD/YYYY format")
    args = parser.parse_args(argv)
    try:
        if args.date is not None:
            parse_newsletter_date(args.date)
        if args.command == "date":
            if not args.date:
                raise ValueError("--date MM/DD/YYYY is required")
            print(parse_newsletter_date(args.date).strftime("%m-%d-%Y"))
            return 0
        bundle = json.loads(args.candidate.read_text()) if args.candidate else None
        before = json.loads(args.snapshot.read_text()) if args.snapshot and args.command != "snapshot" else None
        if args.command in ("validate", "duplicates"):
            inventory(ROOT)
            if bundle:
                validate_bundle(ROOT, bundle, args.date)
        elif args.command == "snapshot":
            if not args.snapshot:
                raise ValueError("--snapshot is required")
            with args.snapshot.open("x") as stream:
                json.dump(snapshot(ROOT), stream, indent=2)
        elif args.command == "hashes":
            print(json.dumps({"row_sha256": digest(bundle["row"]), "claims_sha256": digest(bundle["claims"])}))
        elif args.command == "append":
            if bundle is None or before is None or not args.date:
                raise ValueError("--candidate, --snapshot and --date are required")
            append(ROOT, bundle, before, args.date)
        else:
            if before is None:
                raise ValueError("--snapshot is required")
            (audit if args.command == "audit" else unchanged)(ROOT, before)
        if args.command != "hashes":
            print(f"PASS: {args.command}")
    except (ValueError, KeyError, TypeError, AttributeError, OSError, csv.Error) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
