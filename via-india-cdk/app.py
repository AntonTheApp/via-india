#!/usr/bin/env python3
import os

import aws_cdk as cdk

from via_india_cdk.layer_stack import LayerStack
from via_india_cdk.via_india_cdk_stack import ViaIndiaCdkStack


app = cdk.App()

# Deploy the layer stack first
layer_stack = LayerStack(app, "ViaIndiaLayerStack",
    env=cdk.Environment(account='523182613347', region='us-west-2'),
)

# Deploy the main application stack (depends on layer stack)
app_stack = ViaIndiaCdkStack(app, "ViaIndiaCdkStack",
    env=cdk.Environment(account='523182613347', region='us-west-2'),
)

# Ensure the layer stack is deployed before the app stack
# app_stack.add_dependency(layer_stack)

app.synth()
