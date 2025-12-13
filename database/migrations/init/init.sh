#!/bin/bash
set -e

echo "Applying migrations..."
for f in /docker-entrypoint-initdb.d/migrations/*.sql; do 
    echo "Executing $f"
    psql -U $POSTGRES_USER -d $POSTGRES_DB -f "$f"
done
