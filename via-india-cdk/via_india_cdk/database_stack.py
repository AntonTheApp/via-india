from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    CfnOutput,
)
from constructs import Construct

class DatabaseStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Users table
        self.users_table = dynamodb.Table(
            self, "UsersTable",
            table_name="via-india-users",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,  # Keep data on stack deletion
            point_in_time_recovery=True,
            # stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # Add GSI for email lookups
        self.users_table.add_global_secondary_index(
            index_name="EmailIndex",
            partition_key=dynamodb.Attribute(
                name="email",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Requests table
        self.requests_table = dynamodb.Table(
            self, "RequestsTable",
            table_name="via-india-requests",
            partition_key=dynamodb.Attribute(
                name="request_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True,
            # stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # Add GSI for user lookups
        self.requests_table.add_global_secondary_index(
            index_name="UserIndex",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Add GSI for route-based matching
        self.requests_table.add_global_secondary_index(
            index_name="RouteIndex",
            partition_key=dynamodb.Attribute(
                name="route_key",  # Will be "origin-destination" format
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="departure_date",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Add GSI for status-based queries
        self.requests_table.add_global_secondary_index(
            index_name="StatusIndex",
            partition_key=dynamodb.Attribute(
                name="status",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Matches table
        self.matches_table = dynamodb.Table(
            self, "MatchesTable",
            table_name="via-india-matches",
            partition_key=dynamodb.Attribute(
                name="match_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
            point_in_time_recovery=True
        )

        # Add GSI for request-based lookups
        self.matches_table.add_global_secondary_index(
            index_name="NeedRequestIndex",
            partition_key=dynamodb.Attribute(
                name="need_request_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        self.matches_table.add_global_secondary_index(
            index_name="OfferRequestIndex",
            partition_key=dynamodb.Attribute(
                name="offer_request_id",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Export table names and ARNs for use in other stacks
        CfnOutput(
            self, "UsersTableName",
            value=self.users_table.table_name,
            export_name="ViaIndiaUsersTableName",
            description="Name of the Users DynamoDB table"
        )

        CfnOutput(
            self, "RequestsTableName",
            value=self.requests_table.table_name,
            export_name="ViaIndiaRequestsTableName",
            description="Name of the Requests DynamoDB table"
        )

        CfnOutput(
            self, "MatchesTableName",
            value=self.matches_table.table_name,
            export_name="ViaIndiaMatchesTableName",
            description="Name of the Matches DynamoDB table"
        )

        CfnOutput(
            self, "UsersTableArn",
            value=self.users_table.table_arn,
            export_name="ViaIndiaUsersTableArn",
            description="ARN of the Users DynamoDB table"
        )

        CfnOutput(
            self, "RequestsTableArn",
            value=self.requests_table.table_arn,
            export_name="ViaIndiaRequestsTableArn",
            description="ARN of the Requests DynamoDB table"
        )

        CfnOutput(
            self, "MatchesTableArn",
            value=self.matches_table.table_arn,
            export_name="ViaIndiaMatchesTableArn",
            description="ARN of the Matches DynamoDB table"
        )
