"""
Authentication, Identity, and RBAC schemas.
"""
from typing import List, Optional
from enum import Enum
from pydantic import Field

from app.schemas.common import APIModel


class UserRole(str, Enum):
    DEPARTMENT_PLANNER = "DEPARTMENT_PLANNER"
    CORRIDOR_COORDINATOR = "CORRIDOR_COORDINATOR"
    OPERATING_REVIEWER = "OPERATING_REVIEWER"
    DELEGATED_APPROVER = "DELEGATED_APPROVER"
    INTEGRATION_OPERATOR = "INTEGRATION_OPERATOR"
    RULE_AUTHOR = "RULE_AUTHOR"
    RULE_APPROVER = "RULE_APPROVER"
    AUDITOR = "AUDITOR"
    INFRASTRUCTURE_ADMIN = "INFRASTRUCTURE_ADMIN"


class Permission(str, Enum):
    DEMAND_READ = "DEMAND_READ"
    DEMAND_CREATE = "DEMAND_CREATE"
    DEMAND_MUTATE = "DEMAND_MUTATE"
    TIMETABLE_READ = "TIMETABLE_READ"
    TIMETABLE_MUTATE = "TIMETABLE_MUTATE"
    SOLVE_TRIGGER = "SOLVE_TRIGGER"
    PROGRAMME_REVIEW = "PROGRAMME_REVIEW"
    PROGRAMME_APPROVE = "PROGRAMME_APPROVE"
    RULE_EDIT = "RULE_EDIT"
    RULE_APPROVE = "RULE_APPROVE"
    AUDIT_READ = "AUDIT_READ"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"


class LoginRequest(APIModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4)


class SessionResponse(APIModel):
    user_id: str
    username: str
    display_name: str
    roles: List[UserRole]
    permissions: List[Permission]
    department: Optional[str] = None
    territory: str = "VKC"
    csrf_token: str
    is_authenticated: bool = True


UserSession = SessionResponse

