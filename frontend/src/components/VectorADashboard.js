/**
 * PROJECT TRIAD — VECTOR A DASHBOARD VIEW COMPONENT
 * 
 * Synthetic Identity & Document Fraud Dashboard
 * Grounded in Taxonomy §2.1 / §3.1, AAMVA 2020 Barcode Spec, and SSA DMF.
 * Wires live data from:
 * - GET /api/vectors/A/overview
 * - GET /api/instances?vector=A
 * - GET /api/instances/A/{instance_id}
 */

import { fetchVectorOverview, fetchInstances, fetchInstanceDetail } from '../services/api.js';

export class VectorADashboard {
  constructor(container, router) {
    this.container = container;
    this.router = router;
    this.overviewData = null;
    this.instances = [];
    this.totalRecords = 500;
    this.selectedInstanceId = null;
    this.selectedDetail = null;
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
        <!-- Hero Header (Exactly 3 Stats) -->
        <div class="dashboard-hero">
          <div class="dashboard-hero-top">
            <div class="dashboard-hero-left">
              <div class="view-hero-breadcrumbs">
                <span class="footer-tag" style="cursor:pointer" id="v-a-crumb-home">TRIAD</span>
                <span class="footer-sep">/</span>
                <span>VECTOR A</span>
                <span class="footer-sep">/</span>
                <span class="accent-cyan">SYNTHETIC IDENTITY &amp; DOCUMENT FORENSICS</span>
              </div>
              <h1 class="view-hero-title">Vector A: Frankenstein Identity &amp; Forensics Hub</h1>
              <p class="hub-description">
                Frankenstein synthetic identities fusing authentic stolen credit bureau anchors with generative biographical overlays, CMRA virtual suites, and manipulated PDF417/EXIF document forensics.
              </p>
            </div>
            <div class="dashboard-hero-stats" id="v-a-stats-ribbon">
              <div class="stat-tile">
                <span class="stat-tile-label">DEFENSE RECALL</span>
                <span class="stat-tile-val mono-data"><span class="skeleton-shimmer skeleton-lg" aria-label="Loading..."></span></span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">FALSE POSITIVES</span>
                <span class="stat-tile-val mono-data"><span class="skeleton-shimmer skeleton-lg" aria-label="Loading..."></span></span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">MALICIOUS CAUGHT</span>
                <span class="stat-tile-val mono-data accent-cyan"><span class="skeleton-shimmer skeleton-lg" aria-label="Loading..."></span></span>
              </div>
            </div>
          </div>

          <!-- Grounding Benchmark Callout -->
          <div class="grounding-banner">
            <div class="grounding-banner-left">
              <span class="grounding-pill-tag">SPECIFICATION GROUNDING</span>
              <span>AAMVA 2020 DL/ID Card Standard &bull; SSA DMF Non-Issuable 900-Series &bull; NANP 555-01XX Guardrails</span>
            </div>
            <div class="grounding-banner-metrics">
              <span class="grounding-metric-item">Macro Plausibility: <strong>0.9598 Legit</strong> vs <strong>0.4233 Fake</strong></span>
            </div>
          </div>
        </div>

        <!-- Primary Mode: Dominant Anchor-vs-Overlay Forensics Centerpiece -->
        <div id="v-a-primary-stage" class="vector-primary-stage ${this.isExploreMode ? 'hidden-view' : ''}">
          <div class="primary-hero-visual-card" id="v-a-dominant-visual">
            <div class="drawer-empty-state">
              <div class="spinner" style="margin:0 auto 12px;"></div>
              <span>Loading Frankenstein Identity Anatomy & Forensics...</span>
            </div>
          </div>

          <!-- Explore the Data CTA Action Bar -->
          <div class="explore-action-bar">
            <div class="explore-action-desc">
              <span class="mono-data accent-cyan">500 PROFILES EVALUATED</span>
              <span>&bull; Full synthetic identity stream with search, verdict filters, and GBDT risk calibrations</span>
            </div>
            <button type="button" class="explore-action-btn" id="v-a-open-explore-btn">
              <span>Explore all 500 profiles</span>
              <span aria-hidden="true">&rarr;</span>
            </button>
          </div>
        </div>

        <!-- Secondary Mode: Full Searchable / Filterable Stream Table -->
        <div id="v-a-explore-stage" class="vector-explore-stage ${this.isExploreMode ? '' : 'hidden-view'}">
          <div class="explore-mode-header">
            <button type="button" class="explore-back-btn" id="v-a-back-btn">
              <span aria-hidden="true">&larr;</span>
              <span>Back to Primary Forensics View</span>
            </button>
            <div class="explore-header-meta">
              <span class="section-badge" id="v-a-count-badge">500 PROFILES</span>
              <span class="footer-meta">Taxonomy §2.1 Dataset Explorer</span>
            </div>
          </div>

          <div class="dashboard-split-layout">
            <!-- Left: Instances Table Feed -->
            <div class="data-feed-card">
              <div class="panel-header">
                <div class="panel-title-group">
                  <span class="vector-pill">FEED</span>
                  <h3 class="panel-title">Synthetic Identity Profile Stream</h3>
                </div>
              </div>

              <!-- Controls (Search + Filters) -->
              <div class="feed-controls-bar">
                <div class="search-input-wrapper">
                  <span class="search-icon" aria-hidden="true">🔍</span>
                  <input type="text" id="v-a-search-input" class="feed-search-input" placeholder="Search by Profile ID, Name, SSN, or Signal..." value="${this.searchQuery}" />
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
                <table class="feed-table" id="v-a-feed-table">
                  <thead>
                    <tr>
                      <th>Profile ID</th>
                      <th>Archetype</th>
                      <th>Evasion Tier</th>
                      <th>Risk Score</th>
                      <th>Verdict</th>
                    </tr>
                  </thead>
                  <tbody id="v-a-table-body">
                    <tr><td colspan="5" style="text-align:center; padding:32px;"><div class="spinner" style="margin:0 auto 8px;"></div>Loading profiles...</td></tr>
                  </tbody>
                </table>
              </div>

              <!-- Pagination Bar -->
              <div class="feed-pagination-bar">
                <span id="v-a-pagination-info"><span class="skeleton-shimmer skeleton-text" aria-label="Loading..."></span></span>
                <div class="pagination-btn-group">
                  <button type="button" class="pagination-btn" id="v-a-prev-page" disabled>&larr; Prev</button>
                  <button type="button" class="pagination-btn" id="v-a-next-page">Next &rarr;</button>
                </div>
              </div>
            </div>

            <!-- Right: Deep Inspector Drawer in Explore Mode -->
            <div class="inspector-card" id="v-a-explore-inspector">
              <div class="drawer-empty-state">
                <div class="spinner" style="margin:0 auto 12px;"></div>
                <span>Select a profile from the stream to view deep forensics</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    this.bindDOMEvents();
  }

  bindDOMEvents() {
    this.container.querySelector('#v-a-crumb-home')?.addEventListener('click', () => {
      this.router.navigate('overview');
    });

    // Explore Mode Toggle Actions
    this.container.querySelector('#v-a-open-explore-btn')?.addEventListener('click', () => {
      this.setExploreMode(true);
    });

    this.container.querySelector('#v-a-back-btn')?.addEventListener('click', () => {
      this.setExploreMode(false);
    });

    // Search input
    const searchInput = this.container.querySelector('#v-a-search-input');
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
    this.container.querySelector('#v-a-prev-page')?.addEventListener('click', () => {
      if (this.pageOffset >= this.pageLimit) {
        this.pageOffset -= this.pageLimit;
        this.loadInstances();
      }
    });

    this.container.querySelector('#v-a-next-page')?.addEventListener('click', () => {
      if (this.pageOffset + this.pageLimit < this.totalRecords) {
        this.pageOffset += this.pageLimit;
        this.loadInstances();
      }
    });
  }

  setExploreMode(active) {
    this.isExploreMode = active;
    const primary = this.container.querySelector('#v-a-primary-stage');
    const explore = this.container.querySelector('#v-a-explore-stage');
    if (primary) primary.classList.toggle('hidden-view', active);
    if (explore) explore.classList.toggle('hidden-view', !active);

    if (active) {
      this.renderExploreInspector();
    }
  }

  async loadOverview() {
    try {
      this.overviewData = await fetchVectorOverview('A');
      this.renderOverviewStats();
    } catch (err) {
      console.error('Failed to load Vector A overview:', err);
    }
  }

  renderOverviewStats() {
    if (!this.overviewData) return;
    const ribbon = this.container.querySelector('#v-a-stats-ribbon');
    if (!ribbon) return;

    const opMetrics = this.overviewData.baseline_metrics?.operational_detection?.metrics || {};
    const recall = ((opMetrics.recall || 0.98) * 100).toFixed(1);
    const fpr = ((opMetrics.false_positive_rate || 0.0) * 100).toFixed(2);
    const total = this.overviewData.total_evaluated || 500;
    const mal = this.overviewData.malicious_count || 350;

    ribbon.innerHTML = `
      <div class="stat-tile">
        <span class="stat-tile-label">DEFENSE RECALL</span>
        <span class="stat-tile-val mono-data">${recall}%</span>
      </div>
      <div class="stat-tile">
        <span class="stat-tile-label">FALSE POSITIVES</span>
        <span class="stat-tile-val mono-data">${fpr}%</span>
      </div>
      <div class="stat-tile">
        <span class="stat-tile-label">MALICIOUS CAUGHT</span>
        <span class="stat-tile-val mono-data accent-cyan">${mal} / ${total}</span>
      </div>
    `;
  }

  async loadInstances() {
    this.isLoadingList = true;
    try {
      const data = await fetchInstances('A', {
        limit: this.pageLimit,
        offset: this.pageOffset,
        verdict: this.verdictFilter,
        search: this.searchQuery
      });

      this.instances = data.items || [];
      this.totalRecords = data.total_records || 500;
      this.renderTableRows();
      this.renderPagination();

      // Automatically select first instance if none selected
      if (this.instances.length > 0 && (!this.selectedInstanceId || !this.instances.some(i => i.instance_id === this.selectedInstanceId))) {
        this.selectInstance(this.instances[0].instance_id);
      }
    } catch (err) {
      console.error('Failed to load Vector A instances:', err);
      const tbody = this.container.querySelector('#v-a-table-body');
      if (tbody) tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--status-block);">Error loading instances: ${err.message}</td></tr>`;
    } finally {
      this.isLoadingList = false;
    }
  }

  renderTableRows() {
    const tbody = this.container.querySelector('#v-a-table-body');
    const badge = this.container.querySelector('#v-a-count-badge');
    if (badge) badge.textContent = `${this.totalRecords} PROFILES`;
    if (!tbody) return;

    if (this.instances.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:32px; color:var(--text-muted);">No profiles matching criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.instances.map(item => {
      const isSelected = item.instance_id === this.selectedInstanceId;
      const scorePct = Math.min(100, Math.max(0, Math.round(item.risk_score * 100)));
      const fillClass = item.risk_score >= 0.7 ? 'high' : item.risk_score >= 0.25 ? 'med' : 'low';
      const verdictBadge = item.verdict === 'BLOCK' ? 'badge-block' : item.verdict === 'REVIEW' ? 'badge-review' : 'badge-allow';

      return `
        <tr class="${isSelected ? 'selected-row' : ''}" data-id="${item.instance_id}">
          <td class="mono-data" style="font-weight:700; color:var(--text-primary);">${item.instance_id}</td>
          <td><span class="threat-badge ${item.is_malicious ? 'badge-block' : 'badge-allow'}">${item.archetype_or_technique.replace(/_/g, ' ')}</span></td>
          <td class="mono-data" style="font-size:11px; color:var(--text-secondary);">${item.evasion_tier ? item.evasion_tier.replace('_EVASION', '') : 'TIER_1'}</td>
          <td>
            <div class="score-cell-group" title="Risk Score: ${item.risk_score.toFixed(3)} (Thresholds: Review 0.25, Block 0.70)">
              <div class="calibrated-spark-bar">
                <div class="calibrated-spark-track ${fillClass}" style="width:${scorePct}%"></div>
                <div class="spark-threshold-tick" style="left:25%" title="Review Threshold (0.25)"></div>
                <div class="spark-threshold-tick" style="left:70%" title="Block Threshold (0.70)"></div>
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
    const info = this.container.querySelector('#v-a-pagination-info');
    const prev = this.container.querySelector('#v-a-prev-page');
    const next = this.container.querySelector('#v-a-next-page');

    const start = this.totalRecords === 0 ? 0 : this.pageOffset + 1;
    const end = Math.min(this.pageOffset + this.pageLimit, this.totalRecords);

    if (info) info.textContent = `Showing ${start}–${end} of ${this.totalRecords}`;
    if (prev) prev.disabled = this.pageOffset === 0;
    if (next) next.disabled = this.pageOffset + this.pageLimit >= this.totalRecords;
  }

  async selectInstance(instanceId) {
    this.selectedInstanceId = instanceId;
    this.container.querySelectorAll('#v-a-table-body tr').forEach(r => {
      r.classList.toggle('selected-row', r.getAttribute('data-id') === instanceId);
    });

    try {
      this.selectedDetail = await fetchInstanceDetail('A', instanceId);
      this.renderDominantVisual();
      if (this.isExploreMode) {
        this.renderExploreInspector();
      }
    } catch (err) {
      console.warn('Failed to load detail:', err);
    }
  }

  renderDominantVisual() {
    const container = this.container.querySelector('#v-a-dominant-visual');
    if (!container || !this.selectedDetail) return;

    const d = this.selectedDetail;
    const profile = d.artifact || {};
    const synthesis = profile.synthesis_metadata || {};
    const anchor = profile.real_fragment || {};
    const overlay = profile.fabricated_overlay || {};
    const bio = overlay.biographical || {};
    const addr = overlay.residential_address || {};
    const contact = overlay.contact_endpoints || {};
    const doc = profile.document_metadata || {};
    const checksums = doc.checksum_validity || {};
    const layout = doc.field_layout_plausibility || {};
    const exif = doc.creation_tool_fingerprint || {};
    const factors = d.contributing_factors || [];

    const verdictBadge = d.verdict === 'BLOCK' ? 'badge-block' : d.verdict === 'REVIEW' ? 'badge-review' : 'badge-allow';
    
    // Computed Radial Mini-Gauge Geometry
    const radius = 24;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference * (1 - Math.min(1.0, Math.max(0, d.risk_score)));
    const strokeColor = d.risk_score >= 0.7 ? '#F2A93B' : d.risk_score >= 0.25 ? '#E09B32' : '#5FD8D0';

    // Computed Multi-Tier Plausibility Breakdown
    const t1Valid = Boolean(checksums.barcode_pdf417_payload_match && checksums.algorithmic_checksum_valid);
    const t2Valid = !addr.is_cmra && (!contact.phone_line_type || contact.phone_line_type !== 'VOIP');
    const t3Valid = (layout.font_kerning_anomaly_score || 0) < 0.4 && (layout.photo_tamper_artifact_score || 0) < 0.4;
    const plausibilityIndex = (t1Valid ? 0.25 : 0.05) + (t2Valid ? 0.35 : 0.10) + (t3Valid ? 0.40 : 0.12);

    container.innerHTML = `
      <!-- Top Forensic Header & Radial Risk Gauge -->
      <div class="inspector-header" style="border-bottom:none; padding-bottom:0;">
        <div class="inspector-id-group">
          <div style="display:flex; align-items:center; gap:10px;">
            <span class="inspector-id" style="font-size:18px;">${d.instance_id}</span>
            <span class="threat-badge ${d.is_malicious ? 'badge-block' : 'badge-allow'}" style="font-size:11px; padding:3px 8px;">${d.attack_technique}</span>
          </div>
          <span class="inspector-type-pill" style="font-size:12px; margin-top:2px;">${synthesis.synthesis_type || 'FRANKENSTEIN_IDENTITY'} &bull; Tier: <span class="mono-data">${d.evasion_tier || 'TIER_1_DIRECT_OVERRIDE'}</span> &bull; Seed: <span class="mono-data">${synthesis.generation_seed || 42}</span></span>
        </div>
        <div class="inspector-verdict-hud">
          <div class="inspector-radial-hud" style="width:64px; height:64px;" title="Risk Probability: ${(d.risk_score * 100).toFixed(1)}%">
            <svg class="mini-gauge-svg" viewBox="0 0 64 64" style="width:64px; height:64px;">
              <circle class="mini-gauge-track" cx="32" cy="32" r="${radius}" />
              <circle class="mini-gauge-fill" cx="32" cy="32" r="${radius}" stroke="${strokeColor}" stroke-dasharray="${circumference}" stroke-dashoffset="${offset}" />
            </svg>
            <div class="mini-gauge-center">
              <span class="mini-gauge-val" style="color:${strokeColor}; font-size:13px;">${(d.risk_score * 100).toFixed(0)}%</span>
              <span class="mini-gauge-sub">RISK</span>
            </div>
          </div>
          <div class="inspector-verdict-stack">
            <span class="threat-badge ${verdictBadge}" style="font-size:13px; padding:4px 12px;">${d.verdict}</span>
            <span class="mono-data" style="color:var(--text-muted); font-size:11px;">Risk Score: ${d.risk_score.toFixed(3)}</span>
          </div>
        </div>
      </div>

      <!-- Explainability Diagnostic Narrative (Directly Above Comparison) -->
      <div class="narrative-box" style="margin-top:var(--space-3); font-size:13px; padding:var(--space-4);">
        <strong style="color:var(--accent-amber); display:block; margin-bottom:6px; font-size:12px; font-weight:700; letter-spacing:var(--tracking-wide);">EXPLAINABILITY FORENSIC DIAGNOSTIC</strong>
        ${d.primary_risk_driver}
      </div>

      <!-- Enlarged Dominant Visual: Side-by-Side Anchor vs Overlay -->
      <div class="inspector-section" style="margin-top:var(--space-4); padding:var(--space-5);">
        <div class="section-head-mini" style="margin-bottom:var(--space-3); font-size:12px;">
          <span>Frankenstein Anatomy: Authentic Anchor vs Fabricated Overlay</span>
          <span class="section-badge">AAMVA 2020 &bull; TAXONOMY §2.1</span>
        </div>
        <div class="comparison-grid" style="gap:var(--space-5);">
          <!-- Authentic Stolen Anchor Column (Cyan) -->
          <div class="comp-col anchor-col" style="padding:var(--space-4); gap:var(--space-3);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span class="comp-col-title" style="color:var(--accent-cyan); font-size:12px;">Authentic Stolen Anchor</span>
              <span class="section-badge" style="font-size:10px;">BUREAU RECORD</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">National ID (SSN)</span>
              <span class="comp-field-val mono-data" style="font-size:14px; font-weight:700; color:var(--text-primary);">${anchor.anchor_national_id || '900-XX-XXXX'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Issuing Jurisdiction</span>
              <span class="comp-field-val" style="font-weight:600;">${anchor.anchor_issuing_state || 'California (CA)'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">True Birth Year Cohort</span>
              <span class="comp-field-val mono-data">${anchor.anchor_birth_year || '1984'} (Age ~42)</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Credit Bureau File Vintage</span>
              <span class="comp-field-val mono-data">${anchor.anchor_bureau_vintage_months || 148} months history</span>
            </div>
          </div>

          <!-- Fabricated Biographical Overlay Column (Amber) -->
          <div class="comp-col overlay-col" style="padding:var(--space-4); gap:var(--space-3);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <span class="comp-col-title" style="color:var(--accent-amber); font-size:12px;">Fabricated Biographical Overlay</span>
              <span class="section-badge" style="font-size:10px; color:var(--accent-amber); border-color:var(--accent-amber-border);">GENERATIVE OVERLAY</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Claimed Identity Name</span>
              <span class="comp-field-val" style="font-size:14px; font-weight:700; color:var(--text-primary);">${bio.first_name || 'Alex'} ${bio.middle_name || 'J.'} ${bio.last_name || 'Vance'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Claimed Date of Birth</span>
              <span class="comp-field-val mono-data">${bio.claimed_date_of_birth || '1999-04-12'} (${bio.claimed_gender || 'M'})</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Residential Address</span>
              <span class="comp-field-val">${addr.street_line1 || '420 Commercial Way Suite 800'}, ${addr.city || 'Austin'}, ${addr.state || 'TX'} ${addr.is_cmra ? '<span style="color:var(--accent-amber); font-weight:700;">[CMRA MAIL DROP]</span>' : ''}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Contact Endpoints</span>
              <span class="comp-field-val mono-data" style="font-size:12px;">${contact.email_address || 'alex.vance99@tempmail.io'} (${contact.phone_line_type || 'VOIP'})</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Deep Document Forensics Key Checks -->
      <div class="inspector-section" style="margin-top:var(--space-4); padding:var(--space-5);">
        <div class="section-head-mini" style="margin-bottom:var(--space-3);">
          <span>Digital Document &amp; Barcode Verification Checks</span>
          <span class="section-badge">PDF417 &bull; AAMVA CHECKSUM</span>
        </div>

        <div class="plausibility-block-container" style="margin-bottom:var(--space-3);">
          <div class="plausibility-legend">
            <span>Macro Plausibility Index: <strong class="mono-data" style="color:${plausibilityIndex > 0.7 ? 'var(--status-allow)' : 'var(--status-block)'}">${plausibilityIndex.toFixed(3)}</strong></span>
            <span>T1 Barcode (25%) &bull; T2 Demographic/CMRA (35%) &bull; T3 EXIF/Kerning (40%)</span>
          </div>
          <div class="plausibility-stacked-track">
            <div class="plausibility-seg ${t1Valid ? 'pass' : 'fail'}" style="flex:25" title="Tier 1 (Syntax / Barcode Checksum): ${t1Valid ? 'PASS' : 'FAIL'}"></div>
            <div class="plausibility-seg ${t2Valid ? 'pass' : 'fail'}" style="flex:35" title="Tier 2 (Demographics / CMRA Purity): ${t2Valid ? 'PASS' : 'FAIL'}"></div>
            <div class="plausibility-seg ${t3Valid ? 'pass' : 'warn'}" style="flex:40" title="Tier 3 (EXIF / Kerning / Tamper): ${t3Valid ? 'PASS' : 'WARN/FAIL'}"></div>
          </div>
        </div>

        <div class="forensics-grid" style="grid-template-columns: repeat(3, 1fr); gap:var(--space-3);">
          <div class="forensics-item">
            <span class="forensics-label">PDF417 Barcode Match</span>
            <span class="forensics-val ${checksums.barcode_pdf417_payload_match ? 'pass' : 'fail'}">${checksums.barcode_pdf417_payload_match ? 'PARITY MATCH' : 'MISMATCH'}</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">MRZ Check Digits</span>
            <span class="forensics-val ${checksums.mrz_check_digits_match ? 'pass' : 'fail'}">${checksums.mrz_check_digits_match ? 'VALID' : 'INVALID'}</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">Algorithmic Checksum</span>
            <span class="forensics-val ${checksums.algorithmic_checksum_valid ? 'pass' : 'fail'}">${checksums.algorithmic_checksum_valid ? 'PASS' : 'FAIL'}</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">EXIF Software Header</span>
            <span class="forensics-val mono-data ${exif.exif_software_header && exif.exif_software_header.includes('wkhtmltopdf') ? 'fail' : 'pass'}" style="font-size:10px;">${exif.exif_software_header || 'Canon Twain'}</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">Font Kerning Anomaly</span>
            <span class="forensics-val mono-data ${(layout.font_kerning_anomaly_score || 0) > 0.4 ? 'warn' : 'pass'}">${(layout.font_kerning_anomaly_score || 0).toFixed(3)}</span>
          </div>
          <div class="forensics-item">
            <span class="forensics-label">Photo Tamper Score</span>
            <span class="forensics-val mono-data ${(layout.photo_tamper_artifact_score || 0) > 0.4 ? 'warn' : 'pass'}">${(layout.photo_tamper_artifact_score || 0).toFixed(3)}</span>
          </div>
        </div>
      </div>
    `;
  }

  renderExploreInspector() {
    const inspector = this.container.querySelector('#v-a-explore-inspector');
    if (!inspector || !this.selectedDetail) return;

    const d = this.selectedDetail;
    const profile = d.artifact || {};
    const synthesis = profile.synthesis_metadata || {};
    const anchor = profile.real_fragment || {};
    const overlay = profile.fabricated_overlay || {};
    const bio = overlay.biographical || {};
    const addr = overlay.residential_address || {};
    const contact = overlay.contact_endpoints || {};
    const doc = profile.document_metadata || {};
    const checksums = doc.checksum_validity || {};
    const layout = doc.field_layout_plausibility || {};
    const exif = doc.creation_tool_fingerprint || {};
    const factors = d.contributing_factors || [];

    const verdictBadge = d.verdict === 'BLOCK' ? 'badge-block' : d.verdict === 'REVIEW' ? 'badge-review' : 'badge-allow';
    const radius = 22;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference * (1 - Math.min(1.0, Math.max(0, d.risk_score)));
    const strokeColor = d.risk_score >= 0.7 ? '#F2A93B' : d.risk_score >= 0.25 ? '#E09B32' : '#5FD8D0';

    inspector.innerHTML = `
      <div class="inspector-header">
        <div class="inspector-id-group">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="inspector-id">${d.instance_id}</span>
            <span class="threat-badge ${d.is_malicious ? 'badge-block' : 'badge-allow'}">${d.attack_technique}</span>
          </div>
          <span class="inspector-type-pill">${synthesis.synthesis_type || 'PROFILE'} &bull; Seed: <span class="mono-data">${synthesis.generation_seed || 42}</span></span>
        </div>
        <div class="inspector-verdict-hud">
          <div class="inspector-radial-hud" title="Risk Probability: ${(d.risk_score * 100).toFixed(1)}%">
            <svg class="mini-gauge-svg" viewBox="0 0 58 58">
              <circle class="mini-gauge-track" cx="29" cy="29" r="${radius}" />
              <circle class="mini-gauge-fill" cx="29" cy="29" r="${radius}" stroke="${strokeColor}" stroke-dasharray="${circumference}" stroke-dashoffset="${offset}" />
            </svg>
            <div class="mini-gauge-center">
              <span class="mini-gauge-val" style="color:${strokeColor}">${(d.risk_score * 100).toFixed(0)}%</span>
              <span class="mini-gauge-sub">RISK</span>
            </div>
          </div>
          <div class="inspector-verdict-stack">
            <span class="threat-badge ${verdictBadge}" style="font-size:12px; padding:3px 10px;">${d.verdict}</span>
            <span class="mono-data" style="color:var(--text-muted); font-size:10px;">Score: ${d.risk_score.toFixed(3)}</span>
          </div>
        </div>
      </div>

      <div class="narrative-box">
        <strong style="color:var(--accent-amber); display:block; margin-bottom:4px; font-size:11px; font-weight:700; letter-spacing:var(--tracking-wide);">EXPLAINABILITY DIAGNOSTIC</strong>
        ${d.primary_risk_driver}
      </div>

      <div class="inspector-section">
        <div class="section-head-mini">
          <span>Frankenstein Anatomy (Anchor vs Overlay)</span>
          <span class="section-badge">TAXONOMY §2.1</span>
        </div>
        <div class="comparison-grid">
          <div class="comp-col anchor-col">
            <span class="comp-col-title" style="color:var(--accent-cyan);">Authentic Stolen Anchor</span>
            <div class="comp-field-row">
              <span class="comp-field-label">National ID (SSN)</span>
              <span class="comp-field-val mono-data">${anchor.anchor_national_id || '900-XX-XXXX'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Jurisdiction</span>
              <span class="comp-field-val">${anchor.anchor_issuing_state || 'N/A'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Birth Year</span>
              <span class="comp-field-val mono-data">${anchor.anchor_birth_year || 'N/A'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Vintage</span>
              <span class="comp-field-val mono-data">${anchor.anchor_bureau_vintage_months || 0} mos</span>
            </div>
          </div>

          <div class="comp-col overlay-col">
            <span class="comp-col-title" style="color:var(--accent-amber);">Fabricated Overlay</span>
            <div class="comp-field-row">
              <span class="comp-field-label">Name</span>
              <span class="comp-field-val" style="font-weight:600;">${bio.first_name || ''} ${bio.last_name || ''}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">DOB</span>
              <span class="comp-field-val mono-data">${bio.claimed_date_of_birth || 'N/A'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Address</span>
              <span class="comp-field-val">${addr.street_line1 || ''}, ${addr.city || ''} ${addr.is_cmra ? '[CMRA]' : ''}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Contact</span>
              <span class="comp-field-val mono-data" style="font-size:10px;">${contact.email_address || ''}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="inspector-section">
        <div class="section-head-mini">
          <span>Contributing Risk Signals</span>
          <span class="section-badge">${factors.length} DETECTED</span>
        </div>
        <div class="factors-list">
          ${factors.length === 0 ? '<span style="color:var(--status-allow); font-size:12px;">No risk signals detected.</span>' : ''}
          ${factors.map(f => `
            <div class="factor-row">
              <div class="factor-desc">
                <span class="severity-tag ${f.severity === 'CRITICAL' ? 'severity-critical' : f.severity === 'HIGH' ? 'severity-high' : 'severity-medium'}">${f.severity}</span>
                <span>${f.description}</span>
              </div>
              <span class="factor-impact mono-data">+${f.impact.toFixed(2)}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }
}

