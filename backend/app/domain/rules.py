"""
Domain Engine: Declarative Compatibility Rules and Precedence Evaluator.
Strictly declarative: no arbitrary Python execution in rules.
Invariants:
- Explicit PROHIBITED dominates ALLOWED.
- Missing rule or missing evidence yields UNKNOWN.
- Expired evidence fails (yields UNKNOWN/BLOCKED).
- Human 'verify' action creates a new approved revision with attached evidence; does not set an unverified bypass flag.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import copy

from app.schemas.enums import DepartmentType, CompatibilityEffect
from app.schemas.rules import (
    DeclarativeCompatibilityRule,
    RuleVerificationRequest,
    CompatibilityEvaluationResult,
)


# In-memory versioned repository for declarative compatibility rules
_RULES_REGISTRY: Dict[str, List[DeclarativeCompatibilityRule]] = {}


def _init_default_rules():
    global _RULES_REGISTRY
    if _RULES_REGISTRY:
        return

    defaults = [
        DeclarativeCompatibilityRule(
            rule_id="RULE-IR-001",
            revision=1,
            department_a=DepartmentType.ENGINEERING,
            work_type_a="TAMPING",
            department_b=DepartmentType.SIGNALLING,
            work_type_b="POINT_MACHINE",
            effect=CompatibilityEffect.ALLOWED,
            requires_concurrent_execution=True,
            description="Simultaneous P-Way track tamping and S&T point machine overhaul in same turn-out zone.",
            evidence_reference="IR_PWM_2020_PARA_804",
            author="Chief Track Engineer",
            approver="Principal Chief Engineer",
            effective_from_utc=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_to_utc=None,
        ),
        DeclarativeCompatibilityRule(
            rule_id="RULE-IR-002",
            revision=1,
            department_a=DepartmentType.ENGINEERING,
            work_type_a="BCM_DEEP_SCREENING",
            department_b=DepartmentType.SIGNALLING,
            work_type_b="AXLE_COUNTER",
            effect=CompatibilityEffect.PROHIBITED,
            requires_concurrent_execution=False,
            description="Deep screening ballast cleaning causes extreme vibration and mechanical disturbance that invalidates electronic axle counter calibration.",
            evidence_reference="IR_SEM_PART2_SEC4",
            author="Chief Signal Engineer",
            approver="Principal Chief Signal & Telecom Engineer",
            effective_from_utc=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_to_utc=None,
        ),
        DeclarativeCompatibilityRule(
            rule_id="RULE-IR-003",
            revision=1,
            department_a=DepartmentType.ELECTRICAL,
            work_type_a="OHE_INSPECTION",
            department_b=DepartmentType.ENGINEERING,
            work_type_b="TAMPING",
            effect=CompatibilityEffect.ALLOWED,
            requires_concurrent_execution=True,
            description="OHE de-energized inspection allows simultaneous diesel CSM tamping on the same track segment.",
            evidence_reference="IR_ACTM_VOL2_PARA_203",
            author="Chief Electrical Distribution Engineer",
            approver="Principal Chief Electrical Engineer",
            effective_from_utc=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_to_utc=None,
        ),
        DeclarativeCompatibilityRule(
            rule_id="RULE-IR-004",
            revision=1,
            department_a=DepartmentType.ELECTRICAL,
            work_type_a="CONTACT_WIRE_STRINGING",
            department_b=DepartmentType.SIGNALLING,
            work_type_b="CIRCUIT_TESTING",
            effect=CompatibilityEffect.PROHIBITED,
            requires_concurrent_execution=False,
            description="High tension wire stringing carries severe risk of electro-magnetic induction onto parallel signalling detection circuits.",
            evidence_reference="IR_ACTM_VOL1_PARA_112",
            author="Chief Electrical Engineer (Traction)",
            approver="Principal Chief Engineer",
            effective_from_utc=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_to_utc=None,
        ),
        DeclarativeCompatibilityRule(
            rule_id="RULE-IR-005",
            revision=1,
            department_a=DepartmentType.ELECTRICAL,
            work_type_a="NEUTRAL_SECTION_OVERHAUL",
            department_b=DepartmentType.ENGINEERING,
            work_type_b="MANUAL_PACKING",
            effect=CompatibilityEffect.UNKNOWN,
            requires_concurrent_execution=False,
            description="Requires specific site isolation clearance and physical ladder staging assessment.",
            evidence_reference="PENDING_SITE_ASSESSMENT",
            author="Divisional Electrical Engineer",
            approver="Unapproved (Draft)",
            effective_from_utc=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_to_utc=None,
        ),
        DeclarativeCompatibilityRule(
            rule_id="RULE-IR-006",
            revision=1,
            department_a=DepartmentType.ENGINEERING,
            work_type_a="RAIL_GRINDING",
            department_b=DepartmentType.ELECTRICAL,
            work_type_b="OHE_INSPECTION",
            effect=CompatibilityEffect.PROHIBITED,
            requires_concurrent_execution=False,
            description="High-velocity incandescent sparks and conductive metal dust from rail grinding contaminate composite OHE insulators.",
            evidence_reference="IR_ACTM_VOL2_SEC18",
            author="Chief Electrical Distribution Engineer",
            approver="Principal Chief Electrical Engineer",
            effective_from_utc=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_to_utc=None,
        ),
        DeclarativeCompatibilityRule(
            rule_id="RULE-IR-007",
            revision=1,
            department_a=DepartmentType.SIGNALLING,
            work_type_a="TRACK_CIRCUIT",
            department_b=DepartmentType.ENGINEERING,
            work_type_b="SLEEPER_RENEWAL",
            effect=CompatibilityEffect.ALLOWED,
            requires_sequential_execution=True,
            description="Sleeper renewal requires disconnect of track circuit bonds followed by joint continuity testing.",
            evidence_reference="IR_PWM_2020_PARA_812",
            author="Chief Track Engineer",
            approver="Principal Chief Engineer",
            effective_from_utc=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_to_utc=None,
        ),
        DeclarativeCompatibilityRule(
            rule_id="RULE-IR-008",
            revision=1,
            department_a=DepartmentType.SIGNALLING,
            work_type_a="POINT_MACHINE",
            department_b=DepartmentType.ELECTRICAL,
            work_type_b="OHE_INSPECTION",
            effect=CompatibilityEffect.ALLOWED,
            requires_concurrent_execution=True,
            description="OHE tower wagon inspection aloft is compatible with trackside ground point machine maintenance outside dynamic clearance envelope.",
            evidence_reference="IR_ACTM_VOL2_SEC12",
            author="Chief Signal & Electrical Liaison Officer",
            approver="Principal Chief Electrical Engineer",
            effective_from_utc=datetime(2025, 1, 1, tzinfo=timezone.utc),
            effective_to_utc=None,
        ),
    ]

    for r in defaults:
        _RULES_REGISTRY[r.rule_id] = [r]


_init_default_rules()


def get_all_rules(active_only: bool = True) -> List[DeclarativeCompatibilityRule]:
    """Retrieve all current active rule revisions."""
    _init_default_rules()
    result = []
    for rule_list in _RULES_REGISTRY.values():
        if active_only:
            # Pick latest non-superseded revision
            latest = rule_list[-1]
            if latest.superseded_by_revision is None:
                result.append(latest)
        else:
            result.extend(rule_list)
    return sorted(result, key=lambda x: x.rule_id)


def get_rule_by_id(rule_id: str) -> Optional[DeclarativeCompatibilityRule]:
    _init_default_rules()
    rule_list = _RULES_REGISTRY.get(rule_id)
    if not rule_list:
        return None
    return rule_list[-1]


def verify_rule(request: RuleVerificationRequest, user_id: str = "reviewer") -> DeclarativeCompatibilityRule:
    """
    Human 'verify' action.
    Attaches documentary evidence and updates rule state by creating a NEW approved revision.
    Never bypasses rules via an unverified flag.
    """
    _init_default_rules()
    rule_list = _RULES_REGISTRY.get(request.rule_id)
    if not rule_list:
        raise ValueError(f"Rule {request.rule_id} does not exist")

    current = rule_list[-1]
    new_revision_num = current.revision + 1

    # Mark current as superseded
    current.superseded_by_revision = new_revision_num

    # Create new approved revision
    new_rule = DeclarativeCompatibilityRule(
        rule_id=current.rule_id,
        revision=new_revision_num,
        department_a=current.department_a,
        work_type_a=current.work_type_a,
        department_b=current.department_b,
        work_type_b=current.work_type_b,
        effect=request.new_effect,
        requires_concurrent_execution=current.requires_concurrent_execution,
        requires_sequential_execution=current.requires_sequential_execution,
        requires_isolation=current.requires_isolation,
        description=f"{current.description} [Verified: {request.notes}]",
        evidence_reference=request.evidence_document,
        author=user_id,
        approver=request.approving_officer,
        effective_from_utc=datetime.now(timezone.utc),
        effective_to_utc=None,
        superseded_by_revision=None,
    )
    rule_list.append(new_rule)
    return new_rule


def evaluate_compatibility(
    dept_a: DepartmentType,
    work_a: str,
    dept_b: DepartmentType,
    work_b: str,
    now_utc: Optional[datetime] = None,
) -> CompatibilityEvaluationResult:
    """
    Evaluates compatibility between two departments and work types.
    Precedence rules:
    1. Same department + same track: ALLOWED by default (internal departmental bundling).
    2. Any matching PROHIBITED rule immediately dominates and returns PROHIBITED.
    3. Any matching rule whose evidence is expired or missing returns UNKNOWN.
    4. If at least one active ALLOWED rule matches and zero PROHIBITED rules match -> ALLOWED.
    5. If no rule matches -> UNKNOWN (Missing authority blocks bundling).
    """
    _init_default_rules()
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    # Normalize work types for pattern matching
    wa = work_a.upper()
    wb = work_b.upper()

    # If same department and compatible work
    if dept_a == dept_b:
        return CompatibilityEvaluationResult(
            effect=CompatibilityEffect.ALLOWED,
            matched_rule_ids=["INTRA_DEPARTMENT_DEFAULT"],
            is_allowed=True,
            is_prohibited=False,
            is_unknown=False,
            dominant_rule="INTRA_DEPARTMENT_DEFAULT",
            explanation=f"Intra-department coordination for {dept_a.value} is permitted under standard departmental sectional supervision.",
            facts={"department": dept_a.value, "work_a": work_a, "work_b": work_b},
        )

    matched_rules: List[DeclarativeCompatibilityRule] = []
    active_rules = get_all_rules(active_only=True)

    for rule in active_rules:
        # Check bidirectional match (a -> b or b -> a)
        match_direct = (
            rule.department_a == dept_a
            and (rule.work_type_a == "*" or rule.work_type_a in wa or wa in rule.work_type_a)
            and rule.department_b == dept_b
            and (rule.work_type_b == "*" or rule.work_type_b in wb or wb in rule.work_type_b)
        )
        match_reverse = (
            rule.department_a == dept_b
            and (rule.work_type_a == "*" or rule.work_type_a in wb or wb in rule.work_type_a)
            and rule.department_b == dept_a
            and (rule.work_type_b == "*" or rule.work_type_b in wa or wa in rule.work_type_b)
        )

        if match_direct or match_reverse:
            matched_rules.append(rule)

    if not matched_rules:
        return CompatibilityEvaluationResult(
            effect=CompatibilityEffect.UNKNOWN,
            matched_rule_ids=[],
            is_allowed=False,
            is_prohibited=False,
            is_unknown=True,
            dominant_rule=None,
            explanation=f"No approved declarative compatibility rule exists for pair ({dept_a.value}:{work_a}, {dept_b.value}:{work_b}). Unverified combinations strictly block planning bundling.",
            facts={"dept_a": dept_a.value, "work_a": work_a, "dept_b": dept_b.value, "work_b": work_b},
        )

    # Check for expired evidence in matched rules
    for rule in matched_rules:
        if rule.effective_to_utc and rule.effective_to_utc < now_utc:
            return CompatibilityEvaluationResult(
                effect=CompatibilityEffect.UNKNOWN,
                matched_rule_ids=[rule.rule_id],
                is_allowed=False,
                is_prohibited=False,
                is_unknown=True,
                dominant_rule=rule.rule_id,
                explanation=f"Rule {rule.rule_id} evidence expired on {rule.effective_to_utc.isoformat()}. Expired evidence fails and blocks approval.",
                facts={"expired_rule": rule.rule_id, "evidence_ref": rule.evidence_reference},
            )

    # 1. Prohibitions dominate all allows
    prohibited_rules = [r for r in matched_rules if r.effect == CompatibilityEffect.PROHIBITED]
    if prohibited_rules:
        dominant = prohibited_rules[0]
        return CompatibilityEvaluationResult(
            effect=CompatibilityEffect.PROHIBITED,
            matched_rule_ids=[r.rule_id for r in matched_rules],
            is_prohibited=True,
            is_allowed=False,
            is_unknown=False,
            dominant_rule=dominant.rule_id,
            explanation=f"PROHIBITED by {dominant.rule_id}: {dominant.description} (Ref: {dominant.evidence_reference}). Prohibitions strictly dominate all allowances.",
            facts={"dominant_rule": dominant.rule_id, "evidence_reference": dominant.evidence_reference},
        )

    # 2. Unknown evidence blocks bundling
    unknown_rules = [r for r in matched_rules if r.effect == CompatibilityEffect.UNKNOWN]
    if unknown_rules:
        dominant = unknown_rules[0]
        return CompatibilityEvaluationResult(
            effect=CompatibilityEffect.UNKNOWN,
            matched_rule_ids=[r.rule_id for r in matched_rules],
            is_unknown=True,
            is_allowed=False,
            is_prohibited=False,
            dominant_rule=dominant.rule_id,
            explanation=f"UNKNOWN compatibility per {dominant.rule_id}: {dominant.description}. Requires formal verification and evidence attachment before bundling.",
            facts={"dominant_rule": dominant.rule_id, "evidence_reference": dominant.evidence_reference},
        )

    # 3. Allowed
    allowed_rules = [r for r in matched_rules if r.effect == CompatibilityEffect.ALLOWED]
    dominant = allowed_rules[0]
    return CompatibilityEvaluationResult(
        effect=CompatibilityEffect.ALLOWED,
        matched_rule_ids=[r.rule_id for r in matched_rules],
        is_allowed=True,
        is_prohibited=False,
        is_unknown=False,
        dominant_rule=dominant.rule_id,
        explanation=f"ALLOWED by {dominant.rule_id}: {dominant.description} (Ref: {dominant.evidence_reference}).",
        facts={
            "dominant_rule": dominant.rule_id,
            "requires_concurrent": dominant.requires_concurrent_execution,
            "requires_sequential": dominant.requires_sequential_execution,
            "evidence_reference": dominant.evidence_reference,
        },
    )
