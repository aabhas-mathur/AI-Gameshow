# Full Stack Voting Game - Complete Setup Guide

This guide will help you run both the backend and frontend together.

## Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   React App     │         │  FastAPI + WS   │         │   PostgreSQL    │
│  (Frontend)     │◄───────►│   (Backend)     │◄───────►│   + Redis       │
│  Port 3000      │         │   Port 8000     │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## Quick Start (Recommended)

### Option 1: Run Everything with Docker

**Backend (with Docker Compose):**
```bash
# From project root
docker-compose up -d

# Verify backend is running
curl http://localhost:8000/health
```

**Frontend (separate terminal):**
```bash
cd frontend
npm install
npm start
```

### Option 2: Run Backend Locally

**Terminal 1 - Backend:**
```bash
# Install and start PostgreSQL and Redis first
# Then from project root:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py
python scripts/run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```

## Access the Application

Once both are running:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Testing the Full Stack

### 1. Register Users

Open http://localhost:3000 and create 2-3 accounts:
- User 1: test1@example.com / testuser1 / password123
- User 2: test2@example.com / testuser2 / password123
- User 3: test3@example.com / testuser3 / password123

### 2. Create a Room

Login as User 1 and:
- Click "Create Room"
- Set max players to 8
- Set total rounds to 3
- Note the room code (e.g., ABC123)

### 3. Join the Room

In separate browser windows (or incognito):
- Login as User 2 and User 3
- Use "Join Room" with the room code
- See all players appear in the lobby

### 4. Play the Game

As User 1 (host):
- Click "Start Game"
- Answer the AI-generated question
- Wait for others to answer
- Click "Start Voting"
- Vote on answers
- Click "End Round"
- View leaderboard
- Click "Next Round"

## Development Workflow

### Backend Development

```bash
# Make changes to Python files
# Server auto-reloads with --reload flag

# Run tests
pytest

# Check logs
docker-compose logs -f backend  # if using Docker
# or check terminal output if running locally
```

### Frontend Development

```bash
# Make changes to React files
# Browser auto-reloads

# Check browser console for errors
# Use React DevTools for debugging
```

## Port Configuration

Default ports:
- Frontend: 3000
- Backend: 8000
- PostgreSQL: 5432
- Redis: 6379

To change frontend API URL:
```bash
# Edit frontend/.env
REACT_APP_API_URL=http://localhost:8000
```

To change backend port:
```bash
# Edit scripts/run.py or docker-compose.yml
# Update CORS origins in app/main.py
```

## Environment Files

### Backend `.env`
```env
DATABASE_URL=postgresql://voting_user:voting_password@localhost:5432/voting_game
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-openai-key-here
ENVIRONMENT=development
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend `.env`
```env
REACT_APP_API_URL=http://localhost:8000
```

## Common Issues and Solutions

### Issue: Frontend can't connect to backend
**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS in `app/main.py` includes http://localhost:3000
3. Clear browser cache and cookies
4. Check browser console for errors

### Issue: Socket.IO not connecting
**Solution:**
1. Open browser DevTools → Network → WS tab
2. Look for Socket.IO connection attempts
3. Verify authentication cookie is set
4. Check backend Socket.IO logs

### Issue: Database errors
**Solution:**
```bash
# Reset database
docker-compose down -v
docker-compose up -d

# Or if running locally
python scripts/init_db.py
```

### Issue: Frontend compilation errors
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## Production Deployment

### Backend Deployment (Render, Railway, etc.)
1. Push code to GitHub
2. Connect repository to hosting platform
3. Set environment variables
4. Add PostgreSQL and Redis instances
5. Run database migrations
6. Deploy

### Frontend Deployment (Netlify, Vercel, etc.)
1. Build the app: `npm run build`
2. Update API URL in environment variables
3. Deploy `build` directory
4. Configure redirects for SPA routing

### Environment Variables for Production

**Backend:**
```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-db-url>
REDIS_URL=<production-redis-url>
OPENAI_API_KEY=<your-key>
ALLOWED_ORIGINS=https://yourdomain.com
```

**Frontend:**
```env
REACT_APP_API_URL=https://api.yourdomain.com
```

## Project Structure

```
.
├── app/                      # Backend application
│   ├── api/                  # REST endpoints
│   ├── models/               # Database models
│   ├── services/             # Business logic
│   ├── websocket/            # Socket.IO handlers
│   └── main.py              # App entry point
├── frontend/                 # Frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── pages/           # Page components
│   │   ├── services/        # API & Socket services
│   │   └── App.tsx          # Main app
│   └── public/
├── docker-compose.yml        # Docker services
├── requirements.txt          # Python dependencies
└── README.md                # Backend documentation
```

## Monitoring and Debugging

### Backend Logs
```bash
# Docker
docker-compose logs -f backend

# Local
# Check terminal output
```

### Frontend Logs
- Browser Console (F12)
- React DevTools
- Network tab for API calls

### Database Access
```bash
# Docker
docker exec -it voting_game_db psql -U voting_user -d voting_game

# Local
psql -U voting_user -d voting_game
```

### Redis Access
```bash
# Docker
docker exec -it voting_game_redis redis-cli

# Local
redis-cli
```

## Testing Checklist

- [ ] Backend health endpoint responds
- [ ] User registration works
- [ ] User login works
- [ ] Room creation works
- [ ] Room joining works
- [ ] Socket.IO connects
- [ ] Players appear in lobby
- [ ] Game starts
- [ ] Questions display
- [ ] Answers submit
- [ ] Voting works
- [ ] Leaderboard updates
- [ ] Multiple rounds work
- [ ] Game ends properly

## Support

For issues:
1. Check this guide
2. Review backend README.md
3. Review frontend FRONTEND_README.md
4. Check browser console
5. Check server logs

## API Documentation

Full API documentation available at http://localhost:8000/docs when backend is running.

---

**Ready to play? Start both services and open http://localhost:3000!**