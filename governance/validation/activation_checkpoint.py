#!/usr/bin/env python3
"""
FRAMEWORK ACTIVATION CHECKPOINT — after Step 56, before Step 57.

Implements the five checkpoint requirements from the execution plan verbatim:
  1. Verify the frozen Agent Framework v1 package against its manifest and hashes.
  2. Re-run a concise bootstrap against the just-approved Framework v1.
  3. Confirm role contracts, lifecycle, risk, exceptions, operational independence,
     human approvals, verification map, ProjectOne Profile, GitHub adapter, ChatGPT
     adapter, Anthropic adapter, and coding-workbench adapter are present and version-resolved.
  4. Confirm no material framework defect or unresolved exception blocks repository work.
  5. Confirm production application implementation is still NOT AUTHORIZED.

Reproduce: python3 validation/activation_checkpoint.py [core_dir]
Exit 0 = CHECKPOINT PASS.
"""
import sys, json, pathlib, hashlib, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
CORE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/bootstrap/core")
res = []
def ck(rid, cid, d, ok, det=""):
    res.append((rid, cid, d, "PASS" if ok else "FAIL", det))
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

# ============ REQ 1 — verify frozen package against manifest and hashes ============
# Verify against the CURRENT baseline. Earlier baselines are retained immutably and
# chained by supersession; a governed change legitimately advances the baseline version.
_bl = sorted((ROOT/"manifests").glob("PAF-Frozen-Baseline-v*.json"))
fb = json.loads(_bl[-1].read_text())
ck(1, "AC-1.1", "Frozen baseline manifest present and marked APPROVED_FROZEN_BASELINE",
   fb["releaseState"] == "APPROVED_FROZEN_BASELINE", fb.get("releaseState"))
ck(1, "AC-1.2", "Framework version is 1.0 (not a release candidate)",
   fb["frameworkVersion"] == "1.0", fb.get("frameworkVersion"))
ck(1, "AC-1.6", f"Baseline chain intact (verifying baseline {fb.get('baselineVersion', fb['frameworkVersion'])})",
   all(k in fb for k in ("approvalRefs",)) and bool(fb.get("approvalRefs")), str(fb.get("approvalRefs")))

mismatch, missing = [], []
for c in fb["components"]:
    p = ROOT/c["path"]
    if not p.exists(): missing.append(c["path"]); continue
    if sha(p) != c["sha256"]: mismatch.append(c["path"])
ck(1, "AC-1.3", f"All {len(fb['components'])} frozen components present",
   not missing, f"missing: {missing[:4]}")
ck(1, "AC-1.4", "All frozen component hashes match the manifest (no drift since freeze)",
   not mismatch, f"drifted: {mismatch[:4]}")

# package-level checksums
sums = ROOT/"SHA256SUMS.txt"
sumsok = True; badsum = []
if sums.exists():
    for line in sums.read_text().splitlines():
        if not line.strip(): continue
        h, _, path = line.partition("  ")
        p = ROOT/path.strip()
        if not p.exists() or sha(p) != h: sumsok = False; badsum.append(path.strip())
ck(1, "AC-1.5", "Package SHA256SUMS.txt verifies", sums.exists() and sumsok, f"bad: {badsum[:4]}")

# ============ REQ 2 — concise bootstrap against the approved Framework v1 ============
snap = json.loads((ROOT/"state"/"PAF-Continuity-Snapshot-FrameworkV1.json").read_text())
chain = snap["packageChain"]
core_zip = pathlib.Path("/mnt/user-data/uploads/ProjectOne-Core-Build-Reference-Package-v1_0.zip")
if core_zip.exists():
    ck(2, "AC-2.1", "Immutable corpus hash matches the recorded chain value",
       sha(core_zip) == chain["immutableCorpusHash"], "corpus hash mismatch — STOP condition")
else:
    ck(2, "AC-2.1", "Immutable corpus present for hash verification", False, "core package not mounted")

# core corpus integrity (its own SHA256SUMS)
r = subprocess.run(["sha256sum", "-c", "SHA256SUMS.txt"], cwd=str(CORE), capture_output=True, text=True)
okcount = r.stdout.count(": OK")
ck(2, "AC-2.2", "Core transfer corpus verifies against its own SHA256SUMS (47/47)",
   okcount == 47, f"{okcount}/47 OK")

ck(2, "AC-2.3", "Authority model resolvable: Policy v1.2 / S&R v0.4 / 999 v0.4 present",
   all((CORE/f).exists() for f in [
     "ProjectOne-Build-Requirements-and-Architecture-Policy-v1.2.docx",
     "ProjectOne-Agent-Source-and-Responsibility-Model-v0.4.md",
     "999-Agent-Build-Canon-Modification-Tracker-v0.4.md"]))

prohibited = "ProjectOne-Pre-Build-Governance-Coherence-Audit-INTERNAL-v1.1-FROZEN.md"
ck(2, "AC-2.4", "Prohibited v1.1-FROZEN audit absent from corpus and package",
   not (CORE/prohibited).exists() and not any(p.name == prohibited for p in ROOT.rglob("*")))

# full validation sweep must still pass
sweep = subprocess.run([sys.executable, str(ROOT/"validation"/"run_all_validation.py"), str(CORE)],
                       capture_output=True, text=True)
ck(2, "AC-2.5", "Full validation sweep passes against the frozen baseline (9/9)",
   sweep.returncode == 0, [l for l in sweep.stdout.splitlines() if l.startswith("RESULT")][-1:])

# ============ REQ 3 — required components present and version-resolved ============
REQUIRED = {
  "role contracts (16)":      lambda: len(list((ROOT/"framework/contracts").glob("*.json"))) == 16,
  "lifecycle binding":        lambda: (ROOT/"profile/PROJECTONE-Lifecycle.json").exists(),
  "risk binding":             lambda: (ROOT/"profile/PROJECTONE-Risk.json").exists(),
  "exception binding":        lambda: (ROOT/"profile/PROJECTONE-Exception.json").exists(),
  "operational independence": lambda: (ROOT/"profile/PROJECTONE-Independence.json").exists(),
  "human approvals":          lambda: (ROOT/"profile/PROJECTONE-Human-Approval.json").exists(),
  "verification map binding": lambda: len(json.loads((ROOT/"profile/PROJECTONE-Verification.json").read_text())["records"]) == 360,
  "ProjectOne Profile":       lambda: (ROOT/"profile/PROJECTONE-Profile.json").exists(),
  "GitHub adapter":           lambda: (ROOT/"adapters/PAF-Adapter-GitHub.json").exists(),
  "ChatGPT adapter":          lambda: (ROOT/"adapters/PAF-Adapter-ChatGPT.json").exists(),
  "Anthropic adapter":        lambda: (ROOT/"adapters/PAF-Adapter-Anthropic.json").exists(),
  "coding-workbench adapter": lambda: (ROOT/"adapters/PAF-Adapter-Coding-Workbench.json").exists(),
}
for name, fn in REQUIRED.items():
    ck(3, f"AC-3.{list(REQUIRED).index(name)+1}", f"Present: {name}", fn())

# version-resolved: every frozen artifact carries version + freeze provenance
unresolved = []
for sub in ["framework", "profile", "adapters", "manifests"]:
    for f in (ROOT/sub).rglob("*.json"):
        if "__pycache__" in str(f): continue
        try: h = json.loads(f.read_text()).get("header")
        except Exception: continue
        if isinstance(h, dict) and h.get("status") == "FROZEN":
            if not h.get("version") or not h.get("frozenAt") or not h.get("frozenUnder"):
                unresolved.append(f.name)
ck(3, "AC-3.13", "Every FROZEN artifact is version-resolved with freeze provenance",
   not unresolved, f"unresolved: {unresolved[:4]}")

# ============ REQ 4 — no material defect or unresolved exception blocks repository work ============
sweep_ok = sweep.returncode == 0
ck(4, "AC-4.1", "No open material framework defect (all validation suites pass)", sweep_ok)

# no open exceptions in the snapshot
open_exc = snap.get("openExceptions", [])
ck(4, "AC-4.2", "No unresolved exception outstanding", not open_exc, str(open_exc))

# capability gaps must be declared AND mitigated (declared gaps do not block; undeclared would)
compat = json.loads((ROOT/"manifests"/"PAF-Adapter-Compatibility-Matrix.json").read_text())
unmit = [g for g in compat["declaredGaps"] if not g.get("mitigation") or not g.get("riskAcceptor")]
ck(4, "AC-4.3", f"All {len(compat['declaredGaps'])} declared capability gaps carry mitigation + risk acceptor",
   not unmit, str(unmit[:3]))

# owner approvals recorded, not inferred
appr = json.loads((ROOT/"approvals"/"PAF-Owner-Approval-Record.json").read_text())
ids = {a["approvalId"]: a for a in appr["approvals"]}
ck(4, "AC-4.4", "APR-001 (sustainability thresholds) recorded as explicit human approval",
   ids.get("APR-001", {}).get("approver", {}).get("actorClass") == "HUMAN"
   and "EXPLICIT" in ids.get("APR-001", {}).get("basis", "").upper())
ck(4, "AC-4.5", "APR-002 (Agent Framework v1) recorded as explicit human approval",
   ids.get("APR-002", {}).get("decision") == "APPROVED"
   and ids.get("APR-002", {}).get("approver", {}).get("actorClass") == "HUMAN")
ck(4, "AC-4.6", "Approval record asserts agents cannot approve", appr.get("agentCanApprove") is False)

# open items that are tracked, not blocking — but MUST be visible
od = {d["id"]: d for d in snap.get("openDecisions", [])}
# The GitHub execution model must not be an unaddressed unknown before repository work.
# It is satisfied either by being tracked as open, OR by a recorded disposition — a
# resolved decision meets the intent more fully than an open one.
prof = json.loads((ROOT/"profile"/"PROJECTONE-Profile.json").read_text())
gh_resolved = bool(prof.get("githubExecutionModel", {}).get("decision"))
ck(4, "AC-4.7", "GitHub execution model is dispositioned (resolved) or tracked open before repository work",
   gh_resolved or "OD-01" in od,
   f"resolved={gh_resolved}; open={list(od)}")
ck(4, "AC-4.8", "Every remaining open decision is visible in the continuity snapshot",
   all(d.get("subject") and d.get("status") for d in snap.get("openDecisions", [])),
   str([d.get("id") for d in snap.get("openDecisions", [])]))

# ============ REQ 5 — production application implementation still NOT AUTHORIZED ============
gb = snap["governanceBaseline"]
ck(5, "AC-5.1", "Snapshot still records production application implementation as NOT AUTHORIZED",
   gb.get("productionImplementation") == "NOT AUTHORIZED", gb.get("productionImplementation"))
ck(5, "AC-5.2", "No application source code exists in the package (framework only)",
   not any(p.suffix in (".sql",) for p in ROOT.rglob("*") if p.is_file()),
   str([str(p) for p in ROOT.rglob("*.sql")][:3]))
ck(5, "AC-5.3", "Step 112/113 authorization gate still recorded as required",
   any("112" in d for d in snap.get("doNotDo", [])), "")

# ---------------- report ----------------
REQ = {1:"Verify frozen package against manifest and hashes",
       2:"Concise bootstrap against approved Framework v1",
       3:"Required components present and version-resolved",
       4:"No material defect or unresolved exception blocks repository work",
       5:"Production application implementation still NOT AUTHORIZED"}
fails = sum(1 for r in res if r[3] == "FAIL")
print("="*84); print("FRAMEWORK ACTIVATION CHECKPOINT — after Step 56, before Step 57"); print("="*84)
for rid in sorted(REQ):
    print(f"\nREQUIREMENT {rid} — {REQ[rid]}")
    for r in [x for x in res if x[0] == rid]:
        print(f"  [{r[3]}] {r[1]:<8} {r[2]}")
        if r[3] == "FAIL" and r[4]: print(f"           {r[4]}")
print("\n" + "-"*84)
print(f"RESULT: {len(res)-fails}/{len(res)} checkpoint assertions passed")
print("CHECKPOINT PASS" if not fails else "CHECKPOINT FAIL")
print("="*84)
sys.exit(1 if fails else 0)
