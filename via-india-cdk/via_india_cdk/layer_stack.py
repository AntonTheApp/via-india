from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    CfnOutput,
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

        # Export the layer ARN so other stacks can import it
        CfnOutput(
            self, "FastAPILayerArn",
            value=self.fastapi_layer.layer_version_arn,
            export_name="ViaIndiaFastAPILayerArn",
            description="ARN of the FastAPI Lambda Layer"
        )
