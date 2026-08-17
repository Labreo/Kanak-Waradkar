/**
 * PROJECT TRIAD — FRONTEND MAIN ENTRY POINT
 * 
 * Bootstraps the application shell, mounts the client-side router,
 * and initializes telemetry status monitors.
 */

import { Router } from './components/Navigation.js';

document.addEventListener('DOMContentLoaded', () => {
  const viewRoot = document.getElementById('view-root');
  if (!viewRoot) {
    console.error('Missing #view-root in DOM');
    return;
  }

  // Initialize Router
  const router = new Router(viewRoot);

  // Optional background backend health probe
  async function checkBackendHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        if (statusIndicator && statusText) {
          statusText.textContent = `API // ${data.status.toUpperCase()}`;
        }
      }
    } catch (err) {
      // Graceful offline standalone state for S23 shell scaffolding
      console.log('Backend running in standalone/mock mode for S23 shell.');
    }
  }

  checkBackendHealth();
});
