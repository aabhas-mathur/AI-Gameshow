# Voting Game - Frontend

A React TypeScript frontend for the real-time multiplayer voting game.

## Features

- **Authentication**: Login and registration with JWT cookies
- **Real-time Updates**: Socket.IO integration for live game events
- **Room Management**: Create and join game rooms
- **Game Play**:
  - Answer creative questions
  - Vote on other players' answers
  - Real-time leaderboard
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React** with TypeScript
- **React Router** for navigation
- **Axios** for HTTP requests
- **Socket.IO Client** for WebSocket communication
- **CSS3** for styling

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── GamePlay.tsx         # Game play component
│   ├── contexts/
│   │   └── AuthContext.tsx      # Authentication context
│   ├── pages/
│   │   ├── Login.tsx            # Login page
│   │   ├── Register.tsx         # Registration page
│   │   ├── Dashboard.tsx        # Main dashboard
│   │   └── Room.tsx             # Room/lobby page
│   ├── services/
│   │   ├── api.ts               # API service layer
│   │   └── socket.ts            # Socket.IO service
│   ├── App.tsx                  # Main app component
│   └── App.css                  # Global styles
├── public/
├── .env                         # Environment variables
└── package.json
```

## Setup and Installation

### Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

### Installation

1. **Navigate to frontend directory** (if not already there):
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment** (already created):
The `.env` file is already configured with:
```env
REACT_APP_API_URL=http://localhost:8000
```

4. **Start development server**:
```bash
npm start
```

The app will open at http://localhost:3000

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (irreversible)

## Usage Guide

### 1. Registration/Login

- Navigate to http://localhost:3000
- If not logged in, you'll be redirected to the login page
- Register a new account or login with existing credentials

### 2. Dashboard

After login, you'll see the dashboard with two options:

**Create a Room:**
- Set max players (2-10)
- Set total rounds (1-10)
- Click "Create Room"

**Join a Room:**
- Enter a 6-digit room code
- Click "Join Room"

### 3. Game Lobby

Once in a room:
- See all joined players
- Host can start the game when at least 2 players have joined
- Other players wait for host to start

### 4. Game Play

**Answer Phase:**
- Read the AI-generated question
- Type your creative answer
- Submit before time runs out

**Voting Phase:**
- See all players' answers (anonymized)
- Vote for your favorite (can't vote for your own)
- Real-time vote counts displayed

**Results Phase:**
- View leaderboard with current scores
- Host can start next round
- Continue until all rounds complete

## API Integration

### REST Endpoints Used

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/me` - Get current user
- `POST /api/rooms` - Create room
- `POST /api/rooms/join` - Join room
- `GET /api/rooms/:code` - Get room details
- `DELETE /api/rooms/:code/leave` - Leave room

### WebSocket Events

**Client → Server:**
- `join_room` - Join a room
- `start_game` - Start game (host only)
- `submit_answer` - Submit answer
- `start_voting` - Start voting phase (host only)
- `submit_vote` - Submit vote
- `end_round` - End current round (host only)
- `next_round` - Start next round (host only)

**Server → Client:**
- `player_joined` - Player joined room
- `player_left` - Player left room
- `game_started` - Game has started
- `round_started` - New round started
- `answer_submitted` - Answer count update
- `voting_started` - Voting phase started
- `vote_update` - Real-time vote count
- `round_ended` - Round ended with results
- `game_ended` - Game finished

## Key Components

### AuthContext
- Manages user authentication state
- Provides login, register, logout functions
- Automatically checks authentication on load
- Connects Socket.IO on login

### PrivateRoute
- Protects authenticated routes
- Redirects to login if not authenticated
- Shows loading spinner during auth check

### GamePlay Component
- Handles all game phases (answering, voting, results)
- Real-time updates via Socket.IO
- Host controls for game flow
- Timer display for time-limited phases

## Styling

- Modern gradient backgrounds
- Card-based UI components
- Responsive design with media queries
- Smooth transitions and hover effects
- Color-coded game states
- Leaderboard with podium styling (gold, silver, bronze)

## Environment Variables

- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

## Production Build

To create an optimized production build:

```bash
npm run build
```

This creates a `build/` directory with:
- Minified JavaScript
- Optimized CSS
- Compressed assets
- Ready to deploy to any static hosting

### Deployment Options

- **Netlify**: Drag and drop `build` folder
- **Vercel**: Connect GitHub repo and auto-deploy
- **GitHub Pages**: Use `gh-pages` package
- **AWS S3**: Upload `build` folder to S3 bucket
- **Any static host**: Serve the `build` directory

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ support required
- WebSocket support required

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to backend
**Solution:**
- Verify backend is running on http://localhost:8000
- Check CORS settings in backend allow http://localhost:3000
- Verify `.env` file has correct API URL

**Problem:** WebSocket not connecting
**Solution:**
- Ensure Socket.IO is working on backend
- Check browser console for connection errors
- Verify authentication cookie is set

### Compilation Errors

**Problem:** Module not found errors
**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Problem:** TypeScript errors
**Solution:**
- Check all imports are correct
- Ensure all components have proper type definitions

## Development Tips

1. **Hot Reload**: Changes auto-reload in browser
2. **Console Logs**: Check browser console for Socket.IO events
3. **Network Tab**: Monitor API requests in DevTools
4. **React DevTools**: Install for component inspection

## Known Issues

- None at this time

## Future Enhancements

- [ ] Add sound effects for game events
- [ ] Implement dark mode toggle
- [ ] Add player avatars
- [ ] Show typing indicators during answer phase
- [ ] Add chat functionality in lobby
- [ ] Implement game history/stats
- [ ] Add animations for transitions
- [ ] Progressive Web App (PWA) support

## Contributing

1. Follow existing code style
2. Use TypeScript for type safety
3. Add proper error handling
4. Test all features before committing
5. Keep components modular and reusable

## License

Part of the Vibe Coding Test for MachineHack.

---

**Built with ❤️ using React, TypeScript, and Socket.IO**