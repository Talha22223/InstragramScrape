# Render Deployment Guide

## Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub** (already completed)

2. **Create a new Web Service on Render**
   - Go to https://render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `https://github.com/Talha22223/InstragramScrape`

3. **Configure the service:**
   - **Name**: `instagram-scraper`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd backend && python app.py`
   - **Auto-Deploy**: `Yes`

4. **Set Environment Variables:**
   - `APIFY_API_KEY`: Your Apify API key
   - `PORT`: `10000` (Render will set this automatically)
   - `FLASK_ENV`: `production`
   - `NODE_VERSION`: `18`

## Option 2: Using Dockerfile

If you prefer Docker deployment:

1. In Render, select "Docker" as runtime
2. **Build Command**: Leave empty
3. **Start Command**: Leave empty (uses Dockerfile CMD)
4. Set the same environment variables as above

## Environment Variables Required:

- **APIFY_API_KEY**: Your Apify API token (get from https://apify.com/)
- **PORT**: 10000 (automatically set by Render)
- **FLASK_ENV**: production
- **CORS_ORIGINS**: * (or your specific domain)

## After Deployment:

1. Your app will be available at: `https://your-app-name.onrender.com`
2. API endpoints will be at: `https://your-app-name.onrender.com/api/`
3. Frontend will be served from the same domain

## Important Notes:

- The app combines both frontend and backend in a single service
- Free tier has limitations (apps sleep after 15 min of inactivity)
- First deployment may take 10-15 minutes
- Make sure to add your Apify API key in environment variables

## Troubleshooting:

1. **Build fails**: Check the build logs, ensure all dependencies are in requirements.txt
2. **App doesn't start**: Verify the start command and port configuration
3. **API calls fail**: Check CORS settings and API endpoints
4. **Frontend not loading**: Verify the build process completed successfully