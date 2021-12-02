#!/bin/bash

git pull
poetry install
python manage.py migrate
python manage.py collectstatic --no-input

npm install
sudo npm install -g parcel@latest || exit "$?"
parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

sudo systemctl restart star-burger.service  || exit "$?"

echo "Project deployed successfully"

