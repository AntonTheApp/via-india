import aws_cdk as core
import aws_cdk.assertions as assertions

from via_india_cdk.via_india_cdk_stack import ViaIndiaCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in via_india_cdk/via_india_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ViaIndiaCdkStack(app, "via-india-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
