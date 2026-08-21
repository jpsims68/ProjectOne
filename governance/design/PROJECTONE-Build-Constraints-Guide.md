# ProjectOne Build Constraints Guide

**Status:** ACTIVE
**Audience:** anyone writing ProjectOne code — DDL, backend, frontend
**Authority:** derived. The DDR (201) and the ProjectOne Profile are canonical. Where this guide and a canonical source disagree, the canonical source wins and this guide is the defect.
**Created:** 2026-08-19

---

## What this document is

Six architectural constraints govern how ProjectOne is built. Each was decided deliberately, each is recorded in a change package, and each is easy to violate by accident — because in every case the wrong approach *works locally* and fails later, at a point far from the decision that caused it.

That is the whole reason this guide exists. These aren't style preferences. They are constraints where the feedback signal arrives too late to be useful, so the rule has to arrive early instead.

This guide is **developer-facing**. Client installation and onboarding are a separate concern, handled in the 502 Onboarding Playbook. If you're setting up a client, you want that document, not this one.

### How to read a constraint

Each section states the rule, the reason it exists, and — most importantly — **the testable line**: the specific question you can ask of a design or a diff to know whether it complies. If a constraint has no testable line, it isn't enforceable and you should say so.

### Reading order if you're new

Start with §1 if you're writing SQL or backend code, §5 if you're writing frontend. §2 and §3 affect everyone. §4 and §6 are narrower but catch specific mistakes people reliably make.

---

## 1. Mining computation runs in SQL

**Constraint:** `AC-MINING-PLACEMENT` (Profile v1.5, from CP-002)
**Satisfies:** FR-003

### The rule

All process-mining computation over event data executes **set-based, in SQL, where the data already lives.**

**Narrow exception:** numpy is permitted *only* on results already reduced to a small set — typically percentile or quantile work over pre-aggregated arrays, or an iterative algorithm SQL expresses badly. A numpy step receiving raw event rows is in the wrong place by definition.

**Prohibited:**

- Row-wise Python iteration over event data
- Extracting an event log from the database to compute over it in the application tier
- Mining executed inside a request/response cycle
- Client-side computation over raw event data — the client renders results, it does not compute them

**Execution timing:** mining runs as a scheduled or background job that materializes results the API reads. Never in-request.

### The testable line

> **If a computation step receives raw event rows outside SQL, it is misplaced.**

This is checkable in review and in code structure, not only by measurement. You do not need a profiler to apply it — you need to look at what a function receives as its argument.

### Why

**Data movement dominates.** The expensive part is not the arithmetic, it's the moving. Extraction bills the database to read and serialize, bills the app tier for compute and memory, and adds transfer latency on top. Computing in place avoids all three. Columnstore batch-mode execution suits this workload well: a directly-follows graph is a group-by.

**Cost.** Serverless bills by vCore-second and pauses when idle. SQL-side work is billed once and the database sleeps afterward. Extract-and-compute pays the database for the extract *and* keeps the app tier sized for peak — paying twice for the same computation.

**The language constraint.** Python cannot parallelize CPU-bound work across threads because of the GIL. This matters more than it first appears: a design that puts mining in-request **cannot be repaired by adding capacity.** It requires restructuring. That's why this is recorded as a design constraint satisfied by construction, not as a performance target to be tuned toward later.

**Client-side.** Mining in the browser would require shipping event data to the client — slow at scale, and a tenant-isolation exposure, because data leaves the server to be processed. Cytoscape.js renders results client-side, which is correct. It must not compute them.

### Related

D-50 (stored successor pairs), D-66 (native analytics, no PM4Py), D-21 (Azure SQL serverless posture), CR-3/CR-4 (non-additivity tiering).

D-66 removes most iterative-algorithm cases: most-frequent-variant, the primary reference-model bootstrap, is a SQL group-by. The numpy exception would only widen if the documented inductive-miner alternative were ever adopted.

---

## 2. The OQ-13 design tax: no MI-only capabilities

**Source:** CP-004
**Satisfies:** FR-002
**Enforced by:** `governance/scripts/check_cloud_target_compatibility.py` (FR-010), a required status check

### The rule

The deployment target is **not yet decided.** OQ-13 remains open between **Azure SQL Database** and **Azure SQL Managed Instance**. Until it closes, nothing may depend on a capability that exists only in Managed Instance.

In practice this means coding to the **Azure SQL Database floor**, because it is the more restrictive of the two. Anything that runs there runs on Managed Instance as well.

**Prohibited while OQ-13 is open:**

| Capability | Why it's out |
|---|---|
| SQL Server Agent scheduling | Absent from Azure SQL Database; use an external scheduler |
| Cross-database queries | Three- and four-part names to other databases don't resolve |
| Linked servers | `sp_addlinkedserver`, `OPENQUERY`, `OPENDATASOURCE` unsupported |
| CLR | `CREATE ASSEMBLY`, `EXTERNAL NAME` unsupported |
| Database Mail | `sp_send_dbmail` unsupported |
| FILESTREAM / FILETABLE | File placement is service-managed |
| Instance-level configuration | `sp_configure`, `RECONFIGURE`, trace flags unsupported |

The enforcement check covers more than this list — the `USE` statement, backup and restore syntax, Service Broker, server-scoped objects, Windows authentication, distributed transactions, and others. Read the check for the current full set; it is the operative list.

**One important nuance:** three-part names are *not* uniformly prohibited. Microsoft supports names referencing the **current database** and **tempdb**. `mvp.mining.EventLog` is fine. `Reporting.dbo.FactEvents` is not.

### The consequence of using one

**Using an MI-only capability silently closes an intentionally open decision.** Nobody decides to eliminate Azure SQL Database as an option; it simply becomes impossible, discovered months later when someone tries to deploy. The decision gets made by accident, by whoever wrote the first job step.

### Why this needs enforcement rather than discipline

The development machine is **SQL Server 2022 Developer Edition** — the complete Enterprise feature set. It will happily run SQL Agent jobs, cross-database queries, linked servers, and CLR. Every one of these works perfectly in local testing.

So local success is **not evidence of deployability**, and the natural feedback loop is inverted: the thing that will break in production is the thing that behaves flawlessly on your machine. That's why FR-010 exists as a machine check rather than a line in a document. This section explains it; the check enforces it.

### If OQ-13 resolves

The constraint relaxes only if Managed Instance is chosen, and only by an explicit governed change. If a non-Azure provider were ever selected, D-21 and D-26 would need amending first, and the check would be **revised, not deleted.**

---

## 3. Microsoft Fabric: excluded as a target, supported as a source

**Source:** CP-004 / NOTE-FABRIC-AS-SOURCE
**Satisfies:** FR-001

Both halves of this position must travel together. Recording only the first leads a future reader to decline a legitimate client integration.

### (a) Fabric is EXCLUDED as a deployment target

Fabric Warehouse **cannot enforce uniqueness constraints**, and therefore cannot satisfy LOCKED decision **D-62**. This is not a preference or a maturity judgment. It is a capability the design requires and the platform does not provide.

### (b) Fabric is NOT excluded as a data source

A client lakehouse is a **legitimate connector target** behind the event log data contract (504). Mid-market and enterprise clients increasingly land their data in Fabric. Declining that integration would forgo a commercial advantage that costs nothing architecturally.

The data contract is the boundary. Source technology sits outside it. A Fabric lakehouse is one more source shape alongside CSV, database extract, and API.

### The testable line

> Search this guide for "Fabric". You must find **both** the deployment-target exclusion **and** the source-side support statement. Either one alone is a defect.

The client-facing half of this position is carried by **OV-001** in `governance/overlays/PROJECTONE-999-Overlay-Register.json`, which governs how source-system options are presented during onboarding.

---

## 4. No migration framework

**Source:** CP-005
**Satisfies:** FR-007

### The rule

**No migration framework is used.** Not Alembic, not Flyway, not Liquibase, not an ORM's built-in migration facility.

Schema is defined by **numbered, forward-only SQL scripts** under the db-build-sop.

### Why — and the reasoning matters more than the rule

Migration frameworks are good tools. They are excluded for a specific reason, not because they're bad.

**They optimize for frictionless schema churn.** That's their central value proposition: change the schema easily and often, let the tool reconcile the difference. That directly opposes **DDR P-8**, the no-migration principle — the design must accommodate every known future requirement from the start, so that no migration is ever needed.

A tool that makes migrations easy makes deferring design easy. The friction P-8 relies on is the point.

**Why the reasoning has to be recorded and not just the rule:** a future contributor encountering a schema with no migration framework will read it as an oversight, and helpfully add one. The absence looks like a gap unless the reasoning travels with it. It is a deliberate exclusion.

### The testable line

> A schema change that requires transforming existing data is a **design failure**, not a migration task. It signals that a known requirement was not designed for. Escalate it as a design defect rather than reaching for a tool to smooth it over.

---

## 5. DOM ownership: one owner per container

**Constraint:** `AC-DOM-OWNERSHIP` (Profile v1.5, from CP-003)
**Satisfies:** FR-004

### The governing rule

> **ONE OWNER PER CONTAINER, decided upfront, never mixed.**

### The core tension

React maintains a virtual tree and reconciles it. D3 and Cytoscape mutate elements directly. When both own the same nodes, you get flicker, lost updates, and defects that appear **only on re-render** — which is to say, late, intermittently, and far from the code that caused them.

The defect source is **mixed ownership**, not the framework choice. Either library is fine. Sharing is not.

### Pattern A — D3 for math, React for rendering

**Role: primary by volume.** This is what most components use.

D3 scales, shapes, layouts, and interpolators are used as **pure functions** returning numbers and path strings. React renders the SVG. **D3 never touches the DOM.**

```jsx
const x = d3.scaleLinear().domain([0, max]).range([0, width]);
const path = d3.line().x(d => x(d.t)).y(d => y(d.v))(data);
return <path d={path} stroke="var(--chart-line)" />;
```

Applies to: the custom chart library — the majority of components built.

This pattern is also what makes several chart ground rules achievable: deterministic output (same input, identical pixels), no magic numbers in the render layer, and sizing to container rather than viewport.

### Pattern B — hand the library a container and stay out

**Role: the correct answer for a known set of components. Explicitly NOT a fallback for Pattern A.**

React renders an empty container with a ref. The library owns everything inside it. **React never re-renders that subtree.**

Applies to:

- **Cytoscape.js process maps.** Cytoscape owns its container by design; there is no alternative. React mounts it and passes data. Note: `react-cytoscapejs` is a thin convenience wrapper, **not load-bearing**. If you hit its limits, mounting Cytoscape directly in a `useEffect` is a small amount of code. Do not architect around the wrapper.
- **The animation engine (D-28).** D-28 decouples animation from Cytoscape and names D3+GSAP as a candidate direction. Animation and transition machinery is precisely where D3 *should* drive the DOM directly.

### The testable line

> **Pattern B is not a fallback for Pattern A.** Both are permanent, and they apply to different components. If you find yourself reaching for Pattern B because Pattern A got awkward, that is a signal to re-examine the component, not to switch patterns.

For any container, you should be able to answer in one sentence: *who owns the DOM inside this element?* If the answer is "both" or "it depends," stop.

---

## 6. Python free-threaded mode is not relied upon

**Source:** CP-005
**Satisfies:** FR-008

### The rule

Python 3.13's experimental **free-threaded (GIL-free) build mode is out of scope.** ProjectOne does not use it and does not plan around it.

### Why this needs saying

Free-threaded mode looks like a direct answer to the GIL tradeoff recorded in CP-002 and restated in §1 above. Someone reading that constraint will reasonably think: *the GIL is the problem, and Python 3.13 has a build that removes the GIL — why not use it?*

Because that would **substitute an experimental runtime feature for a sound architectural constraint.** The mechanism that removes the need for free-threaded mode is **`AC-MINING-PLACEMENT`** (§1). If mining runs set-based in SQL, there is no CPU-bound Python work to parallelize, and the GIL stops being relevant. The problem is solved by placement, not by runtime.

Relying on an experimental build would also make the deployment story depend on a feature whose stability and ecosystem support are still moving.

### The testable line

> If a design argument depends on free-threaded mode being available, the design is wrong. Check whether §1 has been violated upstream — the need for thread-level CPU parallelism in Python is itself the symptom.

---

## Constraint index

| § | Constraint | Source | FR | Enforced by |
|---|---|---|---|---|
| 1 | Mining computation in SQL | AC-MINING-PLACEMENT / CP-002 | FR-003 | review; testable line |
| 2 | No MI-only capabilities | CP-004 | FR-002 | **required CI check** (FR-010) |
| 3 | Fabric: target excluded, source supported | CP-004 | FR-001 | review |
| 4 | No migration framework | CP-005 | FR-007 | review; registry |
| 5 | One DOM owner per container | AC-DOM-OWNERSHIP / CP-003 | FR-004 | review; testable line |
| 6 | No free-threaded Python | CP-005 | FR-008 | review |

Only §2 is machine-enforced today. The rest depend on review, which is why each carries a testable line rather than a general principle.

---

## Two standing rules that apply to all of the above

**The technology registry is allowlist-based.** Any tool not listed ACTIVE in `PROJECTONE-Technology-Registry.json` is **DENIED by default.** Unlisted does not mean unconsidered — it means not approved. Adding an entry is a governed change.

**Immutable sources must be read with their overlays.** The 500-series documents (502 Playbook, 504 Data Contract) are uploaded sources that are never edited in place. Every change to their content lives in `governance/overlays/PROJECTONE-999-Overlay-Register.json`. Reading one of those sources without its ACTIVE overlays gives you a stale answer.

**Deferring functionality is fine. Deferring design is not.** Under DDR P-8, the design must accommodate known future requirements from the start, even where the functionality is not built yet. A feature can sit below the cut line; the design that feature will need cannot. This is the principle §4 protects.

---

## Before marking this guide complete

Check `PROJECTONE-Forward-Requirements.json`. That register is a **completion precondition, not a suggestion** — it records obligations placed on documents that did not exist when the decision was made. This guide satisfies FR-001, FR-002, FR-003, FR-004, FR-007, and FR-008. FR-005 and FR-006 target the 502 Playbook and the 504 Data Contract. FR-009 (observability tooling) and FR-010 (the compatibility check) are not document requirements.
