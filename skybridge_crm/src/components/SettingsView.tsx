// SettingsView komponentas - nustatymų valdymas

import React, { useState } from 'react';

interface SettingsViewProps {
  className?: string;
}

export function SettingsView({ className = '' }: SettingsViewProps) {
  const [activeTab, setActiveTab] = useState<'profile' | 'notifications' | 'api'>('profile');

  return (
    <div className={`space-y-6 ${className}`}>
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Nustatymai</h2>
        <p className="text-gray-600">CRM sistemos nustatymai</p>
      </div>

      {/* Settings Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { key: 'profile', label: 'Profilis' },
              { key: 'notifications', label: 'Pranešimai' },
              { key: 'api', label: 'API' },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Profile Settings */}
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Profilio nustatymai</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Vardas</label>
                    <input
                      type="text"
                      defaultValue="Test User"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">El. paštas</label>
                    <input
                      type="email"
                      defaultValue="test@example.com"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Telefonas</label>
                    <input
                      type="tel"
                      placeholder="+37060000000"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Įmonė</label>
                    <input
                      type="text"
                      placeholder="Jūsų įmonė"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Slaptažodžio keitimas</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Dabartinis slaptažodis</label>
                    <input
                      type="password"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Naujas slaptažodis</label>
                    <input
                      type="password"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Patvirtinkite naują slaptažodį</label>
                    <input
                      type="password"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
                  Išsaugoti pakeitimus
                </button>
              </div>
            </div>
          )}

          {/* Notification Settings */}
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Pranešimų nustatymai</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">Follow-up priminimai</div>
                      <div className="text-sm text-gray-500">Gaukite pranešimus apie artėjančius follow-up'us</div>
                    </div>
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">Naujų lead'ų pranešimai</div>
                      <div className="text-sm text-gray-500">Gaukite pranešimus apie naujus lead'us</div>
                    </div>
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">Statuso pakeitimai</div>
                      <div className="text-sm text-gray-500">Gaukite pranešimus kai lead'as pakeičia statusą</div>
                    </div>
                    <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">El. pašto pranešimai</div>
                      <div className="text-sm text-gray-500">Gaukite pranešimus ir el. paštu</div>
                    </div>
                    <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Pranešimų dažnis</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Follow-up priminimai</label>
                    <select className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                      <option>1 diena prieš</option>
                      <option>2 dienos prieš</option>
                      <option>3 dienos prieš</option>
                      <option>1 savaitė prieš</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Ataskaitų dažnis</label>
                    <select className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                      <option>Kasdien</option>
                      <option>Savaitėl</option>
                      <option>Mėnesį</option>
                      <option>Never</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
                  Išsaugoti nustatymus
                </button>
              </div>
            </div>
          )}

          {/* API Settings */}
          {activeTab === 'api' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">API nustatymai</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">API Endpoint</label>
                      <input
                        type="url"
                        defaultValue="http://127.0.0.1:8000"
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
                        readOnly
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">API versija</label>
                      <input
                        type="text"
                        defaultValue="v1"
                        className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
                        readOnly
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">API raktai</h3>
                <div className="space-y-4">
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="text-sm text-yellow-800">
                      <strong>Įspėjimas:</strong> API raktai leidžia prieigą prie jūsų CRM duomenų. Dalinkitės jais atsargiai.
                    </div>
                  </div>
                  
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="font-medium text-gray-900">Pagrindinis API raktas</div>
                        <div className="text-sm text-gray-500">Sukurta: 2024-01-01</div>
                      </div>
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-800 text-sm">Regeneruoti</button>
                        <button className="text-red-600 hover:text-red-800 text-sm">Ištrinti</button>
                      </div>
                    </div>
                    <div className="mt-2 p-2 bg-gray-100 rounded font-mono text-sm">
                      sk_1234567890abcdef...
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Webhook nustatymai</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Webhook URL</label>
                    <input
                      type="url"
                      placeholder="https://your-app.com/webhook"
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                      <label className="ml-2 text-sm text-gray-700">Nauji lead'ai</label>
                    </div>
                    <div className="flex items-center">
                      <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                      <label className="ml-2 text-sm text-gray-700">Lead'o statuso pakeitimai</label>
                    </div>
                    <div className="flex items-center">
                      <input type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
                      <label className="ml-2 text-sm text-gray-700">Nauji komentarai</label>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700">
                  Išsaugoti API nustatymus
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
