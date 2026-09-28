"""
Enums for SAMARATH domain models and wire contracts.
Strictly validated; no silent coercion.
"""
from enum import Enum


class DepartmentType(str, Enum):
    ENGINEERING = "ENGINEERING"  # Track / Permanent Way (TMS)
    SIGNALLING = "SIGNALLING"    # Signalling & Telecom (SMMS)
    ELECTRICAL = "ELECTRICAL"    # Traction Distribution / OHE (TDMS)


class CriticalityTier(str, Enum):
    TIER_1_MANDATORY = "TIER_1_MANDATORY"              # Statutory safety, overdue limit
    TIER_2_SPEED_RESTRICTION = "TIER_2_SPEED_RESTRICTION"  # PSR relief, high operating benefit
    TIER_3_CYCLIC = "TIER_3_CYCLIC"                    # Routine cyclic maintenance


class DemandStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VALIDATED = "VALIDATED"
    WITHDRAWN = "WITHDRAWN"
    SUPERSEDED = "SUPERSEDED"


class ProvenanceMode(str, Enum):
    TEST = "TEST"                                # Synthetic test dataset with visible test badge
    SYNTHETIC_SCENARIO = "SYNTHETIC_SCENARIO"    # Evaluator challenge / stress scenario
    AUTHORIZED_IMPORT = "AUTHORIZED_IMPORT"      # Formally ingested from approved export


class ObjectiveProfile(str, Enum):
    PROGRAMME_IMPROVEMENT = "PROGRAMME_IMPROVEMENT"  # Routine monthly/weekly planning
    DISRUPTION_RECOVERY = "DISRUPTION_RECOVERY"      # Minimal churn event replanning


class JobState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class SolverStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    TIME_LIMIT = "TIME_LIMIT"
    NOT_SOLVED = "NOT_SOLVED"


class StopReason(str, Enum):
    OPTIMAL_PROVEN = "OPTIMAL_PROVEN"
    TIME_LIMIT_REACHED = "TIME_LIMIT_REACHED"
    INFEASIBILITY_PROVEN = "INFEASIBILITY_PROVEN"
    USER_CANCELLED = "USER_CANCELLED"
    ERROR = "ERROR"


class ValidationVerdict(str, Enum):
    VERIFIED_FEASIBLE = "VERIFIED_FEASIBLE"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    UNKNOWN_BLOCKED = "UNKNOWN_BLOCKED"


class RuleVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"  # Missing evidence; always blocks approval


class PlanStatus(str, Enum):
    DRAFT_PROPOSAL = "DRAFT_PROPOSAL"
    CHECKED_FEASIBLE = "CHECKED_FEASIBLE"
    JOINT_REVIEW = "JOINT_REVIEW"
    APPROVED_PROGRAMME = "APPROVED_PROGRAMME"
    STALE = "STALE"


class ProgrammeAuthorityState(str, Enum):
    PROPOSED = "PROPOSED"
    RECOMMENDED = "RECOMMENDED"
    OPERATING_RATIFIED = "OPERATING_RATIFIED"


class FieldAuthorityState(str, Enum):
    NOT_REQUESTED = "NOT_REQUESTED"
    EXTERNAL_PERMIT_PENDING = "EXTERNAL_PERMIT_PENDING"
    EXTERNAL_PERMIT_GRANTED = "EXTERNAL_PERMIT_GRANTED"
    WORK_IN_PROGRESS = "WORK_IN_PROGRESS"
    CLEARED = "CLEARED"


class ApprovalEligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    BLOCKED_CHECK_FAILED = "BLOCKED_CHECK_FAILED"
    BLOCKED_UNKNOWN_RULE = "BLOCKED_UNKNOWN_RULE"
    BLOCKED_LOCKED_CONFLICT = "BLOCKED_LOCKED_CONFLICT"
    BLOCKED_STALE_INPUT = "BLOCKED_STALE_INPUT"
    BLOCKED_RECONCILIATION_REQUIRED = "BLOCKED_RECONCILIATION_REQUIRED"


class MonthlyPlanStatus(str, Enum):
    ALLOCATED_PROVISIONAL = "ALLOCATED_PROVISIONAL"
    SUPERSEDED = "SUPERSEDED"
    AMENDED = "AMENDED"


class VarianceType(str, Enum):
    CROSS_WEEK_MOVE = "CROSS_WEEK_MOVE"
    EMERGENCY_INTAKE = "EMERGENCY_INTAKE"
    CAPACITY_OVERRUN = "CAPACITY_OVERRUN"
    FEASIBILITY_DISCREPANCY = "FEASIBILITY_DISCREPANCY"
    DEFERRED_TASK = "DEFERRED_TASK"


class ReconciliationStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED_AMENDMENT = "APPROVED_AMENDMENT"
    REJECTED = "REJECTED"


class AllocationReasonCode(str, Enum):
    ALLOCATED = "ALLOCATED"
    UNALLOCATED = "UNALLOCATED"
    INFEASIBLE_IN_DECLARED_DOMAIN = "INFEASIBLE_IN_DECLARED_DOMAIN"
    SEARCH_INCOMPLETE = "SEARCH_INCOMPLETE"


class WeekValidationStatus(str, Enum):
    UNVALIDATED = "UNVALIDATED"
    VALID = "VALID"
    INVALID = "INVALID"
    IN_PROGRESS = "IN_PROGRESS"


class ResourceType(str, Enum):
    MACHINE = "MACHINE"
    CREW = "CREW"
    SPECIAL_EQUIPMENT = "SPECIAL_EQUIPMENT"


class TrackDirection(str, Enum):
    UP = "UP"        # Foxtrot -> Alpha
    DOWN = "DOWN"    # Alpha -> Foxtrot
    BOTH = "BOTH"    # Reversible / bidirectional line


class CompatibilityEffect(str, Enum):
    ALLOWED = "ALLOWED"
    PROHIBITED = "PROHIBITED"
    UNKNOWN = "UNKNOWN"


class ReadinessDimension(str, Enum):
    CREW_COMPETENCE = "CREW_COMPETENCE"
    MACHINE_HEALTH = "MACHINE_HEALTH"
    MATERIAL_AVAILABILITY = "MATERIAL_AVAILABILITY"
    EQUIPMENT_STATUS = "EQUIPMENT_STATUS"
    PREREQUISITE_COMPLETION = "PREREQUISITE_COMPLETION"
    SITE_ACCESS = "SITE_ACCESS"
    PLANNING_ISOLATION = "PLANNING_ISOLATION"
    QUANTITY_SURVEY = "QUANTITY_SURVEY"
    RESTORATION_RESOURCES = "RESTORATION_RESOURCES"


class ReadinessState(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    NOT_READY = "NOT_READY"
    UNKNOWN = "UNKNOWN"


class WorkPhaseType(str, Enum):
    PREPARATION = "PREPARATION"      # Setup, flags, possession takeover, isolation
    EXECUTION = "EXECUTION"          # Active track/OHE/S&T engineering work
    TESTING = "TESTING"              # Joint test, point machine switch test, energization
    RESTORATION = "RESTORATION"      # Site clearance, tool return, track hand-back


class DiagnosticReasonCode(str, Enum):
    INPUT_BLOCKED = "INPUT_BLOCKED"
    CANDIDATE_REJECTED = "CANDIDATE_REJECTED"
    NO_CANDIDATE_IN_DOMAIN = "NO_CANDIDATE_IN_DOMAIN"
    MODEL_INFEASIBLE = "MODEL_INFEASIBLE"
    FEASIBLE_BUT_UNSELECTED = "FEASIBLE_BUT_UNSELECTED"
    SEARCH_INCOMPLETE = "SEARCH_INCOMPLETE"


class ProofStatus(str, Enum):
    PROVEN_CONSTRAINED = "PROVEN_CONSTRAINED"
    PROVEN_SUBOPTIMAL = "PROVEN_SUBOPTIMAL"
    EMPIRICALLY_CONFLICTING = "EMPIRICALLY_CONFLICTING"
    INCONCLUSIVE = "INCONCLUSIVE"


class RepairActionType(str, Enum):
    MOVE_OPTIONAL_UNLOCKED_WORK = "MOVE_OPTIONAL_UNLOCKED_WORK"
    SUBSTITUTE_RESOURCE = "SUBSTITUTE_RESOURCE"
    ALTERNATE_PACKAGE_WINDOW = "ALTERNATE_PACKAGE_WINDOW"
    REQUEST_PARENT_WEEK_AMENDMENT = "REQUEST_PARENT_WEEK_AMENDMENT"


class RepairFeasibilityStatus(str, Enum):
    VERIFIED_FEASIBLE = "VERIFIED_FEASIBLE"
    AWAITING_AUTHORITY = "AWAITING_AUTHORITY"
    INVALID = "INVALID"

