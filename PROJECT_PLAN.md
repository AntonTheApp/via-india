# Via India - Travel Companion Matching Platform

## Project Overview

**Via India** is a travel companion matching platform designed to connect non-immigrant employees' parents who need travel assistance with colleagues willing to help during international flights.

### Problem Statement

Many non-immigrant employees bring their parents to the US for short visits. These parents often face challenges:
- Limited English proficiency
- First-time international travel experience
- Unfamiliarity with airport procedures and US entry processes
- Need for assistance during long international flights

Currently, employees resort to posting in company chat groups and email lists asking for travel companions, which is:
- Inefficient and scattered across multiple platforms
- Unreliable with no guarantee of finding matches
- Lacks proper vetting and safety measures
- No structured way to track requests and offers

### Solution

A centralized platform that matches travel requests with willing companions through:
- Structured request/offer system
- Automated matching based on routes and dates
- WhatsApp-based interface for easy adoption
- Company email verification for trust and safety

## MVP Features & Requirements

### Core Features

1. **User Authentication & Verification**
   - Company email-based signup
   - Email verification workflow
   - Restricted to company employees only

2. **WhatsApp Interface**
   - Bot-based interactions for all user flows
   - No frontend development required
   - Rich messaging with quick replies and buttons

3. **Request/Offer Management**
   - Users can post companion requests or offers
   - Collect travel details: routes, dates, special needs
   - Store structured data in backend database

4. **Automated Matching**
   - Match requests with offers based on:
     - Flight routes (origin/destination)
     - Travel dates with flexibility
     - Availability and preferences
   - Real-time notifications via WhatsApp

5. **Connection Facilitation**
   - Notify both parties when matches are found
   - Facilitate consent and contact exchange
   - Enable direct communication between matched users

## Technical Architecture

### Infrastructure Stack ✅ **IMPLEMENTED**

#### **Compute & API** ✅
- **AWS Lambda**: ARM64 serverless functions with FastAPI + Mangum adapter
- **Amazon API Gateway**: RESTful API with CORS enabled
- **FastAPI**: Production-ready API with comprehensive logging and error handling

#### **Deployment & Infrastructure** ✅
- **AWS CDK**: Three-stack architecture with independent deployment capability
  - **ViaIndiaDatabaseStack**: DynamoDB tables with GSI optimization
  - **ViaIndiaLayerStack**: Lambda layer with SSM Parameter Store integration
  - **ViaIndiaCdkStack**: Main Lambda function and API Gateway
- **SSM Parameter Store**: Eliminates CDK export dependencies for layer updates
- **Asset Bundling**: Docker-based automatic dependency building
- **Independent Stack Management**: Layer deploys only when dependencies change

#### **Database** ✅
- **Amazon DynamoDB**: Pay-per-request pricing with three optimized tables
  - **Users Table**: Email GSI for user lookup
  - **Requests Table**: Route, User, and Status GSIs for efficient matching
  - **Matches Table**: Request-based GSIs for consent tracking
- **Cross-Stack Exports**: Database references imported by main stack

#### **Communication Services** (Phase 2)
- **WhatsApp Business API** or **Twilio WhatsApp API**: Chat interface
- **Amazon SES**: Email verification and notifications

#### **Security & Authentication** ✅ (Partial)
- **Company Email Verification**: Domain-based access control implemented
- **Input Validation**: Comprehensive Pydantic model validation
- **AWS IAM**: Role-based DynamoDB access permissions
- **AWS Secrets Manager**: Ready for Phase 2 API keys

### Application Architecture ✅ **IMPLEMENTED**

#### **Current Phase 1 Architecture**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Local Dev     │    │   API Gateway    │    │   Lambda        │
│   /docs Testing │◄──►│   + FastAPI      │◄──►│   Function      │
└─────────────────┘    └──────────────────┘    │   (ARM64)       │
                                                └─────────────────┘
                                                          │
┌─────────────────┐    ┌──────────────────┐              │
│   SSM Parameter │    │   Lambda Layer   │              │
│   Store         │◄──►│   (FastAPI deps) │◄─────────────┤
└─────────────────┘    └──────────────────┘              │
                                                          │
                       ┌──────────────────┐              │
                       │   DynamoDB       │◄─────────────┘
                       │   (3 Tables)     │
                       └──────────────────┘
```

#### **Phase 2 Target Architecture** (Future)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   API Gateway    │    │   Lambda        │
│   Users         │◄──►│   + FastAPI      │◄──►│   Functions     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                          │
                       ┌──────────────────┐              │
                       │   Amazon SES     │◄─────────────┤
                       │   Email Service  │              │
                       └──────────────────┘              │
                                                          │
                       ┌──────────────────┐              │
                       │   DynamoDB       │◄─────────────┘
                       │   Database       │
                       └──────────────────┘
```

## Database Design

### Core Tables

#### **Users Table**
```python
{
    "user_id": "uuid",           # Partition Key
    "email": "string",           # GSI Partition Key
    "phone": "string",           # WhatsApp number
    "name": "string",
    "company_domain": "string",
    "verification_status": "string",  # pending, verified
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

#### **Requests Table**
```python
{
    "request_id": "uuid",        # Partition Key
    "user_id": "string",         # GSI Partition Key
    "type": "string",            # "need_help" or "offer_help"
    "route": {
        "origin": "string",      # Airport code (e.g., "DEL")
        "destination": "string"  # Airport code (e.g., "NYC")
    },
    "travel_dates": {
        "departure": "date",
        "return": "date",        # Optional
        "flexible": "boolean"
    },
    "passenger_details": {
        "name": "string",
        "age": "number",
        "special_needs": "string",
        "languages": ["string"]
    },
    "helper_details": {          # For offer_help requests
        "experience": "string",
        "languages": ["string"],
        "availability": "string"
    },
    "status": "string",          # active, matched, completed
    "created_at": "timestamp"
}
```

#### **Matches Table**
```python
{
    "match_id": "uuid",          # Partition Key
    "need_request_id": "string", # Request needing help
    "offer_request_id": "string", # Offer to help
    "status": "string",          # pending, accepted, declined, completed
    "compatibility_score": "number",
    "both_consented": "boolean",
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

## Implementation Plan

### Phase 1: Foundation (Weeks 1-2) ✅ **COMPLETED**
- [x] Set up AWS infrastructure with CDK
- [x] Deploy basic FastAPI Lambda with API Gateway
- [x] Implement separate layer stack for dependencies
- [x] **Add DynamoDB tables to CDK stack** ✅
  - Created dedicated DatabaseStack with Users, Requests, Matches tables
  - Implemented Global Secondary Indexes for efficient querying
  - Cross-stack exports for table references
- [x] **Implement user signup API endpoints** ✅
  - Complete REST API with FastAPI
  - User registration, verification, and management endpoints
  - Travel request creation and matching endpoints
  - Company email domain validation
- [x] **Create user data models and validation** ✅
  - Comprehensive Pydantic models with type validation
  - Email validation with company domain restrictions
  - Route-based matching data structures
  - Automatic ID generation and timestamps

#### **Additional Phase 1 Achievements Beyond Original Plan:**
- [x] **SSM Parameter Store Integration**: Resolved CDK export dependencies for independent deployments
- [x] **Comprehensive Logging**: Added detailed logging throughout API and database layers
- [x] **Local Development Setup**: Created `run_local.py` with import path resolution
- [x] **Intelligent Matching Algorithm**: Route-based, bidirectional companion matching
- [x] **Production-Ready Architecture**: ARM64 Lambda, optimized dependencies, proper error handling
- [x] **Complete Documentation**: Root README for local development, CDK README for deployment
- [x] **Independent Stack Management**: Layer stack deploys only when dependencies change

#### **Deferred to Phase 2:**
- [ ] **Set up AWS SES for email verification** (moved to Phase 2 - WhatsApp integration priority)

### **Current Status: Phase 1 Complete, Ready for Phase 2** 🚀

### Phase 2: WhatsApp Integration (Weeks 3-4)
- [ ] Set up WhatsApp Business API or Twilio account
- [ ] Implement WhatsApp webhook handler
- [ ] Create conversational flow parser
- [ ] Build user registration via WhatsApp
- [ ] Implement basic command handling
- [ ] Add rich message formatting (buttons, quick replies)

### Phase 3: Core Functionality (Weeks 5-6)
- [ ] Build request/offer collection flows
- [ ] Implement database operations (CRUD)
- [ ] Create matching algorithm
- [ ] Add notification system
- [ ] Build consent and contact exchange flow
- [ ] Implement status tracking

### Phase 4: Testing & Refinement (Weeks 7-8)
- [ ] Internal testing with small user group
- [ ] Add error handling and edge cases
- [ ] Implement logging and monitoring
- [ ] Performance optimization
- [ ] User feedback integration
- [ ] Documentation and deployment guides

## User Experience Flows

### Registration Flow
```
1. User → WhatsApp Bot: "Hi" or "/start"
2. Bot → User: "Welcome! Please provide your company email to get started"
3. User → Bot: "john.doe@company.com"
4. Bot validates email domain
5. Bot sends verification email
6. Bot → User: "Verification email sent! Please check your inbox"
7. User clicks email link → account activated
8. Bot → User: "Account verified! You can now post requests or offers"
```

### Posting a Request for Help
```
1. User → Bot: "/request" or "I need help"
2. Bot → User: "Who needs travel assistance?"
3. User → Bot: "My mother"
4. Bot → User: "What's the travel route?" (with quick reply buttons)
5. User → Bot: "Delhi to New York"
6. Bot → User: "Travel dates?"
7. User → Bot: "December 15, 2024"
8. Bot → User: "Any special assistance needed?"
9. User → Bot: "Wheelchair assistance"
10. Bot → User: "Request posted! I'll notify you when I find matches 🔍"
```

### Offering Help
```
1. User → Bot: "/offer" or "I can help"
2. Bot → User: "What route are you traveling?"
3. User → Bot: "New York to Delhi"
4. Bot → User: "Travel dates?"
5. User → Bot: "December 14-16"
6. Bot → User: "Great! I'll match you with travelers needing help ✈️"
```

### Match Notification & Connection
```
1. Bot → Helper: "🎯 Match found! Someone needs help on your NYC→DEL route Dec 15"
2. Bot → Helper: Shows passenger details and special needs
3. Bot → Helper: "Interested in helping?" [Yes] [No] [More Info]
4. Helper → Bot: "Yes"
5. Bot → Requester: "Great news! Found a travel companion for your mother"
6. Bot → Requester: Shows helper's basic info and experience
7. Bot → Requester: "Accept this match?" [Yes] [No] [Ask Question]
8. Both parties consent → Bot facilitates contact exchange
```

## Success Metrics

### MVP Success Criteria
- 50+ company employees signed up within first month
- 10+ successful matches facilitated
- 90%+ user satisfaction in post-travel surveys
- <2 minute average response time for WhatsApp interactions

### Long-term Goals
- Expand to multiple company locations
- Add premium features (travel insurance integration)
- Scale to general public with enhanced safety features
- Partner with airlines for additional services

## Future Enhancements

### Phase 2 Features
- Mobile app for enhanced experience
- Real-time flight status integration
- Group travel coordination
- Travel document checklist
- Emergency contact system

### Phase 3 Features
- Multi-language support
- Video call integration for pre-travel meetings
- Travel expense sharing tools
- Integration with airline loyalty programs
- Advanced matching with personality compatibility

## Risk Mitigation

### Security & Privacy
- Company email verification for trust
- No sensitive personal data stored
- WhatsApp encryption for communications
- Clear data retention policies

### Safety Measures
- Mutual consent required for all matches
- Emergency contact collection
- Post-travel feedback system
- Reporting mechanism for issues

### Technical Risks
- WhatsApp API rate limiting → Implement queuing
- Lambda cold starts → Provisioned concurrency for critical functions
- Database scaling → DynamoDB on-demand pricing
- Third-party API dependencies → Fallback mechanisms

## Getting Started

### Prerequisites
- AWS Account with appropriate permissions
- Company email domain validation setup
- WhatsApp Business API access or Twilio account
- Docker installed for CDK asset bundling

### Development Setup ✅ **CURRENT INSTRUCTIONS**

#### **Local Development (API Testing)**
```bash
# Clone and setup
git clone <repository>
cd via-india

# Set up local API testing
cd via-india-lambda
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Start local development server
python run_local.py

# Test API at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

#### **AWS Deployment (Production)**
```bash
# Set up CDK environment
cd via-india-cdk
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Deploy to AWS (first time)
cdk deploy ViaIndiaDatabaseStack
cdk deploy ViaIndiaLayerStack
cdk deploy ViaIndiaCdkStack

# Regular development (code changes only)
cdk deploy ViaIndiaCdkStack
```

#### **Phase 2 Setup** (Future)
```bash
# Set up environment variables
# Add WhatsApp API keys to AWS Secrets Manager
# Configure SES for email verification
```

This document serves as the living specification for the Via India project and will be updated as features are implemented and requirements evolve.
