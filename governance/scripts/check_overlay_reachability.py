#!/usr/bin/env python3
"""
Governance check — overlay reachability.

Every approved overlay MUST be reachable from the source it modifies.

WHY THIS EXISTS
The source registry states the rule plainly: "Effective source = immutable source
+ all applicable approved overlay entries. Reading the base source alone is an
incomplete read." The registry also provides an `overlayRefs` field on every
source for exactly that purpose.

For weeks, every one of those fields was empty.

The consequence was not theoretical. Three approved decisions — D-67, D-68, and
the event-order field name `event_sequence_num` — existed only as overlays and
appeared nowhere in the DDR. Anyone reading the DDR alone would have used the
wrong column name in the first DDL written. Nobody noticed until the owner asked
whether prior proposals had been evaluated.

The failure mode is specific and worth naming: an agent reads the document it is
pointed at and treats it as complete. It does not chase a cross-reference it does
not know exists. So the pointer has to live where the reader already is.

WHAT THIS CHECKS
  1. Every approved overlay names a target that resolves to a registered source
  2. Every such source carries an overlayRefs entry for that overlay
  3. Every source with overlays carries a readRule warning the reader

WHAT IT DOES NOT CHECK
Whether the overlay's CONTENT has been correctly applied or understood. That is
not mechanically checkable. This proves the pointer exists, not that anyone
followed it.

Exit 0 = every approved overlay is reachable. Exit 1 = at least one is orphaned.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "governance" / "profile" / "PROJECTONE-Source-Registry.json"
OVERLAYS = ROOT / "governance" / "overlays" / "PROJECTONE-999-Overlay-Register.json"

APPROVED_PREFIXES = ("APPROVED", "ACTIVE", "VERIFIED")


def main() -> int:
    print("=" * 72)
    print("GOVERNANCE CHECK — overlay reachability")
    print("=" * 72)

    for f in (REGISTRY, OVERLAYS):
        if not f.is_file():
            # Absent-unexpected. Both artifacts are required; a missing one is a
            # failure, never a reason to pass.
            print(f"\n::error:: required artifact missing: {f.relative_to(ROOT)}")
            print("\nRESULT: FAIL")
            return 1

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ovl = json.loads(OVERLAYS.read_text(encoding="utf-8"))

    by_id = {s["sourceId"]: s for s in reg["sources"]}
    viol: list[str] = []
    checked = 0
    pending = 0

    for o in ovl["overlays"]:
        status = str(o.get("status", ""))
        oid = o["overlayId"]
        target = str(o.get("targetSource", "")).strip("` ")

        if not status.startswith(APPROVED_PREFIXES):
            pending += 1
            continue

        checked += 1
        m = re.match(r"(\d{3})", target)
        sid = m.group(1) if m else target
        src = by_id.get(sid)

        if src is None:
            viol.append(
                f"[ORPHAN] {oid} targets '{target}', which is not a registered source. "
                f"Nothing can resolve it to a file."
            )
            continue

        refs = {r.get("overlayId") for r in src.get("overlayRefs", [])}
        if oid not in refs:
            viol.append(
                f"[UNREACHABLE] {oid} modifies source {sid} but is not listed in that "
                f"source's overlayRefs. A reader of {sid} would never learn it exists."
            )

    for sid, src in by_id.items():
        if src.get("overlayRefs") and not src.get("readRule"):
            viol.append(
                f"[NO WARNING] source {sid} has {len(src['overlayRefs'])} overlay(s) but "
                f"no readRule. The reader is not told the base file is incomplete."
            )

    print(f"\napproved overlays checked: {checked}")
    print(f"pending overlays skipped:  {pending}")
    print(f"sources carrying overlays: {sum(1 for s in by_id.values() if s.get('overlayRefs'))}")

    if checked == 0:
        # Absent-expected, asserted rather than assumed.
        print("\nSTATE: no approved overlays exist yet — nothing to make reachable.")
        print("\nRESULT: PASS — nothing to check, and nothing was expected")
        return 0

    if viol:
        print(f"\nviolations: {len(viol)}\n")
        for v in viol:
            print(f"  ! {v}")
        print("\nAn approved decision that its own target never mentions is invisible.")
        print("That is how a column name goes wrong in the first schema written.")
        print("\nRESULT: FAIL")
        return 1

    print("\nRESULT: PASS — every approved overlay is reachable from its target")
    return 0


if __name__ == "__main__":
    sys.exit(main())
