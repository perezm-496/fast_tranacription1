#!/bin/bash

echo "=== Current Nginx Configuration Status ==="
echo

echo "1. Nginx service status:"
sudo systemctl status nginx --no-pager -l
echo

echo "2. Enabled nginx sites:"
if [ -d "/etc/nginx/sites-enabled" ]; then
    ls -la /etc/nginx/sites-enabled/
else
    echo "sites-enabled directory not found"
fi
echo

echo "3. Available nginx sites:"
if [ -d "/etc/nginx/sites-available" ]; then
    ls -la /etc/nginx/sites-available/
else
    echo "sites-available directory not found"
fi
echo

echo "4. Nginx configuration test:"
sudo nginx -t
echo

echo "5. Current nginx configuration:"
echo "--- Main nginx.conf ---"
sudo head -20 /etc/nginx/nginx.conf
echo

echo "6. Active server blocks:"
sudo nginx -T 2>/dev/null | grep -A 2 -B 2 "server_name" || echo "Could not retrieve server blocks"
echo

echo "7. Listening ports:"
sudo netstat -tlnp | grep nginx || echo "No nginx processes found listening"
echo

echo "=== End of Nginx Configuration Status ===" 