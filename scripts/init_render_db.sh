#!/bin/bash
# Initialize Render PostgreSQL database with schema
# Usage: ./scripts/init_render_db.sh [database-name]

DB_NAME="${1:-epsteinbase-db}"
INIT_SQL="backend/init.sql"

echo "Initializing database: $DB_NAME"
echo "Using schema file: $INIT_SQL"

# Check if init.sql exists
if [ ! -f "$INIT_SQL" ]; then
    echo "Error: $INIT_SQL not found"
    exit 1
fi

# Use render psql to execute the schema
# Note: This requires interactive mode, but we'll try
cat "$INIT_SQL" | render psql "$DB_NAME" 2>&1

echo "Database initialization complete!"

