import os
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_FILE = os.path.join(BACKEND_DIR, "app.db")
# Ensure normalized forward slashes for SQLite URL on Windows
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_FILE.replace(os.sep, '/')}"

class Settings(BaseModel):
    app_name: str = "Document Intake Assistant"
    app_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Provider settings: "mock", "openai", "gemini"
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock").lower()
    
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    database_url: str = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
    db_file_path: str = DEFAULT_DB_FILE

    cors_origins: List[str] = [
        origin.strip() 
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if origin.strip()
    ]

settings = Settings()
