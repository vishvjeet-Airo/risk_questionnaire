from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Literal
from pydantic import BaseModel, Field
from ..utils.dependencies import get_current_active_user
from ..models.user import User

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    """Request model for feedback submission."""
    type: Literal["bug_report", "feature_request", "general"] = Field(
        ..., 
        description="Type of feedback: bug_report, feature_request, or general"
    )
    subject: str = Field(
        ..., 
        min_length=1, 
        max_length=200, 
        description="Brief subject line for the feedback"
    )
    description: str = Field(
        ..., 
        min_length=10, 
        max_length=2000, 
        description="Detailed description of the feedback"
    )
    priority: Literal["low", "medium", "high"] = Field(
        ..., 
        description="Priority level: low, medium, or high"
    )


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    message: str = Field(..., description="Success message")
    feedback_id: int = Field(..., description="Unique identifier for the submitted feedback")


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit user feedback (low priority feature).
    
    This endpoint allows users to submit various types of feedback including
    bug reports, feature requests, and general feedback. The feedback is
    stored for review and potential action by the development team.
    
    Args:
        feedback: Feedback data including type, subject, description, and priority
        current_user: The authenticated user making the request
        
    Returns:
        FeedbackResponse containing success message and unique feedback ID
        
    Raises:
        HTTPException: 400 if feedback type is invalid or required fields are missing
        HTTPException: 401 if user is not authenticated
        HTTPException: 422 if validation fails (invalid field values, length constraints)
        HTTPException: 500 if there's an internal server error
        
    Example:
        ```python
        POST /api/feedback
        Authorization: Bearer <token>
        Content-Type: application/json
        
        Request Body:
        {
            "type": "bug_report",
            "subject": "Issue with questionnaire upload",
            "description": "Detailed description of the issue",
            "priority": "medium"
        }
        
        Response:
        {
            "message": "Feedback submitted successfully",
            "feedback_id": 123
        }
        ```
        
    Note:
        This is marked as a low priority feature and may have limited
        functionality in the initial implementation.
    """
    # TODO: Implement feedback submission logic
    # - Validate feedback type and priority
    # - Store feedback in database
    # - Send notification to admin team (optional)
    # - Return unique feedback ID
    
    return FeedbackResponse(
        message="Feedback submitted successfully",
        feedback_id=123  # Placeholder ID
    )
