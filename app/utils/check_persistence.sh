#!/bin/bash
# Script to check persistence after training

echo "=== Checking Persistence ==="

# Check if containers are running
echo "Checking if containers are running..."
if ! docker-compose -f docker-compose-fixed.yml ps | grep -q "Up"; then
    echo "Error: Containers are not running."
    exit 1
fi

# Run the debug script in the container
echo "Running debug script in container..."
docker-compose -f docker-compose-fixed.yml exec vanna-app python app/utils/debug_chromadb.py

# Check volume contents
echo "Checking volume contents..."
VOLUME_NAME="vanna-chromadb-data"
CONTAINER=$(docker-compose -f docker-compose-fixed.yml ps -q vanna-app)

echo "Volume contents in vanna-app container:"
docker exec "$CONTAINER" ls -la /app/data/chromadb

echo "Volume contents in chromadb container:"
CHROMADB_CONTAINER=$(docker-compose -f docker-compose-fixed.yml ps -q chromadb)
docker exec "$CHROMADB_CONTAINER" ls -la /chroma/chroma

echo "=== Persistence Check Complete ==="
