#!/bin/bash

set -e

echo "=================================================="
echo "Setting up development environment"
echo "=================================================="
echo ""

echo "Step 1: Cleaning up old containers and volumes..."
docker compose down -v 2>/dev/null || true
echo "✅ Old containers and volumes removed"
echo ""

echo "Step 2: Building and starting fresh containers..."
docker compose up -d --build
sleep 5
docker compose -f ./airflow/docker-compose.yaml up -d
echo "✅ Containers started"
echo ""

echo "Step 3: Waiting for services to be healthy..."
sleep 5
docker compose ps
echo ""

echo "=================================================="
echo "✅ Setup complete!"
echo "=================================================="
echo ""
echo "Services running:"
echo "  - API: http://localhost:8000/docs"
echo "  - Streamlit: http://localhost:8501"
echo "  - pgAdmin: http://localhost:5051"
echo "  - Mongo Express: http://localhost:8081"
echo "  - Airflow: http://localhost:8080"
echo ""
echo "View logs: docker-compose logs -f api"