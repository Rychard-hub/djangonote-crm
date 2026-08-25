import React, { useState, useEffect } from 'react';
import { useLeads } from '../hooks/useCRM';
import type { Lead, LeadStatus } from '../types/crm';

const statusColors: Record<LeadStatus, string> = {
  'new': 'bg-gray-100 text-gray-800',
  'contacted': 'bg-blue-100 text-blue-800',
  'proposal': 'bg-yellow-100 text-yellow-800',
  'won': 'bg-green-100 text-green-800',
  'lost': 'bg-red-100 text-red-800'
};

const statusLabels: Record<LeadStatus, string> = {
  'new': 'Naujas',
  'contacted': 'Susisiektas',
  'proposal': 'Pasiūlymas',
  'won': 'Laimėtas',
  'lost': 'Pralaimėtas'
};

export const PipelineView: React.FC = () => {
  const { leads, loading, error } = useLeads();
  const [draggedLead, setDraggedLead] = useState<Lead | null>(null);

  const pipelineStages: LeadStatus[] = ['new', 'contacted', 'proposal', 'won', 'lost'];

  const getLeadsByStatus = (status: LeadStatus) => {
    return leads.filter(lead => lead.status === status);
  };

  const handleDragStart = (lead: Lead) => {
    setDraggedLead(lead);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent, newStatus: LeadStatus) => {
    e.preventDefault();
    if (draggedLead && draggedLead.status !== newStatus) {
      // TODO: Implement lead status update
      console.log(`Moving ${draggedLead.name} from ${draggedLead.status} to ${newStatus}`);
    }
    setDraggedLead(null);
  };

  const calculateStageStats = (status: LeadStatus) => {
    const stageLeads = getLeadsByStatus(status);
    const totalBudget = stageLeads.reduce((sum, lead) => sum + (Number(lead.budget) || 0), 0);
    return {
      count: stageLeads.length,
      budget: totalBudget
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Kraunamas pipeline...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Klaida: {error}</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Sales Pipeline</h1>
        <p className="text-gray-600">Valdykite savo pardavimų procesą vizualiai</p>
      </div>

      {/* Pipeline Summary */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        {pipelineStages.map(status => {
          const stats = calculateStageStats(status);
          return (
            <div key={status} className="bg-white rounded-lg shadow p-4 border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status]}`}>
                  {statusLabels[status]}
                </span>
                <span className="text-2xl font-bold text-gray-900">{stats.count}</span>
              </div>
              <div className="text-sm text-gray-600">
                €{stats.budget.toLocaleString()}
              </div>
            </div>
          );
        })}
      </div>

      {/* Pipeline Board */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {pipelineStages.map(status => (
          <div
            key={status}
            className="bg-gray-50 rounded-lg p-4 min-h-[400px]"
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, status)}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">
                {statusLabels[status]}
              </h3>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status]}`}>
                {getLeadsByStatus(status).length}
              </span>
            </div>

            <div className="space-y-2">
              {getLeadsByStatus(status).map(lead => (
                <div
                  key={lead.id}
                  draggable
                  onDragStart={() => handleDragStart(lead)}
                  className="bg-white rounded-lg p-3 shadow-sm border border-gray-200 cursor-move hover:shadow-md transition-shadow"
                >
                  <div className="font-medium text-gray-900 truncate">
                    {lead.name}
                  </div>
                  {lead.company && (
                    <div className="text-sm text-gray-600 truncate">
                      {lead.company}
                    </div>
                  )}
                  {lead.budget && (
                    <div className="text-sm font-medium text-blue-600">
                      €{lead.budget.toLocaleString()}
                    </div>
                  )}
                  <div className="text-xs text-gray-500 mt-1">
                    {lead.next_follow_up 
                      ? new Date(lead.next_follow_up).toLocaleDateString('lt-LT')
                      : 'Nėra planų'
                    }
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {leads.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-4">Dar neturite lead'ų</div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
            Pridėti pirmą Lead'ą
          </button>
        </div>
      )}
    </div>
  );
};
