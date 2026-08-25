import React, { useState, useEffect } from 'react';
import { crmApi } from '../utils/api';

export const InviteView: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Gauname URL parametrus
  const getUrlParams = () => {
    const params = new URLSearchParams(window.location.search);
    return {
      uid: params.get('uid'),
      token: params.get('token')
    };
  };

  const { uid, token } = getUrlParams();

  useEffect(() => {
    if (!uid || !token) {
      setError('Netinkamas kvietimo nuorodos formatas');
    }
  }, [uid, token]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (formData.password !== formData.confirmPassword) {
      setError('Slaptažodžiai nesutampa');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Slaptažodis turi būti bent 6 simbolių ilgio');
      setLoading(false);
      return;
    }

    try {
      // Simuliuojame registraciją su kvietimo token'u
      // Realiai čia reikėtų Django endpoint'o, kuris patikrintų token'ą ir sukurtų vartotoją
      const response = await crmApi.login({
        username: formData.email,
        password: formData.password
      });

      if (response) {
        setSuccess(true);
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 2000);
      }
    } catch (error) {
      setError('Klaida kuriant paskyrą. Bandykite dar kartą.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-4xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Paskyra sukurta!
          </h2>
          <p className="text-gray-600 mb-4">
            Sėkmingai prisijungėte prie Freelancer CRM
          </p>
          <p className="text-sm text-gray-500">
            Perkeliate į dashboard...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="text-4xl mb-4">🏢</div>
          <h1 className="text-2xl font-bold text-gray-900">
            Sukurk naują paskyrą
          </h1>
          <p className="text-gray-600 mt-2">
            Jūs buvote pakviesti prisijungti prie Freelancer CRM
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Vardas
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Jūsų vardas"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              El. paštas
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="el.pastas@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Slaptažodis
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              Bent 6 simbolių ilgio
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Patvirtinkite slaptažodį
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="••••••••"
              required
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="terms"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              required
            />
            <label htmlFor="terms" className="ml-2 block text-sm text-gray-900">
              Sutinku su <a href="#" className="text-blue-600 hover:text-blue-500">naudojimo sąlygomis</a>
            </label>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Kuriama...' : 'Sukurti paskyrą'}
            </button>
          </div>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Jau turite paskyrą?{' '}
              <button
                type="button"
                onClick={() => window.location.href = '/'}
                className="text-blue-600 hover:text-blue-500 font-medium"
              >
                Prisijunkite
              </button>
            </p>
          </div>
        </form>

        {uid && token && (
          <div className="mt-6 p-4 bg-gray-50 rounded-md">
            <p className="text-xs text-gray-500">
              Kvietimo ID: {uid}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
