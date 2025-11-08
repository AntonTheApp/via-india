from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)
from constructs import Construct

class ViaIndiaCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda via-india-lambda-layer for dependencies
        fastapi_layer = _lambda.LayerVersion(
            self, "FastAPILayer",
            code=_lambda.Code.from_asset("../via-india-lambda-layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="FastAPI + Mangum dependencies",
        )

        fastapi_lambda = _lambda.Function(
            self, "TravelCompanionLambda",
            architecture=_lambda.Architecture.ARM_64,
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="main.handler",
            code=_lambda.Code.from_asset("../via-india-lambda/app"),
            memory_size=512,
            timeout=Duration.seconds(30),
            layers=[fastapi_layer],
        )

        api = apigw.LambdaRestApi(
            self, "TravelCompanionAPI",
            handler=fastapi_lambda,
            proxy=True
        )
