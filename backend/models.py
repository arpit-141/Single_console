from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Enums
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

# Authentication Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# User Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password_hash: Optional[str] = None
    roles: List[str] = []
    module_access: List[ModuleType] = []
    is_admin: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = []
    module_access: List[ModuleType] = []
    is_admin: bool = False

class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: Optional[List[str]] = None
    module_access: Optional[List[ModuleType]] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str]
    module_access: List[ModuleType]
    is_admin: bool
    is_active: bool
    created_at: datetime

# Application Models
class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    app_name: str
    app_type: AppType
    module: ModuleType
    redirect_url: str
    ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None
    default_port: Optional[int] = None
    is_active: bool = True
    sync_roles: bool = False
    last_role_sync: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ApplicationCreate(BaseModel):
    app_name: str
    app_type: AppType
    module: ModuleType
    redirect_url: str
    ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None
    default_port: Optional[int] = None
    sync_roles: bool = False

class ApplicationUpdate(BaseModel):
    app_name: Optional[str] = None
    app_type: Optional[AppType] = None
    module: Optional[ModuleType] = None
    redirect_url: Optional[str] = None
    ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None
    default_port: Optional[int] = None
    is_active: Optional[bool] = None
    sync_roles: Optional[bool] = None

class ApplicationResponse(BaseModel):
    id: str
    app_name: str
    app_type: AppType
    module: ModuleType
    redirect_url: str
    ip: Optional[str] = None
    description: Optional[str] = None
    default_port: Optional[int] = None
    is_active: bool
    sync_roles: bool
    last_role_sync: Optional[datetime] = None
    created_at: datetime

# Role Models
class Role(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    app_type: Optional[AppType] = None
    external_id: Optional[str] = None  # ID from external system (DefectDojo, etc.)
    is_synced: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    app_type: Optional[AppType] = None

class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str]
    app_type: Optional[AppType] = None
    is_synced: bool
    created_at: datetime

# External Integration Models
class DefectDojoUser(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class DefectDojoRole(BaseModel):
    user_id: str
    role_id: int
    product_id: Optional[int] = None

# Role Sync Models
class RoleSyncRequest(BaseModel):
    app_id: str
    force_sync: bool = False

class RoleSyncResponse(BaseModel):
    app_id: str
    app_name: str
    app_type: AppType
    synced_roles: int
    success: bool
    message: str
    last_sync: datetime