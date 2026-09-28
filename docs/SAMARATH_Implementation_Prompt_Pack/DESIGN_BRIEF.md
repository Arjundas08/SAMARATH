# SAMARATH frontend design brief - Signal & Slate

The desired result is a distinctive, polished railway planning workbench: calm, precise, spacious where decisions need attention, and dense where operators compare records. Beauty should come from typography, alignment, strong information hierarchy and excellent interaction. Do not claim an objectively 'best in the world' interface; demonstrate quality through rendered screens and task performance.

## Art direction

Use an ink-blue navigation frame, warm light work surfaces, crisp rules, restrained teal selections and functional orange disruption accents. Railway identity comes from time-distance paths, chainage rulers, possession bands, direction markers and phase sequences. Avoid stock train photographs, invented government seals, neon cyberpunk styling, glassmorphism, giant gradient headers and interchangeable KPI-card grids.

Create an original simple inline-SVG SAMARATH mark from parallel tracks and one controlled branching path. Keep the name SAMARATH prominent with Team NIRVIKALP secondary. Do not imply official Indian Railways branding or endorsement. SVG is suitable; image generation is unnecessary for the operational interface.

Starter tokens, subject to measured contrast validation:
- Canvas #F4F6F8; surface #FFFFFF; warm surface #FAF9F6.
- Ink #142B3E; muted text #526478; border #D5DEE5.
- Action/selection #006D77; tint #E6F2F2.
- Warning #946200 with a pale warm background; critical #B33636; change accent #B94D2F.
- Success, UNKNOWN, STALE, BLOCKED, TEST and AUTHORIZED states each require explicit text/icon semantics, never colour alone.
- A measured 4/8-pixel spacing system; 6-10 pixel control radii; fine borders; subtle shadow only for overlays and hierarchy. Avoid excessive rounded containers.

Use locally hosted, licence-appropriate fonts: one readable sans family (prefer Inter if available and licensed) with system fallback, plus a monospace family for times/IDs. Use tabular numerals. Typical body 14-16px; table text 13-14px; headings 20-28px; diagram labels at least 12px where possible. Do not hide critical facts in tiny text. Font downloads must not be required at demo runtime. Record licence notices if bundled.

Choose a coherent CSS token system and accessible headless primitives. Keep the component library minimal; style the application intentionally. Prefer the repository's existing approach if sound. For a fresh build, CSS variables with component styles and accessible React primitives are sufficient; a second styling framework is unnecessary. Keep ECharts as the planning visualization library, with bespoke render functions when needed.

## Navigation and layout

Seven destinations: Overview, Maintenance, Planning, Change Review, Rules & Readiness, Data & Outcomes, Audit. The Evidence Drawer is the eighth workspace and opens contextually from several destinations. Monthly/Weekly, Time-Distance/Resources and Current/Compare are subordinate views, not separate top-level apps.

Persistent top context: corridor/territory, selected horizon, data provenance, source age, snapshot/plan version and user role. Keep technical IDs in a details disclosure except where they support a comparison or audit decision. Never place infrastructure terms such as 'CP-SAT job lease' in an ordinary planner action. Prefer 'Generate plan', 'Review changes', 'Why not scheduled?' and 'Check data freshness'.

Desktop planning layout: collapsible global navigation, a 240-280px maintenance queue, a dominant chart workspace and a contextual 360-400px evidence drawer. Dock the drawer only when the chart remains genuinely usable; otherwise use a dismissible overlay. At wide widths the navigation can collapse to a narrow rail to preserve chart area. Avoid rigid columns that crush the chart at 1280px.

Desktop targets: 1280x800, 1440x900 and 1920x1080. At 768px support coherent tablet review and forms. At 390px retain navigation, task detail, evidence, source warnings and review actions. Complex timeline editing may switch to an accessible list/detail view with explicit zoom controls. Horizontal scrolling is intentional inside a time axis, not across the entire page. No hidden unreachable action at 200% zoom.

## Screen responsibilities

1. Overview: an operational briefing. Show current planning applicability, mandatory work needing attention, input-quality blockers, latest completed run, and a compact corridor/horizon summary. Use computed values only. Before a run exists show an informative empty state with import/plan actions, not zero-valued fake success cards.
2. Maintenance: search/filterable table with department, asset/chainage, due time, criticality, readiness and source age. Expand a row into requirements and evidence. Batch actions must respect roles and validate each task; never silently rewrite imported source records. Forms show units and error locations.
3. Planning: the hero workbench. Monthly view emphasizes week allocations and resource-pressure bands. Weekly view emphasizes train occupation, maintenance proposals, resource constraints and selected work phases. Solve controls show genuine queued/running/checking/completed/failed/cancelled states. A spinner never invents percentage progress.
4. Evidence Drawer: selected package/tasks, phase durations, consumed resources, rule/source references, readiness, checks, Why and Why-Not. Keep observed facts, optimization tradeoffs and uncertainty visually distinct. Offer a permitted repair only if a stored trial supports it.
5. Change Review: old/new versions with synchronized time ranges, textual PlanDiff, preserved/conflicting locks, baseline metrics with denominators, and review/approval controls. Comparison must remain understandable without colour. Explain every disabled approval condition with a route to resolve it.
6. Rules & Readiness: effective rule versions, applicability, evidence, pending verification and resource/calendar requirements. Give UNKNOWN a proper workflow, not a decorative amber badge. Rule authors and approvers have separate actions.
7. Data & Outcomes: import manifest, accepted/quarantined rows, exact validation errors, source age, connector entitlement and actual execution feedback. External authority observations are read-only. A TEST badge stays visible throughout the workflow.
8. Audit: searchable version/event/decision history and reproducible run details with correlation IDs, role and source references. Displaying history must not imply every database administrator is technically unable to alter data.

## The signature planning visualization

Time on x; station/chainage on y; label Asia/Kolkata and the displayed dates. Show UP/DOWN or track identity explicitly. Train paths require actual route/time samples; if only occupancy intervals exist, draw occupancy bands and state that continuous train trajectories are unavailable. Never interpolate fictitious train movement as observed data.

Maintenance bands encode requested/selected windows and the true affected footprint. Use patterned or outlined treatments for provisional, stale, locked and unknown states. Planned infrastructure unavailability is distinct from a work task's productive time. Phase detail separates setup, work, testing and restoration. Resource timelines occupy a linked secondary panel or tab; do not confuse resource identity with kilometre distance.

Selecting an assignment highlights its affected resources and opens the drawer. Hover offers concise facts; all content is also reachable through keyboard focus and the accessible table. Zoom/pan has visible controls, reset and a preserved selection. Train/background visibility filters cannot change the constraints used by the solver.

Dragging work creates an explicit proposed input/lock revision, validates it and requests a fresh solve. It never mutates an approved immutable plan in the browser. If safe drag behavior is not implemented, provide a clear edit form and omit the drag affordance. No visually draggable object that silently snaps back without explanation.

## Interaction and state quality

Every important route must support loading, empty, partial data, rejected import, UNKNOWN rule, stale result, forbidden action, infeasible solve, timeout without incumbent, feasible non-optimal result, server outage and successful recovery. Preserve user input after a retryable error. Prevent duplicate submissions with real idempotency and button state. Disabling a button is not authorization.

Use 120-200ms restrained transitions for drawer/menu/selection changes, with reduced-motion support. Do not animate a schedule into a different assignment before a verified new result arrives. Respect focus on rerenders; return focus after dialogs. Keyboard navigation, labelled controls, clear focus rings, semantic headings and accessible status announcements are required. Target WCAG 2.2 AA and verify contrast/focus/zoom with actual checks; do not claim certification.

Use optimistic updates only for reversible UI preferences or draft inputs with rollback. Planning results, locks, approvals, authority observations and metric values require server confirmation. Store filter/selection state without persisting secrets or auth tokens in localStorage.

## Visual QA and deliverables

Maintain a component gallery restricted to development/test builds with visible fixtures. Capture browser screenshots from implemented screens using the real local API and TEST database. Required scenes: empty first use; populated maintenance queue; monthly allocation; weekly plan with an open evidence drawer; infeasible input; new event while solving; PlanDiff; stale/blocked approval; quarantined import; compact mobile evidence view.

Review alignment, chart labels, text density, white space, selected-state contrast, clipping, focus, long IDs and names, empty tables, 200% zoom and reduced motion. Fix observed defects rather than merely producing screenshots. Keep screenshot baselines tied to fixture and application versions. Do not substitute image-generation mockups for working UI evidence.

The visual success test: in a populated workbench, a new viewer can identify the corridor, horizon, data mode, proposed maintenance and current issue within 10 seconds; a planner can inspect the blocking evidence and next permitted action without navigating through several unrelated pages. These are proposed usability checks, not measured results.
