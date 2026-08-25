// API klientas skirtas Django CRM integracijai

import type {
  Lead,
  LeadDetail,
  Comment,
  Task,
  Activity,
  DashboardStats,
  Profile,
  CreateLeadRequest,
  UpdateLeadStatusRequest,
  AddCommentRequest,
  AddTaskRequest,
  ListLeadsParams,
  GetFollowupsParams,
  ApiResponse,
  PaginatedResponse,
  TokenResponse,
  LoginRequest,
  SignupRequest,
  SignupResponse,
  ApiError
} from '../types/crm';

export class CRMApiClient {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
    // Load token from localStorage on initialization
    this.authToken = localStorage.getItem('crm_token');
  }

  // Autentifikacija
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await this.fetch('/auth/token/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    const data = await response.json();
    this.setAuthToken(data.access);
    return data;
  }

  async signup(data: SignupRequest): Promise<SignupResponse> {
    const response = await this.fetch('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    return await response.json() as SignupResponse;
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await fetch(`${this.baseUrl}/auth/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    const data = await response.json();
    this.setAuthToken(data.access);
    return data;
  }

  setAuthToken(token: string | null): void {
    this.authToken = token;
    if (token) {
      localStorage.setItem('crm_token', token);
    } else {
      localStorage.removeItem('crm_token');
    }
  }

  getAuthToken(): string | null {
    if (!this.authToken) {
      this.authToken = localStorage.getItem('crm_token');
    }
    return this.authToken;
  }

  isAuthenticated(): boolean {
    return !!this.getAuthToken();
  }

  
  // Privatus fetch metodas su autentifikacija
  private async fetch(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = new Headers({
      'Content-Type': 'application/json',
      ...options.headers,
    });

    if (this.authToken) {
      headers.set('Authorization', `Bearer ${this.authToken}`);
      console.log('🔑 API fetch su token:', endpoint);
    } else {
      console.log('❌ API fetch be token:', endpoint);
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    console.log('📡 API atsakymas:', endpoint, response.status);

    if (response.status === 401 && this.authToken) {
      console.warn('🔒 Token nebegalioja - atsijungiame');
      this.logout();
      window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    }

    return response;
  }

  private async handleError(response: Response): Promise<ApiError> {
    let errorData: any;
    try {
      errorData = await response.json();
    } catch {
      errorData = { message: response.statusText };
    }

    return {
      code: response.status,
      message: errorData.message || errorData.detail || 'Unknown error',
      details: errorData,
    };
  }

  // Lead'ų valdymas
  async getLeads(params?: ListLeadsParams): Promise<PaginatedResponse<Lead>> {
    const searchParams = new URLSearchParams();
    
    if (params?.status) searchParams.append('status', params.status);
    if (params?.search) searchParams.append('search', params.search);
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.ordering) searchParams.append('ordering', params.ordering);

    const response = await this.fetch(`/leads/?${searchParams}`);
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  async getLead(id: number): Promise<LeadDetail> {
    const response = await this.fetch(`/leads/${id}/`);
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  async createLead(data: CreateLeadRequest): Promise<Lead> {
    const response = await this.fetch('/leads/', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  async updateLead(id: number, data: Partial<CreateLeadRequest>): Promise<Lead> {
    const response = await this.fetch(`/leads/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  async deleteLead(id: number): Promise<void> {
    const response = await this.fetch(`/leads/${id}/`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }
  }

  async updateLeadStatus(id: number, status: UpdateLeadStatusRequest): Promise<Lead> {
    const response = await this.fetch(`/leads/${id}/update_status/`, {
      method: 'PATCH',
      body: JSON.stringify(status),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  // Komentarų valdymas
  async addComment(leadId: number, data: AddCommentRequest): Promise<Comment> {
    const response = await this.fetch(`/leads/${leadId}/add_comment/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  async getComments(leadId: number): Promise<Comment[]> {
    const response = await this.fetch(`/comments/?lead=${leadId}`);
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    const data = await response.json();
    return data.results || data;
  }

  // Užduočių valdymas
  async addTask(leadId: number, data: AddTaskRequest): Promise<Task> {
    const response = await this.fetch(`/leads/${leadId}/add_task/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  async getTasks(params?: { completed?: boolean; lead?: number }): Promise<Task[]> {
    const searchParams = new URLSearchParams();
    
    if (params?.completed !== undefined) searchParams.append('completed', params.completed.toString());
    if (params?.lead) searchParams.append('lead', params.lead.toString());

    const response = await this.fetch(`/tasks/?${searchParams}`);
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    const data = await response.json();
    return data.results || data;
  }

  async toggleTaskComplete(id: number): Promise<Task> {
    const response = await this.fetch(`/tasks/${id}/toggle_complete/`, {
      method: 'PATCH',
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  // Veiksmų istorija
  async getActivities(leadId: number): Promise<Activity[]> {
    const response = await this.fetch(`/leads/${leadId}/activities/`);
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  async getAllActivities(params?: { lead?: number; action?: string }): Promise<Activity[]> {
    const searchParams = new URLSearchParams();
    
    if (params?.lead) searchParams.append('lead', params.lead.toString());
    if (params?.action) searchParams.append('action', params.action);

    const response = await this.fetch(`/activities/?${searchParams}`);
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    const data = await response.json();
    return data.results || data;
  }

  // Dashboard statistika
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.fetch('/dashboard/summary/');
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  // Follow-up'ai
  async getUpcomingFollowups(days: number = 7): Promise<Lead[]> {
    const response = await this.fetch(`/leads/upcoming_followups/?days=${days}`);
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  async getOverdueFollowups(): Promise<Lead[]> {
    const response = await this.fetch('/leads/overdue_followups/');
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  // Profilis
  async getProfile(): Promise<Profile> {
    const response = await this.fetch('/profile/');
    
    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  async updateProfile(data: Partial<Profile>): Promise<Profile> {
    const response = await this.fetch('/profile/', {
      method: 'PATCH',
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    return response.json();
  }

  // MCP serverio integracija
  async callMCPServer(toolName: string, args: Record<string, any>): Promise<any> {
    const mcpRequest = {
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: args,
      },
    };

    const response = await this.fetch('/mcp/', {
      method: 'POST',
      body: JSON.stringify(mcpRequest),
    });

    if (!response.ok) {
      throw await this.handleError(response);
    }

    const mcpResponse = await response.json();
    
    if (mcpResponse.error) {
      throw mcpResponse.error;
    }

    // Parse JSON content from MCP response
    if (mcpResponse.content && mcpResponse.content[0]?.type === 'text') {
      return JSON.parse(mcpResponse.content[0].text);
    }

    return mcpResponse;
  }

  // Pagalbinės funkcijos
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.fetch('/leads/');
      return response.ok;
    } catch {
      return false;
    }
  }

  async logout(): Promise<void> {
    this.setAuthToken(null);
  }

  // Kvietimų siuntimas
  async sendInvitation(email: string): Promise<{ success: boolean; message: string; invitation_link?: string }> {
    const response = await this.fetch('/profile/send_invitation/', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const error = await this.handleError(response);
      throw error;
    }

    const data = await response.json();
    return {
      success: data.success,
      message: data.message,
      invitation_link: data.invitation_link
    };
  }
}

// Singleton instance
export const crmApi = new CRMApiClient();
