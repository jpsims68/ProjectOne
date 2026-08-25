#!/usr/bin/env python3
"""
Pilot event-log generator — F1a thin slice.

WHAT THIS IS
A deterministic generator for a fabricated equipment-maintenance event log,
conforming to the 504 event-log data contract. It produces the same bytes every
run from the same seed, so a diff between two runs means something changed in the
generator, not in the randomness.

WHY A GENERATOR AND NOT A DATASET
F1a's schema will change several times while it is being written. A dataset you
can regenerate in seconds matches that; one you found or received does not. The
generator is the durable artifact — the CSV is disposable output.

WHY EQUIPMENT MAINTENANCE
Deliberately chosen to be nobody's target market. The platform is process- and
industry-agnostic, and a pilot dataset quietly becomes the thing everyone reasons
from — a previous sample drifted into SMB wholesale distribution and had to be
explicitly disowned in canon. Healthcare was considered and rejected: the process
shape was excellent, but fabricated admissions and discharges look like PHI to
anyone glancing at the repository, and healthcare is a plausible vertical.

WHAT IT IS *NOT* FOR
Not performance testing — a few thousand events, hand-verifiable. Performance
work needs the real deployment target, and OQ-13 is open.
Not ingestion testing — daily loads, rejected records and reopened cases are F3
concerns, four build units later. This is a ONE-TIME LOAD.

But the schema must not PRECLUDE those, which is why cases are deliberately left
open at the boundary: you can append later and confirm nothing forbade it.

EDGE CASES BUILT IN DELIBERATELY
Each maps to a decision already made. The dataset exists to test canon, not to
fill tables.

  duplicate timestamps within a case  -> forces event_sequence_num to matter (D-62 cascade, AB-CM-021)
  technician changes depot mid-job    -> exercises D-68 as-of SCD-2 resolution
  three depots with sub-areas         -> exercises D-43 closure ancestry
  rework loops and self-transitions   -> exercises variant logic
  cases open at the boundary          -> proves the schema does not forbid reopening
  nulls in optional fields            -> exercises optionality

USAGE
    python3 tools/generate_pilot_log.py --out data/pilot/
"""

import argparse
import csv
import hashlib
import pathlib
import random
from datetime import datetime, timedelta

SEED = 20260824

# --- Hierarchy: three depots, each with sub-areas. Depth exercises D-43. -----
HIERARCHY = {
    "North Depot": ["N-Bay-1", "N-Bay-2", "N-Field"],
    "Central Depot": ["C-Bay-1", "C-Bay-2", "C-Workshop", "C-Field"],
    "South Depot": ["S-Bay-1", "S-Field"],
}

# --- Activities. The happy path plus the loops that make variants interesting.
HAPPY_PATH = [
    "Fault Reported",
    "Triaged",
    "Parts Ordered",
    "Parts Received",
    "Repair Started",
    "Repair Completed",
    "Tested",
    "Returned to Service",
]

# Technicians. Two change depot partway through the window — D-68's as-of rule
# means an event must resolve to the depot valid at from_ts, never the current one.
TECHNICIANS = [
    ("T-101", "North Depot", None),
    ("T-102", "North Depot", None),
    ("T-201", "Central Depot", None),
    ("T-202", "Central Depot", ("2026-03-15", "South Depot")),  # moves mid-window
    ("T-301", "South Depot", None),
    ("T-302", "South Depot", ("2026-04-01", "Central Depot")),  # moves mid-window
]

EQUIPMENT_TYPES = ["Pump", "Compressor", "Conveyor", "Generator", "Valve Assembly"]

WINDOW_START = datetime(2026, 1, 6, 7, 0)
WINDOW_END = datetime(2026, 5, 29, 18, 0)


def tech_depot_at(tech: str, when: datetime) -> str:
    """Depot valid AT THE GIVEN TIME, not the technician's current depot.

    This is D-68 rule 2 made concrete. A lookup that joins on the technician's
    current depot returns the wrong answer for any event before the move, and
    the error is invisible without a case that spans one.
    """
    for tid, home, move in TECHNICIANS:
        if tid != tech:
            continue
        if move:
            move_date, new_depot = move
            if when >= datetime.strptime(move_date, "%Y-%m-%d"):
                return new_depot
        return home
    raise KeyError(tech)


def build_trace(rng: random.Random, case_num: int) -> list[str]:
    """One case's activity sequence. Roughly 60% happy path, the rest with loops."""
    roll = rng.random()

    if roll < 0.60:
        return list(HAPPY_PATH)

    if roll < 0.75:
        # Failed test -> back to repair. The commonest real rework loop.
        trace = list(HAPPY_PATH)
        i = trace.index("Tested")
        return [
            *trace[: i + 1],
            "Repair Started",
            "Repair Completed",
            "Tested",
            "Returned to Service",
        ]

    if roll < 0.85:
        # Wrong part -> re-order. Loop earlier in the process.
        trace = list(HAPPY_PATH)
        i = trace.index("Parts Received")
        return [*trace[: i + 1], *trace[trace.index("Parts Ordered") :]]

    if roll < 0.92:
        # No parts needed — a legitimate shorter variant, not an error.
        return [a for a in HAPPY_PATH if not a.startswith("Parts")]

    if roll < 0.97:
        # Self-transition: triaged twice. Exercises self-loop handling.
        trace = list(HAPPY_PATH)
        i = trace.index("Triaged")
        return [*trace[: i + 1], "Triaged", *trace[i + 1 :]]

    # Escalation branch — a rarer variant so the tail is not empty.
    trace = list(HAPPY_PATH)
    i = trace.index("Triaged")
    return [*trace[: i + 1], "Escalated to Specialist", *trace[i + 1 :]]


def generate(n_cases: int) -> list[dict[str, object]]:
    rng = random.Random(SEED)
    rows: list[dict[str, object]] = []

    depots = list(HIERARCHY)

    for case_num in range(1, n_cases + 1):
        case_id = f"WO-2026-{case_num:05d}"
        depot = rng.choice(depots)
        area = rng.choice(HIERARCHY[depot])
        equipment = f"EQ-{rng.randint(1000, 1999)}"
        equip_type = rng.choice(EQUIPMENT_TYPES)

        # Start uniformly across the window. Cases starting late will still be
        # running at the boundary — deliberately.
        start = WINDOW_START + timedelta(
            minutes=rng.randint(0, int((WINDOW_END - WINDOW_START).total_seconds() // 60))
        )

        trace = build_trace(rng, case_num)
        t = start
        tech = rng.choice([x[0] for x in TECHNICIANS])

        for idx, activity in enumerate(trace):
            # Gaps vary by activity: ordering parts takes days, triage minutes.
            if activity == "Parts Ordered":
                gap = timedelta(hours=rng.randint(18, 96))
            elif activity in ("Repair Started", "Repair Completed"):
                gap = timedelta(hours=rng.randint(1, 12))
            else:
                gap = timedelta(minutes=rng.randint(5, 240))
            t = t + gap

            # DELIBERATE EDGE CASE: every 17th case gets two events sharing a
            # timestamp. Without event_sequence_num their order is undefined,
            # which is exactly what the D-62 cascade exists to resolve.
            if case_num % 17 == 0 and idx == 2:
                t = t - gap

            # Cases still running at the boundary stop here. This is what proves
            # the schema does not forbid a case receiving later events.
            if t > WINDOW_END:
                break

            # DELIBERATE EDGE CASE: some technicians hand over mid-case.
            if idx > 0 and rng.random() < 0.15:
                tech = rng.choice([x[0] for x in TECHNICIANS])

            duration_min = rng.randint(5, 180)

            rows.append(
                {
                    # 504 contract roles
                    "source_event_id": "",  # filled below — deliberately blank for some
                    "case_id": case_id,
                    "activity": activity,
                    "from_ts": t.strftime("%Y-%m-%d %H:%M:%S"),
                    "to_ts": (t + timedelta(minutes=duration_min)).strftime("%Y-%m-%d %H:%M:%S"),
                    "resource": tech,
                    # Attributes
                    "depot": tech_depot_at(tech, t),
                    "area": area,
                    "equipment_id": equipment,
                    "equipment_type": equip_type,
                    # DELIBERATE EDGE CASE: optional field, sometimes null.
                    "cost_amount": "" if rng.random() < 0.20 else f"{rng.uniform(40, 2600):.2f}",
                    "priority": rng.choice(["Low", "Medium", "High", ""]),
                }
            )

    # source_event_id present for most rows, absent for one depot's rows —
    # so BOTH tiers of the D-62 natural-key cascade are exercised in one file.
    for i, r in enumerate(rows, start=1):
        r["source_event_id"] = "" if r["depot"] == "South Depot" else f"EVT-{i:07d}"

    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/pilot", help="output directory")
    ap.add_argument("--cases", type=int, default=400)
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    rows = generate(a.cases)
    cols = list(rows[0])

    log = out / "pilot-equipment-maintenance-events.csv"
    with log.open("w", newline="", encoding="utf-8") as f:
        # LF explicitly. Python's csv module defaults to \r\n, but .gitattributes
        # normalises all text to LF — so a CRLF-writing generator can never reproduce
        # the committed bytes, and the recorded hash would be of something that does
        # not exist in the repository. Caught by the reproducibility check below.
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # Hierarchy, as its own file — closure ancestry (D-43) needs the tree, and a
    # tree inferred from event rows is not the same as a declared one.
    hier = out / "pilot-location-hierarchy.csv"
    with hier.open("w", newline="", encoding="utf-8") as f:
        hw = csv.writer(f, lineterminator="\n")
        hw.writerow(["level_1", "level_2"])
        for depot, areas in HIERARCHY.items():
            for area in areas:
                hw.writerow([depot, area])

    # Technician depot history, as SCD-2 rows. Without this, D-68's as-of rule
    # cannot be tested — there is nothing to resolve against.
    tech = out / "pilot-technician-scd2.csv"
    with tech.open("w", newline="", encoding="utf-8") as f:
        tw = csv.writer(f, lineterminator="\n")
        tw.writerow(["technician_id", "depot", "valid_from", "valid_to"])
        for tid, home, move in TECHNICIANS:
            if move:
                move_date, new_depot = move
                tw.writerow([tid, home, "2026-01-01", move_date])
                tw.writerow([tid, new_depot, move_date, "9999-12-31"])
            else:
                tw.writerow([tid, home, "2026-01-01", "9999-12-31"])

    digest = hashlib.sha256(log.read_bytes()).hexdigest()

    open_cases = {r["case_id"] for r in rows} - {
        r["case_id"] for r in rows if r["activity"] == "Returned to Service"
    }
    dupes = sum(
        1
        for i in range(1, len(rows))
        if rows[i]["case_id"] == rows[i - 1]["case_id"]
        and rows[i]["from_ts"] == rows[i - 1]["from_ts"]
    )

    print("=" * 66)
    print("PILOT EVENT LOG — equipment maintenance, three depots")
    print("=" * 66)
    print(f"  events                 : {len(rows)}")
    print(f"  cases                  : {a.cases}")
    print(f"  distinct activities    : {len({r['activity'] for r in rows})}")
    print(
        f"  cases open at boundary : {len(open_cases)}  (deliberate — proves reopening is not forbidden)"
    )
    print(f"  duplicate timestamps   : {dupes}  (deliberate — forces event_sequence_num to matter)")
    print(
        f"  rows without source_event_id : {sum(1 for r in rows if not r['source_event_id'])}"
        "  (deliberate — exercises BOTH tiers of the D-62 key cascade)"
    )
    print(f"  null cost_amount       : {sum(1 for r in rows if not r['cost_amount'])}")
    print()
    print(f"  {log}")
    print(f"  {hier}")
    print(f"  {tech}")
    print()
    print(f"  sha256(events) = {digest}")
    print("  Deterministic: same seed, same bytes. A diff means the generator changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
