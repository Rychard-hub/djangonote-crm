// Navigation komponentas skybridge_crm

import React from 'react';

export type NavigationView = 'dashboard' | 'leads' | 'lead-detail' | 'followups' | 'pipeline' | 'settings';

interface NavigationProps {
  currentView: NavigationView;
  onViewChange: (view: NavigationView) => void;
  leadsCount?: number;
}

export function Navigation({ currentView, onViewChange, leadsCount = 0 }: NavigationProps) {
  const navItems = [
    { key: 'dashboard' as NavigationView, label: 'Dashboard', icon: '📊' },
    { key: 'leads' as NavigationView, label: 'Lead\'ai', icon: '👥', count: leadsCount },
    { key: 'followups' as NavigationView, label: 'Follow-up', icon: '📅' },
    { key: 'pipeline' as NavigationView, label: 'Pipeline', icon: '🔄' },
    { key: 'settings' as NavigationView, label: 'Nustatymai', icon: '⚙️' },
  ];

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-gray-900">🏢 Freelancer CRM</h1>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navItems.map((item) => (
                <button
                  key={item.key}
                  onClick={() => onViewChange(item.key)}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    currentView === item.key
                      ? 'border-blue-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                  {item.count !== undefined && (
                    <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                      {item.count}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center">
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 mr-4"
              onClick={() => onViewChange('leads')}
            >
              + Pridėti Lead'ą
            </button>
            <button className="text-gray-500 hover:text-gray-700 text-sm font-medium">
              Atsijungti
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
