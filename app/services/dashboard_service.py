from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select, or_
from fastapi.responses import JSONResponse
from app.models.questionnaire_file import QuestionnaireFile
from app.models.sector import Sector
from app.models.technology import Technology
from app.models.client import Client

from sqlalchemy import func, select
from app.core.logger import get_logger, log_error

logger = get_logger("app.dashboard")



class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        
    def get_dashboard_stats(self, user_id: int):
        """
        Get dashboard statistics for the given user.
        Dynamically calculates:
        - total_clients
        - completed_questionnaires
        - draft_questionnaires
        - total_uploads
        """
        stats = {
            "total_clients": 0,
            "completed_questionnaires": 0,
            "draft_questionnaires": 0,
            "total_uploads": 0,
        }

        try:
            # Fetch total clients
            stats["total_clients"] = self.db.exec(
                select(func.count(Client.id))
            ).scalar_one()

            # Fetch completed questionnaires for the user
            stats["completed_questionnaires"] = self.db.exec(
                select(func.count(QuestionnaireFile.id)).where(
                    QuestionnaireFile.is_completed == True,
                    QuestionnaireFile.user_id == user_id,
                )
            ).scalar_one()

            # Fetch draft questionnaires for the user
            stats["draft_questionnaires"] = self.db.exec(
                select(func.count(QuestionnaireFile.id)).where(
                    QuestionnaireFile.is_draft == True,
                    QuestionnaireFile.user_id == user_id,
                )
            ).scalar_one()

            # Fetch total uploads for the user
            stats["total_uploads"] = self.db.exec(
                select(func.count(QuestionnaireFile.id)).where(
                    QuestionnaireFile.user_id == user_id,
                )
            ).scalar_one()

        except Exception as e:
            log_error(e, context=f"Dashboard stats computation failed for user_id={user_id}")
            
        # return a valid response
        return JSONResponse(
            status_code=200,
            content={
                "message": "Dashboard statistics fetched successfully.",
                "data": stats,
            },
        )


    def _fetch_questionnaires(
        self,
        user_id: int,
        status_filter: str,  # "draft" or "completed"
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ):
        """
        Internal shared method to fetch questionnaires by status with filters.
        """
        try:
            # Determine condition
            if status_filter == "draft":
                query = select(QuestionnaireFile).where(
                    QuestionnaireFile.user_id == user_id,
                    QuestionnaireFile.is_draft == True,
                )
            elif status_filter == "completed":
                query = select(QuestionnaireFile).where(
                    QuestionnaireFile.user_id == user_id,
                    QuestionnaireFile.is_completed == True,
                )
            else:
                return JSONResponse(
                    status_code=400,
                    content={"message": "Invalid status filter", "data": None},
                )

            # Optional search filter
            if search:
                query = query.where(
                    or_(
                        QuestionnaireFile.filename.ilike(f"%{search}%"),
                        QuestionnaireFile.original_filename.ilike(f"%{search}%"),
                    )
                )

            # Date filters (full-day inclusive)
            if date_from:
                try:
                    from_date = datetime.fromisoformat(date_from)
                    query = query.where(QuestionnaireFile.uploaded_at >= from_date)
                except ValueError:
                    pass

            if date_to:
                try:
                    to_date = datetime.fromisoformat(date_to)
                    to_date = to_date + timedelta(days=1) - timedelta(seconds=1)
                    query = query.where(QuestionnaireFile.uploaded_at <= to_date)
                except ValueError:
                    pass

            # Pagination logic
            count_query = select(func.count()).select_from(query.subquery())
            total = self.db.exec(count_query).one()[0]
            offset = (page - 1) * limit

            results = self.db.exec(query.offset(offset).limit(limit)).scalars().all()

            # Build response
            questionnaire_list = []
            for q in results:
                questionnaire_list.append({
                    "id": q.id,
                    "client_name": q.file_metadata.get("client_name") if q.file_metadata else None,
                    "title": q.original_filename,
                    "sectors": [s.name for s in q.sectors] if q.sectors else [],
                    "technologies": [t.name for t in q.technologies] if q.technologies else [],
                    "created_at": q.uploaded_at.isoformat() if q.uploaded_at else None,
                    "status": status_filter,
                })

            pages = (total // limit) + (1 if total % limit else 0)

            return JSONResponse(
                status_code=200,
                content={
                    "message": f"{status_filter.capitalize()} questionnaires fetched successfully.",
                    "data": {
                        "questionnaires": questionnaire_list,
                        "pagination": {
                            "page": page,
                            "limit": limit,
                            "total": total,
                            "pages": pages,
                        },
                    },
                },
            )

        except Exception as e:
            log_error(
                e,
                context=f"Error fetching {status_filter} questionnaires for user_id={user_id}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "message": f"Error fetching {status_filter} questionnaires.",
                    "data": None,
                },
            )

    # Public wrappers
    def get_draft_questionnaires(self, **kwargs):
        return self._fetch_questionnaires(status_filter="draft", **kwargs)

    def get_completed_questionnaires(self, **kwargs):
        return self._fetch_questionnaires(status_filter="completed", **kwargs)
        
