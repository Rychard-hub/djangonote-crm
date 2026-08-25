// FollowUpView komponentas - follow-up'ų valdymas

import React from 'react';
import type { Lead } from '../types/crm';
import { useDashboard } from '../hooks/useCRM';

interface FollowUpViewProps {
  className?: string;
}

export function FollowUpView({ className = '' }: FollowUpViewProps) {
  const { upcomingFollowups, overdueFollowups, loading, error } = useDashboard();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('lt-LT');
  };

  const isOverdue = (dateString: string) => {
    return new Date(dateString) < new Date();
  };

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

  return (
    <div className={`space-y-6 ${className}`}>
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Follow-up'ai</h2>
        <p className="text-gray-600">Visi follow-up'ai ({upcomingFollowups.length + overdueFollowups.length})</p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Šiandien</div>
          <div className="text-3xl font-bold text-blue-600">
            {upcomingFollowups.filter(lead => {
              const today = new Date().toDateString();
              const followUpDate = new Date(lead.next_follow_up || '').toDateString();
              return today === followUpDate;
            }).length}
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Vėluojantys</div>
          <div className="text-3xl font-bold text-red-600">{overdueFollowups.length}</div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Artėjantys</div>
          <div className="text-3xl font-bold text-green-600">{upcomingFollowups.length}</div>
        </div>
      </div>

      {/* Overdue Follow-ups */}
      {overdueFollowups.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-red-600">
              Vėluojantys Follow-up'ai ({overdueFollowups.length})
            </h3>
          </div>
          <div className="divide-y divide-gray-200">
            {overdueFollowups.map((lead) => (
              <div key={lead.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h4 className="text-sm font-medium text-gray-900">{lead.name}</h4>
                      {lead.company && (
                        <span className="ml-2 text-sm text-gray-500">({lead.company})</span>
                      )}
                    </div>
                    <div className="mt-1 flex items-center text-sm text-gray-500">
                      <span className="mr-4">{lead.email || '-'}</span>
                      <span className="mr-4">{lead.phone || '-'}</span>
                      <span className="text-red-600 font-medium">
                        Follow-up: {formatDate(lead.next_follow_up || '')}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      lead.status === 'new' ? 'bg-blue-100 text-blue-800' :
                      lead.status === 'contacted' ? 'bg-yellow-100 text-yellow-800' :
                      lead.status === 'proposal' ? 'bg-purple-100 text-purple-800' :
                      lead.status === 'won' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {lead.status_display}
                    </span>
                    <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                      Priminti
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upcoming Follow-ups */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Artėjantys Follow-up'ai ({upcomingFollowups.length})
          </h3>
        </div>
        <div className="divide-y divide-gray-200">
          {upcomingFollowups.map((lead) => (
            <div key={lead.id} className="px-6 py-4 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <h4 className="text-sm font-medium text-gray-900">{lead.name}</h4>
                    {lead.company && (
                      <span className="ml-2 text-sm text-gray-500">({lead.company})</span>
                    )}
                  </div>
                  <div className="mt-1 flex items-center text-sm text-gray-500">
                    <span className="mr-4">{lead.email || '-'}</span>
                    <span className="mr-4">{lead.phone || '-'}</span>
                    <span className={
                      isOverdue(lead.next_follow_up || '') ? 'text-red-600 font-medium' : 'text-gray-600'
                    }>
                      Follow-up: {formatDate(lead.next_follow_up || '')}
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    lead.status === 'new' ? 'bg-blue-100 text-blue-800' :
                    lead.status === 'contacted' ? 'bg-yellow-100 text-yellow-800' :
                    lead.status === 'proposal' ? 'bg-purple-100 text-purple-800' :
                    lead.status === 'won' ? 'bg-green-100 text-green-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {lead.status_display}
                  </span>
                  <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                    Priminti
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {upcomingFollowups.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500">Nėra artėjančių follow-up'ų</div>
          </div>
        )}
      </div>
    </div>
  );
}
