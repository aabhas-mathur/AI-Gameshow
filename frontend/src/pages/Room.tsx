import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { roomAPI, RoomDetails } from '../services/api';
import socketService from '../services/socket';
import GamePlay from '../components/GamePlay';
import './Room.css';

interface GameState {
  status: 'waiting' | 'playing' | 'finished';
  roundId?: string;
  roundNumber?: number;
  question?: string;
  timeLimit?: number;
  phase?: 'answering' | 'voting' | 'results';
}

const Room: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [room, setRoom] = useState<RoomDetails | null>(null);
  const [gameState, setGameState] = useState<GameState>({ status: 'waiting' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!code) return;

    const loadRoom = async () => {
      try {
        const response = await roomAPI.get(code);
        setRoom(response.data);
        setGameState({ status: response.data.status });
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load room');
      } finally {
        setLoading(false);
      }
    };

    loadRoom();

    // Connect socket and join room
    const socket = socketService.connect();
    socketService.joinRoom(code);

    // Listen to socket events
    socket.on('player_joined', (data: any) => {
      console.log('Player joined:', data);
      // Update room state directly from socket data for instant update
      if (data.participants && data.participant_count !== undefined) {
        setRoom((prev) => prev ? {
          ...prev,
          participants: data.participants,
          participant_count: data.participant_count
        } : null);
      } else {
        // Fallback to reloading if data structure is different
        loadRoom();
      }
    });

    socket.on('player_left', (data: any) => {
      console.log('Player left:', data);
      // Update room state directly from socket data for instant update
      if (data.participants && data.participant_count !== undefined) {
        setRoom((prev) => prev ? {
          ...prev,
          participants: data.participants,
          participant_count: data.participant_count
        } : null);
      } else {
        // Fallback to reloading if data structure is different
        loadRoom();
      }
    });

    socket.on('game_started', (data: any) => {
      console.log('Game started:', data);
      setGameState({
        status: 'playing',
        roundId: data.round_id,
        roundNumber: data.round_number,
        question: data.question,
        timeLimit: data.time_limit,
        phase: 'answering',
      });
    });

    socket.on('round_started', (data: any) => {
      console.log('Round started:', data);
      setGameState({
        status: 'playing',
        roundId: data.round_id,
        roundNumber: data.round_number,
        question: data.question,
        timeLimit: data.time_limit,
        phase: 'answering',
      });
    });

    socket.on('voting_started', (data: any) => {
      console.log('Voting started:', data);
      setGameState((prev) => ({
        ...prev,
        phase: 'voting',
        timeLimit: data.time_limit,
      }));
    });

    socket.on('round_ended', (data: any) => {
      console.log('Round ended:', data);
      setGameState((prev) => ({
        ...prev,
        phase: 'results',
      }));
    });

    socket.on('game_ended', (data: any) => {
      console.log('Game ended:', data);
      // Don't change status - keep showing GamePlay with final scoreboard
      // setGameState({ status: 'finished' });
    });

    socket.on('error', (data: any) => {
      console.error('Socket error:', data);
      setError(data.message || 'An error occurred');
    });

    // Cleanup
    return () => {
      socket.off('player_joined');
      socket.off('player_left');
      socket.off('game_started');
      socket.off('round_started');
      socket.off('voting_started');
      socket.off('round_ended');
      socket.off('game_ended');
      socket.off('error');
    };
  }, [code]);

  const handleStartGame = () => {
    if (code) {
      socketService.startGame(code);
    }
  };

  const handleLeaveRoom = async () => {
    if (code) {
      try {
        socketService.leaveRoom(code);
        await roomAPI.leave(code);
        navigate('/dashboard');
      } catch (err: any) {
        console.error('Failed to leave room:', err);
        navigate('/dashboard');
      }
    }
  };

  if (loading) {
    return (
      <div className="room-container">
        <div className="loading">Loading room...</div>
      </div>
    );
  }

  if (error && !room) {
    return (
      <div className="room-container">
        <div className="error-message">{error}</div>
        <button onClick={() => navigate('/dashboard')} className="btn btn-secondary">
          Back to Dashboard
        </button>
      </div>
    );
  }

  const isHost = room?.host_id === user?.id;

  // Show game play if game is in progress
  if (gameState.status === 'playing' && gameState.roundId && code) {
    return (
      <GamePlay
        roomCode={code}
        roundId={gameState.roundId}
        roundNumber={gameState.roundNumber || 1}
        totalRounds={room?.total_rounds || 3}
        question={gameState.question || ''}
        phase={gameState.phase || 'answering'}
        isHost={isHost}
        onLeave={handleLeaveRoom}
      />
    );
  }

  // Show lobby
  return (
    <div className="room-container">
      <div className="room-header">
        <h1>Room: {code}</h1>
        <button onClick={handleLeaveRoom} className="btn btn-secondary">
          Leave Room
        </button>
      </div>

      <div className="room-info">
        <div className="info-item">
          <span className="label">Status:</span>
          <span className="value status-{gameState.status}">{gameState.status}</span>
        </div>
        <div className="info-item">
          <span className="label">Players:</span>
          <span className="value">
            {room?.participant_count || 0} / {room?.max_players || 0}
          </span>
        </div>
        <div className="info-item">
          <span className="label">Rounds:</span>
          <span className="value">{room?.total_rounds || 0}</span>
        </div>
      </div>

      <div className="participants-section">
        <h2>Players</h2>
        <div className="participants-list">
          {room?.participants.map((participant) => (
            <div key={participant.id} className="participant-item">
              <span className="participant-name">{participant.username}</span>
              {participant.id === room.host_id && (
                <span className="host-badge">Host</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {isHost && gameState.status === 'waiting' && (
        <div className="host-controls">
          <button
            onClick={handleStartGame}
            className="btn btn-primary btn-large"
            disabled={(room?.participant_count || 0) < 2}
          >
            Start Game
          </button>
          {(room?.participant_count || 0) < 2 && (
            <p className="hint">Need at least 2 players to start</p>
          )}
        </div>
      )}

      {!isHost && gameState.status === 'waiting' && (
        <div className="waiting-message">
          <p>Waiting for host to start the game...</p>
        </div>
      )}

      {gameState.status === 'finished' && (
        <div className="game-finished">
          <h2>Game Finished!</h2>
          <button onClick={() => navigate('/dashboard')} className="btn btn-primary">
            Back to Dashboard
          </button>
        </div>
      )}
    </div>
  );
};

export default Room;