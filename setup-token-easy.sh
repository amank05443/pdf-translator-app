#!/bin/bash

echo "========================================="
echo "   Easy Railway Token Setup"
echo "========================================="
echo ""
echo "OPTION 1: Type/Paste Token Directly"
echo "-------------------------------------"
echo ""
echo "After you copy your token, just paste it here:"
echo "(Right-click and select Paste, or press Cmd+V)"
echo ""
read -p "Token: " TOKEN

if [ ! -z "$TOKEN" ]; then
    export RAILWAY_TOKEN="$TOKEN"
    
    if railway whoami &>/dev/null; then
        echo ""
        echo "✅ Success! Token works!"
        echo ""
        
        # Save permanently
        echo "export RAILWAY_TOKEN='$TOKEN'" >> ~/.zshrc
        echo "✅ Token saved!"
        echo ""
        echo "Now run: ./deploy-backend.sh"
    else
        echo "❌ Token invalid. Please try again."
    fi
else
    echo ""
    echo "No token entered. Let's try another way..."
    echo ""
    echo "OPTION 2: Create a token file"
    echo "-------------------------------------"
    echo ""
    echo "1. Open TextEdit or any text editor"
    echo "2. Paste your token"
    echo "3. Save it as: railway-token.txt (in this folder)"
    echo "4. Run this script again"
    echo ""
    
    if [ -f "railway-token.txt" ]; then
        TOKEN=$(cat railway-token.txt)
        export RAILWAY_TOKEN="$TOKEN"
        
        if railway whoami &>/dev/null; then
            echo "✅ Token from file works!"
            echo "export RAILWAY_TOKEN='$TOKEN'" >> ~/.zshrc
            rm railway-token.txt
            echo "✅ Setup complete!"
        fi
    fi
fi
