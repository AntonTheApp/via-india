from aws_cdk import (
    Duration,
    Stack,
    Fn,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
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
