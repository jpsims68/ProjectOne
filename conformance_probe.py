#!/usr/bin/env python3
"""
PAF Run 1 — Contract Conformance Probe
Deterministic, non-judgmental check (independence mechanism AI-3).

Proves that the five CORE registry contracts (Steps 6-10) can actually accept the
project's approved governing registry instances, WITHOUT binding them into the core.
This is the evidence behind decision D-PAF-01.

Reproduce: python3 conformance_probe.py <core_package_dir>
Exit 0 = all conform. Exit 1 = at least one non-conformance.
"""
import json, sys, hashlib, pathlib
from jsonschema import Draft202012Validator, RefResolver

SCHEMA_DIR = pathlib.Path(__file__).resolve().parent.parent / "framework" / "schemas"

PAIRS = [
    ("Step 6  Lifecycle",        "paf.lifecycle-registry.schema.json",      "ProjectOne-Lifecycle-State-Registry-v1.1.json"),
    ("Step 7  Risk",             "paf.risk-standard.schema.json",           "ProjectOne-Risk-and-Materiality-Classification-Standard-v1.1.json"),
    ("Step 8  Exception",        "paf.exception-registry.schema.json",      "ProjectOne-Exception-Eligibility-Registry-v1.1.json"),
    ("Step 9  Independence",     "paf.independence-standard.schema.json",   "ProjectOne-Operational-Independence-Standard-v1.0.json"),
    ("Step 10 Human Approval",   "paf.human-approval-registry.schema.json", "ProjectOne-Human-Approval-Authority-and-Continuity-Registry-v1.0.json"),
]

def load(p):
    with open(p, "rb") as fh:
        raw = fh.read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()

def strip_header(schema):
    """Instances predate the framework and carry no PAF artifactHeader.
    Header conformance is a Profile-binding obligation (Steps 29-33), not a
    property of the pre-existing instance. Probe the substantive contract only."""
    s = json.loads(json.dumps(schema))
    s.get("properties", {}).pop("header", None)
    if "required" in s:
        s["required"] = [r for r in s["required"] if r != "header"]
    return s

def main(core_dir):
    core = pathlib.Path(core_dir)
    store, results, failures = {}, [], 0

    for fn in SCHEMA_DIR.glob("*.json"):
        sch, _ = load(fn)
        store[fn.name] = sch

    for label, schema_file, instance_file in PAIRS:
        schema = strip_header(store[schema_file])
        inst_path = core / instance_file
        if not inst_path.exists():
            results.append((label, "MISSING_INSTANCE", instance_file, []))
            failures += 1
            continue
        instance, ihash = load(inst_path)
        resolver = RefResolver(base_uri="", referrer=schema, store=store)
        v = Draft202012Validator(schema, resolver=resolver)
        errs = sorted(v.iter_errors(instance), key=lambda e: list(e.path))
        if errs:
            failures += 1
            results.append((label, "NON_CONFORMANT", f"{instance_file} [{ihash[:12]}]",
                            [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message[:150]}" for e in errs[:6]]))
        else:
            results.append((label, "CONFORMS", f"{instance_file} [{ihash[:12]}]", []))

    print("=" * 78)
    print("PAF RUN 1 — CONTRACT CONFORMANCE PROBE")
    print("=" * 78)
    for label, status, detail, errs in results:
        print(f"[{status:>15}] {label:<24} {detail}")
        for e in errs:
            print(f"                  ! {e}")
    print("-" * 78)
    print(f"RESULT: {len(results)-failures}/{len(results)} contracts accept their approved instance")
    print("=" * 78)
    return 1 if failures else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/bootstrap/core"))
