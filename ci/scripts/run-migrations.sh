#!/bin/bash
set -euo pipefail

# Database Migration Script
# Usage: ./run-migrations.sh [environment] [region]

ENVIRONMENT="${1:-production}"
REGION="${2:-us-east-1}"
MAX_RETRIES=3
RETRY_DELAY=10

echo "=========================================="
echo "Database Migration Script"
echo "=========================================="
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "=========================================="

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Database configuration
DB_HOST="${DB_HOST:-}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-premium_service}"
DB_USER="${DB_USER:-postgres}"

if [ -z "${DB_HOST}" ]; then
  echo "Getting RDS endpoint..."
  DB_HOST=$(aws rds describe-db-instances \
    --db-instance-identifier "premium-service-${ENVIRONMENT}-db" \
    --region "${REGION}" \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text)
fi

echo "Database host: ${DB_HOST}"

# Set database URL
DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
export DATABASE_URL
export PYTHON_DB_HOST="${DB_HOST}"
export PYTHON_DB_PORT="${DB_PORT}"
export PYTHON_DB_NAME="${DB_NAME}"
export PYTHON_DB_USER="${DB_USER}"
export PYTHON_DB_PASSWORD="${DB_PASSWORD}"

# Install dependencies
echo "Installing dependencies..."
pip install alembic psycopg2-binary sqlalchemy aws-secretsmanager python-dotenv --quiet

# Change to backend directory
cd backend

# Run migration with retries
echo "Running database migrations..."
RETRY_COUNT=0
MIGRATION_SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  echo "Migration attempt $((RETRY_COUNT + 1)) of ${MAX_RETRIES}..."

  # Get current migration version
  echo "Current database schema version:"
  alembic current || true

  # Show pending migrations
  echo "Pending migrations:"
  alembic history --verbose 2>/dev/null || true

  # Run migrations
  if alembic upgrade head; then
    MIGRATION_SUCCESS=true
    echo "Migrations applied successfully!"
    break
  else
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
      echo "Migration failed. Retrying in ${RETRY_DELAY} seconds..."
      sleep $RETRY_DELAY
    fi
  fi
done

if [ "${MIGRATION_SUCCESS}" = false ]; then
  echo "=========================================="
  echo "❌ Migration failed after ${MAX_RETRIES} attempts"
  echo "=========================================="

  # Rollback on failure
  echo "Attempting rollback..."
  alembic downgrade -1 || echo "Rollback failed or not needed"

  exit 1
fi

# Verify migration success
echo "Verifying migration..."
FINAL_VERSION=$(alembic current 2>/dev/null | tr -d '[:space:]')
echo "Final schema version: ${FINAL_VERSION}"

# Run validation checks
echo "Running validation checks..."

# Check that core tables exist
python3 << 'EOF'
import os
import psycopg2

conn = psycopg2.connect(
    host=os.environ['PYTHON_DB_HOST'],
    port=os.environ['PYTHON_DB_PORT'],
    dbname=os.environ['PYTHON_DB_NAME'],
    user=os.environ['PYTHON_DB_USER'],
    password=os.environ['PYTHON_DB_PASSWORD']
)
cursor = conn.cursor()

# Verify core tables
tables_to_check = ['users', 'services', 'providers', 'reviews']
for table in tables_to_check:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"✓ Table {table}: {count} rows")

conn.close()
print("All validation checks passed!")
EOF

# Display migration history
echo "Migration history:"
alembic history --verbose 2>/dev/null || true

echo "=========================================="
echo "✅ Database Migration Completed!"
echo "=========================================="
echo "Environment: ${ENVIRONMENT}"
echo "Final version: ${FINAL_VERSION}"
echo "=========================================="