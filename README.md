# Real-Time Voting Game - Backend API

A scalable Python backend for a real-time multiplayer voting game where users join rooms, answer AI-generated questions, and vote on each other's responses.

## 🎯 Features

- **Authentication**: Email/password with JWT tokens stored in HTTPOnly cookies
- **Real-time Communication**: Socket.IO for live game updates
- **AI-Powered**: OpenAI integration for creative question generation
- **Game Mechanics**:
  - Create/join rooms with unique codes
  - Multiple rounds per game
  - Anonymous answer submissions
  - Real-time voting
  - Live leaderboards
- **Scalable Architecture**: PostgreSQL + Redis + FastAPI + Socket.IO

## 🛠 Tech Stack

- **Framework**: FastAPI
- **WebSocket**: python-socketio
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis
- **Authentication**: JWT with HTTPOnly cookies
- **AI**: OpenAI API
- **Testing**: pytest
- **Migrations**: Alembic

## 📁 Project Structure

```
.
├── app/
│   ├── api/                  # REST API endpoints
│   │   ├── auth.py          # Authentication routes
│   │   ├── rooms.py         # Room management
│   │   └── game.py          # Game operations
│   ├── models/              # SQLAlchemy database models
│   │   ├── user.py
│   │   ├── room.py
│   │   ├── round.py
│   │   ├── answer.py
│   │   ├── vote.py
│   │   └── score.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── room.py
│   │   └── game.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── room_service.py
│   │   ├── game_service.py
│   │   └── ai_service.py
│   ├── websocket/           # Socket.IO handlers
│   │   └── events.py
│   ├── utils/               # Helper functions
│   │   ├── security.py      # JWT & password hashing
│   │   ├── logger.py
│   │   ├── exceptions.py
│   │   └── room_code.py
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── dependencies.py      # FastAPI dependencies
│   └── main.py              # Application entry point
├── tests/                   # Unit tests
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- OpenAI API Key

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
DATABASE_URL=postgresql://user:password@localhost:5432/voting_game
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

### 3. Database Setup

```bash
# Initialize database tables
python scripts/init_db.py

# Or use Alembic migrations
alembic upgrade head
```

### 4. Run the Server

```bash
# Using the run script
python scripts/run.py

# Or directly with uvicorn
uvicorn app.main:socket_app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/socket.io

## 🐳 Docker Setup

### Using Docker Compose (Recommended)

```bash
# Start all services (PostgreSQL, Redis, Backend)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Build Docker Image Only

```bash
docker build -t voting-game-backend .
docker run -p 8000:8000 --env-file .env voting-game-backend
```

## 📡 API Endpoints

### Authentication

```
POST /api/auth/register      # Register new user
POST /api/auth/login         # Login user
POST /api/auth/logout        # Logout user
GET  /api/auth/me            # Get current user
```

### Rooms

```
POST /api/rooms              # Create room
POST /api/rooms/join         # Join room by code
GET  /api/rooms/{code}       # Get room details
DELETE /api/rooms/{code}/leave  # Leave room
```

### Game

```
POST /api/game/{code}/start           # Start game (host only)
POST /api/game/rounds/{id}/answer     # Submit answer
GET  /api/game/rounds/{id}/answers    # Get all answers
POST /api/game/rounds/{id}/vote       # Submit vote
GET  /api/game/{code}/leaderboard     # Get leaderboard
```

## 🔌 WebSocket Events

### Client → Server

```javascript
// Connect with authentication
socket.connect({
  auth: { token: 'jwt-token-here' }
});

// Join room
socket.emit('join_room', { room_code: 'ABC123' });

// Start game (host only)
socket.emit('start_game', { room_code: 'ABC123' });

// Submit answer
socket.emit('submit_answer', {
  round_id: 'uuid',
  room_code: 'ABC123',
  answer: 'My creative answer'
});

// Start voting phase (host only)
socket.emit('start_voting', {
  round_id: 'uuid',
  room_code: 'ABC123'
});

// Submit vote
socket.emit('submit_vote', {
  round_id: 'uuid',
  room_code: 'ABC123',
  answer_id: 'uuid'
});

// End round (host only)
socket.emit('end_round', {
  round_id: 'uuid',
  room_code: 'ABC123'
});

// Start next round (host only)
socket.emit('next_round', { room_code: 'ABC123' });
```

### Server → Client

```javascript
// Player joined room
socket.on('player_joined', (data) => {
  // { user_id, participant_count }
});

// Game started
socket.on('game_started', (data) => {
  // { round_number, question, round_id, time_limit, status }
});

// Answer submitted (count only, not content)
socket.on('answer_submitted', (data) => {
  // { submitted_count }
});

// Voting started
socket.on('voting_started', (data) => {
  // { round_id, answers: [{id, content}], time_limit }
});

// Real-time vote update
socket.on('vote_update', (data) => {
  // { answer_id, vote_count }
});

// Round ended
socket.on('round_ended', (data) => {
  // { round_number, leaderboard }
});

// Game ended
socket.on('game_ended', (data) => {
  // { final_leaderboard }
});

// New round started
socket.on('round_started', (data) => {
  // { round_number, question, round_id, time_limit }
});
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth_service.py -v

# Using the test script
bash scripts/run_tests.sh
```

## 🗄 Database Schema

### Tables

- **users**: User accounts
- **rooms**: Game rooms
- **room_participants**: Users in rooms
- **rounds**: Game rounds
- **answers**: Player submissions
- **votes**: Vote tracking
- **scores**: Points per round/user

### Key Relationships

- User ↔ Rooms (many-to-many via room_participants)
- Room → Rounds (one-to-many)
- Round → Answers (one-to-many)
- Answer → Votes (one-to-many)
- User → Scores (one-to-many)

## 🔐 Security Features

- **Password Hashing**: bcrypt via passlib
- **JWT Tokens**: Stored in HTTPOnly cookies
- **CORS**: Configurable allowed origins
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: SQLAlchemy ORM
- **Authentication Required**: Most endpoints protected

## 📊 Game Flow

1. **User Registration/Login** → JWT token in HTTPOnly cookie
2. **Create/Join Room** → Host creates room, others join with code
3. **Lobby** → Players wait, see participant list
4. **Start Game** → Host initiates first round
5. **Question Phase** → AI-generated question displayed
6. **Answer Phase** → Players submit anonymous answers (60s)
7. **Voting Phase** → All answers shown, players vote (45s)
8. **Results** → Scores updated, leaderboard shown
9. **Next Round** → Repeat steps 5-8
10. **Game End** → Final leaderboard, game marked finished

## 🎮 Game Rules

- **No Self-Voting**: Players cannot vote for their own answers
- **One Answer Per Round**: Each player submits one answer
- **One Vote Per Round**: Each player votes once
- **Anonymous Answers**: During voting, answers are anonymized
- **Points System**: +1 point per vote received
- **Host Controls**: Only host can start game/rounds

## 🚀 Deployment

### Environment Variables for Production

```env
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-postgres-url>
REDIS_URL=<production-redis-url>
OPENAI_API_KEY=<your-api-key>
ALLOWED_ORIGINS=https://yourdomain.com
```

### Recommended Platforms

- **Render**: Easy PostgreSQL + Redis + Web Service
- **Railway**: Integrated database and hosting
- **Heroku**: Add PostgreSQL and Redis addons
- **AWS**: EC2 + RDS + ElastiCache
- **DigitalOcean**: App Platform with managed databases

### Deployment Steps

1. Set environment variables
2. Deploy PostgreSQL and Redis instances
3. Run database migrations: `alembic upgrade head`
4. Deploy backend application
5. Configure CORS origins for your frontend

## 📝 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Use consistent naming conventions
5. Handle errors properly with custom exceptions

## 📄 License

This project is part of the Vibe Coding Test for MachineHack.

## 🎯 Performance Considerations

- **Connection Pooling**: SQLAlchemy pool configured
- **Redis Caching**: Fast session/state retrieval
- **Async Operations**: FastAPI async endpoints
- **Database Indexes**: User email, room code indexed
- **Efficient Queries**: Join optimization in services

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -U user -d voting_game

# Verify DATABASE_URL in .env
```

### Redis Connection Issues
```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

### OpenAI API Errors
- Verify API key is valid
- Check account has credits
- Fallback questions used if AI fails

### WebSocket Connection Issues
- Ensure JWT token is valid
- Check CORS settings
- Verify Socket.IO client version compatibility

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at /docs
3. Check logs for detailed error messages

---

**Built with ❤️ using FastAPI, Socket.IO, PostgreSQL, and OpenAI**