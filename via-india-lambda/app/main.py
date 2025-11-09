from typing import Union, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import logging

from models import (
    UserCreateRequest, UserResponse,
    RequestCreateRequest, RequestResponse,
    Route, TravelDates, PassengerDetails, HelperDetails,
    RequestType, VerificationStatus
)
from database import db

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Via India - Travel Companion API",
    description="API for matching travel companions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
def read_root():
    return {
        "message": "Via India Travel Companion API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2024-11-08T22:10:00Z"}

# User endpoints
@app.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreateRequest):
    """Create a new user account"""
    logger.info(f"API: Creating user account for email {user_data.email}")
    try:
        # Validate company domain (you can customize this)
        allowed_domains = ["example.com"]  # Add your company domains
        domain = user_data.email.split('@')[1]
        logger.info(f"API: Validating domain {domain} against allowed domains")

        if domain not in allowed_domains:
            logger.info(f"API: Domain {domain} not in allowed list")
            raise HTTPException(
                status_code=400,
                detail=f"Email domain {domain} not allowed. Must use company email."
            )

        logger.info(f"API: Domain validation passed for {domain}")
        user = await db.create_user(user_data)

        logger.info(f"API: Successfully created user {user.user_id} with email {user_data.email}")
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            verification_status=user.verification_status.value,
            created_at=user.created_at
        )

    except ValueError as e:
        logger.info(f"API: User creation failed with ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID"""
    logger.info(f"API: Getting user by ID {user_id}")
    try:
        user = await db.get_user_by_id(user_id)
        if not user:
            logger.info(f"API: User {user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"API: Successfully retrieved user {user_id}")
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            verification_status=user.verification_status.value,
            created_at=user.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    """Get user by email"""
    logger.info(f"API: Getting user by email {email}")
    try:
        user = await db.get_user_by_email(email)
        if not user:
            logger.info(f"API: User with email {email} not found")
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"API: Successfully retrieved user {user.user_id} by email {email}")
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            verification_status=user.verification_status.value,
            created_at=user.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/users/{user_id}/verify")
async def verify_user(user_id: str):
    """Verify user email (simplified for MVP)"""
    logger.info(f"API: Verifying user {user_id}")
    try:
        success = await db.update_user_verification(user_id, VerificationStatus.VERIFIED)
        if success:
            logger.info(f"API: Successfully verified user {user_id}")
            return {"message": "User verified successfully"}
        else:
            logger.info(f"API: Verification failed for user {user_id}")
            raise HTTPException(status_code=400, detail="Verification failed")

    except Exception as e:
        logger.error(f"Error verifying user: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Request endpoints
@app.post("/requests", response_model=RequestResponse)
async def create_request(request_data: RequestCreateRequest, user_id: str):
    """Create a new travel request"""
    logger.info(f"API: Creating {request_data.type.value} request for user {user_id} on route {request_data.route.origin}->{request_data.route.destination}")
    try:
        # Verify user exists
        logger.info(f"API: Verifying user {user_id} exists and is verified")
        user = await db.get_user_by_id(user_id)
        if not user:
            logger.info(f"API: User {user_id} not found for request creation")
            raise HTTPException(status_code=404, detail="User not found")

        if user.verification_status != VerificationStatus.VERIFIED:
            logger.info(f"API: User {user_id} is not verified (status: {user.verification_status})")
            raise HTTPException(status_code=400, detail="User must be verified to create requests")

        logger.info(f"API: User {user_id} validation passed, creating request")
        request = await db.create_request(user_id, request_data)

        logger.info(f"API: Successfully created request {request.request_id} for user {user_id}")
        return RequestResponse(
            request_id=request.request_id,
            type=request.type.value,
            route=request.route,
            travel_dates=request.travel_dates,
            status=request.status.value,
            created_at=request.created_at,
            passenger_details=request.passenger_details,
            helper_details=request.helper_details
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/requests/{request_id}", response_model=RequestResponse)
async def get_request(request_id: str):
    """Get request by ID"""
    logger.info(f"API: Getting request by ID {request_id}")
    try:
        request = await db.get_request_by_id(request_id)
        if not request:
            logger.info(f"API: Request {request_id} not found")
            raise HTTPException(status_code=404, detail="Request not found")

        logger.info(f"API: Successfully retrieved request {request_id}")
        return RequestResponse(
            request_id=request.request_id,
            type=request.type.value,
            route=request.route,
            travel_dates=request.travel_dates,
            status=request.status.value,
            created_at=request.created_at,
            passenger_details=request.passenger_details,
            helper_details=request.helper_details
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/users/{user_id}/requests", response_model=List[RequestResponse])
async def get_user_requests(user_id: str):
    """Get all requests for a user"""
    logger.info(f"API: Getting all requests for user {user_id}")
    try:
        requests = await db.get_requests_by_user(user_id)

        logger.info(f"API: Found {len(requests)} requests for user {user_id}")
        return [
            RequestResponse(
                request_id=req.request_id,
                type=req.type.value,
                route=req.route,
                travel_dates=req.travel_dates,
                status=req.status.value,
                created_at=req.created_at,
                passenger_details=req.passenger_details,
                helper_details=req.helper_details
            )
            for req in requests
        ]

    except Exception as e:
        logger.error(f"Error getting user requests: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/requests/{request_id}/matches")
async def find_matches(request_id: str):
    """Find potential matches for a request"""
    logger.info(f"API: Finding matches for request {request_id}")
    try:
        request = await db.get_request_by_id(request_id)
        if not request:
            logger.info(f"API: Request {request_id} not found for matching")
            raise HTTPException(status_code=404, detail="Request not found")

        logger.info(f"API: Running matching algorithm for {request.type.value} request on route {request.route_key}")
        matches = await db.find_potential_matches(request)

        logger.info(f"API: Found {len(matches)} potential matches for request {request_id}")
        return {
            "request_id": request_id,
            "matches_found": len(matches),
            "matches": [
                {
                    "request_id": match.request_id,
                    "type": match.type.value,
                    "route": match.route,
                    "travel_dates": match.travel_dates,
                    "user_id": match.user_id
                }
                for match in matches
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding matches: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Lambda handler
handler = Mangum(app)
