import type { InvitePerson } from "./invite";

export interface ChatMessage {
  id: number;
  conversation_id: string;
  sender_id: string;
  client_token: string;
  body: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  status: "accepted" | "unmatched" | "pending" | "declined";
  can_message: boolean;
  rematch_requested_by: string | null;
  person: InvitePerson;
  opening_message: string | null;
  last_message: ChatMessage | null;
  unread_count: number;
  updated_at: string;
}

export interface DesignDocument {
  title: string;
  summary: string;
  problem: string;
  target_users: string;
  features: string[];
  discussion_notes: string;
  architecture: string;
  tech_stack: { component: string; technology: string; rationale: string }[];
  data_model: string[];
  api_contracts: string[];
  team_roles: { username: string; responsibility: string; learning_goal: string }[];
  milestones: { title: string; estimate: string; deliverables: string[] }[];
  testing: string[];
  deployment: string;
  risks: string[];
  open_questions: string[];
}

export interface ProjectIdea {
  id: string;
  conversation_id: string;
  generated_by: string;
  brief: string;
  content: DesignDocument;
  context_message_id: number | null;
  created_at: string;
  parent_idea_id: string | null;
}

export interface StudioTurn {
  id: number;
  idea_id: string;
  conversation_id: string;
  author: { id: string; username: string; full_name: string };
  mode: "ask" | "revise";
  prompt: string;
  answer: string;
  proposal: DesignDocument | null;
  change_summary: string[];
  saved_idea_id: string | null;
  created_at: string;
}
