import { McpServer } from "skybridge/server";
import { z } from "zod";
import { CRMBridge } from "./crm-bridge";
import { LeadListView } from "./views/LeadListView";
import { LeadDetailView } from "./views/LeadDetailView";
import { DashboardView } from "./views/DashboardView";

// Sukuriam CRM bridge jungtį su Django backend
const crmBridge = new CRMBridge("http://127.0.0.1:8000");

// Sukuriam MCP serverį su CRM funkcionalumu
const server = new McpServer(
  { 
    name: "skybridge-crm", 
    version: "1.0.0" 
  },
  {
    // Konfigūruojame autentifikaciją
    auth: {
      type: "jwt",
      tokenEndpoint: "http://127.0.0.1:8000/api/auth/token/"
    }
  }
);

// Registruojame CRM įrankius
server.registerTool({
  name: "list_leads",
  description: "Gauti lead'ų sąrašą",
  inputSchema: {
    limit: z.number().optional().default(20),
    status: z.enum(["new", "contacted", "proposal", "won", "lost"]).optional(),
    search: z.string().optional()
  },
  view: { component: LeadListView },
  handler: async ({ limit = 20, status, search }: { limit?: number; status?: "new" | "contacted" | "proposal" | "won" | "lost"; search?: string }) => {
    const leads = await crmBridge.getLeads({ limit, status, search });
    return {
      structuredContent: {
        leads: leads.data || [],
        total: leads.count || 0
      }
    };
  }
});

server.registerTool({
  name: "get_lead",
  description: "Gauti konkretų lead'ą",
  inputSchema: {
    leadId: z.number()
  },
  view: { component: LeadDetailView },
  handler: async ({ leadId }: { leadId: number }) => {
    const lead = await crmBridge.getLead(leadId);
    const comments = await crmBridge.getComments(leadId);
    const tasks = await crmBridge.getTasks(leadId);
    
    return {
      structuredContent: {
        lead: lead.data,
        comments: comments.data || [],
        tasks: tasks.data || []
      }
    };
  }
});

server.registerTool({
  name: "create_lead",
  description: "Sukurti naują lead'ą",
  inputSchema: {
    name: z.string(),
    company: z.string().optional(),
    email: z.string().email().optional(),
    phone: z.string().optional(),
    status: z.enum(["new", "contacted", "proposal", "won", "lost"]).default("new"),
    budget: z.number().optional(),
    notes: z.string().optional()
  },
  handler: async (data: { name: string; company?: string; email?: string; phone?: string; status?: "new" | "contacted" | "proposal" | "won" | "lost"; budget?: number; notes?: string }) => {
    const lead = await crmBridge.createLead(data);
    return {
      structuredContent: {
        lead: lead.data,
        message: "Lead'as sėkmingai sukurtas"
      }
    };
  }
});

server.registerTool({
  name: "update_lead",
  description: "Atnaujinti lead'ą",
  inputSchema: {
    leadId: z.number(),
    name: z.string().optional(),
    company: z.string().optional(),
    email: z.string().email().optional(),
    phone: z.string().optional(),
    status: z.enum(["new", "contacted", "proposal", "won", "lost"]).optional(),
    budget: z.number().optional(),
    notes: z.string().optional()
  },
  handler: async ({ leadId, ...updateData }: { leadId: number; name?: string; company?: string; email?: string; phone?: string; status?: "new" | "contacted" | "proposal" | "won" | "lost"; budget?: number; notes?: string }) => {
    const lead = await crmBridge.updateLead(leadId, updateData);
    return {
      structuredContent: {
        lead: lead.data,
        message: "Lead'as sėkmingai atnaujintas"
      }
    };
  }
});

server.registerTool({
  name: "add_comment",
  description: "Pridėti komentarą",
  inputSchema: {
    leadId: z.number(),
    body: z.string(),
    kind: z.enum(["note", "call", "email", "message"]).default("note"),
    author: z.string().default("AI Assistant")
  },
  handler: async ({ leadId, body, kind, author }: { leadId: number; body: string; kind?: "note" | "call" | "email" | "message"; author?: string }) => {
    const comment = await crmBridge.createComment(leadId, { body, kind, author });
    return {
      structuredContent: {
        comment: comment.data,
        message: "Komentaras sėkmingai pridėtas"
      }
    };
  }
});

server.registerTool({
  name: "add_task",
  description: "Pridėti užduotį",
  inputSchema: {
    leadId: z.number(),
    title: z.string()
  },
  handler: async ({ leadId, title }: { leadId: number; title: string }) => {
    const task = await crmBridge.createTask(leadId, { title });
    return {
      structuredContent: {
        task: task.data,
        message: "Užduotis sėkmingai pridėta"
      }
    };
  }
});

server.registerTool({
  name: "get_dashboard",
  description: "Gauti dashboard statistiką",
  inputSchema: {},
  view: { component: DashboardView },
  handler: async () => {
    const stats = await crmBridge.getDashboardStats();
    return {
      structuredContent: {
        stats: stats.data
      }
    };
  }
});

// Eksportuojam serverį
export { server };
