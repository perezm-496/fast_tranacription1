#!/bin/bash

echo "Cleaning up old nginx configurations..."

# Stop nginx
sudo systemctl stop nginx

# Remove all existing site configurations
echo "Removing existing site configurations..."
sudo rm -f /etc/nginx/sites-enabled/*
sudo rm -f /etc/nginx/sites-available/*

# Copy our new configuration
echo "Installing new nginx configuration..."
sudo cp nginx.conf /etc/nginx/sites-available/tunel.healthailabs.com

# Create symbolic link
sudo ln -sf /etc/nginx/sites-available/tunel.healthailabs.com /etc/nginx/sites-enabled/

# Test nginx configuration
echo "Testing nginx configuration..."
if sudo nginx -t; then
    echo "Nginx configuration test passed!"
    
    # Start nginx
    echo "Starting nginx..."
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    echo "Nginx cleanup and setup completed successfully!"
    echo "Your site should now be accessible at https://tunel.healthailabs.com"
else
    echo "Nginx configuration test failed!"
    echo "Please check the configuration and try again."
    exit 1
fi

# Show current nginx status
echo "Current nginx status:"
sudo systemctl status nginx --no-pager -l

# Show enabled sites
echo "Enabled nginx sites:"
ls -la /etc/nginx/sites-enabled/ 