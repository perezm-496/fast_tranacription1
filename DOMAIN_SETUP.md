# Domain Setup Guide for tunel.healthailabs.com

This guide explains how to configure your FastAPI application to serve on `tunel.healthailabs.com` with SSL certificates.

## Prerequisites

1. **Domain DNS Configuration**: Ensure your domain `tunel.healthailabs.com` points to your server's IP address
2. **Server Access**: You need root/sudo access to your server
3. **Ports Available**: Ports 80 and 443 should be open on your server

## Configuration Overview

The application is configured to:
- Redirect HTTP (port 80) to HTTPS (port 443)
- Serve the FastAPI application through nginx proxy
- Use Let's Encrypt SSL certificates
- Handle static files efficiently

## Step-by-Step Setup

### 1. DNS Configuration

First, ensure your domain points to your server:

```bash
# Check if your domain resolves to your server IP
nslookup tunel.healthailabs.com
```

### 2. Generate SSL Certificates

#### Option A: Using Let's Encrypt (Recommended for Production)

```bash
# Make the script executable
chmod +x setup_letsencrypt.sh

# Edit the script to add your email address
# Replace "your-email@example.com" with your actual email

# Run the Let's Encrypt setup
./setup_letsencrypt.sh
```

#### Option B: Using Self-Signed Certificates (Development Only)

```bash
# Generate self-signed certificates
./generate_ssl.sh
```

### 3. Update Environment Variables

Make sure your `.env` file includes the correct domain:

```env
ROOT_PATH=/elise
MONGO_URI=mongodb://elise:elise_can_open_doors@mongo:27017/elise_db?authSource=elise_db
MONGO_DB_NAME=elise_db
```

### 4. Start the Application

#### Development Mode (HTTP only)
```bash
docker-compose up --build
```

#### Production Mode (HTTPS with nginx)
```bash
docker-compose -f docker-compose.https.yml up --build
```

### 5. Test the Setup

```bash
# Test HTTP to HTTPS redirect
curl -I http://tunel.healthailabs.com

# Test HTTPS connection
curl -I https://tunel.healthailabs.com

# Test API endpoints
curl https://tunel.healthailabs.com/elise/docs
```

## Nginx Configuration Details

The `nginx.conf` file is configured to:

1. **HTTP Server (Port 80)**:
   - Redirects all HTTP traffic to HTTPS
   - Server name: `tunel.healthailabs.com`

2. **HTTPS Server (Port 443)**:
   - Uses SSL certificates from Let's Encrypt
   - Proxies requests to the FastAPI container
   - Serves static files efficiently
   - Includes security headers

3. **Proxy Configuration**:
   - Forwards requests to `http://fastapi:8000` (Docker service)
   - Preserves original headers
   - Handles WebSocket connections

## SSL Certificate Management

### Automatic Renewal

Let's Encrypt certificates are automatically renewed via cron job:
```bash
# Check renewal status
sudo certbot certificates

# Test renewal process
sudo certbot renew --dry-run
```

### Manual Renewal

```bash
# Renew certificates manually
sudo certbot renew

# Reload nginx after renewal
sudo systemctl reload nginx
```

## Troubleshooting

### Common Issues

1. **SSL Certificate Not Found**:
   ```bash
   # Check certificate paths
   ls -la /etc/letsencrypt/live/tunel.healthailabs.com/
   
   # Verify nginx configuration
   sudo nginx -t
   ```

2. **Domain Not Resolving**:
   ```bash
   # Check DNS resolution
   dig tunel.healthailabs.com
   nslookup tunel.healthailabs.com
   ```

3. **Port Issues**:
   ```bash
   # Check if ports are open
   sudo netstat -tlnp | grep :80
   sudo netstat -tlnp | grep :443
   ```

4. **Docker Container Issues**:
   ```bash
   # Check container status
   docker-compose ps
   
   # View container logs
   docker-compose logs nginx
   docker-compose logs fastapi
   ```

### Debugging Commands

```bash
# Test nginx configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# View nginx error logs
sudo tail -f /var/log/nginx/error.log

# Test SSL certificate
openssl s_client -connect tunel.healthailabs.com:443 -servername tunel.healthailabs.com
```

## Security Considerations

1. **Firewall Configuration**:
   ```bash
   # Allow HTTP and HTTPS traffic
   sudo ufw allow 80
   sudo ufw allow 443
   ```

2. **SSL Security**:
   - Uses TLS 1.2 and 1.3 only
   - Implements secure cipher suites
   - Includes security headers

3. **Container Security**:
   - Containers run with limited privileges
   - Network isolation between services
   - No root access to containers

## Performance Optimization

1. **Static File Caching**:
   - Static files are cached for 1 year
   - Immutable cache headers for better performance

2. **SSL Session Caching**:
   - SSL sessions cached for 10 minutes
   - Reduces SSL handshake overhead

3. **Gzip Compression**:
   - Consider enabling gzip compression in nginx for better performance

## Monitoring

Set up monitoring for:
- SSL certificate expiration
- nginx error logs
- Application response times
- Server resource usage

## Backup Strategy

1. **SSL Certificates**:
   ```bash
   # Backup Let's Encrypt certificates
   sudo cp -r /etc/letsencrypt /backup/letsencrypt
   ```

2. **Nginx Configuration**:
   ```bash
   # Backup nginx configuration
   sudo cp /etc/nginx/sites-available/tunel.healthailabs.com /backup/nginx/
   ```

3. **Application Data**:
   - MongoDB data is persisted in Docker volumes
   - Regular backups of Docker volumes recommended 