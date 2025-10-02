from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from app.config import settings
from app.api import auth, rooms, game
from app.websocket.events import sio
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Note: Database tables are managed by Alembic migrations
# Run "alembic upgrade head" to create/update tables

# Create FastAPI app
app = FastAPI(
    title="Real-Time Voting Game API",
    description="A multiplayer voting game with AI-generated questions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(game.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real-Time Voting Game API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Create Socket.IO ASGI app
socket_app = socketio.ASGIApp(
    sio,
    app,
    socketio_path="/socket.io"
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:socket_app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )