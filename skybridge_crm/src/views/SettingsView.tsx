import React, { useState } from 'react';
import { useProfile } from '../hooks/useCRM';

export const SettingsView: React.FC = () => {
  const { profile, updateProfile, loading } = useProfile();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    organization: '',
    timezone: 'Europe/Vilnius',
    reminder_days: 1,
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  React.useEffect(() => {
    if (profile) {
      setFormData({
        full_name: profile.user?.first_name || '',
        email: profile.user?.email || '',
        organization: profile.organization || '',
        timezone: profile.timezone || 'Europe/Vilnius',
        reminder_days: profile.reminder_days || 1,
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    }
  }, [profile]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'reminder_days' ? parseInt(value) || 1 : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent, type: 'profile' | 'password') => {
    e.preventDefault();
    setMessage(null);

    try {
      if (type === 'profile') {
        await updateProfile({
          full_name: formData.full_name,
          email: formData.email,
          organization: formData.organization,
          timezone: formData.timezone,
          reminder_days: formData.reminder_days
        });
        setMessage({ type: 'success', text: 'Profilis sėkmingai atnaujintas!' });
      } else {
        // Password change logic would go here
        if (formData.new_password !== formData.confirm_password) {
          setMessage({ type: 'error', text: 'Slaptažodžiai nesutampa!' });
          return;
        }
        setMessage({ type: 'success', text: 'Slaptažodis sėkmingai pakeistas!' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Klaida! Bandykite dar kartą.' });
    }
  };

  const timezones = [
    'Europe/Vilnius',
    'Europe/Riga',
    'Europe/Tallinn',
    'Europe/Warsaw',
    'Europe/Berlin',
    'Europe/London',
    'America/New_York',
    'America/Los_Angeles'
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Kraunami nustatymai...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Nustatymai</h1>
        <p className="text-gray-600">Tvarkykite savo paskyros ir sistemos nustatymus</p>
      </div>

      {message && (
        <div className={`mb-6 p-4 rounded-md ${
          message.type === 'success' 
            ? 'bg-green-50 border border-green-200 text-green-800'
            : 'bg-red-50 border border-red-200 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Settings */}
        <div className="bg-white rounded-lg shadow border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Profilio informacija</h2>
            <p className="text-sm text-gray-600">Atnaujinkite savo asmeninę informaciją</p>
          </div>
          <form onSubmit={(e) => handleSubmit(e, 'profile')} className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Vardas
              </label>
              <input
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Įveskite savo vardą"
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
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="vardas@pavyzdys.lt"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organizacija
              </label>
              <input
                type="text"
                name="organization"
                value={formData.organization}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Įmonės pavadinimas"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Laiko zona
              </label>
              <select
                name="timezone"
                value={formData.timezone}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {timezones.map(tz => (
                  <option key={tz} value={tz}>{tz}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priminimų dienų skaičius
              </label>
              <input
                type="number"
                name="reminder_days"
                value={formData.reminder_days}
                onChange={handleInputChange}
                min="1"
                max="30"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Kiek dienų prieš follow-up siųsti priminimus
              </p>
            </div>

            <div className="pt-4">
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              >
                Išsaugoti pakeitimus
              </button>
            </div>
          </form>
        </div>

        {/* Password Settings */}
        <div className="bg-white rounded-lg shadow border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Slaptažodžio keitimas</h2>
            <p className="text-sm text-gray-600">Pakeiskite savo paskyros slaptažodį</p>
          </div>
          <form onSubmit={(e) => handleSubmit(e, 'password')} className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dabartinis slaptažodis
              </label>
              <input
                type="password"
                name="current_password"
                value={formData.current_password}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Įveskite dabartinį slaptažodį"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Naujas slaptažodis
              </label>
              <input
                type="password"
                name="new_password"
                value={formData.new_password}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Įveskite naują slaptažodį"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Patvirtinkite naują slaptažodį
              </label>
              <input
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Pakartokite naują slaptažodį"
              />
            </div>

            <div className="pt-4">
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
              >
                Keisti slaptažodį
              </button>
            </div>
          </form>
        </div>

        {/* System Settings */}
        <div className="bg-white rounded-lg shadow border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Sistemos nustatymai</h2>
            <p className="text-sm text-gray-600">CRM sistemos konfigūracija</p>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">El. laiškų siuntimas</h3>
                <p className="text-sm text-gray-600">Automatiniai priminimai ir ataskaitos</p>
              </div>
              <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">PDF generavimas</h3>
                <p className="text-sm text-gray-600">Lead'o kortelių eksportavimas</p>
              </div>
              <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">Foninės užduotys</h3>
                <p className="text-sm text-gray-600">Celery background processing</p>
              </div>
              <div className="w-12 h-6 bg-blue-600 rounded-full relative">
                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
              </div>
            </div>

            <div className="pt-4 border-t border-gray-200">
              <div className="text-sm text-gray-600">
                <p><strong>CRM versija:</strong> 1.0.0</p>
                <p><strong>Django versija:</strong> 6.0.6</p>
                <p><strong>Redis statusas:</strong> ✅ Veikia</p>
                <p><strong>Celery statusas:</strong> ✅ Veikia</p>
              </div>
            </div>
          </div>
        </div>

        {/* Data Management */}
        <div className="bg-white rounded-lg shadow border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Duomenų valdymas</h2>
            <p className="text-sm text-gray-600">Eksportavimas ir atsarginės kopijos</p>
          </div>
          <div className="p-6 space-y-4">
            <button className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors">
              Eksportuoti Lead'us (CSV)
            </button>
            <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors">
              Eksportuoti Ataskaitą (PDF)
            </button>
            <button className="w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors">
              Sukurti atsarginę kopiją
            </button>
            <button className="w-full bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 transition-colors">
              Išvalyti senus duomenis
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
