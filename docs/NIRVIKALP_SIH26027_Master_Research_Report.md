# NIRVIKALP — SIH26027 Railway Block Planning Master Research Report

**Prepared for Arjun and Team NIRVIKALP · Research cut-off: 22 September 2026**  
**Purpose:** establish the evidence and research decisions before prototype development. No prototype, user interface, or replacement presentation is delivered here.

## How to read this report

**VERIFIED** means the cited document directly supports the narrowly stated fact. It does not mean that a published policy is uniformly implemented. **STRONGLY SUPPORTED** means credible evidence supports a proposition with a stated provenance or coverage limitation. **INFERRED** means this report's reasoned interpretation or proposed design. **ASSUMPTION** means an explicit input to a hypothetical demonstration. **UNKNOWN** means not established by the sources inspected. Tables declare a default label where repeating it in every cell would obscure the comparison.

The supplied presentation and previous AI report are objects of review, not railway authorities. The presentation audit concerns its statements and extracted slide content, not a complete visual-design review. Source numbers link to the original documents; Section 26 records their evidential scope. Public documentation cannot establish every production capability, deployment, permission, or local operating rule.

---

## 1. Executive Summary

**INFERRED — central answer:** SIH26027 asks for better maintenance scheduling decisions across existing railway information systems: which work to undertake, where, when, and together with what other work, while respecting train operations and maintenance urgency. It should be investigated as a decision-support extension to the existing process. The evidence does not justify presenting it as the invention of railway coordination. [S01][S03][S05][S06][S07][S08][S09]

**VERIFIED:** the official problem statement requests integration, prioritization, cross-department scheduling, and weekly and monthly plans. **VERIFIED:** the Railway Board's rolling-block procedure already provides a joint planning framework. **UNKNOWN:** the precise optimization functions, interfaces, and adoption levels of every current BDMS/RBS installation. These three statements can all be true. [S01][S03][S09]

The most credible research direction is an explainable scheduler for a bounded corridor, using traceable input assumptions, explicitly validated work compatibility, resource constraints, and a fair coordinated baseline. It should show why a plan is feasible, why an urgent task cannot fit, and what a small permitted change would achieve. This is a proposed direction, not a demonstrated product advantage.

Four corrections are necessary before the next presentation:

1. Historical audit observations cannot establish present-day national performance or the fraction of work that could safely be combined.
2. Digitization, visibility, joint planning, optimization, and operational authorization are different capabilities. A gap in one does not prove the absence of the others.
3. Public passenger schedules cannot substitute for complete working timetables, freight forecasts, route occupation, or authorized block calendars.
4. A synthetic-data demonstration can establish software behavior under assumptions. It cannot establish a calibrated railway prediction model or real-world savings.

**INFERRED — success condition:** produce feasible weekly and monthly plans that improve a declared operational objective against an informed baseline, without sacrificing mandatory maintenance or hiding uncertainty. No official SIH-specific asset-availability formula was located; the proposed metrics in Section 21 must therefore be labelled prototype metrics.

> **PPT TAKEAWAY — Improve the decision within the existing railway process.**  
> • Scheduling across departments and two planning horizons are explicit requirements.  
> • Programme coordination already has an official framework.  
> **Visual:** existing systems → validated planning inputs → alternatives → authorized human decision.  
> **Sources:** [official PS][S01]; [Board procedure, clauses (a)–(j)][S03].

## 2. SIH26027 Decoded Requirement by Requirement

The current official listing was inspected under ID 26027. The following short requirement fragments paraphrase its background, detailed description, and expected solution. Their operational interpretations and proposed proof are **INFERRED**, not extra Ministry requirements. The PS does not provide a downloadable operational dataset in the inspected entry. [S01]

| ID / PS element | Operational meaning and decision | Required input | Responsible systems / people | Problem type | Proposed evidence |
|---|---|---|---|---|---|
| B1: separate infrastructure departments | Preserve distinct asset responsibilities while planning common access | Department, asset, responsible unit | Engineering, S&T, TRD | Integration/workflow | Every task retains its owner |
| B2: demands through BDMS | Consume a demand; do not invent its authorization | Demand ID, requested location/time/status | BDMS; requesting and operating staff | Integration/workflow | Trace an imported demand into a draft plan |
| B3: decentralized/manual planning | Compare alternatives beyond an individual request | All relevant demands and constraints | Department planners; Control Office | Optimization/workflow | Benchmark against coordinated human-style planning |
| B4: inefficient coordination/utilization | Test whether changing assignment improves a measurable outcome | Resources, compatible work, occupation | Joint planning team | Optimization | Report benefits and no-benefit cases |
| D1: defects and overdue maintenance | Convert recorded needs into schedulable jobs without losing urgency | Defect, task type, due date, status | TMS, SMMS, TDMS | Integration/prioritization | Validated task records; rejected incomplete records |
| D2: corridor availability through COA | Restrict proposed work to usable access opportunities | Time windows, train occupation, restrictions | COA / operating planners | Integration/optimization | Explain why each selected interval is available |
| D3: combine maintenance and corridor information | Join spatial, temporal and asset identities | Location crosswalk, timestamps, task IDs | All five named systems | Integration | Detect mismatched or ambiguous locations |
| D4: optimize schedules | Select work, timing and permissible grouping jointly | Feasible alternatives, resources, deadlines | Planning decision layer | Optimization | Feasible schedule and reproducible objective |
| D5: prioritize / reduce downtime | Complete important work with economical access use | Authorized severity, deadlines, occupation | Maintenance owners and planners | Prioritization/optimization | No low-priority gain conceals mandatory failure |
| D6: availability / train continuity | Evaluate effects on usable infrastructure and train paths | Track-time occupation and traffic | Control Office | Optimization/evaluation | Separate path impact from simulated delay |
| E1a: defect inputs | Preserve engineering meaning, not just free text | Asset-specific defects | TMS/SMMS/TDMS | Integration | Provenance for each defect |
| E1b: overdue inputs | Compute lateness against the correct due date | Due rule, date, completed/deferred status | Maintenance systems | Prioritization | Overdue task accounting |
| E1c: corridor/block availability | Distinguish requested, planned and granted windows | Window type and lifecycle status | COA/BDMS | Integration/workflow | No draft represented as a live grant |
| E1d: train timetable | Represent relevant running through the work footprint | Section entry/exit, routes, operating dates | Timetable / COA | Integration/optimization | Conflicts checked beyond station stops |
| E1e: goods forecast | Accept prospective freight movement from Control Office | Forecast issue time, paths or arrival ranges | Control Office / relevant freight inputs | Prediction input | Scenario sensitivity; no invented forecasting requirement |
| E2a: AI/ML prioritization | Support transparent ranking of competing needs | Criticality, urgency, impact | Decision layer; asset owner | Prioritization | Ranking explanation and override record |
| E2b: AI/ML scheduling | Search feasible alternatives under constraints | Tasks, access, resources, traffic | Decision layer | Optimization | Compare a constrained method against baseline |
| E2c: availability impact | Expose why a choice affects train operation | Occupation and traffic overlap | Operating planner | Evaluation | Defined, auditable impact calculation |
| E3: coordinate departments | Select compatible concurrent or sequential work | Work footprints and approved compatibility | Engineering + S&T + TRD | Optimization/workflow | Both valid and rejected combinations |
| E4a: weekly plan | Produce executable near-term proposals | Readiness, detailed availability, commitments | Joint planners | Optimization/workflow | Seven-day schedule and unresolved items |
| E4b: monthly plan | Allocate work over a longer horizon | Due work, provisional capacity/resources | Joint planners | Optimization/workflow | Monthly allocation consistent with weekly refinement |
| Outcome: safer, reliable, data-driven planning | Make decisions inspectable and uncertainty visible | Rules, versions, evidence, approvals | Authorized railway staff | Governance/evaluation | Audit trail; no autonomous field authority |

**Scope boundary — INFERRED:** dynamic replanning can be an extension. A national train dispatcher, a new signalling system, an autonomous block-granting system, new sensors, and a production freight predictor are not explicit deliverables in this PS. The exact interpretation of the AI/ML wording should be confirmed with the organizer; do not market a rules-only implementation as a trained model.

> **PPT TAKEAWAY — Prove every requirement with an observable result.**  
> • Integration is an input obligation, not the whole solution.  
> • Weekly and monthly outputs both need evidence.  
> **Visual:** requirement → input → decision → test matrix.  
> **Source:** [SIH26027, background, detailed description and expected solution][S01].

## 3. Indian Railways for a Beginner

### People, places and time

The following is a simplified orientation. Administrative descriptions are **INFERRED explanatory summaries** of the roles visible in the Board procedure and CRIS documentation; they do not specify every delegation of powers. Examples use imaginary stations A, B and C. [S03][S08]

| Term | Simple meaning; technical distinction | Small example |
|---|---|---|
| Railway Board | National policy and coordination level; not the desk issuing every local block | Issues a planning procedure |
| Zone | A regional railway organization covering divisions | Coordinates an issue crossing divisions |
| Division | An operating/maintenance administrative unit | Prepares a rolling programme |
| Control Office | The place coordinating the running railway over a territory | Considers a delayed train before access |
| Section Controller | Controller responsible for train regulation in an assigned control section | Adjusts a proposed access opportunity |
| Station | A defined railway operating location; more than a passenger platform | A has loops and controlled routes |
| Section | A context-dependent stretch of railway; must have explicit endpoints | A–C is the planning section |
| Block section | A specifically defined train-working unit, not a maintenance job | A–B under the applicable block system |
| Corridor | A route or planned maintenance access pattern; scope must be specified | A–C maintenance opportunity |
| UP / DOWN | Locally assigned directions/line designations; not universally north/south | Work occupies DOWN only |
| Working Time Table (WTT) | Operational timetable, requiring more detail than a public passenger schedule | Passing movements matter even without a stop |
| Master chart | A planned time–distance representation | Sloping lines show scheduled trains |
| Control chart | Actual/forecast running representation used in control | A late running line shifts right |
| Train path | A train's occupation of successive infrastructure over time | A 10:00 → B 10:18 → C 10:40 |
| Passenger / goods path | Paths for different traffic, with potentially different timing certainty and performance | A forecast goods movement consumes capacity too |
| Line capacity | Ability to accommodate traffic under specified infrastructure, timetable and operating assumptions | Train mix can change usable paths |

**VERIFIED boundary:** the G&SR definition of a block section and the separate rules for automatic signalling show why a generic “station pair equals the smallest railway unit” model is unsafe. [S15, GR 1.02(10), Chapter IX] A prototype's simplified topology must be labelled an assumption.

### The word “block” has several meanings

Definitions below are **STRONGLY SUPPORTED operational summaries**, with local usage requiring confirmation where stated. Illustrations are **ASSUMPTIONS**, not safe-work instructions.

| Term | Meaning and technical distinction | Illustration / relevance | Source / limit |
|---|---|---|---|
| Railway block section | Train-working geography | A train's authority over A–B; fundamental topology | [S15], GR 1.02(10) |
| Maintenance block | Umbrella planning expression for access needed to maintain assets | Track work needing protected time; central to PS | [S01][S03] |
| Traffic block | Restriction of train movements for work over a defined scope | No permitted train occupation on affected track | [S15], relevant work rules; local procedure needed |
| Line block | Usage can overlap traffic block; do not assume one universal separate category | Store the source's actual category | **UNKNOWN** uniform definition across reviewed material |
| Power block | Electrical isolation arrangements for a defined electrical scope | An OHE task; electrical footprint may differ from track footprint | [S15], Chapter XVII |
| Disconnection | Taking relevant signalling/interlocking apparatus out of normal service under procedure | Point work can affect more than one route | [S15], GR/SR 3.51 |
| Corridor block | Planned access window associated with a corridor | Provisional opportunity in a WTT/planning calendar | [S03] |
| Integrated / combined block | Coordinating multiple maintenance activities within shared access | Compatible work shares occupation; not automatically simultaneous | [S03][S02], pp.30–31 |
| Shadow block | Work taking advantage of access already created by another activity | Additional work fits the existing footprint and duration | [S04]; local eligibility must be verified |
| Mega block | Large organized work/access arrangement; not a universal duration | Major planned package with wider operating consequences | [S03]; no universal threshold established |
| Block bursting / overrun | Work/occupation exceeding the granted duration | Release is later than planned; important uncertainty | [S02], p.34 |
| Engineering allowance | Timetable time accommodating maintenance-related temporary restrictions | Added running allowance is not permission to occupy track | [S28], PDF p.11 |
| Traffic allowance | Timetable cushion for operational delay and its propagation | Recovery time is not an empty maintenance slot | [S28], PDF p.11 |

**INFERRED modelling consequence:** represent geographic scope, time, traffic restrictions, electrical isolation, signalling effects, and lifecycle status separately. A label such as “combined block” cannot substitute for these fields.

> **PPT TAKEAWAY — Geography, access time and authority are different things.**  
> • A block section is not a maintenance task.  
> • A timetable allowance is not a work permit.  
> **Visual:** three layers: track route, electrical section, signalling routes.  
> **Sources:** [G&SR][S15]; [timetabling paper, PDF p.11][S28].

## 4. How Maintenance Block Planning Actually Works Today

**Simple explanation:** departments identify work; planners reconcile access with trains and resources; the programme is approved; authorized operational staff then control actual execution and restoration. Approval of a future programme is not a standing permit to begin work. [S03][S15]

**VERIFIED policy anchor:** the 29 August 2023 Board procedure calls for joint planning, corridor consideration by Sr.DOM, weekly branch-officer review and DRM approval, resource preparation, and recording demand, grant, actual duration and output. It retains existing urgent-block practices. This verifies a prescribed process, not compliance in every division. [S03]

The process map below combines that policy with documented system functions. Unverified local details are explicitly separated.

| Stage | Evidence-backed outline | What remains locally unverified |
|---|---|---|
| Identify | Inspections, defect reports and scheduled maintenance generate work needs [S05][S06][S07] | Exact inspection-to-task conversion and mandatory response time |
| Record | Departmental systems hold relevant asset/maintenance information [S05][S06][S07] | Current fields, screens and mandatory attachments |
| Assess | Authorized maintenance staff interpret condition and due work | Exact severity taxonomy and approval hierarchy |
| Request | PS identifies BDMS for block demands [S01] | Request cut-off, escalation and version-specific routing |
| Reconcile | Joint planning considers corridors, traffic and readiness [S03] | Meeting cadence beyond prescribed review; local arbitration |
| Approve programme | DRM programme approval is explicitly stated [S03] | Delegated exceptions and current divisional instructions |
| Grant and protect | Applicable operating/electrical/signalling procedures govern actual access [S15] | Current local signatories, messages, forms and interlocks |
| Execute | Work must remain within its authorized protection and conditions | Job-specific protection, productivity and adjacent-line restrictions |
| Restore/release | Restoration and required communications are separate from finishing physical work [S15] | Full local release checklist and system update timing |
| Review | Planned versus actual work/duration is recorded [S03] | Data quality, reasons taxonomy and feedback into estimates |

**Overruns — INFERRED design response:** forecast late completion should trigger an exception for authorized staff, not an automatic extension. Do not mark a block released merely because its planned end time passes. Emergency work likewise cannot wait for a weekly optimizer; represent its operational consequences after the competent authority acts.

**NOT PUBLICLY VERIFIED / REQUIRES RAILWAY SME CONFIRMATION:** a single current all-India sequence of software clicks, role permissions, local deadlines, and block-grant/release messages. This report therefore does not fabricate one.

> **PPT TAKEAWAY — Programme approval and actual block grant are separate stages.**  
> • A proposed plan must retain its status.  
> • Execution feedback is needed to evaluate planning quality.  
> **Visual:** need → request → programme → actual authority → work → restoration.  
> **Sources:** [Board procedure][S03]; [G&SR work and electrical rules][S15].

## 5. Engineering vs S&T vs TRD Workflow

**VERIFIED at system-purpose level; INFERRED at proposed planning-field level.** Exact urgency rules and job-level execution instructions require the applicable manuals and an SME. [S05][S06][S07][S15]

| Dimension | Engineering / Permanent Way | Signal & Telecommunications | Traction Distribution / Electrical |
|---|---|---|---|
| Typical asset focus | Track and associated permanent-way assets | Signals, points/interlocking apparatus and relevant signalling assets | OHE and traction distribution assets |
| Recorded need | Inspection finding, defect or scheduled maintenance | Failure, inspection or scheduled maintenance | Inspection defect, failure or scheduled maintenance |
| Principal named system | Track Management System | Signalling Maintenance & Management System | Traction Distribution Management System |
| Possible access implication | Track occupation, machinery, temporary restrictions | Apparatus disconnection and affected route restrictions | Isolation scope, power block and possibly traffic protection |
| Planning inputs to request | Location, work quantity, duration, machines, restoration needs | Apparatus IDs, affected routes, test/restoration needs | Electrical section IDs, isolation requirements, access and restoration needs |
| Resource distinction | A track machine is not a generic interchangeable crew | Required competency and testing capability matter | Authorized electrical personnel/equipment matter |
| Main joint-work question | Can people/machines safely share the footprint? | Does one activity disable protection or routes needed by another? | Does the isolated electrical area match the intended work and traffic restrictions? |

**INFERRED example:** three jobs at the same station may still be incompatible because one needs a machine movement through another's protected worksite. Conversely, two jobs with different asset identifiers may share an already authorized footprint if competent staff confirm compatibility. A distance threshold or common department label cannot answer either case.

Urgency must remain attributable to a railway source: criticality class, due date, applicable restriction, and responsible officer. A proposed algorithm can prioritize among permitted alternatives; it should not silently downgrade a mandatory defect because a low-priority package produces a better “savings” score.

> **PPT TAKEAWAY — A shared location is only the beginning of a compatibility check.**  
> • Track, signalling and electrical footprints differ.  
> • Resources and restoration dependencies can prevent concurrency.  
> **Visual:** three departmental jobs overlaid on one location with distinct footprints.  
> **Sources:** [TMS][S05], [SMMS][S06], [TDMS][S07], [G&SR][S15]; proposed compatibility analysis.

## 6. TMS / SMMS / TDMS / BDMS / COA — What They Really Do

### Documented functions

**VERIFIED** below means advertised/documented by the publisher. It does not independently validate uptime, complete rollout or effectiveness. BDMS evidence has a weaker provenance, stated separately.

| System / owner-developer | Users; inputs → outputs | Timing and scope | Integration / limits |
|---|---|---|---|
| **TMS — Track Management System; CRIS / Indian Railways** | Engineering; asset and inspection records → maintenance/inspection monitoring, alerts and reports | Field information and reporting; public latency SLA not found | CRIS describes condition/codal-life-based prioritization and collaboration. Thus “only a static asset list” is inaccurate. [S05] |
| **SMMS — Signalling Maintenance & Management System; CRIS / Indian Railways** | S&T; assets, maintenance completion and failures → maintenance information and monitoring | Official app describes field access; system-wide latency unknown | App publisher is CRIS. Current detailed interfaces and full rollout scope not established. [S06] |
| **TDMS — Traction Distribution Management System; CRIS / Indian Railways** | TRD; OHE assets, inspection, defects/failures → maintenance information and exception alerts | Field/mobile reporting and planning functions | CRIS describes integration design involving track/signalling assets; deployment of every proposed interface is not proven. [S07] |
| **BDMS — Block & Disconnection Management System; CRIS attribution in mirrored manual** | Requesting departments and Operating; demands/status → processing, monitoring, approval workflow | Mirrored manual describes real-time processing | The manual includes all-department views and unified access with maintenance systems. Current official-host manual and nationwide rollout not verified. [S09] |
| **COA — Control Office Application; CRIS / Indian Railways** | Controllers; train running and operational events → control chart, occupation/running information and forecasts | Operational application; public exact feed latency unknown | CRIS documents exchanges with other railway applications. Train tracking alone understates its role. [S08] |

### Capability inventory

**D** = directly documented; **M** = mirrored-document claim; **U** = not publicly established in reviewed evidence. A U is not “no”. “Approval” refers to recorded workflow, not software independently exercising statutory authority.

| Capability | TMS | SMMS | TDMS | BDMS | COA |
|---|---:|---:|---:|---:|---:|
| Defects/condition/failures | D | D | D | U | Operational events D |
| Maintenance records/planning | D | D | D | Demands M | Corridor information per PS D |
| Train movement records | U | U | U | U | D |
| Block request handling | U | U | U | D in PS / details M | Detailed current ownership U |
| Approval workflow | U | U | U | M | Exact current block workflow U |
| Joint departmental visibility | Full scope U | Full scope U | Full scope U | M | Operational coordination D |
| Mathematical joint optimizer | U | U | U | U | U for the PS's complete task |
| Published integration descriptions | D | Limited official / newer mirror | D | M | D |
| Tested open operational endpoint | None located | None located | None located | None located | None located |

**Public access finding for each of these five systems:** “No official public API located during this research.” This is a search outcome, not proof that internal APIs do not exist. No open task-level production dataset was obtained. Exact authentication, rate limits, schemas and access permissions remain **UNKNOWN**.

### Other relevant platforms

| Platform | Verified relevance and limitation |
|---|---|
| **FOIS — Freight Operations Information System** | CRIS describes freight operational/commercial information and tracking. Its TMS means **Terminal** Management System, not Track Management System. Public access to a planning-grade freight forecast was not established. [S10] |
| **NTES — National Train Enquiry System** | Public passenger running/enquiry service; useful reference, not a full controller occupation feed. [S11] |
| **ICMS — Integrated Coaching Management System** | CRIS describes coaching information, detention/failure reporting and exchanges with COA and other systems. Relevant historical information may exist internally; public task-level extraction is unverified. [S12] |
| **SATSaNG — Software Aided Train Scheduling and Network Governance** | Railway timetabling software identified in CRIS's project directory and the IIT Bombay/railway timetabling account. Exact current optimization modules and external interfaces need confirmation. [S13][S28] |
| **RailSys** | A railway simulation/timetabling product. Its documented historical use with MRVC in the CAG exercise is not evidence of universal current deployment. [S02][S29] |
| **PRAVAH** | Official 2022 project report documents an API integration platform: internal API infrastructure exists. It does not establish open access to the five systems above. [S14] |
| **RBS** | A mirrored 2026 SMMS newsletter describes a Rolling Block System and integrations. Treat this as a document claim pending official confirmation; do not confuse similarly abbreviated CRIS projects. [S16] |

> **PPT TAKEAWAY — The relevant gap is not “Railways has no digital coordination.”**  
> • Existing products already manage maintenance and operating information.  
> • Complete current optimizer capability and accessible interfaces remain unverified.  
> **Visual:** capability matrix with “documented” and “unknown,” avoiding unsupported red crosses.  
> **Sources:** [CRIS product pages][S05], [S07], [S08]; [BDMS mirrored manual][S09].

## 7. What Indian Railways Already Does Well

“Does well” here identifies capabilities and institutional controls, not a measured nationwide performance score.

| Category | Evidence-based assessment | Implication for NIRVIKALP |
|---|---|---|
| A — Established mechanisms | **VERIFIED:** departmental asset information, operational charting and formal planning/approval mechanisms exist [S03][S05][S06][S07][S08] | Preserve ownership and consume their outputs |
| B — Partially evidenced integration | **STRONGLY SUPPORTED:** BDMS documentation describes joint visibility; broader integration claims have uneven public provenance [S09][S16] | Do not sell a shared dashboard as entirely new |
| C — Explicit improvement target | **VERIFIED:** SIH asks for improved coordinated scheduling [S01] | Show decision quality, not merely a connected screen |
| D — Performance unknown | **UNKNOWN:** current joint-optimizer coverage, plan adoption, baseline delay and compatibility rates | Request local evidence before claiming a performance gap |

**INFERRED:** experienced planners can identify constraints missing from a simplified dataset. Their participation is part of model validation, not an obstacle to automation. Recorded reasons for overrides can reveal missing rules or misunderstood priorities. An optimizer finding no improvement can be a valid result if the baseline is already strong.

> **PPT TAKEAWAY — Build on operating expertise and existing records.**  
> • Documented capabilities should be credited.  
> • Product presence does not measure planning effectiveness.  
> **Visual:** established capabilities beneath a proposed comparison/explanation layer.  
> **Sources:** [Board procedure][S03]; [CRIS COA][S08]; report's evaluation interpretation.

## 8. What Problem Still Remains

**INFERRED FROM PS:** the unresolved research problem is selecting good combinations and timings when many legitimate needs compete for constrained access. Connecting records is necessary, but does not itself choose a schedule. [S01]

Four separable questions should guide the investigation:

1. **Can the inputs be joined correctly?** A track kilometre, signalling route and electrical section may describe overlapping but different areas.
2. **Which choices are feasible?** Timing alone is insufficient if crews, protection, isolation or dependencies conflict.
3. **Which feasible choice is preferable?** Fewer occupation minutes can be a poor plan if important work is left overdue.
4. **Can planners act on the explanation?** The output should identify missing information and a specific reason for rejection, not only a score.

These are proposed research questions, not claims that existing products lack each function. The exact production gap must be tested with a Railway SME and current BDMS/COA demonstration. The PS is evidence of an improvement request; it is not a feature specification of every existing platform.

> **PPT TAKEAWAY — The testable opportunity is better constrained choices.**  
> • Data joins and schedule selection are different tasks.  
> • A useful plan must explain exclusions and trade-offs.  
> **Visual:** many demands → feasible alternatives → preferred proposal.  
> **Source:** [SIH26027][S01]; **INFERRED** research framing.

## 9. CAG Evidence — Fully Verified

The original report text was inspected directly. Page numbers below are **printed pages**, not browser PDF indices. The condensed evidence register keeps historical facts together. **VERIFIED historical findings**, not 2026 measurements. [S02]

| Evidence | Scope / locator |
|---|---|
| Combined blocks **2.2%**; remainder **97.8%** separately availed | March 2019; 11 zones; pp.30–31, §2.1.8.5(a)(vii), footnote 43 |
| **240 minutes or twice 150**; Ministry later cites **3 hours** | p.33, §2.1.8.5(c)(i); November 2021 reply |
| **12 trains / seven UP corridors** | Prayagraj; p.34, §2.1.8.5(c)(ii) |
| **1,905 overruns; 4,659 trains delayed; 38–103 minutes** reported average overrun range | 2018–19; PRYJ, DHN, DDU, DNR, HWH, ASN; p.34, (iii) |
| **12,466 simulated conflicts; 244 train pairs** | July 2019 WTT, NDLS–HWH, six divisions; p.50 |
| **172% reported utilization** | Kanpur–Juhi West, 2019–20; p.55 |
| **33–91 simulated free paths** | Maripat–Block Hut K, 116 DOWN/117 UP trains; pp.55–56, Table 2.17, without maintenance block |
| Freight paths often absent from WTT; **97** timetabled goods trains introduced | p.20, §2.1.8.3; October 2020 initiative |

The named 11-zone sample is NCR, ECR, NR, ER, SECR, SER, SWR, ECOR, NWR, NEFR and SCR. The original terms include “in isolation” and “average time of block bursting.” Ministry and audit disputed simulation assumptions; read pp.48–49 alongside results. [S02]

### What these observations can and cannot establish

The following is **INFERRED statistical and modelling interpretation**, not additional CAG findings:

| Claim under review | Legitimate use | Invalid extension | Safe presentation decision |
|---|---|---|---|
| Combined share | Historical motivation for investigating coordination | Treating the complement as safely combinable or avoidable work | Use only with the complete sample/date label above |
| Corridor duration | Evidence of the policy/context discussed in that audit | One universal present-day hard constraint | Do not encode until current applicable order is obtained |
| Overrun counts | Demonstrates the kind of outcome a planner should track | Learning a duration distribution from aggregate averages | Historical evidence only; obtain individual execution records |
| Train delays | Supports asking about operating consequences | Assuming every delayed train would be saved by this product | No claimed NIRVIKALP impact |
| Simulated WTT conflicts | Motivates conflict analysis | Calling simulated conflicts accidents or actual unsafe grants | Label as model findings |
| Capacity comparisons | Shows why assumptions and denominator matter | Claiming universally free capacity or guaranteeing extra trains | Explain modelling scope and dispute |
| Freight observation | Motivates careful treatment of goods traffic | Claiming no current forecasting or freight information exists | Pair with current FOIS/COA evidence |

The distinction matters mathematically: a percentage of recorded blocks does not reveal how many jobs had overlapping locations, deadlines, protection requirements and resources. Without that eligibility denominator, a target combined-block percentage is arbitrary. Likewise, reported aggregate averages do not describe the tails or joint dependence of individual work durations.

> **PPT TAKEAWAY — Historical audit evidence is motivation, not a current baseline.**  
> • Preserve the register's sample, date and unit.  
> • Do not infer compatibility or product savings from aggregate statistics.  
> **Visual:** evidence card with a prominent historical-date label, not a “wasted maintenance” pie chart.  
> **Source:** [CAG Report 22/2021, Chapter 2][S02], locators above; analytical interpretation.

## 10. 2021 → 2026: What Has Changed

| Date | Evidence / confidence | What changes in the story |
|---|---|---|
| 2020 exercise, later published account | **VERIFIED:** IIT Bombay/railway authors describe simulation-assisted timetable work and interaction with SATSaNG [S28] | Optimization and simulation are not new to Indian railway planning |
| 2021 audit / 2022 publication | Historical evidence in Section 9 [S02] | A dated diagnosis must not freeze the present |
| April 2022 | **VERIFIED:** official IT progress report lists PRAVAH with 102 APIs and 310 endpoints [S14, §15.1] | “Railways has no APIs” is untenable; public entitlement is separate |
| 29 August 2023 | **VERIFIED:** rolling-block joint procedure [S03] | Current-process comparisons must include coordination |
| November–December 2023 | **VERIFIED:** PIB reports notification of rolling planning up to 52 weeks; IRICEN publishes an implementation account [S17][S04] | Longer-horizon planning is already policy/practice, not a NIRVIKALP invention |
| 2024–2025 | **VERIFIED:** IRPWM-2024 has a Board correction issued August 2025 [S18] | An older manual cannot automatically supply current constraints |
| January–March 2026 document | **STRONGLY SUPPORTED document claim:** mirrored SMMS newsletter describes RBS-related integration and also cautions that modules are not all launched [S16] | Investigate current deployment; do not generalize the claimed roadmap |
| March 2026 | **VERIFIED:** Ministry release references rolling blocks and ongoing operational monitoring [S19] | The planning environment has continued evolving |
| September 2026 research cut-off | **VERIFIED:** official SIH listing still frames an improvement task [S01] | Validate a present need with present users |

**INFERRED:** the “next intelligence layer” hypothesis fits the combination of an improvement request and established digitized processes. It is not proof that no such intelligence already exists internally. No current official public nationwide combined-block rate or complete BDMS optimizer specification was located.

**Conflict resolution:** the 2023 Board procedure's phased 26-week programme and the later announcement of up to 52 weeks refer to different dated policy statements. Neither changes the PS's required weekly/monthly outputs into a demand that a hackathon team optimize a full year in detail.

> **PPT TAKEAWAY — Evaluate the 2026 problem against the evolved process.**  
> • Policy and digital systems have changed since the audit.  
> • Public announcements do not prove uniform implementation.  
> **Visual:** dated evidence timeline with policy, product and rollout claims separated.  
> **Sources:** [PRAVAH][S14], [rolling-block procedure][S03], [PIB][S17], [2026 update][S19].

## 11. Available Government Data, APIs and Missing Data

### Access findings and their limits

Sources searched included official CRIS product/directory pages, Railway Board/railway portals, IRCEP-linked services, data.gov.in, Parliament, PIB, manuals and RDSO-related results. No restricted operational feed was accessed. A login page is not a documented API. An announced interface is not permission to consume it. An inaccessible website is not proof the underlying data does not exist.

For every operational input marked **restricted/unverified** below: **“No official public API located during this research.”** No endpoint, payload, authentication method or refresh rate is invented. A railway-approved export remains a possible integration route; its availability is **UNKNOWN**.

### Data availability matrix

**V = VERIFIED public content; U = UNKNOWN operational access; L = located lead not independently inspected.** Format, refresh and permissions are part of the table rather than assumed from product names.

| Required input / owner | Access, URL and format | Fields actually established / useful role | Refresh, authentication, rights | Defensible prototype substitute |
|---|---|---|---|---|
| Station/network topology / railway engineering and operating owners | **U** complete planning topology; CRIS directory links relevant systems [S13] | Full routes, track circuits, junction conflicts and electrical mapping not obtained | Operational access/refresh/license unknown | Explicitly fictional A–B–C network; SME-reviewed topology later |
| Section distances / Central Railway | **V** historical PDF [S20] | Section, length, gauge, line configuration, traction, working system | 2021–22 statement; public read; bulk reuse terms not established | Manually referenced historical examples, labelled dated |
| Passenger schedules / Indian Railways | **V** public enquiry page [S21] | Train/station identifiers, arrival/departure, days, distance; reserved-service enquiry scope | Query interface; refresh SLA and bulk/API rights unknown | Small attributed reference set or fully synthetic paths |
| Open timetable catalog / data.gov.in | **L** catalog URL [S22]; payload not retrieved | Do not claim verified rows, schema, API or freshness | Catalog licence and latest resource terms not inspected | Do not depend on it until resource validation |
| Working Time Table / zonal operating authorities | **U** authoritative current chosen-corridor WTT not obtained | Required passing times, operating dates and restrictions not supplied by public schedule alone | Version/date and authorized access needed | Manually created operating timetable, labelled synthetic |
| Running positions / COA, NTES | **V** product descriptions; **U** planning feed [S08][S11] | Public enquiry is not full section/route occupation | Exact operational latency, history, credentials unknown | Event replay with declared timestamps |
| Freight movements / FOIS and Control Office | **V** system purpose; **U** forecast/export [S10] | Required forecast paths, issue times and uncertainty unavailable | No public forecast contract established | Three explicitly assumed traffic scenarios |
| Line capacity / zonal railways, Parliament | **V** PDFs [S20][S23] | Historical section capacities, traffic and utilization summaries | Dated annual/answer snapshots; public read; not current calendars | Context and reasonableness checks only |
| Maintenance defects / TMS, SMMS, TDMS owners | **U** records; **V** documented system functions [S05][S06][S07] | No task-level defect dataset obtained | Railway permission, schema, update cadence unknown | Synthetic records with explicit severity assumptions |
| Track assets / TMS | **U** inventory [S05] | Asset/inspection categories documented; production IDs not obtained | Restricted access contract unknown | Fictional asset master with consistent location IDs |
| Signal assets / SMMS | **U** inventory [S06] | Asset maintenance/failure function documented; route map missing | Same limitation | Fictional apparatus and separately specified route impacts |
| OHE assets / TDMS | **U** inventory [S07] | Asset/inspection function documented; isolation map missing | Same limitation | Fictional electrical sections; no inferred real isolation |
| Block demands / BDMS | **U** records; PS/manual describe process [S01][S09] | Demand lifecycle relevant; exact export schema unknown | Role permissions/refresh unknown | Mock import contract, explicitly not a CRIS API replica |
| Approved/granted blocks / Operating, BDMS/COA | **U** current calendar [S03][S08] | Demand, programme, grant and actual occupation must be distinguishable | Live status authority unknown | Synthetic lifecycle with separate state fields |
| Corridor windows / Operating | **U** selected corridor calendar [S03] | Start/end, scope, conditions, applicable dates needed | WTT/programme revisions; exact cadence unknown | Authored scenarios with versioned windows |
| Historical train delays / ICMS/COA | **U** event-level export; **V** reporting capability [S12] | No linked maintenance→delay causal dataset obtained | Access, attribution quality and retention unknown | Simulated delays only if a traffic model is declared |
| Failures / departmental systems | **U** event records [S05][S06][S07] | Asset, time, cause, recovery/exposure needed for risk modelling | Labels and censoring unknown | Rule scenarios; no trained failure-risk claim |
| Work duration / block execution owners | **U** individual execution data; recording prescribed [S03] | Need preparation, productive work, restoration and release times | Recording consistency and access unknown | Scenario intervals; aggregate audit averages are not calibration |
| Crews, machines, materials / departmental owners | **U** roster/readiness records | Skills, shift, travel, maintenance and availability needed | Staff-data permissions and update frequency unknown | Fictional qualified crews and machine calendars |
| Interfaces / CRIS PRAVAH | **V** historical platform counts; **U** relevant endpoint contracts [S14] | Establishes API infrastructure, not open maintenance schemas | Partner onboarding/authentication unknown | File-based adapter specification pending authorized access |
| Safety/rule documents / Railway Board, zones, RDSO | **V** selected manuals/orders [S15][S18] | Text rules and version references; no machine-readable complete rule set | Document-specific currency; amendment tracking essential | Traceable subset with explicit unknowns, not full certification |

### What to do with public information

**INFERRED:** public documents can anchor terminology, data shapes and dated examples. They generally cannot validate a real division's current plan. A static capacity figure is not a promise of a particular free interval. A passenger stop schedule omits movements and restrictions needed for safe planning.

For a credible demonstration, maintain a data card stating: creator, generation method, date, fictional/real status, units, assumptions, missing constraints and intended use. Keep public reference facts separate from invented operational records. Public visibility does not establish a bulk extraction licence; obtain the resource-specific terms before redistribution or automated use.

A mock connector should demonstrate validation, mapping and lineage against a **proposed** contract. It should never display “live TMS/COA connected” unless an authorized connection has actually been tested.

> **PPT TAKEAWAY — Public context is available; planning-grade operational access remains unconfirmed.**  
> • Passenger enquiries and historical capacity tables have limited roles.  
> • Internal API infrastructure does not establish public entitlement.  
> **Visual:** public reference / authorized operational / synthetic demonstration data lanes.  
> **Sources:** [schedule enquiry][S21], [capacity PDF][S20], [PRAVAH][S14]; access findings above.

## 12. Common Data Model Needed for SIH26027

This is a **conceptual proposal**, not a claimed CRIS schema. **V-field** means a corresponding concept appears in a real document, not that this exact field name exists in an API. **I-field** means inferred planning necessity. **O-field** means optional demonstration metadata. Source provenance must attach to values, not merely to a table name.

| Entity | Proposed fields, individually classified | Derivation / meaning |
|---|---|---|
| MaintenanceTask | `task_id` I; `department` V; `source_system` I; `source_record_id` I; `asset_id` V; `work_description` V; `task_type` I; `defect_status` V; `severity_code` I; `severity_authority` I; `due_at` I; `earliest_start` I | Department/asset/maintenance concepts [S01][S05][S06][S07]; an exact severity scale is not publicly established |
| TaskLocation | `section_endpoints` V; `km_from` V; `km_to` V; `line_designation` V; `track_resource_ids` I; `signal_route_ids` I; `electrical_section_ids` V; `location_mapping_version` I | Electrical block form includes location/line/section concepts [S15, E-TR-D-1]; common crosswalk is proposed |
| WorkEstimate | `requested_duration` V; `setup_minutes` I; `productive_minutes` I; `restoration_minutes` I; `estimate_method` I; `estimate_version` I; `scenario_durations` O; `learned_quantiles` O | Duration recorded in planning process [S03]; decomposition and uncertainty proposed |
| TaskRequirements | `traffic_restriction` I; `power_block_required` V; `disconnection_required` V; `resource_demands` I; `predecessors` I; `readiness_status` I; `compatibility_evidence_ids` I; `split_allowed` I | Access concepts [S15]; readiness principle [S03]; job-specific compatibility not assumed |
| TrainPath | `train_id` V; `operating_date` I; `traffic_type` V; `resource_sequence` I; `entry_at` I; `exit_at` I; `traction_type` I; `forecast_issued_at` I; `scenario_id` O; `authorized_priority` I | COA/FOIS train concepts [S08][S10]; detailed common path representation proposed |
| BlockWindow | `window_id` I; `section` V; `line` V; `start_at` V; `end_at` V; `block_type` V; `electrical_scope` V; `status` I; `source_authority` I; `valid_from/to` I; `conditions` I | Location/time/type concepts from real block form [S15]; proposed lifecycle prevents draft/grant confusion |
| Resource | `resource_id` I; `resource_type` I; `skills` I; `quantity` I; `calendar` I; `base_location` I; `travel_time` I; `ready_at` I | Resource readiness requirement [S03]; exact roster schema unknown |
| CompatibilityRule | `rule_id` I; `scope` I; `version` I; `effective_dates` I; `source_document` I; `decision` I; `approved_by_role` I; `reason` I | Three-valued result: allowed / prohibited / unknown; not a similarity score |
| WorkPackage | `package_id` I; `task_ids` I; `affected_resources` I; `task_sequence` I; `occupation_start/end` I; `validation_evidence` I | A proposed scheduling construct; not assumed native to BDMS |
| PlanVersion | `plan_id` I; `horizon` V; `input_snapshot_id` I; `parent_monthly_plan` I; `locked_assignments` I; `solver_status` O; `objective_breakdown` I; `review_status` I | Weekly/monthly requirement [S01]; reproducibility fields proposed |
| ExecutionRecord | `demand_duration` V; `granted_duration` V; `actual_duration` V; `output_achieved` V; `actual_release_at` I; `delay_reason` I; `work_completed` I | First four concepts explicitly recorded under Board procedure [S03]; additional fields proposed |

**INFERRED validation contract:** reject negative durations, missing time zones, inconsistent kilometre order, unknown location mappings, stale window versions, duplicate task IDs and impossible dependency cycles. Missing criticality or compatibility should remain unknown; neither defaults to “low risk” or “compatible.” Use timezone-aware dates spanning midnight, not just a time-of-day string. Keep cancelled and superseded records available for audit while excluding them from the current input snapshot.

> **PPT TAKEAWAY — The common model must preserve source meaning and uncertainty.**  
> • Proposed field names are not verified API fields.  
> • Location, time, status and provenance are essential joins.  
> **Visual:** task–asset–location–window–path–resource relationship diagram.  
> **Sources:** [PS][S01], [Board records requirement][S03], [G&SR form E-TR-D-1][S15]; proposed schema.

## 13. Weekly vs Monthly Planning

Both outputs are **VERIFIED requirements**. Their detailed decision split below is **INFERRED**, to be tested with planners rather than presented as a universal railway rule. [S01]

| Dimension | Monthly proposal | Weekly refinement |
|---|---|---|
| Main question | Which work belongs in which week/opportunity? | Which exact feasible start, sequence and resources? |
| Task granularity | Backlog, due work, major packages, provisional grouping | Ready jobs with validated quantities and prerequisites |
| Traffic information | Provisional corridor capacity and scenario ranges | Latest authorized planning inputs and detailed paths |
| Resources | Coarse crew/machine capacity and mobilization | Named or precisely categorized availability and travel |
| Commitments | Reservations and work due within the month | Preserve approved/locked work; identify exceptions |
| Output | Allocation, deferred work, capacity pressure and assumptions | Detailed proposal, conflicts, readiness and unresolved approvals |
| Quality test | Avoid reserving more capacity than can be delivered | Avoid silently invalidating the parent plan |

A suggested hierarchy is monthly allocation → weekly detailed solve → explicit reconciliation. If weekly detail proves a monthly allocation infeasible, update the parent plan visibly; do not hide the inconsistency. Monthly feasibility should not be claimed if it was checked only against coarse aggregate hours.

Near-real-time replanning is **optional** relative to the PS. If investigated later, preserve completed and protected commitments; show the changed inputs and affected decisions. A sophisticated disruption demo is not a substitute for the two mandatory horizons.

> **PPT TAKEAWAY — Monthly planning reserves opportunity; weekly planning tests executable detail.**  
> • Both outputs are required.  
> • Their consistency must be checked explicitly.  
> **Visual:** one monthly allocation expanded into a weekly schedule.  
> **Source:** [SIH26027][S01]; proposed horizon decomposition.

## 14. True Optimization Formulation

### The actual decision

**INFERRED formulation:** a multi-department, resource-constrained maintenance scheduling problem with optional compatible work packages, train-path exclusions, deadlines and uncertain inputs. The first defensible scope is to schedule maintenance around supplied traffic assumptions. Jointly changing the train timetable is a materially larger problem and requires separate authorization and modelling.

Published work confirms that integrated train/maintenance scheduling is an established research area. Cillie and Bekker present a microscopic mixed-integer model; Zhang and colleagues model overnight train/maintenance interaction and explicitly discuss electrical-section geography and simplifying assumptions. Neither validates a model for Indian mixed-traffic operations. [S24][S25] The maintenance-planning review provides a broader taxonomy rather than one universally best algorithm. [S26]

### Sets, inputs and decisions

All notation here is a **proposed prototype model**, not an official railway formulation.

| Symbol | Meaning |
|---|---|
| I, M ⊆ I | Tasks; subset declared mandatory within the horizon |
| R, K | Exclusive infrastructure resources; crews/machines and other capacity resources |
| W, T | Candidate access windows; discrete time intervals |
| P | Candidate validated work packages, including singleton tasks |
| Ω | Explicit duration/traffic scenarios, if uncertainty is tested |
| I(p) | Tasks included in package p |
| a_i, d_i | Earliest permitted start and due date of task i |
| q_ik, C_kt | Task i's demand for capacity resource k, and that resource's capacity at time t |
| O_rtω | Supplied train occupation/forbidden time on resource r in scenario ω |
| E | Precedence pairs (i,j) |
| H_p | Internal work/protection/restoration sequence of package p |
| y_p ∈ {0,1} | Whether package p is selected |
| x_i ∈ {0,1} | Whether task i is scheduled |
| s_i, e_i | Task start and completion times |
| z_pw ∈ {0,1} | Assignment of selected package p to window w |
| b_rt ∈ {0,1} | Whether resource r is unavailable due to maintenance at time t |
| u_i ≥ 0 | Tardiness where deferral beyond a non-mandatory deadline is permitted |

Crew/machine capacity and exclusive infrastructure occupation have separate resource dimensions. Keeping these concepts distinct prevents an artificial shared “capacity” from allowing trains through protected worksites. Optional intervals and their time constraints are activated only when the corresponding work is selected.

### Hard constraints

1. **Task coverage:** Σ[p:i∈I(p)] y_p = x_i. A task cannot be counted twice. For i∈M, x_i=1. Unscheduled optional tasks remain visible with reasons.
2. **Window assignment:** Σ_w z_pw = y_p. Selected package occupation, including preparation and restoration allowances, must lie within a permissible window.
3. **Time consistency:** e_i=s_i+duration_i for indivisible work; s_i≥a_i. Mandatory deadlines are hard. Split work needs an explicit, authorized split model.
4. **Precedence:** e_i≤s_j for selected dependent work where (i,j)∈E, together with prerequisite-selection logic. Concurrent work cannot violate testing or restoration order.
5. **Traffic exclusion:** b_rt + O_rtω ≤ 1 on every mutually exclusive resource and relevant scenario. Headways, route locking and applicable margins belong in the validated occupation representation; no universal minute buffer is invented.
6. **Shared resources:** Σ_i q_ik·active_it ≤ C_kt, with setup, travel and shift constraints where applicable. The same machine cannot serve distant jobs simultaneously. The activity indicator is linked to the selected task interval; package occupation similarly defines b_rt as the union of its affected-resource intervals.
7. **Compatibility:** select a combined package only when its required compatibility evidence is complete and applicable. Unknown compatibility is not permission. Whole-package effects must be checked; pairwise checks can miss a three-way resource or restoration conflict.
8. **Readiness and authority:** exclude unready work from an executable proposal or explicitly retain it as conditional. Keep planning states separate from operational grant states.
9. **Commitments:** lock the assignments that authorized staff declare fixed. An emergency exception must be made visible and handled through the proper process.
10. **Boundary consistency:** account for trains/resources crossing the model boundary, preceding occupation and work finishing beyond midnight or the horizon.

The simultaneous-work duration is **not automatically the sum or the maximum** of individual durations. It follows from the validated internal sequence and shared setup/restoration. For example, under an explicitly fictional compatible scenario, two 60-minute jobs sharing 20 minutes of preparation and 10 minutes of restoration might occupy 90 minutes; if they must be sequential, occupation is 150 minutes. The example proves arithmetic only, not railway compatibility.

### Objectives and soft preferences

Use a declared hierarchy rather than an unexplained weighted “AI score”:

1. Satisfy hard feasibility and mandatory work. If impossible, return an infeasibility explanation.
2. Maximize completion of authorized high-priority work and minimize permitted lateness.
3. Minimize weighted union occupation: D = Σ_r v_r·Σ_t Δt·b_rt. The weights v_r are declared assumptions or approved values.
4. Minimize a specified train-impact proxy or simulated delay, only within the model's valid scope.
5. Minimize changes to previous commitments, unnecessary mobilization and other accepted preferences.

Lexicographic optimization means a lower-level gain cannot compensate for a higher-level loss. If alternative trade-offs are desired, expose a Pareto comparison rather than silently changing priorities. Safety constraints never become small penalties that the optimizer can pay to violate.

### Method comparison

Assessments below are **INFERRED engineering judgments** informed by the cited literature and solver documentation. Runtime and scale must be measured on NIRVIKALP instances, not promised from another paper's experiment.

| Method | Suitability and inputs | Explainability / safety | Runtime, scale and prototype judgment |
|---|---|---|---|
| MILP | Strong for linear selection, allocation and timing; needs explicit coefficients | Constraints, bounds and infeasibility analysis can be inspected; correctness still depends on model | Time-indexed formulations may grow quickly; good candidate and benchmark |
| Constraint Programming | Natural for intervals, alternatives, sequencing and cumulative resources | Constraints map well to scheduling concepts; not a safety certificate | Often practical for scheduling; formulation-dependent |
| CP-SAT | Integer CP/SAT-based search with scheduling support; discrete time representation | Report FEASIBLE versus OPTIMAL versus INFEASIBLE/UNKNOWN honestly [S27] | Strong first candidate for a bounded case; no guaranteed national real-time solve |
| Genetic algorithms | Flexible search over encodings; no training labels required | Must repair/reject infeasible candidates and independently validate output | Could help large search; extra tuning and weak bounds make it optional |
| Other metaheuristics | Useful constructive/local search; can warm-start exact methods | Explain individual moves, not a false optimality claim | A simple informed heuristic is essential as baseline |
| Reinforcement learning | Requires a credible environment, states, actions, rewards and substantial evaluation | Learned policy must remain constrained; reward design can hide unsafe trade-offs | Poor first choice without validated simulator and training evidence |
| Multi-agent methods | May represent departments, local decisions and negotiation | Local objectives can conflict with global feasibility; coordination proof needed | Added complexity; organizational analogy alone is insufficient |
| Robust optimization | Protect against declared duration/traffic uncertainty sets | Conservative guarantees hold only within the uncertainty model | Scenario size/conservatism trade-off; useful optional extension |
| Stochastic optimization | Optimize expected/risk-sensitive outcomes across scenarios | Requires defensible probabilities and out-of-sample validation | Do not assign invented probabilities and call them empirical |

**Recommendation — INFERRED:** compare coordinated greedy scheduling with one transparent CP-SAT or MILP formulation, plus an independent feasibility checker. Start with deterministic, declared inputs. Add bounded uncertainty experiments only after correctness and baseline quality are established. An exact solver's model proof is conditional on its inputs and constraints; it is not field safety approval.

> **PPT TAKEAWAY — Optimize useful work under explicit constraints, not the combined-block percentage.**  
> • Mandatory work and safety are feasibility conditions.  
> • Solver status and objective trade-offs must remain visible.  
> **Visual:** feasible region with alternative plans and their objective breakdown.  
> **Sources:** [maintenance MILP][S24], [joint scheduling model][S25], [CP-SAT documentation][S27]; proposed formulation.

## 15. Where AI/ML Is Actually Useful

**Research conclusion — INFERRED:** optimization is justified now as a method to investigate. Railway predictive models are conditional on obtaining suitable historical records. Synthetic labels generated by a rule can test a training pipeline, but performance against those labels measures imitation of the generator, not real railway prediction.

| Use case | Required real evidence | Honest approach now | Integration and uncertainty |
|---|---|---|---|
| Maintenance priority | Authorized severity/deadlines and outcome-informed policy | Transparent rule hierarchy with override provenance | Determines objective tiers; never learns away mandatory obligations |
| Failure risk | Asset exposure, inspections, failures, maintenance interventions and censoring | Do not claim a trained railway risk model | Later calibrated probabilities; evaluate across asset/time boundaries |
| Task duration | Comparable work quantities, resources, site conditions, preparation/restoration and actual times | Declared intervals or SME estimates | Later quantiles/scenarios; track coverage and decision impact |
| Overrun probability | Granted duration, actual occupation and reasons, including incomplete/cancelled jobs | Scenario stress tests | Probability needs calibration, not only discrimination |
| Freight demand/path forecasting | Forecast issue-time snapshots and subsequent movements | Consume supplied forecast; synthetic uncertainty scenarios if absent | Preserve forecast vintage; do not leak future actual running |
| Disruption/delay prediction | Network interactions, traffic, restrictions and linked outcomes | Report conflict/occupation proxies; simulate only with declared assumptions | Distinguish primary and propagated delay |
| Data anomaly detection | Validated normal records and known error types | Schema checks, duplicate detection and range validation | Flag for review; do not auto-correct safety-critical locations |
| Natural-language explanation | Structured reasons from the model | Template-based explanation is sufficient | Optional language model paraphrases evidence; cannot invent rules |

### XGBoost and the proposed P50/P80/P95 claims

The cited 2016 XGBoost paper establishes a general machine-learning method; it does not validate railway maintenance duration prediction. [S31] Quantile labels are meaningful only when their empirical coverage is demonstrated on unseen, relevant records. P80 means a claimed conditional 80th percentile, not “80% model accuracy.”

**INFERRED validation plan if authorized history becomes available:** compare against median-by-task-type and simple regression baselines; split by time and hold out relevant locations; report quantile loss, interval coverage and width, severe underestimation frequency, and the resulting schedule outcomes. Prevent leakage from actual release times, final work quantities unavailable at planning time, or repeated records of the same block.

The maximum of separate P95 task estimates is not automatically a package P95. Shared weather, resource readiness and restoration can create correlated overruns. Preserve a scenario or dependence model, or explicitly state that the uncertainty bound is a conservative assumption.

**Do not use:** learned safety permissions, unsupported accident-prevention claims, fabricated 98% “AI accuracy,” synthetic-trained models presented as operationally calibrated, or an LLM issuing block authority.

> **PPT TAKEAWAY — A prediction claim needs real labels and out-of-sample evidence.**  
> • Synthetic data can test behavior, not establish field accuracy.  
> • Duration uncertainty must be propagated into schedule evaluation.  
> **Visual:** data gate → baseline predictor → validation → scheduling experiment.  
> **Source:** [XGBoost paper][S31]; proposed validation methodology, not railway performance evidence.

## 16. Safety & Human Approval

The rules reviewed establish examples of applicable control principles. They are **not a complete current safety specification** for any proposed demonstration corridor. The Eastern Railway G&SR edition inspected is dated 2019; current amendments and local instructions must be obtained before operational use. IRPWM-2024 amendments demonstrate why version control matters. [S15][S18]

### Verified anchors

| Verified concept | Exact source anchor | Proposed consequence, not an operating instruction |
|---|---|---|
| Signalling interference/disconnection requires prescribed permission and restoration procedure | [S15], GR/SR 3.51, printed pp.44–45 | Store affected apparatus/routes and authorization status |
| Track-machine work has prescribed clearance/restoration communications | [S15], SR 4.65 provisions, printed pp.126–130 | Planned finish is not proof of release |
| A weekly power-block programme does not replace actual power-block/PTW requirements | [S15], Chapter XVII, SR 17.04 provisions | Keep programme, isolation and permit lifecycle distinct |
| Electrical emergency and restoration communications involve competent operating/electrical roles | [S15], Chapter XVII | Escalate; do not automatically energize or extend authority |
| Manual amendments alter applicable rule text | [S18], correction slip dated 18 August 2025 | Attach rule version and applicability |

### Unknowns that must block a “validated for execution” claim

**NOT PUBLICLY VERIFIED / REQUIRES RAILWAY SME CONFIRMATION:** applicable adjacent-line restrictions; safe separations between simultaneous works; machinery movement/protection; exact isolation boundaries; return-current/earthing arrangements; route locking effects; headway and clearance margins; speed restrictions after work; authorized competence; local grant/extension/release messages; exceptional working; emergency delegation; current correction slips.

**INFERRED validation states:** (1) input complete, (2) feasible under modelled rules, (3) reviewed by authorized personnel, and (4) operationally granted are distinct. A green optimizer result can establish only the second under its stated assumptions. An independent checker should reject any missing required rule or contradiction; it does not certify that omitted rules do not exist.

For a research demonstration, use “feasible under declared model constraints” and show unresolved requirements prominently. Human approval is necessary, but does not magically repair an incomplete model; the missing information must be identifiable.

> **PPT TAKEAWAY — A feasible proposal is not a railway authority to work.**  
> • Rule versions and local applicability are part of the evidence.  
> • Unknown protection requirements remain unresolved.  
> **Visual:** separate planning-validation and operational-authorization gates.  
> **Sources:** [G&SR cited provisions][S15], [IRPWM correction][S18].

## 17. Root Causes Beyond “Data Silos”

These are **candidate causes**, not a quantified causal study. **V** marks a directly documented issue/requirement; **I** marks a plausible hypothesis that needs local measurement.

| Cause / evidence | Operational consequence | Explicit PS coverage? | NIRVIKALP treatment / feasibility |
|---|---|---|---|
| Separate departmental information — V [S01] | Joins and priorities must be reconciled | Yes | Common model; feasible with synthetic/authorized inputs |
| Different location semantics — I [S05][S06][S07][S15] | False matches or missed shared scope | Implicit | Explicit mapping and ambiguity rejection; feasible |
| Different horizons — I; two outputs V [S01] | Coarse allocation fails detailed feasibility | Yes, horizons | Parent/child reconciliation; feasible |
| Uncertain goods movements — I; forecast input V [S01] | A nominal gap may not persist | Input explicit | Scenario sensitivity; empirical probabilities conditional |
| Variable duration — I; historical overruns V, Section 9 | Restoration exceeds intended access | Indirect | Stress tests now; prediction later |
| Limited capacity and junction interactions — V [S20][S28] | Small timing changes affect many paths | Implicit | Bounded topology; no national claim |
| Emergency work — V [S03] | Planned commitments become impossible | Not explicit | Optional exception test; preserve operating authority |
| Resource/readiness constraints — V [S03] | A theoretically good window yields little work | Implicit | Crew/machine/readiness gates; feasible under assumptions |
| Dependencies and geographic incompatibility — I | Work cannot be freely bundled | Implicit | Explicit precedence and footprints; feasible |
| Safety incompatibility — I grounded in separate controls [S15] | Concurrent jobs require different protection | Implicit safety | SME-approved compatibility; incomplete rules remain a limit |
| Approval latency — I | A proposed opportunity expires | Not explicit | Measure timestamps before optimizing workflow |
| Late changes and plan churn — I | Mobilization and trust are disrupted | Not explicit | Optional stability objective |
| Local versus global priorities — I | Departmental benefit may consume scarce shared access | Coordination explicit | Common objective with owner-approved priority tiers |
| Inter-division boundaries — I | A locally feasible plan creates downstream conflict | Not explicit | Treat boundary reservations as inputs; defer network-wide solve |
| Trust/explanation — I; implementation account relevant [S28] | Users cannot assess or adopt the proposal | Not explicit | Constraint-linked reasons and review record |

### A five-whys investigation, not a pre-written verdict

**Hypothesis:** two nearby jobs use separate possessions. Why? They were not placed together. Why? Their useful windows did not overlap. Why? One lacked a ready machine or required a different isolation. Why? Readiness and protection were only resolved late. Why? The planning dataset did not expose those conditions early enough.

Every step requires interviews and timestamps. An equally valid outcome is that separate possessions were the safest and most economical choice. Start investigation with specific rejected/overrun examples, not the assumption that departmental staff failed to coordinate.

**Proposed data-flow audit:** source record → location mapping → urgency/readiness → request → reconciled programme → actual grant → execution → closure. At each transition measure missing fields, age, re-entry, status mismatch and delay. This can distinguish an integration problem from genuine capacity scarcity.

> **PPT TAKEAWAY — Diagnose the binding constraint before proposing the remedy.**  
> • Shared data alone cannot create a crew or a safe work window.  
> • Separate possessions can be the correct decision.  
> **Visual:** cause–constraint–decision chain for one concrete example.  
> **Sources:** [PS][S01], [readiness procedure][S03], [safety anchors][S15]; hypotheses labelled above.

## 18. Existing Solutions and Competitor Landscape

### Evidence standards

Official product documentation establishes documented functions. Papers establish published approaches under their own assumptions. Vendor pages establish advertised capabilities. GitHub READMEs establish public claims and common ideas, not correctness, deployment, SIH ranking or performance. No competitor code was executed or independently benchmarked during this research.

| Source / type | Observed positioning | What cannot be concluded |
|---|---|---|
| Existing railway platforms [S05][S06][S07][S08][S09][S10][S11][S12][S13][S14] | Maintenance records, control information, interfaces and planning workflows | Full current optimizer scope remains unknown |
| Cillie & Bekker, 2023 [S24] | Microscopic maintenance-window MILP with a South African case study | Runtime/results do not transfer directly to SIH instances |
| Zhang et al., 2025 [S25] | Joint overnight train/maintenance MILP; electrical-section modelling | Chinese HSR assumptions do not establish Indian compatibility rules |
| Sedghi et al., 2021 [S26] | Maintenance planning/scheduling taxonomy and research review | A review is not a production solution |
| RailSys Suite / RMCon [S29] | Advertised infrastructure, timetable, simulation and construction-planning capabilities | Not proof of every feature's deployment in Indian Railways |
| PODFlo / Network Rail-related publisher [S30] | Describes possession-delivery workflow, resource checks and phased deployment | Not a directly transferable Indian authorization workflow |
| Junction / public repository [S32] | Claims integrated/shadow planning, optimization, explainability and human review | Claims are unvalidated; no inferred adoption or safety assurance |
| RailOpt-AI / public repository [S33] | Claims XGBoost/SHAP, CP-SAT, weekly/monthly planning and assistance | Data provenance and railway deployment not independently established |
| Railway_Block_Planner / public repository [S34] | Describes a mock-data decision layer with scenarios, metrics and audit-oriented outputs | README is not evidence of measured improvement |

A verified, comparable archive of earlier SIH railway winners with detailed evaluated implementations was not established. This is a research limitation; the three repositories are not a complete census of competing teams, nor evidence of their official submission status.

### Feature/positioning matrix

**D** = documented; **C** = publisher/repository claim; **U** = unverified. The final column is a proposal, not a novelty claim.

| Capability | Railway systems/process | Academic/product prior art | Public projects | NIRVIKALP possibility |
|---|---|---|---|---|
| Asset/maintenance dashboard | D | Common presentation function | C | Supporting feature only |
| Priority scoring | D in maintenance monitoring; exact method varies | Established decision modelling | C | Transparent policy, not a differentiator alone |
| Gantt/control-style chart | Operational charting D | Scheduling visualization established | C | Evidence display only |
| OR-Tools / MILP | Exact current use U | Established solver methods | C | Implementation choice |
| Joint work suggestions | Joint planning D; suggestion algorithms U | D | C | Demonstrate validated eligibility and benefit |
| What-if analysis | Current scope U | Simulation D | C | Useful but not unique |
| Digital twin | Specific deployment U | Vendor capability C | C | Avoid term without fidelity/validation definition |
| Explainability | Human planning exists; software scope U | Constraint/model explanations possible | C | Trace every reason to data/rule evidence |
| Replanning | Operating regulation D; optimization scope U | Established research theme | C | Optional stable repair experiment |
| Missing-data-aware validation | Exact production scope U | Related robust/verification ideas exist | Not established by this limited review | Candidate positioning, uniqueness unproven |

**INFERRED conclusion:** “AI + CP-SAT + XGBoost + dashboard + what-if” is not defensible differentiation. A narrower, well-tested operational property may be persuasive, but a novelty claim needs deeper technical comparison and current railway feedback.

> **PPT TAKEAWAY — Common tools are not an innovation claim.**  
> • Public projects already describe much of the proposed feature list.  
> • Evidence quality and evaluated behavior are better grounds for positioning.  
> **Visual:** feature matrix separating claims from tested results.  
> **Sources:** [Junction][S32], [RailOpt-AI][S33], [Railway_Block_Planner][S34], [academic model][S24].

## 19. Potential NIRVIKALP White-Space Innovations

All five directions are **INFERRED candidates**. “Not located publicly” is not “absent” or “unique.” Novelty ratings refer to positioning potential in this limited comparison, not patentability or global originality.

| Direction | Problem, evidence and required inputs | Prototype proof / difficulty | Challenge and honest answer | Decision |
|---|---|---|---|---|
| **1. Evidence-aware package validation** | Ambiguous geography/rules can produce unjustified combinations. Need mapped footprints, permissions, dependencies, versioned compatibility evidence [S15] | Demonstrate allowed/prohibited/unknown outcomes and a whole-package checker; medium difficulty | “Who certified these rules?” Answer: demonstration rules are assumptions; production applicability needs competent railway validation | **INCLUDE** as bounded validation research |
| **2. Explain infeasibility and permitted repair** | A planner needs to know why urgent work cannot fit. Need tasks, constraints, alternatives and protected commitments | Show conflicting requirements and compare authorized changes, e.g. another crew or later optional work; medium/high | “Will you relax safety?” Answer: never; only explicitly permitted planning choices are explored | **INCLUDE** a small, inspectable version |
| **3. Monthly-to-weekly commitment consistency** | Two required horizons can contradict each other [S01]. Need parent allocations, detailed windows and locked decisions | Expose rejected allocations and trace revisions; medium | “Is this already in RBS?” Answer: current overlap is unknown; evaluate against the local process before claiming novelty | **INCLUDE** because it directly serves PS |
| **4. Duration/freight robustness frontier** | Nominal best plan may be fragile. Need declared scenarios initially; calibrated history later | Show occupation versus worst-case/quantile performance without invented probabilities; medium/high | “Are scenarios real?” Answer: synthetic stress tests prove conditional behavior only | **KEEP OPTIONAL** |
| **5. Readiness-aware opportunity selection** | A free window is wasted if resources/materials are not ready; policy already recognizes readiness [S03] | Exclude or flag unready jobs; compare scheduled work versus achievable work; medium | “Is a readiness checklist new?” Answer: no; investigate its integration into objective and feasibility | **INCLUDE BASIC GATE; optional predictive extension** |

### Comparative assessment

Ratings are **INFERRED**: H = high, M = medium, L = low. Data feasibility means demonstrability with declared synthetic cases; production access remains separate.

| Direction | Novelty confidence | Railway usefulness | Technical feasibility | Data feasibility | Demo value | Evidence strength for need | Integration difficulty |
|---|---|---:|---:|---:|---:|---|---:|
| Evidence-aware validation | Unproven | H | H for small rule set | H synthetic / L verified rules | H | Strong principle; local gap unknown | H |
| Infeasibility/repair | Unproven | H | M | H synthetic | H | Inferred user value | M–H |
| Horizon consistency | Unproven | H | H | H synthetic | H | Explicit two-horizon requirement | M |
| Robustness frontier | Established research; local differentiation unknown | H | M | M; calibration L | H | Uncertainty plausible; distribution unknown | H |
| Readiness selection | Low for checklist; optimization value untested | H | H | H synthetic / real L | M | Official readiness principle | M |

Recommended research combination: directions 1–3 plus a simple readiness condition. Evaluate direction 4 only if it does not weaken the evidence for core weekly/monthly scheduling. Avoid claiming that any of these replaces existing systems or is the first of its kind.

> **PPT TAKEAWAY — Investigate a narrow, measurable improvement before claiming uniqueness.**  
> • Constraint evidence and horizon consistency are testable.  
> • Their current production overlap still needs confirmation.  
> **Visual:** candidate directions mapped to PS relevance, evidence and feasibility.  
> **Sources:** [PS][S01], [Board readiness principle][S03], [safety anchors][S15]; research proposals above.

## 20. Feasibility Matrix

These are **INFERRED pre-development assessments**, not completed implementation results. GREEN means feasible to demonstrate honestly in a bounded synthetic setting; it does not imply deployment readiness.

| Capability | Data | Effort / algorithm | Rule/integration dependence | Compute / presentation / reliability | Verdict |
|---|---|---|---|---|---|
| Common schema and validation | Synthetic available | Low–medium | Real mapping later | Low compute; simple tables; repeatable | **GREEN** |
| Mock import with provenance | Authored contract | Low | Does not prove CRIS access | Low compute; reliable offline | **GREEN** |
| Deterministic bounded schedule | Synthetic tasks/windows | Medium | Explicit simplified constraints | Runtime must be measured; modest instance first | **GREEN** |
| Weekly/monthly consistency | Synthetic hierarchy | Medium | Local horizon rules later | Low presentation complexity | **GREEN** |
| Independent feasibility check | Complete declared rules | Medium | Completeness needs SME | Low compute relative to search | **GREEN**, model-relative only |
| Constraint-linked explanations | Model reasons | Medium | Correct constraint names | Simple report adequate | **GREEN** |
| Work compatibility on real railway | Incomplete | Medium–high | Extensive SME/local rules | Wrong assumptions undermine demo | **YELLOW** |
| Robust scenario evaluation | Synthetic scenarios | Medium–high | Meaningful bounds needed | More solves; declare budget | **YELLOW** |
| Authorized file export integration | Access unknown | Medium | Owner-approved schema | No live demo guarantee | **YELLOW** |
| Production API integration | Contracts unavailable | High/unknown | Credentials, security and system owners | Reliability cannot be promised | **YELLOW** as future work; **RED** as present claim |
| Railway-trained duration model | History unavailable | Medium method, high validation | Comparable labelled executions needed | Training itself is not the main obstacle | **RED now** |
| Railway failure-risk predictor | Exposure/labels unavailable | High | Rare events, interventions, safety review | No credible accuracy claim | **RED now** |
| Stable disruption repair | Authored event | Medium–high | Commitment semantics | Keep optional, bounded | **YELLOW** |
| Full network train rescheduling | Operational data unavailable | Very high | Network/inter-division authority | Scale and fidelity unproven | **RED** |
| Autonomous block grant/release | Not appropriate scope | Not a prototype objective | Operational authority required | Unacceptable claim | **RED** |
| Accident reduction / guaranteed zero delay | Causal evidence absent | Cannot establish by toy demo | Beyond available evidence | No defensible measurement | **RED** |

**Do not attempt first:** national real-time optimization; reinforcement learning trained on an unvalidated simulator; live-system claims using mock data; “official” forms without approved templates; an elaborate UI before a correct experiment. Open-source libraries do not make integration, hosting, validation and maintenance cost-free.

> **PPT TAKEAWAY — Demonstrate the planning logic at a scale you can validate.**  
> • Small, reproducible cases can prove algorithm behavior.  
> • Production data access and rule completeness remain separate gates.  
> **Visual:** green/yellow/red scope ladder.  
> **Sources:** access findings in Section 11; [solver documentation][S27]; report's feasibility assessment.

## 21. Fair Baseline and Evaluation Metrics

### What “asset availability” should mean in this experiment

**UNKNOWN:** no official formula specifically defining the SIH26027 optimization KPI was located. Do not present the following as a Ministry standard.

**INFERRED prototype definition:** for a fixed set of track resources and horizon H, let U_r be the union of maintenance-occupation intervals on resource r. Define weighted availability as:

**A = 1 − [Σ_r v_r · length(U_r)] / [H · Σ_r v_r].**

Declare resources, weights, time units, closures outside maintenance and denominator consistently. This is infrastructure-time availability under the model, not trains carried, passenger punctuality, asset reliability or safe field availability. Report mandatory completion alongside A; otherwise “do no maintenance” wins incorrectly. Multi-track occupation must be counted per affected resource, not accidentally collapsed into one corridor interval.

### Baselines

**Proposed primary baseline:** priority/deadline-first coordinated greedy planning. Use the same inputs, validated compatibility, resources, windows and uncertainty assumptions as the optimizer. Sort by mandatory status, authorized priority, due date and declared tie-breaker; place work in the first feasible suitable window; opportunistically combine compatible ready work; allow a limited documented repair pass.

This is a reproducible proxy, not a measured reconstruction of today's entire railway process. Have an SME review it if possible. Include an expert-created plan when available. Department-independent first-fit is only a secondary ablation showing the value of coordination. Never force a historical combined share into the baseline.

The optimizer must not receive a better forecast, longer permissible windows, more crews, different deadlines or a weaker safety checker. Report its time budget and all relevant baseline tuning. Evaluate both on identical scenario realizations.

### Metrics

Every metric below is a **NIRVIKALP PROTOTYPE KPI** unless later adopted by the railway owner.

| Metric | Definition / safeguard |
|---|---|
| Feasibility | Number and type of hard-constraint violations; require zero under declared model |
| Mandatory completion | Mandatory tasks finished by deadline / mandatory tasks due; expose infeasibility rather than hide denominator |
| Critical/overdue work | Count and weighted completion by authorized class; report remaining backlog |
| Occupation | Union track-resource minutes/hours; same geography and horizon for both methods |
| Possessions | Count distinct access episodes with a published counting rule |
| Compatible-work utilization | Fraction of explicitly eligible opportunities used; eligibility itself needs a reproducible definition |
| Train-path conflicts | Modelled intersections with excluded paths; not accidents and not automatically delay |
| Delay minutes | Only from an explicit, validated-for-purpose traffic model; state primary/propagated treatment |
| Overrun robustness | Exceedance frequency or worst-case excess across declared scenarios; empirical probability only with valid data |
| Plan stability | Fraction of previously planned tasks changed plus total start-time movement; distinguish locked work |
| Resources | Productive use, travel/setup and idle time separately; maximizing utilization is not inherently optimal |
| Solve quality | Runtime, status, objective bound/gap where applicable and timeout behavior |
| Explanation quality | Whether a reviewer can trace a decision to input, constraint and permitted alternative |
| Planning effort | Measured human task time only in a defined user study; never infer from solver runtime |

### Experiment protocol

1. Freeze a data manifest, model version, constraint list and evaluation rules before comparison.
2. Use hand-checkable tiny cases, then progressively larger declared synthetic families. Include sparse and congested traffic, abundant and scarce resources, compatible and incompatible work.
3. Include negative cases: no benefit possible; already optimal baseline; unavoidable mandatory infeasibility; missing rule; unavailable machine; crossing-midnight work; an apparently attractive but invalid grouping.
4. Test duration/traffic perturbations separately from algorithm changes. Use multiple seeds for generated cases and report dispersion, not one favorable instance.
5. Run the independent checker on every method. An infeasible lower-occupation plan is not an improvement.
6. Ablate grouping, readiness, horizon consistency and stability one at a time while retaining the same hard safety model.
7. Publish denominators, timeout/no-solution cases and full objective trade-offs. No percentage savings is claimed before this experiment exists.

**Example of correct reporting — ASSUMPTION:** “On these fictional instances, with these constraints and this runtime budget, method B used fewer track-hours while completing the same mandatory work.” It cannot be shortened to “reduces Indian Railways downtime by X%.”

> **PPT TAKEAWAY — Compare against a competent planner, using equal information.**  
> • Completion and feasibility must accompany availability.  
> • Negative and no-improvement cases belong in the evaluation.  
> **Visual:** paired results with mandatory completion, occupation and runtime.  
> **Sources:** [joint planning context][S03], [solver status definitions][S27]; proposed experimental protocol.

## 22. Audit of Our Existing NIRVIKALP PPT

**Input:** `SIH-2026(NIRVIKALP) (2).pptx`, ten slides. Statements below were inspected from the supplied deck. **KEEP** means preserve the idea; it does not validate an unbuilt implementation. **MODIFY** means qualify or correct. **REMOVE** means unsupported/misleading as stated. **VERIFY** means obtain evidence before using it.

| Slide / important statement | Verdict | Exact reason and required treatment |
|---|---|---|
| 1 — team / PS identity | **KEEP / VERIFY** | Keep identity; compare title/category against current official entry [S01] |
| 2 — three named maintenance departments | **MODIFY** | They are the PS's relevant departments, not an exhaustive claim that all railway maintenance has only three owners |
| 2 — “no cross-department coordination” | **REMOVE** | Contradicted as a blanket process claim by joint rolling planning [S03] |
| 2 — “data is siloed” | **MODIFY** | Say heterogeneous departmental records require planning integration; do not deny documented links/visibility [S05][S06][S07][S08][S09] |
| 2 — decentralized/manual process | **MODIFY** | Attribute the challenge to PS wording; explain the existing coordinated process alongside it |
| 2 — repeated possessions, idle machines, reduced availability | **VERIFY** | Plausible consequences; no current local measured frequency or causal attribution supplied |
| 3 — combined-block percentage | **MODIFY** | Use the scoped historical evidence register in Section 9, not an all-current-block claim |
| 3 — complement called “uncoordinated” | **REMOVE** | Separate use does not establish absent coordination or safe combinability |
| 3 — same section blocked three times instead of once | **REMOVE as fact** | Not established by the aggregate audit statistic; can only be an explicitly hypothetical compatible example |
| 3 — 3h + 2.5h + 2h becomes 3.5h and saves 4h | **MODIFY** | Arithmetic scenario only; specify sequencing, protection, resource and restoration assumptions; no railway-validated saving |
| 4 — TMS visible only to Engineering | **REMOVE blanket claim** | Public functions do not establish an absolute access boundary; integration documentation weakens it |
| 4 — SMMS visible only to S&T | **REMOVE blanket claim** | Exact permissions unknown; do not turn lack of access into a product limitation |
| 4 — TDMS visible only to TRD | **REMOVE blanket claim** | CRIS describes integration design [S07] |
| 4 — BDMS no optimization / coordination suggestions | **VERIFY / MODIFY** | Complete current algorithms unknown; mirrored manual already describes shared workflow [S09] |
| 4 — COA only train tracking, not maintenance-linked | **MODIFY** | Understates operating functions and conflicts with the PS's corridor input role [S01][S08] |
| 5 — SAMARATH overall decision layer | **KEEP as proposal** | Fits an extension architecture; avoid presenting conceptual boxes as completed software |
| 5 — unified adapters | **MODIFY** | Proposed contracts/mock imports until actual authorized interfaces are verified |
| 5 — Work Package Formation | **KEEP / MODIFY** | Preserve task identity; do not irreversibly pre-group and exclude better schedules; validate full package |
| 5 — Maintenance Opportunity Engine | **KEEP as hypothesis** | Define precisely how candidates are generated and rejected; matching location/time is insufficient |
| 5 — deterministic safety validation, UNKNOWN/VERIFY | **KEEP / MODIFY** | Strong uncertainty treatment; call it model-relative checking, not certified safety validation |
| 5 — AI duration + CP-SAT | **MODIFY** | Optimization candidate is defensible; learned duration is conditional on historical data |
| 5 — Plans A/B/C | **KEEP / MODIFY** | Same hard constraints; disclose objective differences and avoid dominated alternatives |
| 5 — dynamic PlanDiff, preserve locked/completed | **KEEP OPTIONAL** | Useful research extension; complete weekly/monthly requirements first |
| 5 — human approval | **KEEP / CLARIFY** | Separate programme review from actual operational grant/release |
| 6 — Python/FastAPI/database stack | **VERIFY later** | Not a research conclusion; choose after data and experiment needs are fixed |
| 6 — OR-Tools CP-SAT | **KEEP as candidate** | Benchmark; report solver status and limits [S27] |
| 6 — XGBoost P50/P80/P95 | **MODIFY** | No railway training/calibration evidence; conditional research path only |
| 6 — HTML Canvas / tactical glassmorphic UI | **DEFER** | Does not answer the research problem or establish usability |
| 6 — JWT/HMAC/RBAC | **VERIFY later** | Technology labels are not a security architecture, access approval or audit guarantee |
| 6 — ReportLab “official IR gazette format” | **REMOVE “official”** | No authorized template or official status established |
| 6 — single server, zero licensing cost, all open source | **MODIFY** | Confirm exact components/licences; total hosting, integration and validation cost is not zero |
| 7 — technical approach | **MODIFY later** | Inspected slide contains the heading/logo without a substantive technical approach; no PPT rewrite performed here |
| 8 — React stack | **RECONCILE later** | Inconsistent with the Canvas-only presentation elsewhere; technology choice remains premature |
| 8 — public/reference data and authorized interfaces | **KEEP / QUALIFY** | Distinguish available reference data from unconfirmed operational access |
| 8 — independent checker and unknown flags | **KEEP** | Good proposed evidence mechanism; checker completeness still needs review |
| 8 — corridor to larger network | **MODIFY** | Present scale as a future test, not a guaranteed property |
| 8 — infeasibility diagnostics | **KEEP** | Especially useful if tied to precise constraints and permitted remedies |
| 8 — ML only if authorized historical data exists | **KEEP** | This condition should govern slide 6's unconditional prediction claim |
| 9 — reduced disruption / planning time / risk | **MODIFY** | Expected benefits or evaluation hypotheses, not achieved results |
| 9 — faster recovery / resource optimization | **VERIFY** | Needs experiment and realistic resources; do not infer from architecture |
| 10 — shortened-looking reference URLs | **REPLACE later** | Several displayed paths link to generic homepages; use exact documents and locators in Section 26 |
| 10 — XGBoost paper as duration evidence | **MODIFY** | General algorithm evidence only [S31] |

### Previous AI report: independent audit

The supplied `SIH26027_Deep_Research_Report.md` is not a source for railway facts. Its useful hypotheses are retained only where independently supported above.

| Previous-report proposition | Research verdict |
|---|---|
| The historical combined share is today's baseline | Unsupported temporal extrapolation |
| No APIs exist / real access is impossible | Unsupported; official API infrastructure exists, permission remains unknown [S14] |
| BDMS has no shared visibility | Inconsistent with the mirrored manual; current exact capability still needs verification [S09] |
| Synthetic duration/risk models are calibrated by aggregate audit numbers | Invalid calibration claim; no task-level distribution established |
| Use the historical combined share to construct baseline performance | Unfair and statistically unjustified |
| Freight data is unavailable even within Railways | Unsupported; FOIS/COA purposes demonstrate relevant internal information [S08][S10] |
| Public schedules equal WTT/control data | Incorrect substitution [S21] |
| DRM grants every operational block | Conflates programme approval with actual operating procedures [S03][S15] |
| Corridor windows are immutable except timetable revisions | Not established by inspected evidence |
| Old corridor-duration figures are universal current hard rules | Not established; current applicable instructions needed |
| CP-SAT/what-if/XGBoost make the team uniquely top-ranked | No comparative evaluation or ranking evidence |
| Optimization cannot count as AI in any sense | Too categorical; distinguish constrained search from learned prediction and clarify PS expectations |

> **PPT TAKEAWAY — Preserve the decision-support concept; repair the factual claims.**  
> • Current-system absence claims need evidence or removal.  
> • Proposed capabilities and measured results must be visually distinct.  
> **Visual:** KEEP / MODIFY / REMOVE / VERIFY audit summary.  
> **Sources:** supplied deck; [Board procedure][S03], [BDMS manual][S09], [API report][S14], Section 9 evidence register.

## 23. What We Know / What We Assume / What We Still Need From a Railway SME

| Knowledge class | Current position |
|---|---|
| **VERIFIED** | PS requirements; documented system purposes; dated Board procedure; historical evidence scoped in Section 9; selected manual provisions |
| **STRONGLY SUPPORTED** | Additional BDMS/RBS workflow/integration descriptions in third-party-hosted documents, pending official provenance/current deployment confirmation |
| **INFERRED** | A bounded decision-support scheduler is an appropriate research direction; the proposed schema, objectives and experiment are useful starting points |
| **ASSUMPTION** | Any synthetic topology, duration, freight scenario, compatibility rule or resource calendar used before railway review |
| **UNKNOWN** | Exact current local workflow, full compatibility rules, production schemas/API entitlement, available training data, actual baseline quality and achievable savings |

### Prioritized SME interview and document request

| Priority | Specific question / evidence requested | Decision it resolves |
|---|---|---|
| P0 | Show one current demand from creation through programme, grant, extension if any, release and closure | Correct lifecycle and responsible roles |
| P0 | Demonstrate current BDMS/RBS/COA suggestion, conflict and optimization functions | Actual product gap; avoid duplication |
| P0 | Supply applicable divisional/zonal rules and amendments for one bounded corridor | Which constraints can be claimed valid |
| P0 | Review three proposed combinations: allowed, prohibited and ambiguous | Meaningful compatibility evidence |
| P0 | Explain how criticality, due dates and mandatory work are determined | Objective hierarchy and non-negotiable tasks |
| P0 | Identify an approved data-sharing route and a minimal redacted sample | Integration and training feasibility |
| P1 | Explain monthly versus weekly commitments, cut-offs and freeze periods | Horizon consistency model |
| P1 | Show how goods forecasts are produced, revised and used | Input granularity and uncertainty |
| P1 | Review the coordinated greedy baseline against a real planning example | Fair evaluation |
| P1 | Provide actual duration components and reasons for overrun/cancellation | Whether duration prediction is supportable |
| P1 | Explain machinery travel, crew competence and readiness constraints | Resource feasibility |
| P1 | Define the locally meaningful availability/impact KPI | Objective validity and reporting denominator |
| P2 | Describe approval latency, override reasons and cross-division coordination | Future workflow and explanation research |

**INFERRED evidence pack to bring:** this report, one fictional corridor case, a source/field mapping, a compatibility worksheet and the proposed baseline protocol. Ask for corrections and counterexamples rather than endorsement of a preselected technology.

> **PPT TAKEAWAY — The next validation milestone is a concrete railway walkthrough.**  
> • Current capability and applicable rules are the highest-value unknowns.  
> • A small redacted example is more useful than a broad assurance.  
> **Visual:** known / assumed / unanswered evidence board.  
> **Sources:** limitations documented in Sections 6, 11 and 16; proposed interview plan.

## 24. Recommended Research Conclusions BEFORE Prototype Design

**INFERRED recommendation:** investigate a corridor-level planning assistant that consumes authorized or explicitly synthetic records, compares feasible weekly/monthly schedules, and explains the selected and rejected work. Keep the proposal bounded until current railway software and local constraints are demonstrated by an SME.

The research supports the following decisions now:

1. **Correct the problem narrative.** Describe an improvement to joint planning, not the invention of coordination.
2. **Choose a measurable question.** Can constrained scheduling reduce occupation or improve urgent-work completion against a coordinated baseline, under the same information?
3. **Separate evidence layers.** Real document facts, proposed rules, synthetic instances and measured results must never be blended.
4. **Treat missing rules as substantive.** A fast answer to an incomplete model is not operational readiness.
5. **Make both horizons central.** Demonstrate how monthly allocations survive or change under weekly detail.
6. **Defer predictive ML until data qualifies.** An honest interval/scenario model is preferable to fabricated calibration.
7. **Use minimal presentation to explain the experiment.** Technology and visual styling follow the research, not the reverse.

### Gates before implementation decisions

| Gate | Evidence required | If unavailable |
|---|---|---|
| Gap | Current-system walkthrough or carefully bounded public-gap statement | Do not claim absence/uniqueness |
| Data | Provenance and either authorized sample or explicit synthetic data card | No live-integration or training claim |
| Rules | Applicable subset, unknowns and validation responsibility | Research-only model-relative feasibility |
| Objective | Accepted priorities and KPI definitions | Present alternative assumptions and sensitivity |
| Baseline | Reproducible informed heuristic, ideally SME reviewed | Label as proxy, not actual national practice |
| Evidence | Completed paired experiments | No numerical benefit promises |

The Ministry's stated task supports investigating a better planning decision layer. What remains unproven is the exact local production gap and its magnitude. That uncertainty should guide the next investigation, not be hidden behind a stronger product claim.

> **PPT TAKEAWAY — Prove one useful planning improvement before expanding scope.**  
> • A narrow experiment can be rigorous without production access.  
> • Real deployment claims require a separate evidence path.  
> **Visual:** gap → data/rules → baseline → experiment → review gates.  
> **Sources:** [PS][S01], [existing procedure][S03]; report's recommendations.

## 25. PPT-Ready Evidence Bank

These are research-approved message directions, not a rewritten deck. Historical figures should be copied with the complete labels from Section 9 rather than detached into oversized numbers.

| Message for later use | Evidence level | Required qualification / exact source | Suggested visual |
|---|---|---|---|
| “The PS calls for coordinated weekly and monthly maintenance planning.” | VERIFIED | Official requirement, not achieved capability [S01, expected solution] | Two linked horizons |
| “Existing railway planning already includes a joint process.” | VERIFIED policy | Do not imply uniform measured implementation [S03, clauses (a)–(j)] | Process with proposed assistant inserted |
| “Historical audit findings motivate better scheduling evaluation.” | VERIFIED historical / INFERRED motivation | Use full date/sample from Section 9 [S02, pp.30–34] | Scoped evidence card |
| “Public documentation does not establish the complete current optimizer capability.” | UNKNOWN / search finding | Not a claim of absence [S05][S06][S07][S08][S09] | Documented versus unverified matrix |
| “Internal railway API infrastructure exists; our access is not yet established.” | VERIFIED / UNKNOWN | Platform evidence does not grant entitlement [S14, §15] | Access boundary |
| “Public passenger timings are not complete operational planning inputs.” | INFERRED from service scope | Public enquiry scope and missing operational requirements [S21][S01] | Public schedule versus required path record |
| “A proposed combined package needs evidence of compatibility.” | INFERRED design | Applicable rules/SME review still required [S15] | Allowed / prohibited / unknown examples |
| “Our baseline will coordinate compatible work too.” | Proposed methodology | Do not claim experiments already ran | Paired evaluation diagram, Section 21 |
| “Synthetic instances demonstrate conditional behavior, not field savings.” | Methodological limitation | State all generated assumptions | Data card and result boundary |
| “Prediction will be conditional on suitable historical data.” | Research decision | Generic XGBoost citation is not railway validation [S31] | Training-data gate |
| “Common solver and dashboard features are not uniqueness evidence.” | STRONGLY SUPPORTED comparison | Repository claims only [S32][S33][S34] | Prior-art matrix |
| “A solver proposal remains subject to applicable operational authority.” | INFERRED design from verified rules | Do not label plan output an actual permit [S15] | Separate proposal and authority statuses |

> **PPT TAKEAWAY — Every headline should carry its evidence boundary.**  
> • Keep dates and denominators attached to numbers.  
> • Label proposals and expected benefits before measurements exist.  
> **Visual:** claim / source / limitation cards.  
> **Sources:** exact references in the evidence bank above.

## 26. Full Source Ledger

**Last checked for every entry below: 22 September 2026.** “Undated” means the inspected page did not establish a reliable publication date; it is not replaced with a crawler date. URLs link to the document/page inspected. Source authority and claim confidence are different: an official source can be historical, and a repository can reliably prove only what its author claims.

| ID / claim supported | Source title | Organization / author | Publication date | Page / paragraph / table | URL | Evidence level / what exactly it proves | Last checked |
|---|---|---|---|---|---|---|---|
| S01 — requirements | SIH 2026 Problem Statements, ID 26027 | Smart India Hackathon / Ministry of Railways entry | 2026 listing; exact posting date unstated | Background, detailed description, expected solution | [Official entry listing][S01] | Primary; requested inputs, planning outcomes and horizons, not current product feature inventory | 2026-09-22 |
| S02 — historical audit | Report No.22 of 2021, Chapter 2 | Comptroller and Auditor General of India | Report designated 2021 | Printed pp.20, 30–34, 48–50, 55–60; §2.1.8.5; Table 2.17 | [Original chapter][S02] | Primary historical audit; scoped findings in Section 9, including Ministry responses; not current national baseline | 2026-09-22 |
| S03 — joint rolling planning | Joint procedure order for rolling block programme | Railway Board | 29 Aug 2023 | Three-page order, clauses (a)–(j) | [Official IRICEN-hosted order][S03] | Primary policy; prescribed planning, review, approval, readiness and recording process | 2026-09-22 |
| S04 — implementation account | Rolling Block — Paradigm, Lumding account | IRICEN/IPWE proceedings contributors | Nov 2023 proceedings | Printed pp.13–28 | [Proceedings paper][S04] | Official-host professional account; an implementation example, not all-India effectiveness measurement | 2026-09-22 |
| S05 — TMS functions | Track Management System | CRIS | Undated product page | Goals/features | [CRIS TMS][S05] | Primary product description; inspection/maintenance information and prioritization functions | 2026-09-22 |
| S06 — SMMS functions | SMMS official app listing | CRIS publisher | Listing inspected; update shown Aug 2026 | About this app / publisher | [Official publisher listing][S06] | Primary publisher claim; maintenance/assets/failures functionality, not complete platform architecture | 2026-09-22 |
| S07 — TDMS functions | Traction Distribution Management System | CRIS | Undated page; project history shown | Goals/features | [CRIS TDMS][S07] | Primary product description; assets, inspections, defects and integration design | 2026-09-22 |
| S08 — COA functions | Control Office Application | CRIS | Undated | Goals/features/integrations | [CRIS COA][S08] | Primary product description; operating charting/running and information exchange | 2026-09-22 |
| S09 — BDMS workflow | BDMS User Manual | CRIS attribution within document; third-party upload | Date not established | Introduction; all-department/my-block views | [Mirrored manual][S09] | Secondary-host document; workflow/visibility claim, current provenance and deployment need confirmation | 2026-09-22 |
| S10 — freight information | Freight Operations Information System | CRIS | Undated | RMS/TMS, features | [CRIS FOIS][S10] | Primary product description; freight information exists, no public forecast API established | 2026-09-22 |
| S11 — public running enquiry | National Train Enquiry System | CRIS | Undated | Product description | [CRIS NTES][S11] | Primary product description; passenger enquiry role, not full controller data access | 2026-09-22 |
| S12 — coaching information | Integrated Coaching Management System | CRIS | Undated | Reporting and integration descriptions | [CRIS ICMS][S12] | Primary product description; relevant reporting/exchanges, not obtainable historical payload | 2026-09-22 |
| S13 — platform identities | CRIS Project List | CRIS | Undated | Project directory entries | [CRIS directory][S13] | Primary directory; product/link identities, not implementation completeness | 2026-09-22 |
| S14 — API infrastructure | Progress of IT Projects, CRIS | Railway Board / CRIS | April 2022 | Printed p.5, §§15.1–15.2 | [Official progress report][S14] | Primary historical status; PRAVAH API counts, not public access to maintenance systems | 2026-09-22 |
| S15 — safety/terminology anchors | General & Subsidiary Rules | Eastern Railway | 2019 edition | GR 1.02; GR/SR 3.51; SR 4.65; Ch.XVII; E-TR-D-1 | [Official G&SR PDF][S15] | Primary regional rulebook edition; cited provisions only, current amendments/local applicability unverified | 2026-09-22 |
| S16 — newer integration claims | SMMS newsletter, Jan–Mar 2026 | Team_SMMS / CRIS-attributed content; third-party host | Jan–Mar 2026 issue | Foreword/integration discussion; module disclaimer | [Mirrored newsletter][S16] | Document claim; RBS/integrations reported, not official-host verified rollout evidence | 2026-09-22 |
| S17 — longer rolling horizon | Year-end Ministry of Railways review | PIB / Ministry of Railways | 15 Dec 2023 | Item 27 | [PIB release][S17] | Primary announcement; 52-week rolling-block notification, not uniform implementation | 2026-09-22 |
| S18 — manual currency | ACS-6 to IRPWM-2024 | Railway Board; IRICEN host | 18 Aug 2025 order | Opening order and amended material | [Official correction PDF][S18] | Primary amendment; demonstrates applicable text/version must be checked | 2026-09-22 |
| S19 — 2026 context | Indian Railways Ensures High Operational Reliability by Running 25,000 Trains Safely Every Day and Moving Millions | PIB / Ministry of Railways | 12 Mar 2026 | Rolling-block and monitoring discussion | [PIB release][S19] | Primary statement of continuing measures; no causal validation of NIRVIKALP benefits | 2026-09-22 |
| S20 — historical capacity fields | Line Capacity Statement 2021–2022 | Central Railway | Reporting year 2021–22 | Two-page section table | [Official statement][S20] | Primary historical table; section/traffic/capacity fields, not live availability | 2026-09-22 |
| S21 — public timetable fields | Train Schedule enquiry | Indian Railways | Live page, undated | Query/result headings and scope note | [Official enquiry][S21] | Primary public interface; displayed schedule fields, not an open bulk API or full WTT | 2026-09-22 |
| S22 — open-data lead | Indian Railways Train Time Table catalog | data.gov.in | Not verified from opened payload | Catalog lead only | [Catalog URL][S22] | **Unverified access lead**; not used as evidence for rows, freshness, licence or API | 2026-09-22 |
| S23 — capacity context | Lok Sabha Starred Question 201 | Ministry of Railways / Parliament | 16 Mar 2022 | Answer and annexure | [Parliament PDF][S23] | Primary historical capacity answer; not current access windows | 2026-09-22 |
| S24 — scheduling prior art | Development of a Maintenance Possession Scheduler for a Railway | Cillie & Bekker; South African Journal of Industrial Engineering | 25 Aug 2023 | Article abstract; DOI 10.7166/34-2-2750 | [Journal article][S24] | Academic; maintenance-window MILP and specific case study, no Indian deployment proof | 2026-09-22 |
| S25 — integrated model | A linear programming joint optimization model of overnight train timetabling and maintenance planning on high-speed railway | Tianwei Zhang et al.; Scientific Reports | 26 Nov 2025 | Abstract; model/scope discussion | [Article][S25] | Academic; joint formulation and assumptions, not a transferable safety specification | 2026-09-22 |
| S26 — research taxonomy | A taxonomy of railway track maintenance planning and scheduling: A review and research trends | Sedghi et al.; university repository copy | 2021 | Review taxonomy and discussion | [Full paper][S26] | Academic review; established research landscape | 2026-09-22 |
| S27 — solver behavior | CP-SAT Solver | Google OR-Tools documentation | Undated current documentation | Integer constraints; solver statuses | [Official documentation][S27] | Primary technical documentation; status semantics and solver usage, not runtime guarantee | 2026-09-22 |
| S28 — Indian timetable research | Rationalized timetabling using a simulation tool: a paradigm shift in Indian Railways | Anoop K. P. et al.; IIT Bombay, Railway Board and CRIS affiliations | Repository manuscript; publication date not established | PDF pp.1, 10–14 | [Author-hosted manuscript][S28] | Primary research account; 2020 exercise, SATSaNG interaction and allowance definitions | 2026-09-22 |
| S29 — commercial prior art | RailSys Suite | RMCon International | Undated | Product capabilities | [Vendor page][S29] | Vendor claims; capabilities advertised, not independent performance/deployment validation | 2026-09-22 |
| S30 — international possession workflow | PODFlo | RailAI information site / Network Rail-related project | Page describes 2024 phase | Workflow and rollout description | [Product information][S30] | Publisher claims; international workflow precedent, not Indian operating authority | 2026-09-22 |
| S31 — general ML method | XGBoost: A Scalable Tree Boosting System | Tianqi Chen & Carlos Guestrin | 2016 | Abstract / paper | [Original paper][S31] | Academic method; not railway duration prediction validation | 2026-09-22 |
| S32 — public feature claims | Junction | GitHub author samyakmisal | Repository date not established | README | [Repository][S32] | Community; advertised features only, not executed or benchmarked | 2026-09-22 |
| S33 — public feature claims | RailOpt-AI | GitHub author subham120 | Repository date not established | README | [Repository][S33] | Community; advertised stack/features only | 2026-09-22 |
| S34 — public feature claims | Railway_Block_Planner | GitHub author sawantpranav | Repository date not established | README | [Repository][S34] | Community; advertised mock-data planning approach only | 2026-09-22 |
| U01 — presentation claims | SIH-2026(NIRVIKALP) (2).pptx | Team NIRVIKALP, supplied by user | File date not independently established | Slides 1–10 | User-provided local file | Primary evidence of the team's statements; not authority for railway facts | 2026-09-22 |
| U02 — hypotheses to audit | SIH26027_Deep_Research_Report.md | Previous AI-generated report supplied by user | Date not independently established | Claims reviewed in Section 22 | User-provided local file | Hypothesis source only; never used to verify operations | 2026-09-22 |

### Access limitations and unresolved leads

The data.gov.in resource payload, some official ACTM/IRSEM/manual pages, and a located Parliamentary Accounts Committee PDF could not be reliably retrieved in this session. They are not used to assert their contents. Firecrawl's general web search/scrape was unavailable because its tool reported insufficient credits; accessible primary sources were inspected through the available web reader. A research-index search helped locate literature; article sources were subsequently read directly. No search-result snippet is used as a substitute for a read source in the evidential conclusions.

The original CAG text was inspected, but its browser screenshot route failed; numerical claims were checked in extracted document text and their printed-page locations. Current system internals, restricted APIs and divisional operating records were not accessible. This bounds the report's conclusions and identifies the next evidence to request.

> **PPT TAKEAWAY — Source quality includes date, scope and access status.**  
> • An official historical document is not a current measurement.  
> • A product claim is not an independent test result.  
> **Visual:** compact evidence legend attached to every factual slide.  
> **Sources:** complete ledger above; research method and access record.

---

**Research boundary:** This report recommends what to investigate and how to evaluate it. It does not certify a railway operating plan, claim a completed implementation, predict a hackathon ranking, or report unmeasured savings.

[S01]: https://www.sih.gov.in/sih2026PS
[S02]: https://cag.gov.in/uploads/download_audit_report/2021/Chapter%202-0624d8042c49185.46299461.pdf
[S03]: https://www.iricen.gov.in/iricen/other_manual/ircm_ref_docs/1801.pdf
[S04]: https://iricen.gov.in/iricen/ipwe_seminar/2017/Nov%202023%20Vol-1/Rolling%20Block%20-%20Paradigm%202%20.pdf
[S05]: https://cris.org.in/loadpage?page=proTMS
[S06]: https://play.google.com/store/apps/details?hl=en_SG&id=org.cris.smms
[S07]: https://cris.org.in/loadpage?page=proTDMS
[S08]: https://cris.org.in/loadpage?page=proCOA
[S09]: https://www.scribd.com/document/938691657/BDMS-User-Manual
[S10]: https://cris.org.in/loadpage?page=proFOIS
[S11]: https://cris.org.in/loadpage?page=proNTES
[S12]: https://cris.org.in/loadpage?page=proICMS
[S13]: https://cris.org.in/loadpage?page=ProjectListPage
[S14]: https://indianrailways.gov.in/railwayboard/uploads/directorate/cis/Progress_of_IT_projects_CRIS.pdf
[S15]: https://er.indianrailways.gov.in/cris/uploads/files/1572612805247-GRSR19.pdf
[S16]: https://anyflip.com/ogwes/dqcq/basic/
[S17]: https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1986713&lang=2&reg=48
[S18]: https://www.iricen.gov.in/iricen/Track_Manuals/ACS-6%20to%20IRPWM-2024.pdf
[S19]: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2239095&lang=2&reg=48
[S20]: https://cr.indianrailways.gov.in/cris/uploads/files/1661856840746-Line%20Capacity%20Statement%202021-2022.pdf
[S21]: https://www.indianrail.gov.in/enquiry/SCHEDULE/TrainSchedule.html?locale=e
[S22]: https://www.data.gov.in/catalog/indian-railways-train-time-table
[S23]: https://sansad.in/getFile/loksabhaquestions/annex/178/AS201.pdf?source=pqals
[S24]: https://sajie.journals.ac.za/pub/article/view/2750
[S25]: https://www.nature.com/articles/s41598-025-26026-9
[S26]: https://oulurepo.oulu.fi/bitstream/handle/10024/29624/nbnfi-fe2021102652277.pdf?isAllowed=y&sequence=1
[S27]: https://developers.google.com/optimization/cp/cp_solver
[S28]: https://www.ee.iitb.ac.in/~belur/pdfs/j23informs.pdf
[S29]: https://rmcon-int.de/railsys-suite/
[S30]: https://info.railai.co.uk/podflo/
[S31]: https://arxiv.org/abs/1603.02754
[S32]: https://github.com/samyakmisal/Junction
[S33]: https://github.com/subham120/RailOpt-AI
[S34]: https://github.com/sawantpranav/Railway_Block_Planner
