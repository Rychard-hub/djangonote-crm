// LeadsView komponentas - lead'ų sąrašo view

import React, { useState } from 'react';
import type { Lead, LeadStatus } from '../types/crm';
import { useLeads } from '../hooks/useCRM';
import { LeadsTable } from '../components/LeadsTable';
import { LeadDetailView } from './LeadDetailView';

export function LeadsView() {
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const { leads, createLead, updateLeadStatus, deleteLead, refetch } = useLeads();

  const handleLeadSelect = (lead: Lead) => {
    setSelectedLead(lead);
  };

  const handleStatusChange = (leadId: number, status: LeadStatus) => {
    updateLeadStatus(leadId, status);
  };

  const handleDelete = (leadId: number) => {
    deleteLead(leadId);
    if (selectedLead?.id === leadId) {
      setSelectedLead(null);
    }
  };

  const handleRefresh = async () => {
    await refetch();
  };

  const handleBackToList = () => {
    setSelectedLead(null);
  };

  if (selectedLead) {
    return (
      <div>
        <button
          onClick={handleBackToList}
          className="mb-4 text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          ← Grįžti į lead'ų sąrašą
        </button>
        <LeadDetailView
          lead={selectedLead}
          onBack={handleBackToList}
          onUpdate={handleRefresh}
        />
      </div>
    );
  }

  return (
    <LeadsTable
      leads={leads}
      onLeadSelect={handleLeadSelect}
      onStatusChange={handleStatusChange}
      onDelete={handleDelete}
      onRefresh={handleRefresh}
    />
  );
}
