import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for HTTPOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export interface AuthResponse {
  user: User;
  message: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface Room {
  id: string;
  code: string;
  host_id: string;
  max_players: number;
  total_rounds: number;
  current_round: number;
  status: 'waiting' | 'playing' | 'finished';
  created_at: string;
}

export interface RoomDetails extends Room {
  participants: User[];
  participant_count: number;
}

export interface CreateRoomData {
  max_players?: number;
  total_rounds?: number;
}

// Auth API
export const authAPI = {
  register: (data: RegisterData) =>
    api.post<AuthResponse>('/api/auth/register', data),

  login: (data: LoginData) =>
    api.post<AuthResponse>('/api/auth/login', data),

  logout: () =>
    api.post('/api/auth/logout'),

  me: () =>
    api.get<User>('/api/auth/me'),
};

// Room API
export const roomAPI = {
  create: (data: CreateRoomData) =>
    api.post<Room>('/api/rooms', data),

  join: (code: string) =>
    api.post<Room>('/api/rooms/join', { code }),

  get: (code: string) =>
    api.get<RoomDetails>(`/api/rooms/${code}`),

  leave: (code: string) =>
    api.delete(`/api/rooms/${code}/leave`),
};

// Game API
export const gameAPI = {
  start: (code: string) =>
    api.post(`/api/game/${code}/start`),

  submitAnswer: (roundId: string, answer: string) =>
    api.post(`/api/game/rounds/${roundId}/answer`, { content: answer }),

  getAnswers: (roundId: string) =>
    api.get(`/api/game/rounds/${roundId}/answers`),

  submitVote: (roundId: string, answerId: string) =>
    api.post(`/api/game/rounds/${roundId}/vote`, { answer_id: answerId }),

  getLeaderboard: (code: string) =>
    api.get(`/api/game/${code}/leaderboard`),
};