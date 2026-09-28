"""
Authentication endpoints: login, logout, and session inspection.
"""
from fastapi import APIRouter, Response, Request, HTTPException, status, Depends

from app.schemas.auth import LoginRequest, SessionResponse
from app.core.auth import authenticate_user, get_current_user
from app.core.security import create_access_token, generate_csrf_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=SessionResponse)
async def login(login_data: LoginRequest, response: Response):
    """
    Authenticate user and set secure HttpOnly session cookie and CSRF cookie.
    Never exposes raw tokens in response body for localStorage.
    """
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create signed JWT token
    token = create_access_token(
        subject=user["user_id"],
        roles=[r.value for r in user["roles"]],
        permissions=[p.value for p in user["permissions"]],
        department=user["department"],
        territory=user["territory"],
    )

    csrf_token = generate_csrf_token()

    # Set HttpOnly, SameSite=Lax session cookie
    response.set_cookie(
        key="samarath_session",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # Localhost development exception; True in TLS production
        path="/",
        max_age=8 * 3600,
    )

    # Set CSRF cookie (readable by frontend client)
    response.set_cookie(
        key="samarath_csrf",
        value=csrf_token,
        httponly=False,
        samesite="lax",
        secure=False,
        path="/",
        max_age=8 * 3600,
    )

    return SessionResponse(
        user_id=user["user_id"],
        username=user["username"],
        display_name=user["display_name"],
        roles=user["roles"],
        permissions=user["permissions"],
        department=user["department"],
        territory=user["territory"],
        csrf_token=csrf_token,
        is_authenticated=True,
    )


@router.post("/logout")
async def logout(response: Response):
    """
    Terminates session by clearing authentication and CSRF cookies.
    """
    response.delete_cookie("samarath_session", path="/")
    response.delete_cookie("samarath_csrf", path="/")
    return {"message": "Session successfully terminated."}


@router.get("/session", response_model=SessionResponse)
async def get_session(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Returns current authenticated session details.
    """
    csrf_token = request.cookies.get("samarath_csrf", "")
    return SessionResponse(
        user_id=current_user.get("sub", ""),
        username=current_user.get("sub", ""),
        display_name=current_user.get("sub", ""),
        roles=current_user.get("roles", []),
        permissions=current_user.get("permissions", []),
        department=current_user.get("department"),
        territory=current_user.get("territory", "VKC"),
        csrf_token=csrf_token,
        is_authenticated=True,
    )
