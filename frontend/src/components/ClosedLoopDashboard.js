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
        <!-- Hero Header -->
        <div class="dashboard-hero">
          <div class="dashboard-hero-top">
            <div class="dashboard-hero-left">
              <div class="view-hero-breadcrumbs">
                <span class="footer-tag" style="cursor:pointer" id="v-l-crumb-home">TRIAD</span>
                <span class="footer-sep">/</span>
                <span>CLOSED LOOP</span>
                <span class="footer-sep">/</span>
                <span class="accent-cyan">ADVERSARIAL CO-EVOLUTION ENGINE</span>
              </div>
              <h1 class="view-hero-title">Closed-Loop Adversarial Feedback &amp; Wave Trigger</h1>
              <p class="hub-description">
                Iterative 5-phase cycle state machine (Generate &rarr; Defend &rarr; Evaluate &rarr; Mutate &rarr; Log) demonstrating red-team evasion gains and blue-team adaptation across cycles.
              </p>
            </div>
            <div class="dashboard-hero-stats" id="v-l-stats-ribbon">
              <div class="stat-tile">
                <span class="stat-tile-label">COMPLETED CYCLES</span>
                <span class="stat-tile-val mono-data accent-cyan" id="v-l-completed-cycles">4 CYCLES / VECTOR</span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">ADVERSARIAL GAIN</span>
                <span class="stat-tile-val mono-data accent-cyan" id="v-l-gain-val">+83.0%</span>
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

        <!-- Live Wave Trigger Control Panel -->
        <div class="trigger-control-panel">
          <div class="trigger-header-row">
            <div class="panel-title-group">
              <span class="vector-pill">CO-EVOLUTION</span>
              <h3 class="panel-title">Live Attack Wave Orchestrator</h3>
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
                  <option value="500">500 samples</option>
                </select>
              </div>

              <div class="trigger-input-item">
                <label for="v-l-cycles-count" class="trigger-input-label">Cycles</label>
                <select id="v-l-cycles-count" class="trigger-select">
                  <option value="3">3 Iterations (C0 &rarr; C1 &rarr; C2)</option>
                  <option value="4" selected>4 Iterations (C0 &rarr; C1 &rarr; C2 &rarr; C3 [Retrain])</option>
                </select>
              </div>

              <div class="trigger-input-item">
                <label for="v-l-seed-input" class="trigger-input-label">PRNG Seed</label>
                <div style="display:flex; align-items:center; gap:4px;">
                  <input type="number" id="v-l-seed-input" class="trigger-input-num" style="width:80px;" value="42" />
                  <button type="button" class="scenario-chip" id="v-l-rand-seed" style="padding:4px 8px; font-size:10px;">🎲 Rand</button>
                </div>
              </div>
            </div>

            <button type="button" class="run-wave-action-btn" id="v-l-run-wave-btn">
              <span id="v-l-btn-icon">&#9658;</span>
              <span id="v-l-btn-label">Run Live Attack Wave</span>
            </button>
          </div>

          <!-- 5-Phase Transition Stepper -->
          <div class="phase-stepper-bar" id="v-l-phase-stepper">
            <div class="stepper-step active" id="phase-1"><span class="step-num">1</span> <span>GENERATE</span></div>
            <span class="stepper-arrow">&rarr;</span>
            <div class="stepper-step" id="phase-2"><span class="step-num">2</span> <span>DEFEND</span></div>
            <span class="stepper-arrow">&rarr;</span>
            <div class="stepper-step" id="phase-3"><span class="step-num">3</span> <span>EVALUATE</span></div>
            <span class="stepper-arrow">&rarr;</span>
            <div class="stepper-step" id="phase-4"><span class="step-num">4</span> <span>MUTATE</span></div>
            <span class="stepper-arrow">&rarr;</span>
            <div class="stepper-step" id="phase-5"><span class="step-num">5</span> <span>LOG</span></div>
          </div>
        </div>

        <!-- Dual Real-Time Visualizations Grid -->
        <div class="loop-visuals-grid">
          <!-- Left: Signature Concentric Closing Loop Gauge -->
          <div class="loop-visual-card">
            <div class="panel-header">
              <div class="panel-title-group">
                <span class="vector-pill">GEOMETRY</span>
                <h3 class="panel-title">Signature Closed-Loop Radial Progress Gauge</h3>
              </div>
              <span class="section-badge" id="v-l-gauge-badge">CYCLE 2 ACTIVE</span>
            </div>
            <div id="v-l-gauge-container" style="display:flex; justify-content:center; align-items:center; min-height:420px;"></div>
          </div>

          <!-- Right: Multi-Cycle Cumulative Evasion & Detection Area/Line Chart -->
          <div class="loop-visual-card">
            <div class="panel-header">
              <div class="panel-title-group">
                <span class="vector-pill">TELEMETRY</span>
                <h3 class="panel-title">Multi-Cycle Cumulative Evasion Trajectory</h3>
              </div>
              <div class="chart-legend-bar">
                <div class="legend-item">
                  <span class="legend-color-dot amber"></span>
                  <span>Evasion Rate</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color-dot cyan"></span>
                  <span>Detection Recall</span>
                </div>
              </div>
            </div>
            
            <div class="chart-container-box" id="v-l-chart-container">
              <!-- SVG chart will be rendered here dynamically -->
              <div class="drawer-empty-state">
                <div class="spinner"></div>
                <span>Rendering trajectory curves...</span>
              </div>
            </div>

            <!-- Dynamic Telemetry Summary Tile -->
            <div class="grounding-banner" style="margin-top:auto;" id="v-l-chart-hud-banner">
              <div class="grounding-banner-left">
                <span class="grounding-pill-tag" id="v-l-hud-tier-tag">TIER 3: STEALTH MUTATIONS</span>
                <span id="v-l-hud-summary-text">Cumulative adversarial gain verified across 3 iterative feedback loops.</span>
              </div>
              <div class="grounding-banner-metrics">
                <span class="grounding-metric-item">Evasion: <strong class="accent-amber" id="v-l-hud-evasion-stat">83.0%</strong></span>
                <span class="grounding-metric-item">Defense Recall: <strong class="accent-cyan" id="v-l-hud-recall-stat">17.0%</strong></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Adversarial Mutation Audit Log -->
        <div class="mutation-audit-card">
          <div class="panel-header">
            <div class="panel-title-group">
              <span class="vector-pill">AUDIT</span>
              <h3 class="panel-title">Cycle-by-Cycle Adversarial Mutation Registry</h3>
            </div>
            <span class="section-badge" id="v-l-audit-count">3 CYCLES RECORDED</span>
          </div>

          <div class="mutation-cycle-accordion" id="v-l-mutation-log-container">
            <div class="drawer-empty-state"><div class="spinner"></div><span>Loading mutation audit...</span></div>
          </div>
        </div>
      </div>
    `;

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

    // Randomize seed button
    this.container.querySelector('#v-l-rand-seed')?.addEventListener('click', () => {
      const seedInput = this.container.querySelector('#v-l-seed-input');
      if (seedInput) {
        const randSeed = Math.floor(Math.random() * 9000) + 1000;
        seedInput.value = randSeed;
        this.seed = randSeed;
      }
    });

    // Form inputs
    this.container.querySelector('#v-l-batch-size')?.addEventListener('change', (e) => {
      this.batchSize = Number(e.target.value);
    });
    this.container.querySelector('#v-l-cycles-count')?.addEventListener('change', (e) => {
      this.cyclesCount = Number(e.target.value);
    });
    this.container.querySelector('#v-l-seed-input')?.addEventListener('input', (e) => {
      this.seed = Number(e.target.value) || 42;
    });

    // Run wave action button
    this.container.querySelector('#v-l-run-wave-btn')?.addEventListener('click', () => {
      this.executeLiveWave();
    });
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
      gainVal.textContent = `+${(peakEvas * 100).toFixed(1)}% PEAK`;
    }
    if (completedCycles) {
      completedCycles.textContent = `${totalCycles} CYCLES / VECTOR`;
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
    const tierTag = this.container.querySelector('#v-l-hud-tier-tag');
    const summaryText = this.container.querySelector('#v-l-hud-summary-text');
    const evasStat = this.container.querySelector('#v-l-hud-evasion-stat');
    const recallStat = this.container.querySelector('#v-l-hud-recall-stat');

    if (tierTag) tierTag.textContent = (cycle.tier || 'TIER 3').toUpperCase();
    if (summaryText) summaryText.textContent = cycle.mutation || 'Cycle mutations applied.';
    if (evasStat) evasStat.textContent = `${((cycle.evasionRate || 0) * 100).toFixed(1)}%`;
    if (recallStat) recallStat.textContent = `${((cycle.detectionRate || 0) * 100).toFixed(1)}%`;

    // Wire global header cycle telemetry to match selected cycle
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
    const height = 240;
    const padding = { top: 20, right: 30, bottom: 40, left: 45 };

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
      <svg class="trajectory-svg" viewBox="0 0 ${width} ${height}">
        <defs>
          <linearGradient id="evasionAreaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#F2A93B" stop-opacity="0.6"/>
            <stop offset="100%" stop-color="#F2A93B" stop-opacity="0.0"/>
          </linearGradient>
          <linearGradient id="detectionAreaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#5FD8D0" stop-opacity="0.4"/>
            <stop offset="100%" stop-color="#5FD8D0" stop-opacity="0.0"/>
          </linearGradient>
        </defs>

        <!-- Horizontal Gridlines -->
        ${[0, 0.25, 0.5, 0.75, 1.0].map(val => {
          const y = padding.top + (1.0 - val) * chartH;
          return `
            <line class="chart-grid-line" x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}"/>
            <text class="chart-axis-label" x="${padding.left - 8}" y="${y + 3}" text-anchor="end">${Math.round(val * 100)}%</text>
          `;
        }).join('')}

        <!-- X-Axis Labels -->
        ${points.map(p => `
          <line class="chart-grid-line" x1="${p.x}" y1="${padding.top}" x2="${p.x}" y2="${padding.top + chartH}"/>
          <text class="chart-axis-label" x="${p.x}" y="${padding.top + chartH + 20}" text-anchor="middle" font-weight="bold">C${p.index} (${p.cycle.mutation_tier ? p.cycle.mutation_tier.replace(/TIER_[0-9]_/, '') : ''})</text>
        `).join('')}

        <!-- Area Fills -->
        <path class="chart-area-evasion" d="${evasAreaD}"/>
        <path class="chart-area-detection" d="${detectAreaD}"/>

        <!-- Lines -->
        <path class="chart-line-detection" d="${detectLineD}"/>
        <path class="chart-line-evasion" d="${evasLineD}"/>

        <!-- Node Points -->
        ${points.map(p => `
          <g class="chart-node-point" data-index="${p.index}">
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

  renderMutationAudit() {
    const container = this.container.querySelector('#v-l-mutation-log-container');
    if (!container || !this.loopHistory || !this.loopHistory.cycles) return;

    const cycles = this.loopHistory.cycles;
    container.innerHTML = cycles.map(c => {
      const muts = c.mutations_applied || [];
      const evadingIds = c.evading_sample_ids || [];

      return `
        <div class="mutation-cycle-item">
          <div class="mutation-cycle-head">
            <div class="mutation-cycle-title">
              <span class="threat-badge badge-allow">CYCLE ${c.cycle_index}</span>
              <span>${c.mutation_tier ? c.mutation_tier.replace(/_/g, ' ') : 'TIER BASELINE'}</span>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
              <span class="mono-data" style="font-size:11px; color:var(--text-secondary);">Seed: ${c.generation_seed}</span>
              <span class="threat-badge ${c.evasion_rate > 0 ? 'badge-block' : 'badge-allow'}">
                Evasion: ${(c.evasion_rate * 100).toFixed(1)}% (${c.evading_count || 0} / ${c.total_malicious || c.batch_size})
              </span>
            </div>
          </div>

          <p style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin:0;">
            ${c.cycle_summary || 'Baseline generation cycle.'}
          </p>

          ${muts.length > 0 ? `
            <table class="mutations-table">
              <thead>
                <tr>
                  <th style="width:24%">Parameter Mutated</th>
                  <th style="width:38%">Transition</th>
                  <th style="width:38%">Adversarial Rationale</th>
                </tr>
              </thead>
              <tbody>
                ${muts.map(m => `
                  <tr>
                    <td class="mono-data" style="color:var(--accent-cyan); font-size:11px; word-break:break-word;">${m.parameter}</td>
                    <td class="mono-data">
                      <div class="transition-flow">
                        <span class="transition-prev">${String(m.previous_value)}</span>
                        <span class="transition-arrow">&rarr;</span>
                        <strong class="transition-mut">${String(m.mutated_value)}</strong>
                      </div>
                    </td>
                    <td style="color:var(--text-secondary); font-size:11px; line-height:1.45; word-break:break-word;">${m.rationale}</td>
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
            <div style="margin-top:6px;">
              <span style="font-size:10px; color:var(--text-muted); text-transform:uppercase; font-weight:600; letter-spacing:var(--tracking-wider); display:block; margin-bottom:4px;">Evading Sample IDs:</span>
              <div class="evading-samples-wrap">
                ${evadingIds.slice(0, 10).map(id => `<span class="sample-id-chip">${id}</span>`).join('')}
                ${evadingIds.length > 10 ? `<span class="footer-tag">+${evadingIds.length - 10} more</span>` : ''}
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

    const runBtn = this.container.querySelector('#v-l-run-wave-btn');
    const btnLabel = this.container.querySelector('#v-l-btn-label');
    const btnIcon = this.container.querySelector('#v-l-btn-icon');

    if (runBtn) {
      runBtn.classList.add('running');
      runBtn.disabled = true;
    }
    if (btnLabel) btnLabel.textContent = 'Running Attack Wave...';
    if (btnIcon) btnIcon.innerHTML = '&#9203;';

    // Step through stepper
    const setStep = (num) => {
      for (let i = 1; i <= 5; i++) {
        const el = this.container.querySelector(`#phase-${i}`);
        if (el) {
          el.className = `stepper-step ${i === num ? 'active' : (i < num ? 'completed' : '')}`;
        }
      }
    };

    setStep(1); // GENERATE
    setTimeout(() => setStep(2), 80); // DEFEND
    setTimeout(() => setStep(3), 160); // EVALUATE
    setTimeout(() => setStep(4), 240); // MUTATE

    try {
      const response = await triggerLoopWave(this.activeVector, {
        cycles: this.cyclesCount,
        batch_size: this.batchSize,
        seed: this.seed
      });

      setStep(5); // LOG
      this.loopHistory = response;
      this.renderAllViews();

      // Update global header status indicator if present
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
        if (btnIcon) btnIcon.innerHTML = '&#9658;';
      }, 400);
    }
  }
}
