#!/bin/bash

# Enhanced OSINT System v2.0 - Coolify Deployment Script
# Automated deployment and configuration for Coolify

set -e

echo "🚀 Enhanced OSINT System v2.0 - Coolify Deployment"
echo "=================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Please copy .env.example to .env and configure your settings"
    exit 1
fi

# Load environment variables
source .env

echo "📋 Configuration:"
echo "   Environment: ${ENVIRONMENT:-production}"
echo "   Max Workers: ${MAX_WORKERS:-80}"
echo "   Batch Size: ${BATCH_SIZE:-5000}"
echo "   Log Level: ${LOG_LEVEL:-INFO}"
echo ""

# Validate required environment variables
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "❌ Missing required Supabase credentials!"
    echo "   Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env"
    exit 1
fi

echo "✅ Environment validation passed"
echo ""

# Build Docker image
echo "🏗️ Building Docker image for Coolify..."
docker build -t enhanced-osint-coolify:v2.0 .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"
echo ""

# Test local deployment
echo "🧪 Testing local deployment..."
docker-compose up -d

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Check container status
if docker-compose ps | grep -q "Up"; then
    echo "✅ Local deployment successful"
else
    echo "❌ Local deployment failed"
    docker-compose logs
    exit 1
fi

echo ""
echo "🚀 READY FOR COOLIFY DEPLOYMENT!"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo "   1. Push this repository to your Git provider"
echo "   2. Connect the repository to Coolify"
echo "   3. Set the following environment variables in Coolify:"
echo "      - SUPABASE_URL=${SUPABASE_URL}"
echo "      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}"
echo "      - MAX_WORKERS=${MAX_WORKERS:-80}"
echo "      - BATCH_SIZE=${BATCH_SIZE:-5000}"
echo "      - LOG_LEVEL=${LOG_LEVEL:-INFO}"
echo "   4. Deploy and monitor through Coolify dashboard"
echo ""
echo "🔍 Local Testing Commands:"
echo "   docker-compose logs -f enhanced-osint    # View logs"
echo "   docker-compose down                      # Stop services"
echo "   docker-compose up --build               # Rebuild and start"
echo ""
echo "📊 Performance Expectations:"
echo "   - 1,000 leads: ~30 minutes with 80 workers"
echo "   - 5,000 leads: ~6 hours with 80 workers"
echo "   - 10,000 leads: ~12 hours with 80 workers"
echo ""
echo "🎯 Your Enhanced OSINT System is ready for production!"
echo "   Built for scale. Optimized for Coolify. 🚀"
