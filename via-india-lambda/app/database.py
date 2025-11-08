import os
import boto3
from typing import Optional, List, Dict, Any
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import logging

from models import (
    User, Request, Match,
    UserCreateRequest, RequestCreateRequest,
    VerificationStatus, RequestStatus, RequestType,
    to_dynamodb_item, from_dynamodb_item
)

# Set up logging
logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-west-2'))

        # Get table names from environment variables
        self.users_table_name = os.getenv('USERS_TABLE_NAME')
        self.requests_table_name = os.getenv('REQUESTS_TABLE_NAME')
        self.matches_table_name = os.getenv('MATCHES_TABLE_NAME')

        # Initialize table objects
        self.users_table = self.dynamodb.Table(self.users_table_name)
        self.requests_table = self.dynamodb.Table(self.requests_table_name)
        self.matches_table = self.dynamodb.Table(self.matches_table_name)

    # User operations
    async def create_user(self, user_data: UserCreateRequest) -> User:
        """Create a new user"""
        logger.info(f"Creating new user with email: {user_data.email}")
        try:
            user = User(
                user_id="",  # Will be auto-generated
                email=user_data.email,
                phone=user_data.phone,
                name=user_data.name,
                company_domain="",  # Will be extracted from email
                created_at="",  # Will be auto-generated
                updated_at=""   # Will be auto-generated
            )

            # Convert to DynamoDB item
            item = to_dynamodb_item(user)
            logger.info(f"Generated user_id: {user.user_id} for {user_data.email}")

            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                logger.info(f"User with email {user_data.email} already exists")
                raise ValueError(f"User with email {user_data.email} already exists")

            # Save to DynamoDB
            self.users_table.put_item(Item=item)
            logger.info(f"Successfully created user {user.user_id} with email {user_data.email}")

            return user

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by user_id"""
        logger.info(f"Looking up user by ID: {user_id}")
        try:
            response = self.users_table.get_item(Key={'user_id': user_id})

            if 'Item' in response:
                logger.info(f"Found user {user_id}")
                return from_dynamodb_item(response['Item'], User)
            logger.info(f"User {user_id} not found")
            return None

        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email using GSI"""
        logger.info(f"Looking up user by email: {email}")
        try:
            response = self.users_table.query(
                IndexName='EmailIndex',
                KeyConditionExpression=Key('email').eq(email)
            )

            if response['Items']:
                logger.info(f"Found user with email {email}")
                return from_dynamodb_item(response['Items'][0], User)
            logger.info(f"No user found with email {email}")
            return None

        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            raise

    async def update_user_verification(self, user_id: str, status: VerificationStatus) -> bool:
        """Update user verification status"""
        logger.info(f"Updating verification status for user {user_id} to {status.value}")
        try:
            from datetime import datetime

            response = self.users_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET verification_status = :status, updated_at = :updated_at',
                ExpressionAttributeValues={
                    ':status': status.value,
                    ':updated_at': datetime.utcnow().isoformat()
                },
                ReturnValues='UPDATED_NEW'
            )
            logger.info(f"Successfully updated user {user_id} verification status to {status.value}")
            return True

        except Exception as e:
            logger.error(f"Error updating user verification: {str(e)}")
            raise

    # Request operations
    async def create_request(self, user_id: str, request_data: RequestCreateRequest) -> Request:
        """Create a new travel request"""
        logger.info(f"Creating {request_data.type.value} request for user {user_id}, route: {request_data.route.origin} -> {request_data.route.destination}")
        try:
            request = Request(
                request_id="",  # Will be auto-generated
                user_id=user_id,
                type=request_data.type,
                route=request_data.route,
                travel_dates=request_data.travel_dates,
                passenger_details=request_data.passenger_details,
                helper_details=request_data.helper_details,
                created_at="",  # Will be auto-generated
                route_key="",   # Will be auto-generated
                departure_date=""  # Will be auto-generated
            )

            # Convert to DynamoDB item
            item = to_dynamodb_item(request)
            logger.info(f"Generated request_id: {request.request_id} for user {user_id}")

            # Save to DynamoDB
            self.requests_table.put_item(Item=item)
            logger.info(f"Successfully created request {request.request_id} - {request_data.type.value} on route {request.route_key}")

            return request

        except Exception as e:
            logger.error(f"Error creating request: {str(e)}")
            raise

    async def get_request_by_id(self, request_id: str) -> Optional[Request]:
        """Get request by request_id"""
        logger.info(f"Looking up request by ID: {request_id}")
        try:
            response = self.requests_table.get_item(Key={'request_id': request_id})

            if 'Item' in response:
                logger.info(f"Found request {request_id}")
                return from_dynamodb_item(response['Item'], Request)
            logger.info(f"Request {request_id} not found")
            return None

        except Exception as e:
            logger.error(f"Error getting request by ID {request_id}: {str(e)}")
            raise

    async def get_requests_by_user(self, user_id: str) -> List[Request]:
        """Get all requests for a user"""
        logger.info(f"Getting all requests for user: {user_id}")
        try:
            response = self.requests_table.query(
                IndexName='UserIndex',
                KeyConditionExpression=Key('user_id').eq(user_id)
            )

            requests = [from_dynamodb_item(item, Request) for item in response['Items']]
            logger.info(f"Found {len(requests)} requests for user {user_id}")
            return requests

        except Exception as e:
            logger.error(f"Error getting requests for user {user_id}: {str(e)}")
            raise

    async def get_active_requests_by_route(self, route_key: str) -> List[Request]:
        """Get active requests for a specific route"""
        logger.info(f"Getting active requests for route: {route_key}")
        try:
            response = self.requests_table.query(
                IndexName='RouteIndex',
                KeyConditionExpression=Key('route_key').eq(route_key),
                FilterExpression=Attr('status').eq(RequestStatus.ACTIVE.value)
            )

            requests = [from_dynamodb_item(item, Request) for item in response['Items']]
            logger.info(f"Found {len(requests)} active requests for route {route_key}")
            return requests

        except Exception as e:
            logger.error(f"Error getting requests for route {route_key}: {str(e)}")
            raise

    async def get_requests_by_type(self, request_type: RequestType) -> List[Request]:
        """Get active requests by type (need_help or offer_help)"""
        try:
            response = self.requests_table.query(
                IndexName='StatusIndex',
                KeyConditionExpression=Key('status').eq(RequestStatus.ACTIVE.value),
                FilterExpression=Attr('type').eq(request_type.value)
            )

            return [from_dynamodb_item(item, Request) for item in response['Items']]

        except Exception as e:
            logger.error(f"Error getting requests by type {request_type}: {str(e)}")
            raise

    async def update_request_status(self, request_id: str, status: RequestStatus) -> bool:
        """Update request status"""
        try:
            from datetime import datetime

            self.requests_table.update_item(
                Key={'request_id': request_id},
                UpdateExpression='SET #status = :status, updated_at = :updated_at',
                ExpressionAttributeNames={'#status': 'status'},  # 'status' is a reserved word
                ExpressionAttributeValues={
                    ':status': status.value,
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            return True

        except Exception as e:
            logger.error(f"Error updating request status: {str(e)}")
            raise

    # Match operations
    async def create_match(self, need_request_id: str, offer_request_id: str,
                          compatibility_score: Optional[float] = None) -> Match:
        """Create a new match between need and offer requests"""
        logger.info(f"Creating match between need_request {need_request_id} and offer_request {offer_request_id}")
        try:
            match = Match(
                match_id="",  # Will be auto-generated
                need_request_id=need_request_id,
                offer_request_id=offer_request_id,
                compatibility_score=compatibility_score,
                created_at="",  # Will be auto-generated
                updated_at=""   # Will be auto-generated
            )

            # Convert to DynamoDB item
            item = to_dynamodb_item(match)
            logger.info(f"Generated match_id: {match.match_id} with compatibility score: {compatibility_score}")

            # Save to DynamoDB
            self.matches_table.put_item(Item=item)
            logger.info(f"Successfully created match {match.match_id}")

            return match

        except Exception as e:
            logger.error(f"Error creating match: {str(e)}")
            raise

    async def get_match_by_id(self, match_id: str) -> Optional[Match]:
        """Get match by match_id"""
        try:
            response = self.matches_table.get_item(Key={'match_id': match_id})

            if 'Item' in response:
                return from_dynamodb_item(response['Item'], Match)
            return None

        except Exception as e:
            logger.error(f"Error getting match by ID {match_id}: {str(e)}")
            raise

    async def get_matches_for_request(self, request_id: str, is_need_request: bool = True) -> List[Match]:
        """Get all matches for a specific request"""
        try:
            if is_need_request:
                index_name = 'NeedRequestIndex'
                key_condition = Key('need_request_id').eq(request_id)
            else:
                index_name = 'OfferRequestIndex'
                key_condition = Key('offer_request_id').eq(request_id)

            response = self.matches_table.query(
                IndexName=index_name,
                KeyConditionExpression=key_condition
            )

            return [from_dynamodb_item(item, Match) for item in response['Items']]

        except Exception as e:
            logger.error(f"Error getting matches for request {request_id}: {str(e)}")
            raise

    async def update_match_consent(self, match_id: str, both_consented: bool) -> bool:
        """Update match consent status"""
        try:
            from datetime import datetime

            self.matches_table.update_item(
                Key={'match_id': match_id},
                UpdateExpression='SET both_consented = :consent, updated_at = :updated_at',
                ExpressionAttributeValues={
                    ':consent': both_consented,
                    ':updated_at': datetime.utcnow().isoformat()
                }
            )
            return True

        except Exception as e:
            logger.error(f"Error updating match consent: {str(e)}")
            raise

    # Matching algorithm helper
    async def find_potential_matches(self, request: Request) -> List[Request]:
        """Find potential matches for a given request"""
        logger.info(f"Finding potential matches for {request.type.value} request {request.request_id} on route {request.route_key}")
        try:
            # Get the opposite type of requests on the same route
            target_type = RequestType.OFFER_HELP if request.type == RequestType.NEED_HELP else RequestType.NEED_HELP
            logger.info(f"Looking for {target_type.value} requests on route {request.route_key}")

            # First get by route
            potential_matches = await self.get_active_requests_by_route(request.route_key)

            # Filter by type and exclude the same user
            matches = []
            for potential in potential_matches:
                if (potential.type == target_type and
                    potential.user_id != request.user_id and
                    potential.status == RequestStatus.ACTIVE):
                    matches.append(potential)
                    logger.info(f"Found compatible match: {potential.request_id} from user {potential.user_id}")

            logger.info(f"Found {len(matches)} potential matches for request {request.request_id}")
            return matches

        except Exception as e:
            logger.error(f"Error finding potential matches: {str(e)}")
            raise

# Global database instance
db = DatabaseService()
