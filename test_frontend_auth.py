"""
Test frontend authentication flow
"""

import requests
import json

def test_login_flow():
    """Test the complete login flow"""
    print("🔐 Testing Frontend Authentication Flow")
    print("=" * 50)
    
    try:
        # Step 1: Test login endpoint
        print("1. Testing login endpoint...")
        login_response = requests.post(
            "http://127.0.0.1:8000/api/auth/token/",
            json={
                "username": "test@example.com",
                "password": "test123"
            }
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data['access']
            refresh_token = token_data['refresh']
            
            print(f"✅ Login successful!")
            print(f"   Access token: {access_token[:50]}...")
            print(f"   Refresh token: {refresh_token[:50]}...")
            
            # Step 2: Test API with token
            print("\n2. Testing API with JWT token...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Test dashboard endpoint
            dashboard_response = requests.get(
                "http://127.0.0.1:8000/api/dashboard/summary/",
                headers=headers
            )
            
            if dashboard_response.status_code == 200:
                dashboard_data = dashboard_response.json()
                print(f"✅ Dashboard API successful!")
                print(f"   Total leads: {dashboard_data.get('total_leads', 0)}")
                print(f"   New leads: {dashboard_data.get('new_leads', 0)}")
                print(f"   Won leads: {dashboard_data.get('won_leads', 0)}")
            else:
                print(f"❌ Dashboard API failed: {dashboard_response.status_code}")
                print(f"   Response: {dashboard_response.text}")
                return False
            
            # Test leads endpoint
            leads_response = requests.get(
                "http://127.0.0.1:8000/api/leads/",
                headers=headers
            )
            
            if leads_response.status_code == 200:
                leads_data = leads_response.json()
                print(f"✅ Leads API successful!")
                print(f"   Found {len(leads_data.get('results', []))} leads")
            else:
                print(f"❌ Leads API failed: {leads_response.status_code}")
                print(f"   Response: {leads_response.text}")
                return False
            
            return True
            
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🎯 Frontend Authentication Test")
    print("=" * 60)
    
    success = test_login_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 AUTHENTICATION WORKING!")
        print("\n📋 Next Steps:")
        print("1. Open http://localhost:3002/ in browser")
        print("2. Login with: test@example.com / test123")
        print("3. Dashboard should load successfully")
        print("\n🔧 If still failing:")
        print("- Check browser console for JavaScript errors")
        print("- Check network tab for failed requests")
        print("- Clear browser localStorage")
    else:
        print("❌ AUTHENTICATION FAILED")
        print("Check the errors above and fix Django API issues")
    
    return success

if __name__ == "__main__":
    main()
