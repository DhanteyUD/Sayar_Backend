import requests
import json

BASE_URL = "http://127.0.0.1:8000"
SIGNUP_URL = f"{BASE_URL}/api/v1/auth/signup/merchant"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"


def test_merchant_signup():
    print("=" * 60)
    print("Testing Merchant Signup")
    print("=" * 60)

    # Signup data
    signup_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+2348012345678",
        "business_name": "Test Business Ltd",
        "password": "SecurePass123",
        "confirm_password": "SecurePass123"
    }

    print("\nSending signup request...")
    print(f"URL: {SIGNUP_URL}")
    print(f"Data: {json.dumps(signup_data, indent=2)}")

    try:
        response = requests.post(SIGNUP_URL, json=signup_data)

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 201:
            print("\n✅ SUCCESS! Merchant account created successfully!")
            result = response.json()
            print(f"\nResponse Data:")
            print(json.dumps(result, indent=2))

            if "tokens" in result:
                token = result["tokens"]["access_token"]
                print(f"\n🔑 Access Token: {token[:50]}...")
                return token
        else:
            print("\n❌ FAILED! Error creating merchant account")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

    return None


def test_merchant_login(email="john.doe@example.com", password="SecurePass123"):
    print("\n" + "=" * 60)
    print("Testing Merchant Login")
    print("=" * 60)

    login_data = {
        "email": email,
        "password": password
    }

    print("\nSending login request...")
    print(f"URL: {LOGIN_URL}")
    print(f"Data: {json.dumps(login_data, indent=2)}")

    try:
        response = requests.post(LOGIN_URL, json=login_data)

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            print("\n✅ SUCCESS! Login successful!")
            result = response.json()
            print(f"\nResponse Data:")
            print(json.dumps(result, indent=2))

            token = result.get("access_token")
            print(f"\n🔑 Access Token: {token[:50]}...")
            return token
        else:
            print("\n❌ FAILED! Login failed")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

    return None


def test_get_current_user(token):
    print("\n" + "=" * 60)
    print("Testing Get Current User")
    print("=" * 60)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    me_url = f"{BASE_URL}/api/v1/auth/me"

    print(f"\nSending request to: {me_url}")

    try:
        response = requests.get(me_url, headers=headers)

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            print("\n✅ SUCCESS! User info retrieved!")
            result = response.json()
            print(f"\nUser Data:")
            print(json.dumps(result, indent=2))
        else:
            print("\n❌ FAILED!")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


def test_health_check():
    print("\n" + "=" * 60)
    print("Testing Health Check")
    print("=" * 60)

    health_url = f"{BASE_URL}/health"

    try:
        response = requests.get(health_url)
        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ API is healthy!")
            print(f"Response: {response.json()}")
        else:
            print("❌ Health check failed")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    print("\n🚀 Starting Sayar API Tests...\n")

    test_health_check()

    access_token = test_merchant_signup()

    if access_token:
        test_get_current_user(access_token)
    else:
        print("\n💡 Trying login instead (user might already exist)...")
        access_token = test_merchant_login()

        if access_token:
            test_get_current_user(access_token)

    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)
    print("\n📚 Visit http://127.0.0.1:8000/api/v1/docs for interactive API documentation")
