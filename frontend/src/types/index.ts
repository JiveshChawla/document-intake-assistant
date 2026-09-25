export interface ExecutorInfo {
  name: string | null;
  relationship: string | null;
}

export interface GiftItem {
  item: string;
  recipient: string;
}

export interface PersonalWishesState {
  full_name: string | null;
  home_address: string | null;
  covers_worldwide_assets: boolean | null;
  has_children: boolean | null;
  children: string[] | null;
  executor: ExecutorInfo | null;
  specific_gifts: GiftItem[];
  additional_wishes: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  extracted_fields?: string[];
  ambiguities?: string[];
}

export interface SessionResponse {
  session_id: string;
  messages: ChatMessage[];
  state: PersonalWishesState;
  document_markdown: string;
  document_html: string;
  completion_percentage: number;
  missing_fields: string[];
  active_provider: string;
}

export interface ChatResponse {
  message: ChatMessage;
  state: PersonalWishesState;
  state_delta: Record<string, any>;
  ambiguities: string[];
  document_markdown: string;
  document_html: string;
  completion_percentage: number;
  missing_fields: string[];
  active_provider: string;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
  active_provider: string;
}
