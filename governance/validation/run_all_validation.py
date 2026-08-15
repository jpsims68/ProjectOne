#!/usr/bin/env python3
"""PAF Steps 44/51 — aggregate static validation + full regression re-run after corrections."""
import subprocess, sys, pathlib
ROOT=pathlib.Path(__file__).resolve().parent
CORE=sys.argv[1] if len(sys.argv)>1 else "/home/claude/bootstrap/core"
SUITES=[("Static: framework core (Run 1)",["validate_framework.py"]),
        ("Static: roles/workflows/matrices (Run 2)",["validate_run2.py"]),
        ("Static: testing/registries/gui/ops (Run 3)",["validate_run3.py"]),
        ("Static: profile binding (Run 4)",["validate_run4.py",CORE]),
        ("Static: adapters/assembly (Run 5)",["validate_run5.py"]),
        ("Conformance: contract<->instance",["conformance_probe.py",CORE]),
        ("Executed: regression portfolio (Step 45)",["run_regression.py",CORE]),
        ("Executed: governance dry run (Steps 46-48)",["run_dryrun.py",CORE]),
        ("Executed: retrospective replay (Step 47)",["run_replay.py",CORE])]
print("="*78); print("PAF STEPS 44 / 51 — FULL VALIDATION SWEEP"); print("="*78)
fails=0
for name,cmd in SUITES:
    r=subprocess.run([sys.executable,str(ROOT/cmd[0])]+cmd[1:],capture_output=True,text=True)
    last=[l for l in r.stdout.strip().splitlines() if l.startswith("RESULT")]
    status="PASS" if r.returncode==0 else "FAIL"
    if r.returncode!=0: fails+=1
    print(f"[{status}] {name:<46} {last[-1][8:] if last else ''}")
print("-"*78); print(f"RESULT: {len(SUITES)-fails}/{len(SUITES)} suites passed"); print("="*78)
sys.exit(1 if fails else 0)
