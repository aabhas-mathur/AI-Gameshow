import { io, Socket } from 'socket.io-client';

const SOCKET_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class SocketService {
  private socket: Socket | null = null;

  connect(token?: string) {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(SOCKET_URL, {
      auth: token ? { token } : undefined,
      withCredentials: true,
      transports: ['websocket', 'polling'],
    });

    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket?.id);
    });

    this.socket.on('disconnect', () => {
      console.log('Socket disconnected');
    });

    this.socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  getSocket(): Socket | null {
    return this.socket;
  }

  // Room events
  joinRoom(roomCode: string) {
    this.socket?.emit('join_room', { room_code: roomCode });
  }

  leaveRoom(roomCode: string) {
    this.socket?.emit('leave_room', { room_code: roomCode });
  }

  // Game events
  startGame(roomCode: string) {
    this.socket?.emit('start_game', { room_code: roomCode });
  }

  submitAnswer(roundId: string, roomCode: string, answer: string) {
    this.socket?.emit('submit_answer', {
      round_id: roundId,
      room_code: roomCode,
      answer,
    });
  }

  startVoting(roundId: string, roomCode: string) {
    this.socket?.emit('start_voting', {
      round_id: roundId,
      room_code: roomCode,
    });
  }

  submitVote(roundId: string, roomCode: string, answerId: string) {
    this.socket?.emit('submit_vote', {
      round_id: roundId,
      room_code: roomCode,
      answer_id: answerId,
    });
  }

  endRound(roundId: string, roomCode: string) {
    this.socket?.emit('end_round', {
      round_id: roundId,
      room_code: roomCode,
    });
  }

  nextRound(roomCode: string) {
    this.socket?.emit('next_round', { room_code: roomCode });
  }

  // Event listeners
  on(event: string, callback: (...args: any[]) => void) {
    this.socket?.on(event, callback);
  }

  off(event: string, callback?: (...args: any[]) => void) {
    this.socket?.off(event, callback);
  }
}

export const socketService = new SocketService();
export default socketService;