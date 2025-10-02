import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { roomAPI } from '../services/api';
import './Dashboard.css';

const Dashboard: React.FC = () => {
  const [roomCode, setRoomCode] = useState('');
  const [maxPlayers, setMaxPlayers] = useState(8);
  const [totalRounds, setTotalRounds] = useState(5);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleCreateRoom = async () => {
    setError('');
    setLoading(true);

    try {
      const response = await roomAPI.create({
        max_players: maxPlayers,
        total_rounds: totalRounds,
      });
      navigate(`/room/${response.data.code}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create room');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async () => {
    if (!roomCode.trim()) {
      setError('Please enter a room code');
      return;
    }

    setError('');
    setLoading(true);

    try {
      await roomAPI.join(roomCode.toUpperCase());
      navigate(`/room/${roomCode.toUpperCase()}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join room');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Voting Game</h1>
        <div className="user-info">
          <span>Welcome, {user?.username}!</span>
          <button onClick={handleLogout} className="btn btn-secondary">
            Logout
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="card">
          <h2>Create a New Room</h2>
          <div className="form-group">
            <label htmlFor="maxPlayers">Max Players (2-10)</label>
            <input
              type="number"
              id="maxPlayers"
              min="2"
              max="10"
              value={maxPlayers}
              onChange={(e) => setMaxPlayers(parseInt(e.target.value))}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="totalRounds">Total Rounds (1-10)</label>
            <input
              type="number"
              id="totalRounds"
              min="1"
              max="10"
              value={totalRounds}
              onChange={(e) => setTotalRounds(parseInt(e.target.value))}
              disabled={loading}
            />
          </div>

          <button
            onClick={handleCreateRoom}
            className="btn btn-primary btn-large"
            disabled={loading}
          >
            Create Room
          </button>
        </div>

        <div className="divider">OR</div>

        <div className="card">
          <h2>Join an Existing Room</h2>
          <div className="form-group">
            <label htmlFor="roomCode">Room Code</label>
            <input
              type="text"
              id="roomCode"
              value={roomCode}
              onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
              placeholder="Enter 6-digit room code"
              maxLength={6}
              disabled={loading}
            />
          </div>

          <button
            onClick={handleJoinRoom}
            className="btn btn-primary btn-large"
            disabled={loading}
          >
            Join Room
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
      </div>
    </div>
  );
};

export default Dashboard;