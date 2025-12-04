#!/bin/bash

echo "🚀 Deploying Frontend to Vercel..."
echo ""

# Check if logged in
if ! vercel whoami &>/dev/null; then
    echo "Please login to Vercel..."
    vercel login
fi

cd frontend

# Prompt for backend URL
echo ""
read -p "Enter your Railway backend URL (e.g., https://your-app.railway.app): " BACKEND_URL

# Deploy to Vercel
echo ""
echo "Deploying to Vercel..."
vercel --prod -e NEXT_PUBLIC_API_URL="$BACKEND_URL"

echo ""
echo "✅ Frontend deployed!"
echo ""
echo "Final step:"
echo "1. Copy your Vercel URL from above"
echo "2. Go to Railway dashboard"
echo "3. Add environment variable: ALLOWED_ORIGINS=<your-vercel-url>"
