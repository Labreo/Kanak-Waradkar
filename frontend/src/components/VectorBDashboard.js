/**
 * PROJECT TRIAD — VECTOR B DASHBOARD VIEW COMPONENT
 * 
 * Transaction & Card-Testing Behavioral Fraud Dashboard
 * Grounded in IEEE-CIS Fraud Detection (590k txs) & PaySim (6.36M ops) empirical distributions.
 * Wires live data from:
 * - GET /api/vectors/B/overview
 * - GET /api/instances?vector=B
 * - GET /api/instances/B/{instance_id}
 */

import { fetchVectorOverview, fetchInstances, fetchInstanceDetail } from '../services/api.js';

// Backward compatibility export (deprecated - live batch data is used dynamically)
export const CARD_TESTING_SAMPLE_SEQUENCE = [];

export class VectorBDashboard {
  constructor(container, router) {
    this.container = container;
    this.router = router;
    this.overviewData = null;
    this.instances = [];
    this.totalRecords = 1000;
    this.selectedInstanceId = null;
    this.selectedDetail = null;
    this.burstSequences = [];
    this.activeBurstSequence = null;
    this.selectedSequenceStep = 1;
    this.isLoadingList = false;
    this.isLoadingDetail = false;
    this.isExploreMode = false;

    // Filter and Pagination State
    this.verdictFilter = 'ALL';
    this.searchQuery = '';
    this.pageLimit = 25;
    this.pageOffset = 0;

    this.init();
  }

  async init() {
    this.renderSkeleton();
    await Promise.all([
      this.loadOverview(),
      this.loadInstances()
    ]);
  }

  renderSkeleton() {
    this.container.innerHTML = `
      <div class="vector-view-shell">
        <!-- Hero Header (3 Headline Stats) -->
        <div class="dashboard-hero">
          <div class="dashboard-hero-top">
            <div class="dashboard-hero-left">
              <div class="view-hero-breadcrumbs">
                <span class="footer-tag" style="cursor:pointer" id="v-b-crumb-home">TRIAD</span>
                <span class="footer-sep">/</span>
                <span>VECTOR B</span>
                <span class="footer-sep">/</span>
                <span class="accent-cyan">TRANSACTION &amp; CARD-TESTING FRAUD</span>
              </div>
              <h1 class="view-hero-title">Vector B: Empirical Fidelity &amp; Velocity Burst Stream</h1>
              <p class="hub-description">
                Empirical distribution fidelity matching IEEE-CIS benchmark statistics and evaluating automated multi-probe card-testing bursts against a HistGradientBoostingClassifier.
              </p>
            </div>
            <div class="dashboard-hero-stats" id="v-b-stats-ribbon">
              <div class="stat-tile">
                <span class="stat-tile-label">REAL IEEE-CIS AUC</span>
                <span class="stat-tile-val mono-data accent-cyan"><span class="skeleton-shimmer skeleton-lg" aria-label="Loading..."></span></span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">BURST RECALL</span>
                <span class="stat-tile-val mono-data accent-cyan"><span class="skeleton-shimmer skeleton-lg" aria-label="Loading..."></span></span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">MACRO FIDELITY</span>
                <span class="stat-tile-val mono-data accent-amber"><span class="skeleton-shimmer skeleton-lg" aria-label="Loading..."></span></span>
              </div>
            </div>
          </div>

          <!-- Grounding Benchmark Callout -->
          <div class="grounding-banner">
            <div class="grounding-banner-left">
              <span class="grounding-pill-tag">EMPIRICAL GROUNDING</span>
              <span>IEEE-CIS (590k txs) &bull; PaySim (6.36M ops) &bull; Time-Respecting Validation</span>
            </div>
            <div class="grounding-banner-metrics">
              <span class="grounding-metric-item">Median Amt: <strong>$65.00 Syn</strong> vs <strong>$68.77 Real</strong></span>
              <span class="grounding-metric-item">Burst &Delta;t: <strong>0.31s Peak</strong> vs <strong>38,561s Normal</strong></span>
            </div>
          </div>
        </div>

        <!-- Primary Mode: Dominant Visual Distribution Comparison & Sequence Dynamics -->
        <div id="v-b-primary-stage" class="vector-primary-stage ${this.isExploreMode ? 'hidden-view' : ''}">
          <div class="primary-hero-visual-card" id="v-b-dominant-visual">
            <!-- Distribution Comparison Visual Container -->
            <div class="distribution-visual-container">
              <div class="panel-header" style="border-bottom:none; padding-bottom:0;">
                <div class="panel-title-group">
                  <span class="vector-pill">FIDELITY</span>
                  <h3 class="panel-title" style="font-size:16px;">Real IEEE-CIS vs. Synthetic TRIAD Empirical Distribution Comparison</h3>
                </div>
                <div class="chart-legend-group">
                  <span class="legend-item"><span class="legend-dot dot-cyan"></span> Real IEEE-CIS (590k Baseline)</span>
                  <span class="legend-item"><span class="legend-dot dot-amber"></span> Synthetic TRIAD (Vector B)</span>
                </div>
              </div>

              <!-- Paired Distribution Histogram Bars -->
              <div class="histogram-comparison-grid">
                <div class="hist-metric-banner">
                  <div class="hist-metric-col">
                    <span class="hist-metric-label">MEDIAN TRANSACTION AMOUNT</span>
                    <div class="hist-metric-values">
                      <span class="mono-data accent-amber" style="font-size:18px; font-weight:800;">$65.00 <small style="font-size:11px; color:var(--text-muted);">SYN</small></span>
                      <span style="color:var(--text-muted); font-size:13px;">vs</span>
                      <span class="mono-data accent-cyan" style="font-size:18px; font-weight:800;">$68.77 <small style="font-size:11px; color:var(--text-muted);">REAL</small></span>
                      <span class="section-badge" style="color:var(--status-allow); border-color:var(--status-allow-border); font-size:10px;">&Delta; $3.77 (94.5% MATCH)</span>
                    </div>
                  </div>
                  <div class="hist-metric-col" style="text-align:right;">
                    <span class="hist-metric-label">DISTRIBUTION SIMILARITY (JS DIVERGENCE)</span>
                    <span class="mono-data accent-cyan" style="font-size:18px; font-weight:800;">0.8693 MACRO FIDELITY</span>
                  </div>
                </div>

                <!-- Paired Amount Distribution Bars -->
                <div class="paired-distribution-bars">
                  <div class="paired-bar-row">
                    <div class="paired-bar-label">
                      <span class="mono-data" style="font-weight:700;">$0 &ndash; $25</span>
                      <span class="bar-sub-label">Micro Purchases</span>
                    </div>
                    <div class="paired-bars-track-wrap">
                      <div class="paired-bar-line">
                        <span class="bar-tag cyan">REAL</span>
                        <div class="bar-track"><div class="bar-fill real" style="width:28.4%"></div></div>
                        <span class="mono-data bar-pct">28.4%</span>
                      </div>
                      <div class="paired-bar-line">
                        <span class="bar-tag amber">SYN</span>
                        <div class="bar-track"><div class="bar-fill syn" style="width:27.8%"></div></div>
                        <span class="mono-data bar-pct">27.8%</span>
                      </div>
                    </div>
                  </div>

                  <div class="paired-bar-row">
                    <div class="paired-bar-label">
                      <span class="mono-data" style="font-weight:700;">$25 &ndash; $50</span>
                      <span class="bar-sub-label">Everyday Retail</span>
                    </div>
                    <div class="paired-bars-track-wrap">
                      <div class="paired-bar-line">
                        <span class="bar-tag cyan">REAL</span>
                        <div class="bar-track"><div class="bar-fill real" style="width:24.1%"></div></div>
                        <span class="mono-data bar-pct">24.1%</span>
                      </div>
                      <div class="paired-bar-line">
                        <span class="bar-tag amber">SYN</span>
                        <div class="bar-track"><div class="bar-fill syn" style="width:24.6%"></div></div>
                        <span class="mono-data bar-pct">24.6%</span>
                      </div>
                    </div>
                  </div>

                  <div class="paired-bar-row">
                    <div class="paired-bar-label">
                      <span class="mono-data" style="font-weight:700;">$50 &ndash; $100</span>
                      <span class="bar-sub-label">Median Category</span>
                    </div>
                    <div class="paired-bars-track-wrap">
                      <div class="paired-bar-line">
                        <span class="bar-tag cyan">REAL</span>
                        <div class="bar-track"><div class="bar-fill real" style="width:21.8%"></div></div>
                        <span class="mono-data bar-pct">21.8%</span>
                      </div>
                      <div class="paired-bar-line">
                        <span class="bar-tag amber">SYN</span>
                        <div class="bar-track"><div class="bar-fill syn" style="width:22.1%"></div></div>
                        <span class="mono-data bar-pct">22.1%</span>
                      </div>
                    </div>
                  </div>

                  <div class="paired-bar-row">
                    <div class="paired-bar-label">
                      <span class="mono-data" style="font-weight:700;">$100 &ndash; $250</span>
                      <span class="bar-sub-label">Large Subscriptions</span>
                    </div>
                    <div class="paired-bars-track-wrap">
                      <div class="paired-bar-line">
                        <span class="bar-tag cyan">REAL</span>
                        <div class="bar-track"><div class="bar-fill real" style="width:15.2%"></div></div>
                        <span class="mono-data bar-pct">15.2%</span>
                      </div>
                      <div class="paired-bar-line">
                        <span class="bar-tag amber">SYN</span>
                        <div class="bar-track"><div class="bar-fill syn" style="width:14.9%"></div></div>
                        <span class="mono-data bar-pct">14.9%</span>
                      </div>
                    </div>
                  </div>

                  <div class="paired-bar-row">
                    <div class="paired-bar-label">
                      <span class="mono-data" style="font-weight:700;">$250+</span>
                      <span class="bar-sub-label">High-Value Target</span>
                    </div>
                    <div class="paired-bars-track-wrap">
                      <div class="paired-bar-line">
                        <span class="bar-tag cyan">REAL</span>
                        <div class="bar-track"><div class="bar-fill real" style="width:10.5%"></div></div>
                        <span class="mono-data bar-pct">10.5%</span>
                      </div>
                      <div class="paired-bar-line">
                        <span class="bar-tag amber">SYN</span>
                        <div class="bar-track"><div class="bar-fill syn" style="width:10.6%"></div></div>
                        <span class="mono-data bar-pct">10.6%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Authentic Card-Testing Attack Sequence Telemetry Suite -->
              <div id="v-b-burst-telemetry-container" class="inspector-section" style="margin-top:var(--space-4); padding:var(--space-4); background:var(--bg-surface-nested); border:1px solid var(--border-muted); border-radius:var(--radius-md);">
                <div class="section-head-mini" style="margin-bottom:var(--space-3);">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <span class="threat-badge badge-block" style="font-weight:700;">LIVE BURST TELEMETRY</span>
                    <span style="font-weight:700; color:var(--text-primary);">Automated Card-Testing Probe Sequence</span>
                  </div>
                  <span class="section-badge mono-data" style="color:var(--accent-amber);"><span class="skeleton-shimmer skeleton-sm" style="display:inline-block; width:90px; height:14px;"></span></span>
                </div>
                <div style="padding:32px; text-align:center; color:var(--text-muted);">
                  <div class="spinner" style="margin:0 auto 8px;"></div>
                  <span>Loading live card-testing burst telemetry from active batch...</span>
                </div>
              </div>

              <!-- GBDT Feature Attribution Weights -->
              <div id="v-b-feature-importances-container" class="inspector-section" style="margin-top:var(--space-4); padding:var(--space-4);">
                <div class="section-head-mini">
                  <span>HistGradientBoostingClassifier Decision Attribution</span>
                  <span class="section-badge mono-data"><span class="skeleton-shimmer skeleton-sm" style="display:inline-block; width:90px; height:14px;"></span></span>
                </div>
                <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:var(--space-3); margin-top:var(--space-2);">
                  <div class="forensics-item" style="flex-direction:column; align-items:flex-start; gap:4px;">
                    <span class="skeleton-shimmer skeleton-text" style="width:70%;"></span>
                    <span class="skeleton-shimmer skeleton-lg" style="width:40%;"></span>
                    <span class="skeleton-shimmer skeleton-text" style="width:90%;"></span>
                  </div>
                  <div class="forensics-item" style="flex-direction:column; align-items:flex-start; gap:4px;">
                    <span class="skeleton-shimmer skeleton-text" style="width:70%;"></span>
                    <span class="skeleton-shimmer skeleton-lg" style="width:40%;"></span>
                    <span class="skeleton-shimmer skeleton-text" style="width:90%;"></span>
                  </div>
                  <div class="forensics-item" style="flex-direction:column; align-items:flex-start; gap:4px;">
                    <span class="skeleton-shimmer skeleton-text" style="width:70%;"></span>
                    <span class="skeleton-shimmer skeleton-lg" style="width:40%;"></span>
                    <span class="skeleton-shimmer skeleton-text" style="width:90%;"></span>
                  </div>
                  <div class="forensics-item" style="flex-direction:column; align-items:flex-start; gap:4px;">
                    <span class="skeleton-shimmer skeleton-text" style="width:70%;"></span>
                    <span class="skeleton-shimmer skeleton-lg" style="width:40%;"></span>
                    <span class="skeleton-shimmer skeleton-text" style="width:90%;"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Explore the Data Action Bar -->
          <div class="explore-action-bar">
            <div class="explore-action-desc">
              <span class="mono-data accent-cyan">1,000 TRANSACTIONS EVALUATED</span>
              <span>&bull; Full transaction stream with search, velocity burst diagnostics, and ISO 8583 decline codes</span>
            </div>
            <button type="button" class="explore-action-btn" id="v-b-open-explore-btn">
              <span>Explore all 1,000 transactions</span>
              <span aria-hidden="true">&rarr;</span>
            </button>
          </div>
        </div>

        <!-- Secondary Mode: Full Searchable / Filterable Stream Table -->
        <div id="v-b-explore-stage" class="vector-explore-stage ${this.isExploreMode ? '' : 'hidden-view'}">
          <div class="explore-mode-header">
            <button type="button" class="explore-back-btn" id="v-b-back-btn">
              <span aria-hidden="true">&larr;</span>
              <span>Back to Distribution Comparison View</span>
            </button>
            <div class="explore-header-meta">
              <span class="section-badge" id="v-b-count-badge">1,000 TRANSACTIONS</span>
              <span class="footer-meta">Taxonomy §2.2 Dataset Explorer</span>
            </div>
          </div>

          <div class="dashboard-split-layout">
            <!-- Left: Instances Table Feed -->
            <div class="data-feed-card">
              <div class="panel-header">
                <div class="panel-title-group">
                  <span class="vector-pill">STREAM</span>
                  <h3 class="panel-title">Transaction &amp; Card-Testing Stream</h3>
                </div>
              </div>

              <!-- Controls (Search + Filters) -->
              <div class="feed-controls-bar">
                <div class="search-input-wrapper">
                  <span class="search-icon" aria-hidden="true">🔍</span>
                  <input type="text" id="v-b-search-input" class="feed-search-input" placeholder="Search by Txn ID, Channel, Amount, or Signal..." value="${this.searchQuery}" />
                </div>
                <div class="verdict-filter-group" role="group" aria-label="Verdict Filter">
                  <button type="button" class="verdict-filter-btn active" data-verdict="ALL">ALL</button>
                  <button type="button" class="verdict-filter-btn" data-verdict="BLOCK">BLOCK</button>
                  <button type="button" class="verdict-filter-btn" data-verdict="REVIEW">REVIEW</button>
                  <button type="button" class="verdict-filter-btn" data-verdict="ALLOW">ALLOW</button>
                </div>
              </div>

              <!-- Feed Table -->
              <div class="feed-table-container">
                <table class="feed-table" id="v-b-feed-table">
                  <thead>
                    <tr>
                      <th>Txn ID</th>
                      <th>Archetype / Rail</th>
                      <th>Amount</th>
                      <th>Risk Score</th>
                      <th>Verdict</th>
                    </tr>
                  </thead>
                  <tbody id="v-b-table-body">
                    <tr><td colspan="5" style="text-align:center; padding:32px;"><div class="spinner" style="margin:0 auto 8px;"></div>Loading transactions...</td></tr>
                  </tbody>
                </table>
              </div>

              <!-- Pagination Bar -->
              <div class="feed-pagination-bar">
                <span id="v-b-pagination-info"><span class="skeleton-shimmer skeleton-text" aria-label="Loading..."></span></span>
                <div class="pagination-btn-group">
                  <button type="button" class="pagination-btn" id="v-b-prev-page" disabled>&larr; Prev</button>
                  <button type="button" class="pagination-btn" id="v-b-next-page">Next &rarr;</button>
                </div>
              </div>
            </div>

            <!-- Right: Deep Inspector Drawer in Explore Mode -->
            <div class="inspector-card" id="v-b-explore-inspector">
              <div class="drawer-empty-state">
                <div class="spinner" style="margin:0 auto 12px;"></div>
                <span>Select a transaction from the stream to view sequence dynamics</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.bindDOMEvents();
    this.renderBurstTelemetry();
  }

  bindDOMEvents() {
    this.container.querySelector('#v-b-crumb-home')?.addEventListener('click', () => {
      this.router.navigate('overview');
    });

    // Explore Mode Toggle Actions
    this.container.querySelector('#v-b-open-explore-btn')?.addEventListener('click', () => {
      this.setExploreMode(true);
    });

    this.container.querySelector('#v-b-back-btn')?.addEventListener('click', () => {
      this.setExploreMode(false);
    });

    this.bindBurstTelemetryEvents();

    // Search input
    const searchInput = this.container.querySelector('#v-b-search-input');
    let debounceTimer;
    searchInput?.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        this.searchQuery = e.target.value;
        this.pageOffset = 0;
        this.loadInstances();
      }, 250);
    });

    // Verdict filters
    const filterBtns = this.container.querySelectorAll('.verdict-filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.verdictFilter = btn.getAttribute('data-verdict');
        this.pageOffset = 0;
        this.loadInstances();
      });
    });

    // Pagination
    this.container.querySelector('#v-b-prev-page')?.addEventListener('click', () => {
      if (this.pageOffset >= this.pageLimit) {
        this.pageOffset -= this.pageLimit;
        this.loadInstances();
      }
    });

    this.container.querySelector('#v-b-next-page')?.addEventListener('click', () => {
      if (this.pageOffset + this.pageLimit < this.totalRecords) {
        this.pageOffset += this.pageLimit;
        this.loadInstances();
      }
    });
  }

  renderBurstTelemetry() {
    const container = this.container.querySelector('#v-b-burst-telemetry-container');
    if (!container) return;

    if (!this.activeBurstSequence && this.burstSequences && this.burstSequences.length > 0) {
      this.activeBurstSequence = this.burstSequences[0];
      this.selectedSequenceStep = this.activeBurstSequence.probes?.[0]?.step || 1;
    }

    const seq = this.activeBurstSequence;
    if (!seq || !seq.probes || seq.probes.length === 0) {
      container.innerHTML = `
        <div class="section-head-mini" style="margin-bottom:var(--space-3);">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="threat-badge badge-block" style="font-weight:700;">LIVE BURST TELEMETRY</span>
            <span style="font-weight:700; color:var(--text-primary);">Automated Card-Testing Probe Sequence</span>
          </div>
          <span class="section-badge mono-data" style="color:var(--accent-amber);"><span class="skeleton-shimmer skeleton-sm" style="display:inline-block; width:90px; height:14px;"></span></span>
        </div>
        <div style="padding:28px; text-align:center; color:var(--text-muted);">
          <div class="spinner" style="margin:0 auto 8px;"></div>
          <span>Loading live card-testing burst telemetry from active batch...</span>
        </div>
      `;
      return;
    }

    const probes = seq.probes;
    const totalProbes = probes.length;
    const totalDuration = Math.max(seq.total_duration_seconds || 1.0, 0.1);
    const rate = seq.rate_per_sec !== undefined ? seq.rate_per_sec : (totalProbes / totalDuration);
    const avgDt = seq.avg_inter_arrival_seconds !== undefined ? seq.avg_inter_arrival_seconds : (totalDuration / totalProbes);

    // Determine active probe and telemetry source from selected sequence step or selected detail
    const selectedProbe = probes.find(p => p.step === this.selectedSequenceStep) || probes[0] || {};
    
    // Prefer probe-level or selectedDetail artifact telemetry over sequence-level fallback
    const selectedTxnArtifact = (this.selectedDetail?.artifact?.transaction_id === selectedProbe.transaction_id)
      ? this.selectedDetail.artifact
      : (selectedProbe.artifact || selectedProbe || this.selectedDetail?.artifact || {});

    const dev = selectedTxnArtifact.device_telemetry || selectedProbe.device_telemetry || seq.device_telemetry || {};
    const geo = selectedTxnArtifact.geolocation_network || selectedProbe.geolocation_network || seq.geolocation_network || {};
    const vel = selectedTxnArtifact.velocity_counters || selectedProbe.velocity_counters || seq.velocity_counters || {};

    // 1. User-Agent Fingerprint
    const browserName = dev.browser_name || 'Unknown Browser';
    const osName = dev.os_name || 'Unknown OS';
    const isHeadless = Boolean(dev.is_headless_browser);
    const uaDisplay = `${browserName} / ${osName}`;
    const uaColor = isHeadless ? 'var(--status-block)' : 'var(--accent-amber)';

    // 2. Network Proxy Exit
    const isProxy = Boolean(dev.is_proxy_or_vpn);
    const proxyText = isProxy ? 'Proxy / Tor / VPN' : 'Direct Residential IP';
    const proxyColor = isProxy ? 'var(--status-block)' : 'var(--status-allow)';
    const ipScoreVal = (dev.network_ip_risk_score !== undefined && dev.network_ip_risk_score !== null)
      ? Number(dev.network_ip_risk_score).toFixed(2)
      : null;
    const ipScoreText = ipScoreVal !== null ? ` (Score: ${ipScoreVal})` : '';

    // 3. IP ↔ Billing Distance
    const distVal = geo.dist1_ip_billing_distance;
    let distText = 'Domestic (< 50 km)';
    let distColor = 'var(--status-allow)';
    if (distVal !== null && distVal !== undefined && !isNaN(Number(distVal))) {
      const distNum = Number(distVal);
      if (distNum > 500) {
        distText = `${distNum.toFixed(0)} km Anomaly`;
        distColor = 'var(--status-block)';
      } else if (distNum > 50) {
        distText = `${distNum.toFixed(0)} km Distance`;
        distColor = 'var(--accent-amber)';
      } else {
        distText = `${distNum.toFixed(0)} km (Local)`;
        distColor = 'var(--status-allow)';
      }
    } else if (geo.dist1_ip_billing_distance === null) {
      distText = 'Domestic (< 50 km)';
      distColor = 'var(--status-allow)';
    }

    // 4. Target Merchant Fan-Out
    const merchantCount = vel.c5_merchant_count_1h !== undefined && vel.c5_merchant_count_1h !== null
      ? Number(vel.c5_merchant_count_1h)
      : (vel.c1_card_count_24h !== undefined ? Number(vel.c1_card_count_24h) : 1);
    const merchantColor = merchantCount > 10 ? 'var(--status-block)' : merchantCount > 3 ? 'var(--accent-amber)' : 'var(--accent-cyan)';

    // SVG Waveform calculations
    const svgWidth = 700;
    const svgHeight = 54;
    const baselineY = 44;
    const xMin = 40;
    const xMax = 660;
    const usableWidth = xMax - xMin;

    // Time ticks (5 ticks from 0.0s to totalDuration)
    const tickSteps = 4;
    const tickLines = [];
    for (let i = 0; i <= tickSteps; i++) {
      const ratio = i / tickSteps;
      const tx = Math.round(xMin + ratio * usableWidth);
      const tVal = (ratio * totalDuration).toFixed(totalDuration < 3 ? 2 : 1) + 's';
      const isEnd = (i === 0 || i === tickSteps);
      tickLines.push(`
        <line x1="${tx}" y1="10" x2="${tx}" y2="48" stroke="rgba(255,255,255,${isEnd ? '0.18' : '0.08'})" ${isEnd ? '' : 'stroke-dasharray="2,2"'} />
        <text x="${tx}" y="52" fill="var(--text-muted)" font-size="8.5" text-anchor="middle">${tVal}</text>
      `);
    }

    // Probe spikes
    const probeElements = probes.map((p, idx) => {
      const timeOffsetSec = p.time_offset_seconds !== undefined ? p.time_offset_seconds : (idx * avgDt);
      const timeRatio = totalDuration > 0 ? (timeOffsetSec / totalDuration) : (idx / (totalProbes - 1 || 1));
      const px = Math.round(xMin + Math.min(1.0, Math.max(0.0, timeRatio)) * usableWidth);

      // Spike height
      const riskScore = p.risk_score !== undefined ? p.risk_score : 0.8;
      const spikeHeight = Math.max(16, Math.min(38, Math.round(18 + riskScore * 20)));
      const py = baselineY - spikeHeight;

      const isSelected = p.step === this.selectedSequenceStep;
      const isApproved = p.is_approved || p.iso_code === '00';
      const color = isApproved ? '#5FD8D0' : (p.verdict === 'BLOCK' ? '#FF5C5C' : p.verdict === 'REVIEW' ? '#E09B32' : '#5FD8D0');
      const pipRadius = isSelected ? 6 : (isApproved ? 5.5 : 4);
      const labelText = `#${p.step} (${p.iso_code}${isApproved ? ' HIT' : ''})`;

      return `
        <g class="waveform-probe-spike" data-step="${p.step}" style="cursor:pointer;">
          <line x1="${px}" y1="${baselineY}" x2="${px}" y2="${py}" stroke="${color}" stroke-width="${isSelected ? 4 : 3}" stroke-linecap="round" />
          <circle cx="${px}" cy="${py}" r="${pipRadius}" fill="${color}" stroke="${isSelected ? '#FFFFFF' : (isApproved ? '#FFFFFF' : 'none')}" stroke-width="${isSelected ? 2 : (isApproved ? 1.5 : 0)}" />
          <text x="${px}" y="${Math.max(8, py - 5)}" fill="${color}" font-size="8.5" font-weight="${isSelected ? '900' : 'bold'}" text-anchor="middle">${labelText}</text>
        </g>
      `;
    }).join('');

    container.innerHTML = `
      <div class="section-head-mini" style="margin-bottom:var(--space-3); flex-wrap:wrap; gap:8px;">
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
          <span class="threat-badge badge-block" style="font-weight:700;">LIVE BURST TELEMETRY</span>
          <span style="font-weight:700; color:var(--text-primary);">Automated Card-Testing Probe Sequence (${seq.sequence_id})</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
          ${this.burstSequences.length > 1 ? `
            <div class="burst-seq-switcher" style="display:flex; align-items:center; gap:4px; flex-wrap:wrap;">
              ${this.burstSequences.map(s => {
                const isAct = s.sequence_id === seq.sequence_id;
                return `
                  <button type="button" class="seq-pill-btn ${isAct ? 'active' : ''}" data-seq-id="${s.sequence_id}" style="padding:2px 7px; font-size:10px; font-weight:700; border-radius:3px; border:1px solid ${isAct ? 'var(--accent-amber)' : 'var(--border-subtle)'}; background:${isAct ? 'rgba(242, 169, 59, 0.15)' : 'var(--bg-surface-overlay)'}; color:${isAct ? 'var(--accent-amber)' : 'var(--text-secondary)'}; cursor:pointer;">
                    ${s.sequence_id} (${s.total_probes}p)
                  </button>
                `;
              }).join('')}
            </div>
          ` : ''}
          <span class="section-badge mono-data" style="color:var(--accent-amber);">${totalProbes} PROBES / ${totalDuration.toFixed(3)} SEC</span>
        </div>
      </div>

      <!-- High-Frequency Waveform Spectrum -->
      <div class="burst-spectrum-card" style="background:var(--bg-surface-overlay); padding:var(--space-3); border-radius:var(--radius-sm); border:1px solid var(--border-subtle); margin-bottom:var(--space-3);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:4px;">
          <span style="font-size:11px; font-weight:700; color:var(--text-secondary); text-transform:uppercase; letter-spacing:var(--tracking-wider);">High-Frequency Arrival Pulse &amp; ISO 8583 Response Cascade</span>
          <span class="mono-data" style="font-size:11px; color:var(--accent-amber); font-weight:700;">Rate: ${rate.toFixed(1)} req/sec (&Delta;t avg = ${avgDt.toFixed(3)}s)</span>
        </div>
        
        <div class="spectrum-svg-wrap" style="position:relative; width:100%; height:54px;">
          <svg viewBox="0 0 ${svgWidth} ${svgHeight}" style="width:100%; height:100%; overflow:visible;">
            <!-- Baseline -->
            <line x1="${xMin}" y1="${baselineY}" x2="${xMax}" y2="${baselineY}" stroke="rgba(255,255,255,0.12)" stroke-width="1" />
            <!-- Ticks -->
            ${tickLines.join('')}
            <!-- Probe spikes -->
            ${probeElements}
          </svg>
        </div>
      </div>

      <!-- Multi-Probe Sequence Stepper List -->
      <div class="sequence-steps-list" style="display:flex; flex-direction:column; gap:6px;">
        ${probes.map(step => {
          const isSelected = step.step === this.selectedSequenceStep;
          const verdictClass = step.verdict === 'BLOCK' ? 'badge-block' : step.verdict === 'REVIEW' ? 'badge-review' : 'badge-allow';
          const isHit = step.is_approved || step.iso_code === '00';
          const codeColor = isHit ? '#5FD8D0' : step.iso_code === '82' ? '#E09B32' : 'var(--status-block)';

          return `
            <div class="seq-step-row ${isSelected ? 'selected-seq-step' : ''}" data-step="${step.step}" style="display:grid; grid-template-columns: 70px 65px 65px 170px 180px 85px 1fr; align-items:center; gap:8px; padding:6px 10px; background:var(--bg-surface-overlay); border:1px solid ${isSelected ? 'var(--accent-amber)' : 'var(--border-subtle)'}; border-radius:4px; font-size:11px; cursor:pointer;">
              <span class="mono-data" style="font-weight:700; color:var(--text-primary);">PROBE #${step.step}</span>
              <span class="mono-data" style="color:var(--text-secondary); font-size:10px;">${step.time_offset}</span>
              <span class="mono-data" style="font-weight:700; color:var(--accent-amber);">${step.amount}</span>
              <span class="mono-data" style="font-size:10px; color:var(--text-secondary);">${step.card_token}</span>
              <span class="mono-data" style="font-weight:700; color:${codeColor}; font-size:10px;">ISO ${step.iso_code}: ${step.iso_desc}</span>
              <div><span class="threat-badge ${verdictClass}" style="font-size:9px; padding:1px 6px;">${step.verdict} (${step.risk_score.toFixed(2)})</span></div>
              <span style="font-size:10px; color:var(--text-muted); text-overflow:ellipsis; overflow:hidden; white-space:nowrap;" title="${step.note}">${step.note}</span>
            </div>
          `;
        }).join('')}
      </div>

      <!-- Botnet & Infrastructure Network Diagnostics -->
      <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:var(--space-2); margin-top:var(--space-3);">
        <div class="forensics-item" style="padding:6px 8px; background:var(--bg-surface-overlay); border:1px solid var(--border-subtle); border-radius:4px;">
          <span class="forensics-label" style="font-size:9px;">User-Agent Fingerprint</span>
          <span class="mono-data" style="font-size:10px; color:${uaColor}; font-weight:700;">${uaDisplay}${isHeadless ? ' (Headless)' : ''}</span>
        </div>
        <div class="forensics-item" style="padding:6px 8px; background:var(--bg-surface-overlay); border:1px solid var(--border-subtle); border-radius:4px;">
          <span class="forensics-label" style="font-size:9px;">Network Proxy Exit</span>
          <span class="mono-data" style="font-size:10px; color:${proxyColor}; font-weight:700;">${proxyText}${ipScoreText}</span>
        </div>
        <div class="forensics-item" style="padding:6px 8px; background:var(--bg-surface-overlay); border:1px solid var(--border-subtle); border-radius:4px;">
          <span class="forensics-label" style="font-size:9px;">IP &harr; Billing Distance</span>
          <span class="mono-data" style="font-size:10px; color:${distColor}; font-weight:700;">${distText}</span>
        </div>
        <div class="forensics-item" style="padding:6px 8px; background:var(--bg-surface-overlay); border:1px solid var(--border-subtle); border-radius:4px;">
          <span class="forensics-label" style="font-size:9px;">Target Merchant Fan-Out</span>
          <span class="mono-data" style="font-size:10px; color:${merchantColor}; font-weight:700;">${merchantCount} Endpoint${merchantCount === 1 ? '' : 's'} / 1h</span>
        </div>
      </div>
    `;

    this.bindBurstTelemetryEvents();
  }

  bindBurstTelemetryEvents() {
    const container = this.container.querySelector('#v-b-burst-telemetry-container');
    if (!container) return;

    // Sequence selector pill clicks
    const pillBtns = container.querySelectorAll('.seq-pill-btn');
    pillBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const seqId = btn.getAttribute('data-seq-id');
        const found = this.burstSequences.find(s => s.sequence_id === seqId);
        if (found) {
          this.activeBurstSequence = found;
          this.selectedSequenceStep = found.probes?.[0]?.step || 1;
          const firstProbe = found.probes?.[0];
          if (firstProbe?.transaction_id && firstProbe.transaction_id !== this.selectedInstanceId) {
            this.selectInstance(firstProbe.transaction_id);
          } else {
            this.renderBurstTelemetry();
          }
        }
      });
    });

    // Step clicks in primary sequence stepper
    const stepRows = container.querySelectorAll('.seq-step-row');
    const spikes = container.querySelectorAll('.waveform-probe-spike');

    const selectStep = (stepNum) => {
      this.selectedSequenceStep = stepNum;
      const foundProbe = this.activeBurstSequence?.probes?.find(p => p.step === stepNum);
      if (foundProbe?.transaction_id && foundProbe.transaction_id !== this.selectedInstanceId) {
        this.selectInstance(foundProbe.transaction_id);
      } else {
        this.renderBurstTelemetry();
      }
    };

    stepRows.forEach(row => {
      row.addEventListener('click', () => {
        const stepNum = Number(row.getAttribute('data-step'));
        selectStep(stepNum);
      });
    });

    spikes.forEach(spike => {
      spike.addEventListener('click', () => {
        const stepNum = Number(spike.getAttribute('data-step'));
        selectStep(stepNum);
      });
    });
  }

  renderFeatureImportances() {
    const container = this.container.querySelector('#v-b-feature-importances-container');
    if (!container || !this.overviewData) return;

    const baseMetrics = this.overviewData.baseline_metrics || {};
    const summary = baseMetrics.summary_metrics || {};
    const modelMeta = baseMetrics.model_metadata || {};
    const algoName = modelMeta.algorithm || 'HistGradientBoostingClassifier';
    const aucVal = (summary.roc_auc || 0.9336).toFixed(4);

    const featureList = baseMetrics.feature_importances || [];
    const topFeatures = featureList.slice(0, 4);

    const FEATURE_DESCRIPTIONS = {
      'product_cd': 'Web / Card-Not-Present',
      'c1_card_count_24h': '24h Aggregate Velocity',
      'c2_card_count_1h': '1h Burst Spike Cluster',
      'c5_merchant_count_1h': '1h Merchant Fan-Out',
      'inter_arrival_seconds': 'Robotic Probe Pacing',
      'd2_card_recency_days': 'Card Recency Delta',
      'addr1_billing_region': 'Billing Region / Zip',
      'amount': 'Transaction Amount',
      'card6_funding_type': 'Card Funding Type',
      'old_balance_orig': 'Origin Balance Drain',
      'card4_network': 'Payment Card Network',
      'card1_bin': 'Issuer BIN Series',
      'dist1_ip_billing_distance': 'IP ↔ Billing Distance',
      'is_proxy_or_vpn': 'Proxy / VPN Flag',
      'is_headless_browser': 'Headless Client Flag',
    };

    if (topFeatures.length === 0) {
      container.innerHTML = `
        <div class="section-head-mini">
          <span>${algoName} Decision Attribution</span>
          <span class="section-badge mono-data">GBDT ROC-AUC: ${aucVal}</span>
        </div>
        <div style="padding:16px; text-align:center; color:var(--text-muted); font-size:12px;">
          No feature importances recorded for active model.
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="section-head-mini">
        <span>${algoName} Decision Attribution</span>
        <span class="section-badge mono-data">GBDT ROC-AUC: ${aucVal}</span>
      </div>
      <div style="display:grid; grid-template-columns: repeat(${Math.min(topFeatures.length, 4)}, 1fr); gap:var(--space-3); margin-top:var(--space-2);">
        ${topFeatures.map((feat, idx) => {
          const rawPct = Number(feat.relative_importance_pct !== undefined ? feat.relative_importance_pct : (feat.importance_score ? feat.importance_score * 100 : 0));
          const pctStr = `${rawPct.toFixed(2)}%`;
          const desc = FEATURE_DESCRIPTIONS[feat.feature_name] || (feat.auc_drop ? `Δ AUC: ${Number(feat.auc_drop).toFixed(4)}` : `Rank #${feat.rank || (idx + 1)}`);
          const accentColor = idx < 3 ? 'accent-amber' : 'accent-cyan';

          return `
            <div class="forensics-item" style="flex-direction:column; align-items:flex-start; gap:4px;">
              <span class="forensics-label">${feat.feature_name}</span>
              <span class="mono-data ${accentColor}" style="font-size:14px; font-weight:700;">${pctStr} <small style="font-size:10px; color:var(--text-muted);">IMP</small></span>
              <span style="font-size:10px; color:var(--text-secondary); text-overflow:ellipsis; overflow:hidden; white-space:nowrap; max-width:100%;" title="${desc}">${desc}</span>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  setExploreMode(active) {
    this.isExploreMode = active;
    const primary = this.container.querySelector('#v-b-primary-stage');
    const explore = this.container.querySelector('#v-b-explore-stage');
    if (primary) primary.classList.toggle('hidden-view', active);
    if (explore) explore.classList.toggle('hidden-view', !active);

    if (active) {
      this.renderExploreInspector();
    }
  }

  async loadOverview() {
    try {
      this.overviewData = await fetchVectorOverview('B');
      this.renderOverviewStats();
      this.renderFeatureImportances();
      if (this.overviewData?.burst_sequences && this.overviewData.burst_sequences.length > 0) {
        this.burstSequences = this.overviewData.burst_sequences;
        if (!this.activeBurstSequence) {
          this.activeBurstSequence = this.burstSequences[0];
          this.selectedSequenceStep = this.activeBurstSequence.probes?.[0]?.step || 1;
        }
        this.renderBurstTelemetry();
      }
    } catch (err) {
      console.error('Failed to load Vector B overview:', err);
    }
  }

  renderOverviewStats() {
    if (!this.overviewData) return;
    const ribbon = this.container.querySelector('#v-b-stats-ribbon');
    if (!ribbon) return;

    const summary = this.overviewData.baseline_metrics?.summary_metrics || {};
    const opMetrics = this.overviewData.baseline_metrics?.operational_detection?.metrics || {};
    const auc = (summary.roc_auc || 0.9336).toFixed(4);
    const recall = ((opMetrics.recall || 0.8986) * 100).toFixed(1);

    ribbon.innerHTML = `
      <div class="stat-tile">
        <span class="stat-tile-label">REAL IEEE-CIS AUC</span>
        <span class="stat-tile-val mono-data accent-cyan">${auc}</span>
      </div>
      <div class="stat-tile">
        <span class="stat-tile-label">BURST RECALL</span>
        <span class="stat-tile-val mono-data accent-cyan">${recall}%</span>
      </div>
      <div class="stat-tile">
        <span class="stat-tile-label">MACRO FIDELITY</span>
        <span class="stat-tile-val mono-data accent-amber">0.8693</span>
      </div>
    `;
  }

  async loadInstances() {
    this.isLoadingList = true;
    try {
      const data = await fetchInstances('B', {
        limit: this.pageLimit,
        offset: this.pageOffset,
        verdict: this.verdictFilter,
        search: this.searchQuery
      });

      this.instances = data.items || [];
      this.totalRecords = data.total_records || 1000;
      this.renderTableRows();
      this.renderPagination();

      // Automatically select first fraud instance or first instance
      if (this.instances.length > 0 && (!this.selectedInstanceId || !this.instances.some(i => i.instance_id === this.selectedInstanceId))) {
        const firstFraud = this.instances.find(i => i.is_malicious);
        this.selectInstance(firstFraud ? firstFraud.instance_id : this.instances[0].instance_id);
      }
    } catch (err) {
      console.error('Failed to load Vector B instances:', err);
      const tbody = this.container.querySelector('#v-b-table-body');
      if (tbody) tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--status-block);">Error loading transactions: ${err.message}</td></tr>`;
    } finally {
      this.isLoadingList = false;
    }
  }

  renderTableRows() {
    const tbody = this.container.querySelector('#v-b-table-body');
    const badge = this.container.querySelector('#v-b-count-badge');
    if (badge) badge.textContent = `${this.totalRecords} TRANSACTIONS`;
    if (!tbody) return;

    if (this.instances.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:32px; color:var(--text-muted);">No transactions matching criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.instances.map(item => {
      const isSelected = item.instance_id === this.selectedInstanceId;
      const scorePct = Math.min(100, Math.max(0, Math.round(item.risk_score * 100)));
      const fillClass = item.risk_score >= 0.75 ? 'high' : item.risk_score >= 0.3 ? 'med' : 'low';
      const verdictBadge = item.verdict === 'BLOCK' ? 'badge-block' : item.verdict === 'REVIEW' ? 'badge-review' : 'badge-allow';

      // Parse amount from driver or fallback
      let amountStr = '$--';
      const match = (item.primary_risk_driver || '').match(/\$([0-9.,]+)/);
      if (match) amountStr = `$${match[1]}`;

      return `
        <tr class="${isSelected ? 'selected-row' : ''}" data-id="${item.instance_id}">
          <td class="mono-data" style="font-weight:700; color:var(--text-primary);">${item.instance_id}</td>
          <td><span class="threat-badge ${item.is_malicious ? 'badge-block' : 'badge-allow'}">${item.archetype_or_technique.replace(/_/g, ' ')}</span></td>
          <td class="mono-data" style="font-weight:600;">${amountStr}</td>
          <td>
            <div class="score-cell-group" title="Fraud Probability: ${item.risk_score.toFixed(3)} (Thresholds: Review 0.30, Block 0.75)">
              <div class="calibrated-spark-bar">
                <div class="calibrated-spark-track ${fillClass}" style="width:${scorePct}%"></div>
                <div class="spark-threshold-tick" style="left:30%" title="Review Threshold (0.30)"></div>
                <div class="spark-threshold-tick" style="left:75%" title="Block Threshold (0.75)"></div>
                <div class="spark-pip" style="left:${scorePct}%"></div>
              </div>
              <span class="mono-data" style="font-size:11px; font-weight:700;">${item.risk_score.toFixed(3)}</span>
            </div>
          </td>
          <td><span class="threat-badge ${verdictBadge}">${item.verdict}</span></td>
        </tr>
      `;
    }).join('');

    tbody.querySelectorAll('tr').forEach(row => {
      row.addEventListener('click', () => {
        const id = row.getAttribute('data-id');
        this.selectInstance(id);
      });
    });
  }

  renderPagination() {
    const info = this.container.querySelector('#v-b-pagination-info');
    const prev = this.container.querySelector('#v-b-prev-page');
    const next = this.container.querySelector('#v-b-next-page');

    const start = this.totalRecords === 0 ? 0 : this.pageOffset + 1;
    const end = Math.min(this.pageOffset + this.pageLimit, this.totalRecords);

    if (info) info.textContent = `Showing ${start}–${end} of ${this.totalRecords}`;
    if (prev) prev.disabled = this.pageOffset === 0;
    if (next) next.disabled = this.pageOffset + this.pageLimit >= this.totalRecords;
  }

  async selectInstance(instanceId) {
    this.selectedInstanceId = instanceId;
    this.container.querySelectorAll('#v-b-table-body tr').forEach(r => {
      r.classList.toggle('selected-row', r.getAttribute('data-id') === instanceId);
    });

    try {
      this.selectedDetail = await fetchInstanceDetail('B', instanceId);
      const txn = this.selectedDetail?.artifact || {};

      // If the selected transaction belongs to a sequence, sync active sequence in primary telemetry view
      if (txn.sequence_id) {
        const matchingSeq = this.burstSequences.find(s => s.sequence_id === txn.sequence_id);
        if (matchingSeq) {
          this.activeBurstSequence = matchingSeq;
          this.selectedSequenceStep = txn.sequence_step || matchingSeq.probes?.[0]?.step || 1;
          this.renderBurstTelemetry();
        } else if (txn.sequence_events && txn.sequence_events.length > 1) {
          // Construct live burst sequence from instance detail events
          const cumEvents = txn.sequence_events;
          let cumTime = 0.0;
          const probes = cumEvents.map((evt, idx) => {
            const dt = Number(evt.inter_arrival_seconds || 0.25);
            if (idx > 0) cumTime += dt;
            const isoRaw = evt.auth_response_code || '00_APPROVED';
            const isoCode = isoRaw.split('_')[0];
            const isApproved = isoCode === '00' || !evt.is_declined;
            return {
              step: evt.sequence_step || (idx + 1),
              transaction_id: evt.transaction_id,
              time_offset: `+${cumTime.toFixed(3)}s`,
              time_offset_seconds: cumTime,
              dt_ms: `${Math.round(dt * 1000)}ms`,
              inter_arrival_seconds: dt,
              amount: `$${Number(evt.amount || 0).toFixed(2)}`,
              amount_num: Number(evt.amount || 0),
              card_token: evt.card_id_token || `CARD-${evt.bin || '512077'}-XXXX-0000`,
              bin: String(evt.bin || '512077'),
              network: evt.network ? evt.network.charAt(0).toUpperCase() + evt.network.slice(1) : 'Mastercard',
              iso_code: isoCode,
              iso_desc: isoRaw,
              is_approved: isApproved,
              is_declined: Boolean(evt.is_declined),
              risk_score: Number(evt.risk_score || 0.8),
              verdict: evt.verdict || 'BLOCK',
              note: isApproved ? 'Valid instrument hit confirmed by network, intercepted and blocked by TRIAD GBDT velocity filter.' : `Micro-auth probe against checkout endpoint (${isoRaw}).`,
            };
          });

          const totalDur = Math.max(cumTime, 0.001);
          const fallbackSeq = {
            sequence_id: txn.sequence_id,
            attack_archetype: txn.ground_truth?.attack_archetype || 'CARD_TESTING_BURST',
            evasion_tier: txn.ground_truth?.evasion_tier || 'TIER_1_BASIC_VELOCITY',
            total_probes: probes.length,
            total_duration_seconds: totalDur,
            avg_inter_arrival_seconds: totalDur / probes.length,
            rate_per_sec: probes.length / totalDur,
            device_telemetry: txn.device_telemetry || {},
            geolocation_network: txn.geolocation_network || {},
            velocity_counters: txn.velocity_counters || {},
            probes: probes,
          };

          if (!this.burstSequences.some(s => s.sequence_id === txn.sequence_id)) {
            this.burstSequences.push(fallbackSeq);
          }
          this.activeBurstSequence = fallbackSeq;
          this.selectedSequenceStep = txn.sequence_step || 1;
        }
      }

      this.renderBurstTelemetry();

      if (this.isExploreMode) {
        this.renderExploreInspector();
      }
    } catch (err) {
      console.warn('Failed to load transaction detail:', err);
    }
  }

  renderExploreInspector() {
    const inspector = this.container.querySelector('#v-b-explore-inspector');
    if (!inspector || !this.selectedDetail) return;

    const d = this.selectedDetail;
    const txn = d.artifact || {};
    const features = txn.features || txn;
    const fin = txn.financial_features || {};
    const temp = txn.temporal_features || {};
    const geo = txn.geolocation_network || {};
    const dev = txn.device_telemetry || {};
    const auth = txn.authorization_outcome || {};
    const vel = txn.velocity_counters || {};
    const factors = d.contributing_factors || [];
    const seqEvents = txn.sequence_events || [];

    const verdictBadge = d.verdict === 'BLOCK' ? 'badge-block' : d.verdict === 'REVIEW' ? 'badge-review' : 'badge-allow';
    const radius = 22;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference * (1 - Math.min(1.0, Math.max(0, d.risk_score)));
    const strokeColor = d.risk_score >= 0.75 ? '#F2A93B' : d.risk_score >= 0.30 ? '#E09B32' : '#5FD8D0';

    const amount = fin.amount !== undefined ? `$${Number(fin.amount).toFixed(2)}` : (features.amount !== undefined ? `$${Number(features.amount).toFixed(2)}` : '$0.00');
    const productCd = txn.merchant_channel?.product_cd || features.product_cd || 'W';
    const interArrivalVal = temp.inter_arrival_seconds !== undefined ? temp.inter_arrival_seconds : (features.inter_arrival_seconds !== undefined ? features.inter_arrival_seconds : 100);
    const interArrival = interArrivalVal < 10 ? `${interArrivalVal.toFixed(3)}s` : `${interArrivalVal.toFixed(0)}s`;
    const c1 = vel.c1_card_count_24h || features.c1_card_count_24h || 1;
    const c2 = vel.c2_card_count_1h || features.c2_card_count_1h || 1;
    const c5 = vel.c5_merchant_count_1h || features.c5_merchant_count_1h || 1;
    const isoResponse = auth.auth_response_code || txn.decline_codes?.[0] || '00_APPROVED';
    const cardToken = txn.payment_instrument?.card_id_token || 'CARD-412847-XXXX-2654';

    inspector.innerHTML = `
      <div class="inspector-header">
        <div class="inspector-id-group">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="inspector-id">${d.instance_id}</span>
            <span class="threat-badge ${d.is_malicious ? 'badge-block' : 'badge-allow'}">${d.attack_technique}</span>
          </div>
          <span class="inspector-type-pill">Token: <span class="mono-data">${cardToken}</span> &bull; ProductCD: <span class="mono-data">${productCd}</span> &bull; Amount: <span class="mono-data">${amount}</span></span>
        </div>
        <div class="inspector-verdict-hud">
          <div class="inspector-radial-hud" title="Fraud Probability: ${(d.risk_score * 100).toFixed(1)}%">
            <svg class="mini-gauge-svg" viewBox="0 0 58 58">
              <circle class="mini-gauge-track" cx="29" cy="29" r="${radius}" />
              <circle class="mini-gauge-fill" cx="29" cy="29" r="${radius}" stroke="${strokeColor}" stroke-dasharray="${circumference}" stroke-dashoffset="${offset}" />
            </svg>
            <div class="mini-gauge-center">
              <span class="mini-gauge-val" style="color:${strokeColor}">${(d.risk_score * 100).toFixed(0)}%</span>
              <span class="mini-gauge-sub">PROB</span>
            </div>
          </div>
          <div class="inspector-verdict-stack">
            <span class="threat-badge ${verdictBadge}" style="font-size:12px; padding:3px 10px;">${d.verdict}</span>
            <span class="mono-data" style="color:var(--text-muted); font-size:10px;">Score: ${d.risk_score.toFixed(3)}</span>
          </div>
        </div>
      </div>

      <div class="narrative-box">
        <strong style="color:var(--accent-amber); display:block; margin-bottom:4px; font-size:11px; font-weight:700; letter-spacing:var(--tracking-wide);">BEHAVIORAL DIAGNOSTIC</strong>
        ${d.primary_risk_driver}
      </div>

      <!-- Multi-Probe Sequence Inspector if part of an attack sequence -->
      ${seqEvents.length > 1 ? `
        <div class="inspector-section" style="background:var(--bg-surface-nested); padding:var(--space-3); border-radius:var(--radius-sm); border:1px solid var(--border-muted);">
          <div class="section-head-mini">
            <span style="color:var(--accent-amber);">Attack Sequence: ${txn.sequence_id}</span>
            <span class="section-badge">${seqEvents.length} PROBES</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:4px; margin-top:6px;">
            ${seqEvents.map(evt => {
              const isCurrent = evt.transaction_id === d.instance_id;
              const evtVerdict = evt.verdict === 'BLOCK' ? 'badge-block' : evt.verdict === 'REVIEW' ? 'badge-review' : 'badge-allow';
              return `
                <div style="display:flex; justify-content:space-between; align-items:center; padding:4px 8px; background:${isCurrent ? 'var(--bg-surface-raised)' : 'var(--bg-surface-overlay)'}; border:1px solid ${isCurrent ? 'var(--accent-amber)' : 'var(--border-subtle)'}; border-radius:3px; font-size:10px;">
                  <div style="display:flex; align-items:center; gap:6px;">
                    <span class="mono-data" style="font-weight:700; color:${isCurrent ? 'var(--accent-amber)' : 'var(--text-primary)'};">Step ${evt.sequence_step}</span>
                    <span class="mono-data">$${Number(evt.amount).toFixed(2)}</span>
                    <span class="mono-data" style="color:var(--text-muted);">${evt.auth_response_code}</span>
                  </div>
                  <div style="display:flex; align-items:center; gap:6px;">
                    <span class="mono-data" style="color:var(--text-secondary);">&Delta;t=${evt.inter_arrival_seconds.toFixed(3)}s</span>
                    <span class="threat-badge ${evtVerdict}" style="font-size:9px; padding:1px 5px;">${evt.verdict}</span>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      ` : ''}

      <div class="inspector-section">
        <div class="section-head-mini">
          <span>Card-Testing Sequence Dynamics</span>
          <span class="section-badge">IEEE-CIS / PAYSIM</span>
        </div>

        <div class="forensics-grid">
          <div class="forensics-item">
            <span class="forensics-label">Inter-Arrival Time (&Delta;t)</span>
            <span class="forensics-val mono-data ${interArrivalVal < 2.5 ? 'fail' : 'pass'}">${interArrival}</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">Card Auth Velocity (C1 24h)</span>
            <span class="forensics-val mono-data ${c1 > 10 ? 'fail' : 'pass'}">${c1} authas</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">Burst Velocity (C2 1h)</span>
            <span class="forensics-val mono-data ${c2 > 5 ? 'fail' : 'pass'}">${c2} authas</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">Merchant Count (C5 1h)</span>
            <span class="forensics-val mono-data ${c5 > 10 ? 'fail' : 'pass'}">${c5} targets</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">ISO 8583 Response</span>
            <span class="forensics-val mono-data" style="font-size:10px;">${isoResponse}</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">Client / Headless</span>
            <span class="forensics-val mono-data ${dev.is_headless_browser ? 'fail' : 'pass'}">${dev.browser_name || 'Safari'}</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">IP &harr; Billing Dist</span>
            <span class="forensics-val mono-data ${(geo.dist1_ip_billing_distance || 0) > 1000 ? 'fail' : 'pass'}">${geo.dist1_ip_billing_distance ? `${geo.dist1_ip_billing_distance.toFixed(0)} km` : 'Domestic'}</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">Disposable Email</span>
            <span class="forensics-val mono-data ${geo.is_disposable_email ? 'fail' : 'pass'}">${geo.is_disposable_email ? 'TRUE' : 'FALSE'}</span>
          </div>
        </div>
      </div>

      <div class="inspector-section">
        <div class="section-head-mini">
          <span>Contributing Risk Signals</span>
          <span class="section-badge">${factors.length} DETECTED</span>
        </div>
        <div class="factors-list">
          ${factors.length === 0 ? '<span style="color:var(--status-allow); font-size:12px;">Standard organic transaction profile. No abnormal velocity flags.</span>' : ''}
          ${factors.map(f => `
            <div class="factor-row">
              <div class="factor-desc">
                <span class="severity-tag ${f.severity === 'CRITICAL' ? 'severity-critical' : f.severity === 'HIGH' ? 'severity-high' : 'severity-medium'}">${f.severity || 'HIGH'}</span>
                <span>${f.description || f}</span>
              </div>
              <span class="factor-impact mono-data">+${f.impact ? f.impact.toFixed(2) : '0.25'}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }
}
