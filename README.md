# Here are your Instructions
# 🛡️ Unified Security Console v2.0

A production-ready centralized web application for managing and integrating multiple security tools with configurable authentication, role-based access control, and generic application templates.

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+** and **Yarn**
- **MongoDB** (local or remote)

### 1. Clone and Setup Backend

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file with your configurations
```

### 2. Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
yarn install

# The .env file should already contain the correct backend URL
```

### 3. Start Services

**Option A: Manual Start**
```bash
# Terminal 1 - Start MongoDB (if local)
mongod

# Terminal 2 - Start Backend
cd backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3 - Start Frontend
cd frontend
yarn start
```

**Option B: Using Supervisor (Recommended)**
```bash
# Start all services
sudo supervisorctl start all

# Check status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.*.log
tail -f /var/log/supervisor/frontend.*.log
```

## 🔐 Default Credentials

After starting the application, use these credentials to log in:

- **URL**: http://localhost:3000 (or your configured frontend URL)
- **Username**: `admin`
- **Password**: `admin123`

> ⚠️ **Security Note**: Change the default password immediately after first login!

## ⚙️ Configuration

### Backend Environment Variables (.env)

```bash
# Database Configuration
MONGO_URL="mongodb://localhost:27017"
DB_NAME="security_console"

# Authentication Settings
AUTH_TYPE="simple"                    # "simple" or "keycloak"
JWT_SECRET="your-super-secret-jwt-key-change-in-production-2024"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS="24"
SIMPLE_AUTH_ENABLED="true"

# Security
ENCRYPTION_KEY="syILT6dNCzVOHbrvznENmpBrx9g2oxg0_5lNWs_Q6LQ="

# DefectDojo Integration (Optional)
DEFECTDOJO_URL="https://demo.defectdojo.org"
DEFECTDOJO_API_KEY="your-defectdojo-api-key"

# Keycloak Configuration (Future Use)
KEYCLOAK_SERVER_URL=""
KEYCLOAK_REALM=""
KEYCLOAK_CLIENT_ID=""
KEYCLOAK_CLIENT_SECRET=""
```

### Frontend Environment Variables (.env)

```bash
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
```

## 🎯 Key Features

### ✅ **Authentication System**
- **JWT-based Authentication** with secure token management
- **Configurable Auth Types**: Switch between Simple Auth and Keycloak
- **Password Security**: bcrypt hashing with secure password change
- **Protected Routes**: Role-based access control throughout the app

### ✅ **Application Management**
- **10+ Security Tool Templates**: DefectDojo, TheHive, OpenSearch, Wazuh, etc.
- **Template-Based Creation**: Automated configuration from predefined templates
- **Role Synchronization**: Sync roles from external security applications
- **Module Organization**: XDR, XDR+, OXDR, GSOS security modules

### ✅ **User & Role Management**
- **Module-Based Access Control**: Fine-grained permissions per security module
- **Dynamic Role Assignment**: Import and assign roles from external systems
- **User Hierarchy**: Admin and regular user permission levels
- **Bulk Operations**: Efficient user and application management

### ✅ **Production-Ready Features**
- **Secure Credential Storage**: Encrypted API keys and passwords
- **Comprehensive Error Handling**: Proper HTTP status codes and messages
- **Health Monitoring**: System status and integration health checks
- **Audit Logging**: Track user actions and system events

## 🏗️ Application Architecture

### Backend Stack
- **FastAPI**: High-performance async web framework
- **MongoDB**: Document database with Motor async driver
- **JWT Authentication**: Secure token-based authentication
- **Pydantic Models**: Data validation and serialization
- **Cryptography**: Secure encryption for sensitive data

### Frontend Stack
- **React 19**: Modern React with hooks and context
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing with protected routes
- **Axios**: HTTP client for API communication
- **Context API**: State management for authentication

## 📱 Using the Application

### 1. **Dashboard**
- View all configured security applications organized by modules
- Quick access to application statistics and system health
- Module-based access control (users see only authorized modules)

### 2. **Application Management**
- **Browse Applications**: View all configured security tools
- **Filter & Search**: Find applications by name, type, or module
- **Launch Applications**: Direct links to external security tools
- **Role Synchronization**: Sync roles from external applications

### 3. **Admin Panel** (Admin Only)
- **Add Applications**: Create new applications using templates
- **User Management**: Create and manage user accounts
- **Role Management**: View and organize synced roles
- **System Configuration**: Manage application settings

### 4. **User Management**
- **User Profiles**: View user details and permissions
- **Module Access**: See which modules users can access
- **Role Assignments**: View roles assigned to each user

## 🔧 API Documentation

### Authentication Endpoints

```bash
# Login
POST /api/auth/login
{
  "username": "admin",
  "password": "admin123"
}

# Get Current User
GET /api/auth/me
Authorization: Bearer <token>

# Change Password
POST /api/auth/change-password
Authorization: Bearer <token>
{
  "current_password": "admin123",
  "new_password": "newpassword"
}

# Get Auth Configuration
GET /api/auth/config
```

### Application Management

```bash
# Get All Applications
GET /api/applications

# Create Application
POST /api/applications
Authorization: Bearer <token>
{
  "app_name": "My DefectDojo",
  "app_type": "DefectDojo",
  "module": "XDR",
  "redirect_url": "https://my-defectdojo.com",
  "api_key": "your-api-key",
  "sync_roles": true
}

# Sync Application Roles
POST /api/applications/{app_id}/sync-roles
Authorization: Bearer <token>

# Get Application Templates
GET /api/app-templates
```

### User & Role Management

```bash
# Get All Users
GET /api/users
Authorization: Bearer <token>

# Create User
POST /api/users
Authorization: Bearer <token>
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "module_access": ["XDR", "OXDR"],
  "is_admin": false
}

# Get All Roles
GET /api/roles
Authorization: Bearer <token>
```

## 🛠️ Supported Security Tools

The system includes templates for these security applications:

| Tool | Description | Role Sync | Auth Type |
|------|-------------|-----------|-----------|
| **DefectDojo** | Vulnerability management | ✅ | API Key |
| **TheHive** | Incident response platform | 🏗️ | API Key |
| **OpenSearch** | Search & analytics engine | 🏗️ | Basic Auth |
| **Wazuh** | Security monitoring | 🏗️ | Basic Auth |
| **Elastic** | Elasticsearch cluster | 🏗️ | Basic Auth |
| **Splunk** | Data analytics platform | 🏗️ | Basic Auth |
| **MISP** | Threat intelligence | 🏗️ | API Key |
| **Cortex** | Observable analysis | 🏗️ | API Key |
| **Suricata** | Network detection | 🏗️ | None |
| **Custom** | Custom applications | 🏗️ | Custom |

> 📝 **Note**: ✅ = Fully implemented, 🏗️ = Template ready (implementation needed)

## 🧪 Testing

### Backend Testing
```bash
# Run backend tests
cd backend
python backend_test.py

# Expected output: All 28 tests should pass
```

### Manual Testing Checklist
- [ ] Login with admin/admin123
- [ ] Change password
- [ ] Create a new user
- [ ] Add a new application using template
- [ ] Sync roles from DefectDojo (if configured)
- [ ] Test module-based access control
- [ ] Verify protected routes work

## 🚨 Troubleshooting

### Common Issues

**1. Backend won't start**
```bash
# Check Python dependencies
pip install -r requirements.txt

# Check MongoDB connection
mongo --eval "db.adminCommand('ismaster')"

# Check environment variables
cat backend/.env
```

**2. Frontend won't start**
```bash
# Clear node modules and reinstall
rm -rf node_modules yarn.lock
yarn install

# Check backend URL in .env
cat frontend/.env
```

**3. Login not working**
```bash
# Check if default admin user was created
# Look in backend logs for: "Created default admin user"

# Verify JWT secret is set
grep JWT_SECRET backend/.env
```

**4. Applications not loading**
```bash
# Check API endpoints
curl -H "Authorization: Bearer <token>" http://localhost:8001/api/applications

# Check CORS configuration
# Ensure frontend URL is in CORS origins
```

### Log Files

```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs  
tail -f /var/log/supervisor/frontend.*.log

# MongoDB logs (if local)
tail -f /var/log/mongodb/mongod.log
```

## 🔒 Security Considerations

### Production Deployment
- [ ] Change default JWT secret key
- [ ] Update default admin credentials
- [ ] Configure HTTPS/TLS
- [ ] Set proper CORS origins
- [ ] Enable rate limiting
- [ ] Set up monitoring alerts
- [ ] Regular security updates
- [ ] Backup database regularly

### Environment Security
```bash
# Secure file permissions
chmod 600 backend/.env frontend/.env

# Use environment variables in production
export JWT_SECRET="your-production-secret"
export MONGO_URL="your-production-mongodb-url"
```

## 🛣️ Roadmap

### Next Features
- **Keycloak Integration**: Complete SSO implementation
- **Additional Tool Integrations**: TheHive, OpenSearch, Wazuh
- **Advanced RBAC**: Fine-grained permission system
- **Audit Dashboard**: Complete user action tracking
- **API Rate Limiting**: Production-grade protection
- **Mobile App**: React Native interface

## 📞 Support

### Getting Help
1. **Documentation**: Check this README and `/ROADMAP.md`
2. **Logs**: Always check backend/frontend logs first
3. **Configuration**: Verify environment variables
4. **Database**: Ensure MongoDB is running and accessible

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## ⚡ Quick Reference

**Start Application:**
```bash
sudo supervisorctl start all
```

**Check Status:**
```bash
sudo supervisorctl status
```

**Default Login:**
- URL: http://localhost:3000
- Username: `admin`
- Password: `admin123`

**Key Endpoints:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/api
- Health Check: http://localhost:8001/api/health

**Configuration Files:**
- Backend: `backend/.env`
- Frontend: `frontend/.env`

---

🎉 **You're all set! The Unified Security Console v2.0 is ready for production use.**