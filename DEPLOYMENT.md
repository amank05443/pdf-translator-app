# Deployment Guide - PDF Translator App

## Overview
This guide will help you deploy your PDF Translator app to production for free using:
- **Railway** - Backend (FastAPI with system dependencies)
- **Vercel** - Frontend (Next.js)

## Prerequisites
- GitHub account
- Railway account (sign up at railway.app)
- Vercel account (sign up at vercel.com)

## Step 1: Push to GitHub

1. Create a new repository on GitHub (https://github.com/new)
   - Name it: `pdf-translator-app`
   - Make it public or private
   - Don't initialize with README (we already have one)

2. Push your code to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/pdf-translator-app.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Deploy Backend to Railway

1. Go to https://railway.app and sign in with GitHub

2. Click "New Project" → "Deploy from GitHub repo"

3. Select your `pdf-translator-app` repository

4. Railway will detect the backend automatically

5. Configure environment variables:
   - Click on your service
   - Go to "Variables" tab
   - Add the following variable:
     ```
     ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
     ```
     (You'll update this after deploying the frontend)

6. Railway will automatically:
   - Install Python 3.9
   - Install system dependencies (tesseract, poppler, pango, etc.) using nixpacks.toml
   - Install Python packages from requirements.txt
   - Start the server using the Procfile

7. Wait for deployment to complete (2-5 minutes)

8. Copy your backend URL (it will look like: `https://your-app.railway.app`)

## Step 3: Deploy Frontend to Vercel

1. Go to https://vercel.com and sign in with GitHub

2. Click "Add New" → "Project"

3. Import your `pdf-translator-app` repository

4. Configure the project:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

5. Add environment variable:
   - Click "Environment Variables"
   - Add:
     ```
     Name: NEXT_PUBLIC_API_URL
     Value: https://your-backend.railway.app
     ```
     (Use the Railway URL from Step 2)

6. Click "Deploy"

7. Wait for deployment to complete (1-2 minutes)

8. Copy your frontend URL (it will look like: `https://your-app.vercel.app`)

## Step 4: Update Backend CORS

1. Go back to Railway

2. Update the `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```

3. Save and wait for Railway to redeploy (automatic)

## Step 5: Test Your App

1. Open your Vercel URL in a browser

2. Try uploading and translating a PDF

3. Share the URL with anyone - it works on mobile too!

## Troubleshooting

### Backend Issues

- **Check Railway logs**: Go to your Railway service → "Deployments" tab → Click latest deployment → "View Logs"
- **Common issues**:
  - System dependencies not installing: Check nixpacks.toml is present
  - Port binding error: Ensure Procfile uses `$PORT`

### Frontend Issues

- **Check Vercel logs**: Go to your project → "Deployments" tab → Click latest deployment → "View Function Logs"
- **Common issues**:
  - CORS errors: Ensure ALLOWED_ORIGINS in Railway matches your Vercel URL exactly
  - API not found: Verify NEXT_PUBLIC_API_URL is set correctly

### PDF Processing Issues

- **OCR not working**: Railway includes Tesseract automatically via nixpacks.toml
- **WeasyPrint errors**: System dependencies (pango, cairo) are in nixpacks.toml
- **Translation fails**: Check the backend logs for specific errors

## Costs

- **Railway**: Free tier includes 500 hours/month and $5 credit
- **Vercel**: Free tier includes unlimited deployments and 100GB bandwidth

Both free tiers are sufficient for personal use and testing!

## Updates

To update your app after making changes:

1. Commit and push changes to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```

2. Both Railway and Vercel will automatically redeploy!
