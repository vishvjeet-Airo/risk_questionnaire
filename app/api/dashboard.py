from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from ..utils.dependencies import get_current_active_user
from ..models.user import User
from sqlmodel import Session
from fastapi.responses import JSONResponse
from ..database.connection import get_session
from ..utils.dependencies import get_current_user
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieves overall dashboard statistics for the logged-in user.
    """
    service = DashboardService(db)
    return service.get_dashboard_stats(user_id=current_user.id)


@router.get("/draft_questionnaires")
def get_draft_questionnaires(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieves draft questionnaires for the current user with filters.
    """
    service = DashboardService(db)
    return service.get_draft_questionnaires(
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/completed_questionnaires")
def get_completed_questionnaires(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    search: str = Query(None),
    date_from: str = Query(None),
    date_to: str = Query(None),
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieves completed questionnaires for the current user with filters.
    """
    service = DashboardService(db)
    return service.get_completed_questionnaires(
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )