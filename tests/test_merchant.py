import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def test_login():
    """Login and get access token"""
    print_header("LOGIN")

    login_data = {
        "email": "sarah@bookio.com",
        "password": "BookioPass123"
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    if response.status_code == 200:
        result = response.json()
        print("✅ Login successful!")
        return result["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None


def test_get_current_user(token):
    """Test /auth/me endpoint"""
    print_header("GET CURRENT USER WITH MERCHANTS")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

    if response.status_code == 200:
        user = response.json()
        print("✅ User information retrieved!")
        print(f"\n📧 Email: {user['email']}")
        print(f"👤 Name: {user['first_name']} {user['last_name']}")
        print(f"🔑 Role: {user['role']}")
        print(f"\n🏢 Merchants ({len(user['merchants'])}):")

        for merchant in user['merchants']:
            print(f"\n   • {merchant['business_name']}")
            print(f"     ID: {merchant['merchant_id']}")
            print(f"     Role: {merchant['role']}")
            print(f"     Status: {merchant['status']}")

        return user['merchants'][0]['merchant_id'] if user['merchants'] else None
    else:
        print(f"❌ Failed: {response.text}")
        return None


def test_list_user_merchants(token):
    """Test /merchants/list endpoint"""
    print_header("LIST USER'S MERCHANTS")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/merchants/list", headers=headers)

    if response.status_code == 200:
        merchants = response.json()
        print(f"✅ Found {len(merchants)} merchant(s)")

        for i, merchant in enumerate(merchants, 1):
            print(f"\n{i}. {merchant['business_name']}")
            print(f"   ID: {merchant['merchant_id']}")
            print(f"   Category: {merchant.get('category', 'N/A')}")
            print(f"   Your Role: {merchant['user_role']}")
            print(f"   Status: {'✓ Active' if merchant['is_active'] else '✗ Inactive'}")
            print(f"   Verified: {'✓ Yes' if merchant['is_verified'] else '✗ No'}")

        return merchants
    else:
        print(f"❌ Failed: {response.text}")
        return []


def test_get_merchant_details(token, merchant_id):
    """Test /merchants/{merchant_id} endpoint"""
    print_header("GET MERCHANT DETAILS")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/merchants/{merchant_id}",
        headers=headers
    )

    if response.status_code == 200:
        merchant = response.json()
        print("✅ Merchant details retrieved!")
        print(f"\n🏢 Business Name: {merchant['business_name']}")
        print(f"📧 Email: {merchant.get('business_email', 'N/A')}")
        print(f"📞 Phone: {merchant.get('business_phone', 'N/A')}")
        print(f"🏷️  Category: {merchant.get('category', 'N/A')}")
        print(f"💰 Currency: {merchant.get('currency', 'N/A')}")
        print(f"📍 Location: {merchant.get('city', 'N/A')}, {merchant.get('state', 'N/A')}")
        print(f"✅ Active: {merchant['is_active']}")
        print(f"✓ Verified: {merchant['is_verified']}")
    else:
        print(f"❌ Failed: {response.text}")


def test_list_merchant_users(token, merchant_id):
    """Test /merchants/merchant-users endpoint"""
    print_header("LIST MERCHANT USERS")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/merchants/merchant-users",
        params={"merchant_id": merchant_id},
        headers=headers
    )

    if response.status_code == 200:
        users = response.json()
        print(f"✅ Found {len(users)} user(s)")

        for i, user in enumerate(users, 1):
            print(f"\n{i}. {user['first_name']} {user['last_name']}")
            print(f"   Email: {user['email']}")
            print(f"   Phone: {user['phone']}")
            print(f"   Role: {user['role']}")
            print(f"   Status: {user['status']}")
            if user.get('joined_at'):
                print(f"   Joined: {user['joined_at']}")
    else:
        print(f"❌ Failed: {response.text}")


def test_get_merchant_stats(token, merchant_id):
    """Test /merchants/stats endpoint"""
    print_header("GET MERCHANT STATISTICS")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/merchants/stats",
        params={"merchant_id": merchant_id},
        headers=headers
    )

    if response.status_code == 200:
        stats = response.json()
        print("✅ Statistics retrieved!")
        print(f"\n👥 Total Users: {stats['total_users']}")
        print(f"✓ Active Users: {stats['active_users']}")
        print(f"\n📊 Roles Distribution:")
        print(f"   Owners: {stats['roles']['owner']}")
        print(f"   Admins: {stats['roles']['admin']}")
        print(f"   Staff: {stats['roles']['staff']}")
    else:
        print(f"❌ Failed: {response.text}")


def test_list_all_users_admin(token):
    """Test /merchants/all/users endpoint (Admin only)"""
    print_header("LIST ALL USERS (ADMIN ONLY)")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/merchants/all/users",
        params={"limit": 10},
        headers=headers
    )

    if response.status_code == 200:
        users = response.json()
        print(f"✅ Found {len(users)} user(s)")

        for i, user in enumerate(users, 1):
            print(f"\n{i}. {user['first_name']} {user['last_name']}")
            print(f"   Email: {user['email']}")
            print(f"   Role: {user['role']}")
    elif response.status_code == 403:
        print("ℹ️  This endpoint requires admin access")
    else:
        print(f"❌ Failed: {response.text}")


def test_list_all_merchants_admin(token):
    """Test /merchants/all/merchants endpoint (Admin only)"""
    print_header("LIST ALL MERCHANTS (ADMIN ONLY)")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/merchants/all/merchants",
        params={"limit": 10},
        headers=headers
    )

    if response.status_code == 200:
        merchants = response.json()
        print(f"✅ Found {len(merchants)} merchant(s)")

        for i, merchant in enumerate(merchants, 1):
            print(f"\n{i}. {merchant['business_name']}")
            print(f"   ID: {merchant['id']}")
            print(f"   Active: {merchant['is_active']}")
    elif response.status_code == 403:
        print("ℹ️  This endpoint requires admin access")
    else:
        print(f"❌ Failed: {response.text}")


def main():
    """Main test flow"""
    print("\n🚀 TESTING MERCHANT & USER ENDPOINTS")

    # Step 1: Login
    token = test_login()
    if not token:
        return

    input("\nPress Enter to continue...")

    # Step 2: Get current user with merchants
    merchant_id = test_get_current_user(token)

    input("\nPress Enter to continue...")

    # Step 3: List user's merchants
    merchants = test_list_user_merchants(token)

    print(f"Listing {len(merchants)} user(s)")

    if merchant_id:
        input("\nPress Enter to continue...")

        # Step 4: Get merchant details
        test_get_merchant_details(token, merchant_id)

        input("\nPress Enter to continue...")

        # Step 5: List merchant users
        test_list_merchant_users(token, merchant_id)

        input("\nPress Enter to continue...")

        # Step 6: Get merchant stats
        test_get_merchant_stats(token, merchant_id)

    input("\nPress Enter to test admin endpoints...")

    # Step 7: Test admin endpoints (will fail if not admin)
    test_list_all_users_admin(token)

    input("\nPress Enter to continue...")

    test_list_all_merchants_admin(token)

    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETE!")
    print("=" * 70)
    print("\n📚 API Documentation: http://127.0.0.1:8000/api/v1/docs")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
