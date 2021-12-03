#!/bin/bash

git pull
poetry install || exit "$?"
python manage.py migrate || exit "$?"
python manage.py collectstatic --no-input || exit "$?"

npm install
sudo npm install -g parcel@latest || exit "$?"
parcel build bundles-src/index.js --dist-dir bundles --public-url="./" || exit "$."

sudo systemctl restart star-burger.service  || exit "$?"

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

