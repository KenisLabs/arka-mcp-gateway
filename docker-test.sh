#!/bin/bash
set -e

echo "🐳 Arka MCP Gateway - Local Docker Test Script"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "❌ Error: .env.production file not found"
    exit 1
fi

echo "✅ .env.production file found"
echo ""

# Function to show menu
show_menu() {
    echo "What would you like to do?"
    echo ""
    echo "1) Build all Docker images"
    echo "2) Start all services"
    echo "3) Stop all services"
    echo "4) View logs (all services)"
    echo "5) View logs (specific service)"
    echo "6) Check service status"
    echo "7) Clean up (stop and remove containers)"
    echo "8) Full cleanup (including volumes - ⚠️  DATA LOSS)"
    echo "9) Rebuild and restart"
    echo "0) Exit"
    echo ""
}

# Function to build images
build_images() {
    echo "🔨 Building Docker images..."
    docker-compose build --no-cache
    echo "✅ Build complete!"
}

# Function to start services
start_services() {
    echo "🚀 Starting services..."
    docker-compose --env-file .env.production up -d
    echo ""
    echo "✅ Services started!"
    echo ""
    echo "📊 Service URLs:"
    echo "   Frontend:  http://localhost:3000"
    echo "   Backend:   http://localhost:8080"
    echo "   Worker:    http://localhost:8081"
    echo "   Database:  localhost:5433"
    echo ""
    sleep 3
    docker-compose ps
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping services..."
    docker-compose down
    echo "✅ Services stopped!"
}

# Function to view all logs
view_logs() {
    echo "📋 Viewing logs (press Ctrl+C to exit)..."
    docker-compose logs -f
}

# Function to view specific service logs
view_service_logs() {
    echo ""
    echo "Which service logs do you want to view?"
    echo "1) Backend"
    echo "2) Frontend"
    echo "3) Worker"
    echo "4) PostgreSQL"
    read -p "Enter choice: " service_choice
    
    case $service_choice in
        1) docker-compose logs -f backend ;;
        2) docker-compose logs -f frontend ;;
        3) docker-compose logs -f worker ;;
        4) docker-compose logs -f postgres ;;
        *) echo "Invalid choice" ;;
    esac
}

# Function to check status
check_status() {
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🏥 Health Checks:"
    echo ""
    
    # Check backend
    echo -n "Backend API:  "
    if curl -f -s http://localhost:8080/ > /dev/null; then
        echo "✅ Healthy"
    else
        echo "❌ Not responding"
    fi
    
    # Check frontend
    echo -n "Frontend:     "
    if curl -f -s http://localhost:3000/health > /dev/null; then
        echo "✅ Healthy"
    else
        echo "❌ Not responding"
    fi
    
    # Check database
    echo -n "Database:     "
    if docker exec arka-postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Not ready"
    fi
}

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up containers..."
    docker-compose down
    echo "✅ Cleanup complete!"
}

# Function to full cleanup
full_cleanup() {
    echo "⚠️  WARNING: This will delete all data including the database!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        echo "🧹 Performing full cleanup..."
        docker-compose down -v
        echo "✅ Full cleanup complete!"
    else
        echo "Cancelled."
    fi
}

# Function to rebuild and restart
rebuild_restart() {
    echo "🔄 Rebuilding and restarting..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose --env-file .env.production up -d
    echo "✅ Rebuild and restart complete!"
    sleep 3
    docker-compose ps
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (0-9): " choice
    echo ""
    
    case $choice in
        1) build_images ;;
        2) start_services ;;
        3) stop_services ;;
        4) view_logs ;;
        5) view_service_logs ;;
        6) check_status ;;
        7) cleanup ;;
        8) full_cleanup ;;
        9) rebuild_restart ;;
        0) echo "👋 Goodbye!"; exit 0 ;;
        *) echo "❌ Invalid choice. Please try again." ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read
    clear
done
