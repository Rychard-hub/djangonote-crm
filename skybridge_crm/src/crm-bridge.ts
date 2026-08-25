/**
 * CRM Bridge - jungtis tarp Skybridge ir Django API
 * Atsakinga už visus HTTP requestus į Django backend
 */

export interface Lead {
  id: number;
  name: string;
  company?: string;
  email?: string;
  phone?: string;
  status: 'new' | 'contacted' | 'proposal' | 'won' | 'lost';
  budget?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  next_follow_up?: string;
  last_contacted?: string;
}

export interface Comment {
  id: number;
  lead: number;
  body: string;
  kind: 'note' | 'call' | 'email' | 'message';
  author: string;
  created_at: string;
  created_by?: number;
}

export interface Task {
  id: number;
  lead: number;
  title: string;
  completed: boolean;
  created_at: string;
  created_by?: number;
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

export interface ApiResponse<T> {
  data?: T;
  count?: number;
  next?: string;
  previous?: string;
  error?: string;
  details?: string;
}

export class CRMBridge {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  }

  private async getHeaders(): Promise<HeadersInit> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async authenticate(username: string, password: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/auth/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        this.token = data.access;
        return true;
      }

      return false;
    } catch (error) {
      console.error('Authentication error:', error);
      return false;
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}/api${endpoint}`, {
        ...options,
        headers: await this.getHeaders(),
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: `HTTP ${response.status}`,
          details: data.detail || 'Unknown error',
        };
      }

      return { data };
    } catch (error) {
      return {
        error: 'connection_error',
        details: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async getLeads(params: {
    limit?: number;
    status?: string;
    search?: string;
  } = {}): Promise<ApiResponse<Lead[]>> {
    const queryParams = new URLSearchParams();
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.status) queryParams.append('status', params.status);
    if (params.search) queryParams.append('search', params.search);

    const endpoint = `/leads/${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request<Lead[]>(endpoint);
  }

  async getLead(leadId: number): Promise<ApiResponse<Lead>> {
    return this.request<Lead>(`/leads/${leadId}/`);
  }

  async createLead(leadData: Partial<Lead>): Promise<ApiResponse<Lead>> {
    return this.request<Lead>('/leads/', {
      method: 'POST',
      body: JSON.stringify(leadData),
    });
  }

  async updateLead(leadId: number, leadData: Partial<Lead>): Promise<ApiResponse<Lead>> {
    return this.request<Lead>(`/leads/${leadId}/`, {
      method: 'PATCH',
      body: JSON.stringify(leadData),
    });
  }

  async getComments(leadId: number): Promise<ApiResponse<Comment[]>> {
    return this.request<Comment[]>(`/leads/${leadId}/comments/`);
  }

  async createComment(
    leadId: number,
    commentData: { body: string; kind?: string; author?: string }
  ): Promise<ApiResponse<Comment>> {
    return this.request<Comment>(`/leads/${leadId}/comments/`, {
      method: 'POST',
      body: JSON.stringify(commentData),
    });
  }

  async getTasks(leadId: number): Promise<ApiResponse<Task[]>> {
    return this.request<Task[]>(`/leads/${leadId}/tasks/`);
  }

  async createTask(
    leadId: number,
    taskData: { title: string }
  ): Promise<ApiResponse<Task>> {
    return this.request<Task>(`/leads/${leadId}/tasks/`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    return this.request<DashboardStats>('/dashboard/summary/');
  }

  // Papildomi naudingi metodai
  async updateLeadStatus(leadId: number, status: string): Promise<ApiResponse<Lead>> {
    return this.request<Lead>(`/leads/${leadId}/update_status/`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  async toggleTaskComplete(taskId: number): Promise<ApiResponse<Task>> {
    return this.request<Task>(`/tasks/${taskId}/toggle_complete/`, {
      method: 'PATCH',
    });
  }

  async getUpcomingFollowups(days: number = 7): Promise<ApiResponse<Lead[]>> {
    return this.request<Lead[]>(`/leads/upcoming_followups/?days=${days}`);
  }

  async getOverdueFollowups(): Promise<ApiResponse<Lead[]>> {
    return this.request<Lead[]>('/leads/overdue_followups/');
  }
}
