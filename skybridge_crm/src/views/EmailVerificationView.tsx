import React, { useState, useEffect } from 'react';

export const EmailVerificationView: React.FC = () => {
  const [token, setToken] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    // Gauname token iš URL
    const urlParams = new URLSearchParams(window.location.search);
    const urlToken = urlParams.get('token') || '';
    
    // Jei token yra URL parametre, automatiškai bandom patvirtinti
    if (urlToken) {
      setToken(urlToken);
      handleVerifyEmail(urlToken);
    }
  }, []);

  const handleVerifyEmail = async (verificationToken?: string) => {
    const tokenToUse = verificationToken || token;
    
    if (!tokenToUse) {
      setError('Token būtinas');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/verify-email/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: tokenToUse
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setSuccess(true);
      } else {
        setError(data.error || 'Patvirtinimas nepavyko');
      }
    } catch (error) {
      setError('Klaida siunčiant užklausą. Bandykite dar kartą.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleVerifyEmail();
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-4xl mb-4">✅</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            El. paštas patvirtintas!
          </h2>
          <p className="text-gray-600 mb-6">
            Jūsų paskyra sėkmingai aktyvuota. Dabar galite prisijungti prie CRM sistemos.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => window.location.href = '/'}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 transition-colors"
            >
              Prisijungti
            </button>
            <button
              onClick={() => window.location.href = '/dashboard'}
              className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 transition-colors"
            >
              Eiti į Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="text-4xl mb-4">🔐</div>
          <h1 className="text-2xl font-bold text-gray-900">
            Patvirtinkite el. paštą
          </h1>
          <p className="text-gray-600 mt-2">
            Įveskite patvirtinimo kodą, kurį gavote el. paštu
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="text-center py-8">
            <div className="text-2xl mb-4">⏳</div>
            <p className="text-gray-600">Patvirtinamas el. paštas...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Patvirtinimo kodas
              </label>
              <input
                type="text"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Įveskite patvirtinimo kodą"
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Kodą gavote el. paštu po registracijos
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <p className="text-sm text-blue-800">
                <strong>Informacija:</strong>
              </p>
              <ul className="text-sm text-blue-700 mt-2 space-y-1">
                <li>• Patvirtinimo kodas galios 24 valandas</li>
                <li>• Patikrinkite savo el. pašto aplanką "Spam"</li>
                <li>• Jei kodas nebeveikia, registruokitės iš naujo</li>
              </ul>
            </div>

            <div>
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
              >
                Patvirtinti el. paštą
              </button>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-600">
                Neradote kodą?{' '}
                <button
                  type="button"
                  onClick={() => window.location.href = '/register'}
                  className="text-blue-600 hover:text-blue-500 font-medium"
                >
                  Registruokitės iš naujo
                </button>
              </p>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
