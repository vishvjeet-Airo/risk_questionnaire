from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from ..utils.dependencies import get_current_active_user
from ..models.user import User
from app.models.sector import Sector
from app.models.technology import Technology
from sqlalchemy.orm import Session
from app.database.connection import get_session

router = APIRouter(prefix="", tags=["reference-data"])


class SectorsResponse(BaseModel):
    """Response model for sectors list."""
    status: str = "success"
    status_code: int = 200
    message: str = "Sectors fetched successfully"
    sectors: List[str] = Field(..., description="List of available sectors")
    total_count: int = Field(..., description="Total number of sectors")


class TechnologiesResponse(BaseModel):
    """Response model for technologies list."""
    status: str = "success"
    status_code: int = 200
    message: str = "Technologies fetched successfully"
    technologies: List[str] = Field(..., description="List of available technologies")
    total_count: int = Field(..., description="Total number of technologies")


class ClientSearchResponse(BaseModel):
    """Response model for client search."""
    client_exists: bool = Field(..., description="Whether the client exists in the system")
    client_info: Dict[str, Any] = Field(..., description="Client information if found")

@router.get("/sectors", response_model=SectorsResponse)
async def get_sectors(
    # current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """
    Get list of available sectors.
    
    This endpoint returns a comprehensive list of all available sectors
    that can be used when uploading documents or questionnaires.
    Sectors are used for categorization and matching in the AI processing.
    
    Args:
        current_user: The authenticated user making the request
        
    Returns:
        SectorsResponse containing list of sectors and total count
        
    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 500 if there's an internal server error
        
    Example:
        ```python
        GET /api/sectors
        Authorization: Bearer <token>
        
        Response:
        {
            "sectors": [
                "Technology",
                "Finance",
                "Healthcare",
                "Manufacturing",
                "Retail",
                "Education",
                "Government",
                "Energy",
                "Transportation",
                "Telecommunications"
            ],
            "total_count": 10
        }
        ```
        
    Note:
        The sectors list is maintained by the system administrators
        and may be updated periodically to reflect industry changes.
    """
    # TODO: Implement sectors retrieval logic
    # - Fetch sectors from database or configuration
    # - Return formatted list with count
    # - Consider caching for performance
    
    try:
        # Fetch all sectors ordered by name
        sectors = db.query(Sector).order_by(Sector.name.asc()).all()

        # Extract only sector names
        sector_names = [sector.name for sector in sectors]

        # Count total sectors
        total_count = len(sector_names)

        return SectorsResponse(
            sectors=sector_names,
            total_count=total_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch sectors: {str(e)}"
        )


@router.get("/technologies", response_model=TechnologiesResponse)
async def get_technologies(
    # current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """
    Get list of available technologies.
    
    This endpoint returns a comprehensive list of all available technologies
    that can be used when uploading documents or questionnaires.
    Technologies are used for categorization and matching in the AI processing.
    
    Args:
        current_user: The authenticated user making the request
        
    Returns:
        TechnologiesResponse containing list of technologies and total count
        
    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 500 if there's an internal server error
        
    Example:
        ```python
        GET /api/technologies
        Authorization: Bearer <token>
        
        Response:
        {
            "technologies": [
                "Artificial Intelligence",
                "Machine Learning",
                "Cloud Computing",
                "Blockchain",
                "Internet of Things (IoT)",
                "Cybersecurity",
                "Data Analytics",
                "Mobile Applications",
                "Web Development",
                "DevOps"
            ],
            "total_count": 10
        }
        ```
        
    Note:
        The technologies list is maintained by the system administrators
        and may be updated periodically to reflect technological advances.
    """
    # TODO: Implement technologies retrieval logic
    # - Fetch technologies from database or configuration
    # - Return formatted list with count
    # - Consider caching for performance
    
    try:
        # Fetch all sectors ordered by name
        technologies = db.query(Technology).order_by(Technology.name.asc()).all()

        # Extract only sector names
        technologies_names = [technology.name for technology in technologies]

        # Count total sectors
        total_count = len(technologies_names)

        return TechnologiesResponse(
            technologies=technologies_names,
            total_count=total_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to technologies sectors: {str(e)}"
        )


@router.get("/client/{client_name}", response_model=ClientSearchResponse)
async def search_client(
    client_name: str = Path(..., description="Client name to search for"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Search for client by name to check availability.
    
    This endpoint allows users to search for existing clients by name
    to check if they already exist in the system. This is useful when
    uploading questionnaires to avoid creating duplicate client records.
    
    Args:
        client_name: Name of the client to search for (required)
        current_user: The authenticated user making the request
        
    Returns:
        ClientSearchResponse containing client existence status and information
        
    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 500 if there's an internal server error
        
    Example:
        ```python
        GET /api/client/ABC Corporation
        Authorization: Bearer <token>
        
        Response (Client Found):
        {
            "client_exists": true,
            "client_info": {
                "id": 123,
                "name": "ABC Corporation",
                "email": "contact@abccorp.com",
                "created_at": "2024-01-01T00:00:00Z",
                "total_questionnaires": 5
            }
        }
        
        Response (Client Not Found):
        {
            "client_exists": false,
            "client_info": null
        }
        ```
        
    Note:
        - Search is case-insensitive
        - Partial matches may be supported in future versions
        - Client information is only returned if the client exists
    """
    # TODO: Implement client search logic
    # - Search for client by name (case-insensitive)
    # - Return client information if found
    # - Handle partial matches if needed
    # - Consider fuzzy matching for better UX
    
    # Placeholder implementation
    if client_name.lower() == "abc corporation":
        return ClientSearchResponse(
            client_exists=True,
            client_info={
                "id": 123,
                "name": "ABC Corporation",
                "email": "contact@abccorp.com",
                "created_at": "2024-01-01T00:00:00Z",
                "total_questionnaires": 5
            }
        )
    else:
        return ClientSearchResponse(
            client_exists=False,
            client_info={}
        )
