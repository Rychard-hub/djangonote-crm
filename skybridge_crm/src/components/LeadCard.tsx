// LeadCard komponentas skirtas lead'o vaizdavimui Skybridge CRM

import React, { useState } from 'react';
import type { Lead, LeadStatus } from '../types/crm';
import { crmApi } from '../utils/api';

interface LeadCardProps {
  lead: Lead;
  onUpdate?: (lead: Lead) => void;
  onDelete?: (leadId: number) => void;
  onStatusChange?: (leadId: number, status: LeadStatus) => void;
  className?: string;
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

export function LeadCard({ 
  lead, 
  onUpdate, 
  onDelete, 
  onStatusChange, 
  className = '' 
}: LeadCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showStatusMenu, setShowStatusMenu] = useState(false);

  const handleStatusChange = async (newStatus: LeadStatus) => {
    try {
      await crmApi.updateLeadStatus(lead.id, { status: newStatus });
      setShowStatusMenu(false);
      onStatusChange?.(lead.id, newStatus);
    } catch (error) {
      console.error('Failed to update lead status:', error);
    }
  };

  const handleDelete = async () => {
    if (confirm('Ar tikrai norite ištrinti šį lead\'ą?')) {
      try {
        await crmApi.deleteLead(lead.id);
        onDelete?.(lead.id);
      } catch (error) {
        console.error('Failed to delete lead:', error);
      }
    }
  };

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('lt-LT');
  };

  const formatBudget = (budget: string | null | undefined) => {
    if (!budget) return '-';
    return `€${parseFloat(budget).toLocaleString('lt-LT')}`;
  };

  return (
    <div className={`bg-white rounded-lg shadow-md border border-gray-200 p-4 hover:shadow-lg transition-shadow ${className}`}>
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{lead.name}</h3>
          {lead.company && (
            <p className="text-sm text-gray-600">{lead.company}</p>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[lead.status]}`}>
            {statusLabels[lead.status]}
          </span>
          <div className="relative">
            <button
              onClick={() => setShowStatusMenu(!showStatusMenu)}
              className="p-1 text-gray-400 hover:text-gray-600 rounded"
              title="Keisti statusą"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
            </button>
            
            {showStatusMenu && (
              <div className="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200">
                <div className="py-1">
                  {(Object.keys(statusColors) as LeadStatus[]).map((status) => (
                    <button
                      key={status}
                      onClick={() => handleStatusChange(status)}
                      className={`block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 ${
                        lead.status === status ? 'bg-gray-100 font-medium' : ''
                      }`}
                    >
                      <span className={`inline-block w-2 h-2 rounded-full mr-2 ${statusColors[status].split(' ')[0]}`}></span>
                      {statusLabels[status]}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Contact Info */}
      <div className="space-y-1 mb-3">
        {lead.email && (
          <div className="flex items-center text-sm text-gray-600">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            {lead.email}
          </div>
        )}
        {lead.phone && (
          <div className="flex items-center text-sm text-gray-600">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            {lead.phone}
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-3 text-sm">
        <div className="text-center">
          <div className="font-medium text-gray-900">{formatBudget(lead.budget)}</div>
          <div className="text-gray-500">Biudžetas</div>
        </div>
        <div className="text-center">
          <div className="font-medium text-gray-900">{lead.comments_count}</div>
          <div className="text-gray-500">Komentarai</div>
        </div>
        <div className="text-center">
          <div className="font-medium text-gray-900">{lead.completed_tasks_count}/{lead.tasks_count}</div>
          <div className="text-gray-500">Užduotys</div>
        </div>
      </div>

      {/* Dates */}
      <div className="flex justify-between text-xs text-gray-500 mb-3">
        <div>
          <span className="font-medium">Sukurtas:</span> {formatDate(lead.created_at)}
        </div>
        <div>
          <span className="font-medium">Follow-up:</span> {formatDate(lead.next_follow_up)}
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between items-center">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          {isExpanded ? 'Rodyti mažiau' : 'Rodyti daugiau'}
        </button>
        
        <div className="flex space-x-2">
          <button
            onClick={() => onUpdate?.(lead)}
            className="p-1 text-gray-400 hover:text-blue-600 rounded"
            title="Redaguoti"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            onClick={handleDelete}
            className="p-1 text-gray-400 hover:text-red-600 rounded"
            title="Ištrinti"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && lead.notes && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            <span className="font-medium">Pastabos:</span>
            <p className="mt-1 whitespace-pre-wrap">{lead.notes}</p>
          </div>
        </div>
      )}
    </div>
  );
}
