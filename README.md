# Via India - Travel Companion Platform

A serverless platform for matching travel companions within company networks. Employees can post travel requests (need help or offer help) and get matched with colleagues traveling on similar routes and dates.

## 🎯 Features

- **User Registration**: Company email validation and verification
- **Travel Requests**: Post needs for help or offers to help others
- **Smart Matching**: Route-based algorithm matching compatible travelers
- **RESTful API**: Complete backend with FastAPI and comprehensive logging

## 📁 Project Structure

```
via-india/
├── README.md                        # This file - project overview
├── PROJECT_PLAN.md                  # Detailed project roadmap
├── via-india-cdk/                   # AWS CDK infrastructure code
│   ├── README.md                    # CDK-specific deployment guide
│   ├── app.py                       # CDK app entry point
│   ├── via_india_cdk/               # Stack definitions
│   └── via-india-lambda-layer/      # Layer dependencies
├── via-india-lambda/                # Lambda application code
│   ├── app/                         # FastAPI application
│   │   ├── main.py                  # API endpoints
│   │   ├── models.py                # Data models
│   │   └── database.py              # DynamoDB operations
│   ├── run_local.py                 # Local development server
│   └── requirements-dev.txt         # Local development dependencies
└── index.html                       # Project landing page
```

## 🚀 Quick Start - Run API Locally

### **Prerequisites**
- Python 3.9 or higher
- pip package manager

### **1. Clone and Navigate**
```bash
git clone <your-repo-url>
cd via-india
```

### **2. Set Up Local Development Environment**
```bash
# Navigate to Lambda code
cd via-india-lambda

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### **3. Start Local API Server**
```bash
# From via-india-lambda directory
python run_local.py
```

You should see:
```
🚀 Starting Via India API locally...
📍 API will be available at: http://localhost:8000
📖 API docs at: http://localhost:8000/docs
🔄 Auto-reload enabled for development
==================================================
```

### **4. Test the API**

#### **Health Check**
```bash
curl http://localhost:8000/
```

#### **Interactive API Documentation**
Open in your browser: [http://localhost:8000/docs](http://localhost:8000/docs)

#### **Create a User**
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@amazon.com",
    "name": "John Doe",
    "phone": "+1234567890"
  }'
```

## 🧪 Development Features

### **Auto-Reload**
The local server automatically reloads when you modify code files. Just save and test!

### **Comprehensive Logging**
All API calls and operations are logged with detailed information:
```
INFO: API: Creating user account for email john.doe@amazon.com
INFO: API: Validating domain amazon.com against allowed domains
INFO: API: Domain validation passed for amazon.com
```

### **Interactive API Docs**
FastAPI automatically generates interactive documentation at `/docs`:
- Test endpoints directly in the browser
- View request/response schemas
- Explore API functionality

### **Local Limitations**
- **DynamoDB operations will fail** (expected - no local database)
- Use local testing for **API validation and business logic**
- Deploy to AWS for **full integration testing**

## 📋 Available API Endpoints

### **Health & Info**
- `GET /` - Health check and API info
- `GET /health` - Health status

### **User Management**
- `POST /users` - Create user account
- `GET /users/{user_id}` - Get user by ID
- `GET /users/email/{email}` - Get user by email
- `POST /users/{user_id}/verify` - Verify user account

### **Travel Requests**
- `POST /requests?user_id={user_id}` - Create travel request
- `GET /requests/{request_id}` - Get specific request
- `GET /users/{user_id}/requests` - Get all user requests
- `GET /requests/{request_id}/matches` - Find potential matches

## 🛠️ Development Workflow

### **Making Changes**
1. **Edit code** in `via-india-lambda/app/`
2. **Server auto-reloads** - changes are live immediately
3. **Test endpoints** using curl or `/docs` interface
4. **Check logs** in terminal for detailed operation info

### **Testing New Features**
1. **Start local server**: `python run_local.py`
2. **Open API docs**: `http://localhost:8000/docs`
3. **Test interactively** in browser
4. **View detailed logs** in terminal

### **Debugging**
- **Check terminal logs** for detailed API call information
- **Use `/docs` interface** to test requests with proper formatting
- **Verify JSON structure** against the interactive schema docs

## 🌐 Production Deployment

For deploying to AWS:
1. See `via-india-cdk/README.md` for comprehensive CDK deployment guide
2. The CDK will deploy the same FastAPI code to AWS Lambda
3. Production includes DynamoDB integration and API Gateway

## 🔧 Configuration

### **Allowed Email Domains**
Edit `via-india-lambda/app/main.py`:
```python
allowed_domains = ["amazon.com", "aboutamazon.com"]  # Add your domains
```

### **Environment Variables (Auto-set for local)**
- `USERS_TABLE_NAME` - DynamoDB users table
- `REQUESTS_TABLE_NAME` - DynamoDB requests table
- `MATCHES_TABLE_NAME` - DynamoDB matches table
- `AWS_REGION` - AWS region

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Test locally**: `python run_local.py`
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open Pull Request**

---

**Happy coding!** 🚀

For AWS deployment details, see [`via-india-cdk/README.md`](via-india-cdk/README.md)
