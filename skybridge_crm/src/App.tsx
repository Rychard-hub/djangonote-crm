// Pagrindinis Skybridge CRM aplikacijos komponentas

import React, { useState } from 'react';
import { Header } from './components/Header';
import { DashboardView } from './views/DashboardView';
import { LeadsView } from './views/LeadsView';
import { FollowUpView } from './views/FollowUpView';
import { PipelineView } from './views/PipelineView';
import { SettingsView } from './views/SettingsView';
import { InviteView } from './views/InviteView';
import { RegistrationView } from './views/RegistrationView';
import { EmailVerificationView } from './views/EmailVerificationView';
import { AuthView } from './views/AuthView';
import { SignupView } from './views/SignupView';
import { useAuth, useLeads, useProfile } from './hooks/useCRM';

export function App() {
  const [currentView, setCurrentView] = useState<string>('dashboard');
  const [authMode, setAuthMode] = useState<'login' | 'signup'>('login');
  const { isAuthenticated, login, logout, signup } = useAuth();
  const { leads } = useLeads();
  const { profile } = useProfile();

  // Tikriname, ar tai kvietimo nuoroda
  const checkInvitationLink = () => {
    const params = new URLSearchParams(window.location.search);
    const uid = params.get('uid');
    const token = params.get('token');
    return uid && token;
  };

  // Tikriname, ar tai el. pašto patvirtinimo nuoroda
  const checkEmailVerification = () => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    return token;
  };

  // Tikriname, ar tai registracijos puslapis
  const checkRegistration = () => {
    return window.location.pathname === '/register';
  };

  // Tikriname, ar tai el. pašto patvirtinimo puslapis
  const checkEmailVerificationPage = () => {
    return window.location.pathname === '/verify-email';
  };

  // Jei tai el. pašto patvirtinimo nuoroda, rodom EmailVerificationView
  if (checkEmailVerification() || checkEmailVerificationPage()) {
    return <EmailVerificationView />;
  }

  // Jei tai registracijos puslapis, rodom RegistrationView
  if (checkRegistration()) {
    return <RegistrationView />;
  }

  // Jei tai kvietimo nuoroda, rodom InviteView
  if (checkInvitationLink()) {
    return <InviteView />;
  }

  if (!isAuthenticated) {
    if (authMode === 'login') {
      return (
        <AuthView 
          onLogin={login} 
          onShowSignup={() => setAuthMode('signup')} 
        />
      );
    } else {
      return (
        <SignupView 
          onSignup={signup} 
          onShowLogin={() => setAuthMode('login')} 
        />
      );
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header 
        currentView={currentView}
        onNavigate={setCurrentView}
        isAuthenticated={isAuthenticated}
        onLogout={logout}
        user={{
          name: 'Test User',
          email: 'test@example.com'
        }}
      />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {currentView === 'dashboard' && <DashboardView />}
        {currentView === 'leads' && <LeadsView />}
        {currentView === 'lead-detail' && <LeadsView />}
        {currentView === 'followup' && <FollowUpView />}
        {currentView === 'pipeline' && <PipelineView />}
        {currentView === 'settings' && <SettingsView />}
      </main>
    </div>
  );
}
