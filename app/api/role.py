from fastapi import APIRouter, Depends, status
from app.schemas.role import RoleCreate, RoleResponse
from app.services.role import RoleService, get_role_service
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    role_service: RoleService = Depends(get_role_service)
):
    """Create a new role."""
    return role_service.create_role(role_data)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_roles(
    role_service: RoleService = Depends(get_role_service)
):
    """Get all roles."""
    return role_service.get_roles()
