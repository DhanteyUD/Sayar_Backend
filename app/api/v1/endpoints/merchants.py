# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
#
# from ....core.database import get_db
# from ....core.security import get_current_user
# from ....models.user import User
# from ....models.merchant import Merchant
# from ....schemas.merchant import MerchantCreate, MerchantResponse, MerchantUpdate
# from ....services.payment_service import paystack_service
#
# router = APIRouter()
#
#
# @router.post("/", response_model=MerchantResponse)
# async def create_merchant(
#         merchant_data: MerchantCreate,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     existing_merchant = db.query(Merchant).filter_by(owner_id=current_user.id).first()
#     if existing_merchant:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="User already has a merchant account"
#         )
#
#     # Create Paystack subaccount for merchant
#     paystack_result = paystack_service.create_subaccount(
#         business_name=merchant_data.business_name,
#         account_number=merchant_data.paystack_account_number,
#         bank_code=merchant_data.paystack_bank_code
#     )
#
#     if not paystack_result.get("status"):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Paystack account creation failed: {paystack_result.get('message')}"
#         )
#
#     # Create merchant in database
#     db_merchant = Merchant(
#         business_name=merchant_data.business_name,
#         business_registration_number=merchant_data.business_registration_number,
#         business_address=merchant_data.business_address,
#         industry_type=merchant_data.industry_type,
#         business_category=merchant_data.business_category,
#         paystack_bank_code=merchant_data.paystack_bank_code,
#         paystack_account_number=merchant_data.paystack_account_number,
#         owner_id=current_user.id,
#         paystack_subaccount_id=paystack_result["data"]["subaccount_code"],
#         onboarding_completed=False
#     )
#
#     db.add(db_merchant)
#     db.commit()
#     db.refresh(db_merchant)
#
#     return db_merchant
#
#
# @router.get("/", response_model=MerchantResponse)
# async def get_merchant(
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
#     merchant = db.query(Merchant).filter_by(owner_id=current_user.id).first()
#     if not merchant:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Merchant account not found"
#         )
#
#     return merchant
#
#
# @router.put("/", response_model=MerchantResponse)
# async def update_merchant(
#         merchant_data: MerchantUpdate,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
#     if not merchant:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Merchant account not found"
#         )
#
#     # Update merchant fields
#     update_data = merchant_data.dict(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(merchant, field, value)
#
#     db.commit()
#     db.refresh(merchant)
#
#     return merchant
#
#
# @router.post("/complete-onboarding")
# async def complete_onboarding(
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
#     if not merchant:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Merchant account not found"
#         )
#
#     # Check if all required fields are set
#     required_fields = [
#         merchant.whatsapp_business_account_id,
#         merchant.meta_catalog_id,
#         merchant.paystack_subaccount_id
#     ]
#
#     if not all(required_fields):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Please complete all integration setups first"
#         )
#
#     merchant.onboarding_completed = True
#     db.commit()
#
#     return {"message": "Onboarding completed successfully"}
#
#
# @router.post("/connect-whatsapp")
# async def connect_whatsapp(
#         whatsapp_data: dict,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
#     if not merchant:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Merchant account not found"
#         )
#
#     # Update WhatsApp connection details
#     merchant.whatsapp_business_account_id = whatsapp_data.get("business_account_id")
#     merchant.whatsapp_phone_number = whatsapp_data.get("phone_number")
#     merchant.whatsapp_access_token = whatsapp_data.get("access_token")
#     merchant.whatsapp_verified = True
#
#     db.commit()
#
#     return {"message": "WhatsApp connection established successfully"}
#
#
# @router.post("/connect-meta-catalog")
# async def connect_meta_catalog(
#         meta_data: dict,
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     merchant = db.query(Merchant).filter(Merchant.owner_id == current_user.id).first()
#     if not merchant:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Merchant account not found"
#         )
#
#     # Update Meta Catalog details
#     merchant.meta_business_manager_id = meta_data.get("business_manager_id")
#     merchant.meta_catalog_id = meta_data.get("catalog_id")
#
#     db.commit()
#
#     return {"message": "Meta Catalog connected successfully"}
