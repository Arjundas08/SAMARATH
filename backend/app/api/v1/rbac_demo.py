"""
Protected endpoints demonstrating role-based access control and isolation guards.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import Permission
from app.schemas.enums import DepartmentType
from app.core.auth import require_permission, require_department, require_territory

router = APIRouter(prefix="/protected", tags=["RBAC Guards"])


@router.post("/plans/{plan_id}/approve")
async def approve_plan_action(
    plan_id: str,
    user: dict = Depends(require_permission(Permission.PROGRAMME_APPROVE)),
):
    """
    Action requiring delegated operational programme approval authority.
    Must succeed for DELEGATED_APPROVER, and fail (403) for INFRASTRUCTURE_ADMIN and DEPARTMENT_PLANNER.
    """
    return {
        "plan_id": plan_id,
        "action": "APPROVED",
        "approved_by": user.get("sub"),
        "status": "APPROVED_PROGRAMME",
    }


@router.post("/departments/{department}/demands")
async def create_departmental_demand(
    department: DepartmentType,
    user: dict = Depends(require_permission(Permission.DEMAND_CREATE)),
):
    """
    Action enforcing departmental isolation.
    """
    # Verify department isolation
    user_dept = user.get("department")
    if user_dept and user_dept != department.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: Department isolation violation. User in '{user_dept}' cannot modify '{department.value}' demands.",
        )

    return {
        "status": "SUCCESS",
        "department": department.value,
        "created_by": user.get("sub"),
    }
