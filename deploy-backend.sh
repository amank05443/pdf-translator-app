#!/bin/bash

echo "🚀 Deploying Backend to Railway..."
echo ""

# Check if RAILWAY_TOKEN is set
if [ -z "$RAILWAY_TOKEN" ]; then
    echo "Railway requires a token for authentication."
    echo ""
    echo "Please follow these steps:"
    echo "1. Go to https://railway.app/account/tokens"
    echo "2. Click 'Create Token'"
    echo "3. Copy the token"
    echo "4. Paste it below"
    echo ""
    read -sp "Enter your Railway token: " RAILWAY_TOKEN
    export RAILWAY_TOKEN
    echo ""
fi

cd backend

# Check if already logged in
if ! railway whoami &>/dev/null; then
    echo "Error: Token authentication failed."
    echo "Please verify your token and try again."
    exit 1
fi

# Initialize Railway project
echo ""
echo "Creating Railway project..."
railway init --name pdf-translator-backend

# Deploy
echo ""
echo "Deploying to Railway..."
railway up

# Get the domain
echo ""
echo "Getting deployment URL..."
RAILWAY_URL=$(railway domain)

if [ -z "$RAILWAY_URL" ]; then
    echo ""
    echo "⚠️  No custom domain found. Creating one..."
    railway domain
    RAILWAY_URL=$(railway domain)
fi

echo ""
echo "✅ Backend deployed!"
echo ""
echo "Backend URL: https://$RAILWAY_URL"
echo ""
echo "Save this URL! You'll need it for frontend deployment."
echo ""
echo "Next: Run ./deploy-frontend.sh"
