from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"  # This tells Pydantic to ignore extra fields from .env
    
    app_name: str = "Compass Risk Scanner API"
    secret_key: str = "dev-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    # AWS Bedrock configuration
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    #embedding model configuration
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v1"
    vector_dim: int = 1536
    

    # Qdrant configuration
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "compass_group_knowledge"

    aws_bearer_token_bedrock: Optional[str] = None

    
    # Langfuse configuration
    langfuse_secret_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "risk_db"
    
    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        
settings = Settings()
