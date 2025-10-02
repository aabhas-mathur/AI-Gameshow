# 🚀 Quick Deploy Guide (5 Minutes)

## ⚠️ Important Note
The automatic `render.yaml` deployment is experimental. **Manual deployment is recommended** for reliability.

---

## Step 1: Deploy Backend on Render (2 min)

### A. Create Database
1. Go to https://dashboard.render.com/
2. Click **"New +" → "PostgreSQL"**
3. Fill in:
   - Name: `ai-gameshow-db`
   - Region: **Oregon (US West)**
   - Plan: **Free**
4. Click **"Create Database"**
5. **Copy the "Internal Database URL"** (looks like `postgresql://...`)

### B. Create Web Service
1. Click **"New +" → "Web Service"**
2. Connect GitHub: `aabhas-mathur/AI-Gameshow`
3. Select branch: `gameshow_backend`
4. Fill in:
   - Name: `ai-gameshow-backend`
   - Region: **Oregon (US West)** (same as database!)
   - Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:socket_app --host 0.0.0.0 --port $PORT`
5. Click **"Advanced"** → Add Environment Variables:
   ```
   DATABASE_URL = <paste the Internal Database URL from step A5>
   OPENAI_API_KEY = <your OpenAI API key>
   SECRET_KEY = <generate random string or let Render auto-generate>
   ENVIRONMENT = production
   ALLOWED_ORIGINS = https://ai-gameshow.vercel.app
   ```
6. Click **"Create Web Service"**
7. Wait for deployment (~3-5 minutes)
8. **Copy your backend URL** (looks like `https://ai-gameshow-backend.onrender.com`)

### C. Run Database Migration
1. Once deployed, go to your web service page
2. Click **"Shell"** tab
3. Run: `alembic upgrade head`

---

## Step 2: Deploy Frontend on Vercel (2 min)

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Select `aabhas-mathur/AI-Gameshow`
4. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
5. Click **"Environment Variables"** → Add:
   ```
   REACT_APP_API_URL = <paste your backend URL from Step 1-B-8>
   ```
   (Example: `https://ai-gameshow-backend.onrender.com`)
6. Click **"Deploy"**
7. Wait for deployment (~2 minutes)
8. **Copy your frontend URL** (looks like `https://ai-gameshow-xyz.vercel.app`)

---

## Step 3: Update CORS (1 min)

1. Go back to Render → Your Web Service
2. Click **"Environment"** tab
3. Update `ALLOWED_ORIGINS` to your actual Vercel URL:
   ```
   ALLOWED_ORIGINS = https://ai-gameshow-xyz.vercel.app
   ```
4. Save → Service will auto-redeploy

---

## ✅ Test Your Deployment

1. Visit your Vercel URL
2. Register a new account
3. Create a game room
4. Invite friends or open in incognito mode
5. Play a round!

---

## 🐛 Common Issues

**Backend won't start:**
- Check Render logs for errors
- Verify DATABASE_URL is correct
- Ensure OPENAI_API_KEY is set

**Frontend can't connect:**
- Verify REACT_APP_API_URL in Vercel environment variables
- Check ALLOWED_ORIGINS matches your Vercel URL exactly
- Look at browser console for CORS errors

**WebSocket connection fails:**
- Render free tier has 30s cold start - wait and retry
- Check backend is using `socket_app` not `app`

**Database errors:**
- Make sure you ran `alembic upgrade head` in Shell
- Verify DATABASE_URL is the "Internal" URL, not "External"

---

## 💰 Cost: $0/month

Both services are 100% free with these limitations:
- **Render**: Sleeps after 15min inactivity (30s cold start)
- **Vercel**: 100GB bandwidth/month

For production without cold starts: Upgrade Render to $7/month.

---

## 🎉 You're Done!

Your AI Gameshow is now live and shareable!

Share your Vercel URL with friends and start playing!
