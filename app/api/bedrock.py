from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from ..services.bedrock_service import BedrockService, get_bedrock_service
from ..utils.dependencies import get_current_active_user
from ..models.user import User

router = APIRouter(prefix="/bedrock", tags=["bedrock"])


@router.get("/test-connection", response_model=Dict[str, Any])
async def test_bedrock_connection(
    bedrock_service: BedrockService = Depends(get_bedrock_service)
):
    """
    Test the connection to Amazon Bedrock service.
    
    This endpoint verifies that:
    - AWS credentials are properly configured
    - The Bedrock service is accessible
    - The configured model can be invoked
    
    Returns:
        Dict containing connection status and details
    """
    try:
        result = bedrock_service.test_connection()
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=result["message"],
                headers={"X-Error-Details": str(result["details"])}
            )
        
        return {
            "success": True,
            "message": "Bedrock connection test successful",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during Bedrock test: {str(e)}"
        )


@router.get("/model-info", response_model=Dict[str, Any])
async def get_model_info(
    bedrock_service: BedrockService = Depends(get_bedrock_service)
):
    """
    Get information about the configured Bedrock model.
    
    Returns:
        Dict containing model configuration details
    """
    try:
        model_info = bedrock_service.get_model_info()
        
        return {
            "success": True,
            "message": "Model information retrieved successfully",
            "data": model_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving model information: {str(e)}"
        )


@router.post("/invoke", response_model=Dict[str, Any])
async def invoke_model(
    prompt: str,
    bedrock_service: BedrockService = Depends(get_bedrock_service)
):
    """
    Invoke the Bedrock model with a custom prompt.
    
    Args:
        prompt: The input prompt for the model
        
    Returns:
        Dict containing the model response
    """
    if not prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty"
        )
    
    try:
        response = bedrock_service._invoke_model(prompt)
        
        return {
            "success": True,
            "message": "Model invocation successful",
            "data": {
                "prompt": prompt,
                "response": response["content"],
                "usage": response.get("usage", {}),
                "model_id": response.get("model_id")
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error invoking model: {str(e)}"
        )
