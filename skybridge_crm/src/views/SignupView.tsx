// SignupView komponentas - registracijos forma

import React, { useState } from 'react';

interface SignupViewProps {
  onSignup: (data: { username: string; email: string; password: string }) => Promise<boolean>;
  onShowLogin?: () => void;
}

export function SignupView({ onSignup, onShowLogin }: SignupViewProps) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Slaptažodžiai nesutampa');
      return;
    }

    // Validate password strength
    if (password.length < 6) {
      setError('Slaptažodis turi būti bent 6 simbolių ilgio');
      return;
    }

    setLoading(true);

    try {
      const success = await onSignup({
        username,
        email,
        password,
      });

      if (!success) {
        setError('Registracija nepavyko');
      }
    } catch (err) {
      setError('Registracijos klaida');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="text-center text-3xl font-extrabold text-gray-900">
          🏢 Freelancer CRM
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Sukurk naują paskyrą
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {/* Error Message */}
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-md p-4">
              <div className="text-sm text-red-800">{error}</div>
            </div>
          )}

          {/* Signup Form */}
          <form onSubmit={handleSignup} className="space-y-6">
            <div>
              <label htmlFor="signup-username" className="block text-sm font-medium text-gray-700">
                Vardas
              </label>
              <input
                id="signup-username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Jūsų vardas"
              />
            </div>

            <div>
              <label htmlFor="signup-email" className="block text-sm font-medium text-gray-700">
                El. paštas
              </label>
              <input
                id="signup-email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="el.pastas@example.com"
              />
            </div>

            <div>
              <label htmlFor="signup-password" className="block text-sm font-medium text-gray-700">
                Slaptažodis
              </label>
              <input
                id="signup-password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="signup-confirm-password" className="block text-sm font-medium text-gray-700">
                Patvirtinkite slaptažodį
              </label>
              <input
                id="signup-confirm-password"
                name="confirm-password"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="••••••••"
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Kuriama...' : 'Sukurti paskyrą'}
              </button>
            </div>
          </form>

          {/* Footer Links */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">arba</span>
              </div>
            </div>
            
            <div className="mt-6 text-center">
              <div className="text-sm text-gray-600">
                Jau turi paskyrą?{' '}
                {onShowLogin && (
                  <button
                    onClick={onShowLogin}
                    className="font-medium text-blue-600 hover:text-blue-500"
                  >
                    Prisijungti
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
