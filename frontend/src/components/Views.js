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

  // 1. Command Hub Hero
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
      <div class="dashboard-hero-stats">
        <div class="stat-tile">
          <span class="stat-tile-label">Total Vectors</span>
          <span class="stat-tile-val mono-data">03</span>
        </div>
        <div class="stat-tile">
          <span class="stat-tile-label">Avg Recall</span>
          <span class="stat-tile-val mono-data" id="hub-avg-recall">96.6%</span>
        </div>
        <div class="stat-tile">
          <span class="stat-tile-label">Max Evasion</span>
          <span class="stat-tile-val mono-data accent-cyan" id="hub-max-evasion">87.0%</span>
        </div>
      </div>
    </div>
  `;
  shell.appendChild(hero);

  // 2. Three Vector Cards (Equal Visual Weight)
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
  cardsSection.appendChild(renderVectorCards((target) => router.navigate(target)));
  shell.appendChild(cardsSection);

  // 3. Lower Command Hub Grid (Signature Closing Loop + Threat Matrix Feed)
  const lowerGrid = document.createElement('section');
  lowerGrid.className = 'command-hub-lower-grid';
  lowerGrid.innerHTML = `
    <!-- Left: Signature Closing Loop Gauge -->
    <div class="hub-panel loop-gauge-panel">
      <div class="panel-header">
        <div class="panel-title-group">
          <span class="vector-pill">LOOP</span>
          <h3 class="panel-title">Closed-Loop Evasion &amp; Adaptation Trajectory</h3>
        </div>
        <span class="section-badge">RADIAL PROGRESS RING</span>
      </div>
      <div id="overview-loop-mount"></div>
    </div>

    <!-- Right: Real-time Threat Matrix & Attack Archetypes Feed -->
    <div class="hub-panel threat-feed-panel">
      <div class="panel-header">
        <div class="panel-title-group">
          <span class="vector-pill">SOC</span>
          <h3 class="panel-title">Attack Matrix &amp; Evasion Archetypes</h3>
        </div>
        <span class="section-badge">TAXONOMY §2.1-§2.3</span>
      </div>
      <div class="threat-matrix-list">
        <div class="threat-item">
          <div class="threat-main">
            <span class="threat-vector-tag">V_A</span>
            <div class="threat-info">
              <div class="threat-title">PDF417 Barcode Parity Tamper</div>
              <div class="threat-sub">Frankenstein stolen anchor + AAMVA checksum repair</div>
            </div>
          </div>
          <span class="threat-badge badge-block">BLOCKED (100%)</span>
        </div>

        <div class="threat-item">
          <div class="threat-main">
            <span class="threat-vector-tag">V_B</span>
            <div class="threat-info">
              <div class="threat-title">Sub-Second Velocity Burst Probes</div>
              <div class="threat-sub">ISO 8583 decline cascade + BIN range enumeration</div>
            </div>
          </div>
          <span class="threat-badge badge-block">BLOCKED (89.9%)</span>
        </div>

        <div class="threat-item">
          <div class="threat-main">
            <span class="threat-vector-tag">V_C</span>
            <div class="threat-info">
              <div class="threat-title">Hidden CSS / HTML Comment Injection</div>
              <div class="threat-sub">Autonomous tool-call prompt override + AP invoice memo</div>
            </div>
          </div>
          <span class="threat-badge badge-block">BLOCKED (100%)</span>
        </div>

        <div class="threat-item">
          <div class="threat-main">
            <span class="threat-vector-tag">LOOP</span>
            <div class="threat-info">
              <div class="threat-title">Tier 3 Semantic Mutation Evasion</div>
              <div class="threat-sub">Organic amounts + native EXIF metadata camouflage</div>
            </div>
          </div>
          <span class="threat-badge badge-review">MUTATED (83%)</span>
        </div>
      </div>
    </div>
  `;
  shell.appendChild(lowerGrid);

  // Mount ClosingLoopGauge in lower grid and fetch live vector summaries
  setTimeout(async () => {
    const mount = shell.querySelector('#overview-loop-mount');
    if (mount) {
      new ClosingLoopGauge(mount, {
        initialCycle: 2,
        onCycleSelect: (cycle) => {
          const headerCycle = document.querySelector('#header-cycle-val');
          if (headerCycle) headerCycle.textContent = `${cycle.id} // ${cycle.label.split('//')[1].trim()}`;
        }
      });
    }

    try {
      const summaries = await fetchVectors();
      if (summaries && Array.isArray(summaries)) {
        updateVectorCardsData(cardsSection, summaries);

        // Compute aggregate metrics
        let totalRecall = 0;
        let maxEvas = 0;
        summaries.forEach(s => {
          if (s.current_defense_recall !== undefined) totalRecall += s.current_defense_recall;
          if (s.latest_loop_evasion_rate !== undefined && s.latest_loop_evasion_rate > maxEvas) {
            maxEvas = s.latest_loop_evasion_rate;
          }
        });
        const avgRecall = summaries.length > 0 ? (totalRecall / summaries.length) * 100 : 96.6;
        const avgRecallEl = shell.querySelector('#hub-avg-recall');
        const maxEvasEl = shell.querySelector('#hub-max-evasion');
        if (avgRecallEl) avgRecallEl.textContent = `${avgRecall.toFixed(1)}%`;
        if (maxEvasEl) maxEvasEl.textContent = `${(maxEvas * 100).toFixed(1)}%`;
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
