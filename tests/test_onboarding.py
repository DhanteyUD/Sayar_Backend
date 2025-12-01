"""
Test script for Sayar merchant onboarding flow
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

access_token = None
merchant_id = None


def print_step(step_num, title):
    print("\n" + "=" * 70)
    print(f"STEP {step_num}: {title}")
    print("=" * 70)


def test_signup_and_login():
    global access_token, merchant_id

    print_step(0, "MERCHANT SIGNUP & LOGIN")

    signup_data = {
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah@bookio.com",
        "phone": "+2348012345678",
        "business_name": "Bookio",
        "password": "BookioPass123",
        "confirm_password": "BookioPass123",
        "agree_to_terms": True,
        "send_marketing_emails": False
    }

    print("\n📝 Attempting signup...")
    response = requests.post(f"{BASE_URL}/auth/signup/merchant", json=signup_data)

    if response.status_code == 201:
        print("✅ Signup successful!")
        result = response.json()
        access_token = result["tokens"]["access_token"]
        merchant_id = result["merchant"]["id"]
        print(f"Merchant ID: {merchant_id}")
    elif response.status_code == 400:
        print("ℹ️  User exists, logging in instead...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "sarah@bookio.com", "password": "BookioPass123"}
        )

        if login_response.status_code == 200:
            print("✅ Login successful!")
            result = login_response.json()
            access_token = result["access_token"]

            me_response = requests.get(
                f"{BASE_URL}/auth/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            if me_response.status_code == 200:
                # For now, we'll need to get merchant_id from database or pass it manually
                # In production, you'd have an endpoint to list user's merchants
                merchant_id = input("Enter your merchant ID: ")
        else:
            print(f"❌ Login failed: {login_response.text}")
            return False
    else:
        print(f"❌ Signup failed: {response.text}")
        return False

    print(f"\n🔑 Access Token: {access_token[:50]}...")
    print(f"🏢 Merchant ID: {merchant_id}")
    return True


def get_onboarding_progress():
    print_step("?", "GET ONBOARDING PROGRESS")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{BASE_URL}/onboarding/progress",
        params={"merchant_id": merchant_id},
        headers=headers
    )

    if response.status_code == 200:
        progress = response.json()
        print("\n✅ Current Progress:")
        print(f"   Status: {progress['status']}")
        print(f"   Current Step: {progress['current_step']}")
        print(f"   Completed: {progress['steps_completed']}/{progress['total_steps']}")
        print(f"   Percentage: {progress['completion_percentage']}%")
        print(f"\n   Steps:")
        print(f"   1. Business Details: {progress['business_details']['status']}")
        print(f"   2. WhatsApp Connection: {progress['whatsapp_connection']['status']}")
        print(f"   3. Catalog ID: {progress['catalog_id']['status']}")
        print(f"   4. Payment Details: {progress['payment_details']['status']}")
        return progress
    else:
        print(f"❌ Failed: {response.text}")
        return None


def complete_step1_business_details():
    print_step(1, "BUSINESS DETAILS")

    data = {
        "business_name": "Bookio",
        "business_email": "support@bookio.com",
        "business_category": "education",
        "operating_currency": "NGN",
        "business_description": "Agriculture Educational Platform",
        "business_phone": "+2348012345678",
        "address_line1": "123 Farm Road",
        "country": "Nigeria",
        "state": "Lagos"
    }

    print("\n📤 Submitting business details...")
    print(json.dumps(data, indent=2))

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        f"{BASE_URL}/onboarding/step1/business-details",
        params={"merchant_id": merchant_id},
        json=data,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ {result['message']}")
        print(f"   Steps completed: {result['onboarding']['steps_completed']}/4")
        print(f"   Progress: {result['onboarding']['completion_percentage']}%")
        return True
    else:
        print(f"\n❌ Failed: {response.text}")
        return False


def complete_step2_whatsapp():
    print_step(2, "WHATSAPP CONNECTION")

    data = {
        "app_id": "sayar-merchant-12345",
        "app_secret": "EAAwG...YourSecretToken...L4xZ",
        "business_account_id": "123456789012345",
        "phone_number_id": "987654321098765",
        "whatsapp_phone_number": "+2348012345678",
        "access_token": "EAAwG...YourAccessToken...xYz"
    }

    print("\n📤 Submitting WhatsApp configuration...")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        f"{BASE_URL}/onboarding/step2/whatsapp-connection",
        params={"merchant_id": merchant_id},
        json=data,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ {result['message']}")

        print("\n🔄 Testing WhatsApp connection...")
        test_response = requests.post(
            f"{BASE_URL}/onboarding/step2/test-connection",
            params={"merchant_id": merchant_id},
            headers=headers
        )

        if test_response.status_code == 200:
            test_result = test_response.json()
            print(f"   {test_result['message']}")

        return True
    else:
        print(f"\n❌ Failed: {response.text}")
        return False


def complete_step3_catalog():
    print_step(3, "META CATALOG ID")

    print("\nOptions:")
    print("1. Configure catalog")
    print("2. Skip this step")

    choice = input("\nEnter choice (1/2): ").strip()

    headers = {"Authorization": f"Bearer {access_token}"}

    if choice == "2":
        print("\n⏭️  Skipping catalog configuration...")
        response = requests.post(
            f"{BASE_URL}/onboarding/step3/skip",
            params={"merchant_id": merchant_id},
            headers=headers
        )
    else:
        data = {
            "catalog_id": "1234567890",
            "product_feed_url": "https://example.com/sayar/"
        }

        print("\n📤 Submitting catalog configuration...")
        response = requests.post(
            f"{BASE_URL}/onboarding/step3/catalog-connection",
            params={"merchant_id": merchant_id},
            json=data,
            headers=headers
        )

        if response.status_code == 200:
            print("\n🔄 Testing catalog connection...")
            test_response = requests.post(
                f"{BASE_URL}/onboarding/step3/test-connection",
                params={"merchant_id": merchant_id},
                headers=headers
            )

            if test_response.status_code == 200:
                test_result = test_response.json()
                print(f"   {test_result['message']}")
                print(f"   Feed Status: {test_result.get('feed_status', 'N/A')}")

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ {result['message']}")
        return True
    else:
        print(f"\n❌ Failed: {response.text}")
        return False


def complete_step4_payment():
    print_step(4, "PAYMENT DETAILS")

    data = {
        "bank_name": "Access Bank",
        "account_number": "0123456789"
    }

    print("\n📤 Submitting payment details...")
    print(json.dumps(data, indent=2))

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(
        f"{BASE_URL}/onboarding/step4/payment-details",
        params={"merchant_id": merchant_id},
        json=data,
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ {result['message']}")

        if result['onboarding']['is_completed']:
            print("\n🎉🎉🎉 ONBOARDING COMPLETED! 🎉🎉🎉")
            print(f"   All {result['onboarding']['total_steps']} steps completed!")

        return True
    else:
        print(f"\n❌ Failed: {response.text}")
        return False


def main():
    print("\n🚀 SAYAR MERCHANT ONBOARDING TEST")
    print("=" * 70)

    if not test_signup_and_login():
        print("\n❌ Authentication failed. Exiting.")
        return

    input("\nPress Enter to continue...")

    get_onboarding_progress()
    input("\nPress Enter to start onboarding...")

    # Step 1: Business Details
    if complete_step1_business_details():
        get_onboarding_progress()
        input("\nPress Enter to continue...")

    # Step 2: WhatsApp
    if complete_step2_whatsapp():
        get_onboarding_progress()
        input("\nPress Enter to continue...")

    # Step 3: Catalog
    if complete_step3_catalog():
        get_onboarding_progress()
        input("\nPress Enter to continue...")

    # Step 4: Payment
    if complete_step4_payment():
        get_onboarding_progress()

    print("\n" + "=" * 70)
    print("✅ ONBOARDING TEST COMPLETE!")
    print("=" * 70)
    print("\n📚 Check the database to see all the onboarding records.")
    print("🌐 Visit http://127.0.0.1:8000/api/v1/docs for API documentation.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
