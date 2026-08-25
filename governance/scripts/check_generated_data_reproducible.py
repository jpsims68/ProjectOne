#!/usr/bin/env python3
"""
Governance check — generated data is reproducible.

Every committed dataset produced by a generator MUST be reproducible by running
that generator. This check regenerates into a temporary directory and compares
bytes against what is committed.

WHY THIS EXISTS
The pilot dataset's SHA-256 was recorded in the continuity snapshot as evidence
of determinism. It was the hash of a file that did not exist in the repository.

Python's csv module writes CRLF by default. `.gitattributes` normalises all text
to LF — deliberately, because check_baseline_integrity verifies 87 framework files
by hash and Windows CRLF conversion would break it. So the generator wrote CRLF,
git stored LF, and the recorded hash matched neither the committed file nor
anything a reader could reproduce.

The content was never wrong. The claim about it was. That is the more dangerous
failure: a hash recorded as evidence, which proves nothing, and which nobody would
question because it looks like rigour.

WHAT THIS CHECKS
For each registered dataset: run its generator into a sandbox, compare every
output file byte-for-byte against what is committed, and compare the committed
bytes against the hash recorded in the continuity snapshot.

WHAT IT DOES NOT CHECK
Whether the data is CORRECT or FIT FOR PURPOSE. It proves the committed bytes are
what the generator makes and what the record claims. Nothing more.

Exit 0 = every dataset reproduces. Exit 1 = at least one does not.
"""

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "governance" / "state" / "PAF-Continuity-Snapshot-FrameworkV1.json"

# Registered generated datasets. Add an entry when a generator is committed.
DATASETS = [
    {
        "name": "pilot event log",
        "generator": "tools/generate_pilot_log.py",
        "outputDir": "data/pilot",
        "primary": "pilot-equipment-maintenance-events.csv",
        "snapshotHashPath": ["pilotDataset", "eventsSha256"],
    },
]


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dig(d: dict[str, object], path: list[str]) -> str | None:
    cur: object = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur if isinstance(cur, str) else None


def main() -> int:
    print("=" * 72)
    print("GOVERNANCE CHECK — generated data is reproducible")
    print("=" * 72)

    if not DATASETS:
        # Absent-expected, asserted rather than assumed.
        print("\nSTATE: no generated datasets registered — nothing to reproduce.")
        print("\nRESULT: PASS — nothing to check, and nothing was expected")
        return 0

    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8")) if SNAPSHOT.is_file() else {}
    viol: list[str] = []
    checked = 0

    for ds in DATASETS:
        gen = ROOT / str(ds["generator"])
        out = ROOT / str(ds["outputDir"])

        if not gen.is_file():
            viol.append(f"[MISSING GENERATOR] {ds['name']}: {ds['generator']} not found")
            continue
        if not out.is_dir():
            viol.append(f"[MISSING OUTPUT] {ds['name']}: {ds['outputDir']} not found")
            continue

        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [sys.executable, str(gen), "--out", tmp],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=300,
            )
            if r.returncode != 0:
                viol.append(
                    f"[GENERATOR FAILED] {ds['name']}: exit {r.returncode}\n{r.stderr[:400]}"
                )
                continue

            regenerated = {p.name: p for p in pathlib.Path(tmp).glob("*") if p.is_file()}
            committed = {p.name: p for p in out.glob("*") if p.is_file()}

            only_committed = set(committed) - set(regenerated)
            only_regenerated = set(regenerated) - set(committed)
            if only_committed:
                viol.append(
                    f"[EXTRA COMMITTED] {ds['name']}: {sorted(only_committed)} not produced by the generator"
                )
            if only_regenerated:
                viol.append(
                    f"[NOT COMMITTED] {ds['name']}: generator produces {sorted(only_regenerated)}, absent from the repository"
                )

            for name in sorted(set(committed) & set(regenerated)):
                checked += 1
                c, g = sha256(committed[name]), sha256(regenerated[name])
                if c != g:
                    hint = ""
                    if committed[name].read_bytes().replace(b"\r\n", b"\n") == regenerated[
                        name
                    ].read_bytes().replace(b"\r\n", b"\n"):
                        hint = " — content identical; LINE ENDINGS differ. .gitattributes normalises to LF; make the generator write LF."
                    viol.append(
                        f"[NOT REPRODUCIBLE] {ds['name']}/{name}{hint}\n      committed {c[:24]}  regenerated {g[:24]}"
                    )

            # The recorded hash must describe the committed file, not something else.
            recorded = dig(snapshot, list(ds["snapshotHashPath"]))
            primary = committed.get(str(ds["primary"]))
            if recorded and primary:
                actual = sha256(primary)
                if recorded != actual:
                    viol.append(
                        f"[RECORDED HASH WRONG] {ds['name']}: snapshot records {recorded[:24]}, "
                        f"committed file is {actual[:24]}. A hash recorded as evidence that describes "
                        f"nothing in the repository proves nothing."
                    )

    print(f"\ndatasets registered: {len(DATASETS)}")
    print(f"files compared:      {checked}")

    if viol:
        print(f"\nviolations: {len(viol)}\n")
        for v in viol:
            print(f"  ! {v}")
        print("\nA dataset nobody can regenerate is not evidence of anything.")
        print("\nRESULT: FAIL")
        return 1

    print("\nRESULT: PASS — every committed dataset reproduces from its generator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
