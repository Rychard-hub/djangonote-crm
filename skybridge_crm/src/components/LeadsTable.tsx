// LeadsTable komponentas - lead'ų sąrašas lentelės formatu

import React, { useState } from 'react';
import type { Lead, LeadStatus } from '../types/crm';
import { crmApi } from '../utils/api';

interface LeadsTableProps {
  leads: Lead[];
  onLeadSelect: (lead: Lead) => void;
  onStatusChange: (leadId: number, status: LeadStatus) => void;
  onDelete: (leadId: number) => void;
  onRefresh: () => void;
}

const statusColors: Record<LeadStatus, string> = {
  new: 'bg-blue-100 text-blue-800',
  contacted: 'bg-yellow-100 text-yellow-800',
  proposal: 'bg-purple-100 text-purple-800',
  won: 'bg-green-100 text-green-800',
  lost: 'bg-red-100 text-red-800',
};

const statusLabels: Record<LeadStatus, string> = {
  new: 'Naujas',
  contacted: 'Susisiektas',
  proposal: 'Pasiūlymas',
  won: 'Laimėtas',
  lost: 'Pralaimėtas',
};

export function LeadsTable({ leads, onLeadSelect, onStatusChange, onDelete, onRefresh }: LeadsTableProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<LeadStatus | ''>('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  const filteredLeads = leads.filter(lead => {
    const matchesSearch = !searchQuery || 
      lead.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (lead.company && lead.company.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (lead.email && lead.email.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesStatus = !statusFilter || lead.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('lt-LT');
  };

  const formatBudget = (budget: string | null | undefined) => {
    if (!budget) return '-';
    return `€${parseFloat(budget).toLocaleString('lt-LT')}`;
  };

  const handleCreateLead = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    
    try {
      await crmApi.createLead({
        name: formData.get('name') as string,
        company: formData.get('company') as string,
        email: formData.get('email') as string,
        phone: formData.get('phone') as string,
        status: formData.get('status') as LeadStatus,
        budget: parseFloat(formData.get('budget') as string) || undefined,
        notes: formData.get('notes') as string,
      });
      
      setShowCreateForm(false);
      onRefresh();
      const form = e.target as HTMLFormElement;
      form.reset();
    } catch (error) {
      console.error('Failed to create lead:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Toolbar */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Lead'ai</h2>
          <p className="text-gray-600">Visi jūsų lead'ai ({leads.length})</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
        >
          + Pridėti Lead'ą
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 items-center">
        <input
          type="search"
          placeholder="Paieška pagal vardą, įmonę, el. paštą"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as LeadStatus | '')}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Visi statusai</option>
          <option value="new">Naujas</option>
          <option value="contacted">Susisiektas</option>
          <option value="proposal">Pasiūlymas</option>
          <option value="won">Laimėtas</option>
          <option value="lost">Pralaimėtas</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Vardas / Įmonė
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Kontaktas
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Statusas
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Paskutinis kontaktas
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Kitas follow-up
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Biudžetas
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Veiksmai
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredLeads.map((lead) => (
              <tr key={lead.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{lead.name}</div>
                  <div className="text-sm text-gray-500">{lead.company || '-'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{lead.email || '-'}</div>
                  <div className="text-sm text-gray-500">{lead.phone || '-'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusColors[lead.status]}`}>
                    {statusLabels[lead.status]}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(lead.last_contacted)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatDate(lead.next_follow_up)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatBudget(lead.budget)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => onLeadSelect(lead)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    Peržiūrėti
                  </button>
                  <button
                    onClick={() => onDelete(lead.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Ištrinti
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {filteredLeads.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500">Nerasta lead'ų</div>
          </div>
        )}
      </div>

      {/* Create Lead Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Sukurti naują lead'ą</h3>
            
            <form onSubmit={handleCreateLead} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Pavadinimas *</label>
                <input
                  name="name"
                  type="text"
                  required
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Įmonė</label>
                <input
                  name="company"
                  type="text"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">El. paštas</label>
                <input
                  name="email"
                  type="email"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Telefonas</label>
                <input
                  name="phone"
                  type="tel"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Statusas</label>
                <select
                  name="status"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  <option value="new">Naujas</option>
                  <option value="contacted">Susisiektas</option>
                  <option value="proposal">Pasiūlymas</option>
                  <option value="won">Laimėtas</option>
                  <option value="lost">Pralaimėtas</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Biudžetas</label>
                <input
                  name="budget"
                  type="number"
                  step="0.01"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Pastabos</label>
                <textarea
                  name="notes"
                  rows={3}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Atšaukti
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Sukurti
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
