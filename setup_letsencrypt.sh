#!/bin/bash

# Install certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Replace 'your-domain.com' with your actual domain
DOMAIN="your-domain.com"

# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain SSL certificate
sudo certbot certonly --standalone -d $DOMAIN --email your-email@example.com --agree-tos --non-interactive

# Update nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/$DOMAIN
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Set up automatic renewal
sudo crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "SSL certificate setup complete for $DOMAIN"
echo "Your site should now be accessible at https://$DOMAIN" 