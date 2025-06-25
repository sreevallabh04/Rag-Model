#!/bin/bash
# Intelligent RAG Assistant - Digital Ocean Deployment
# Author: Sreevallabh kakarala
# Version: 2.0

echo "=============================================="
echo " RAG Assistant - Digital Ocean Deployment"
echo " Author: Sreevallabh kakarala"
echo "=============================================="

# Configuration
APP_NAME="rag-assistant"
REGION="nyc1"
SIZE="s-2vcpu-4gb"
IMAGE="docker-20-04"

echo ""
echo "[1/6] Checking Digital Ocean CLI..."
if ! command -v doctl &> /dev/null; then
    echo "ERROR: doctl not found. Please install Digital Ocean CLI first."
    echo "Download from: https://github.com/digitalocean/doctl"
    exit 1
fi

echo ""
echo "[2/6] Checking authentication..."
doctl auth list
if [ $? -ne 0 ]; then
    echo "ERROR: Not authenticated with Digital Ocean."
    echo "Run: doctl auth init"
    exit 1
fi

echo ""
echo "[3/6] Building and pushing Docker image..."
docker build -t $APP_NAME:latest .
docker tag $APP_NAME:latest registry.digitalocean.com/sreevallabh/$APP_NAME:latest

echo ""
echo "[4/6] Creating droplet..."
doctl compute droplet create $APP_NAME \
    --region $REGION \
    --size $SIZE \
    --image $IMAGE \
    --user-data-file - <<EOF
#!/bin/bash
apt-get update
apt-get install -y docker.io
systemctl start docker
systemctl enable docker

# Pull and run the container
docker run -d \\
  --name rag-assistant-container \\
  -p 80:8501 \\
  --restart unless-stopped \\
  registry.digitalocean.com/sreevallabh/$APP_NAME:latest
EOF

echo ""
echo "[5/6] Waiting for droplet to be ready..."
sleep 30

echo ""
echo "[6/6] Getting droplet information..."
IP=$(doctl compute droplet list --format Name,PublicIPv4 --no-header | grep $APP_NAME | awk '{print $2}')

echo ""
echo "=============================================="
echo " 🚀 Deployment Complete!"
echo " 📊 Access at: http://$IP"
echo " 🌐 Public IP: $IP"
echo " 🔧 Manage: doctl compute droplet list"
echo "=============================================="
echo "" 