!/bin/bash
# ==============================================================================
# Production SSL Setup Script - Fully Automated
# ==============================================================================
# This script properly uses docker volumes and works on any fresh VM
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DOMAIN="${1:-arka.kenislabs.com}"
EMAIL="${2:-support@kenislabs.com}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Production SSL Certificate Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Domain: ${DOMAIN}${NC}"
echo -e "${YELLOW}Email: ${EMAIL}${NC}"
echo ""

# Ensure we're in the project directory
cd ~/arka-mcp-gateway

# Step 1: Make sure services are running
echo -e "${YELLOW}Step 1: Ensuring services are running...${NC}"
docker compose -f docker-compose.production.yml --env-file .env.azure.production up -d postgres backend worker frontend

echo ""
echo -e "${YELLOW}Waiting for services to be healthy (30s)...${NC}"
sleep 30

# Step 2: Test that the challenge endpoint works
echo ""
echo -e "${YELLOW}Step 2: Testing Let's Encrypt challenge endpoint...${NC}"
docker exec arka-frontend sh -c 'mkdir -p /var/www/certbot/.well-known/acme-challenge && echo "test" > /var/www/certbot/.well-known/acme-challenge/test'
CHALLENGE_TEST=$(curl -s http://localhost/.well-known/acme-challenge/test || echo "FAILED")

if [ "$CHALLENGE_TEST" != "test" ]; then
    echo -e "${RED}ERROR: Challenge endpoint not working!${NC}"
    echo "Response: $CHALLENGE_TEST"
    echo "Please check nginx configuration"
    exit 1
fi

echo -e "${GREEN}✓ Challenge endpoint working${NC}"

# Step 3: Generate certificate using certbot container with docker volumes
echo ""
echo -e "${YELLOW}Step 3: Generating SSL certificate...${NC}"
docker compose -f docker-compose.production.yml run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email ${EMAIL} \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    --non-interactive \
    -d ${DOMAIN}

CERTBOT_EXIT=$?

if [ $CERTBOT_EXIT -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ Certificate generation failed (exit code: ${CERTBOT_EXIT})${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "1. Verify DNS: nslookup ${DOMAIN}"
    echo "2. Test from outside: curl http://${DOMAIN}/.well-known/acme-challenge/test"
    echo "3. Check logs: docker logs arka-certbot"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Certificate obtained successfully!${NC}"

# Step 4: Update nginx to HTTPS configuration
echo ""
echo -e "${YELLOW}Step 4: Switching to HTTPS configuration...${NC}"

# Use the HTTPS config that's already in the container
docker exec arka-frontend sh -c 'cp /etc/nginx/conf.d/default-https.conf /etc/nginx/conf.d/default.conf'

# Test nginx config
if ! docker exec arka-frontend nginx -t; then
    echo -e "${RED}✗ Nginx configuration test failed${NC}"
    echo "Reverting to HTTP configuration..."
    docker exec arka-frontend sh -c 'cp /etc/nginx/conf.d/default-https.conf.bak /etc/nginx/conf.d/default.conf' 2>/dev/null || true
    docker exec arka-frontend nginx -s reload
    exit 1
fi

# Reload nginx
docker exec arka-frontend nginx -s reload

echo -e "${GREEN}✓ Nginx switched to HTTPS${NC}"

# Step 5: Start certbot renewal service
echo ""
echo -e "${YELLOW}Step 5: Starting certificate renewal service...${NC}"
docker compose -f docker-compose.production.yml up -d certbot

# Step 6: Test HTTPS
echo ""
echo -e "${YELLOW}Step 6: Testing HTTPS...${NC}"
sleep 3

HTTP_TEST=$(curl -s http://${DOMAIN}/health || echo "FAILED")
HTTPS_TEST=$(curl -sk https://${DOMAIN}/health || echo "FAILED")

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ SSL Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Your application is now available at:${NC}"
echo -e "${GREEN}https://${DOMAIN}${NC}"
echo ""
echo -e "${YELLOW}HTTP Test:${NC} $HTTP_TEST"
echo -e "${YELLOW}HTTPS Test:${NC} $HTTPS_TEST"
echo ""
echo -e "${YELLOW}Certificate will auto-renew every 12 hours via certbot service${NC}"
echo ""
echo -e "${YELLOW}To view certificate details:${NC}"
echo "docker compose -f docker-compose.production.yml exec certbot certbot certificates"