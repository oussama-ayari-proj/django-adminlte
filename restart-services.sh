#!/bin/bash

# Restart Services for File Upload Fix
echo "🔄 Restarting services with updated file upload configurations..."

# Stop services
echo "📥 Stopping services..."
docker-compose down

# Rebuild and start services
echo "🔨 Rebuilding and starting services..."
docker-compose up --build -d

# Check status
echo "✅ Checking service status..."
docker-compose ps

echo "🎉 Services restarted! File upload limits have been updated:"
echo "   - Django: 100MB per file, 500MB total request"
echo "   - Nginx: 500MB client max body size"
echo "   - Gunicorn: Extended timeouts for large uploads"
echo ""
echo "Your application should now handle larger file uploads at:"
echo "   http://172.16.3.201:8000"
echo "   http://localhost:5085"
