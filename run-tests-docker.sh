#!/bin/bash
set -e

echo "=== Martian Bank Test Runner (Docker) ==="

mkdir -p artifacts/screenshots artifacts/videos

echo ""
echo "=== Running Unit Tests ==="
cd tests/unit
python -m pytest . -v --html=../../artifacts/unit-report.html --self-contained-html 2>&1 || true
cd ../..

echo ""
echo "=== Running Integration Tests ==="
cd tests/integration
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

echo "Done!"
