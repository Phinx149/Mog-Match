// Mirrors backend/app/services/invite_service.py. Keep field names in sync with the Flask JSON.

export type InviteStatus = "pending" | "accepted" | "declined";

/** Just enough of a profile to show who an invite is from/to. */
export interface InvitePerson {
  id: string;
  full_name: string;
  username: string;
  avatar_url: string | null;
}

export interface Invite {
  id: string;
  sender: InvitePerson;
  recipient: InvitePerson;
  message: string | null;
  status: InviteStatus;
  created_at: string;
  updated_at: string;
  team_mog: TeamMog | null;
}

export interface TeamMog {
  score: number;
  max_score: number;
  tier: string;
  members: (InvitePerson & { mog_score: number })[];
  breakdown: { key: string; label: string; points: number; max: number; reason: string }[];
}

/** GET /api/invites/inbox */
export interface InboxResponse {
  received: Invite[];
  sent: Invite[];
  /** Received invites still waiting for my answer (the nav badge). */
  pending_count: number;
}

export const MAX_INVITE_MESSAGE_LENGTH = 280;
