"""
Authentication dependencies, user bootstrap, and role-based access control (RBAC).
"""
from typing import Dict, Any, List, Optional
from fastapi import Request, HTTPException, status, Depends
from jose import JWTError

from app.schemas.auth import UserRole, Permission, SessionResponse
from app.schemas.enums import DepartmentType
from app.core.security import decode_access_token, hash_password, verify_password

# Bootstrap mock users for testing & demonstration
# In production, users are authenticated via Keycloak OIDC
BOOTSTRAP_USERS: Dict[str, Dict[str, Any]] = {
    "planner_tms": {
        "user_id": "usr-001-tms",
        "username": "planner_tms",
        "display_name": "R. K. Sharma (P-Way / Track)",
        "password_hash": hash_password("tms@pass2026"),
        "roles": [UserRole.DEPARTMENT_PLANNER],
        "permissions": [
            Permission.DEMAND_READ,
            Permission.DEMAND_CREATE,
            Permission.DEMAND_MUTATE,
            Permission.TIMETABLE_READ,
        ],
        "department": "ENGINEERING",
        "territory": "VKC",
    },
    "planner_smms": {
        "user_id": "usr-002-smms",
        "username": "planner_smms",
        "display_name": "Anita Verma (S&T / Signalling)",
        "password_hash": hash_password("smms@pass2026"),
        "roles": [UserRole.DEPARTMENT_PLANNER],
        "permissions": [
            Permission.DEMAND_READ,
            Permission.DEMAND_CREATE,
            Permission.DEMAND_MUTATE,
            Permission.TIMETABLE_READ,
        ],
        "department": "SIGNALLING",
        "territory": "VKC",
    },
    "planner_tdms": {
        "user_id": "usr-003-tdms",
        "username": "planner_tdms",
        "display_name": "V. Suresh (TRD / OHE)",
        "password_hash": hash_password("tdms@pass2026"),
        "roles": [UserRole.DEPARTMENT_PLANNER],
        "permissions": [
            Permission.DEMAND_READ,
            Permission.DEMAND_CREATE,
            Permission.DEMAND_MUTATE,
            Permission.TIMETABLE_READ,
        ],
        "department": "ELECTRICAL",
        "territory": "VKC",
    },
    "coordinator_vkc": {
        "user_id": "usr-004-coord",
        "username": "coordinator_vkc",
        "display_name": "Deepak Mehta (Joint Corridor Coordinator)",
        "password_hash": hash_password("coord@pass2026"),
        "roles": [UserRole.CORRIDOR_COORDINATOR],
        "permissions": [
            Permission.DEMAND_READ,
            Permission.TIMETABLE_READ,
            Permission.SOLVE_TRIGGER,
            Permission.PROGRAMME_REVIEW,
        ],
        "department": None,
        "territory": "VKC",
    },
    "reviewer_operating": {
        "user_id": "usr-005-rev",
        "username": "reviewer_operating",
        "display_name": "S. Chatterjee (Section Controller / Operating)",
        "password_hash": hash_password("rev@pass2026"),
        "roles": [UserRole.OPERATING_REVIEWER],
        "permissions": [
            Permission.DEMAND_READ,
            Permission.TIMETABLE_READ,
            Permission.TIMETABLE_MUTATE,
            Permission.SOLVE_TRIGGER,
            Permission.PROGRAMME_REVIEW,
        ],
        "department": None,
        "territory": "VKC",
    },
    "approver_operating": {
        "user_id": "usr-006-appr",
        "username": "approver_operating",
        "display_name": "Arun Kumar (Sr. DOM / Programme Approver)",
        "password_hash": hash_password("appr@pass2026"),
        "roles": [UserRole.DELEGATED_APPROVER],
        "permissions": [
            Permission.DEMAND_READ,
            Permission.TIMETABLE_READ,
            Permission.PROGRAMME_REVIEW,
            Permission.PROGRAMME_APPROVE,  # Statutory authority to approve rolling programmes
            Permission.AUDIT_READ,
        ],
        "department": None,
        "territory": "VKC",
    },
    "admin_infra": {
        "user_id": "usr-009-admin",
        "username": "admin_infra",
        "display_name": "System Administrator",
        "password_hash": hash_password("admin@pass2026"),
        "roles": [UserRole.INFRASTRUCTURE_ADMIN],
        "permissions": [
            Permission.SYSTEM_ADMIN,
            Permission.AUDIT_READ,
            # Note Invariant: INFRASTRUCTURE_ADMIN does NOT have PROGRAMME_APPROVE permission
        ],
        "department": None,
        "territory": "VKC",
    },
}


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = BOOTSTRAP_USERS.get(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Extracts session from HttpOnly cookie or Authorization Bearer header.
    Validates token integrity and expiry.
    """
    token = request.cookies.get("samarath_session")
    if not token:
        # Check Authorization header as fallback for API integration
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not found in session cookie or header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid session token or expired: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def require_authenticated(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    return current_user


def require_permission(required_perm: Permission):
    def dependency(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_perms = user.get("permissions", [])
        if required_perm.value not in user_perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires '{required_perm.value}' permission.",
            )
        return user
    return dependency


def require_department(dept: DepartmentType):
    """
    Enforces department-scoped mutation isolation.
    A planner in TMS cannot mutate SMMS or TDMS records.
    """
    def dependency(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_dept = user.get("department")
        # Global roles without specific department (e.g. coordinator) pass if permitted
        if user_dept and user_dept != dept.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Department isolation violation. User in '{user_dept}' cannot modify '{dept.value}' demands.",
            )
        return user
    return dependency


def require_territory(territory: str):
    """
    Enforces territory-scoped isolation.
    """
    def dependency(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_terr = user.get("territory")
        if user_terr and user_terr != territory:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Territory isolation violation. User in '{user_terr}' cannot access '{territory}'.",
            )
        return user
    return dependency
