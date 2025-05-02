#!/bin/bash
# Script to check Docker volume persistence

echo "=== Docker Volume Debug Information ==="

# Check if Docker is running
echo "Checking if Docker is running..."
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or you don't have permission to use it."
    exit 1
fi

# List all Docker volumes
echo -e "\nListing all Docker volumes:"
docker volume ls

# Get volume name from docker-compose.yml
VOLUME_NAME=$(grep -A 1 "volumes:" docker-compose.yml | grep -v "volumes:" | awk '{print $1}' | tr -d ':')
echo -e "\nVolume name from docker-compose.yml: $VOLUME_NAME"

# Check if the volume exists
echo -e "\nChecking if volume exists..."
if docker volume inspect "$VOLUME_NAME" > /dev/null 2>&1; then
    echo "Volume $VOLUME_NAME exists."
    
    # Get volume information
    echo -e "\nVolume information:"
    docker volume inspect "$VOLUME_NAME"
    
    # Check volume mount points in containers
    echo -e "\nChecking volume mount points in containers:"
    docker ps -a --filter "volume=$VOLUME_NAME" --format "table {{.ID}}\t{{.Names}}\t{{.Mounts}}"
    
    # Check if containers are using the volume
    CONTAINERS=$(docker ps -a --filter "volume=$VOLUME_NAME" --format "{{.Names}}")
    if [ -z "$CONTAINERS" ]; then
        echo "No containers are using volume $VOLUME_NAME."
    else
        echo -e "\nContainers using volume $VOLUME_NAME:"
        echo "$CONTAINERS"
        
        # Check volume contents in the first container
        CONTAINER=$(echo "$CONTAINERS" | head -n 1)
        echo -e "\nChecking volume contents in container $CONTAINER:"
        
        # Get mount point from docker-compose.yml
        MOUNT_POINT=$(grep -A 2 "$VOLUME_NAME:" docker-compose.yml | grep -v "$VOLUME_NAME:" | head -n 1 | awk '{print $1}')
        echo "Mount point from docker-compose.yml: $MOUNT_POINT"
        
        # Check if the directory exists in the container
        echo -e "\nChecking if directory exists in container:"
        docker exec "$CONTAINER" ls -la "$MOUNT_POINT"
        
        # Check if there are any files in the directory
        echo -e "\nChecking files in directory:"
        docker exec "$CONTAINER" find "$MOUNT_POINT" -type f | sort
    fi
else
    echo "Volume $VOLUME_NAME does not exist."
fi

echo -e "\n=== Docker Volume Debug Complete ==="
