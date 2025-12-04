#!/bin/bash

echo "========================================"
echo "   PDF Translator - Easy Deployment"
echo "========================================"
echo ""
echo "This script will deploy your app to:"
echo "  - Backend: Railway (FREE)"
echo "  - Frontend: Vercel (FREE)"
echo ""
read -p "Press Enter to continue..."

# Step 1: Deploy Backend
echo ""
echo "STEP 1: Deploying Backend to Railway..."
echo "----------------------------------------"
./deploy-backend.sh

# Get backend URL
echo ""
read -p "Enter the Railway backend URL that was just deployed: " BACKEND_URL

# Step 2: Deploy Frontend  
echo ""
echo "STEP 2: Deploying Frontend to Vercel..."
echo "----------------------------------------"
cd frontend
if ! vercel whoami &>/dev/null; then
    vercel login
fi

vercel --prod -e NEXT_PUBLIC_API_URL="$BACKEND_URL"
cd ..

# Get frontend URL
echo ""
read -p "Enter the Vercel frontend URL that was just deployed: " FRONTEND_URL

# Step 3: Configure CORS
echo ""
echo "STEP 3: Configuring CORS..."
echo "----------------------------------------"
echo "Go to your Railway dashboard and add this environment variable:"
echo ""
echo "  Name: ALLOWED_ORIGINS"
echo "  Value: $FRONTEND_URL"
echo ""
echo "Or run this command:"
echo "  cd backend && railway variables set ALLOWED_ORIGINS=$FRONTEND_URL"
echo ""
echo "========================================"
echo "   🎉 Deployment Complete!"
echo "========================================"
echo ""
echo "Your app is live at: $FRONTEND_URL"
echo ""
echo "Share this URL with anyone - it works on all devices!"
