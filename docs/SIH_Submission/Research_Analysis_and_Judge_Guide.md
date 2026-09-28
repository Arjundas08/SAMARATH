# SAMARATH: submission strategy and judge preparation

Team NIRVIKALP • SIH26027 • Prepared 27 September 2026

This companion explains the six-slide submission. It is for team preparation, not an extra slide attachment to the SIH portal. The supplied template limits the uploaded presentation to six slides including the cover, retains the required sections, and asks for PDF. Add the registered Team ID and the public prototype link before exporting your final submission.

## 1. What the research actually establishes

We inspected three public archived presentations visually: Cannon Crew (2024, six pages), Framework Fanatics (2025, six pages), and SMARTIrrIS AI (2023, five pages including instructions). We also read first-party accounts of verified MathWorks problem-statement winners Solar Masters (2024) and TwinX (2025). This is a targeted sample, not a review of every SIH winner or statistical evidence about selection.

The public deck archive calls its collection winning presentations, but individual award status was not independently established for these three decks. Their slide design can be studied without treating their filenames, benefit figures, or architecture claims as verified outcomes. No other team's artwork or wording has been copied into the SAMARATH slides.

| Reference | Observed strength | Weakness or evidence limit | Application to SAMARATH |
|---|---|---|---|
| Cannon Crew | Follows the official sections, names an operating environment, shows a technical workflow and maps risks to remedies | Dense explanatory text and small architecture labels. The archived deck alone does not prove an award or measured performance | Keep the section coverage and risk/remedy relationship. Use fewer, larger architecture labels |
| Framework Fanatics | Connects an organizational problem to a processing pipeline and operating benefits | Many competing visual elements. Large savings figures appear without enough visible measurement context to adopt them | Name existing Railway systems and show data flow. Use a transparent arithmetic example instead of unsupported percentages |
| SMARTIrrIS AI | Puts the input-to-decision process beside its proposed solution and explicitly lists dependencies | Detailed diagram competes with long text, and some labels become small | Make data dependencies visible but separate implementation detail into notes |
| Solar Masters | MathWorks confirms the 2024 problem-statement win. Its account describes simulation, prototype work, testing, usability and practical constraints | A retrospective team account is not a controlled comparison of presentation styles. Their actual submission PPT was not obtained | Show what can be tested and explain the path from bounded demonstration to field evidence |
| TwinX | MathWorks confirms the 2025 problem-statement win. Its account identifies a specific real-world workflow gap, functional modules and iterative refinement | The account does not prove that any particular slide style caused the win. Their actual submission PPT was not obtained | Explain the planning gap precisely and prepare for a judge to change an input |

Sources:
- [Public presentation archive](https://github.com/DgrnBoi/SIH-Past-PPTS-2024)
- [Cannon Crew archived deck](https://github.com/DgrnBoi/SIH-Past-PPTS-2024/blob/main/SIH_2024_Cannon_Crew_High_Quality.pdf)
- [Framework Fanatics archived deck](https://github.com/DgrnBoi/SIH-Past-PPTS-2024/blob/main/SIH_2025_Framework_Fanatics_KMRL_Document_Automation.pdf)
- [SMARTIrrIS AI archived deck](https://github.com/DgrnBoi/SIH-Past-PPTS-2024/blob/main/SIH_2023_SMARTIrrIS_AI_Valves_Regulation.pdf)
- [MathWorks winner archive](https://www.mathworks.com/academia/students/competitions/hackathons/winners.html)
- [Solar Masters account](https://blogs.mathworks.com/student-lounge/2025/06/13/innovation-meets-excellence-solar-masters-winning-journey-at-smart-india-hackathon-2024/)
- [TwinX account](https://blogs.mathworks.com/student-lounge/2026/04/06/from-real-roads-to-real-simulations-how-team-twinx-won-smart-india-hackathon-2025/)

Historical official college-SPOC guidance names novelty, clarity, feasibility, practical use, sustainability, impact, user experience and future progression as evaluation considerations. The accessible indexed guidance is for 2024; it is not presented here as a verified 2026 weighted scoring rubric. The supplied 2026 template and current official problem statement are the submission baseline. [Historical guidance](https://sih.gov.in/letters/Guidelines-College-SPOC.pdf)

## 2. The central argument

SAMARATH proposes a coordinated railway maintenance programme that selects feasible work, explains omissions, and revises plans when conditions change. The operational value comes from using scarce block time better while retaining official review and external operational authority.

Do not lead with a list of fashionable technologies. Start with the planning decision: several departments need the same infrastructure, but their work, resources, testing and train constraints must fit together. A shared calendar alone cannot establish that a combined work package is executable.

Our defensible emphasis is the combination of compatibility evidence, complete package durations, an independent feasibility check, actionable why-not explanations, and stable replanning. Scheduling, grouping, dashboards and optimization are established ideas. We should not claim to have invented them or claim that existing BDMS lacks a function without an authorized product walkthrough.

## 3. Exact problem-statement coverage

The official SIH26027 listing was successfully refreshed on 26 September 2026. Team NIRVIKALP subsequently supplied matching text. Category is Software; theme is Transportation & Logistics. [Official statement](https://www.sih.gov.in/sih2026PS)

| Required outcome | Proposed SAMARATH mechanism | Where the deck communicates it | Evidence still needed |
|---|---|---|---|
| Integrate defects and overdue maintenance from TMS, SMMS and TDMS | Authorized imports, validation and normalized versioned records | Slides 2–3 | Actual export contracts, field mapping and permission |
| Use timetable and Control Office goods forecasts with corridor availability | Versioned train occupation, forecast issue time and planning windows | Slide 3 | Complete route/time records and local owner validation |
| Prioritize by criticality, urgency and availability impact | Authorized priority policy plus constrained search; future learned duration estimates | Slide 3 and notes | Working implementation and clarification of AI/ML expectations |
| Coordinate departments and reduce infrastructure occupation | Evidence-valid work packages with setup, work, tests and restoration | Slides 2 and 5 | Validated compatibility rules and measured equal-coverage comparison |
| Weekly and monthly plans | Monthly allocation refined into a detailed week, with reconciliation | Slides 2–3 | Consistency tests and explicit cross-week amendments |
| Improve reliable operations | Independent checking, stale-plan handling and human decisions | Slides 2–4 | Domain review and an authorized pilot |

## 4. Full technical explanation behind slide 3

### Inputs and provenance

Use three explicit input modes: labelled fictional TEST records, authorized file imports, and future owner-approved integration. All modes pass through the same normalization and planning logic. Never relabel fictional records as live data.

The input snapshot includes tasks, assets/topology, locations, working windows, timetable occupation, goods-forecast vintage, crews, machines, readiness evidence, compatibility rules, priority policy and hard commitments. Preserve source identifiers, time zone, units, revision time and evidence lineage. Invalid or ambiguous data should enter a visible correction queue.

### Compatibility and executable packages

Compatibility has three states: allowed, prohibited and unknown. Unknown is not permission. A package can combine work only if the applicable rules, location, resources and test/restoration requirements permit it.

Overlap alone is not enough. Include mobilization/setup, work phases, testing and restoration in resource occupation. A shared crew or machine may force work into sequence. Do not use the longest task duration as the package duration without checking those dependencies.

### Candidate generation and optimization

Generate possible assignments only for eligible windows and resources. Use sparse structures and explicit domain limits instead of considering every candidate pair indiscriminately. Record when a search domain is truncated.

Use OR-Tools CP-SAT as the primary constraint optimizer. Mandatory work, protected train occupation, capacity, compatibility and hard locks remain constraints. For normal programme improvement, optimize the declared coverage and deadline policy before occupation and secondary costs. For disruption recovery, protect required coverage and hard commitments, then minimize changed assignments before marginal efficiency gains.

A time-limited feasible plan is not necessarily optimal. A timeout without a plan does not prove infeasibility. Preserve solver status, stop reason and search-domain coverage separately. [CP-SAT documentation](https://developers.google.com/optimization/cp/cp_solver)

### Independent checker

The checker must read the original snapshot and proposed assignments and recompute feasibility. A separate folder using the optimizer's same constraint predicates is insufficient. Test it with intentionally corrupted results: missing readiness, duplicate resource use, forbidden grouping, time-window overflow and broken locks.

Checker acceptance establishes consistency with the represented model and input evidence. It does not certify railway operational safety or grant authority to execute work.

### Durable services and UI

The proposed stack is React/TypeScript with ECharts, Python/FastAPI, PostgreSQL, OR-Tools, Keycloak and a separate solver worker. Requests create durable jobs; workers claim short leases, solve outside database transactions, and publish only current, checked results. Preserve input versions, plan history and audit records.

The workbench contains monthly/weekly planning, task readiness, resource occupation, why-not evidence, before/after changes and official review. Draw actual train paths only where the available inputs support them. Otherwise display occupation bands. Every metric must come from the current checked result.

### Changes and approval

When a resource, rule, train record or window changes, invalidate affected plan applicability immediately. Keep the earlier plan as history, not as a currently valid recommendation. Repair a bounded affected area first, and disclose that scope. Expand the search if necessary.

Hard locks cannot silently disappear. Approval must check input freshness and version atomically. SAMARATH proposes maintenance programmes; authorized Railway procedures continue to grant, extend and release operational blocks.

### AI/ML scope

The official statement explicitly asks for AI/ML prioritization and scheduling. Constraint optimization is a credible scheduling method, but it is not a trained predictive model. Do not describe CP-SAT as an ML model or claim the proposed historical learner exists today.

The data-gated ML extension predicts work duration and uncertainty using authorized actual execution records. Evaluate it on future time periods and held-out locations, compare with a simple estimate baseline, and test its effect on plan quality. Retain a fallback when history is insufficient or unreliable. Safety and resource constraints remain outside the learner's discretion. Confirm the intended AI/ML scope with the problem owner rather than silently assuming acceptance.

## 5. The worked example and its limits

Slide 5 uses a transparent illustration, not a field result:

- Setup: 10 minutes.
- Task A: 40 minutes.
- Task B: 25 minutes.
- Common testing: 15 minutes.
- Restoration: 10 minutes.

Sequential occupation = 10 + 40 + 25 + 15 + 10 = 100 minutes.

Compatible parallel occupation = 10 + max(40, 25) + 15 + 10 = 75 minutes.

The difference is 25 minutes for the same work under the stated assumptions. A shared crew, incompatible isolation requirement or additional testing can remove this benefit. The example demonstrates the mechanism, not a claimed percentage improvement across Indian Railways.

For a pilot, compare the optimized and coordinated baseline plans on identical inputs and required work coverage. Report completed tasks by priority, occupied resource-minutes, missed deadlines and changed assignments. Do not count overlapping occupation twice. Do not translate minutes directly into rupees, punctuality or emissions without validated operating data.

## 6. Six-slide speaking guide

Suggested timing is a team rehearsal aid, not an SIH rule. Adapt to the time your institution or judging panel grants.

1. **Title, about 15 seconds:** Introduce NIRVIKALP, SAMARATH and SIH26027. Explain that the product proposes coordinated maintenance blocks for Railway officials.
2. **Solution, about 40 seconds:** Explain the conflict over infrastructure and resources. Walk through inputs, feasible packages and the month/week output. Use the 75-minute job in a 60-minute window to show what a useful why-not answer looks like.
3. **Technical approach, about 55 seconds:** Follow the diagram in order. Explain that the solver selects and the checker independently verifies. Mention immutable input versions and changed-input recovery. Be precise about proposed versus implemented AI/ML.
4. **Feasibility, about 35 seconds:** Explain the six-station TEST scope, actual integration dependencies, sparse candidate generation, and the shadow-planning pathway. Say what still needs measurement.
5. **Impact, about 40 seconds:** Explain the arithmetic and the resource/compatibility assumptions. Name the pilot metrics instead of promising unmeasured savings.
6. **References, about 15 seconds:** Show the official requirement, Railway procedure and tool evidence. Direct the panel to the real public demo once the link is added.

## 7. Likely judge questions

**What already works?**
Answer from the actual prototype only. The team reports a prototype exists, but its link and feature evidence were not provided for this deck. Demonstrate the tested features and name the remaining proposed components. Do not read the architecture diagram as a completed-feature checklist.

**Why not simply use BDMS or a spreadsheet?**
Position SAMARATH as a planning-assistance layer for selecting feasible combinations, examining reasons and managing revisions. Preserve existing systems and official processes. Do not claim BDMS has no optimization without checking its current deployed scope.

**Where will you obtain Railway data?**
Begin with fictional TEST records for correctness and authorized exports for a pilot. Integration depends on owner-approved contracts and security review. Public descriptions of CRIS products do not establish public API access.

**What happens when no valid plan exists?**
Display the actual outcome and known reasons. Show proven input conflicts or permitted repair options where evidence supports them. Do not convert a timeout into a proof of impossibility or relax hard constraints to return a green result.

**How is your checker independent?**
It recomputes feasibility against original records through separately implemented checks and rejects mutated assignments in tests. Explain its scope honestly: model consistency, not operational certification.

**Can two departments always work together?**
No. Grouping depends on work type, location, isolation, resources, testing and restoration. Unknown evidence prevents grouping. The 75-minute example works only under explicit assumptions.

**Can this scale across India?**
National scalability has not been demonstrated. First measure candidate generation, model construction, solve, check and memory on the bounded corridor. Grow with territory scope and shared-boundary coordination after evidence supports it.

**What happens if a machine fails after approval?**
Retain the historical approval, mark current applicability stale or blocked, and calculate a checked alternative that preserves hard commitments and minimizes permitted changes. External operational authority remains with Railway officials.

**Why are your savings credible?**
The slide contains a stated arithmetic example, not measured savings. The pilot will use identical input snapshots and comparable work coverage against a coordinated baseline, including no-benefit cases.

**Where is the AI?**
Explain constraint-based scheduling accurately. Historical duration prediction is proposed and requires authorized data and validation. Do not claim a trained model or call synthetic outcomes Railway ground truth.

## 8. Demonstration sequence once the prototype is ready

1. Load one clearly labelled TEST corridor and show input provenance.
2. Show the baseline and checked plan with matching scope and work coverage.
3. Inspect one package including setup, testing and restoration.
4. Open a genuinely unscheduled task and show its evidence-backed reason.
5. Let a judge change a resource or valid planning window.
6. Show immediate stale status, a real re-solve and independent check.
7. Show the before/after difference, including unchanged work.
8. Demonstrate a blocked or infeasible case honestly.

Only demonstrate this sequence when the corresponding behavior actually works. A video can support a demo but should not disguise scripted results as live computation.

## 9. Final manual fields and submission

Replace [ADD REGISTERED ID] on slide 1 and [ADD PUBLIC DEMO LINK] on slide 6. Use a demo link that an evaluator can open without your private account. After changing either field, export a fresh six-page PDF from the edited PowerPoint. Do not upload the earlier PDF with placeholders. Confirm the institution's current deadline and any portal file-size requirement before upload.

The original project outputs remain the detailed reference: the 98-page production blueprint, source pack and phase-by-phase implementation prompt pack. This presentation compresses those findings into the template's evaluation sections; it does not replace the engineering acceptance gates.
