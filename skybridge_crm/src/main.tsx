// React aplikacijos pagrindinis failas - skirtas testavimui

import React from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './index.css';

// Sukuriam root elementą, jeigu jo nėra
let rootElement = document.getElementById('root');
if (!rootElement) {
  rootElement = document.createElement('div');
  rootElement.id = 'root';
  document.body.appendChild(rootElement);
}

// Inicializuojame React aplikaciją
const root = createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Export for potential external use
export { rootElement };
