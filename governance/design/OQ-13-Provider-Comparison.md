# OQ-13 — Cloud Provider Comparison: AWS vs Azure

**Purpose:** decision support for OQ-13 (deployment target). **This is analysis, not a decision.**
**Date:** 2026-08-14 · **Status:** OPEN — owner decision required
**Scope:** SQL Server hosting only. Application/frontend hosting is a smaller, more portable decision and is noted separately in §6.

> **Verification note.** Azure's serverless rate is taken from your own DDR §5 ($0.5218/vCore-hour). AWS instance prices below come from third-party pricing trackers dated 2026, **not** from AWS's own price page, which does not expose figures in a scrapable form. Treat AWS figures as **directional and requiring confirmation** in the AWS Pricing Calculator before commitment. Structural facts (no serverless SQL Server, 7-day stop cap, License Included only) are confirmed against AWS's own documentation.

---

## 1. Requirement-by-requirement comparison

Legend for "DDR requires?" — **LOCKED** = a locked decision depends on it · **DESIGN** = design-now/build-later commitment · **DESIRABLE** = wanted, not mandated · **NO** = not a ProjectOne requirement

| # | Need | DDR ref | DDR requires? | Azure SQL Database | AWS RDS for SQL Server | Recommend |
|---|---|---|---|---|---|---|
| 1 | **Compute scales to zero when idle** | D-21 ("can pause when idle", "$0 compute when paused") | **LOCKED** | **Yes** — serverless GP auto-pause, per-second billing, indefinite | **No.** No serverless SQL Server exists. Stop is capped at 7 days then auto-restarts | **Azure** |
| 2 | **Bursty scale-up for refresh windows** | D-21 ("serverless scales to refresh bursts and down between them") | **LOCKED** | **Yes** — autoscale between min/max vCores | Manual instance resize (restart required) | **Azure** |
| 3 | **Columnstore on fact/base-metric tables** | D-21, D-27 | **LOCKED** | Yes | Yes (SE 2016 SP1+) | **Either** |
| 4 | **Date-range partitioning + partition elimination** | D-27 | **LOCKED** | Yes | Yes | **Either** |
| 5 | **Columnstore archival compression for cold partitions** | D-27 (hot/cold tiering) | **LOCKED** | Yes | Yes | **Either** |
| 6 | **UNIQUE constraint enforced at storage layer** | **D-62** ("duplicates rejected at the storage layer") | **LOCKED** | Yes | Yes | **Either** *(this is what excludes Fabric, not AWS)* |
| 7 | **MERGE on natural key for idempotent re-load** | D-62, D-19 | **LOCKED** | Yes | Yes | **Either** |
| 8 | **Isolated clients as separate databases via resolver row** | D-16, D-17 | **LOCKED** | **Yes** — each is an independent serverless DB, pausing independently | Separate databases on one instance; cannot pause individually | **Azure** |
| 9 | **Graduate a latency-sensitive tenant to always-warm** | D-26, D-17 ("one row") | **LOCKED** | **Yes** — change that DB's tier; other tenants unaffected | Whole instance is always warm; no per-tenant distinction to make | **Azure** *(the requirement only exists because Azure pauses)* |
| 10 | **Free tier for dev / staging / demos** | D-21 ("free dev tier") | **LOCKED** | **Yes** — ongoing free serverless offer | **Express Edition on t3.micro only, 12 months.** Express is feature-limited | **Azure** |
| 11 | **Tier-1 < 1s warm interactive reads** | D-26 | **LOCKED** | Yes | Yes | **Either** |
| 12 | **Tier-2 ≤ 2s p95 warm queries** | D-26 | **LOCKED** | Yes | Yes | **Either** |
| 13 | **Cold-start ~30–60s acceptable as an exception** | D-26 (explicit carve-out) | **LOCKED** | Applies (this is the auto-pause cost) | N/A — never paused, so never cold | **Either** *(AWS avoids the problem by never pausing, which is the thing you pay for)* |
| 14 | **Elastic Pool / pooled compute when DB count grows** | D-21 (Option B, "cost trigger") | **LOCKED** growth path | **Yes** — Elastic Pool is a named product | No equivalent. Consolidate onto one instance instead — different mechanism, comparable outcome | **Azure** |
| 15 | **Hyperscale-class growth when raw retention gets large** | D-21 (Option C) | **LOCKED** growth path | **Yes** — Hyperscale tier, up to 100 TB | GP SSD caps at 16 TiB per instance; shard beyond | **Azure** |
| 16 | **Read/write separation at scale** | D-21 ("when read/write separation is wanted") | **DESIGN** | Yes — Hyperscale replicas | Yes — read replicas | **Either** |
| 17 | **Cross-tenant benchmarking substrate** | D-27, DDR §"conformed dims → FR-1 external-benchmarking normalization substrate" | **DESIGN** | Via benchmark store fed by per-tenant refresh — no cross-DB query needed | Same pattern. Native cross-DB queries also available but **should not be used** (see §4) | **Either** |
| 18 | **Delphics / delegate cross-tenant access** | D-37, **D-61** | **LOCKED** (Delphics functional in MVP) | Permission model in the application + resolver. Not a DB engine feature | Same | **Either** *(this is a role capability, not a SQL mechanism)* |
| 19 | **Cross-database T-SQL queries (3-part names)** | — | **NO** | Only via Elastic Query: preview for years, SELECT-only, **requires public network access**, no Managed Identity | **Yes**, native within an instance | **AWS** on capability — but see §4: this should not be used |
| 20 | **SQL Server Agent (in-database scheduler)** | — | **NO** | Not available. Use Elastic Jobs / timer function / container | **Yes** | **AWS** on capability — but an external scheduler is needed regardless (AC-MINING-PLACEMENT) |
| 21 | **Linked servers to external SQL Servers** | 504 data contract | **NO** | No | **Yes** | **AWS** on capability — but clients *supply* logs; you don't reach into their production DB |
| 22 | **CLR (.NET inside the database)** | — | **NO** | No | **Yes** (option group) | **AWS** on capability — Python does this work under CP-002 |
| 23 | **Mining executes set-based in the database** | **AC-MINING-PLACEMENT** (CP-002) | **LOCKED** | Yes | Yes | **Either** |
| 24 | **Ingestion run / lineage spine** | **D-63** | **LOCKED** | Yes — ordinary tables | Yes | **Either** |
| 25 | **Baseline reconciliation at ingestion** | D-53 | **LOCKED** | Yes | Yes | **Either** |
| 26 | **Tenant isolation demonstrable per access path** | Global non-waivable invariant | **LOCKED** | **Strong** — separate databases, separate credentials, no cross-DB path exists by default | Achievable, but a cross-DB path *exists* and must be disciplined away | **Azure** *(isolation by construction beats isolation by policy)* |
| 27 | **Private endpoint / no public network exposure** | Security policy | **LOCKED** | Yes — **but Elastic Query is incompatible with private endpoints** | Yes — VPC | **Either** *(reinforces not using Elastic Query)* |
| 28 | **Audit trail separable for operator vs client actions** | D-30, D-61 | **LOCKED** | Yes — Azure SQL Auditing | Yes — RDS audit options | **Either** |
| 29 | **Observability: log / metric / trace / audit / alert** | 25 verification-map decisions; **FR-009** | **LOCKED** (mechanism required before production) | Azure Monitor · Log Analytics · Application Insights — integrated | CloudWatch · X-Ray — integrated | **Either** *(both adequate; this is why FR-009 was deferred pending OQ-13, and it becomes selectable once decided)* |
| 30 | **No-migration posture: no forced schema transformation** | **P-8** | **LOCKED** | Provider-neutral. Numbered forward-only scripts (CP-005) | Same | **Either** |

**Tally on the 30 needs:** Azure preferred on 9 · AWS preferred on 4 (all four being capabilities the DDR does **not** require) · Either on 17.

---

## 2. The decisive finding

**Requirement #1 is a locked decision that AWS cannot satisfy.**

D-21 locks the serving posture as serverless with pause-when-idle, and quantifies it: *"$0 compute when paused."* D-26 then builds the latency budget *around* that behaviour, carving out an explicit exception for the 30–60s first query after an auto-pause.

There is **no serverless SQL Server on AWS.** Aurora Serverless v2 — the scale-to-zero product — runs PostgreSQL and MySQL only. RDS for SQL Server can be stopped, but AWS's own documentation caps that at seven days before automatic restart. That is a dev/test convenience, not an operating posture.

**So choosing AWS is not "picking a different vendor." It requires amending LOCKED D-21 and D-26 through the 999 overlay mechanism.** That is a legitimate thing to do — but it is a canon change, not a deployment choice, and it should be made deliberately rather than as a side effect.

---

## 3. Cost comparison

### Azure SQL Database (serverless GP)

From your own DDR §5: **$0.5218 / vCore-hour**, per-second billing, min 0.5 vCore, **$0 compute when paused** (storage still billed).

| Scenario | Usage | Compute | Storage | **Total / month** |
|---|---|---|---|---|
| **A — Intermittent** (pauses overnight/weekends; early pilot) | ~6 hr/day @ ~1 vCore | ~$90 | ~$5–12 | **~$100** |
| **Dev / staging / demo** | Free tier | $0 | $0 | **$0** |

### AWS RDS for SQL Server (Standard Edition, License Included)

No pause. Billed continuously. Licence baked into the hourly rate; **no BYOL option on RDS.**

| Configuration | Rate | Running 24/7 | **Total / month** |
|---|---|---|---|
| SE `db.r8g.xlarge` (4 vCPU) Single-AZ | ~$1.224/hr | 730 hr | **~$894** + ~$115/TB storage |
| Same, 1-yr Reserved (~25% off) | ~$0.914/hr | 730 hr | **~$667** |
| SE `db.m5.2xlarge` (8 vCPU) Single-AZ | ~$3.00–3.50/hr | 730 hr | **~$2,200–2,500** |
| Same, Multi-AZ (HA) | ~2× | 730 hr | **~$4,400–5,000** |
| Dev / staging | t3.micro **Express only**, 12 months | — | **$0 → then paid** |

*A smaller 2-vCPU class would roughly halve the entry figure (~$450/month), but 2 vCPU with limited RAM is marginal for a columnstore analytic workload.*

### The gap

| | Azure | AWS (entry) | Multiple |
|---|---|---|---|
| Pre-revenue pilot | **~$100/mo** | **~$450–900/mo** | **4.5–9×** |
| Dev/staging/demo | **$0** | Express-limited, then paid | — |

**Why the gap is structural, not a pricing quirk.** Your workload is *"light and bursty (calm monitoring + batch refresh + few analysts)"* — D-21's own words. Azure bills for the hours you use. AWS bills for the hours that exist. At ~25% utilisation the difference is roughly the inverse of utilisation, and the SQL Server licence is being paid on idle hours too.

**AWS is not badly priced.** It is priced for a database that runs continuously. Yours does not.

---

## 4. Why AWS's four extra capabilities do not close the gap

AWS genuinely offers SQL Agent, cross-database queries, linked servers and CLR. None is a ProjectOne requirement, and one of them is actively undesirable.

**Cross-database queries would work against your architecture.** Cross-tenant benchmarking should not join across live tenant databases, on any provider:

- **Isolation.** `tenant_isolation` is a global non-waivable invariant. A query path that *can* cross tenant boundaries is the capability that invariant exists to prevent. Building on it means creating the dangerous path and relying on discipline.
- **Fan-out.** Isolated tenants live in auto-pausing databases. Benchmarking across 40 tenants means 40 cold starts at 30–60s each (D-26).
- **Consent.** You cannot show Tenant A Tenant B's figures. Benchmarking needs anonymised, aggregated, threshold-suppressed data — a different dataset.
- **Comparability.** The platform is industry-agnostic; tenants have different activities and vocabularies. Raw joins would compare incomparable things.

**Your DDR already specifies the right pattern:** conformed dimensions as the *"FR-1 external-benchmarking normalization substrate"*, with base metrics retained ~3+ years to *"power historical drift/SPC/benchmarking look-back"* (D-27).

**The pattern:** each tenant's scheduled refresh writes anonymised, consented, aggregated metrics into one benchmark store. Benchmarking reads that single database. No cross-database query anywhere. Isolation preserved by construction. Identical on either provider.

**On the other three:** SQL Agent is replaced by an external scheduler you need anyway, because AC-MINING-PLACEMENT requires mining to run as a background job and you will have app-tier jobs Agent could not run. Linked servers assume you reach into a client's production database, which is not the model in your data contract (504). CLR is superseded by Python under CP-002.

---

## 5. Handling data and client expansion

### Azure — the growth path D-21 already specifies

| Trigger | Move | What it costs you |
|---|---|---|
| **Now** (~10s of tenants) | Shared serverless DB + separate serverless DBs for isolated clients | Cheapest credible start |
| **Separate DBs multiply** — a **cost** trigger, not isolation | **Elastic Pool** (Option B) | Amortises per-DB idle compute floors; tenants still logically separate |
| **Raw retention gets large**, or read/write separation wanted | **Hyperscale** (Option C) | Up to 100 TB; read replicas |
| **Measured pause/wake ratio favours it** | Provisioned compute | A later cost dial, chosen on evidence |
| **A tenant needs low latency** | Graduate that DB to always-warm — **one resolver row** (D-17) | Per-tenant, no platform change |

**Each step is a configuration change on the same engine.** Schema is untouched, so no step is a P-8 migration event. This is the "growth dial": D-21 pre-decided the *sequence* and the *trigger* for each move, so scaling is a threshold being crossed rather than a decision being made under pressure.

**Weakness:** per-database compute floors. Forty databases each carry a minimum. Elastic Pool exists precisely to absorb that, and D-21 names it as the response.

### AWS — expansion by instance sizing and sharding

| Trigger | Move | What it costs you |
|---|---|---|
| More tenants | More databases on the same instance | Cheap per tenant — **no per-DB floor.** Genuine advantage at density |
| Instance saturated | Resize to a larger class | Requires a restart; step changes, not smooth |
| Beyond 16 TiB (GP SSD cap) | Shard across instances | Application-level sharding — real engineering work |
| Isolation needed per tenant | Separate RDS instance per tenant | **Each pays a full always-on instance + licence.** Prohibitive at low tenant counts |
| A tenant needs low latency | Nothing to do — always warm | The thing you pay for continuously |

**Strength:** no per-database compute floor. At high density, one instance with many databases is cheaper per tenant than many serverless databases.

**Weakness:** the cost curve starts high and steps rather than scales. Isolated clients (D-16/D-17) are expensive on AWS because isolation implies a separate always-on instance, and the licence is charged per instance.

### The shape of the two curves

**Azure starts near zero and rises with usage.** Cheapest exactly where you are now — pre-revenue, few tenants, intermittent load — and Elastic Pool absorbs the density problem when it arrives.

**AWS starts high and flattens.** More economical only at sustained high utilisation with many tenants densely packed — a state you might reach in years, or never.

**For a solo founder pre-revenue, the curve that starts near zero is worth more than the curve that flattens later** — partly on cash, but mainly because it removes a fixed monthly obligation before there is revenue to meet it.

---

## 6. Application and frontend hosting — separable

This comparison is about **SQL Server hosting**, which is where the lock-in and the cost asymmetry both sit.

FastAPI and a React build are portable. Container images and static assets run on Azure App Service, Container Apps, AWS ECS/Fargate, or Amplify with comparable effort and cost. Nothing in the DDR constrains this, and it can be revisited without touching data.

**Practical caveat:** placing application compute in a different cloud from the database adds cross-cloud egress cost and latency on every query. Co-locating is the sane default. So the database decision effectively carries the app-hosting decision — not by constraint, but by physics.

---

## 7. Summary and recommendation

**Recommendation: Azure.** Three reasons, in order of weight.

**1. AWS cannot satisfy a locked decision.** D-21 locks pause-when-idle serverless and D-26 depends on it. There is no serverless SQL Server on AWS. Choosing AWS means amending locked canon through the 999 overlay — a deliberate act, not a deployment preference.

**2. Cost, structurally, for this workload.** 4.5–9× at the pilot stage, plus a real ongoing free tier for dev and demos versus 12 months of feature-limited Express. The workload is intermittent; Azure charges for use, AWS charges for existence.

**3. The growth path is pre-decided.** D-21 already names each move and its trigger. Every step is configuration on the same engine, so none is a P-8 event.

**What choosing Azure costs you.** The fuller SQL Server surface — SQL Agent, cross-database queries, linked servers, CLR. §4 argues none is needed, and that cross-database queries would work against your isolation invariant. If any of those four later proves load-bearing, that is the moment to revisit.

**What would change this recommendation.** Sustained high utilisation across many densely-packed tenants — in which case AWS's absent per-database floor starts to matter, and the pause capability stops being worth paying for. That is a *later* condition, testable against the same pause/wake ratio D-21 already nominates as the provisioned-compute trigger.

**Honest limitation of this analysis.** AWS figures are third-party and directional; confirm in the AWS Pricing Calculator before relying on them. The structural facts — no serverless SQL Server, 7-day stop cap, License Included only, Express-only free tier — are confirmed against AWS's own documentation and are what actually drive the recommendation. **The conclusion does not depend on the price figures being exact.**

---

## 8. If you choose Azure — what unblocks immediately

| Item | Currently | After deciding |
|---|---|---|
| **FR-009** observability tooling | Deferred pending OQ-13 | Selectable: Azure Monitor, Log Analytics, Application Insights |
| **D-27** partition scheme and tier boundaries | *"tied to the deployment target (OQ-13)"* | Can be specified |
| Scheduler choice | Unresolved | Azure Elastic Jobs / timer function / container |
| MI-only prohibition (CP-004) | Recorded as a temporary tax to keep options open | Becomes **permanent**, and the reason simplifies: Azure SQL Database does not have these features, full stop |
| **OQ-06** volumes | Open | Still open — it is a volume question, not a provider question |

**Still open after deciding Azure:** the growth dial (which of Option A → Elastic Pool → Hyperscale, and when), because that is triggered by volumes under OQ-06 and by the measured pause/wake ratio. That is the part of OQ-13 that is genuinely, usefully late-binding.
