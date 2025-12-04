#!/bin/bash

echo "🚀 Deploying Backend to Railway..."
echo ""

# Check if logged in
if ! railway whoami &>/dev/null; then
    echo "Please login to Railway..."
    railway login
fi

cd backend

# Initialize Railway project
echo ""
echo "Creating Railway project..."
railway init

# Link to GitHub repo
echo ""
echo "Deploying from GitHub..."
railway up

# Get the deployment URL
echo ""
echo "✅ Backend deployed!"
echo "Your backend URL will be shown above."
echo ""
echo "Next steps:"
echo "1. Copy your Railway backend URL"
echo "2. Run ./deploy-frontend.sh and provide the backend URL when prompted"
