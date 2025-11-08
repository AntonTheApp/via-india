# -------- CONFIG --------
LAYER_DIR=via-india-lambda-layer
PYTHON_VER=3.12
ARCH=arm64

# -------- TASKS --------

.PHONY: build-layer deploy clean

build-layer:
	@echo "🚧 Building Lambda layer for Python $(PYTHON_VER)..."
	docker run --rm \
	  -v "$$(pwd)":/var/task \
	  -w /var/task \
	  public.ecr.aws/sam/build-python$(PYTHON_VER) \
	  pip install -r $(LAYER_DIR)/requirements.txt -t $(LAYER_DIR)/python
	#docker run --rm -v "$PWD":/var/task -w /var/task \
#	  public.ecr.aws/sam/build-python3.12 \
#  	  pip install -r via-india-lambda-layer/requirements.txt -t via-india-lambda-layer/python
	@echo "✅ Lambda layer built successfully!"


deploy: build-layer
	@echo "🚀 Deploying CDK stack..."
	cdk deploy

clean:
	@echo "🧹 Cleaning layer build output..."
	rm -rf $(LAYER_DIR)/python
