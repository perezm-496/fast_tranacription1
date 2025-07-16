#!/usr/bin/env python3
"""
Script to start FastAPI application with HTTPS support
"""

import uvicorn
import os
from pathlib import Path

def main():
    # SSL certificate paths
    ssl_keyfile = "ssl/private.key"
    ssl_certfile = "ssl/certificate.crt"
    
    # Check if SSL certificates exist
    if not Path(ssl_keyfile).exists() or not Path(ssl_certfile).exists():
        print("SSL certificates not found. Generating self-signed certificates...")
        os.system("./generate_ssl.sh")
    
    # Start the application with SSL
    uvicorn.run(
        "elise.main:app",
        host="0.0.0.0",
        port=8443,  # Standard HTTPS port
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        reload=True
    )

if __name__ == "__main__":
    main() 