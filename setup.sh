#!/usr/bin/env bash
set -e

echo "Starting project setup..."

# Load environment variables if present
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# Defaults
DB_NAME=${POSTGRES_DB:-invoice_db}
DB_USER=${POSTGRES_USER:-invoice_user}
DB_PASSWORD=${POSTGRES_PASSWORD:-password123}

echo "1. Creating database if it does not exist..."
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
psql -U postgres -c "CREATE DATABASE $DB_NAME"

echo "2. Creating user if it does not exist..."
psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER'" | grep -q 1 || \
psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD'"

echo "3. Granting privileges..."
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER"
psql -U postgres -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER"

echo "4. Creating tables..."
psql -U postgres -d $DB_NAME -f db/init.sql

echo "Setup completed."
