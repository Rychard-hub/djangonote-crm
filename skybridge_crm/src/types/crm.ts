// CRM tipai skirti Skybridge integracijai su Django API

export interface Lead {
  id: number;
  name: string;
  company?: string;
  email?: string;
  phone?: string;
  source?: string;
  status: LeadStatus;
  status_display: string;
  last_contacted?: string;
  next_follow_up?: string;
  budget?: string;
  notes?: string;
  owner: number;
  owner_name: string;
  owner_email: string;
  created_at: string;
  updated_at: string;
  comments_count: number;
  tasks_count: number;
  completed_tasks_count: number;
}

export interface LeadDetail extends Lead {
  comments: Comment[];
  tasks: Task[];
  activities: Activity[];
}

export interface Comment {
  id: number;
  lead: number;
  lead_name: string;
  body: string;
  author: string;
  author_name: string;
  kind: CommentKind;
  created_at: string;
}

export interface Task {
  id: number;
  lead: number;
  lead_name: string;
  lead_status: string;
  title: string;
  completed: boolean;
  created_at: string;
}

export interface Activity {
  id: number;
  lead: number;
  lead_name: string;
  action: string;
  details: string;
  created_by: string;
  created_at: string;
}

export interface Profile {
  id: number;
  user: number;
  user_name: string;
  user_email: string;
  organization?: string;
  timezone?: string;
  reminder_days?: number;
}

export interface DashboardStats {
  total_leads: number;
  new_leads: number;
  contacted_leads: number;
  proposal_leads: number;
  won_leads: number;
  lost_leads: number;
  today_followups: number;
  overdue_followups: number;
  total_budget: number;
  won_budget: number;
}

// Enum tipai
export type LeadStatus = 'new' | 'contacted' | 'proposal' | 'won' | 'lost';
export type CommentKind = 'note' | 'call' | 'email' | 'message';

// API užklausų tipai
export interface CreateLeadRequest {
  name: string;
  company?: string;
  email?: string;
  phone?: string;
  source?: string;
  status?: LeadStatus;
  last_contacted?: string;
  next_follow_up?: string;
  budget?: number;
  notes?: string;
}

export interface UpdateLeadStatusRequest {
  status: LeadStatus;
}

export interface AddCommentRequest {
  body: string;
  kind?: CommentKind;
  author?: string;
}

export interface AddTaskRequest {
  title: string;
}

export interface ListLeadsParams {
  status?: LeadStatus;
  search?: string;
  limit?: number;
  ordering?: string;
}

export interface GetFollowupsParams {
  type?: 'upcoming' | 'overdue';
  days?: number;
}

// API atsakymų tipai
export interface ApiResponse<T> {
  count?: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// JWT autentifikacijos tipai
export interface LoginRequest {
  username: string;
  password: string;
}

export interface SignupRequest {
  username: string;
  email: string;
  password: string;
}

export interface SignupResponse {
  success: boolean;
  message: string;
  user_id: number;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

// MCP serverio tipai
export interface MCPRequest {
  method: string;
  params: {
    name: string;
    arguments: Record<string, any>;
  };
}

export interface MCPResponse {
  content: Array<{
    type: string;
    text: string;
  }>;
  error?: {
    code: number;
    message: string;
  };
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, any>;
}

// UI komponentų tipai
export interface LeadCardProps {
  lead: Lead;
  onUpdate?: (lead: Lead) => void;
  onDelete?: (leadId: number) => void;
  onStatusChange?: (leadId: number, status: LeadStatus) => void;
}

export interface DashboardProps {
  stats: DashboardStats;
  upcomingFollowups: Lead[];
  overdueFollowups: Lead[];
}

export interface LeadDetailProps {
  lead: LeadDetail;
  onAddComment: (leadId: number, comment: AddCommentRequest) => Promise<void>;
  onAddTask: (leadId: number, task: AddTaskRequest) => Promise<void>;
  onStatusUpdate: (leadId: number, status: LeadStatus) => Promise<void>;
}

// Formų tipai
export interface LeadFormData {
  name: string;
  company: string;
  email: string;
  phone: string;
  status: LeadStatus;
  budget: string;
  notes: string;
}

export interface CommentFormData {
  body: string;
  kind: CommentKind;
  author: string;
}

export interface TaskFormData {
  title: string;
}

// Filtrų tipai
export interface LeadFilters {
  status?: LeadStatus;
  search?: string;
  dateRange?: {
    start: string;
    end: string;
  };
  budgetRange?: {
    min: number;
    max: number;
  };
}

// Skybridge specifiniai tipai
export interface SkybridgeConfig {
  apiBaseUrl: string;
  authToken?: string;
  enableMCP?: boolean;
  mcpServerUrl?: string;
}

export interface SkybridgeState {
  isAuthenticated: boolean;
  user: Profile | null;
  leads: Lead[];
  currentLead: LeadDetail | null;
  loading: boolean;
  error: string | null;
}

// Error tipai
export interface ApiError {
  code: number;
  message: string;
  details?: Record<string, any>;
}

// Helper tipai
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
