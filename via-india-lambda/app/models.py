from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from enum import Enum
import uuid

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"

class RequestType(str, Enum):
    NEED_HELP = "need_help"
    OFFER_HELP = "offer_help"

class RequestStatus(str, Enum):
    ACTIVE = "active"
    MATCHED = "matched"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MatchStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    COMPLETED = "completed"

# Route model
class Route(BaseModel):
    origin: str  # Airport code (e.g., "DEL")
    destination: str  # Airport code (e.g., "NYC")

    @validator('origin', 'destination')
    def validate_airport_code(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError("Airport code must be at least 3 characters")
        return v.upper().strip()

# Travel dates model
class TravelDates(BaseModel):
    departure: str  # ISO date string
    return_date: Optional[str] = None  # ISO date string
    flexible: bool = False

# Passenger details for requests needing help
class PassengerDetails(BaseModel):
    name: str
    age: Optional[int] = None
    special_needs: Optional[str] = None
    languages: List[str] = []

# Helper details for offers to help
class HelperDetails(BaseModel):
    experience: Optional[str] = None  # Previous travel experience
    languages: List[str] = []
    availability: Optional[str] = None  # Additional availability info

# User model
class User(BaseModel):
    user_id: str
    email: EmailStr
    phone: Optional[str] = None
    name: str
    company_domain: str
    verification_status: VerificationStatus = VerificationStatus.PENDING
    created_at: str
    updated_at: str

    @validator('user_id', pre=True, always=True)
    def generate_user_id(cls, v):
        return v or str(uuid.uuid4())

    @validator('created_at', 'updated_at', pre=True, always=True)
    def generate_timestamp(cls, v):
        return v or datetime.utcnow().isoformat()

    @validator('company_domain', pre=True)
    def extract_domain(cls, v, values):
        if 'email' in values:
            email = values['email']
            return email.split('@')[1] if '@' in email else v
        return v

# Request model
class Request(BaseModel):
    request_id: str
    user_id: str
    type: RequestType
    route: Route
    travel_dates: TravelDates
    passenger_details: Optional[PassengerDetails] = None
    helper_details: Optional[HelperDetails] = None
    status: RequestStatus = RequestStatus.ACTIVE
    created_at: str
    route_key: str  # Computed field for GSI queries
    departure_date: str  # Computed field for GSI queries

    @validator('request_id', pre=True, always=True)
    def generate_request_id(cls, v):
        return v or str(uuid.uuid4())

    @validator('created_at', pre=True, always=True)
    def generate_timestamp(cls, v):
        return v or datetime.utcnow().isoformat()

    @validator('route_key', pre=True, always=True)
    def generate_route_key(cls, v, values):
        if 'route' in values:
            route = values['route']
            return f"{route.origin}-{route.destination}"
        return v

    @validator('departure_date', pre=True, always=True)
    def set_departure_date(cls, v, values):
        if 'travel_dates' in values:
            return values['travel_dates'].departure
        return v

    @validator('passenger_details')
    def validate_passenger_details(cls, v, values):
        request_type = values.get('type')
        if request_type == RequestType.NEED_HELP and not v:
            raise ValueError("Passenger details required for help requests")
        return v

    @validator('helper_details')
    def validate_helper_details(cls, v, values):
        request_type = values.get('type')
        if request_type == RequestType.OFFER_HELP and not v:
            # Create default helper details if not provided
            return HelperDetails()
        return v

# Match model
class Match(BaseModel):
    match_id: str
    need_request_id: str  # Request that needs help
    offer_request_id: str  # Request offering help
    status: MatchStatus = MatchStatus.PENDING
    compatibility_score: Optional[float] = None
    both_consented: bool = False
    created_at: str
    updated_at: str

    @validator('match_id', pre=True, always=True)
    def generate_match_id(cls, v):
        return v or str(uuid.uuid4())

    @validator('created_at', 'updated_at', pre=True, always=True)
    def generate_timestamp(cls, v):
        return v or datetime.utcnow().isoformat()

# Request/Response models for API
class UserCreateRequest(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    name: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    verification_status: str
    created_at: str

class RequestCreateRequest(BaseModel):
    type: RequestType
    route: Route
    travel_dates: TravelDates
    passenger_details: Optional[PassengerDetails] = None
    helper_details: Optional[HelperDetails] = None

class RequestResponse(BaseModel):
    request_id: str
    type: str
    route: Route
    travel_dates: TravelDates
    status: str
    created_at: str
    passenger_details: Optional[PassengerDetails] = None
    helper_details: Optional[HelperDetails] = None

class MatchResponse(BaseModel):
    match_id: str
    need_request_id: str
    offer_request_id: str
    status: str
    compatibility_score: Optional[float] = None
    created_at: str

# Utility functions for DynamoDB conversion
def to_dynamodb_item(model: BaseModel) -> Dict[str, Any]:
    """Convert Pydantic model to DynamoDB item format"""
    return model.dict()

def from_dynamodb_item(item: Dict[str, Any], model_class) -> BaseModel:
    """Convert DynamoDB item to Pydantic model"""
    return model_class(**item)
