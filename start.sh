#!/bin/bash

# SAP AI Core LLM Proxy Startup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MODE="${1:-dev}"
CONFIG="${2:-config.json}"

echo "SAP AI Core LLM Proxy"
echo "====================="

case "$MODE" in
  dev)
    echo "Starting in DEVELOPMENT mode..."
    echo ""
    echo "This will start:"
    echo "  - Backend server on http://localhost:3001"
    echo "  - Frontend dev server on http://localhost:5173"
    echo ""
    echo "Open http://localhost:5173 in your browser"
    echo ""

    # Check if frontend dependencies are installed
    if [ ! -d "frontend/node_modules" ]; then
      echo "Installing frontend dependencies..."
      cd frontend && npm install && cd ..
    fi

    # Start backend in background
    echo "Starting backend..."
    python proxy_server.py --config "$CONFIG" &
    BACKEND_PID=$!

    # Give backend time to start
    sleep 2

    # Start frontend dev server
    echo "Starting frontend dev server..."
    cd frontend && npm run dev

    # Cleanup on exit
    kill $BACKEND_PID 2>/dev/null || true
    ;;

  prod|production)
    echo "Starting in PRODUCTION mode..."
    echo ""

    # Build frontend if needed
    if [ ! -f "static/index.html" ]; then
      echo "Building frontend..."
      cd frontend
      npm install
      npm run build
      cd ..
    fi

    echo "Starting server on http://localhost:3001"
    echo ""
    python proxy_server.py --config "$CONFIG"
    ;;

  build)
    echo "Building frontend only..."
    cd frontend
    npm install
    npm run build
    echo ""
    echo "Frontend built successfully to ./static/"
    ;;

  *)
    echo "Usage: $0 [dev|prod|build] [config.json]"
    echo ""
    echo "Modes:"
    echo "  dev   - Development mode (default): Runs backend + Vite dev server"
    echo "  prod  - Production mode: Builds frontend, runs single server"
    echo "  build - Build frontend only"
    exit 1
    ;;
esac
