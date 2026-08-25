// Dashboard komponentas skirtas CRM statistikos ir follow-up'ų vaizdavimui

import { useDashboard } from '../hooks/useCRM';

interface DashboardProps {
  className?: string;
}

export function Dashboard({ className = '' }: DashboardProps) {
  const { stats, upcomingFollowups, overdueFollowups, loading, error } = useDashboard();

  const formatCurrency = (amount: number) => {
    return `€${amount.toLocaleString('lt-LT')}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('lt-LT');
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

  if (!stats) {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-4 ${className}`}>
        <div className="text-gray-600">Nėra duomenų</div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Viso Lead'ų</div>
          <div className="text-3xl font-bold text-gray-900">{stats.total_leads}</div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Nauji</div>
          <div className="text-3xl font-bold text-blue-600">{stats.new_leads}</div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Laimėti</div>
          <div className="text-3xl font-bold text-green-600">{stats.won_leads}</div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm font-medium text-gray-600">Biudžetas</div>
          <div className="text-3xl font-bold text-purple-600">{formatCurrency(stats.total_budget)}</div>
        </div>
      </div>

      {/* Status Overview */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Statusų apžvalga</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.new_leads}</div>
            <div className="text-sm text-gray-600">Nauji</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{stats.contacted_leads}</div>
            <div className="text-sm text-gray-600">Susisiekti</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{stats.proposal_leads}</div>
            <div className="text-sm text-gray-600">Pasiūlymai</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.won_leads}</div>
            <div className="text-sm text-gray-600">Laimėti</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{stats.lost_leads}</div>
            <div className="text-sm text-gray-600">Pralaimėti</div>
          </div>
        </div>
      </div>

      {/* Financial Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Finansinė apžvalga</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Visas biudžetas:</span>
              <span className="font-semibold">{formatCurrency(stats.total_budget)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Laimėtas biudžetas:</span>
              <span className="font-semibold text-green-600">{formatCurrency(stats.won_budget)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Konversija:</span>
              <span className="font-semibold">
                {stats.total_leads > 0 
                  ? `${((stats.won_leads / stats.total_leads) * 100).toFixed(1)}%`
                  : '0%'
                }
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Follow-up'ai</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Šiandien:</span>
              <span className="font-semibold text-blue-600">{stats.today_followups}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Vėluojantys:</span>
              <span className="font-semibold text-red-600">{stats.overdue_followups}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Follow-up Lists */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Follow-ups */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Artėjantys Follow-up'ai ({upcomingFollowups.length})
          </h2>
          {upcomingFollowups.length > 0 ? (
            <div className="space-y-3">
              {upcomingFollowups.slice(0, 5).map((lead) => (
                <div key={lead.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div>
                    <div className="font-medium text-gray-900">{lead.name}</div>
                    {lead.company && (
                      <div className="text-sm text-gray-600">{lead.company}</div>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-blue-600">
                      {lead.next_follow_up ? formatDate(lead.next_follow_up) : '-'}
                    </div>
                    <div className="text-xs text-gray-500">{lead.status_display}</div>
                  </div>
                </div>
              ))}
              {upcomingFollowups.length > 5 && (
                <div className="text-center text-sm text-gray-600">
                  Ir dar {upcomingFollowups.length - 5}...
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-600 text-center py-4">Nėra artėjančių follow-up'ų</div>
          )}
        </div>

        {/* Overdue Follow-ups */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Vėluojantys Follow-up'ai ({overdueFollowups.length})
          </h2>
          {overdueFollowups.length > 0 ? (
            <div className="space-y-3">
              {overdueFollowups.slice(0, 5).map((lead) => (
                <div key={lead.id} className="flex items-center justify-between p-3 bg-red-50 rounded border border-red-200">
                  <div>
                    <div className="font-medium text-gray-900">{lead.name}</div>
                    {lead.company && (
                      <div className="text-sm text-gray-600">{lead.company}</div>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-red-600">
                      {lead.next_follow_up ? formatDate(lead.next_follow_up) : '-'}
                    </div>
                    <div className="text-xs text-gray-500">{lead.status_display}</div>
                  </div>
                </div>
              ))}
              {overdueFollowups.length > 5 && (
                <div className="text-center text-sm text-gray-600">
                  Ir dar {overdueFollowups.length - 5}...
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-600 text-center py-4">Nėra vėluojančių follow-up'ų</div>
          )}
        </div>
      </div>
    </div>
  );
}
