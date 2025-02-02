#!/bin/bash

# filepath: /workspaces/transcendence/app/generate_env.sh

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to generate a secret key
generate_secret_key() {
  python -c "import random, string; print(''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(50)))"
}

# Confirmation to override existing .env files
if [ -f ".env" ] || [ -f ".env.postgres" ] || ls .env.* 1> /dev/null 2>&1; then
  echo -e "${YELLOW}Existing .env files detected. Do you want to override them? (y/n)${NC}"
  read -r confirm
  if [ "$confirm" != "y" ]; then
    echo -e "${RED}Operation cancelled.${NC}"
    exit 1
  fi
fi

echo -e "${GREEN}Enter DEBUG value (True/False):${NC}"
read -r DEBUG

echo -e "${GREEN}Enter POSTGRES_USER:${NC}"
read -r POSTGRES_USER

echo -e "${GREEN}Enter POSTGRES_PASSWORD:${NC}"
read -r POSTGRES_PASSWORD

echo -e "${GREEN}Enter POSTGRES_DB:${NC}"
read -r POSTGRES_DB

echo -e "${GREEN}Enter CLIENT_ID:${NC}"
read -r CLIENT_ID

echo -e "${GREEN}Enter CLIENT_SECRET:${NC}"
read -r CLIENT_SECRET

echo -e "${GREEN}Enter Host:${NC}"
read -r HOST

echo -e "${GREEN}Enter JWT_SECRET:${NC}"
read -r JWT_SECRET

REDIRECT_URI="https://$HOST/oauth_callback/"
DATABASE_URL="postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@postgres_db:5432/$POSTGRES_DB"

services=("user_service" "stat_service" "game_service" "chat_service" "auth_service" "main_service" "frontend_service")

for service in "${services[@]}"; do
  SECRET_KEY=$(generate_secret_key)
  cat <<EOL > .env.$service
DEBUG=$DEBUG
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB
DATABASE_URL=$DATABASE_URL
CLIENT_ID=$CLIENT_ID
CLIENT_SECRET=$CLIENT_SECRET
REDIRECT_URI=$REDIRECT_URI
JWT_SECRET=$JWT_SECRET
SECRET_KEY=$SECRET_KEY
HOST=$HOST
EOL
  echo -e "${GREEN}.env.$service file generated successfully.${NC}"
done

cat <<EOL > .env
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB
EOL

echo -e "${GREEN}.env.postgres file generated successfully.${NC}"
