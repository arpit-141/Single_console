#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class UnifiedSecurityConsoleAPITester:
    def __init__(self, base_url="https://940225cc-aa7b-4168-81a4-d021ca1c8bb0.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.auth_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details
        })

    def set_auth_token(self, token: str):
        """Set authentication token for subsequent requests"""
        self.auth_token = token
        self.headers['Authorization'] = f'Bearer {token}'

    def test_auth_config(self):
        """Test authentication configuration endpoint"""
        try:
            response = requests.get(f"{self.api_url}/auth/config", headers={'Content-Type': 'application/json'}, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                auth_type = data.get('auth_type')
                simple_enabled = data.get('simple_auth_enabled')
                details = f"Auth type: {auth_type}, Simple auth: {simple_enabled}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Auth Configuration", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Auth Configuration", False, str(e))
            return False, {}

    def test_login_authentication(self):
        """Test JWT authentication system with default admin credentials"""
        # Test login with correct credentials
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", 
                                   json=login_data, 
                                   headers={'Content-Type': 'application/json'}, 
                                   timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                token = data.get('access_token')
                user = data.get('user', {})
                
                if token and user.get('username') == 'admin':
                    self.set_auth_token(token)
                    details = f"Login successful, admin user authenticated, token received"
                else:
                    success = False
                    details = f"Login response missing token or user data"
            else:
                details = f"Status code: {response.status_code}, Response: {response.text}"
                
            self.log_test("JWT Login Authentication", success, details)
            
            # Test login with wrong credentials
            wrong_login = {
                "username": "admin",
                "password": "wrongpassword"
            }
            
            response = requests.post(f"{self.api_url}/auth/login", 
                                   json=wrong_login, 
                                   headers={'Content-Type': 'application/json'}, 
                                   timeout=10)
            wrong_success = response.status_code == 401
            self.log_test("JWT Login Wrong Password", wrong_success, 
                         "Correctly rejected wrong password" if wrong_success else f"Status: {response.status_code}")
            
            return success and wrong_success
            
        except Exception as e:
            self.log_test("JWT Login Authentication", False, str(e))
            return False

    def test_token_validation(self):
        """Test JWT token validation for protected endpoints"""
        if not self.auth_token:
            self.log_test("Token Validation", False, "No auth token available")
            return False
            
        try:
            # Test /auth/me endpoint with valid token
            response = requests.get(f"{self.api_url}/auth/me", headers=self.headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                user_data = response.json()
                if user_data.get('username') == 'admin':
                    details = f"Token validated, user: {user_data.get('username')}"
                else:
                    success = False
                    details = f"Token valid but wrong user: {user_data.get('username')}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("JWT Token Validation", success, details)
            
            # Test with invalid token
            invalid_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer invalid-token'}
            response = requests.get(f"{self.api_url}/auth/me", headers=invalid_headers, timeout=10)
            invalid_success = response.status_code == 401
            self.log_test("JWT Invalid Token Rejection", invalid_success, 
                         "Correctly rejected invalid token" if invalid_success else f"Status: {response.status_code}")
            
            return success and invalid_success
            
        except Exception as e:
            self.log_test("JWT Token Validation", False, str(e))
            return False

    def test_password_change(self):
        """Test password change functionality"""
        if not self.auth_token:
            self.log_test("Password Change", False, "No auth token available")
            return False
            
        try:
            # Test password change with correct current password
            change_data = {
                "current_password": "admin123",
                "new_password": "newadmin123"
            }
            
            response = requests.post(f"{self.api_url}/auth/change-password", 
                                   json=change_data, headers=self.headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                # Test login with new password
                login_data = {"username": "admin", "password": "newadmin123"}
                login_response = requests.post(f"{self.api_url}/auth/login", 
                                             json=login_data, 
                                             headers={'Content-Type': 'application/json'}, 
                                             timeout=10)
                new_login_success = login_response.status_code == 200
                
                if new_login_success:
                    # Update token
                    new_data = login_response.json()
                    self.set_auth_token(new_data.get('access_token'))
                    
                    # Change password back to original
                    revert_data = {
                        "current_password": "newadmin123",
                        "new_password": "admin123"
                    }
                    requests.post(f"{self.api_url}/auth/change-password", 
                                json=revert_data, headers=self.headers, timeout=10)
                    
                    # Update token again with original password
                    original_login = {"username": "admin", "password": "admin123"}
                    original_response = requests.post(f"{self.api_url}/auth/login", 
                                                    json=original_login, 
                                                    headers={'Content-Type': 'application/json'}, 
                                                    timeout=10)
                    if original_response.status_code == 200:
                        self.set_auth_token(original_response.json().get('access_token'))
                    
                    details = "Password change and revert successful"
                else:
                    success = False
                    details = "Password changed but new login failed"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Password Change Functionality", success, details)
            
            # Test password change with wrong current password
            wrong_change = {
                "current_password": "wrongpassword",
                "new_password": "newpassword"
            }
            
            response = requests.post(f"{self.api_url}/auth/change-password", 
                                   json=wrong_change, headers=self.headers, timeout=10)
            wrong_success = response.status_code == 400
            self.log_test("Password Change Wrong Current", wrong_success, 
                         "Correctly rejected wrong current password" if wrong_success else f"Status: {response.status_code}")
            
            return success and wrong_success
            
        except Exception as e:
            self.log_test("Password Change Functionality", False, str(e))
            return False

    def test_health_check(self):
        """Test basic health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health", headers=self.headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Status: {data.get('status')}, Version: {data.get('version')}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Health Check", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False, {}

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        try:
            response = requests.get(f"{self.api_url}/dashboard/stats", headers=self.headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                details = f"Apps: {data.get('total_applications')}, Users: {data.get('total_users')}, Roles: {data.get('total_roles')}"
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Dashboard Stats", success, details)
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Dashboard Stats", False, str(e))
            return False, {}

    def test_app_templates(self):
        """Test application templates system"""
        if not self.auth_token:
            self.log_test("App Templates", False, "No auth token available")
            return False
            
        # Test GET all app templates
        try:
            response = requests.get(f"{self.api_url}/app-templates", headers=self.headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                templates = response.json()
                expected_types = ["DefectDojo", "TheHive", "OpenSearch", "Wazuh", "Suricata", 
                                "Elastic", "Splunk", "MISP", "Cortex", "Custom"]
                
                found_types = [template_data.get('name') for template_data in templates.values()]
                missing_types = [t for t in expected_types if t not in found_types]
                
                if not missing_types:
                    details = f"All {len(expected_types)} app templates found"
                else:
                    details = f"Missing templates: {missing_types}"
                    success = False
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get App Templates", success, details)
        except Exception as e:
            self.log_test("Get App Templates", False, str(e))
            success = False

        # Test GET specific app template
        try:
            response = requests.get(f"{self.api_url}/app-templates/DefectDojo", headers=self.headers, timeout=10)
            specific_success = response.status_code == 200
            
            if specific_success:
                template = response.json()
                required_fields = ["name", "default_port", "description", "auth_type", "supports_role_sync"]
                missing_fields = [f for f in required_fields if f not in template]
                
                if not missing_fields:
                    details = f"DefectDojo template complete: {template.get('name')}, port {template.get('default_port')}, role sync: {template.get('supports_role_sync')}"
                else:
                    details = f"Missing fields: {missing_fields}"
                    specific_success = False
            else:
                details = f"Status code: {response.status_code}"
                
            self.log_test("Get Specific App Template", specific_success, details)
        except Exception as e:
            self.log_test("Get Specific App Template", False, str(e))
            specific_success = False

        return success and specific_success

    def test_applications_crud(self):
        """Test applications CRUD operations with different templates"""
        if not self.auth_token:
            self.log_test("Applications CRUD", False, "No auth token available")
            return False
            
        # Test GET applications
        try:
            response = requests.get(f"{self.api_url}/applications", headers=self.headers, timeout=10)
            get_success = response.status_code == 200
            apps_data = response.json() if get_success else []
            self.log_test("Get Applications", get_success, f"Found {len(apps_data)} applications")
        except Exception as e:
            self.log_test("Get Applications", False, str(e))
            get_success = False
            apps_data = []

        # Test POST application (create) with DefectDojo template
        test_app = {
            "app_name": "Test Security App",
            "app_type": "DefectDojo",
            "module": "XDR",
            "redirect_url": "https://example.com/test-app",
            "description": "Test DefectDojo application for API testing",
            "ip": "192.168.1.100",
            "username": "securityadmin",
            "password": "securepass123",
            "api_key": "test-api-key-defectdojo-123",
            "sync_roles": True
        }
        
        try:
            response = requests.post(f"{self.api_url}/applications", 
                                   json=test_app, headers=self.headers, timeout=10)
            post_success = response.status_code == 200
            created_app = response.json() if post_success else {}
            app_id = created_app.get('id') if post_success else None
            
            # Verify app_type and template defaults were applied
            if post_success:
                app_type = created_app.get('app_type')
                default_port = created_app.get('default_port')
                sync_roles = created_app.get('sync_roles')
                
                if app_type == 'DefectDojo' and default_port == 8080 and sync_roles:
                    details = f"Created DefectDojo app with ID: {app_id}, port: {default_port}, sync_roles: {sync_roles}"
                else:
                    details = f"App created but template defaults not applied correctly: type={app_type}, port={default_port}, sync={sync_roles}"
                    post_success = False
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Create Application with Template", post_success, details)
        except Exception as e:
            self.log_test("Create Application with Template", False, str(e))
            post_success = False
            app_id = None

        # Test PUT application (update) with different template
        if post_success and app_id:
            update_data = {
                "description": "Updated security application description",
                "app_type": "TheHive",
                "sync_roles": False
            }
            try:
                response = requests.put(f"{self.api_url}/applications/{app_id}", 
                                      json=update_data, headers=self.headers, timeout=10)
                put_success = response.status_code == 200
                
                if put_success:
                    updated_app = response.json()
                    app_type = updated_app.get('app_type')
                    sync_roles = updated_app.get('sync_roles')
                    
                    if app_type == 'TheHive' and not sync_roles:
                        details = f"Updated app {app_id} to TheHive type, sync_roles: {sync_roles}"
                    else:
                        details = f"App not updated correctly: type={app_type}, sync={sync_roles}"
                        put_success = False
                else:
                    details = f"Status: {response.status_code}"
                    
                self.log_test("Update Application Template", put_success, details)
            except Exception as e:
                self.log_test("Update Application Template", False, str(e))
                put_success = False
        else:
            self.log_test("Update Application Template", False, "No app ID to update")
            put_success = False

        # Test DELETE application if we created one
        if post_success and app_id:
            try:
                response = requests.delete(f"{self.api_url}/applications/{app_id}", 
                                         headers=self.headers, timeout=10)
                delete_success = response.status_code == 200
                self.log_test("Delete Application", delete_success, 
                             f"Deleted app {app_id}" if delete_success else f"Status: {response.status_code}")
            except Exception as e:
                self.log_test("Delete Application", False, str(e))
                delete_success = False
        else:
            self.log_test("Delete Application", False, "No app ID to delete")
            delete_success = False

        return get_success and post_success and put_success and delete_success

    def test_users_crud(self):
        """Test users CRUD operations with module access control"""
        if not self.auth_token:
            self.log_test("Users CRUD", False, "No auth token available")
            return False
            
        # Test GET users
        try:
            response = requests.get(f"{self.api_url}/users", headers=self.headers, timeout=10)
            get_success = response.status_code == 200
            users_data = response.json() if get_success else []
            
            # Check if default admin user exists
            admin_found = any(user.get('username') == 'admin' and user.get('is_admin') for user in users_data)
            if admin_found:
                details = f"Found {len(users_data)} users including default admin"
            else:
                details = f"Found {len(users_data)} users but no admin user"
                get_success = False
                
            self.log_test("Get Users with Admin Check", get_success, details)
        except Exception as e:
            self.log_test("Get Users with Admin Check", False, str(e))
            get_success = False

        # Test POST user (create) with module access
        test_user = {
            "username": f"securityanalyst_{datetime.now().strftime('%H%M%S')}",
            "email": f"analyst_{datetime.now().strftime('%H%M%S')}@securityconsole.com",
            "password": "SecurePass123!",
            "first_name": "Security",
            "last_name": "Analyst",
            "roles": ["Security Analyst"],
            "module_access": ["XDR", "XDR+"],
            "is_admin": False
        }
        
        try:
            response = requests.post(f"{self.api_url}/users", 
                                   json=test_user, headers=self.headers, timeout=10)
            post_success = response.status_code == 200
            created_user = response.json() if post_success else {}
            user_id = created_user.get('id') if post_success else None
            
            if post_success:
                module_access = created_user.get('module_access', [])
                roles = created_user.get('roles', [])
                if 'XDR' in module_access and 'Security Analyst' in roles:
                    details = f"Created user with ID: {user_id}, modules: {module_access}, roles: {roles}"
                else:
                    details = f"User created but module access or roles incorrect: modules={module_access}, roles={roles}"
                    post_success = False
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Create User with Module Access", post_success, details)
        except Exception as e:
            self.log_test("Create User with Module Access", False, str(e))
            post_success = False
            user_id = None

        # Test GET specific user if we created one
        if post_success and user_id:
            try:
                response = requests.get(f"{self.api_url}/users/{user_id}", 
                                      headers=self.headers, timeout=10)
                get_user_success = response.status_code == 200
                
                if get_user_success:
                    user_data = response.json()
                    username = user_data.get('username')
                    is_admin = user_data.get('is_admin')
                    details = f"Retrieved user {username}, admin: {is_admin}"
                else:
                    details = f"Status: {response.status_code}"
                    
                self.log_test("Get Specific User", get_user_success, details)
            except Exception as e:
                self.log_test("Get Specific User", False, str(e))
                get_user_success = False
        else:
            self.log_test("Get Specific User", False, "No user ID to retrieve")
            get_user_success = False

        return get_success and post_success and get_user_success

    def test_roles_crud(self):
        """Test roles CRUD operations"""
        # Test GET roles
        try:
            response = requests.get(f"{self.api_url}/roles", headers=self.headers, timeout=10)
            get_success = response.status_code == 200
            roles_data = response.json() if get_success else []
            self.log_test("Get Roles", get_success, f"Found {len(roles_data)} roles")
        except Exception as e:
            self.log_test("Get Roles", False, str(e))
            get_success = False

        # Test POST role (create)
        test_role = {
            "name": f"TestRole_{datetime.now().strftime('%H%M%S')}",
            "description": "Test role for API testing",
            "permissions": ["read", "write"]
        }
        
        try:
            response = requests.post(f"{self.api_url}/roles", 
                                   json=test_role, headers=self.headers, timeout=10)
            post_success = response.status_code == 200
            created_role = response.json() if post_success else {}
            role_id = created_role.get('id') if post_success else None
            self.log_test("Create Role", post_success, 
                         f"Created role with ID: {role_id}" if role_id else f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create Role", False, str(e))
            post_success = False

        return get_success and post_success

    def test_role_sync_framework(self):
        """Test generic role synchronization framework"""
        if not self.auth_token:
            self.log_test("Role Sync Framework", False, "No auth token available")
            return False
            
        # First, get applications to find one that supports role sync
        try:
            response = requests.get(f"{self.api_url}/applications", headers=self.headers, timeout=10)
            if response.status_code != 200:
                self.log_test("Role Sync Framework", False, "Could not get applications list")
                return False
                
            apps = response.json()
            defectdojo_app = None
            
            # Look for DefectDojo app or create one for testing
            for app in apps:
                if app.get('app_type') == 'DefectDojo':
                    defectdojo_app = app
                    break
            
            if not defectdojo_app:
                # Create a test DefectDojo app for role sync testing
                test_app = {
                    "app_name": "Test DefectDojo for Role Sync",
                    "app_type": "DefectDojo",
                    "module": "XDR",
                    "redirect_url": "https://demo.defectdojo.org",
                    "description": "Test DefectDojo for role synchronization",
                    "api_key": "test-api-key-for-sync",
                    "sync_roles": True
                }
                
                create_response = requests.post(f"{self.api_url}/applications", 
                                              json=test_app, headers=self.headers, timeout=10)
                if create_response.status_code == 200:
                    defectdojo_app = create_response.json()
                else:
                    self.log_test("Role Sync Framework", False, "Could not create test DefectDojo app")
                    return False
            
            app_id = defectdojo_app.get('id')
            
            # Test role synchronization
            sync_response = requests.post(f"{self.api_url}/applications/{app_id}/sync-roles", 
                                        headers=self.headers, timeout=15)
            sync_success = sync_response.status_code == 200
            
            if sync_success:
                sync_data = sync_response.json()
                synced_count = sync_data.get('synced_roles', 0)
                success_flag = sync_data.get('success', False)
                message = sync_data.get('message', '')
                
                if success_flag:
                    details = f"Role sync successful: {synced_count} roles synced, message: {message}"
                else:
                    details = f"Role sync completed but reported failure: {message}"
                    # This might be expected if external service is not available
            else:
                details = f"Status: {sync_response.status_code}, Response: {sync_response.text}"
                
            self.log_test("DefectDojo Role Synchronization", sync_success, details)
            
            # Test role sync for unsupported app type
            unsupported_app = {
                "app_name": "Test Suricata No Sync",
                "app_type": "Suricata",
                "module": "XDR",
                "redirect_url": "https://example.com/suricata",
                "description": "Test Suricata (no role sync support)",
                "sync_roles": False
            }
            
            create_response = requests.post(f"{self.api_url}/applications", 
                                          json=unsupported_app, headers=self.headers, timeout=10)
            if create_response.status_code == 200:
                unsupported_app_data = create_response.json()
                unsupported_id = unsupported_app_data.get('id')
                
                # Try to sync roles for unsupported app
                unsupported_sync = requests.post(f"{self.api_url}/applications/{unsupported_id}/sync-roles", 
                                               headers=self.headers, timeout=10)
                unsupported_success = unsupported_sync.status_code == 400  # Should fail
                
                # Clean up
                requests.delete(f"{self.api_url}/applications/{unsupported_id}", headers=self.headers)
                
                self.log_test("Unsupported App Role Sync Rejection", unsupported_success, 
                             "Correctly rejected role sync for unsupported app" if unsupported_success else f"Status: {unsupported_sync.status_code}")
            else:
                self.log_test("Unsupported App Role Sync Rejection", False, "Could not create test unsupported app")
                unsupported_success = False
            
            return sync_success and unsupported_success
            
        except Exception as e:
            self.log_test("Role Sync Framework", False, str(e))
            return False

    def test_applications_by_module(self):
        """Test getting applications by module with access control"""
        if not self.auth_token:
            self.log_test("Applications by Module", False, "No auth token available")
            return False
            
        modules = ["XDR", "XDR+", "OXDR", "GSOS"]
        all_success = True
        
        for module in modules:
            try:
                response = requests.get(f"{self.api_url}/applications/module/{module}", 
                                      headers=self.headers, timeout=10)
                success = response.status_code == 200
                if success:
                    apps = response.json()
                    # Verify all returned apps have the correct module
                    correct_module = all(app.get('module') == module for app in apps)
                    if correct_module:
                        details = f"Found {len(apps)} applications for {module}, all correctly filtered"
                    else:
                        details = f"Found {len(apps)} applications but some have wrong module"
                        success = False
                else:
                    details = f"Status code: {response.status_code}"
                self.log_test(f"Get {module} Applications", success, details)
                all_success = all_success and success
            except Exception as e:
                self.log_test(f"Get {module} Applications", False, str(e))
                all_success = False
        
        return all_success

    def test_production_features(self):
        """Test production-ready features like encryption and error handling"""
        if not self.auth_token:
            self.log_test("Production Features", False, "No auth token available")
            return False
            
        # Test encrypted credential storage by creating app with sensitive data
        test_app_with_creds = {
            "app_name": "Test Encrypted Credentials",
            "app_type": "DefectDojo",
            "module": "XDR",
            "redirect_url": "https://example.com/secure-app",
            "description": "Test app for credential encryption",
            "username": "secureuser",
            "password": "supersecretpassword123",
            "api_key": "very-secret-api-key-12345"
        }
        
        try:
            # Create app with credentials
            response = requests.post(f"{self.api_url}/applications", 
                                   json=test_app_with_creds, headers=self.headers, timeout=10)
            create_success = response.status_code == 200
            
            if create_success:
                created_app = response.json()
                app_id = created_app.get('id')
                
                # Verify credentials are not returned in plain text (should be encrypted or omitted)
                returned_password = created_app.get('password')
                returned_api_key = created_app.get('api_key')
                
                # In a secure system, these should either be omitted or encrypted
                if returned_password != "supersecretpassword123" and returned_api_key != "very-secret-api-key-12345":
                    details = f"Credentials properly secured (not returned in plain text)"
                    encryption_success = True
                else:
                    details = f"WARNING: Credentials returned in plain text"
                    encryption_success = False
                
                # Clean up
                requests.delete(f"{self.api_url}/applications/{app_id}", headers=self.headers)
            else:
                details = f"Could not create test app: {response.status_code}"
                encryption_success = False
                
            self.log_test("Encrypted Credential Storage", encryption_success, details)
            
        except Exception as e:
            self.log_test("Encrypted Credential Storage", False, str(e))
            encryption_success = False
        
        # Test error handling with invalid requests
        try:
            # Test invalid JSON
            invalid_response = requests.post(f"{self.api_url}/applications", 
                                           data="invalid json", 
                                           headers=self.headers, timeout=10)
            error_handling_success = invalid_response.status_code in [400, 422]  # Should return proper error
            
            self.log_test("Error Handling for Invalid Data", error_handling_success, 
                         f"Properly handled invalid data with status {invalid_response.status_code}" if error_handling_success else f"Status: {invalid_response.status_code}")
        except Exception as e:
            self.log_test("Error Handling for Invalid Data", False, str(e))
            error_handling_success = False
        
        return encryption_success and error_handling_success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Unified Security Console v2.0 API Tests")
        print("=" * 70)
        
        # Test authentication configuration first
        print("\n🔐 Authentication Configuration Tests:")
        self.test_auth_config()
        
        # Test JWT authentication system
        print("\n🔑 JWT Authentication System Tests:")
        auth_success = self.test_login_authentication()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with protected endpoint tests")
            print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
            return 1
        
        # Test token validation
        self.test_token_validation()
        self.test_password_change()
        
        # Test basic functionality
        print("\n📋 Basic API Tests:")
        self.test_health_check()
        self.test_dashboard_stats()
        
        # Test application templates system
        print("\n🎯 Application Templates System Tests:")
        self.test_app_templates()
        
        # Test CRUD operations
        print("\n📝 Application Management Tests:")
        self.test_applications_crud()
        
        # Test user management
        print("\n👥 User & Role Management Tests:")
        self.test_users_crud()
        self.test_roles_crud()
        
        # Test role synchronization framework
        print("\n🔄 Role Synchronization Framework Tests:")
        self.test_role_sync_framework()
        
        # Test module-specific endpoints
        print("\n🔧 Module-Based Access Control Tests:")
        self.test_applications_by_module()
        
        # Test production features
        print("\n🛡️ Production-Ready Features Tests:")
        self.test_production_features()
        
        # Print summary
        print("\n" + "=" * 70)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Unified Security Console v2.0 is working correctly.")
            return 0
        else:
            print("⚠️  Some tests failed. Check the details above.")
            
            # Print failed tests
            failed_tests = [test for test in self.test_results if not test['success']]
            if failed_tests:
                print("\n❌ Failed Tests:")
                for test in failed_tests:
                    print(f"  - {test['name']}: {test['details']}")
            
            return 1

def main():
    """Main function to run the tests"""
    tester = UnifiedSecurityConsoleAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())