#!/bin/bash
# setup.sh - Complete setup script for HarvestNet

echo "🚀 Setting up HarvestNet with password123..."

# Create .env file
cat > .env << EOF
DB_PASSWORD=password123
SECRET_KEY=harvestnet_super_secret_key_$(openssl rand -hex 16)
CORS_ORIGINS=http://localhost:3025
FRONTEND_PORT=3025
BACKEND_PORT=8000
EOF

echo "✅ Created .env file with password123"

# Create backend directory structure
mkdir -p backend/app/{api/routes,core,models,services}

# Create frontend directory structure  
mkdir -p frontend/src/{components/dashboard,pages,hooks,api}

echo "✅ Created directory structure"

# Build and start containers
docker-compose down -v  # Clean slate
docker-compose up --build -d

echo "✅ Containers starting..."

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Test database connection
echo "🔍 Testing database connection..."
docker-compose exec -T postgres pg_isready -U harvestnet -d harvestnet

if [ $? -eq 0 ]; then
    echo "✅ Database is ready with password123"
else
    echo "❌ Database connection failed"
fi

# Test backend
echo "🔍 Testing backend API..."
curl -s http://localhost:8000/docs > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend API is running on port 8000"
else
    echo "❌ Backend API not responding"
fi

# Test frontend
echo "🔍 Testing frontend..."
curl -s http://localhost:3025 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Frontend dashboard is running on port 3025"
else
    echo "❌ Frontend not responding"
fi

echo ""
echo "🎉 HarvestNet is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Dashboard:    http://localhost:3025"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "🗄️  Database:     postgresql://harvestnet:password123@localhost:5432/harvestnet"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo "To reset: docker-compose down -v && docker-compose up --build"