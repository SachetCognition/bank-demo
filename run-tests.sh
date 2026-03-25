#!/bin/bash
set -e

echo "=== Martian Bank Test Runner ==="
echo "Starting all services..."

# Create artifacts directory
mkdir -p artifacts/screenshots artifacts/videos

# Start services
docker-compose up -d --build 2>&1 || true

echo "Waiting for services to be ready..."
sleep 30

# Health checks
echo "Checking service health..."
for i in {1..30}; do
    if curl -s http://localhost:5000/ > /dev/null 2>&1; then
        echo "Dashboard is ready"
        break
    fi
    echo "Waiting for dashboard... ($i/30)"
    sleep 5
done

for i in {1..30}; do
    if curl -s http://localhost:8000/api/users > /dev/null 2>&1; then
        echo "Customer Auth is ready"
        break
    fi
    echo "Waiting for customer-auth... ($i/30)"
    sleep 5
done

echo ""
echo "=== Running Unit Tests ==="
cd tests/unit
pip install pytest pytest-html -q 2>/dev/null || true
python -m pytest . -v --html=../../artifacts/unit-report.html --self-contained-html 2>&1 || true
cd ../..

echo ""
echo "=== Running Integration Tests ==="
cd tests/integration
pip install pytest pytest-html requests -q 2>/dev/null || true
python -m pytest . -v --html=../../artifacts/integration-report.html --self-contained-html 2>&1 || true
cd ../..

echo ""
echo "=== Running E2E Tests ==="
cd tests/e2e
npx playwright test --reporter=html 2>&1 || true
cd ../..

echo ""
echo "=== Test Summary ==="
echo "Artifacts saved in artifacts/ directory:"
ls -la artifacts/ 2>/dev/null || echo "No artifacts directory found"
ls -la artifacts/screenshots/ 2>/dev/null || echo "No screenshots found"
ls -la artifacts/videos/ 2>/dev/null || echo "No videos found"

echo ""
echo "=== Tearing down services ==="
docker-compose down 2>&1 || true

echo "Done!"
