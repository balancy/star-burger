#!/bin/bash

set -e

echo "Fetching repo updates"
git pull

echo "Building frontend"
sudo docker build -t star-burger_frontend -f dockerfiles/Dockerfile.frontend .
sudo docker run --rm -v $(pwd)/bundles:/app/bundles star-burger_frontend

echo "Setting up backend"
sudo docker-compose -f docker-compose.prod.yml up -d
sudo docker exec -t django python manage.py migrate
sudo docker cp django:/app/staticfiles .

echo "Clearing unused docker items"
sudo docker system prune -f

curl -X POST https://api.rollbar.com/api/1/deploy \
     -H "X-Rollbar-Access-Token: "$(awk -F'=' '/^ROLLBAR_ACCESS_TOKEN/ { print $2}' .env.prod)"" \
     -H "Content-Type: application/json" \
     -d $'{
        "environment": "production",
        "revision": "'"$(git rev-parse HEAD)"'",
        "rollbar_username": "'"$(whoami)"'",
        "local_username": "'"$(git config user.name)"'",
        "comment": "deploy"
}' > /dev/null

echo
echo "Project deployed successfully"
