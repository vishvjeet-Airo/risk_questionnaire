from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.bedrock import router as bedrock_router
from app.api.dashboard import router as dashboard_router
from app.api.feedback import router as feedback_router
from app.api.knowledge_base import router as knowledge_base_router
from app.api.questionnaire import router as questionnaire_router
from app.api.reference_data import router as reference_data_router
from app.database.connection import create_db_and_tables
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered risk questionnaire scanner",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(bedrock_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(knowledge_base_router, prefix="/api")
app.include_router(questionnaire_router, prefix="/api")
app.include_router(reference_data_router, prefix="/api")

# Create database tables on startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Risk Questionnaire AI Scanner"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
