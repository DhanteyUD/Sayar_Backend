"""
Test script for Sayar merchant onboarding flow
"""
import requests

# API endpoint
BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api/v1"


def test_complete_onboarding_flow():
    """Test the complete onboarding flow"""
    print("\n" + "=" * 70)
    print("SAYAR MERCHANT ONBOARDING TEST")
    print("=" * 70)

    # Step 0: Login to get token
    print("\n📝 Step 0: Login")
    print("-" * 70)

    login_data = {
        "email": "john@example.com",
        "password": "SecurePass123"
    }

    response = requests.post(f"{API_BASE}/auth/login", json=login_data)

    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return

    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"✅ Login successful!")
    print(f"🔑 Token: {access_token[:50]}...")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Check initial onboarding status
    print("\n📊 Checking Initial Onboarding Status")
    print("-" * 70)

    response = requests.get(f"{API_BASE}/onboarding/status", headers=headers)

    if response.status_code == 200:
        status = response.json()
        print(f"✅ Onboarding Status Retrieved")
        print(f"   Progress: {status['steps_completed']}/{status['total_steps']} ({status['completion_percentage']}%)")
        print(f"   Current Step: {status['current_step']}")
    else:
        print(f"❌ Failed: {response.text}")

    # Step 1: Business Details
    print("\n📝 Step 1: Business Details")
    print("-" * 70)

    business_details = {
        "business_name": "Sayar Retail Solutions",
        "business_email": "info@sayarretail.com",
        "business_logo_url": "https://cloudinary.com/logo.png",
        "business_category": "retail",
        "operating_currency": "NGN",
        "business_description": "We provide innovative retail solutions for modern businesses",
        "business_phone": "+2348012345678",
        "address_line1": "123 Commerce Street",
        "address_line2": "Floor 5, Suite 501",
        "country": "Nigeria",
        "state": "Lagos",
        "city": "Ikeja",
        "postal_code": "100001",
        "website": "https://sayarretail.com"
    }

    response = requests.post(
        f"{API_BASE}/onboarding/business-details",
        json=business_details,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   Next Step: {result['next_step']}")
        print(
            f"   Progress: {result['onboarding_progress']['steps_completed']}/{result['onboarding_progress']['total_steps']}")
    else:
        print(f"❌ Failed: {response.text}")
        return

    # # Step 2: WhatsApp Connection
    # print("\n📱 Step 2: WhatsApp Connection")
    # print("-" * 70)
    #
    # whatsapp_data = {
    #     "whatsapp_number": "+2348012345678",
    #     "whatsapp_business_id": "1234567890",
    #     "verification_code": "123456"
    # }
    #
    # response = requests.post(
    #     f"{API_BASE}/onboarding/whatsapp-connection",
    #     json=whatsapp_data,
    #     headers=headers
    # )
    #
    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"✅ {result['message']}")
    #     print(f"   Next Step: {result['next_step']}")
    #     print(
    #         f"   Progress: {result['onboarding_progress']['steps_completed']}/{result['onboarding_progress']['total_steps']}")
    # else:
    #     print(f"❌ Failed: {response.text}")

    # # Step 3: Catalog ID
    # print("\n📦 Step 3: Catalog ID")
    # print("-" * 70)
    #
    # catalog_data = {
    #     "catalog_id": "CAT-2024-001",
    #     "catalog_name": "Main Product Catalog"
    # }
    #
    # response = requests.post(
    #     f"{API_BASE}/onboarding/catalog-id",
    #     json=catalog_data,
    #     headers=headers
    # )
    #
    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"✅ {result['message']}")
    #     print(f"   Next Step: {result['next_step']}")
    #     print(
    #         f"   Progress: {result['onboarding_progress']['steps_completed']}/{result['onboarding_progress']['total_steps']}")
    # else:
    #     print(f"❌ Failed: {response.text}")

    # # Step 4: Payment Details
    # print("\n💳 Step 4: Payment Details")
    # print("-" * 70)
    #
    # payment_data = {
    #     "bank_name": "First Bank of Nigeria",
    #     "account_number": "1234567890",
    #     "account_name": "Sayar Retail Solutions",
    #     "bank_code": "011",
    #     "tax_id": "12345678-0001"
    # }
    #
    # response = requests.post(
    #     f"{API_BASE}/onboarding/payment-details",
    #     json=payment_data,
    #     headers=headers
    # )
    #
    # if response.status_code == 200:
    #     result = response.json()
    #     print(f"✅ {result['message']}")
    #     print(f"   Onboarding Completed: {result['onboarding_progress']['is_completed']}")
    #     print(
    #         f"   Progress: {result['onboarding_progress']['steps_completed']}/{result['onboarding_progress']['total_steps']}")
    # else:
    #     print(f"❌ Failed: {response.text}")
    #
    # # Final Status Check
    # print("\n📊 Final Onboarding Status")
    # print("-" * 70)
    #
    # response = requests.get(f"{API_BASE}/onboarding/status", headers=headers)
    #
    # if response.status_code == 200:
    #     status = response.json()
    #     print(f"✅ Onboarding Complete!")
    #     print(f"   Progress: {status['completion_percentage']}%")
    #     print(f"   All Steps:")
    #     print(f"      1. Business Details: {status['business_details_status']}")
    #     print(f"      2. WhatsApp Connection: {status['whatsapp_connection_status']}")
    #     print(f"      3. Catalog ID: {status['catalog_id_status']}")
    #     print(f"      4. Payment Details: {status['payment_details_status']}")
    # else:
    #     print(f"❌ Failed: {response.text}")
    #
    # print("\n" + "=" * 70)
    # print("✅ ONBOARDING TEST COMPLETE!")
    # print("=" * 70)


def test_skip_step():
    """Test skipping optional steps"""
    print("\n" + "=" * 70)
    print("TEST: SKIPPING OPTIONAL STEPS")
    print("=" * 70)

    # Login first
    login_data = {
        "email": "john@example.com",
        "password": "SecurePass123"
    }

    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    token_data = response.json()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    # Try skipping WhatsApp Connection
    print("\n⏭️  Attempting to skip WhatsApp Connection...")

    response = requests.post(
        f"{API_BASE}/onboarding/skip/whatsapp_connection",
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   Next Step: {result['next_step']}")
    else:
        print(f"❌ Failed: {response.text}")


if __name__ == "__main__":
    print("\n🚀 Starting Sayar Onboarding Tests...\n")

    print("Choose test to run:")
    print("1. Complete onboarding flow")
    print("2. Test skip functionality")
    print("3. Both")

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        test_complete_onboarding_flow()
    elif choice == "2":
        test_skip_step()
    elif choice == "3":
        test_complete_onboarding_flow()
        test_skip_step()
    else:
        print("Invalid choice")

    print("\n📚 Visit http://127.0.0.1:8000/api/v1/docs for interactive API documentation\n")