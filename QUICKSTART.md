# Quick Start Guide - Running Backend Only

This guide will help you run the backend server locally for testing and development.

## Option 1: Using Docker Compose (Easiest)

This method sets up everything automatically (PostgreSQL, Redis, Backend).

### Step 1: Install Docker
- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Make sure Docker is running

### Step 2: Create .env file
```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key (optional, fallback questions will be used if not provided):
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### Step 3: Start All Services
```bash
docker-compose up -d
```

### Step 4: Check if it's running
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Step 5: Stop Services
```bash
docker-compose down
```

---

## Option 2: Run Backend Locally (Manual Setup)

This method requires you to install PostgreSQL and Redis separately.

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 15+ installed and running
- Redis installed and running

### Step 1: Install Python Dependencies

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### On Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Install and Start PostgreSQL

#### On Windows:
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Install and remember the password you set for the `postgres` user
3. Open pgAdmin or command line and create a database:
```sql
CREATE DATABASE voting_game;
CREATE USER voting_user WITH PASSWORD 'voting_password';
GRANT ALL PRIVILEGES ON DATABASE voting_game TO voting_user;
```

#### On Mac (using Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15
createdb voting_game
```

#### On Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb voting_game
```

### Step 3: Install and Start Redis

#### On Windows:
1. Download Redis from https://github.com/microsoftarchive/redis/releases
2. Or use WSL2: `sudo apt install redis-server && sudo service redis-server start`

#### On Mac:
```bash
brew install redis
brew services start redis
```

#### On Linux:
```bash
sudo apt install redis-server
sudo systemctl start redis
```

### Step 4: Configure Environment

Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` with your database settings:
```env
DATABASE_URL=postgresql://voting_user:voting_password@localhost:5432/voting_game
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here-change-this
OPENAI_API_KEY=sk-your-api-key-here
ENVIRONMENT=development
DEBUG=True
```

### Step 5: Initialize Database

```bash
python scripts/init_db.py
```

Or using Alembic:
```bash
alembic upgrade head
```

### Step 6: Run the Server

```bash
python scripts/run.py
```

Or directly:
```bash
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload
```

### Step 7: Test the API

Open your browser and visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Option 3: Simplified Local Setup (SQLite for Testing)

If you don't want to install PostgreSQL, you can use SQLite for quick testing.

### Step 1: Modify config temporarily

Edit `app/config.py` and change the DATABASE_URL default:
```python
DATABASE_URL: str = "sqlite:///./voting_game.db"
```

### Step 2: Skip Redis (Optional)

Comment out Redis-related code in services if you're not using caching features.

### Step 3: Run
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python scripts/init_db.py
python scripts/run.py
```

---

## Testing the API

### Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Try the endpoints:

#### Register a User
```json
POST /api/auth/register
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "password123"
}
```

#### Create a Room
```json
POST /api/rooms
{
  "max_players": 8,
  "total_rounds": 5
}
```

### Using curl

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'
```

#### Login User
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email":"test@example.com","password":"password123"}'
```

#### Create Room (with authentication)
```bash
curl -X POST http://localhost:8000/api/rooms \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"max_players":8,"total_rounds":5}'
```

---

## Testing WebSocket Connection

### Using Python Client

Create a test file `test_socket.py`:

```python
import socketio

# Create client
sio = socketio.Client()

# Connect event
@sio.on('connect')
def on_connect():
    print('Connected to server!')

# Disconnect event
@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

# Player joined event
@sio.on('player_joined')
def on_player_joined(data):
    print(f'Player joined: {data}')

# Connect with auth token (get from login response)
sio.connect('http://localhost:8000',
            auth={'token': 'your-jwt-token-here'})

# Join a room
sio.emit('join_room', {'room_code': 'ABC123'})

# Keep connection alive
sio.wait()
```

Run it:
```bash
python test_socket.py
```

### Using Browser Console

```javascript
// Load Socket.IO client library first
const socket = io('http://localhost:8000', {
  auth: {
    token: 'your-jwt-token-here'
  }
});

socket.on('connect', () => {
  console.log('Connected!');
});

socket.emit('join_room', { room_code: 'ABC123' });

socket.on('player_joined', (data) => {
  console.log('Player joined:', data);
});
```

---

## Common Issues

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in scripts/run.py
```

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Or check service status
sudo systemctl status postgresql  # Linux
brew services list  # Mac
```

### Redis Connection Error
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Start Redis if not running
redis-server  # Direct start
# or
sudo systemctl start redis  # Linux
brew services start redis  # Mac
```

### Import Errors
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### OpenAI API Errors
- The backend will use fallback questions if OpenAI fails
- You can skip setting OPENAI_API_KEY for testing
- Check your API key has credits if you want AI features

---

## Stopping the Server

### Docker Compose
```bash
docker-compose down
```

### Local Server
Press `Ctrl+C` in the terminal where the server is running

### Background Services
```bash
# Stop PostgreSQL
sudo systemctl stop postgresql  # Linux
brew services stop postgresql  # Mac

# Stop Redis
sudo systemctl stop redis  # Linux
brew services stop redis  # Mac
```

---

## Next Steps

1. **Test the API** using the interactive docs at http://localhost:8000/docs
2. **Build a Frontend** to connect to this backend
3. **Deploy** to production using Render, Railway, or Heroku

## Need Help?

- Check server logs for errors
- Verify all services are running (PostgreSQL, Redis)
- Ensure .env file has correct values
- Check firewall/antivirus isn't blocking ports