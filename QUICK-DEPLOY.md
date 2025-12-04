# Quick Deployment Guide

## ✅ What's Already Done:

1. ✅ Git repository initialized
2. ✅ Code pushed to GitHub: https://github.com/amank05443/pdf-translator-app
3. ✅ Deployment scripts created
4. ✅ Railway CLI installed
5. ✅ All configuration files ready

## 🚀 Deploy in 3 Commands:

### Option 1: Automated (Easiest)
```bash
./deploy.sh
```
This single script handles everything! Just follow the prompts.

### Option 2: Step by Step

#### Step 1: Deploy Backend
```bash
./deploy-backend.sh
```
- Will open browser for Railway login
- Creates and deploys your backend
- Copy the Railway URL it gives you

#### Step 2: Deploy Frontend
```bash
./deploy-frontend.sh
```
- Will open browser for Vercel login  
- Paste your Railway backend URL when prompted
- Copy the Vercel URL it gives you

#### Step 3: Configure CORS
Go to Railway dashboard and add:
```
ALLOWED_ORIGINS=<your-vercel-url>
```

## That's It!

Your app will be live at your Vercel URL and accessible worldwide on any device!

## Cost: $0/month

Both Railway and Vercel free tiers are more than enough for personal use.
