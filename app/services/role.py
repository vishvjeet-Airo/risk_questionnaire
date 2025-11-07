from sqlmodel import Session, select
from fastapi import HTTPException, status, Depends
from app.models.user import Role
from app.schemas.role import RoleCreate, RoleResponse
from app.database.connection import get_session
from app.core.logger import api_logger
from fastapi.responses import JSONResponse


class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role_data: RoleCreate):
        """Add a new role."""
        try:
            existing_role = self.db.exec(
                select(Role).where(Role.name == role_data.name)
            ).first()
            if existing_role:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"message": "Role already exists.", "data": None},
                )

            new_role = Role(
                name=role_data.name,
                description=role_data.description,
            )
            self.db.add(new_role)
            self.db.commit()
            self.db.refresh(new_role)

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "Role created successfully.",
                    "data": {
                        "id": new_role.id,
                        "name": new_role.name,
                        "description": new_role.description,
                    },
                },
            )

        except Exception as e:
            api_logger.exception(f"Error creating role: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Internal server error while creating role.", "data": None},
            )

    def get_roles(self):
        """Fetch all roles."""
        try:
            roles = self.db.exec(select(Role)).all()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Roles fetched successfully.",
                    "data": [
                        {
                            "id": r.id,
                            "name": r.name,
                            "description": r.description,
                        }
                        for r in roles
                    ],
                },
            )
        except Exception as e:
            api_logger.exception(f"Error fetching roles: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "Error fetching roles.", "data": None},
            )


def get_role_service(db: Session = Depends(get_session)) -> RoleService:
    """Dependency to get RoleService."""
    return RoleService(db)
