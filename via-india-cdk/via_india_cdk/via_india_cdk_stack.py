from aws_cdk import (
    Duration,
    Stack,
    Fn,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

class ViaIndiaCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import the FastAPI layer from the LayerStack
        layer_arn = Fn.import_value("ViaIndiaFastAPILayerArn")
        fastapi_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "ImportedFastAPILayer",
            layer_version_arn=layer_arn
        )

        # Import DynamoDB table references from DatabaseStack
        users_table_name = Fn.import_value("ViaIndiaUsersTableName")
        requests_table_name = Fn.import_value("ViaIndiaRequestsTableName")
        matches_table_name = Fn.import_value("ViaIndiaMatchesTableName")

        users_table_arn = Fn.import_value("ViaIndiaUsersTableArn")
        requests_table_arn = Fn.import_value("ViaIndiaRequestsTableArn")
        matches_table_arn = Fn.import_value("ViaIndiaMatchesTableArn")

        # Create Lambda function with DynamoDB environment variables
        fastapi_lambda = _lambda.Function(
            self, "TravelCompanionLambda",
            architecture=_lambda.Architecture.ARM_64,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="main.handler",
            code=_lambda.Code.from_asset("../via-india-lambda/app"),
            memory_size=512,
            timeout=Duration.seconds(30),
            layers=[fastapi_layer],
            environment={
                "USERS_TABLE_NAME": users_table_name,
                "REQUESTS_TABLE_NAME": requests_table_name,
                "MATCHES_TABLE_NAME": matches_table_name,
                "AWS_REGION": self.region,
            }
        )

        # Grant Lambda permissions to access DynamoDB tables
        # Import table objects to grant permissions
        users_table = dynamodb.Table.from_table_attributes(
            self, "ImportedUsersTable",
            table_arn=users_table_arn,
            grant_index_permissions=True,
        )
        requests_table = dynamodb.Table.from_table_attributes(
            self, "ImportedRequestsTable",
            table_arn=requests_table_arn,
            grant_index_permissions=True,
        )
        matches_table = dynamodb.Table.from_table_attributes(
            self, "ImportedMatchesTable",
            table_arn=matches_table_arn,
            grant_index_permissions=True,
        )

        # Grant read/write permissions
        users_table.grant_read_write_data(fastapi_lambda)
        requests_table.grant_read_write_data(fastapi_lambda)
        matches_table.grant_read_write_data(fastapi_lambda)

        api = apigw.LambdaRestApi(
            self, "TravelCompanionAPI",
            handler=fastapi_lambda,
            proxy=True
        )
