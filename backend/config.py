import os
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class AuthType(str, Enum):
    SIMPLE = "simple"
    KEYCLOAK = "keycloak"

class AuthConfig(BaseModel):
    auth_type: AuthType = AuthType.SIMPLE
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Simple Auth Config
    simple_auth_enabled: bool = True
    
    # Keycloak Config (for future use)
    keycloak_server_url: Optional[str] = None
    keycloak_realm: Optional[str] = None
    keycloak_client_id: Optional[str] = None
    keycloak_client_secret: Optional[str] = None

class AppConfig(BaseModel):
    # Database
    mongo_url: str
    db_name: str
    
    # Security
    encryption_key: str
    
    # External Integrations
    defectdojo_url: str
    defectdojo_api_key: str
    
    # Authentication
    auth: AuthConfig

def load_config() -> AppConfig:
    """Load configuration from environment variables"""
    
    # Load auth configuration
    auth_config = AuthConfig(
        auth_type=AuthType(os.environ.get('AUTH_TYPE', 'simple')),
        jwt_secret=os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production'),
        jwt_algorithm=os.environ.get('JWT_ALGORITHM', 'HS256'),
        jwt_expiration_hours=int(os.environ.get('JWT_EXPIRATION_HOURS', '24')),
        simple_auth_enabled=os.environ.get('SIMPLE_AUTH_ENABLED', 'true').lower() == 'true',
        keycloak_server_url=os.environ.get('KEYCLOAK_SERVER_URL'),
        keycloak_realm=os.environ.get('KEYCLOAK_REALM'),
        keycloak_client_id=os.environ.get('KEYCLOAK_CLIENT_ID'),
        keycloak_client_secret=os.environ.get('KEYCLOAK_CLIENT_SECRET')
    )
    
    return AppConfig(
        mongo_url=os.environ.get('MONGO_URL', 'mongodb://localhost:27017'),
        db_name=os.environ.get('DB_NAME', 'security_console'),
        encryption_key=os.environ.get('ENCRYPTION_KEY', 'syILT6dNCzVOHbrvznENmpBrx9g2oxg0_5lNWs_Q6LQ='),
        defectdojo_url=os.environ.get('DEFECTDOJO_URL', 'https://demo.defectdojo.org'),
        defectdojo_api_key=os.environ.get('DEFECTDOJO_API_KEY', '548afd6fab3bea9794a41b31da0e9404f733e222'),
        auth=auth_config
    )

# Global config instance
config = load_config()