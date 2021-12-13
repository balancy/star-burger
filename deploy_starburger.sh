#!/bin/bash

set -e

git pull
sudo docker build -t star-burger_frontend -f Dockerfile-frontend .
sudo docker run --rm -v $(pwd)/bundles:/app/bundles star-burger_frontend
sudo docker-compose build
sudo docker-compose -d up

curl -X POST https://api.rollbar.com/api/1/deploy \
     -H "X-Rollbar-Access-Token: "$(awk -F'=' '/^ROLLBAR_ACCESS_TOKEN/ { print $2}' .env.dev)"" \
     -H "Content-Type: application/json" \
     -d $'{
        "environment": "production",
        "revision": "'"$(git rev-parse HEAD)"'",
        "rollbar_username": "'"$(whoami)"'",
        "local_username": "'"$(git config user.name)"'",
        "comment": "deploy"
}'
echo
echo "Project deployed successfully"
