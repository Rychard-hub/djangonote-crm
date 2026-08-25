// PipelineView komponentas - lead'ų pipeline vaizdavimas

import React from 'react';
import type { Lead } from '../types/crm';
import { useLeads } from '../hooks/useCRM';

interface PipelineViewProps {
  className?: string;
}

const statusConfig = [
  { key: 'new', label: 'Nauji', color: 'bg-blue-100 border-blue-300' },
  { key: 'contacted', label: 'Susisiekti', color: 'bg-yellow-100 border-yellow-300' },
  { key: 'proposal', label: 'Pasiūlymas', color: 'bg-purple-100 border-purple-300' },
  { key: 'won', label: 'Laimėti', color: 'bg-green-100 border-green-300' },
  { key: 'lost', label: 'Pralaimėti', color: 'bg-red-100 border-red-300' },
];

export function PipelineView({ className = '' }: PipelineViewProps) {
  const { leads, loading, error } = useLeads();

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <div className="text-red-800">
          <strong>Klaida:</strong> {error}
        </div>
      </div>
    );
  }

  const getLeadsByStatus = (status: string) => {
    return leads.filter(lead => lead.status === status);
  };

  const formatBudget = (budget: string | null | undefined) => {
    if (!budget) return '-';
    return `€${parseFloat(budget).toLocaleString('lt-LT')}`;
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('lt-LT');
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Pipeline</h2>
        <p className="text-gray-600">Lead'ų pipeline peržiūra ({leads.length} viso)</p>
      </div>

      {/* Pipeline Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {statusConfig.map((status) => {
          const statusLeads = getLeadsByStatus(status.key);
          const totalBudget = statusLeads.reduce((sum, lead) => {
            return sum + (lead.budget ? parseFloat(lead.budget) : 0);
          }, 0);

          return (
            <div key={status.key} className="bg-white rounded-lg shadow p-4">
              <div className="text-sm font-medium text-gray-600">{status.label}</div>
              <div className="text-2xl font-bold text-gray-900">{statusLeads.length}</div>
              <div className="text-sm text-gray-500">{formatBudget(totalBudget.toString())}</div>
            </div>
          );
        })}
      </div>

      {/* Pipeline Board */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {statusConfig.map((status) => {
          const statusLeads = getLeadsByStatus(status.key);
          
          return (
            <div key={status.key} className={`${status.color} border-2 rounded-lg p-4`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-800">{status.label}</h3>
                <span className="bg-white bg-opacity-70 px-2 py-1 rounded-full text-sm font-medium">
                  {statusLeads.length}
                </span>
              </div>
              
              <div className="space-y-3">
                {statusLeads.map((lead) => (
                  <div key={lead.id} className="bg-white bg-opacity-90 rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                    <div className="font-medium text-gray-900 text-sm">{lead.name}</div>
                    {lead.company && (
                      <div className="text-xs text-gray-600">{lead.company}</div>
                    )}
                    
                    <div className="mt-2 space-y-1">
                      {lead.email && (
                        <div className="text-xs text-gray-500 truncate">{lead.email}</div>
                      )}
                      {lead.budget && (
                        <div className="text-xs font-medium text-gray-700">
                          {formatBudget(lead.budget)}
                        </div>
                      )}
                      {lead.next_follow_up && (
                        <div className="text-xs text-blue-600">
                          📅 {formatDate(lead.next_follow_up)}
                        </div>
                      )}
                    </div>
                    
                    <div className="mt-2 flex justify-between items-center">
                      <div className="text-xs text-gray-500">
                        {lead.comments_count} 💬 | {lead.tasks_count} ✅
                      </div>
                      <button className="text-blue-600 hover:text-blue-800 text-xs font-medium">
                        Peržiūrėti
                      </button>
                    </div>
                  </div>
                ))}
                
                {statusLeads.length === 0 && (
                  <div className="text-center py-8 text-gray-500 text-sm">
                    Nėra lead'ų
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Conversion Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Konversijos metrika</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="text-sm text-gray-600">Bendra konversija</div>
            <div className="text-2xl font-bold text-green-600">
              {leads.length > 0 
                ? `${((getLeadsByStatus('won').length / leads.length) * 100).toFixed(1)}%`
                : '0%'
              }
            </div>
            <div className="text-xs text-gray-500">
              {getLeadsByStatus('won').length} iš {leads.length}
            </div>
          </div>
          
          <div>
            <div className="text-sm text-gray-600">Vid. biudžetas</div>
            <div className="text-2xl font-bold text-blue-600">
              {formatBudget(
                (leads.reduce((sum, lead) => sum + (lead.budget ? parseFloat(lead.budget) : 0), 0) / leads.length || 0).toString()
              )}
            </div>
          </div>
          
          <div>
            <div className="text-sm text-gray-600">Laimėtas biudžetas</div>
            <div className="text-2xl font-bold text-green-600">
              {formatBudget(
                getLeadsByStatus('won').reduce((sum, lead) => sum + (lead.budget ? parseFloat(lead.budget) : 0), 0).toString()
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
