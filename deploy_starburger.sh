#!/bin/bash

set -e

git pull
poetry install
python manage.py migrate --no-input
python manage.py collectstatic --no-input

npm install
sudo npm install -g parcel@latest
parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

sudo systemctl restart star-burger.service

curl -X POST https://api.rollbar.com/api/1/deploy \
     -H "X-Rollbar-Access-Token: "$(awk -F'=' '/^ROLLBAR_ACCESS_TOKEN/ { print $2}' .env)"" \
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
