#!/bin/bash
# Initialize Render database - can be run as a one-off job or manually
# This script assumes DATABASE_URL is set in the environment

echo "Initializing Render database schema..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL not set"
    echo "This should be set automatically by Render when database is linked"
    exit 1
fi

# Run the Python initialization script
cd "$(dirname "$0")/.."
python3 scripts/init_database.py

