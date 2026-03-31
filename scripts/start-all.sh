#!/bin/bash
# AI Employee - Quick Start Script
# Run this to start all services with PM2

set -e

echo "=============================================="
echo "  AI Employee - Silver Tier Quick Start"
echo "=============================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.13+"
    exit 1
fi
echo "✓ Python: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✓ Node.js: $(node --version)"

# Check PM2
if ! command -v pm2 &> /dev/null; then
    echo "⚠️  PM2 not found. Installing..."
    npm install -g pm2
fi
echo "✓ PM2: $(pm2 --version)"

echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting services with PM2..."
echo ""

# Start all services
pm2 start ecosystem.config.json

echo ""
echo "⏳ Waiting for services to start..."
sleep 3

echo ""
echo "📊 Service Status:"
echo ""
pm2 status

echo ""
echo "=============================================="
echo "  ✅ AI Employee Started Successfully!"
echo "=============================================="
echo ""
echo "📝 Useful commands:"
echo ""
echo "  View status:     pm2 status"
echo "  View logs:       pm2 logs"
echo "  Stop all:        pm2 stop all"
echo "  Restart all:     pm2 restart all"
echo ""
echo "📁 Logs location:  AI_Employee_Vault/Logs/"
echo ""
echo "🔧 To run on system startup:"
echo "  pm2 startup"
echo "  pm2 save"
echo ""
