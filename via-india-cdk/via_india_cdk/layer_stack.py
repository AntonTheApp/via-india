from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_ssm as ssm,
    BundlingOptions,
)
from constructs import Construct

class LayerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda layer for FastAPI dependencies with automatic bundling
        self.fastapi_layer = _lambda.LayerVersion(
            self, "FastAPILayer",
            code=_lambda.Code.from_asset(
                "./via-india-lambda-layer",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output/python --platform linux_aarch64 --only-binary=:all:"
                    ],
                )
            ),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="FastAPI + Mangum dependencies for via-india (auto-bundled)",
        )

        # Store layer ARN in SSM Parameter Store for independent deployments
        ssm.StringParameter(
            self, "FastAPILayerArnParameter",
            parameter_name="/via-india/layer/fastapi-arn",
            string_value=self.fastapi_layer.layer_version_arn,
            description="FastAPI Lambda Layer ARN for Via India"
        )
