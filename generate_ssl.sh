#!/bin/bash

# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/private.key \
    -out ssl/certificate.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set permissions
chmod 600 ssl/private.key
chmod 644 ssl/certificate.crt

echo "Self-signed SSL certificate generated in ssl/ directory"
echo "For production, use Let's Encrypt or a proper CA certificate" 