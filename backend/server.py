from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
import requests
from cryptography.fernet import Fernet
from datetime import datetime

# Import our custom modules
from config import config, AuthType
from auth import AuthService
from models import *

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
client = AsyncIOMotorClient(config.mongo_url)
db = client[config.db_name]

# Create the main app
app = FastAPI(title="Unified Security Console", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize Auth Service
auth_service = AuthService(db)

# Encryption setup
cipher_suite = Fernet(config.encryption_key.encode())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application Templates
APP_TEMPLATES = {
    AppType.DEFECTDOJO: {
        "name": "DefectDojo",
        "default_port": 8080,
        "description": "Open source vulnerability management tool",
        "auth_type": "api_key",
        "api_endpoints": ["/api/v2/users/", "/api/v2/roles/", "/api/v2/findings/"],
        "supports_role_sync": True,
        "role_sync_endpoint": "/api/v2/roles/"
    },
    AppType.THEHIVE: {
        "name": "TheHive",
        "default_port": 9000,
        "description": "Security incident response platform",
        "auth_type": "api_key",
        "api_endpoints": ["/api/user", "/api/case", "/api/alert"],
        "supports_role_sync": False,
        "role_sync_endpoint": None
    },
    AppType.OPENSEARCH: {
        "name": "OpenSearch",
        "default_port": 9200,
        "description": "Distributed search and analytics engine",
        "auth_type": "basic",
        "api_endpoints": ["/_security/user", "/_security/role", "/_cluster/health"],
        "supports_role_sync": True,
        "role_sync_endpoint": "/_security/role"
    },
    AppType.WAZUH: {
        "name": "Wazuh",
        "default_port": 55000,
        "description": "Open source security monitoring",
        "auth_type": "basic",
        "api_endpoints": ["/security/users", "/security/roles", "/agents"],
        "supports_role_sync": True,
        "role_sync_endpoint": "/security/roles"
    },
    AppType.SURICATA: {
        "name": "Suricata",
        "default_port": 8080,
        "description": "Network threat detection engine",
        "auth_type": "none",
        "api_endpoints": ["/rules", "/alerts", "/stats"],
        "supports_role_sync": False,
        "role_sync_endpoint": None
    },
    AppType.ELASTIC: {
        "name": "Elastic",
        "default_port": 9200,
        "description": "Elasticsearch cluster",
        "auth_type": "basic",
        "api_endpoints": ["/_security/user", "/_security/role", "/_cluster/health"],
        "supports_role_sync": True,
        "role_sync_endpoint": "/_security/role"
    },
    AppType.SPLUNK: {
        "name": "Splunk",
        "default_port": 8089,
        "description": "Data platform for security monitoring",
        "auth_type": "basic",
        "api_endpoints": ["/services/authentication/users", "/services/authorization/roles"],
        "supports_role_sync": True,
        "role_sync_endpoint": "/services/authorization/roles"
    },
    AppType.MISP: {
        "name": "MISP",
        "default_port": 443,
        "description": "Malware information sharing platform",
        "auth_type": "api_key",
        "api_endpoints": ["/users", "/roles", "/events"],
        "supports_role_sync": False,
        "role_sync_endpoint": None
    },
    AppType.CORTEX: {
        "name": "Cortex",
        "default_port": 9001,
        "description": "Observable analysis and response engine",
        "auth_type": "api_key",
        "api_endpoints": ["/api/user", "/api/analyzer", "/api/job"],
        "supports_role_sync": False,
        "role_sync_endpoint": None
    },
    AppType.CUSTOM: {
        "name": "Custom Application",
        "default_port": 8080,
        "description": "Custom security application",
        "auth_type": "custom",
        "api_endpoints": [],
        "supports_role_sync": False,
        "role_sync_endpoint": None
    }
}

# Utility Functions
def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return ""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return ""
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except:
        return encrypted_data  # Return as is if decryption fails

# Override the auth dependency functions
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_service.security)):
    return await auth_service.get_current_user(credentials)

async def require_admin(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Authentication Routes
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """Authenticate user and return JWT token"""
    user = await auth_service.authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(data={"sub": user["username"]})
    return LoginResponse(
        access_token=access_token,
        user=user
    )

@api_router.post("/auth/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    # Verify current password
    user_doc = await db.users.find_one({"username": current_user["username"]})
    if not user_doc or not auth_service.verify_password(password_request.current_password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    new_password_hash = auth_service.get_password_hash(password_request.new_password)
    await db.users.update_one(
        {"username": current_user["username"]},
        {"$set": {"password_hash": new_password_hash, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Password updated successfully"}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    user_doc = await db.users.find_one({"username": current_user["username"]})
    return UserResponse(**user_doc)

@api_router.get("/auth/config")
async def get_auth_config():
    """Get authentication configuration"""
    return {
        "auth_type": config.auth.auth_type,
        "simple_auth_enabled": config.auth.simple_auth_enabled,
        "keycloak_enabled": config.auth.keycloak_server_url is not None
    }

# Application Management Routes
@api_router.get("/applications", response_model=List[ApplicationResponse])
async def get_applications():
    """Get all applications"""
    apps = await db.applications.find({"is_active": True}).to_list(1000)
    return [ApplicationResponse(**app) for app in apps]

@api_router.get("/applications/module/{module}")
async def get_applications_by_module(module: ModuleType):
    """Get applications by module"""
    apps = await db.applications.find({"module": module, "is_active": True}).to_list(1000)
    return [ApplicationResponse(**app) for app in apps]

@api_router.post("/applications", response_model=ApplicationResponse)
async def create_application(
    app_data: ApplicationCreate, 
    current_user: dict = Depends(require_admin)
):
    """Create a new application"""
    # Encrypt sensitive data
    app_dict = app_data.dict()
    if app_dict.get("password"):
        app_dict["password"] = encrypt_data(app_dict["password"])
    if app_dict.get("api_key"):
        app_dict["api_key"] = encrypt_data(app_dict["api_key"])
    
    # Set template defaults if not provided
    template = APP_TEMPLATES.get(app_data.app_type)
    if template and not app_dict.get("default_port"):
        app_dict["default_port"] = template["default_port"]
    if template and not app_dict.get("description"):
        app_dict["description"] = template["description"]
    
    app_obj = Application(**app_dict)
    await db.applications.insert_one(app_obj.dict())
    return ApplicationResponse(**app_obj.dict())

@api_router.put("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: str, 
    app_data: ApplicationUpdate, 
    current_user: dict = Depends(require_admin)
):
    """Update an application"""
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
    return ApplicationResponse(**updated_app)

@api_router.delete("/applications/{app_id}")
async def delete_application(app_id: str, current_user: dict = Depends(require_admin)):
    """Delete an application"""
    result = await db.applications.update_one(
        {"id": app_id}, 
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted successfully"}

# Application Templates and Helper Routes
@api_router.get("/app-templates")
async def get_app_templates():
    """Get available application templates"""
    templates = {}
    for app_type, template in APP_TEMPLATES.items():
        templates[app_type] = {
            "name": template["name"],
            "default_port": template["default_port"],
            "description": template["description"],
            "auth_type": template["auth_type"],
            "supports_role_sync": template["supports_role_sync"]
        }
    return templates

@api_router.get("/app-templates/{app_type}")
async def get_app_template(app_type: AppType):
    """Get specific application template"""
    if app_type not in APP_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    return APP_TEMPLATES[app_type]

# User Management Routes
@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get all users"""
    users = await db.users.find({"is_active": True}).to_list(1000)
    return [UserResponse(**user) for user in users]

@api_router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, current_user: dict = Depends(require_admin)):
    """Create a new user"""
    # Check if username already exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password
    user_dict = user_data.dict()
    user_dict["password_hash"] = auth_service.get_password_hash(user_data.password)
    del user_dict["password"]  # Remove plain password
    
    user_obj = User(**user_dict)
    await db.users.insert_one(user_obj.dict())
    
    # Try to sync with DefectDojo
    if config.defectdojo_api_key:
        try:
            await sync_user_with_defectdojo(user_obj.dict())
        except Exception as e:
            logger.warning(f"Failed to sync user with DefectDojo: {e}")
    
    return UserResponse(**user_obj.dict())

@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific user"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, 
    user_data: UserUpdate, 
    current_user: dict = Depends(require_admin)
):
    """Update a user"""
    update_data = user_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.users.update_one({"id": user_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await db.users.find_one({"id": user_id})
    return UserResponse(**updated_user)

# Role Management Routes
@api_router.get("/roles", response_model=List[RoleResponse])
async def get_roles():
    """Get all roles"""
    roles = await db.roles.find().to_list(1000)
    return [RoleResponse(**role) for role in roles]

@api_router.post("/roles", response_model=RoleResponse)
async def create_role(role_data: RoleCreate, current_user: dict = Depends(require_admin)):
    """Create a new role"""
    role_obj = Role(**role_data.dict())
    await db.roles.insert_one(role_obj.dict())
    return RoleResponse(**role_obj.dict())

# Role Synchronization Routes
@api_router.post("/applications/{app_id}/sync-roles", response_model=RoleSyncResponse)
async def sync_application_roles(
    app_id: str,
    sync_request: Optional[RoleSyncRequest] = None,
    current_user: dict = Depends(require_admin)
):
    """Sync roles from an application"""
    app = await db.applications.find_one({"id": app_id})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    
    app_type = app["app_type"]
    template = APP_TEMPLATES.get(app_type)
    
    if not template or not template.get("supports_role_sync"):
        raise HTTPException(
            status_code=400, 
            detail=f"Role synchronization not supported for {app_type}"
        )
    
    try:
        if app_type == AppType.DEFECTDOJO:
            synced_count = await sync_defectdojo_roles(app)
        else:
            # Placeholder for other app types
            synced_count = 0
            logger.info(f"Role sync for {app_type} not implemented yet")
        
        # Update last sync time
        await db.applications.update_one(
            {"id": app_id},
            {"$set": {"last_role_sync": datetime.utcnow()}}
        )
        
        return RoleSyncResponse(
            app_id=app_id,
            app_name=app["app_name"],
            app_type=app_type,
            synced_roles=synced_count,
            success=True,
            message=f"Successfully synced {synced_count} roles",
            last_sync=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error syncing roles for {app_id}: {e}")
        return RoleSyncResponse(
            app_id=app_id,
            app_name=app["app_name"],
            app_type=app_type,
            synced_roles=0,
            success=False,
            message=f"Failed to sync roles: {str(e)}",
            last_sync=datetime.utcnow()
        )

# Helper functions for external integrations
async def sync_defectdojo_roles(app: dict) -> int:
    """Sync roles from DefectDojo"""
    headers = {
        "Authorization": f"Token {decrypt_data(app.get('api_key', '')) or config.defectdojo_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        base_url = app.get("redirect_url", config.defectdojo_url).rstrip("/")
        response = requests.get(f"{base_url}/api/v2/roles/", headers=headers)
        response.raise_for_status()
        
        roles_data = response.json()
        synced_count = 0
        
        for role in roles_data.get("results", []):
            role_obj = Role(
                name=f"DD_{role.get('name', 'Unknown')}",
                description=f"DefectDojo role: {role.get('name')}",
                permissions=["read", "write"],
                app_type=AppType.DEFECTDOJO,
                external_id=str(role.get("id")),
                is_synced=True
            )
            
            # Update or insert role
            await db.roles.update_one(
                {"external_id": str(role.get("id")), "app_type": AppType.DEFECTDOJO},
                {"$set": role_obj.dict()},
                upsert=True
            )
            synced_count += 1
        
        return synced_count
        
    except Exception as e:
        logger.error(f"Error syncing DefectDojo roles: {e}")
        raise

async def sync_user_with_defectdojo(user: dict):
    """Sync user with DefectDojo"""
    headers = {
        "Authorization": f"Token {config.defectdojo_api_key}",
        "Content-Type": "application/json"
    }
    
    user_data = {
        "username": user["username"],
        "email": user["email"],
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", "")
    }
    
    try:
        response = requests.post(
            f"{config.defectdojo_url}/api/v2/users/",
            json=user_data,
            headers=headers
        )
        response.raise_for_status()
        logger.info(f"Successfully synced user {user['username']} with DefectDojo")
    except requests.exceptions.RequestException as e:
        logger.warning(f"Failed to sync user with DefectDojo: {e}")
        # Don't raise, as this is not critical

# Dashboard Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    app_count = await db.applications.count_documents({"is_active": True})
    user_count = await db.users.count_documents({"is_active": True})
    role_count = await db.roles.count_documents({})
    
    # Count applications by module
    module_stats = {}
    for module in ModuleType:
        count = await db.applications.count_documents({"module": module, "is_active": True})
        module_stats[module] = count
    
    return {
        "total_applications": app_count,
        "total_users": user_count,
        "total_roles": role_count,
        "module_stats": module_stats,
        "defectdojo_connected": bool(config.defectdojo_api_key),
        "last_sync": datetime.utcnow(),
        "auth_type": config.auth.auth_type
    }

# Health Check
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "2.0.0",
        "auth_type": config.auth.auth_type
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

@app.on_event("startup")
async def startup_event():
    """Initialize database and create default data"""
    logger.info("Starting Unified Security Console v2.0...")
    
    # Create default admin user
    await auth_service.create_default_admin()
    
    # Initialize default roles if none exist
    role_count = await db.roles.count_documents({})
    if role_count == 0:
        default_roles = [
            Role(name="Admin", description="Full system access", permissions=["read", "write", "delete", "admin"]),
            Role(name="User", description="Basic user access", permissions=["read"]),
            Role(name="Viewer", description="Read-only access", permissions=["read"]),
            Role(name="Security Analyst", description="Security operations access", permissions=["read", "write"]),
            Role(name="SOC Manager", description="SOC team management access", permissions=["read", "write", "manage_users"])
        ]
        
        for role in default_roles:
            await db.roles.insert_one(role.dict())
        
        logger.info("Initialized default roles")
    
    # Create sample DefectDojo application if none exists
    app_count = await db.applications.count_documents({"app_type": AppType.DEFECTDOJO})
    if app_count == 0:
        sample_app = Application(
            app_name="DefectDojo Demo",
            app_type=AppType.DEFECTDOJO,
            module=ModuleType.XDR,
            redirect_url=config.defectdojo_url,
            description="Demo DefectDojo instance for vulnerability management",
            api_key=encrypt_data(config.defectdojo_api_key),
            default_port=8080,
            sync_roles=True
        )
        await db.applications.insert_one(sample_app.dict())
        logger.info("Created sample DefectDojo application")
    
    logger.info(f"Authentication mode: {config.auth.auth_type}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()