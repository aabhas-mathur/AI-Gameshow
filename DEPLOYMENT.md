# 🚀 Deployment Guide

This guide covers deploying the AI Gameshow application using free hosting services.

## Architecture Overview

- **Frontend**: Vercel (Free tier)
- **Backend**: Render.com (Free tier with WebSocket support)
- **Database**: Render PostgreSQL (Free tier) or Supabase

---

## Part 1: Deploy Backend to Render.com

### Prerequisites
- GitHub account
- Render.com account (sign up at https://render.com)

### Steps

1. **Push your code to GitHub** (already done)

2. **Create PostgreSQL Database FIRST**
   - Go to https://dashboard.render.com/
   - Click "New +" → "PostgreSQL"
   - Configure:
     ```
     Name: ai-gameshow-db
     Database: gameshow
     User: gameshow_user
     Region: Oregon (US West)
     PostgreSQL Version: 16
     Plan: Free
     ```
   - Click "Create Database"
   - **IMPORTANT**: Copy the "Internal Database URL" from the database page (you'll need this next)

3. **Create a new Web Service on Render**
   - Go to https://dashboard.render.com/
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `aabhas-mathur/AI-Gameshow`
   - Select the `gameshow_backend` branch

4. **Configure the Web Service**
   ```
   Name: ai-gameshow-backend
   Region: Oregon (US West) - MUST match database region
   Branch: gameshow_backend
   Root Directory: (leave empty)
   Runtime: Python 3
   Build Command: pip install --upgrade pip && pip install -r requirements.txt
   Start Command: uvicorn app.main:socket_app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

   **IMPORTANT**: Do NOT use `python3 -m` prefix in the start command!

5. **Add Environment Variables**
   In your Web Service settings → Environment tab, add these environment variables:
   ```
   DATABASE_URL=<Internal Database URL from PostgreSQL instance>
   SECRET_KEY=<generate-a-random-secret-key-here>
   OPENAI_API_KEY=<your-openai-api-key>
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
   ```

   To generate a SECRET_KEY:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note your backend URL: `https://ai-gameshow-backend.onrender.com`

7. **Run Database Migrations**
   - Once deployed, go to the Shell tab in your Render web service
   - Run:
   ```bash
   alembic upgrade head
   ```

---

## Part 2: Deploy Frontend to Vercel

### Prerequisites
- Vercel account (sign up at https://vercel.com)
- Vercel CLI installed (already done)

### Option A: Deploy via GitHub (Recommended)

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard
   - Click "Add New..." → "Project"

2. **Import GitHub Repository**
   - Select `aabhas-mathur/AI-Gameshow`
   - Click "Import"

3. **Configure Project**
   ```
   Framework Preset: Create React App
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: build
   Install Command: npm install
   ```

4. **Add Environment Variables**
   ```
   REACT_APP_API_URL=https://ai-gameshow-backend.onrender.com
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Note your frontend URL: `https://ai-gameshow.vercel.app`

### Option B: Deploy via CLI

1. **Login to Vercel**
   ```bash
   vercel login
   ```

2. **Deploy from frontend directory**
   ```bash
   cd "/mnt/d/testing/New folder/AI-Gameshow/AI-Gameshow/frontend"
   vercel --prod
   ```

3. **Set environment variables**
   ```bash
   vercel env add REACT_APP_API_URL production
   # Enter: https://ai-gameshow-backend.onrender.com
   ```

---

## Part 3: Update CORS Settings

After deploying, update the backend's CORS settings:

1. **In Render Dashboard**, update the `ALLOWED_ORIGINS` environment variable:
   ```
   ALLOWED_ORIGINS=https://your-actual-vercel-url.vercel.app,https://ai-gameshow.vercel.app
   ```

2. **Redeploy** the backend service for changes to take effect

---

## Part 4: Test Your Deployment

1. Visit your Vercel URL: `https://ai-gameshow.vercel.app`
2. Register a new account
3. Create a game room
4. Test the full game flow

---

## Troubleshooting

### Backend Issues

**Database Connection Errors**
- Verify `DATABASE_URL` in Render environment variables
- Ensure database migrations ran successfully
- Check Render logs for specific errors

**WebSocket Connection Failures**
- Render free tier may have cold start delays (~30 seconds)
- Check that CORS origins include your Vercel URL
- Verify backend is using `socket_app` not `app`

**OpenAI API Errors**
- Verify `OPENAI_API_KEY` is set correctly
- Ensure you have API credits available

### Frontend Issues

**API Connection Errors**
- Verify `REACT_APP_API_URL` points to correct Render URL
- Check browser console for CORS errors
- Ensure backend is running and healthy

**Build Failures**
- Check Vercel build logs
- Verify all dependencies are in `package.json`
- Try building locally first: `npm run build`

### Performance Notes

**Render Free Tier Limitations**
- Services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start)
- 750 hours/month of runtime
- Consider upgrading for production use

**Vercel Free Tier**
- 100GB bandwidth/month
- Unlimited deployments
- Automatic HTTPS and CDN

---

## Alternative Backend Hosting Options

If Render doesn't work for you, try these alternatives:

### Railway.app
- Free tier: $5 credit/month
- Better cold start performance
- Similar setup to Render

### Fly.io
- Free tier: 3 shared VMs
- Better for WebSocket apps
- Requires Docker knowledge

### Heroku
- No longer has a free tier
- $5/month minimum

---

## Cost Optimization

To minimize costs:

1. **Use Render free tier** for backend (~15min sleep on inactivity)
2. **Use Vercel free tier** for frontend
3. **Use Render PostgreSQL free tier** (1GB storage)
4. **Monitor OpenAI API usage** to control costs

**Total Monthly Cost: $0** (with free tiers)

---

## Production Recommendations

For production deployment:

1. **Upgrade Render backend** to Starter plan ($7/mo) for:
   - No sleep/cold starts
   - Better performance
   - More reliable WebSocket connections

2. **Use environment-specific configs**
   - Separate dev/staging/prod environments
   - Different API keys for each environment

3. **Set up monitoring**
   - Use Render's built-in monitoring
   - Set up error tracking (Sentry)
   - Monitor OpenAI API costs

4. **Enable custom domain**
   - Configure custom domain on Vercel
   - Set up SSL certificates
   - Update CORS settings

---

## Automated Deployments

Both Vercel and Render support automatic deployments:

- **Vercel**: Auto-deploys on push to `gameshow_backend` branch
- **Render**: Auto-deploys on push to `gameshow_backend` branch

To disable auto-deploy:
- **Vercel**: Project Settings → Git → Disable auto-deploy
- **Render**: Service Settings → Auto-Deploy → Disable

---

## Need Help?

- Vercel Documentation: https://vercel.com/docs
- Render Documentation: https://render.com/docs
- GitHub Issues: https://github.com/aabhas-mathur/AI-Gameshow/issues
