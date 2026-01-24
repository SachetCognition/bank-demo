#!/bin/bash
# Script to generate self-signed SSL certificates for development

# Create the certs directory if it doesn't exist
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Generate private key
openssl genrsa -out server.key 2048

# Generate certificate signing request
openssl req -new -key server.key -out server.csr -subj "/C=US/ST=California/L=San Jose/O=MartianBank/OU=Development/CN=localhost"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

# Set appropriate permissions
chmod 600 server.key
chmod 644 server.crt

# Clean up CSR file
rm server.csr

echo "Self-signed certificates generated successfully!"
echo "  - server.key (private key)"
echo "  - server.crt (certificate)"
