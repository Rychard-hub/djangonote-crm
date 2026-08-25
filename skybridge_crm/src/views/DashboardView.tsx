import React from 'react';
import { useDashboard } from '../hooks/useCRM';

export const DashboardView: React.FC = () => {
  const { stats, loading, error } = useDashboard();

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="text-red-800">
            <strong>Klaida:</strong> {error}
          </div>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const statusCards = [
    { label: 'Nauji', value: stats.new_leads, color: 'bg-blue-500', status: 'new' },
    { label: 'Susisiekti', value: stats.contacted_leads, color: 'bg-yellow-500', status: 'contacted' },
    { label: 'Pasiūlymas', value: stats.proposal_leads, color: 'bg-purple-500', status: 'proposal' },
    { label: 'Laimėti', value: stats.won_leads, color: 'bg-green-500', status: 'won' },
    { label: 'Prarasti', value: stats.lost_leads, color: 'bg-red-500', status: 'lost' },
  ];

  const followupCards = [
    { label: 'Šiandien', value: stats.today_followups, color: 'bg-orange-500', icon: '📅' },
    { label: 'Vėluojantys', value: stats.overdue_followups, color: 'bg-red-600', icon: '⚠️' },
  ];

  const budgetCards = [
    { label: 'Visas biudžetas', value: stats.total_budget, color: 'bg-indigo-500', format: 'currency' },
    { label: 'Laimėtas biudžetas', value: stats.won_budget, color: 'bg-green-600', format: 'currency' },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">CRM Dashboard</h1>
        <p className="text-gray-600 mt-2">Viso lead'ų: {stats.total_leads}</p>
      </div>

      {/* Lead Status Overview */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Lead'ų statusai</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {statusCards.map((card) => (
            <div key={card.status} className="bg-white rounded-lg shadow p-4 border-l-4 border-gray-200 hover:shadow-md transition-shadow">
              <div className={`w-3 h-3 ${card.color} rounded-full mb-2`}></div>
              <div className="text-2xl font-bold text-gray-900">{card.value}</div>
              <div className="text-sm text-gray-600">{card.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Follow-ups */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Follow-up'ai</h2>
        <div className="grid grid-cols-2 gap-4">
          {followupCards.map((card, index) => (
            <div key={index} className={`${card.color} text-white rounded-lg p-4 shadow hover:shadow-md transition-shadow`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-2xl font-bold">{card.value}</div>
                  <div className="text-sm opacity-90">{card.label}</div>
                </div>
                <div className="text-2xl">{card.icon}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Budget Overview */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Biudžeto apžvalga</h2>
        <div className="grid grid-cols-2 gap-4">
          {budgetCards.map((card, index) => (
            <div key={index} className={`${card.color} text-white rounded-lg p-4 shadow hover:shadow-md transition-shadow`}>
              <div className="text-2xl font-bold">
                {card.format === 'currency' ? `€${card.value?.toLocaleString() || 0}` : card.value}
              </div>
              <div className="text-sm opacity-90">{card.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Greiti veiksmai</h2>
        <div className="flex flex-wrap gap-3">
          <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
            ➕ Sukurti lead'ą
          </button>
          <button className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition-colors">
            📋 Peržiūrėti lead'us
          </button>
          <button className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors">
            📅 Šiandien follow-up'ai
          </button>
          <button className="bg-purple-500 text-white px-4 py-2 rounded-lg hover:bg-purple-600 transition-colors">
            📊 Pipeline
          </button>
        </div>
      </div>
    </div>
  );
};
