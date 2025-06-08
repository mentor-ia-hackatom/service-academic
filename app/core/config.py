from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mi API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Configuración de Supabase
    SUPABASE_PASSWORD: str 
    SUPABASE_DB_URL: Optional[str] = None
    
    # Configuración de seguridad
    SECRET_KEY: str = "tu_clave_secreta_aqui"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 días
    
    # Configuración de APIs
    API_AUTH_URL: str
    API_PREDICTION_URL: str
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 