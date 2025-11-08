#!/usr/bin/env python3
import os

import aws_cdk as cdk

from via_india_cdk.layer_stack import LayerStack
from via_india_cdk.database_stack import DatabaseStack
from via_india_cdk.via_india_cdk_stack import ViaIndiaCdkStack


app = cdk.App()

# Deploy the database stack first
database_stack = DatabaseStack(app, "ViaIndiaDatabaseStack",
    env=cdk.Environment(account='523182613347', region='us-west-2'),
)

# Deploy the layer stack
layer_stack = LayerStack(app, "ViaIndiaLayerStack",
    env=cdk.Environment(account='523182613347', region='us-west-2'),
)

# Deploy the main application stack (depends on database and layer stacks)
app_stack = ViaIndiaCdkStack(app, "ViaIndiaCdkStack",
    env=cdk.Environment(account='523182613347', region='us-west-2'),
)

# Ensure proper deployment order
app_stack.add_dependency(database_stack)
# Uncomment when python dependencies change
# app_stack.add_dependency(layer_stack)

app.synth()
