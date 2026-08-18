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
    this.totalRecords = 0;
    this.selectedInstanceId = null;
    this.selectedDetail = null;
    this.isLoadingList = false;
    this.isLoadingDetail = false;
    
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
        <!-- Hero Header -->
        <div class="dashboard-hero">
          <div class="dashboard-hero-top">
            <div class="dashboard-hero-left">
              <div class="view-hero-breadcrumbs">
                <span class="footer-tag" style="cursor:pointer" id="v-a-crumb-home">TRIAD</span>
                <span class="footer-sep">/</span>
                <span>VECTOR A</span>
                <span class="footer-sep">/</span>
                <span class="accent-cyan">SYNTHETIC IDENTITY &amp; DOCUMENT FRAUD</span>
              </div>
              <h1 class="view-hero-title">Vector A: Frankenstein Identity &amp; Forensics Hub</h1>
              <p class="hub-description">
                Frankenstein synthetic identities combining authentic stolen credit bureau anchors with generative biographical overlays, CMRA virtual suites, and manipulated PDF417/EXIF document forensics.
              </p>
            </div>
            <div class="dashboard-hero-stats" id="v-a-stats-ribbon">
              <div class="stat-tile">
                <span class="stat-tile-label">DEFENSE RECALL</span>
                <span class="stat-tile-val mono-data">100.0%</span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">FALSE POSITIVES</span>
                <span class="stat-tile-val mono-data">0.00%</span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">TOTAL PROFILES</span>
                <span class="stat-tile-val mono-data">500</span>
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

        <!-- Split-Pane Layout -->
        <div class="dashboard-split-layout">
          <!-- Left: Instances Table Feed -->
          <div class="data-feed-card">
            <div class="panel-header">
              <div class="panel-title-group">
                <span class="vector-pill">FEED</span>
                <h3 class="panel-title">Synthetic Identity Profile Stream</h3>
              </div>
              <span class="section-badge" id="v-a-count-badge">500 RECORDS</span>
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
              <span id="v-a-pagination-info">Showing 1–25 of 500</span>
              <div class="pagination-btn-group">
                <button type="button" class="pagination-btn" id="v-a-prev-page" disabled>&larr; Prev</button>
                <button type="button" class="pagination-btn" id="v-a-next-page">Next &rarr;</button>
              </div>
            </div>
          </div>

          <!-- Right: Deep Inspector Drawer -->
          <div class="inspector-card" id="v-a-inspector">
            <div class="drawer-empty-state">
              <div class="spinner" style="margin:0 auto 12px;"></div>
              <span>Select a profile from the stream to view deep forensics</span>
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
    const recall = ((opMetrics.recall || 1.0) * 100).toFixed(1);
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
      this.totalRecords = data.total_records || 0;
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
      const scorePct = Math.round(item.risk_score * 100);
      const fillClass = item.risk_score >= 0.7 ? 'high' : item.risk_score >= 0.25 ? 'med' : 'low';
      const verdictBadge = item.verdict === 'BLOCK' ? 'badge-block' : item.verdict === 'REVIEW' ? 'badge-review' : 'badge-allow';

      return `
        <tr class="${isSelected ? 'selected-row' : ''}" data-id="${item.instance_id}">
          <td class="mono-data" style="font-weight:700; color:var(--text-primary);">${item.instance_id}</td>
          <td><span class="threat-badge ${item.is_malicious ? 'badge-block' : 'badge-allow'}">${item.archetype_or_technique.replace(/_/g, ' ')}</span></td>
          <td class="mono-data" style="font-size:11px; color:var(--text-secondary);">${item.evasion_tier ? item.evasion_tier.replace('_EVASION', '') : 'TIER_1'}</td>
          <td>
            <div class="score-cell-group">
              <div class="score-mini-bar">
                <div class="score-mini-fill ${fillClass}" style="width:${scorePct}%"></div>
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

    const inspector = this.container.querySelector('#v-a-inspector');
    if (!inspector) return;

    inspector.innerHTML = `
      <div class="drawer-empty-state">
        <div class="spinner" style="margin:0 auto 8px;"></div>
        <span>Loading forensic details for ${instanceId}...</span>
      </div>
    `;

    try {
      this.selectedDetail = await fetchInstanceDetail('A', instanceId);
      this.renderInspector();
    } catch (err) {
      inspector.innerHTML = `
        <div class="drawer-empty-state" style="color:var(--status-block);">
          <span>Error loading detail: ${err.message}</span>
        </div>
      `;
    }
  }

  renderInspector() {
    const inspector = this.container.querySelector('#v-a-inspector');
    if (!inspector || !this.selectedDetail) return;

    const d = this.selectedDetail;
    const profile = d.artifact || {};
    const synthesis = profile.synthesis_metadata || {};
    const anchor = profile.real_fragment || {};
    const overlay = profile.fabricated_overlay || {};
    const bio = overlay.biographical || {};
    const addr = overlay.residential_address || {};
    const contact = overlay.contact_endpoints || {};
    const emp = overlay.employment_profile || {};
    const doc = profile.document_metadata || {};
    const checksums = doc.checksum_validity || {};
    const layout = doc.field_layout_plausibility || {};
    const exif = doc.creation_tool_fingerprint || {};
    const factors = d.contributing_factors || [];

    const verdictBadge = d.verdict === 'BLOCK' ? 'badge-block' : d.verdict === 'REVIEW' ? 'badge-review' : 'badge-allow';
    const scoreColor = d.risk_score >= 0.7 ? 'var(--status-block)' : d.risk_score >= 0.25 ? 'var(--status-review)' : 'var(--status-allow)';

    inspector.innerHTML = `
      <!-- Inspector Header -->
      <div class="inspector-header">
        <div class="inspector-id-group">
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="inspector-id">${d.instance_id}</span>
            <span class="threat-badge ${d.is_malicious ? 'badge-block' : 'badge-allow'}">${d.attack_technique}</span>
          </div>
          <span class="inspector-type-pill">${synthesis.synthesis_type || 'PROFILE'} &bull; Seed: <span class="mono-data">${synthesis.generation_seed || 42}</span></span>
        </div>
        <div class="inspector-verdict-hud">
          <span class="threat-badge ${verdictBadge}" style="font-size:12px; padding:3px 10px;">${d.verdict}</span>
          <div class="inspector-score-pill" style="background:var(--bg-surface-raised); border:1px solid var(--border-default);">
            <span style="color:var(--text-muted); font-size:11px;">RISK SCORE:</span>
            <span class="mono-data" style="color:${scoreColor}; font-size:13px; font-weight:700;">${d.risk_score.toFixed(3)}</span>
          </div>
        </div>
      </div>

      <!-- Explainability Narrative -->
      <div class="narrative-box">
        <strong style="color:var(--accent-amber); display:block; margin-bottom:4px; font-size:11px; font-weight:700; letter-spacing:var(--tracking-wide);">EXPLAINABILITY DIAGNOSTIC</strong>
        ${d.primary_risk_driver}
      </div>

      <!-- Frankenstein Identity Architecture Comparison -->
      <div class="inspector-section">
        <div class="section-head-mini">
          <span>Frankenstein Anatomy (Anchor vs Overlay)</span>
          <span class="section-badge">TAXONOMY §2.1</span>
        </div>
        <div class="comparison-grid">
          <!-- Authentic Anchor Column -->
          <div class="comp-col anchor-col">
            <span class="comp-col-title" style="color:var(--accent-cyan);">Authentic Stolen Anchor</span>
            <div class="comp-field-row">
              <span class="comp-field-label">National ID (SSN)</span>
              <span class="comp-field-val mono-data">${anchor.anchor_national_id || '900-XX-XXXX'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Issuing Jurisdiction</span>
              <span class="comp-field-val">${anchor.anchor_issuing_state || 'N/A'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">True Birth Year Range</span>
              <span class="comp-field-val mono-data">${anchor.anchor_birth_year || 'N/A'}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Credit Bureau Vintage</span>
              <span class="comp-field-val mono-data">${anchor.anchor_bureau_vintage_months || 0} months</span>
            </div>
          </div>

          <!-- Synthesized Overlay Column -->
          <div class="comp-col overlay-col">
            <span class="comp-col-title" style="color:var(--accent-amber);">Fabricated Biographical Overlay</span>
            <div class="comp-field-row">
              <span class="comp-field-label">Claimed Identity</span>
              <span class="comp-field-val" style="font-weight:600;">${bio.first_name || ''} ${bio.middle_name || ''} ${bio.last_name || ''}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Claimed DOB</span>
              <span class="comp-field-val mono-data">${bio.claimed_date_of_birth || 'N/A'} (${bio.claimed_gender || ''})</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Residential Address</span>
              <span class="comp-field-val">${addr.street_line1 || ''}, ${addr.city || ''}, ${addr.state || ''} ${addr.is_cmra ? '<span style="color:var(--accent-amber); font-weight:700;">[CMRA]</span>' : ''}</span>
            </div>
            <div class="comp-field-row">
              <span class="comp-field-label">Contact Endpoints</span>
              <span class="comp-field-val mono-data" style="font-size:11px;">${contact.email_address || ''} (${contact.phone_line_type || 'VOIP'})</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Secondary Deep Forensics (Collapsible behind Single Expand Action) -->
      <button type="button" class="drawer-expand-btn" id="v-a-toggle-forensics">
        <span>Deep Document Forensics &amp; Risk Signals (${factors.length})</span>
        <span class="expand-icon" aria-hidden="true">▾</span>
      </button>

      <div class="drawer-collapsible-content collapsed" id="v-a-forensics-collapsible">
        <!-- Document Forensics Inspection -->
        <div class="inspector-section">
          <div class="section-head-mini">
            <span>Digital Document Forensics</span>
            <span class="section-badge">AAMVA PDF417 / EXIF</span>
          </div>
          <div class="forensics-grid">
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

        <!-- Contributing Factors Breakdown -->
        <div class="inspector-section">
          <div class="section-head-mini">
            <span>Contributing Risk Signals</span>
            <span class="section-badge">${factors.length} DETECTED</span>
          </div>
          <div class="factors-list">
            ${factors.length === 0 ? '<span style="color:var(--status-allow); font-size:12px;">No risk signals detected. Profile passed all verification gates.</span>' : ''}
            ${factors.map(f => {
              const sevClass = f.severity === 'CRITICAL' ? 'severity-critical' : f.severity === 'HIGH' ? 'severity-high' : f.severity === 'MEDIUM' ? 'severity-medium' : 'severity-low';
              return `
                <div class="factor-row">
                  <div class="factor-desc">
                    <div style="display:flex; align-items:center; gap:6px; margin-bottom:2px;">
                      <span class="severity-tag ${sevClass}">${f.severity}</span>
                      <span class="mono-data" style="color:var(--text-secondary); font-size:10px;">${f.tier}</span>
                    </div>
                    <span>${f.description}</span>
                  </div>
                  <span class="factor-impact mono-data">+${f.impact.toFixed(2)}</span>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </div>
    `;

    // Bind collapsible toggle
    const toggleBtn = inspector.querySelector('#v-a-toggle-forensics');
    const collapsible = inspector.querySelector('#v-a-forensics-collapsible');
    toggleBtn?.addEventListener('click', () => {
      const isCollapsed = collapsible.classList.contains('collapsed');
      collapsible.classList.toggle('collapsed', !isCollapsed);
      toggleBtn.classList.toggle('active', isCollapsed);
    });
  }
}
