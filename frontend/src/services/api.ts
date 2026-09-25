import { SessionResponse, ChatResponse, HealthResponse, PersonalWishesState } from '../types';

const API_BASE = '/api';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    const message = errorBody.message || errorBody.detail || `Request failed with status ${res.status}`;
    throw new ApiError(res.status, message);
  }

  return res.json();
}

export const api = {
  async getSession(sessionId = 'default'): Promise<SessionResponse> {
    return request<SessionResponse>(`/session?session_id=${encodeURIComponent(sessionId)}`);
  },

  async sendMessage(message: string, sessionId = 'default'): Promise<ChatResponse> {
    return request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    });
  },

  async resetSession(sessionId = 'default'): Promise<SessionResponse> {
    return request<SessionResponse>(`/session/reset?session_id=${encodeURIComponent(sessionId)}`, {
      method: 'POST',
    });
  },

  async updateStateDirectly(state: PersonalWishesState, sessionId = 'default'): Promise<SessionResponse> {
    return request<SessionResponse>('/state/manual-edit', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, state }),
    });
  },

  async getHealth(): Promise<HealthResponse> {
    return request<HealthResponse>('/health');
  },
};
