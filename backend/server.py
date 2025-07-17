from fastapi import FastAPI, APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import requests
from cryptography.fernet import Fernet
import json
import asyncio
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Unified Security Console", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

# DefectDojo Configuration
DEFECTDOJO_URL = os.environ.get('DEFECTDOJO_URL', 'https://demo.defectdojo.org')
DEFECTDOJO_API_KEY = os.environ.get('DEFECTDOJO_API_KEY', '548afd6fab3bea9794a41b31da0e9404f733e222')

# Models
class ModuleType(str, Enum):
    XDR = "XDR"
    XDR_PLUS = "XDR+"
    OXDR = "OXDR"
    GSOS = "GSOS"

class AppType(str, Enum):
    DEFECTDOJO = "DefectDojo"
    THEHIVE = "TheHive"
    OPENSEARCH = "OpenSearch"
    WAZUH = "Wazuh"
    SURICATA = "Suricata"
    ELASTIC = "Elastic"
    SPLUNK = "Splunk"
    MISP = "MISP"
    CORTEX = "Cortex"
    CUSTOM = "Custom"

class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    app_name: str
    module: ModuleType
    redirect_url: str
    ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ApplicationCreate(BaseModel):
    app_name: str
    module: ModuleType
    redirect_url: str
    ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None

class ApplicationUpdate(BaseModel):
    app_name: Optional[str] = None
    module: Optional[ModuleType] = None
    redirect_url: Optional[str] = None
    ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []
    module_access: List[ModuleType] = []
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []
    module_access: List[ModuleType] = []
    is_admin: bool = False

class Role(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    defectdojo_id: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DefectDojoUser(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class DefectDojoRole(BaseModel):
    user_id: str
    role_id: int
    product_id: Optional[int] = None

# Helper functions
def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

async def get_defectdojo_headers():
    """Get headers for DefectDojo API requests"""
    return {
        "Authorization": f"Token {DEFECTDOJO_API_KEY}",
        "Content-Type": "application/json"
    }

# DefectDojo API Integration
class DefectDojoService:
    @staticmethod
    async def get_users():
        """Get all users from DefectDojo"""
        headers = await get_defectdojo_headers()
        try:
            response = requests.get(f"{DEFECTDOJO_URL}/api/v2/users/", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching DefectDojo users: {e}")
            return {"results": []}

    @staticmethod
    async def create_user(user_data: DefectDojoUser):
        """Create a user in DefectDojo"""
        headers = await get_defectdojo_headers()
        try:
            response = requests.post(
                f"{DEFECTDOJO_URL}/api/v2/users/",
                json=user_data.dict(),
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error creating DefectDojo user: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create user in DefectDojo: {str(e)}")

    @staticmethod
    async def get_roles():
        """Get all roles from DefectDojo"""
        headers = await get_defectdojo_headers()
        try:
            response = requests.get(f"{DEFECTDOJO_URL}/api/v2/roles/", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching DefectDojo roles: {e}")
            return {"results": []}

    @staticmethod
    async def assign_role(user_id: int, role_data: DefectDojoRole):
        """Assign a role to a user in DefectDojo"""
        headers = await get_defectdojo_headers()
        try:
            # This would typically be a product membership or global role assignment
            # For now, implementing as a placeholder
            response = requests.post(
                f"{DEFECTDOJO_URL}/api/v2/global_roles/",
                json={"user": user_id, "role": role_data.role_id},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error assigning role in DefectDojo: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to assign role in DefectDojo: {str(e)}")

# Authentication (simplified for MVP)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token (simplified implementation)"""
    # For MVP, we'll use a simple token check
    # In production, implement proper JWT validation
    if credentials.credentials == "admin-token":
        return {"username": "admin", "is_admin": True}
    return {"username": "user", "is_admin": False}

# Application Management Routes
@api_router.get("/applications", response_model=List[Application])
async def get_applications():
    """Get all applications"""
    apps = await db.applications.find().to_list(1000)
    return [Application(**app) for app in apps]

@api_router.get("/applications/module/{module}")
async def get_applications_by_module(module: ModuleType):
    """Get applications by module"""
    apps = await db.applications.find({"module": module}).to_list(1000)
    return [Application(**app) for app in apps]

@api_router.post("/applications", response_model=Application)
async def create_application(app_data: ApplicationCreate, current_user: dict = Depends(get_current_user)):
    """Create a new application"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Encrypt sensitive data
    app_dict = app_data.dict()
    if app_dict.get("password"):
        app_dict["password"] = encrypt_data(app_dict["password"])
    if app_dict.get("api_key"):
        app_dict["api_key"] = encrypt_data(app_dict["api_key"])
    
    app_obj = Application(**app_dict)
    await db.applications.insert_one(app_obj.dict())
    return app_obj

@api_router.put("/applications/{app_id}", response_model=Application)
async def update_application(app_id: str, app_data: ApplicationUpdate, current_user: dict = Depends(get_current_user)):
    """Update an application"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get existing application
    existing_app = await db.applications.find_one({"id": app_id})
    if not existing_app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Update fields
    update_data = app_data.dict(exclude_unset=True)
    if update_data.get("password"):
        update_data["password"] = encrypt_data(update_data["password"])
    if update_data.get("api_key"):
        update_data["api_key"] = encrypt_data(update_data["api_key"])
    
    update_data["updated_at"] = datetime.utcnow()
    
    await db.applications.update_one({"id": app_id}, {"$set": update_data})
    updated_app = await db.applications.find_one({"id": app_id})
    return Application(**updated_app)

@api_router.delete("/applications/{app_id}")
async def delete_application(app_id: str, current_user: dict = Depends(get_current_user)):
    """Delete an application"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await db.applications.delete_one({"id": app_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted successfully"}

# User Management Routes
@api_router.get("/users", response_model=List[User])
async def get_users():
    """Get all users"""
    users = await db.users.find().to_list(1000)
    return [User(**user) for user in users]

@api_router.post("/users", response_model=User)
async def create_user(user_data: UserCreate, current_user: dict = Depends(get_current_user)):
    """Create a new user and sync with DefectDojo"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Create user in DefectDojo first
    dojo_user = DefectDojoUser(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    try:
        dojo_response = await DefectDojoService.create_user(dojo_user)
        logging.info(f"Created user in DefectDojo: {dojo_response}")
    except Exception as e:
        logging.error(f"Failed to create user in DefectDojo: {e}")
        # Continue with local user creation even if DefectDojo fails
    
    # Create user locally
    user_obj = User(**user_data.dict())
    await db.users.insert_one(user_obj.dict())
    return user_obj

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get a specific user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

# Role Management Routes
@api_router.get("/roles", response_model=List[Role])
async def get_roles():
    """Get all roles"""
    roles = await db.roles.find().to_list(1000)
    return [Role(**role) for role in roles]

@api_router.post("/roles", response_model=Role)
async def create_role(role_data: Role, current_user: dict = Depends(get_current_user)):
    """Create a new role"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    await db.roles.insert_one(role_data.dict())
    return role_data

# DefectDojo Integration Routes
@api_router.get("/defectdojo/users")
async def get_defectdojo_users():
    """Get users from DefectDojo"""
    return await DefectDojoService.get_users()

@api_router.get("/defectdojo/roles")
async def get_defectdojo_roles():
    """Get roles from DefectDojo"""
    return await DefectDojoService.get_roles()

@api_router.post("/defectdojo/sync-roles")
async def sync_defectdojo_roles(current_user: dict = Depends(get_current_user)):
    """Sync roles from DefectDojo to local database"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dojo_roles = await DefectDojoService.get_roles()
    synced_count = 0
    
    for role in dojo_roles.get("results", []):
        role_obj = Role(
            name=role.get("name", "Unknown"),
            description=f"DefectDojo role: {role.get('name')}",
            defectdojo_id=role.get("id"),
            permissions=["read", "write"]  # Default permissions
        )
        
        # Update or insert role
        await db.roles.update_one(
            {"defectdojo_id": role.get("id")},
            {"$set": role_obj.dict()},
            upsert=True
        )
        synced_count += 1
    
    return {"message": f"Synced {synced_count} roles from DefectDojo"}

# Dashboard Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    app_count = await db.applications.count_documents({})
    user_count = await db.users.count_documents({})
    role_count = await db.roles.count_documents({})
    
    # Count applications by module
    module_stats = {}
    for module in ModuleType:
        count = await db.applications.count_documents({"module": module})
        module_stats[module] = count
    
    return {
        "total_applications": app_count,
        "total_users": user_count,
        "total_roles": role_count,
        "module_stats": module_stats,
        "defectdojo_connected": True,  # Add actual health check
        "last_sync": datetime.utcnow()
    }

# Health Check
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize database and sync roles"""
    logger.info("Starting Unified Security Console...")
    
    # Initialize default roles if none exist
    role_count = await db.roles.count_documents({})
    if role_count == 0:
        default_roles = [
            Role(name="Admin", description="Full system access", permissions=["read", "write", "delete", "admin"]),
            Role(name="User", description="Basic user access", permissions=["read"]),
            Role(name="Viewer", description="Read-only access", permissions=["read"])
        ]
        
        for role in default_roles:
            await db.roles.insert_one(role.dict())
        
        logger.info("Initialized default roles")
    
    # Sync DefectDojo roles
    try:
        await sync_defectdojo_roles({"is_admin": True})
        logger.info("Synced DefectDojo roles on startup")
    except Exception as e:
        logger.error(f"Failed to sync DefectDojo roles on startup: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()