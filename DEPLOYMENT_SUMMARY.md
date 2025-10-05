# AI Gameshow - Deployment & Setup Summary

## Project Overview
A real-time multiplayer voting game with AI-generated questions, built with FastAPI backend and React frontend.

**Live URLs:**
- Frontend: https://ai-gameshow-tawny.vercel.app
- Backend: https://ai-gameshow.onrender.com
- Repository: https://github.com/aabhas-mathur/AI-Gameshow

---

## Architecture

### Backend (FastAPI + Python)
- **Hosting:** Render
- **Database:** PostgreSQL (Render)
- **Cache:** Redis (if needed)
- **Real-time:** Socket.IO for WebSockets
- **Authentication:** JWT tokens with HTTPOnly cookies

### Frontend (React + TypeScript)
- **Hosting:** Vercel
- **State Management:** React Context API
- **Real-time:** Socket.IO client
- **API Client:** Axios

---

## Issues Fixed & Solutions

### 1. **404 Error on `/api/auth/me`**
**Problem:** Frontend couldn't connect to backend API
**Solution:**
- Updated `REACT_APP_API_URL` in Vercel to `https://ai-gameshow.onrender.com`
- Backend was at different URL than expected

### 2. **Database Tables Not Created**
**Problem:** `relation "users" does not exist` error
**Solution:**
- Added `from app import models` to `app/main.py` to import models before `Base.metadata.create_all()`
- Models need to be imported for SQLAlchemy to register them

### 3. **Cross-Domain Cookie Issues (CORS)**
**Problem:** Cookies not working between Vercel (frontend) and Render (backend)
**Solution:**
- Updated backend `ALLOWED_ORIGINS` to include Vercel URL: `https://ai-gameshow-tawny.vercel.app`
- Changed cookie settings to `secure=True` and `samesite="none"` for cross-domain support

### 4. **WebSocket Authentication Failures**
**Problem:** WebSocket connections failing with "Connection attempt without token"
**Root Cause:** Cross-domain cookies unreliable for WebSocket connections
**Solution:**
- Modified backend to return `access_token` in response body (not just cookies)
- Updated frontend to pass token explicitly to WebSocket connection
- Changed `socketService.connect()` to `socketService.connect(response.data.access_token)`

### 5. **TypeScript Build Error**
**Problem:** `Property 'access_token' does not exist on type 'AuthResponse'`
**Solution:**
- Added `access_token: string` to `AuthResponse` interface in `frontend/src/services/api.ts`

---

## Environment Variables

### Backend (Render)
```
DATABASE_URL=<postgresql connection string from Render>
REDIS_URL=<redis connection string if using Redis>
SECRET_KEY=<secure random string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
OPENAI_API_KEY=<your OpenAI API key>
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://ai-gameshow-tawny.vercel.app
ENVIRONMENT=production
DEBUG=False
```

### Frontend (Vercel)
```
REACT_APP_API_URL=https://ai-gameshow.onrender.com
```

---

## Key Code Changes

### 1. Backend - Cookie Configuration (`app/api/auth.py`)
```python
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=True,          # Required for HTTPS
    samesite="none",      # Required for cross-domain
    max_age=60 * 60 * 24 * 7  # 7 days
)
```

### 2. Backend - Return Token in Response (`app/schemas/auth.py`)
```python
class AuthResponse(BaseModel):
    user: UserResponse
    message: str = "Authentication successful"
    access_token: str  # Added for cross-domain WebSocket auth
```

### 3. Backend - Import Models (`app/main.py`)
```python
from app import models  # Import models to register them with Base

# Create database tables
Base.metadata.create_all(bind=engine)
```

### 4. Frontend - Pass Token to WebSocket (`frontend/src/contexts/AuthContext.tsx`)
```typescript
const login = async (email: string, password: string) => {
    const response = await authAPI.login({ email, password });
    setUser(response.data.user);
    socketService.connect(response.data.access_token);  // Pass token
};

const register = async (email: string, username: string, password: string) => {
    const response = await authAPI.register({ email, username, password });
    setUser(response.data.user);
    socketService.connect(response.data.access_token);  // Pass token
};
```

### 5. Frontend - Update TypeScript Interface (`frontend/src/services/api.ts`)
```typescript
export interface AuthResponse {
    user: User;
    message: string;
    access_token: string;  // Added
}
```

---

## CI/CD Setup (GitHub Actions)

### Workflows Created

1. **Backend CI** (`.github/workflows/backend-ci.yml`)
   - Runs on push/PR with backend changes
   - Python 3.11, PostgreSQL, Redis
   - Linting with flake8
   - Tests with pytest
   - Coverage reports

2. **Frontend CI** (`.github/workflows/frontend-ci.yml`)
   - Runs on push/PR with frontend changes
   - Node.js 18
   - TypeScript type checking
   - Tests and build
   - Uploads build artifacts

3. **Deploy** (`.github/workflows/deploy.yml`)
   - Runs on push to main branch
   - Auto-deploys backend to Render
   - Auto-deploys frontend to Vercel

4. **PR Check** (`.github/workflows/pr-check.yml`)
   - Validates PR titles (semantic versioning)
   - Auto-labels PRs
   - Warns on large PRs (>50 files)

### Required GitHub Secrets
Add in GitHub Settings → Secrets and variables → Actions:

- `OPENAI_API_KEY` - Your OpenAI API key
- `RENDER_SERVICE_ID` - From Render dashboard URL
- `RENDER_API_KEY` - Create in Render Account Settings
- `VERCEL_DEPLOY_HOOK` - Create in Vercel project settings

---

## Database Setup

### Create PostgreSQL on Render
1. Go to https://dashboard.render.com
2. New → PostgreSQL
3. Name: `ai-gameshow-db`
4. Region: Same as backend
5. Instance Type: Free
6. Copy "Internal Database URL"
7. Add to backend env vars as `DATABASE_URL`

### Tables Created Automatically
The following tables are created on startup:
- `users` - User accounts
- `rooms` - Game rooms
- `room_participants` - Players in rooms
- `rounds` - Game rounds
- `answers` - Player answers
- `votes` - Player votes
- `scores` - Player scores

---

## Deployment Process

### Backend Deployment (Render)
1. Push code to GitHub
2. Render auto-deploys on push to main
3. Runs: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:socket_app --host 0.0.0.0 --port $PORT`
5. Tables created automatically via `Base.metadata.create_all()`

### Frontend Deployment (Vercel)
1. Push code to GitHub
2. Vercel auto-deploys on push to main
3. Build command: `npm run build`
4. Output directory: `build`
5. Environment variables must be set in Vercel dashboard

---

## Testing Locally

### Backend
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://user:password@localhost:5432/voting_game
export REDIS_URL=redis://localhost:6379
export SECRET_KEY=your-secret-key
export OPENAI_API_KEY=your-openai-key

# Run server
uvicorn app.main:socket_app --reload
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Run development server
npm start
```

---

## Current Status

✅ **Working:**
- User registration and login
- JWT authentication with cookies
- WebSocket real-time connections
- Room creation and joining
- Cross-domain authentication (Vercel ↔ Render)
- Database tables created automatically
- CI/CD pipelines configured

⚠️ **To Complete:**
- Add GitHub secrets for CI/CD
- Merge to main branch to trigger workflows
- Set up branch protection rules (optional)
- Configure Redis if needed for sessions

---

## Important Files Modified

**Backend:**
- `app/main.py` - Added model imports
- `app/api/auth.py` - Updated cookie settings, return token
- `app/schemas/auth.py` - Added access_token to response
- `app/config.py` - CORS origins configuration

**Frontend:**
- `frontend/.env` - API URL configuration
- `frontend/src/services/api.ts` - Updated AuthResponse interface
- `frontend/src/contexts/AuthContext.tsx` - Pass token to WebSocket

**CI/CD:**
- `.github/workflows/backend-ci.yml` - Backend testing
- `.github/workflows/frontend-ci.yml` - Frontend testing
- `.github/workflows/deploy.yml` - Auto deployment
- `.github/workflows/pr-check.yml` - PR validation

---

## Troubleshooting

### Issue: 401 Unauthorized on API calls
**Check:**
- Cookie settings (secure=true, samesite=none)
- CORS allowed origins includes frontend URL
- Token is being sent correctly

### Issue: WebSocket connection fails
**Check:**
- Token is passed to `socketService.connect(token)`
- Backend WebSocket accepts token in auth object
- CORS settings allow WebSocket connections

### Issue: Database errors
**Check:**
- DATABASE_URL is set correctly
- PostgreSQL is running
- Models are imported in main.py

### Issue: Deployment fails
**Check:**
- All environment variables are set
- GitHub secrets are configured
- Build commands are correct

---

## Next Steps

1. **Add GitHub Secrets** for CI/CD automation
2. **Merge to main branch** to deploy with CI/CD
3. **Test production deployment** end-to-end
4. **Set up monitoring** (optional)
5. **Add error tracking** like Sentry (optional)
6. **Configure custom domain** (optional)

---

## Support & Resources

- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **GitHub Actions:** https://docs.github.com/actions
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Socket.IO Docs:** https://socket.io/docs/v4

---

**Last Updated:** October 5, 2025
**Deployed By:** Aabhas Mathur
**Status:** Production Ready ✅
