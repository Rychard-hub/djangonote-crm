import React, { useState } from 'react';
import { InvitationModal } from './InvitationModal';
import { crmApi } from '../utils/api';

interface HeaderProps {
  currentView: string;
  onNavigate: (view: string) => void;
  isAuthenticated: boolean;
  onLogout: () => void;
  user?: {
    name?: string;
    email?: string;
  };
}

export const Header: React.FC<HeaderProps> = ({
  currentView,
  onNavigate,
  isAuthenticated,
  onLogout,
  user
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isInvitationModalOpen, setIsInvitationModalOpen] = useState(false);

  const navigationItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: '📊',
      description: 'Statistika ir apžvalga'
    },
    {
      id: 'leads',
      label: 'Lead\'ai',
      icon: '👥',
      description: 'Klientų valdymas'
    },
    {
      id: 'followup',
      label: 'Follow-up',
      icon: '📅',
      description: 'Susitikimai ir priminimai'
    },
    {
      id: 'pipeline',
      label: 'Pipeline',
      icon: '🔄',
      description: 'Pardavimų procesas'
    },
    {
      id: 'settings',
      label: 'Nustatymai',
      icon: '⚙️',
      description: 'Sistemos nustatymai'
    }
  ];

  const handleNavigation = (view: string) => {
    onNavigate(view);
    setIsMobileMenuOpen(false);
  };

  const handleSendInvitation = async (email: string) => {
    return crmApi.sendInvitation(email);
  };

  const isActive = (view: string) => {
    return currentView === view;
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-bold text-gray-900 flex items-center">
                <span className="text-blue-600 mr-2">🏢</span>
                Freelancer CRM
              </h1>
            </div>
          </div>

          {/* Desktop Navigation */}
          {isAuthenticated && (
            <nav className="hidden md:flex space-x-1">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavigation(item.id)}
                  className={`
                    px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200
                    flex items-center space-x-2
                    ${isActive(item.id)
                      ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                  title={item.description}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              ))}
            </nav>
          )}

          {/* User Menu */}
          {isAuthenticated && (
            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                  {user?.name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.name || user?.email || 'Vartotojas'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user?.email || 'user@example.com'}
                  </p>
                </div>
              </div>
              
              <button
                onClick={() => setIsInvitationModalOpen(true)}
                className="bg-blue-600 text-white px-3 py-2 rounded-md hover:bg-blue-700 transition-colors duration-200 text-sm font-medium"
                title="Siųsti kvietimą"
              >
                📧 Sukurti naują paskyrą
              </button>
              
              <button
                onClick={onLogout}
                className="text-gray-500 hover:text-gray-700 transition-colors duration-200"
                title="Atsijungti"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          )}

          {/* Mobile menu button */}
          {isAuthenticated && (
            <div className="md:hidden">
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="text-gray-500 hover:text-gray-700 focus:outline-none focus:text-gray-700"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {isMobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          )}
        </div>

        {/* Mobile Navigation */}
        {isAuthenticated && isMobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavigation(item.id)}
                  className={`
                    w-full text-left px-3 py-2 rounded-md text-base font-medium transition-colors duration-200
                    flex items-center space-x-3
                    ${isActive(item.id)
                      ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <span className="text-xl">{item.icon}</span>
                  <div>
                    <div>{item.label}</div>
                    <div className="text-xs text-gray-500">{item.description}</div>
                  </div>
                </button>
              ))}
              
              {/* Mobile User Info */}
              <div className="border-t border-gray-200 pt-4 mt-4">
                <div className="flex items-center space-x-3 px-3 py-2">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                    {user?.name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {user?.name || user?.email || 'Vartotojas'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {user?.email || 'user@example.com'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={onLogout}
                  className="w-full text-left px-3 py-2 text-red-600 hover:bg-red-50 rounded-md transition-colors duration-200 flex items-center space-x-3"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span>Atsijungti</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Invitation Modal */}
      <InvitationModal
        isOpen={isInvitationModalOpen}
        onClose={() => setIsInvitationModalOpen(false)}
        onSendInvitation={handleSendInvitation}
      />
    </header>
  );
};
