# ProjectOne Build Constraints Guide

**Status:** ACTIVE
**Audience:** anyone writing ProjectOne code — DDL, backend, frontend
**Authority:** derived. The DDR (201) and the ProjectOne Profile are canonical. Where this guide and a canonical source disagree, the canonical source wins and this guide is the defect.
**Created:** 2026-08-20

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

## 7. Decisions that live ONLY as overlays

**Source:** AB-CM-011, AB-CM-021, AB-CM-022 in `governance/overlays/PROJECTONE-999-Overlay-Register.json`
**Satisfies:** CF-005

### Read this before you open the DDR

Three approved decisions **do not appear anywhere in the DDR file.** Searching `201-ProjectOne-Design-Decision-Record.md` for any of them returns **zero** results:

- **D-67** — Data-Driven Theming Architecture
- **D-68** — Event business-unit assignment precedence
- **`event_sequence_num`** — the canonical D-47 event-order field name

They were approved by the owner on 5–8 August 2026 and recorded as overlays against an immutable source, which is the correct mechanism. But it means the DDR read alone is **incomplete on two decisions and actively wrong on one field name.**

Two further things the DDR gets wrong about itself, both settled by AB-CM-029 and AB-CM-030:

- Its header reads **v1.35**. The current authoritative version is **v1.37** — the header is stale, the file is not older.
- Its stated range is D-01…D-66. The effective range is **D-01…D-68**.

### 7a. The event-order field is `event_sequence_num`

**Not `sequence_num`.** Wherever D-47 says `sequence_num` for the canonical event ordering and tie-break field, read `event_sequence_num`.

The total sort is:

```
(from_ts, event_sequence_num, event_key)
```

D-62 controls the field name and the source/synthesis cascade. D-47 continues to control deterministic ordering semantics.

**Why this one matters most.** It is a column name in the first table anyone writes. Get it wrong and it propagates into DDL, the field catalog, APIs, mappings, fixtures and tests before anyone notices — and renaming a key ordering column after data exists is exactly the migration DDR P-8 exists to prevent.

> **The testable line:** if you find `sequence_num` unqualified in any DDL, mapping, fixture or test, it is wrong.

### 7b. Business-unit assignment precedence (D-68)

Determines how `event.business_unit_key` is populated. Four rules, in order:

1. **Direct wins when valid.** If the event-log mapping supplies a business-unit value resolving to a valid `business_unit_dim` member for the tenant, that value is authoritative and becomes the effective `event.business_unit_key`.
2. **Resource is the deterministic fallback.** With no valid direct value, derive from the resolved `resource_dim.business_unit_key` using the **SCD-2 version valid at `event.from_ts`**. Never the resource's *current* business unit for a historical event.
3. **Provenance is mandatory.** Record `business_unit_assignment_source` as `direct_event`, `resource_asof`, or `none`.
4. **Disagreement is a finding, not an overwrite.** When a valid direct value and a resource-derived value both exist and differ: keep the direct value as effective, set `business_unit_conflict_flag = true`, and emit a data-quality finding. Do not silently overwrite either meaning.

Rules 2 and 4 are the ones that get implemented wrongly by default. As-of resolution is more work than a current-value join, and silently preferring one source is easier than surfacing a conflict — which is precisely why both are written down.

> **The testable line:** if a business-unit lookup joins on the resource's current row rather than the row valid at `event.from_ts`, it is wrong. If a conflict resolves without setting a flag and emitting a finding, it is wrong.

### 7c. Data-driven theming (D-67)

Theme definitions are stored in a platform-agnostic versioned format such as JSON, validated against a schema, resolved through primitive, semantic, component, state and visualization tokens, and mapped to CSS Custom Properties for the web client.

The canonical flow:

```
theme data → schema validation → token resolution → Theming/Skinning Engine
           → platform adapter → CSS Custom Properties
```

**Feature slices consume approved semantic or component tokens and approved themed shared controls.** They do not create private theme systems, do not hard-code replacement appearance values where approved tokens exist, and do not place feature business logic in the theme layer.

Runtime skinning must support approved tenant, product, environment, branding, density and accessibility skins **without feature-code changes.**

This interacts directly with §5. Pattern A — D3 as pure math, React rendering — is what makes token-driven theming possible, because the render layer reads CSS Custom Properties rather than computing colours. A component that hard-codes a colour breaks both constraints at once.

> **The testable line:** if changing a theme requires touching feature code, the theming layer has been bypassed.

### Why this section exists as its own section

These three could have been filed under the constraints above — the field name under a data section, theming beside DOM ownership. They are deliberately kept together because **the most important fact about them is the category they belong to**: approved decisions that a reader consulting the primary source will not find.

If a fourth appears, it belongs here too.

---

## 8. Code structure and computation placement

**Source:** D-69 (AB-CM-036) · AC-MINING-PLACEMENT · CP-002
**Status of D-69:** APPROVED 2026-08-24 (D69-A) — effective. AC-MINING-PLACEMENT is LOCKED and in force.

### Where computation goes — two questions

For any computation **over event data**, in order:

**Question 1 — does the input grow with tenant data volume?**

| Answer | Placement |
|---|---|
| **Yes** | **SQL, set-based. No exception**, whatever the operation |
| **No** | Python permitted — go to Question 2 |

"Every event" grows. "One row per activity" does not — a process has a bounded activity count whether the tenant loads ten thousand events or ten million.

Answerable by reading a function signature. No profiler, no benchmark, no production data — which matters, because none exists yet.

**Question 2 — can SQL express the operation?**

| Answer | Placement |
|---|---|
| **Yes** | **Use SQL anyway.** SQL is the default, not the fallback |
| **No** | Python |

SQL is inadequate for these — **illustrative of the objective, not a definition of it**. The objective is: *SQL unless SQL genuinely cannot do the work.*

1. Unbounded-depth recursion through cyclic structures
2. Iterative convergence, where termination depends on a criterion rather than on data
3. Sequence alignment and edit-distance
4. Linear algebra and matrix operations
5. Combinatorial search and optimization

**What SQL handles well — reaching for Python here is the common error.** Directly-follows pairs (`LAG` within case partition) · variant identification (`STRING_AGG` then group) · percentiles (`PERCENTILE_CONT`) · running totals, rank, gap-and-island, sessionization (window functions) · conformance rule evaluation · wait-time aggregation. Native regex is GA in Azure SQL Database; pattern matching alone does not justify moving work to Python.

### One local-versus-Azure trap

`REGEXP_LIKE`, `REGEXP_MATCHES` and `REGEXP_SPLIT_TO_TABLE` require **database compatibility level 170+**, which is SQL Server 2025. The local development instance is **SQL Server 2022 — maximum level 160**.

So these functions **work on Azure SQL Database and fail on the local machine.**

That is the *inverse* of the §2 problem. There, Developer Edition runs everything happily and the failure surfaces at deployment. Here the failure surfaces on the first local run, in seconds, with a clear error. Loud and immediate, which is why it is accepted rather than guarded by a check.

If you need one of these constructs, that is a **decision** — raise it — not a workaround to code around.

> **The general form, which outlasts regex:** Azure SQL Database tracks ahead of the boxed product. Any capability newer than SQL Server 2022 may exist in the target and not locally. The durable answer is CI running against a real Azure SQL Database, so both directions are caught by execution rather than by pattern-matching. Recorded as CF-006; it belongs with the OQ-13 and FR-009 cluster.

### The dangerous quadrant

|  | Input bounded | Input grows with data |
|---|---|---|
| **SQL can do it** | Either — prefer SQL | **SQL, mandatory** |
| **SQL cannot** | **Python — legitimate** | ⚠ **Reduce first, then escalate** |

Bottom-right is where real decisions live. Sequence alignment across all traces is SQL-inadequate *and* data-volume-bound. The answer is never "therefore Python" — it is reduce in SQL to the bounded variant set, then align over that.

> **The testable line:** if a computation step receives raw event rows outside SQL, it is misplaced. If you cannot answer Question 1 from the function signature alone, the signature is wrong.

### Timing is a separate requirement

Mining runs as a **scheduled or background job that materializes results the API reads**. Correct SQL inside a request handler still violates the constraint. Both rules must hold.

### Runtime backstop

Every Python analytical entry point **asserts its input size against a declared row budget and fails loudly** when exceeded. Catches a cardinality assumed bounded that turns out not to be.

An assertion in code, not a design-time threshold. Design-time thresholds are untestable before data exists and invite argument afterwards.

### When the rule does not clearly decide

Raise a **`DECISION_REQUIRED`** escalation. Do not choose. Every escalation is evidence the rule needs tightening, and is more useful recorded than resolved silently.

---

### Operational rules for application code

These govern the application tier. The analytical tier is carved out above.

**Fail fast at boundaries.** Validate inputs where they enter a module. A value that has crossed a boundary unvalidated is indistinguishable from a valid one three call frames later.
> *Testable line:* if a function must defend against malformed input from inside its own module, validation is in the wrong place.

**Design failure, do not infer it.** Error behaviour is part of a contract: what fails, what it returns, what the caller must handle. An unhandled exception path is an undesigned one.
> *Testable line:* if the answer to "what happens when this fails?" requires reading the implementation, the contract is incomplete.

**Encapsulate.** Internal implementation is invisible to consumers. A consumer reaching past an interface has created coupling nobody declared.
> *Testable line:* if changing a module's internals breaks a consumer, the interface was not the boundary.

**Shared code is not a dumping ground.** A utility module accumulates everything nobody could place. Shared abstractions are introduced on **demonstrated** reuse, not anticipated reuse.
> *Testable line:* if a shared module's responsibility cannot be stated in one sentence, it has become a dumping ground.

**Classify idempotency explicitly.** Any operation that may be retried is marked idempotent or not, deliberately. Not discovered during an incident.
> *Testable line:* if you cannot say whether running it twice is safe, it is not ready to be retried.

**No hidden dependencies.** Declared and injected. A module reaching for a global, a singleton, or the clock has a dependency its signature denies.
> *Testable line:* if a test needs monkey-patching to control behaviour, the dependency is hidden.

### Already enforced — referenced, not restated

These exist as controls. **The control governs; this list only points at it.**

| Rule | Enforced by |
|---|---|
| Slice boundaries, cross-slice contracts | `check_slice_boundaries.py` (VSA-1/VSA-3) — cross-slice import is a build failure |
| Bounded change surface | CPM-1 in every PR |
| Dependency pinning, reproducibility | Technology registry allowlist + `uv.lock` + CI `--frozen` |
| Regression protection | `ROLE_CODING` — may not weaken a test to make it pass |
| Chart determinism, additive components | Chart ground rules |
| Re-load idempotency | D-62 — unique constraint at the storage layer |

**Observability** is a principle without a tool: FR-009 defers the tooling choice pending OQ-13, because the stack depends on the deployment target. Boundary operations should expose logging, metrics and tracing; *which* system remains unselected.

---

## 9. Testing architecture — F1a scope

**Status:** F1a-SCOPED, owner decision 2026-08-24. Layers beyond F1a are deferred with recorded triggers — see the deferral table at the end of this section.
**Source:** architectureLayerInventory (testing recorded as ABSENT) · pilot dataset (B2.12 PRE-2)

### Why this is scoped rather than complete

Canon had no testing architecture at all: zero occurrences of `test pyramid`, `unit test`, `integration test`, `contract test`, `test strategy` or `coverage target` across 35 documents. Practices existed — pytest, CI, the may-not-weaken-a-test prohibition, chart ground rule 7's fixture matrix — with nothing connecting them.

Writing the full pyramid now would mostly be guesswork: there are no slices, no contracts, no deployment target. What **cannot** wait is narrower and sharper:

> **Is what F1a produces testable at all?**

That is a *design* property, not a test-writing task. If the event model cannot be verified without a full load, or a directly-follows result cannot be asserted without hand-computing it, that is a **schema** problem — fixed by changing the schema, which is exactly what P-8 exists to prevent. So this section covers F1a, and the rest carries triggers.

### 9a. The three questions F1a testing must answer

**1. Does the schema accept the contract?** The pilot log conforms to 504. Loading it must require no column the schema lacks, and no transformation that invents meaning.

> *Testable line:* if loading the pilot log requires editing the pilot log, the schema is wrong — not the data.

**2. Do dimension resolutions produce the right answer?** Specifically the ones with a wrong default. D-68's as-of SCD-2 lookup returns a different, plausible, wrong answer if joined on the resource's current row. The pilot dataset contains **32 cases spanning a technician's depot change** precisely so this is detectable.

> *Testable line:* every dimension resolution with a temporal dimension needs at least one test case that spans a change. A test set where no entity ever changes cannot distinguish as-of from current.

**3. Are Tier-1 query results correct?** Not "does the query run" — correct. Directly-follows counts, variant identification, wait-time aggregates, closure-ancestry subtree filters.

> *Testable line:* a Tier-1 result is verified only if the expected answer was derived independently of the query that produces it.

### 9b. Where expected answers come from

This is the part that decides whether F1a testing means anything.

The pilot dataset is **generated**, so its correct answers are **derivable from the generator**, not from running the system and blessing the output. That distinction is the whole point.

| Practice | Status |
|---|---|
| Expected values computed from generator parameters or by independent means | **Required** |
| Expected values captured from a system run and frozen as "correct" | **PROHIBITED for correctness tests** |

Capturing output as a baseline is legitimate for *regression* — detecting unintended change. It is not legitimate for *correctness* — it proves only that behaviour is stable, including stably wrong.

> *Testable line:* if the expected value in a test came from running the code under test, it is a regression assertion, not a correctness assertion. Label it as such.

### 9c. Test classes for F1a

Three, with distinct jobs. Markers are declared in `pyproject.toml` and enforced by `--strict-markers`.

**Schema shape tests** — no data. Does the DDL create what the contract needs, with the constraints the design requires? Fast, run on every commit, no database state.

**Load and resolution tests** — pilot dataset, marked `local_env`. Loading and dimension resolution against a real instance. Cannot run in CI: CI has no SQL Server, and the existing exceptions EXC-TEST-01..03 already record this as permanent and correct.

**Tier-1 correctness tests** — pilot dataset, expected answers derived independently. The tests that would catch a wrong directly-follows edge or a mis-resolved business unit.

> A load test proves data arrived. A correctness test proves it arrived *right*. Passing the first while failing the second is the failure this section exists to prevent.

### 9d. What CI can and cannot verify

CI has no SQL Server and will not get one before OQ-13 resolves. So:

| Class | CI | Local |
|---|---|---|
| Schema shape | **Yes** | Yes |
| Load and resolution | **No** — `local_env` | Yes |
| Tier-1 correctness | **No** — `local_env` | Yes |

**This is a real limitation, not a workaround.** Two of the three F1a test classes will be **owner-executed**, exactly as canonical Steps 108 and 109 were. Their results are evidence only when the owner runs them and returns output — the standing rule against recording a step as passing that the owner did not execute.

The durable answer is CI against a real Azure SQL Database, which also closes CF-006's local-versus-Azure divergence. It belongs with the OQ-13 and FR-009 cluster and cannot be scoped until the deployment target is decided.

### 9e. Deferred layers — triggers and prompt points

Each deferred layer names the event that reopens it. **When a trigger fires, the owner is to be prompted with the layer named** — deferral without a prompt point is how an intention becomes an omission.

| Layer | Trigger | Prompt the owner when |
|---|---|---|
| **Contract testing** | First cross-slice contract declared | A `slice.manifest.json` first lists a `producedContracts` entry |
| **Coverage expectations** | F1a code exists | The first F1a PR is opened |
| **Integration testing across slices** | Second slice begins | Build unit F1b starts |
| **End-to-end testing** | A deployable environment exists | OQ-13 resolves |
| **Performance testing** | Real volume on the real target | OQ-13 resolves **and** a client dataset exists |
| **Security testing** | Security architecture is defined | The security-architecture item is taken up (queue item 11) |
| **CI against a real database** | Deployment target chosen | OQ-13 resolves — see CF-006 |

**A deferred layer is not an absent layer.** Every one will be built. What is deferred is *deciding its shape* before there is anything to shape it around — the same reasoning FR-009 applies to observability tooling, and OV-002 to the Fabric source note.

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
| 7 | Decisions that exist only as overlays | AB-CM-011/021/022 | CF-005 | review; testable lines |
| 8 | Code structure and computation placement | D-69 / AC-MINING-PLACEMENT | — | review; testable lines |
| 9 | Testing architecture (F1a scope) | owner decision 2026-08-24 | — | review; testable lines |

Only §2 is machine-enforced today. The rest depend on review, which is why each carries a testable line rather than a general principle. §7 is the least defended of all: it depends on a reader knowing to consult the overlay register, which the DDR itself does not tell them to do.

---

## Two standing rules that apply to all of the above

**The technology registry is allowlist-based.** Any tool not listed ACTIVE in `PROJECTONE-Technology-Registry.json` is **DENIED by default.** Unlisted does not mean unconsidered — it means not approved. Adding an entry is a governed change.

**Immutable sources must be read with their overlays.** This is not a formality — see §7, where three approved decisions exist only as overlays and one of them is a column name. The 500-series documents (502 Playbook, 504 Data Contract) are uploaded sources that are never edited in place. Every change to their content lives in `governance/overlays/PROJECTONE-999-Overlay-Register.json`. Reading one of those sources without its ACTIVE overlays gives you a stale answer.

**Deferring functionality is fine. Deferring design is not.** Under DDR P-8, the design must accommodate known future requirements from the start, even where the functionality is not built yet. A feature can sit below the cut line; the design that feature will need cannot. This is the principle §4 protects.

---

## Before marking this guide complete

Check `PROJECTONE-Forward-Requirements.json`. That register is a **completion precondition, not a suggestion** — it records obligations placed on documents that did not exist when the decision was made. This guide satisfies FR-001, FR-002, FR-003, FR-004, FR-007, and FR-008. FR-005 and FR-006 target the 502 Playbook and the 504 Data Contract. FR-009 (observability tooling) and FR-010 (the compatibility check) are not document requirements.
