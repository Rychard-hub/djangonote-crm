// React hooks skirti CRM duomenų valdymui

import { useState, useEffect, useCallback } from 'react';
import { crmApi } from '../utils/api';
import type {
  Lead,
  LeadDetail,
  Comment,
  Task,
  Activity,
  DashboardStats,
  Profile,
  CreateLeadRequest,
  AddCommentRequest,
  AddTaskRequest,
  ListLeadsParams,
  LeadStatus,
  ApiError
} from '../types/crm';

// Lead'ų valdymo hooks
export function useLeads(params?: ListLeadsParams) {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLeads = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await crmApi.getLeads(params);
      console.log('🔍 React useLeads: Gauti leadai:', response.results.length);
      console.log('🔍 React useLeads: Atsakymas:', response);
      setLeads(response.results);
    } catch (err) {
      console.error('❌ React useLeads klaida:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch leads');
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    if (crmApi.isAuthenticated()) {
      fetchLeads();
    }
  }, [fetchLeads]);

  // Pridedame autentifikacijos pasikrovimą iš localStorage
  useEffect(() => {
    // Patikriname, ar token'as yra localStorage
    if (crmApi.isAuthenticated()) {
      fetchLeads();
    }
  }, []);

  const createLead = useCallback(async (data: CreateLeadRequest): Promise<Lead | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const newLead = await crmApi.createLead(data);
      setLeads(prev => [newLead, ...prev]);
      return newLead;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create lead');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateLeadStatus = useCallback(async (id: number, status: LeadStatus): Promise<boolean> => {
    try {
      const updatedLead = await crmApi.updateLeadStatus(id, { status });
      setLeads(prev => prev.map(lead => 
        lead.id === id ? updatedLead : lead
      ));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update lead status');
      return false;
    }
  }, []);

  const deleteLead = useCallback(async (id: number): Promise<boolean> => {
    try {
      await crmApi.deleteLead(id);
      setLeads(prev => prev.filter(lead => lead.id !== id));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete lead');
      return false;
    }
  }, []);

  return {
    leads,
    loading,
    error,
    refetch: fetchLeads,
    createLead,
    updateLeadStatus,
    deleteLead,
  };
}

// Konkretaus lead'o duomenų hooks
export function useLead(id: number) {
  const [lead, setLead] = useState<LeadDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLead = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const leadData = await crmApi.getLead(id);
      setLead(leadData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch lead');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (crmApi.isAuthenticated() && id) {
      fetchLead();
    }
  }, [fetchLead, id]);

  const addComment = useCallback(async (data: AddCommentRequest): Promise<Comment | null> => {
    try {
      const newComment = await crmApi.addComment(id, data);
      setLead(prev => prev ? {
        ...prev,
        comments: [newComment, ...prev.comments]
      } : null);
      return newComment;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add comment');
      return null;
    }
  }, [id]);

  const addTask = useCallback(async (data: AddTaskRequest): Promise<Task | null> => {
    try {
      const newTask = await crmApi.addTask(id, data);
      setLead(prev => prev ? {
        ...prev,
        tasks: [newTask, ...prev.tasks]
      } : null);
      return newTask;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add task');
      return null;
    }
  }, [id]);

  return {
    lead,
    loading,
    error,
    refetch: fetchLead,
    addComment,
    addTask,
  };
}

// Dashboard statistikos hooks
export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [upcomingFollowups, setUpcomingFollowups] = useState<Lead[]>([]);
  const [overdueFollowups, setOverdueFollowups] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [statsData, upcomingData, overdueData] = await Promise.all([
        crmApi.getDashboardStats(),
        crmApi.getUpcomingFollowups(7),
        crmApi.getOverdueFollowups(),
      ]);
      
      setStats(statsData);
      setUpcomingFollowups(upcomingData);
      setOverdueFollowups(overdueData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (crmApi.isAuthenticated()) {
      fetchDashboardData();
    }
  }, [fetchDashboardData]);

  return {
    stats,
    upcomingFollowups,
    overdueFollowups,
    loading,
    error,
    refetch: fetchDashboardData,
  };
}

// Užduočių valdymo hooks
export function useTasks(params?: { completed?: boolean; lead?: number }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const tasksData = await crmApi.getTasks(params);
      setTasks(tasksData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    if (crmApi.isAuthenticated()) {
      fetchTasks();
    }
  }, [fetchTasks]);

  const toggleTaskComplete = useCallback(async (id: number): Promise<boolean> => {
    try {
      const updatedTask = await crmApi.toggleTaskComplete(id);
      setTasks(prev => prev.map(task => 
        task.id === id ? updatedTask : task
      ));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle task');
      return false;
    }
  }, []);

  return {
    tasks,
    loading,
    error,
    refetch: fetchTasks,
    toggleTaskComplete,
  };
}

// Veiksmų istorijos hooks
export function useActivities(leadId?: number) {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchActivities = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const activitiesData = leadId 
        ? await crmApi.getActivities(leadId)
        : await crmApi.getAllActivities();
      setActivities(activitiesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch activities');
    } finally {
      setLoading(false);
    }
  }, [leadId]);

  useEffect(() => {
    if (crmApi.isAuthenticated()) {
      fetchActivities();
    }
  }, [fetchActivities]);

  return {
    activities,
    loading,
    error,
    refetch: fetchActivities,
  };
}

// Profilio valdymo hooks
export function useProfile() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const profileData = await crmApi.getProfile();
      setProfile(profileData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch profile');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (crmApi.isAuthenticated()) {
      fetchProfile();
    }
  }, [fetchProfile]);

  const updateProfile = useCallback(async (data: Partial<Profile>): Promise<boolean> => {
    try {
      const updatedProfile = await crmApi.updateProfile(data);
      setProfile(updatedProfile);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
      return false;
    }
  }, []);

  return {
    profile,
    loading,
    error,
    refetch: fetchProfile,
    updateProfile,
  };
}

// Autentifikacijos hooks
export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(crmApi.isAuthenticated());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (username: string, password: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      await crmApi.login({ username, password });
      setIsAuthenticated(true);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    crmApi.logout();
    setIsAuthenticated(false);
  }, []);

  const signup = useCallback(async (data: { username: string; email: string; password: string }): Promise<boolean> => {
    setLoading(true);
    setError(null);
    
    try {
      await crmApi.signup(data);
      await crmApi.login({ username: data.username, password: data.password });
      setIsAuthenticated(true);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  // Patikriname autentifikacijos būseną kiekvieną kartą, kai komponentas mount'inamas
  useEffect(() => {
    const checkAuth = () => {
      const isAuth = crmApi.isAuthenticated();
      if (isAuth !== isAuthenticated) {
        setIsAuthenticated(isAuth);
      }
    };
    
    checkAuth();
    
    // Patikriname kas keletą sekundžių (jei token'as pasikeičė kitame tab'e)
    const interval = setInterval(checkAuth, 5000);

    // Jei API grąžina 401, nedelsiant atsijungiame
    const handleUnauthorized = () => {
      logout();
    };
    window.addEventListener('auth:unauthorized', handleUnauthorized);

    return () => {
      clearInterval(interval);
      window.removeEventListener('auth:unauthorized', handleUnauthorized);
    };
  }, [isAuthenticated, logout]);

  return {
    isAuthenticated,
    loading,
    error,
    login,
    logout,
    signup,
  };
}

// MCP serverio integracijos hooks
export function useMCP() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const callMCPServer = useCallback(async (toolName: string, args: Record<string, any>) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await crmApi.callMCPServer(toolName, args);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'MCP server call failed');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    loading,
    error,
    callMCPServer,
  };
}

// Paieškos hooks
export function useSearch<T>(
  searchFunction: (query: string) => Promise<T[]>,
  debounceMs: number = 300
) {
  const [results, setResults] = useState<T[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (query.trim()) {
        setLoading(true);
        setError(null);
        
        try {
          const searchResults = await searchFunction(query);
          setResults(searchResults);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Search failed');
          setResults([]);
        } finally {
          setLoading(false);
        }
      } else {
        setResults([]);
        setError(null);
      }
    }, debounceMs);

    return () => clearTimeout(timeoutId);
  }, [query, searchFunction, debounceMs]);

  return {
    results,
    query,
    setQuery,
    loading,
    error,
  };
}
