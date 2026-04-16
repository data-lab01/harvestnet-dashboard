#!/bin/bash
echo "🌾 Starting HarvestNet..."

# Start backend (Docker)
cd ~/Documents/harvestnet-dashboard
docker-compose up -d backend postgres

# Start frontend (Python)
cd frontend
python3 -m http.server 5500 &

echo ""
echo "✅ HarvestNet is running!"
echo "📊 Dashboard: http://localhost:5500"
echo "📚 API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
wait
