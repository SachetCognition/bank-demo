FROM python:3.12-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Playwright system dependencies
RUN npx playwright install-deps chromium

WORKDIR /app

# Copy test files
COPY tests/ tests/

# Install Python test dependencies
RUN pip install --no-cache-dir -r tests/unit/requirements.txt && \
    pip install --no-cache-dir -r tests/integration/requirements.txt

# Install E2E test dependencies
RUN cd tests/e2e && npm install && npx playwright install chromium

# Create artifacts directory
RUN mkdir -p artifacts/screenshots artifacts/videos

# Default entrypoint runs all test suites
COPY run-tests-docker.sh /app/run-tests-docker.sh
RUN chmod +x /app/run-tests-docker.sh

ENTRYPOINT ["/app/run-tests-docker.sh"]
