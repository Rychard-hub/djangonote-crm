import React, { useState } from 'react';
import type { Lead, Comment, Task } from '../types/crm';

interface LeadDetailViewProps {
  lead?: Lead;
  comments?: Comment[];
  tasks?: Task[];
  onBack?: () => void;
  onUpdate?: () => void;
}

export const LeadDetailView: React.FC<LeadDetailViewProps> = ({ 
  lead, 
  comments = [], 
  tasks = [],
  onBack,
  onUpdate
}) => {
  const [activeTab, setActiveTab] = useState<'details' | 'comments' | 'tasks'>('details');
  const [newComment, setNewComment] = useState('');
  const [newTask, setNewTask] = useState('');

  if (!lead) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const statusColors = {
    new: 'bg-blue-100 text-blue-800',
    contacted: 'bg-yellow-100 text-yellow-800',
    proposal: 'bg-purple-100 text-purple-800',
    won: 'bg-green-100 text-green-800',
    lost: 'bg-red-100 text-red-800',
  };

  const statusLabels = {
    new: 'Naujas',
    contacted: 'Susisiekti',
    proposal: 'Pasiūlymas',
    won: 'Laimėtas',
    lost: 'Prarastas',
  };

  const commentKindColors = {
    note: 'bg-gray-100 text-gray-800',
    call: 'bg-blue-100 text-blue-800',
    email: 'bg-green-100 text-green-800',
    message: 'bg-purple-100 text-purple-800',
  };

  const commentKindLabels = {
    note: 'Pastaba',
    call: 'Skambutis',
    email: 'El. laiškas',
    message: 'Žinutė',
  };

  const completedTasks = tasks.filter(task => task.completed);
  const pendingTasks = tasks.filter(task => !task.completed);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{lead.name}</h1>
          {lead.company && (
            <p className="text-lg text-gray-600 mt-1">{lead.company}</p>
          )}
          <div className="mt-2 flex items-center space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[lead.status]}`}>
              {statusLabels[lead.status]}
            </span>
            {lead.budget && (
              <span className="text-lg font-semibold text-gray-900">
                €{lead.budget.toLocaleString()}
              </span>
            )}
          </div>
        </div>
        <div className="flex space-x-3">
          <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
            Redaguoti
          </button>
          <button className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
            Ištrinti
          </button>
        </div>
      </div>

      {/* Contact Information */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Kontaktinė informacija</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">El. paštas</label>
            <div className="mt-1 text-gray-900">{lead.email || '—'}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Telefonas</label>
            <div className="mt-1 text-gray-900">{lead.phone || '—'}</div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Paskutinis kontaktas</label>
            <div className="mt-1 text-gray-900">
              {lead.last_contacted ? new Date(lead.last_contacted).toLocaleDateString('lt-LT') : '—'}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Kitas follow-up</label>
            <div className="mt-1 text-gray-900">
              {lead.next_follow_up ? new Date(lead.next_follow_up).toLocaleDateString('lt-LT') : '—'}
            </div>
          </div>
        </div>
        {lead.notes && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700">Pastabos</label>
            <div className="mt-1 text-gray-900 whitespace-pre-wrap">{lead.notes}</div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b">
          <nav className="flex space-x-8 px-6">
            {[
              { key: 'details', label: 'Informacija', count: null },
              { key: 'comments', label: 'Komentarai', count: comments.length },
              { key: 'tasks', label: 'Užduotys', count: tasks.length },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
                {tab.count !== null && (
                  <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Details Tab */}
          {activeTab === 'details' && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Sukurta:</span>
                  <span className="ml-2 text-gray-900">
                    {new Date(lead.created_at).toLocaleString('lt-LT')}
                  </span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Atnaujinta:</span>
                  <span className="ml-2 text-gray-900">
                    {new Date(lead.updated_at).toLocaleString('lt-LT')}
                  </span>
                </div>
              </div>
              
              {/* Quick Actions */}
              <div className="border-t pt-4">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Greiti veiksmai</h3>
                <div className="flex flex-wrap gap-3">
                  <button className="bg-green-500 text-white px-3 py-2 rounded-lg hover:bg-green-600 transition-colors text-sm">
                    📞 Susisiekti
                  </button>
                  <button className="bg-blue-500 text-white px-3 py-2 rounded-lg hover:bg-blue-600 transition-colors text-sm">
                    📧 Siųsti laišką
                  </button>
                  <button className="bg-purple-500 text-white px-3 py-2 rounded-lg hover:bg-purple-600 transition-colors text-sm">
                    📋 Pasiūlymas
                  </button>
                  <button className="bg-orange-500 text-white px-3 py-2 rounded-lg hover:bg-orange-600 transition-colors text-sm">
                    📅 Planuoti follow-up
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Comments Tab */}
          {activeTab === 'comments' && (
            <div className="space-y-4">
              {/* Add Comment */}
              <div className="border rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-3">Pridėti komentarą</h3>
                <div className="space-y-3">
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Rašykite komentarą..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <div className="flex justify-between items-center">
                    <select className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                      <option value="note">Pastaba</option>
                      <option value="call">Skambutis</option>
                      <option value="email">El. laiškas</option>
                      <option value="message">Žinutė</option>
                    </select>
                    <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                    Pridėti
                  </button>
                </div>
              </div>
            </div>

          {/* Comments List */}
          {comments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">💬</div>
              <div>Komentarų dar nėra</div>
            </div>
          ) : (
            <div className="space-y-4">
              {comments.map((comment) => (
                <div key={comment.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">{comment.author}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${commentKindColors[comment.kind]}`}>
                        {commentKindLabels[comment.kind]}
                      </span>
                    </div>
                    <span className="text-sm text-gray-500">
                      {new Date(comment.created_at).toLocaleString('lt-LT')}
                    </span>
                  </div>
                  <div className="text-gray-900 whitespace-pre-wrap">{comment.body}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tasks Tab */}
      {activeTab === 'tasks' && (
        <div className="space-y-4">
          {/* Add Task */}
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Pridėti užduotį</h3>
            <div className="space-y-3">
              <input
                type="text"
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                placeholder="Užduoties pavadinimas..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
                Pridėti užduotį
              </button>
            </div>
          </div>

          {/* Tasks Lists */}
          {tasks.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">✅</div>
              <div>Užduočių dar nėra</div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Pending Tasks */}
              {pendingTasks.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Laukiančios užduotys ({pendingTasks.length})</h4>
                  <div className="space-y-2">
                    {pendingTasks.map((task) => (
                      <div key={task.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                          <span className="text-gray-900">{task.title}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">
                            {new Date(task.created_at).toLocaleDateString('lt-LT')}
                          </span>
                          <button className="text-red-600 hover:text-red-800 text-sm">
                            Ištrinti
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Completed Tasks */}
              {completedTasks.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Atliktos užduotys ({completedTasks.length})</h4>
                  <div className="space-y-2">
                    {completedTasks.map((task) => (
                      <div key={task.id} className="flex items-center justify-between p-3 border rounded-lg opacity-60">
                        <div className="flex items-center space-x-3">
                          <input type="checkbox" checked className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" readOnly />
                          <span className="text-gray-700 line-through">{task.title}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-gray-500">
                            {new Date(task.created_at).toLocaleDateString('lt-LT')}
                          </span>
                          <button className="text-red-600 hover:text-red-800 text-sm">
                            Ištrinti
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      </div>
      </div>
    </div>
  );
};
