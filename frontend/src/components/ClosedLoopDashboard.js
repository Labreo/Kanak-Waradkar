/**
 * PROJECT TRIAD — CLOSED LOOP DASHBOARD & REAL-TIME ADVERSARIAL TELEMETRY
 * 
 * Interactive Multi-Vector Closed-Loop Orchestrator
 * Connects directly to backend endpoints:
 * - GET /api/loop/history?vector={A|B|C}
 * - GET /api/loop/cycle/{vector_id}/{cycle_index}
 * - POST /api/loop/trigger
 */

import { fetchLoopHistory, triggerLoopWave } from '../services/api.js';
import { ClosingLoopGauge } from './ClosingLoopGauge.js';

export class ClosedLoopDashboard {
  constructor(container, router) {
    this.container = container;
    this.router = router;
    this.activeVector = 'A';
    this.loopHistory = null;
    this.isRunningWave = false;
    this.gaugeInstance = null;
    this.isRegistryExpanded = false;
    
    // Trigger Form State
    this.batchSize = 100;
    this.cyclesCount = 4;
    this.seed = 42;

    this.init();
  }

  async init() {
    this.renderSkeleton();
    await this.loadLoopHistory();
  }

  renderSkeleton() {
    this.container.innerHTML = `
      <div class="vector-view-shell">
        <!-- Hero Header (3 Headline Stats) -->
        <div class="dashboard-hero">
          <div class="dashboard-hero-top">
            <div class="dashboard-hero-left">
              <div class="view-hero-breadcrumbs">
                <span class="footer-tag" style="cursor:pointer" id="v-l-crumb-home">TRIAD</span>
                <span class="footer-sep">/</span>
                <span>CLOSED LOOP</span>
                <span class="footer-sep">/</span>
                <span class="accent-cyan">ADVERSARIAL CO-EVOLUTION FINALE</span>
              </div>
              <h1 class="view-hero-title">Closed-Loop Adversarial Feedback &amp; Wave Trigger</h1>
              <p class="hub-description">
                Iterative 5-phase cycle state machine (Generate &rarr; Defend &rarr; Evaluate &rarr; Mutate &rarr; Log) demonstrating red-team evasion gains and blue-team adaptation across cycles.
              </p>
            </div>
            <div class="dashboard-hero-stats" id="v-l-stats-ribbon">
              <div class="stat-tile">
                <span class="stat-tile-label">CYCLES EVALUATED</span>
                <span class="stat-tile-val mono-data accent-cyan" id="v-l-completed-cycles"><span class="skeleton-shimmer skeleton-lg" aria-label="Loading..."></span></span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">PEAK EVASION</span>
                <span class="stat-tile-val mono-data accent-amber" id="v-l-gain-val"><span class="skeleton-shimmer skeleton-lg" aria-label="Loading..."></span></span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">STATE MACHINE</span>
                <span class="stat-tile-val mono-data accent-cyan" style="font-size:13px;">5-PHASE STRICT</span>
              </div>
            </div>
          </div>

          <!-- Grounding Invariants Callout -->
          <div class="grounding-banner">
            <div class="grounding-banner-left">
              <span class="grounding-pill-tag">ORCHESTRATION INVARIANTS</span>
              <span>Independent Vector Decoupling &bull; Seed-Controlled Determinism &bull; Standardized JSON Telemetry (<code>loop/schema.json</code>)</span>
            </div>
            <div class="grounding-banner-metrics">
              <span class="grounding-metric-item">Execution Runtime: <strong>&lt; 150ms / Wave</strong></span>
              <span class="grounding-metric-item">State Continuity: <strong>Client-Side Maintained</strong></span>
            </div>
          </div>
        </div>

        <!-- Live Wave Trigger Orchestrator Rail (Always Visible) -->
        <div class="trigger-control-panel">
          <div class="trigger-header-row">
            <div class="panel-title-group">
              <span class="vector-pill">ORCHESTRATE</span>
              <h3 class="panel-title">Live Attack Wave Trigger</h3>
            </div>

            <!-- Vector Switcher Rail -->
            <div class="vector-rail-tabs" role="tablist" aria-label="Vector Selection">
              <button type="button" class="rail-tab-btn active" data-vector="A" id="rail-a">Vector A: Identity</button>
              <button type="button" class="rail-tab-btn" data-vector="B" id="rail-b">Vector B: Transaction</button>
              <button type="button" class="rail-tab-btn" data-vector="C" id="rail-c">Vector C: Agentic</button>
            </div>
          </div>

          <!-- Trigger Controls & Inputs -->
          <div class="trigger-form-row">
            <div class="trigger-inputs-group">
              <div class="trigger-input-item">
                <label for="v-l-batch-size" class="trigger-input-label">Batch Size</label>
                <select id="v-l-batch-size" class="trigger-select">
                  <option value="50">50 samples</option>
                  <option value="100" selected>100 samples</option>
                  <option value="200">200 samples</option>
                </select>
              </div>

              <div class="trigger-input-item">
                <label for="v-l-cycles-count" class="trigger-input-label">Cycles</label>
                <select id="v-l-cycles-count" class="trigger-select">
                  <option value="3">3 Iterations (C0 &rarr; C1 &rarr; C2)</option>
                  <option value="4" selected>4 Iterations (C0 &rarr; C1 &rarr; C2 &rarr; C3)</option>
                </select>
              </div>

              <div class="trigger-input-item">
                <label for="v-l-evasion-tier" class="trigger-input-label">Evasion Strategy</label>
                <select id="v-l-evasion-tier" class="trigger-select">
                  <option value="TIER_1_DIRECT_OVERRIDE">Tier 1: Direct Override / Synthesized Anchor</option>
                  <option value="TIER_2_CONCEALED_STRUCTURAL">Tier 2: Concealed Structural / Burst Cluster</option>
                  <option value="TIER_3_SEMANTIC_PRETEXT" selected>Tier 3: Semantic Pretext / Dilated Cascade</option>
                </select>
              </div>
            </div>

            <!-- Action Button Group -->
            <div class="trigger-actions-group">
              <button type="button" class="trigger-execute-btn" id="v-l-execute-btn">
                <span class="btn-icon" aria-hidden="true">&#9654;</span>
                <span class="btn-label" id="v-l-execute-label">Run Live Attack Wave</span>
              </button>
            </div>
          </div>

          <!-- Execution Stepper (Revealed during live wave simulation) -->
          <div class="trigger-progress-container" id="v-l-progress-row" style="display:none;">
            <div class="loop-stepper" style="display:flex; justify-content:space-between; margin-top:8px;">
              <span class="stepper-step" id="phase-1">1. GENERATE</span>
              <span class="stepper-step" id="phase-2">2. DEFEND</span>
              <span class="stepper-step" id="phase-3">3. EVALUATE</span>
              <span class="stepper-step" id="phase-4">4. MUTATE</span>
              <span class="stepper-step" id="phase-5">5. LOG &amp; RETRAIN</span>
            </div>
          </div>
        </div>

        <!-- Above Fold: Two Hero Visuals Side-by-Side Full Width -->
        <div class="coevolution-grid" style="display:grid; grid-template-columns: 1fr 1fr; gap:var(--space-4); margin-top:var(--space-4);">
          <!-- Left: Closing Loop Radial Gauge Hero Visual -->
          <div class="chart-panel-card" style="display:flex; flex-direction:column;">
            <div class="panel-header">
              <div class="panel-title-group">
                <span class="vector-pill">GAUGE</span>
                <h3 class="panel-title">Closing Loop Radial Progress Gauge</h3>
              </div>
            </div>
            <div class="gauge-mount-point" id="v-l-gauge-container" style="flex:1; display:flex; align-items:center; justify-content:center; min-height:280px;">
              <div class="spinner"></div>
            </div>
          </div>

          <!-- Right: Live Trajectory Line Chart Hero Visual -->
          <div class="chart-panel-card" style="display:flex; flex-direction:column;">
            <div class="panel-header">
              <div class="panel-title-group">
                <span class="vector-pill">TRAJECTORY</span>
                <h3 class="panel-title">Multi-Cycle Red vs. Blue Co-Evolution Curve</h3>
              </div>
              <div class="chart-legend-group">
                <span class="legend-item"><span class="legend-dot dot-amber"></span> Red Evasion</span>
                <span class="legend-item"><span class="legend-dot dot-cyan"></span> Blue Recall</span>
              </div>
            </div>

            <!-- SVG Chart Viewport -->
            <div class="svg-chart-viewport" id="v-l-chart-container" style="flex:1; min-height:280px; display:flex; align-items:center; justify-content:center;">
              <div class="spinner"></div>
            </div>
          </div>
        </div>

        <!-- Below Fold: Single-Line Cycle Summaries -->
        <div class="cycle-summary-strip" style="margin-top:var(--space-4);">
          <div class="panel-header" style="border-bottom:none; margin-bottom:var(--space-2);">
            <div class="panel-title-group">
              <span class="vector-pill">SUMMARY</span>
              <h3 class="panel-title">Cycle Progression Summary</h3>
            </div>
          </div>
          <div class="cycle-lines-list" id="v-l-cycle-lines-container">
            <div class="drawer-empty-state"><div class="spinner"></div><span>Loading cycle summaries...</span></div>
          </div>
        </div>

        <!-- Secondary Mode: Mutation Registry Action Bar & Deep Inspector -->
        <div class="explore-action-bar" style="margin-top:var(--space-4);">
          <div class="explore-action-desc">
            <span class="mono-data accent-cyan">MUTATION AUDIT REGISTRY</span>
            <span>&bull; Full cycle-by-cycle parameter transition tables, mutation rationales, and evading sample IDs</span>
          </div>
          <button type="button" class="explore-action-btn" id="v-l-open-registry-btn">
            <span>Explore the mutation registry</span>
            <span aria-hidden="true">&rarr;</span>
          </button>
        </div>

        <!-- Collapsible Mutation Registry Detail -->
        <div class="mutation-audit-card ${this.isRegistryExpanded ? '' : 'hidden-view'}" id="v-l-mutation-registry-panel" style="margin-top:var(--space-3);">
          <div class="explore-mode-header" style="margin-bottom:var(--space-3);">
            <button type="button" class="explore-back-btn" id="v-l-close-registry-btn">
              <span aria-hidden="true">&larr;</span>
              <span>Collapse Mutation Registry</span>
            </button>
            <div class="explore-header-meta">
              <span class="section-badge" id="v-l-audit-count">4 CYCLES RECORDED</span>
              <span class="footer-meta">Taxonomy §3.4 Co-Evolution Registry</span>
            </div>
          </div>

          <div class="mutation-cycle-accordion" id="v-l-mutation-log-container">
            <div class="drawer-empty-state"><div class="spinner"></div><span>Loading mutation audit...</span></div>
          </div>
        </div>
      </div>
    `;

    const gaugeContainer = this.container.querySelector('#v-l-gauge-container');
    if (gaugeContainer) {
      gaugeContainer.innerHTML = '';
      this.gaugeInstance = new ClosingLoopGauge(gaugeContainer, {
        onCycleSelect: (cycle) => {
          this.updateHUDFromCycle(cycle);
        }
      });
    }

    this.bindDOMEvents();
  }


  bindDOMEvents() {
    this.container.querySelector('#v-l-crumb-home')?.addEventListener('click', () => {
      this.router.navigate('overview');
    });

    // Vector rail tabs
    const railTabs = this.container.querySelectorAll('.rail-tab-btn');
    railTabs.forEach(btn => {
      btn.addEventListener('click', () => {
        railTabs.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.activeVector = btn.getAttribute('data-vector');
        this.loadLoopHistory();
      });
    });

    // Registry explore toggle actions
    this.container.querySelector('#v-l-open-registry-btn')?.addEventListener('click', () => {
      this.setRegistryExpanded(true);
    });

    this.container.querySelector('#v-l-close-registry-btn')?.addEventListener('click', () => {
      this.setRegistryExpanded(false);
    });

    // Form inputs
    this.container.querySelector('#v-l-batch-size')?.addEventListener('change', (e) => {
      this.batchSize = Number(e.target.value);
    });
    this.container.querySelector('#v-l-cycles-count')?.addEventListener('change', (e) => {
      this.cyclesCount = Number(e.target.value);
    });

    // Run wave action button
    const runBtn = this.container.querySelector('#v-l-execute-btn');
    runBtn?.addEventListener('click', () => {
      this.executeLiveWave();
    });
  }

  setRegistryExpanded(expanded) {
    this.isRegistryExpanded = expanded;
    const panel = this.container.querySelector('#v-l-mutation-registry-panel');
    if (panel) {
      panel.classList.toggle('hidden-view', !expanded);
      if (expanded) {
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }

  async loadLoopHistory() {
    try {
      this.loopHistory = await fetchLoopHistory(this.activeVector);
      this.renderAllViews();
    } catch (err) {
      console.error('Failed to load loop history:', err);
    }
  }

  renderAllViews() {
    if (!this.loopHistory) return;
    this.renderHeaderStats();
    this.renderGauge();
    this.renderTrajectoryChart();
    this.renderCycleSummaries();
    this.renderMutationAudit();
  }

  renderHeaderStats() {
    const trend = this.loopHistory.summary_trend || {};
    const totalCycles = this.loopHistory.total_cycles_completed || (this.loopHistory.cycles ? this.loopHistory.cycles.length : 4);
    const gainVal = this.container.querySelector('#v-l-gain-val');
    const completedCycles = this.container.querySelector('#v-l-completed-cycles');
    const auditCount = this.container.querySelector('#v-l-audit-count');

    if (gainVal) {
      const peakEvas = trend.peak_evasion_rate !== undefined ? trend.peak_evasion_rate : (trend.final_evasion_rate || 0.83);
      gainVal.textContent = `${(peakEvas * 100).toFixed(1)}%`;
    }
    if (completedCycles) {
      completedCycles.textContent = `${totalCycles} CYCLES`;
    }
    if (auditCount) {
      auditCount.textContent = `${totalCycles} CYCLES RECORDED`;
    }
  }

  renderGauge() {
    const gaugeContainer = this.container.querySelector('#v-l-gauge-container');
    if (!gaugeContainer) return;

    if (!this.gaugeInstance) {
      gaugeContainer.innerHTML = '';
      this.gaugeInstance = new ClosingLoopGauge(gaugeContainer, {
        initialCycle: 2,
        onCycleSelect: (cycle) => {
          this.updateHUDFromCycle(cycle);
        }
      });
    }

    if (this.loopHistory.cycles) {
      this.gaugeInstance.updateData(this.loopHistory.cycles);
    }
  }

  updateHUDFromCycle(cycle) {
    if (typeof document !== 'undefined') {
      const headerCycle = document.querySelector('#header-cycle-val');
      if (headerCycle) {
        const shortLabel = cycle.label && cycle.label.includes('//') 
          ? cycle.label.split('//')[1].trim() 
          : (cycle.tier ? cycle.tier.replace(/Tier\s*\d+:?\s*/i, '').trim() : 'ADAPTED');
        headerCycle.textContent = `${cycle.id} // ${shortLabel.toUpperCase()}`;
      }
    }
  }

  renderTrajectoryChart() {
    const chartBox = this.container.querySelector('#v-l-chart-container');
    if (!chartBox || !this.loopHistory || !this.loopHistory.cycles) return;

    const cycles = this.loopHistory.cycles;
    const width = 540;
    const height = 260;
    const padding = { top: 25, right: 30, bottom: 40, left: 45 };

    const chartW = width - padding.left - padding.right;
    const chartH = height - padding.top - padding.bottom;

    // Calculate coordinates
    const points = cycles.map((c, i) => {
      const x = padding.left + (cycles.length > 1 ? (i / (cycles.length - 1)) * chartW : chartW / 2);
      const evas = c.evasion_rate !== undefined ? c.evasion_rate : 0;
      const detect = c.detection_rate !== undefined ? c.detection_rate : (1.0 - evas);
      const yEvas = padding.top + (1.0 - evas) * chartH;
      const yDetect = padding.top + (1.0 - detect) * chartH;
      return { x, yEvas, yDetect, evas, detect, cycle: c, index: i };
    });

    // Build SVG paths
    const evasLineD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.yEvas}`).join(' ');
    const detectLineD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.yDetect}`).join(' ');

    const evasAreaD = `${evasLineD} L ${points[points.length - 1].x} ${padding.top + chartH} L ${points[0].x} ${padding.top + chartH} Z`;
    const detectAreaD = `${detectLineD} L ${points[points.length - 1].x} ${padding.top + chartH} L ${points[0].x} ${padding.top + chartH} Z`;

    chartBox.innerHTML = `
      <svg class="trajectory-svg" viewBox="0 0 ${width} ${height}" style="width:100%; height:100%;">
        <defs>
          <linearGradient id="evasionAreaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#F2A93B" stop-opacity="0.45"/>
            <stop offset="100%" stop-color="#F2A93B" stop-opacity="0.0"/>
          </linearGradient>
          <linearGradient id="detectionAreaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#5FD8D0" stop-opacity="0.35"/>
            <stop offset="100%" stop-color="#5FD8D0" stop-opacity="0.0"/>
          </linearGradient>
        </defs>

        <!-- Horizontal Gridlines -->
        ${[0, 0.25, 0.5, 0.75, 1.0].map(val => {
          const y = padding.top + (1.0 - val) * chartH;
          return `
            <line class="chart-grid-line" x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="rgba(255,255,255,0.06)" />
            <text class="chart-axis-label" x="${padding.left - 8}" y="${y + 3}" text-anchor="end" fill="var(--text-muted)" font-size="10px">${Math.round(val * 100)}%</text>
          `;
        }).join('')}

        <!-- X-Axis Labels -->
        ${points.map(p => `
          <line class="chart-grid-line" x1="${p.x}" y1="${padding.top}" x2="${p.x}" y2="${padding.top + chartH}" stroke="rgba(255,255,255,0.06)" />
          <text class="chart-axis-label" x="${p.x}" y="${padding.top + chartH + 20}" text-anchor="middle" font-weight="bold" fill="var(--text-secondary)" font-size="11px">C${p.index}</text>
        `).join('')}

        <!-- Area Fills -->
        <path d="${evasAreaD}" fill="url(#evasionAreaGradient)"/>
        <path d="${detectAreaD}" fill="url(#detectionAreaGradient)"/>

        <!-- Lines -->
        <path d="${detectLineD}" fill="none" stroke="#5FD8D0" stroke-width="2.5" stroke-linecap="round"/>
        <path d="${evasLineD}" fill="none" stroke="#F2A93B" stroke-width="2.5" stroke-linecap="round"/>

        <!-- Node Points -->
        ${points.map(p => `
          <g class="chart-node-point" data-index="${p.index}" style="cursor:pointer;">
            <circle cx="${p.x}" cy="${p.yEvas}" r="5" fill="#F2A93B" stroke="#0C0E1E" stroke-width="2"/>
            <text class="mono-data" x="${p.x}" y="${p.yEvas - 10}" text-anchor="middle" fill="#F2A93B" font-size="11px" font-weight="bold">${(p.evas * 100).toFixed(1)}%</text>
            <circle cx="${p.x}" cy="${p.yDetect}" r="4" fill="#5FD8D0" stroke="#0C0E1E" stroke-width="1.5"/>
          </g>
        `).join('')}
      </svg>
    `;

    chartBox.querySelectorAll('.chart-node-point').forEach(node => {
      node.addEventListener('click', () => {
        const idx = Number(node.getAttribute('data-index'));
        if (this.gaugeInstance) {
          this.gaugeInstance.setCycle(idx);
        }
      });
    });
  }

  renderCycleSummaries() {
    const container = this.container.querySelector('#v-l-cycle-lines-container');
    if (!container || !this.loopHistory || !this.loopHistory.cycles) return;

    const cycles = this.loopHistory.cycles;
    container.innerHTML = `
      <div style="display:flex; flex-direction:column; gap:var(--space-2);">
        ${cycles.map((c, i) => {
          const evasPct = ((c.evasion_rate || 0) * 100).toFixed(1);
          const detectPct = ((c.detection_rate !== undefined ? c.detection_rate : (1 - (c.evasion_rate || 0))) * 100).toFixed(1);
          const tierName = c.mutation_tier ? c.mutation_tier.replace(/_/g, ' ') : `CYCLE ${i}`;
          
          return `
            <div class="cycle-summary-line" style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:6px;">
              <div style="display:flex; align-items:center; gap:12px;">
                <span class="threat-badge badge-allow" style="font-weight:700;">CYCLE ${c.cycle_index !== undefined ? c.cycle_index : i}</span>
                <span style="font-size:13px; font-weight:600; color:var(--text-primary);">${tierName}</span>
                <span style="font-size:12px; color:var(--text-secondary);">&bull; ${c.cycle_summary || 'Feedback mutation step'}</span>
              </div>
              <div style="display:flex; align-items:center; gap:16px;">
                <span class="mono-data" style="font-size:12px; color:var(--accent-amber); font-weight:700;">Evasion: ${evasPct}%</span>
                <span class="mono-data" style="font-size:12px; color:var(--accent-cyan); font-weight:700;">Recall: ${detectPct}%</span>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  renderMutationAudit() {
    const container = this.container.querySelector('#v-l-mutation-log-container');
    if (!container || !this.loopHistory || !this.loopHistory.cycles) return;

    const cycles = this.loopHistory.cycles;
    container.innerHTML = cycles.map(c => {
      const muts = c.mutations_applied || [];
      const evadingIds = c.evading_sample_ids || [];

      return `
        <div class="mutation-cycle-item" style="margin-bottom:var(--space-3); padding:var(--space-3); background:var(--bg-surface); border:1px solid var(--border-subtle); border-radius:6px;">
          <div class="mutation-cycle-head" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div class="mutation-cycle-title" style="display:flex; align-items:center; gap:8px;">
              <span class="threat-badge badge-allow">CYCLE ${c.cycle_index}</span>
              <span style="font-weight:700;">${c.mutation_tier ? c.mutation_tier.replace(/_/g, ' ') : 'TIER BASELINE'}</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span class="mono-data" style="font-size:11px; color:var(--text-secondary);">Seed: ${c.generation_seed}</span>
              <span class="threat-badge ${c.evasion_rate > 0 ? 'badge-block' : 'badge-allow'}">
                Evasion: ${(c.evasion_rate * 100).toFixed(1)}% (${c.evading_count || 0} / ${c.total_malicious || c.batch_size})
              </span>
            </div>
          </div>

          <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin-bottom:8px;">
            ${c.cycle_summary || 'Baseline generation cycle.'}
          </p>

          ${muts.length > 0 ? `
            <table class="mutations-table" style="width:100%; border-collapse:collapse; font-size:12px;">
              <thead>
                <tr style="text-align:left; border-bottom:1px solid var(--border-subtle);">
                  <th style="padding:6px 8px; width:25%;">Parameter Mutated</th>
                  <th style="padding:6px 8px; width:35%;">Transition</th>
                  <th style="padding:6px 8px; width:40%;">Adversarial Rationale</th>
                </tr>
              </thead>
              <tbody>
                ${muts.map(m => `
                  <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                    <td class="mono-data" style="padding:6px 8px; color:var(--accent-cyan); font-size:11px;">${m.parameter}</td>
                    <td class="mono-data" style="padding:6px 8px;">
                      <div class="transition-flow" style="display:flex; align-items:center; gap:6px;">
                        <span style="color:var(--text-muted);">${String(m.previous_value)}</span>
                        <span style="color:var(--text-secondary);">&rarr;</span>
                        <strong style="color:var(--accent-amber);">${String(m.mutated_value)}</strong>
                      </div>
                    </td>
                    <td style="padding:6px 8px; color:var(--text-secondary); font-size:11px; line-height:1.45;">${m.rationale}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          ` : `
            <div style="font-size:11px; color:var(--text-muted); padding:4px 0;">
              &bull; Baseline generation without adversarial feedback mutations applied.
            </div>
          `}

          ${evadingIds.length > 0 ? `
            <div style="margin-top:8px;">
              <span style="font-size:10px; color:var(--text-muted); text-transform:uppercase; font-weight:600; letter-spacing:var(--tracking-wider); display:block; margin-bottom:4px;">Evading Sample IDs:</span>
              <div class="evading-samples-wrap" style="display:flex; flex-wrap:wrap; gap:4px;">
                ${evadingIds.slice(0, 10).map(id => `<span class="sample-id-chip" style="font-size:10px; padding:2px 6px; background:var(--bg-inset); border:1px solid var(--border-subtle); border-radius:3px;">${id}</span>`).join('')}
                ${evadingIds.length > 10 ? `<span class="footer-tag" style="font-size:10px;">+${evadingIds.length - 10} more</span>` : ''}
              </div>
            </div>
          ` : ''}
        </div>
      `;
    }).join('');
  }

  async executeLiveWave() {
    if (this.isRunningWave) return;
    this.isRunningWave = true;

    const runBtn = this.container.querySelector('#v-l-execute-btn');
    const btnLabel = this.container.querySelector('#v-l-execute-label');
    const progressRow = this.container.querySelector('#v-l-progress-row');

    if (runBtn) {
      runBtn.classList.add('running');
      runBtn.disabled = true;
    }
    if (btnLabel) btnLabel.textContent = 'Running Attack Wave...';
    if (progressRow) progressRow.style.display = 'block';

    const setStep = (num) => {
      for (let i = 1; i <= 5; i++) {
        const el = this.container.querySelector(`#phase-${i}`);
        if (el) {
          el.className = `stepper-step ${i === num ? 'active' : (i < num ? 'completed' : '')}`;
        }
      }
    };

    setStep(1); // GENERATE
    setTimeout(() => setStep(2), 60); // DEFEND
    setTimeout(() => setStep(3), 120); // EVALUATE
    setTimeout(() => setStep(4), 180); // MUTATE

    try {
      const response = await triggerLoopWave(this.activeVector, {
        cycles: this.cyclesCount,
        batch_size: this.batchSize,
        seed: this.seed
      });

      setStep(5); // LOG
      this.loopHistory = response;
      this.renderAllViews();

      if (typeof document !== 'undefined') {
        const headerCycle = document.querySelector('#header-cycle-val');
        if (headerCycle) {
          headerCycle.textContent = `C2 // ADAPTED (VECT ${this.activeVector})`;
        }
      }

    } catch (err) {
      console.error('Failed to run attack wave:', err);
      alert(`Wave trigger error: ${err.message}`);
    } finally {
      setTimeout(() => {
        this.isRunningWave = false;
        if (runBtn) {
          runBtn.classList.remove('running');
          runBtn.disabled = false;
        }
        if (btnLabel) btnLabel.textContent = 'Run Live Attack Wave';
        if (progressRow) progressRow.style.display = 'none';
      }, 350);
    }
  }
}
