#!/usr/bin/env python3
"""
Backend API Testing for Social Media Automation Platform
Tests all API endpoints with proper authentication flow.
"""

import requests
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any

class SocialMediaAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        
        result = f"{status} - {name}"
        if details:
            result += f" | {details}"
        
        print(result)
        self.test_results.append({
            "name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        return success

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    expected_status: int = 200, use_auth: bool = False) -> tuple[bool, Dict]:
        """Make HTTP request and validate response"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        if use_auth and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                return False, {"error": f"Unsupported method: {method}"}

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if not success:
                response_data["status_code"] = response.status_code
                response_data["expected_status"] = expected_status

            return success, response_data

        except requests.exceptions.RequestException as e:
            return False, {"error": f"Request failed: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}

    def test_health_check(self) -> bool:
        """Test health check endpoint"""
        print("\n🔍 Testing Health Check...")
        success, response = self.make_request('GET', '/api/health', expected_status=200)
        
        if success:
            details = f"Status: {response.get('status', 'unknown')}"
            if 'services' in response:
                services = response['services']
                details += f" | DB: {services.get('database', 'unknown')} | API: {services.get('api', 'unknown')}"
        else:
            details = f"Error: {response.get('error', 'Unknown error')}"
            if 'status_code' in response:
                details += f" | Status: {response['status_code']}"

        return self.log_test("Health Check", success, details)

    def test_user_registration(self) -> bool:
        """Test user registration"""
        print("\n🔍 Testing User Registration...")
        
        # Generate unique test user
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_user = {
            "email": f"test_user_{timestamp}@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        success, response = self.make_request(
            'POST', 
            '/api/v1/auth/register', 
            data=test_user,
            expected_status=200
        )
        
        if success:
            self.token = response.get('access_token')
            self.user_data = response.get('user', {})
            details = f"User ID: {self.user_data.get('id', 'unknown')} | Email: {self.user_data.get('email', 'unknown')}"
        else:
            details = f"Error: {response.get('error', response.get('detail', 'Unknown error'))}"
            if 'status_code' in response:
                details += f" | Status: {response['status_code']}"

        return self.log_test("User Registration", success, details)

    def test_user_login(self) -> bool:
        """Test user login with registered user"""
        print("\n🔍 Testing User Login...")
        
        if not self.user_data:
            return self.log_test("User Login", False, "No user data available from registration")
        
        login_data = {
            "email": self.user_data.get('email'),
            "password": "TestPassword123!"
        }
        
        success, response = self.make_request(
            'POST',
            '/api/v1/auth/login',
            data=login_data,
            expected_status=200
        )
        
        if success:
            # Update token from login response
            self.token = response.get('access_token')
            user = response.get('user', {})
            details = f"Token received | User: {user.get('email', 'unknown')}"
        else:
            details = f"Error: {response.get('error', response.get('detail', 'Unknown error'))}"
            if 'status_code' in response:
                details += f" | Status: {response['status_code']}"

        return self.log_test("User Login", success, details)

    def test_get_user_profile(self) -> bool:
        """Test getting user profile"""
        print("\n🔍 Testing Get User Profile...")
        
        if not self.token:
            return self.log_test("Get User Profile", False, "No authentication token available")
        
        success, response = self.make_request(
            'GET',
            '/api/v1/users/profile',
            use_auth=True,
            expected_status=200
        )
        
        if success:
            details = f"Name: {response.get('first_name', '')} {response.get('last_name', '')} | Tier: {response.get('subscription_tier', 'unknown')}"
        else:
            details = f"Error: {response.get('error', response.get('detail', 'Unknown error'))}"
            if 'status_code' in response:
                details += f" | Status: {response['status_code']}"

        return self.log_test("Get User Profile", success, details)

    def test_set_success_goals(self) -> bool:
        """Test setting success goals"""
        print("\n🔍 Testing Set Success Goals...")
        
        if not self.token:
            return self.log_test("Set Success Goals", False, "No authentication token available")
        
        goals_data = {
            "followers_target": 5000,
            "engagement_rate_target": 0.05,
            "revenue_target": 500.0,
            "timeframe_days": 90
        }
        
        success, response = self.make_request(
            'POST',
            '/api/v1/users/success-goals',
            data=goals_data,
            use_auth=True,
            expected_status=200
        )
        
        if success:
            goals = response.get('goals', {})
            details = f"Followers: {goals.get('followers_target', 0)} | Revenue: ${goals.get('revenue_target', 0)} | Days: {goals.get('timeframe_days', 0)}"
        else:
            details = f"Error: {response.get('error', response.get('detail', 'Unknown error'))}"
            if 'status_code' in response:
                details += f" | Status: {response['status_code']}"

        return self.log_test("Set Success Goals", success, details)

    def test_create_content(self) -> bool:
        """Test creating content"""
        print("\n🔍 Testing Create Content...")
        
        if not self.token:
            return self.log_test("Create Content", False, "No authentication token available")
        
        content_data = {
            "title": "Test Instagram Post",
            "content_type": "text",
            "platform": "instagram",
            "text_content": "This is a test post for our social media automation platform! 🚀 #testing #automation #socialmedia",
            "hashtags": ["testing", "automation", "socialmedia"]
        }
        
        success, response = self.make_request(
            'POST',
            '/api/v1/content/create',
            data=content_data,
            use_auth=True,
            expected_status=200
        )
        
        if success:
            details = f"Content ID: {response.get('id', 'unknown')} | Platform: {response.get('platform', 'unknown')} | Status: {response.get('status', 'unknown')}"
        else:
            details = f"Error: {response.get('error', response.get('detail', 'Unknown error'))}"
            if 'status_code' in response:
                details += f" | Status: {response['status_code']}"

        return self.log_test("Create Content", success, details)

    def test_list_content(self) -> bool:
        """Test listing user content"""
        print("\n🔍 Testing List Content...")
        
        if not self.token:
            return self.log_test("List Content", False, "No authentication token available")
        
        success, response = self.make_request(
            'GET',
            '/api/v1/content/list',
            use_auth=True,
            expected_status=200
        )
        
        if success:
            if isinstance(response, list):
                content_count = len(response)
                details = f"Found {content_count} content items"
                if content_count > 0:
                    first_item = response[0]
                    details += f" | First item: {first_item.get('title', 'No title')} ({first_item.get('platform', 'unknown')})"
            else:
                details = "Response is not a list"
        else:
            details = f"Error: {response.get('error', response.get('detail', 'Unknown error'))}"
            if 'status_code' in response:
                details += f" | Status: {response['status_code']}"

        return self.log_test("List Content", success, details)

    def run_all_tests(self) -> bool:
        """Run all API tests in sequence"""
        print("🚀 Starting Social Media Automation Platform API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 60)
        
        # Test sequence - order matters for authentication flow
        test_methods = [
            self.test_health_check,
            self.test_user_registration,
            self.test_user_login,
            self.test_get_user_profile,
            self.test_set_success_goals,
            self.test_create_content,
            self.test_list_content
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(test_method.__name__, False, f"Exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return False

def main():
    """Main test execution"""
    # Use the frontend's configured backend URL
    backend_url = "http://localhost:8001"
    
    print("🧪 Social Media Automation Platform - Backend API Testing")
    print(f"🌐 Testing against: {backend_url}")
    
    tester = SocialMediaAPITester(backend_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())