# Sayar
WhatsApp-based commerce system designed to streamline the buying and selling experience

# Sayar WhatsApp Commerce Backend

A comprehensive FastAPI backend for WhatsApp-based e-commerce platform with Paystack payment integration, Cloudinary media management, and PostgreSQL database.

## 🚀 Features

- **User Authentication** - JWT-based auth with refresh tokens
- **Merchant Management** - Complete merchant onboarding and profile management
- **Product Catalog** - Product management with multiple image uploads
- **Order Processing** - End-to-end order management system
- **Payment Integration** - Paystack payment gateway integration
- **WhatsApp Integration** - Meta Cloud API for messaging
- **Invoice Generation** - Automated invoice creation
- **Admin Dashboard** - Comprehensive admin panel APIs
- **Shipping & Tracking** - Delivery tracking system
- **File Upload** - Cloudinary integration for image management

## 📋 Prerequisites

- Python 3.9 or higher
- PostgreSQL 12 or higher
- Cloudinary account
- Paystack account
- Meta/Facebook Business account (for WhatsApp API)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sayar-backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Setup

Create a `.env` file in the root directory:

```env
# Application
APP_NAME=Sayar Backend
APP_ENV=development
DEBUG=True
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/sayar_db

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Paystack
PAYSTACK_SECRET_KEY=sk_test_your_secret_key
PAYSTACK_PUBLIC_KEY=pk_test_your_public_key
PAYSTACK_CALLBACK_URL=http://localhost:8000/api/v1/payments/callback

# WhatsApp (Meta Cloud API)
WHATSAPP_API_TOKEN=your_whatsapp_api_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_VERIFY_TOKEN=your_webhook_verify_token

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAILS_FROM_EMAIL=noreply@sayar.com

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### 5. Database Setup

```bash
# Create PostgreSQL database
createdb sayar_db

# Or using psql
psql -U postgres
CREATE DATABASE sayar_db;
\q

# Run migrations
alembic upgrade head
```

## 🏃 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Access the application:
- API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 Project Structure

```
sayar-backend/
├── app/
│   ├── api/              # API route handlers
│   ├── core/             # Core functionality (security, deps)
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   └── main.py           # Application entry point
├── alembic/              # Database migrations
├── tests/                # Test files
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔌 API Endpoints

### Authentication
```
POST   /api/v1/auth/register       - Register new merchant
POST   /api/v1/auth/login          - Login
POST   /api/v1/auth/refresh        - Refresh token
GET    /api/v1/auth/me             - Get current user
POST   /api/v1/auth/logout         - Logout
```

### Merchants
```
GET    /api/v1/merchants/profile       - Get profile
PUT    /api/v1/merchants/profile       - Update profile
POST   /api/v1/merchants/onboard       - Complete onboarding
GET    /api/v1/merchants/dashboard     - Dashboard stats
```

### Products
```
GET    /api/v1/products                - List products
POST   /api/v1/products                - Create product
GET    /api/v1/products/{id}           - Get product
PUT    /api/v1/products/{id}           - Update product
DELETE /api/v1/products/{id}           - Delete product
POST   /api/v1/products/{id}/images    - Upload images
```

### Orders
```
GET    /api/v1/orders                  - List orders
POST   /api/v1/orders                  - Create order
GET    /api/v1/orders/{id}             - Get order
PUT    /api/v1/orders/{id}/status      - Update status
GET    /api/v1/orders/{id}/tracking    - Track delivery
```

### Payments
```
POST   /api/v1/payments/initialize     - Initialize payment
GET    /api/v1/payments/verify/{ref}   - Verify payment
POST   /api/v1/payments/callback       - Payment callback
GET    /api/v1/payments/transactions   - List transactions
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py -v
```

## 🚢 Deployment

### Deploy to Railway.app

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login and deploy:
```bash
railway login
railway init
railway up
```

3. Add environment variables in Railway dashboard

### Deploy to Render.com

1. Connect your GitHub repository
2. Create new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`
5. Add environment variables
6. Deploy

### Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create app
heroku create sayar-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your_secret_key
heroku config:set CLOUDINARY_CLOUD_NAME=your_cloud_name
# ... set other env vars

# Deploy
git push heroku main
```

### Using Docker

```bash
# Build image
docker build -t sayar-backend .

# Run container
docker run -d -p 8000:8000 --env-file .env sayar-backend
```

## 🔐 Security Best Practices

1. Never commit `.env` file
2. Use strong `SECRET_KEY` in production
3. Enable HTTPS in production
4. Implement rate limiting
5. Validate all user inputs
6. Keep dependencies updated
7. Use environment-specific configurations
8. Enable CORS only for trusted origins

## 📊 Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current version
alembic current
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Verify DATABASE_URL in .env
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

### Cloudinary Upload Failures
- Verify API credentials in `.env`
- Check file size limits (default: 5MB)
- Ensure proper file format (JPEG, PNG, WebP)

### Payment Verification Issues
- Verify Paystack secret key
- Check webhook URL is publicly accessible
- Ensure callback URL is correct

### WhatsApp Messages Not Sending
- Verify API token is valid
- Check phone number ID
- Ensure business account is verified
- Check message format compliance

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Paystack API Docs](https://paystack.com/docs)
- [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Cloudinary Docs](https://cloudinary.com/documentation)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Support

For support, email support@sayar.com or open an issue on GitHub.

---

**Made with ❤️ by Sayar Team**