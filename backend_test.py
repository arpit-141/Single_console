#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any

class UnifiedSecurityConsoleAPITester:
    def __init__(self, base_url="https://7bb2adb0-31af-4083-9206-07fbebae4a3f.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer admin-token'
        }
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
        """Test new app templates endpoints"""
        # Test GET all app templates
        try:
            response = requests.get(f"{self.api_url}/app-templates", headers=self.headers, timeout=10)
            success = response.status_code == 200
            
            if success:
                templates = response.json()
                expected_types = ["DefectDojo", "TheHive", "OpenSearch", "Wazuh", "Suricata", 
                                "Elastic", "Splunk", "MISP", "Cortex", "Custom"]
                
                found_types = list(templates.keys())
                missing_types = [t for t in expected_types if t not in found_types]
                
                if not missing_types:
                    details = f"All {len(expected_types)} app types found"
                else:
                    details = f"Missing types: {missing_types}"
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
                required_fields = ["name", "default_port", "description", "auth_type"]
                missing_fields = [f for f in required_fields if f not in template]
                
                if not missing_fields:
                    details = f"DefectDojo template complete: {template.get('name')}, port {template.get('default_port')}"
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
        """Test applications CRUD operations with app_type field"""
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

        # Test POST application (create) with app_type
        test_app = {
            "app_name": "Test DefectDojo App",
            "app_type": "DefectDojo",
            "module": "XDR",
            "redirect_url": "https://example.com/test-app",
            "description": "Test DefectDojo application for API testing",
            "ip": "192.168.1.100",
            "default_port": 8080,
            "username": "testuser",
            "password": "testpass123",
            "api_key": "test-api-key-123"
        }
        
        try:
            response = requests.post(f"{self.api_url}/applications", 
                                   json=test_app, headers=self.headers, timeout=10)
            post_success = response.status_code == 200
            created_app = response.json() if post_success else {}
            app_id = created_app.get('id') if post_success else None
            
            # Verify app_type was saved correctly
            if post_success and created_app.get('app_type') == 'DefectDojo':
                details = f"Created DefectDojo app with ID: {app_id}"
            elif post_success:
                details = f"Created app but app_type incorrect: {created_app.get('app_type')}"
                post_success = False
            else:
                details = f"Status: {response.status_code}"
                
            self.log_test("Create Application with App Type", post_success, details)
        except Exception as e:
            self.log_test("Create Application with App Type", False, str(e))
            post_success = False
            app_id = None

        # Test PUT application (update) with app_type change
        if post_success and app_id:
            update_data = {
                "description": "Updated test application description",
                "app_type": "TheHive"
            }
            try:
                response = requests.put(f"{self.api_url}/applications/{app_id}", 
                                      json=update_data, headers=self.headers, timeout=10)
                put_success = response.status_code == 200
                
                if put_success:
                    updated_app = response.json()
                    if updated_app.get('app_type') == 'TheHive':
                        details = f"Updated app {app_id} to TheHive type"
                    else:
                        details = f"App type not updated correctly: {updated_app.get('app_type')}"
                        put_success = False
                else:
                    details = f"Status: {response.status_code}"
                    
                self.log_test("Update Application App Type", put_success, details)
            except Exception as e:
                self.log_test("Update Application App Type", False, str(e))
                put_success = False
        else:
            self.log_test("Update Application App Type", False, "No app ID to update")
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
        """Test users CRUD operations"""
        # Test GET users
        try:
            response = requests.get(f"{self.api_url}/users", headers=self.headers, timeout=10)
            get_success = response.status_code == 200
            users_data = response.json() if get_success else []
            self.log_test("Get Users", get_success, f"Found {len(users_data)} users")
        except Exception as e:
            self.log_test("Get Users", False, str(e))
            get_success = False

        # Test POST user (create)
        test_user = {
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "roles": ["User"],
            "module_access": ["XDR"],
            "is_admin": False
        }
        
        try:
            response = requests.post(f"{self.api_url}/users", 
                                   json=test_user, headers=self.headers, timeout=10)
            post_success = response.status_code == 200
            created_user = response.json() if post_success else {}
            user_id = created_user.get('id') if post_success else None
            self.log_test("Create User", post_success, 
                         f"Created user with ID: {user_id}" if user_id else f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Create User", False, str(e))
            post_success = False
            user_id = None

        # Test GET specific user if we created one
        if post_success and user_id:
            try:
                response = requests.get(f"{self.api_url}/users/{user_id}", 
                                      headers=self.headers, timeout=10)
                get_user_success = response.status_code == 200
                self.log_test("Get Specific User", get_user_success, 
                             f"Retrieved user {user_id}" if get_user_success else f"Status: {response.status_code}")
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

    def test_defectdojo_integration(self):
        """Test DefectDojo API integration"""
        # Test GET DefectDojo users
        try:
            response = requests.get(f"{self.api_url}/defectdojo/users", headers=self.headers, timeout=15)
            users_success = response.status_code == 200
            if users_success:
                data = response.json()
                user_count = len(data.get('results', []))
                details = f"Found {user_count} DefectDojo users"
            else:
                details = f"Status code: {response.status_code}"
            self.log_test("DefectDojo Users", users_success, details)
        except Exception as e:
            self.log_test("DefectDojo Users", False, str(e))
            users_success = False

        # Test GET DefectDojo roles
        try:
            response = requests.get(f"{self.api_url}/defectdojo/roles", headers=self.headers, timeout=15)
            roles_success = response.status_code == 200
            if roles_success:
                data = response.json()
                role_count = len(data.get('results', []))
                details = f"Found {role_count} DefectDojo roles"
            else:
                details = f"Status code: {response.status_code}"
            self.log_test("DefectDojo Roles", roles_success, details)
        except Exception as e:
            self.log_test("DefectDojo Roles", False, str(e))
            roles_success = False

        # Test DefectDojo roles sync
        try:
            response = requests.post(f"{self.api_url}/defectdojo/sync-roles", 
                                   headers=self.headers, timeout=15)
            sync_success = response.status_code == 200
            if sync_success:
                data = response.json()
                details = data.get('message', 'Sync completed')
            else:
                details = f"Status code: {response.status_code}"
            self.log_test("DefectDojo Sync Roles", sync_success, details)
        except Exception as e:
            self.log_test("DefectDojo Sync Roles", False, str(e))
            sync_success = False

        return users_success and roles_success and sync_success

    def test_applications_by_module(self):
        """Test getting applications by module"""
        modules = ["XDR", "XDR+", "OXDR", "GSOS"]
        all_success = True
        
        for module in modules:
            try:
                response = requests.get(f"{self.api_url}/applications/module/{module}", 
                                      headers=self.headers, timeout=10)
                success = response.status_code == 200
                if success:
                    apps = response.json()
                    details = f"Found {len(apps)} applications for {module}"
                else:
                    details = f"Status code: {response.status_code}"
                self.log_test(f"Get {module} Applications", success, details)
                all_success = all_success and success
            except Exception as e:
                self.log_test(f"Get {module} Applications", False, str(e))
                all_success = False
        
        return all_success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Unified Security Console API Tests")
        print("=" * 60)
        
        # Test basic functionality
        print("\n📋 Basic API Tests:")
        self.test_health_check()
        self.test_dashboard_stats()
        
        # Test new app templates feature
        print("\n🎯 New App Templates Feature Tests:")
        self.test_app_templates()
        
        # Test CRUD operations
        print("\n📝 CRUD Operations Tests:")
        self.test_applications_crud()
        self.test_users_crud()
        self.test_roles_crud()
        
        # Test module-specific endpoints
        print("\n🔧 Module-Specific Tests:")
        self.test_applications_by_module()
        
        # Test DefectDojo integration
        print("\n🔗 DefectDojo Integration Tests:")
        self.test_defectdojo_integration()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
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