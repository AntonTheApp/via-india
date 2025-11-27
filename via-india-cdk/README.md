# Via India CDK Infrastructure

This CDK project implements the **Via India Travel Companion Platform** - a serverless backend for matching travel companions within company networks.

## 🏗️ Architecture Overview

The project uses a **three-stack architecture** designed for independent deployments and cost efficiency:

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  ViaIndiaDatabaseStack  │    │  ViaIndiaLayerStack   │    │  ViaIndiaCdkStack     │
│                     │    │                     │    │                     │
│  • DynamoDB Tables  │    │  • Lambda Layer     │    │  • Lambda Function  │
│  • GSI Optimization │    │  • FastAPI/Mangum   │    │  • API Gateway      │
│  • Cross-stack      │    │  • Auto-bundling    │    │  • Permissions      │
│    Exports          │    │  • SSM Parameter    │    │  • SSM Lookup       │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 📦 Stack Dependencies

### **Dependency Management Strategy**

We use **SSM Parameter Store** instead of CloudFormation exports for layer dependencies to enable independent deployments:

- **Database Stack** → **Main Stack**: Traditional exports (tables rarely change)
- **Layer Stack** → **Main Stack**: **SSM Parameter Store** (enables independent layer updates)

### **Why SSM Parameter Store?**

**Problem**: CloudFormation exports create deployment dependencies. When a Lambda layer is redeployed, AWS creates a new layer version with a new ARN. This changes the export value, but CDK blocks the update because the main stack is importing it.

**Solution**: Store the layer ARN in SSM Parameter Store instead of exports:

```python
# Layer Stack: Stores ARN in SSM
ssm.StringParameter(
    parameter_name="/via-india/layer/fastapi-arn",
    string_value=layer.layer_version_arn
)

# Main Stack: Reads from SSM (no dependency)
layer_arn = ssm.StringParameter.value_for_string_parameter(
    self, "/via-india/layer/fastapi-arn"
)
```

## 🚀 Deployment Strategies

### **Initial Setup (First Time)**
```bash
# Deploy all stacks in dependency order
cdk deploy ViaIndiaDatabaseStack
cdk deploy ViaIndiaLayerStack
cdk deploy ViaIndiaCdkStack
```

### **Regular Development Workflow**

#### **When Only Lambda Code Changes** (Most Common)
```bash
# Deploy just the main stack - fast iteration!
cdk deploy ViaIndiaCdkStack
```

#### **When Layer Dependencies Change** (Rare)
```bash
# 1. Update layer with new dependencies
cdk deploy ViaIndiaLayerStack

# 2. Deploy main stack to use new layer version
cdk deploy ViaIndiaCdkStack
```

#### **When Database Schema Changes** (Rare)
```bash
# Deploy database first, then main stack
cdk deploy ViaIndiaDatabaseStack ViaIndiaCdkStack
```

### **Emergency: Force All Updates**
```bash
# Deploy all stacks together (handles all dependencies)
cdk deploy --all
```

## 🛠️ Development Setup

### **Prerequisites**
- Python 3.9+
- Node.js 18+ (for CDK)
- Docker (for Lambda layer building)
- AWS CLI configured

### **Initial Setup**
```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate.bat

# 2. Install CDK dependencies
pip install -r requirements.txt

# 3. Install CDK CLI (if not installed)
npm install -g aws-cdk

# 4. Verify setup
cdk ls
```

### **Local Development**
```bash
# Test Lambda code locally (in ../via-india-lambda/)
cd ../via-india-lambda
python run_local.py  # Starts FastAPI server on localhost:8000
```

## 📁 Project Structure

```
via-india-cdk/
├── app.py                          # CDK app entry point
├── cdk.json                        # CDK configuration
├── requirements.txt                # CDK dependencies
├── via_india_cdk/
│   ├── database_stack.py           # DynamoDB tables and GSIs
│   ├── layer_stack.py              # Lambda layer with SSM parameter
│   └── via_india_cdk_stack.py      # Main Lambda + API Gateway
└── via-india-lambda-layer/
    └── requirements.txt            # Layer dependencies (FastAPI, etc.)
```

## 🔍 Stack Details

### **ViaIndiaDatabaseStack**
- **Users Table**: Company email validation, verification workflow
- **Requests Table**: Travel requests with route-based matching GSIs
- **Matches Table**: Companion matching with consent tracking
- **Exports**: Table names and ARNs for main stack import

### **ViaIndiaLayerStack**
- **FastAPI Layer**: Auto-bundled with Docker for ARM64
- **Dependencies**: FastAPI, Mangum, Uvicorn, Pydantic[email]
- **SSM Parameter**: `/via-india/layer/fastapi-arn` stores layer ARN
- **No Exports**: Uses SSM to avoid deployment conflicts

### **ViaIndiaCdkStack**
- **Lambda Function**: FastAPI app with Mangum adapter
- **API Gateway**: RESTful API with CORS enabled
- **Imports**: Database tables from exports, layer ARN from SSM
- **Permissions**: Read/write access to DynamoDB tables

## ⚡ Performance Optimizations

### **Layer Management**
- **ARM64 Architecture**: Better price/performance ratio
- **Optimized Dependencies**: No boto3 (AWS provides it)
- **Docker Bundling**: Consistent, platform-specific builds
- **Independent Updates**: Only rebuild when dependencies change

### **Database Design**
- **Global Secondary Indexes**: Fast queries by email, route, status
- **Composite Keys**: Route matching with `origin-destination` format
- **Pay-per-request**: Cost-effective scaling

## 🐛 Troubleshooting

### **Common CDK Deployment Issues**

#### **"Export in use" Error**
```
Update canceled. Cannot update export ViaIndiaFastAPILayerArn as it is in use by ViaIndiaCdkStack.
```
**Solution**: This shouldn't happen with SSM Parameter Store approach. If you see this, verify you're using the updated stacks with SSM parameters.

#### **Layer Build Failures**
```
docker: command not found
```
**Solution**: Install Docker and ensure it's running before deploying layer stack.

#### **Permission Denied During Build**
```
Permission denied while trying to connect to Docker daemon
```
**Solution**:
- **macOS/Linux**: `sudo usermod -aG docker $USER` (logout/login required)
- **Windows**: Run as Administrator or add user to docker-users group

### **Local Development Issues**

#### **Import Errors in Local Testing**
```
ModuleNotFoundError: No module named 'models'
```
**Solution**: Use the provided `run_local.py` script instead of running `uvicorn` directly.

#### **DynamoDB Connection Errors (Expected)**
Local development won't connect to AWS DynamoDB. This is expected - use local testing for API validation, deploy to AWS for full integration testing.

## 📚 API Endpoints

Once deployed, your API provides:



- **Matching**: `GET /requests/{id}/matches`

Interactive API documentation available at: `https://your-api-gateway-url/docs`

### Testing from API Gateway Console
Go to AWS API Gateway Console: API Gateway/APIs/Resources - TravelCompanionAPI
Resources-> /{proxy+} - ANY - Method execution

Use below Method Type, proxy, Request Body based on the operation:

- **Health**: `GET /` and `GET /health`
- **Users**: 
`POST /users`
{
    "email": "john.doe@example.com",
    "name": "John Doe",
    "phone": "+1234567890"
  }

`GET /users/{id}`
Sample id: ec9d61c0-94cf-49ab-9d5d-d885817ccd60

`POST /users/{id}/verify`
Empty body
Sample id: ec9d61c0-94cf-49ab-9d5d-d885817ccd60

- **Requests**: 
`POST /requests`

query param: user_id=ec9d61c0-94cf-49ab-9d5d-d885817ccd60
{
  "type": "need_help",
  "route": {
    "origin": "DEL",
    "destination": "JFK"
  },
  "travel_dates": {
    "departure": "2025-12-15",
    "return": "2025-12-30",
    "flexible": false
  },
  "passenger_details": {
    "name": "Anita Sharma",
    "age": 67,
    "special_needs": "Wheelchair assistance at airport",
    "languages": ["Hindi"]
  },
  "status": "active",
  "notes": "Needs help with check-in and immigration formalities."
}

query param: user_id=cdfe2c71-bf76-41d5-8203-f40982e6d6bd
{
  "type": "offer_help",
  "route": {
    "origin": "JFK",
    "destination": "DEL"
  },
  "travel_dates": {
    "departure": "2025-12-14",
    "return": "2025-12-16",
    "flexible": true
  },
  "helper_details": {
    "experience": "Frequently travels to India, comfortable assisting seniors",
    "languages": ["English", "Hindi"],
    "availability": "Can assist at JFK on 2025-12-14"
  },
  "status": "active",
  "notes": "Can help with airport navigation and boarding."
}

`GET /requests/{id}`
Sample request ID: 862c09ee-f4be-4a5d-8232-a41c6df97145

`GET /users/{id}/requests`
Sample user ID with requests: ec9d61c0-94cf-49ab-9d5d-d885817ccd60

`GET /requests/{request_id}/matches`
Sample request ID with matches: 862c09ee-f4be-4a5d-8232-a41c6df97145



## 🔄 CI/CD Considerations

### **Recommended Pipeline**
1. **PR Validation**: `cdk synth` to validate templates
2. **Layer Updates**: Deploy layer stack when `requirements.txt` changes
3. **Code Updates**: Deploy main stack for Lambda code changes
4. **Integration Tests**: Test deployed API endpoints

### **Environment Strategy**
- **Development**: Independent developer stacks
- **Staging**: Shared staging environment
- **Production**: Separate AWS account with approval gates

## 📈 Monitoring

### **CloudWatch Logs**
```bash
# View Lambda logs
aws logs tail /aws/lambda/ViaIndiaCdkStack-TravelCompanionLambda --follow
```

### **Key Metrics**
- Lambda duration and error rate
- API Gateway 4xx/5xx errors
- DynamoDB read/write capacity
- Layer cold start performance

## 🚀 Next Steps (Phase 2)

The current Phase 1 foundation supports:
- User registration and verification
- Travel request creation and matching
- RESTful API with comprehensive logging

**Phase 2 additions:**
- WhatsApp bot integration
- Email verification with SES
- Enhanced matching algorithm with scoring
- Real-time notifications

---

## 📞 Support

For questions or issues:
1. Check this README for common solutions
2. Review CloudWatch logs for runtime errors
3. Use `cdk diff` to preview changes before deployment
4. Test locally with `run_local.py` for faster iteration

**Happy coding!** 🚀
