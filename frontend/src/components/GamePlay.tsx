import React, { useState, useEffect } from 'react';
import socketService from '../services/socket';
import { gameAPI } from '../services/api';
import './GamePlay.css';

interface GamePlayProps {
  roomCode: string;
  roundId: string;
  roundNumber: number;
  totalRounds: number;
  question: string;
  phase: 'answering' | 'voting' | 'results';
  isHost: boolean;
  onLeave: () => void;
}

interface Answer {
  id: string;
  content: string;
  vote_count?: number;
}

interface LeaderboardEntry {
  user_id: string;
  username: string;
  score: number;
}

const GamePlay: React.FC<GamePlayProps> = ({
  roomCode,
  roundId,
  roundNumber,
  totalRounds,
  question,
  phase: initialPhase,
  isHost,
  onLeave,
}) => {
  const [phase, setPhase] = useState(initialPhase);
  const [answer, setAnswer] = useState('');
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [selectedAnswerId, setSelectedAnswerId] = useState<string | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    setPhase(initialPhase);
    setAnswer('');
    setSelectedAnswerId(null);
    setIsProcessing(false); // Reset processing state when phase changes
    // Reset hasSubmitted when round changes OR when entering voting phase
    if (initialPhase === 'voting') {
      setHasSubmitted(false);
    }
  }, [roundId, initialPhase]);

  // Reset hasSubmitted and isProcessing when new round starts
  useEffect(() => {
    if (initialPhase === 'answering') {
      setHasSubmitted(false);
      setIsProcessing(false);
    }
  }, [roundId, initialPhase]);

  useEffect(() => {
    const socket = socketService.getSocket();
    if (!socket) return;

    socket.on('answer_submitted', (data: any) => {
      console.log('Answer submitted count:', data.submitted_count);
    });

    socket.on('voting_started', async (data: any) => {
      console.log('Voting started:', data);
      console.log('Resetting hasSubmitted to false for voting');
      setPhase('voting');
      setAnswers(data.answers || []);
      setTimeLeft(data.time_limit);
      setHasSubmitted(false); // Reset here as well
      setIsProcessing(false); // Reset processing state
    });

    socket.on('vote_update', (data: any) => {
      console.log('Vote update:', data);
      setAnswers((prev) =>
        prev.map((ans) =>
          ans.id === data.answer_id
            ? { ...ans, vote_count: data.vote_count }
            : ans
        )
      );
    });

    socket.on('round_ended', (data: any) => {
      console.log('Round ended:', data);
      setPhase('results');
      setLeaderboard(data.leaderboard || []);
      setIsProcessing(false); // Reset processing state
    });

    return () => {
      socket.off('answer_submitted');
      socket.off('voting_started');
      socket.off('vote_update');
      socket.off('round_ended');
    };
  }, []);

  useEffect(() => {
    if (timeLeft === null) return;

    if (timeLeft <= 0) {
      setTimeLeft(null);
      return;
    }

    const timer = setTimeout(() => {
      setTimeLeft(timeLeft - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [timeLeft]);

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      setError('Please enter an answer');
      return;
    }

    setError('');
    try {
      await gameAPI.submitAnswer(roundId, answer.trim());
      setHasSubmitted(true);
    } catch (err: any) {
      console.log('Submit error:', err.response?.data);
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        const errorMsg = detail.map((e: any) => e.msg).join(', ');
        console.log('Validation error:', errorMsg);
        setError(errorMsg);
      } else if (typeof detail === 'string') {
        console.log('String error:', detail);
        setError(detail);
      } else {
        console.log('Unknown error format:', detail);
        setError('Failed to submit answer');
      }
    }
  };

  const handleSubmitVote = async (answerId: string) => {
    console.log('Vote clicked! answerId:', answerId, 'hasSubmitted:', hasSubmitted);
    if (hasSubmitted) {
      console.log('Vote blocked - already submitted');
      return;
    }

    setError('');
    setSelectedAnswerId(answerId);
    try {
      await gameAPI.submitVote(roundId, answerId);
      setHasSubmitted(true);
      console.log('Vote submitted successfully');
    } catch (err: any) {
      console.log('Vote submission error:', err);
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map((e: any) => e.msg).join(', '));
      } else if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError('Failed to submit vote');
      }
      setSelectedAnswerId(null);
    }
  };

  const handleStartVoting = () => {
    if (isProcessing) return;
    setIsProcessing(true);
    socketService.startVoting(roundId, roomCode);

    // Failsafe: reset processing state after 5 seconds if no response
    setTimeout(() => {
      setIsProcessing(false);
    }, 5000);
  };

  const handleEndRound = () => {
    if (isProcessing) return;
    setIsProcessing(true);
    socketService.endRound(roundId, roomCode);
  };

  const handleNextRound = () => {
    if (isProcessing) return;
    setIsProcessing(true);
    socketService.nextRound(roomCode);
  };

  const handleEndGame = async () => {
    // Navigate to dashboard without calling onLeave to show scoreboard
    window.location.href = '/dashboard';
  };

  const isLastRound = roundNumber >= totalRounds;
  const showingFinalResults = phase === 'results' && isLastRound;

  return (
    <div className="gameplay-container">
      <div className="gameplay-header">
        <h2>{showingFinalResults ? 'Game Complete' : `Round ${roundNumber}`}</h2>
        {!showingFinalResults && (
          <button onClick={onLeave} className="btn btn-secondary btn-small">
            Leave
          </button>
        )}
      </div>

      {timeLeft !== null && (
        <div className="timer">Time Left: {timeLeft}s</div>
      )}

      <div className="question-section">
        <h3>Question:</h3>
        <p className="question">{question}</p>
      </div>

      {error && <div className="error-message">{error}</div>}

      {phase === 'answering' && (
        <div className="answering-phase">
          {!hasSubmitted ? (
            <>
              <textarea
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your creative answer here..."
                rows={4}
                maxLength={500}
              />
              <button
                onClick={handleSubmitAnswer}
                className="btn btn-primary"
              >
                Submit Answer
              </button>
            </>
          ) : (
            <div className="submitted-message">
              <p>Answer submitted! Waiting for other players...</p>
              {isHost && (
                <button
                  onClick={handleStartVoting}
                  className="btn btn-primary"
                  disabled={isProcessing}
                >
                  {isProcessing ? 'Starting...' : 'Start Voting'}
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {phase === 'voting' && (
        <div className="voting-phase">
          <h3>Vote for your favorite answer:</h3>
          <div className="answers-list">
            {answers.map((ans) => (
              <div
                key={ans.id}
                className={`answer-item ${
                  selectedAnswerId === ans.id ? 'selected' : ''
                } ${hasSubmitted ? 'disabled' : ''}`}
                onClick={() => !hasSubmitted && handleSubmitVote(ans.id)}
              >
                <p className="answer-content">{ans.content}</p>
                {ans.vote_count !== undefined && (
                  <span className="vote-count">{ans.vote_count} votes</span>
                )}
              </div>
            ))}
          </div>
          {hasSubmitted && <p className="hint">Vote submitted!</p>}
          {isHost && (
            <button
              onClick={handleEndRound}
              className="btn btn-primary"
              disabled={isProcessing}
            >
              {isProcessing ? 'Ending...' : 'End Round'}
            </button>
          )}
        </div>
      )}

      {phase === 'results' && (
        <div className="results-phase">
          {isLastRound ? (
            <>
              <h3>Final Results:</h3>
              <div className="final-leaderboard">
                {leaderboard.map((entry, index) => (
                  <div key={entry.user_id} className="leaderboard-item final">
                    <span className="rank">#{index + 1}</span>
                    <span className="username">{entry.username}</span>
                    <span className="score">{entry.score} points</span>
                  </div>
                ))}
              </div>
              <div className="game-over-message">
                <h2>🎉 Game Over! 🎉</h2>
                {leaderboard.length > 0 && (
                  <p className="winner-message">
                    Congratulations to {leaderboard[0].username}!
                  </p>
                )}
              </div>
              <button
                onClick={handleEndGame}
                className="btn btn-primary btn-large"
              >
                End Game
              </button>
            </>
          ) : (
            <>
              <h3>Leaderboard:</h3>
              <div className="leaderboard">
                {leaderboard.map((entry, index) => (
                  <div key={entry.user_id} className="leaderboard-item">
                    <span className="rank">#{index + 1}</span>
                    <span className="username">{entry.username}</span>
                    <span className="score">{entry.score} points</span>
                  </div>
                ))}
              </div>
              {isHost && (
                <button
                  onClick={handleNextRound}
                  className="btn btn-primary"
                  disabled={isProcessing}
                >
                  {isProcessing ? 'Starting...' : 'Next Round'}
                </button>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default GamePlay;