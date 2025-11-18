# Multi-stage build for optimized production image

# Stage 1: Build the React application
# Explicitly use AMD64 platform for Azure VM compatibility
FROM --platform=linux/amd64 node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install ALL dependencies (including devDependencies needed for build)
RUN npm ci

# Copy application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Serve with nginx
# Explicitly use AMD64 platform for Azure VM compatibility
FROM --platform=linux/amd64 nginx:alpine AS production

# Copy custom nginx configurations (both HTTP and HTTPS versions)
COPY nginx.conf /etc/nginx/conf.d/default.conf
# COPY nginx-https.conf /etc/nginx/conf.d/default-https.conf  # Uncomment when SSL certs are available

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create certbot webroot directory
RUN mkdir -p /var/www/certbot

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
