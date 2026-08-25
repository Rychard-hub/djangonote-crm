import React, { useState } from 'react';

interface InvitationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSendInvitation: (email: string) => Promise<{ success: boolean; message: string; invitation_link?: string }>;
}

export const InvitationModal: React.FC<InvitationModalProps> = ({
  isOpen,
  onClose,
  onSendInvitation
}) => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string; invitation_link?: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email.trim()) {
      setResult({ success: false, message: 'Įveskite el. pašto adresą' });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await onSendInvitation(email);
      setResult(response);
      
      if (response.success) {
        setEmail('');
        setTimeout(() => {
          onClose();
        }, 3000);
      }
    } catch (error) {
      setResult({ 
        success: false, 
        message: error instanceof Error ? error.message : 'Klaida siunčiant kvietimą' 
      });
    } finally {
      setLoading(false);
    }
  };

  const copyInvitationLink = () => {
    if (result?.invitation_link) {
      navigator.clipboard.writeText(result.invitation_link);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              📧 Siųsti kvietimą
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {!result ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  El. pašto adresas
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="vardas@pavyzdys.lt"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Įveskite el. paštą, į kurį norite siųsti kvietimą
                </p>
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Atšaukti
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {loading ? 'Siunčiama...' : 'Siųsti kvietimą'}
                </button>
              </div>
            </form>
          ) : (
            <div className={`space-y-4 ${result.success ? 'text-green-600' : 'text-red-600'}`}>
              <div className="text-center">
                <div className="text-2xl mb-2">
                  {result.success ? '✅' : '❌'}
                </div>
                <p className="font-medium">
                  {result.success ? 'Kvietimas išsiųstas!' : 'Klaida!'}
                </p>
                <p className="text-sm mt-1">
                  {result.message}
                </p>
              </div>

              {result.success && result.invitation_link && (
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Kvietimo nuoroda:
                  </p>
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={result.invitation_link}
                      readOnly
                      className="flex-1 text-xs bg-white border border-gray-300 rounded px-2 py-1"
                    />
                    <button
                      onClick={copyInvitationLink}
                      className="px-2 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                    >
                      📋 Kopijuoti
                    </button>
                  </div>
                </div>
              )}

              {!result.success && (
                <button
                  onClick={() => setResult(null)}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Bandyti dar kartą
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
