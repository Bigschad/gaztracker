"""
RBAC (Role-Based Access Control) Middleware

Decorators and dependencies for role-based access control.
"""

from typing import List
from fastapi import Depends, HTTPException, status
from functools import wraps

from app.models.user import User, UserRole
from app.middleware.auth_middleware import get_current_active_user


def require_roles(*allowed_roles: UserRole):
    """
    Dependency factory to require specific roles.
    
    Args:
        *allowed_roles: Roles that are allowed to access the endpoint
        
    Returns:
        Dependency function that checks user role
        
    Example:
        @app.get("/admin", dependencies=[Depends(require_roles(UserRole.ADMIN))])
        async def admin_endpoint():
            return {"message": "Admin only"}
    """
    async def check_role(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    
    return check_role


def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to require admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current user if admin
        
    Raises:
        HTTPException: 403 if user is not admin
        
    Example:
        @app.get("/admin")
        async def admin_endpoint(user: User = Depends(require_admin)):
            return {"message": "Admin access granted"}
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_any_role(*allowed_roles: UserRole):
    """
    Dependency factory to require any of the specified roles.

    Args:
        *allowed_roles: Roles allowed to access

    Returns:
        Dependency function

    Example:
        require_manager = require_any_role(UserRole.ADMIN, UserRole.RESPONSABLE_LOGISTIQUE)

        @app.get("/manage", dependencies=[Depends(require_manager)])
        async def management_endpoint():
            return {"message": "Manager access"}
    """
    return require_roles(*allowed_roles)


def require_role(allowed_role_names: List[str]):
    """
    Dependency factory to require specific roles (accepts role names as strings).

    Args:
        allowed_role_names: List of role names as strings (e.g., ["ADMIN", "RESPONSABLE_LOGISTIQUE"])

    Returns:
        Dependency function that checks user role

    Example:
        @app.get("/protected")
        async def protected_route(user: User = Depends(require_role(["ADMIN"]))):
            return {"message": "Protected"}
    """
    # Convert string role names to UserRole enums
    allowed_roles = []
    for role_name in allowed_role_names:
        try:
            allowed_roles.append(UserRole(role_name))
        except ValueError:
            # Invalid role name, skip it
            pass

    return require_roles(*allowed_roles)


# Role permission matrix for future fine-grained permissions
ROLE_PERMISSIONS = {
    UserRole.ADMIN: ["*"],  # All permissions
    UserRole.RESPONSABLE_LOGISTIQUE: [
        "expedition:*",
        "palette:read",
        "palette:create",
        "palette:update",
        "user:read",
        "report:read",
    ],
    UserRole.OPERATEUR_USINE: [
        "palette:read",
        "palette:create",
        "palette:scan",
        "expedition:read",
    ],
    UserRole.CHAUFFEUR: [
        "palette:read",
        "palette:scan",
        "expedition:read",
        "expedition:update",
    ],
    UserRole.GROSSISTE: [
        "expedition:read",
        "expedition:validate",
        "palette:read",
    ],
}


def has_permission(user: User, permission: str) -> bool:
    """
    Check if user has a specific permission.
    
    Args:
        user: User to check
        permission: Permission string (e.g., "palette:create")
        
    Returns:
        bool: True if user has permission
        
    Example:
        if has_permission(current_user, "palette:create"):
            # Allow palette creation
    """
    user_permissions = ROLE_PERMISSIONS.get(user.role, [])
    
    # Check for wildcard permission
    if "*" in user_permissions:
        return True
    
    # Check for specific permission
    if permission in user_permissions:
        return True
    
    # Check for resource wildcard (e.g., "palette:*")
    resource = permission.split(":")[0]
    if f"{resource}:*" in user_permissions:
        return True
    
    return False


def require_permission(permission: str):
    """
    Dependency factory to require a specific permission.
    
    Args:
        permission: Permission required (e.g., "palette:create")
        
    Returns:
        Dependency function
        
    Example:
        @app.post("/palettes", dependencies=[Depends(require_permission("palette:create"))])
        async def create_palette():
            return {"message": "Palette created"}
    """
    async def check_permission(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
        return current_user
    
    return check_permission
