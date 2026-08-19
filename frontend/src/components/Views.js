/**
 * PROJECT TRIAD — VIEW RENDERERS & SHELL SCAFFOLDS
 * 
 * Provides view templates and scaffolding for:
 * 1. Overview (Command Hub with Equal-Weight Vector Cards + Signature Closing Loop Gauge)
 * 2. Vector A (Synthetic Identity & Document Forensics)
 * 3. Vector B (Transaction & Card Testing Streams)
 * 4. Vector C (Agentic Payment Hijacking Centerpiece)
 * 5. Closed Loop (Multi-Cycle Telemetry & Live Wave Trigger Engine)
 */

import { renderVectorCards, updateVectorCardsData } from './VectorCards.js';
import { ClosingLoopGauge } from './ClosingLoopGauge.js';
import { VectorADashboard } from './VectorADashboard.js';
import { VectorBDashboard } from './VectorBDashboard.js';
import { VectorCDashboard } from './VectorCDashboard.js';
import { ClosedLoopDashboard } from './ClosedLoopDashboard.js';
import { fetchVectors } from '../services/api.js';

export function renderOverviewView(router) {
  const root = document.createElement('div');
  root.className = 'vector-view-container';

  const shell = document.createElement('div');
  shell.className = 'vector-view-shell overview-view';

  // 1. Command Hub Hero (Eyebrow, Title, One-sentence subhead)
  const hero = document.createElement('div');
  hero.className = 'dashboard-hero command-hub-header';
  hero.innerHTML = `
    <div class="dashboard-hero-top">
      <div class="dashboard-hero-left">
        <div class="view-hero-breadcrumbs">
          <span class="status-pulse"></span>
          <span>Red-Team / Blue-Team Orchestration Engine</span>
        </div>
        <h1 class="view-hero-title">Autonomous Payment Fraud Red-Teaming &amp; Defense System</h1>
        <p class="hub-description">
          Continuous adversarial feedback loop generating sophisticated synthetic fraud vectors, evaluating multi-tier defense scanners, and mutating evasive attack parameters across three mission-critical payment rails.
        </p>
      </div>
    </div>
  `;
  shell.appendChild(hero);

  // 2. Three Vector Cards (Equal Visual Weight, 2 headline stats each)
  const cardsSection = document.createElement('section');
  cardsSection.className = 'cards-section';
  cardsSection.innerHTML = `
    <div class="section-title-bar">
      <h2 class="section-heading">
        <span>Payment Threat Vectors</span>
        <span class="section-badge">3 ACTIVE RAILS</span>
      </h2>
    </div>
  `;
  const cardsContainer = renderVectorCards((target) => router.navigate(target));
  cardsSection.appendChild(cardsContainer);
  shell.appendChild(cardsSection);

  // Fetch live vector summaries to populate cards
  setTimeout(async () => {
    try {
      const summaries = await fetchVectors();
      if (summaries && Array.isArray(summaries)) {
        updateVectorCardsData(cardsSection, summaries);
      }
    } catch (err) {
      console.warn('Could not load live vector summaries for Command Hub:', err);
    }
  }, 0);

  root.appendChild(shell);
  return root;
}

export function renderVectorAShell(router) {
  const root = document.createElement('div');
  root.className = 'vector-view-container';
  new VectorADashboard(root, router);
  return root;
}

export function renderVectorBShell(router) {
  const root = document.createElement('div');
  root.className = 'vector-view-container';
  new VectorBDashboard(root, router);
  return root;
}

export function renderVectorCShell(router) {
  const root = document.createElement('div');
  root.className = 'vector-view-container';
  new VectorCDashboard(root, router);
  return root;
}

export function renderLoopShell(router) {
  const root = document.createElement('div');
  root.className = 'vector-view-container';
  new ClosedLoopDashboard(root, router);
  return root;
}
