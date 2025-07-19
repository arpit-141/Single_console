from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

from config import config, AuthType
from models import User

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=config.auth.jwt_expiration_hours)
        
        to_encode.update({"exp": expire, "type": "access_token"})
        encoded_jwt = jwt.encode(to_encode, config.auth.jwt_secret, algorithm=config.auth.jwt_algorithm)
        return encoded_jwt
    
    async def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user with username/password"""
        if config.auth.auth_type == AuthType.SIMPLE:
            return await self._authenticate_simple(username, password)
        elif config.auth.auth_type == AuthType.KEYCLOAK:
            return await self._authenticate_keycloak(username, password)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid authentication type configured"
            )
    
    async def _authenticate_simple(self, username: str, password: str) -> Optional[dict]:
        """Simple authentication against local database"""
        try:
            user_doc = await self.db.users.find_one({"username": username})
            if not user_doc:
                return None
            
            # Check if password field exists, if not, create default password
            if "password_hash" not in user_doc:
                # For backward compatibility, create default password
                if username == "admin":
                    default_password = "admin123"  # Default admin password
                else:
                    default_password = "password123"  # Default user password
                
                password_hash = self.get_password_hash(default_password)
                await self.db.users.update_one(
                    {"username": username},
                    {"$set": {"password_hash": password_hash}}
                )
                user_doc["password_hash"] = password_hash
            
            if not self.verify_password(password, user_doc["password_hash"]):
                return None
            
            return {
                "id": user_doc["id"],
                "username": user_doc["username"],
                "email": user_doc["email"],
                "is_admin": user_doc.get("is_admin", False),
                "roles": user_doc.get("roles", []),
                "module_access": user_doc.get("module_access", [])
            }
        except Exception as e:
            logger.error(f"Error in simple authentication: {e}")
            return None
    
    async def _authenticate_keycloak(self, username: str, password: str) -> Optional[dict]:
        """Keycloak authentication (placeholder for future implementation)"""
        # TODO: Implement Keycloak authentication
        logger.info("Keycloak authentication not implemented yet")
        return None
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """Get current user from JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(credentials.credentials, config.auth.jwt_secret, algorithms=[config.auth.jwt_algorithm])
            username: str = payload.get("sub")
            token_type: str = payload.get("type")
            
            if username is None or token_type != "access_token":
                raise credentials_exception
                
        except JWTError:
            raise credentials_exception
        
        # Get user from database
        user_doc = await self.db.users.find_one({"username": username})
        if user_doc is None:
            raise credentials_exception
            
        return {
            "id": user_doc["id"],
            "username": user_doc["username"],
            "email": user_doc["email"],
            "is_admin": user_doc.get("is_admin", False),
            "roles": user_doc.get("roles", []),
            "module_access": user_doc.get("module_access", [])
        }
    
    async def require_admin(self, current_user: dict = Depends(get_current_user)) -> dict:
        """Dependency that requires admin access"""
        if not current_user.get("is_admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    async def create_default_admin(self):
        """Create default admin user if none exists"""
        try:
            admin_exists = await self.db.users.find_one({"is_admin": True})
            if not admin_exists:
                default_admin = {
                    "id": "admin-001",
                    "username": "admin",
                    "email": "admin@securityconsole.com",
                    "first_name": "System",
                    "last_name": "Administrator",
                    "password_hash": self.get_password_hash("admin123"),
                    "is_admin": True,
                    "roles": ["Admin"],
                    "module_access": ["XDR", "XDR+", "OXDR", "GSOS"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await self.db.users.insert_one(default_admin)
                logger.info("Created default admin user (username: admin, password: admin123)")
        except Exception as e:
            logger.error(f"Error creating default admin: {e}")

# Create a dependency function for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency function to get current user"""
    # This will be injected with the actual auth service in server.py
    pass

async def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency function that requires admin access"""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user