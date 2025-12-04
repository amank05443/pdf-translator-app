# Railway Token Setup Guide

The Railway CLI browser login has issues. Use token authentication instead:

## Step 1: Get Your Railway Token

1. Go to **https://railway.app/account/tokens**
2. Click **"Create Token"**
3. Give it a name like "CLI Deployment"
4. Click **"Create"**
5. **Copy the token** (you won't see it again!)

## Step 2: Use the Token

### Option A: Set it permanently (recommended)
```bash
echo 'export RAILWAY_TOKEN=your-token-here' >> ~/.zshrc
source ~/.zshrc
```

### Option B: Set it for this session only
```bash
export RAILWAY_TOKEN=your-token-here
```

## Step 3: Deploy

Now run:
```bash
./deploy-backend.sh
```

The script will use your token automatically!

## Verify It Works

Test your token:
```bash
railway whoami
```

Should show your Railway username.

## Security Note

Keep your token secret! Don't commit it to git or share it publicly.
