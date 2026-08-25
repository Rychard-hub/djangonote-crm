import React, { useState, useEffect } from 'react';
import { useLeads } from '../hooks/useCRM';
import type { Lead } from '../types/crm';

interface FollowUpItem {
  lead: Lead;
  daysUntil: number;
  isOverdue: boolean;
  priority: 'high' | 'medium' | 'low';
}

export const FollowUpView: React.FC = () => {
  const { leads, loading, error } = useLeads();
  const [followUps, setFollowUps] = useState<FollowUpItem[]>([]);
  const [filter, setFilter] = useState<'all' | 'overdue' | 'today' | 'upcoming'>('all');

  useEffect(() => {
    if (leads.length > 0) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const followUpItems = leads
        .filter(lead => lead.next_follow_up)
        .map(lead => {
          const followUpDate = new Date(lead.next_follow_up!);
          followUpDate.setHours(0, 0, 0, 0);
          
          const diffTime = followUpDate.getTime() - today.getTime();
          const daysUntil = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
          
          let priority: 'high' | 'medium' | 'low' = 'low';
          if (daysUntil < 0) priority = 'high';
          else if (daysUntil <= 1) priority = 'high';
          else if (daysUntil <= 3) priority = 'medium';
          
          return {
            lead,
            daysUntil,
            isOverdue: daysUntil < 0,
            priority
          };
        })
        .sort((a, b) => a.daysUntil - b.daysUntil);
      
      setFollowUps(followUpItems);
    }
  }, [leads]);

  const getFilteredFollowUps = () => {
    switch (filter) {
      case 'overdue':
        return followUps.filter(item => item.isOverdue);
      case 'today':
        return followUps.filter(item => item.daysUntil === 0);
      case 'upcoming':
        return followUps.filter(item => item.daysUntil > 0);
      default:
        return followUps;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const getDaysText = (daysUntil: number) => {
    if (daysUntil === 0) return 'Šiandien';
    if (daysUntil === 1) return 'Rytoj';
    if (daysUntil === -1) return 'Vakar';
    if (daysUntil < 0) return `Prieš ${Math.abs(daysUntil)} d.`;
    return `Po ${daysUntil} d.`;
  };

  const getStats = () => {
    const overdue = followUps.filter(item => item.isOverdue).length;
    const today = followUps.filter(item => item.daysUntil === 0).length;
    const upcoming = followUps.filter(item => item.daysUntil > 0).length;
    
    return { overdue, today, upcoming, total: followUps.length };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Kraunami follow-up'ai...</div>
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

  const stats = getStats();
  const filteredFollowUps = getFilteredFollowUps();

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Follow-up Valdymas</h1>
        <p className="text-gray-600">Sekite ir planuokite susitikimus su klientais</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Viso</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <span className="text-xl">📅</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Vėluojantys</p>
              <p className="text-2xl font-bold text-red-600">{stats.overdue}</p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
              <span className="text-xl">⚠️</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Šiandien</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.today}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
              <span className="text-xl">🎯</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Ateityje</p>
              <p className="text-2xl font-bold text-green-600">{stats.upcoming}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <span className="text-xl">📈</span>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow mb-6 border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h3 className="font-medium text-gray-900">Filtrai</h3>
        </div>
        <div className="p-4">
          <div className="flex flex-wrap gap-2">
            {[
              { key: 'all', label: 'Visi', count: stats.total },
              { key: 'overdue', label: 'Vėluojantys', count: stats.overdue },
              { key: 'today', label: 'Šiandien', count: stats.today },
              { key: 'upcoming', label: 'Ateityje', count: stats.upcoming }
            ].map(({ key, label, count }) => (
              <button
                key={key}
                onClick={() => setFilter(key as any)}
                className={`px-4 py-2 rounded-md border transition-colors ${
                  filter === key
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }`}
              >
                {label} ({count})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Follow-ups List */}
      <div className="bg-white rounded-lg shadow border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h3 className="font-medium text-gray-900">
            Follow-up'ai ({filteredFollowUps.length})
          </h3>
        </div>
        
        {filteredFollowUps.length === 0 ? (
          <div className="p-8 text-center">
            <div className="text-gray-500 mb-4">
              {filter === 'all' ? 'Nėra planuotų follow-up\'ų' : `Nėra follow-up\'ų su filtru "${filter}"`}
            </div>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
              Planuoti Follow-up
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {filteredFollowUps.map(({ lead, daysUntil, isOverdue, priority }) => (
              <div key={lead.id} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <h4 className="font-medium text-gray-900">{lead.name}</h4>
                      {lead.company && (
                        <span className="text-gray-500">({lead.company})</span>
                      )}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getPriorityColor(priority)}`}>
                        {priority === 'high' ? 'Aukštas' : priority === 'medium' ? 'Vidutinis' : 'Žemas'}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                      <span className="flex items-center">
                        📅 {new Date(lead.next_follow_up!).toLocaleDateString('lt-LT')}
                      </span>
                      {lead.email && (
                        <span className="flex items-center">
                          ✉️ {lead.email}
                        </span>
                      )}
                      {lead.phone && (
                        <span className="flex items-center">
                          📞 {lead.phone}
                        </span>
                      )}
                    </div>
                    
                    {lead.budget && (
                      <div className="mt-2 text-sm font-medium text-blue-600">
                        💰 €{Number(lead.budget).toLocaleString()}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <div className={`text-right ${isOverdue ? 'text-red-600' : daysUntil === 0 ? 'text-yellow-600' : 'text-gray-600'}`}>
                      <div className="font-medium">
                        {getDaysText(daysUntil)}
                      </div>
                      {isOverdue && (
                        <div className="text-xs">Vėluoja!</div>
                      )}
                    </div>
                    
                    <div className="flex space-x-2">
                      <button className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm">
                        Susisiekti
                      </button>
                      <button className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm">
                        Perplanuoti
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
