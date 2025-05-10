#!/bin/bash
# Script to fix training issues and verify persistence

echo "=== Fixing Training Issues and Verifying Persistence ==="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or you don't have permission to use it."
    exit 1
fi

# Check if the container is running
CONTAINER_NAME=$(docker-compose ps -q vanna-app 2>/dev/null || docker compose ps -q vanna-app 2>/dev/null || echo "")
if [ -z "$CONTAINER_NAME" ]; then
    echo "Error: vanna-app container is not running. Start it with 'docker-compose up -d'."
    exit 1
fi

# Reset and train
echo -e "\n=== Resetting and Training ==="
docker exec $CONTAINER_NAME python app/train_all.py --reset --all

# Check documents
echo -e "\n=== Checking Documents ==="
docker exec $CONTAINER_NAME python app/utils/check_documents.py

# Restart the container to verify persistence
echo -e "\n=== Restarting Container to Verify Persistence ==="
docker restart $CONTAINER_NAME

# Wait for the container to start
echo "Waiting for container to start..."
sleep 10

# Check documents again
echo -e "\n=== Checking Documents After Restart ==="
docker exec $CONTAINER_NAME python app/utils/check_documents.py

echo -e "\n=== Process Complete ==="
echo "If you see the same documents before and after restart, persistence is working correctly!"
