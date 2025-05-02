#!/bin/bash
# Script to restart containers with fixed volume configuration

echo "=== Restarting with Fixed Volume Configuration ==="

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Check if the volume exists
VOLUME_NAME="vanna-chromadb-data"
echo "Checking if volume $VOLUME_NAME exists..."
if docker volume inspect "$VOLUME_NAME" > /dev/null 2>&1; then
    echo "Volume $VOLUME_NAME exists. Keeping it."
else
    echo "Volume $VOLUME_NAME does not exist. Creating it..."
    docker volume create "$VOLUME_NAME"
fi

# Start containers with the fixed configuration
echo "Starting containers with fixed configuration..."
docker-compose -f docker-compose-fixed.yml up -d --build

# Wait for containers to start
echo "Waiting for containers to start..."
sleep 10

# Check container status
echo "Container status:"
docker-compose -f docker-compose-fixed.yml ps

# Check volume mounts
echo "Volume mounts:"
docker inspect -f '{{ .Mounts }}' $(docker-compose -f docker-compose-fixed.yml ps -q)

echo "=== Restart Complete ==="
echo "Access the application at http://localhost:8501"
echo "After training, run './check_persistence.sh' to verify persistence"
