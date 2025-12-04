#!/bin/bash

echo "========================================="
echo "   Railway Token Setup"
echo "========================================="
echo ""
echo "Instructions:"
echo "1. Go to: https://railway.app/account/tokens"
echo "2. Create a token"
echo "3. Copy it (Cmd+C)"
echo "4. Paste it below when prompted"
echo ""
echo "Tip: Right-click in terminal and select 'Paste'"
echo "     Or use Cmd+V"
echo ""
read -sp "Paste your Railway token here: " TOKEN
echo ""

if [ -z "$TOKEN" ]; then
    echo ""
    echo "❌ No token entered. Please try again."
    exit 1
fi

# Set for current session
export RAILWAY_TOKEN="$TOKEN"

# Verify it works
echo ""
echo "Verifying token..."
if railway whoami &>/dev/null; then
    echo "✅ Token is valid!"
    echo ""
    
    # Ask if they want to save permanently
    read -p "Save token permanently? (y/n): " SAVE
    if [ "$SAVE" = "y" ] || [ "$SAVE" = "Y" ]; then
        # Check which shell they use
        if [ -f "$HOME/.zshrc" ]; then
            echo "export RAILWAY_TOKEN='$TOKEN'" >> ~/.zshrc
            echo "✅ Token saved to ~/.zshrc"
        elif [ -f "$HOME/.bashrc" ]; then
            echo "export RAILWAY_TOKEN='$TOKEN'" >> ~/.bashrc
            echo "✅ Token saved to ~/.bashrc"
        fi
        echo ""
        echo "Reload your shell or run: source ~/.zshrc"
    else
        echo ""
        echo "Token set for this session only."
        echo "Run this script again next time you need it."
    fi
    
    echo ""
    echo "✅ Ready to deploy!"
    echo ""
    echo "Next step: Run ./deploy-backend.sh"
else
    echo "❌ Token verification failed."
    echo "Please check the token and try again."
    exit 1
fi
