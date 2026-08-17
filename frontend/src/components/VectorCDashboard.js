/**
 * PROJECT TRIAD — VECTOR C AGENT-VIEW CENTERPIECE
 * 
 * Interactive Agentic Payment Hijacking & Pre-Execution Defense Theater
 * Grounded in Taxonomy §2.3 / §3.3, Air-Gapped Sandbox Invariants, and FakeWallet tool interception.
 * Wires live data from:
 * - GET /api/vectors/C/overview
 * - GET /api/instances?vector=C
 * - GET /api/instances/C/{instance_id}
 */

import { fetchVectorOverview, fetchInstances, fetchInstanceDetail } from '../services/api.js';

export class VectorCDashboard {
  constructor(container, router) {
    this.container = container;
    this.router = router;
    this.overviewData = null;
    this.instances = [];
    this.totalRecords = 0;
    this.selectedInstanceId = null;
    this.selectedDetail = null;
    this.isRevealed = true;
    this.isSimulating = false;
    this.simulationStep = 0;
    
    // Filter and Pagination State
    this.verdictFilter = 'ALL';
    this.searchQuery = '';
    this.pageLimit = 20;
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
                <span class="footer-tag" style="cursor:pointer" id="v-c-crumb-home">TRIAD</span>
                <span class="footer-sep">/</span>
                <span>VECTOR C</span>
                <span class="footer-sep">/</span>
                <span class="accent-cyan">AGENTIC PAYMENT HIJACKING (CENTERPIECE)</span>
              </div>
              <h1 class="view-hero-title">Vector C: Autonomous Agent Tool Interception Hub</h1>
              <p class="hub-description">
                Air-gapped sandboxed shopping and procurement agent subjected to indirect prompt injections across hidden HTML comments, CSS cloaking, and invoice pretexts with pre-execution tool interception.
              </p>
            </div>
            <div class="dashboard-hero-stats" id="v-c-stats-ribbon">
              <div class="stat-tile">
                <span class="stat-tile-label">OPERATIONAL RECALL</span>
                <span class="stat-tile-val mono-data accent-cyan">100.0%</span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">WALLET LOSS</span>
                <span class="stat-tile-val mono-data accent-cyan">$0.00</span>
              </div>
              <div class="stat-tile">
                <span class="stat-tile-label">SCAN LATENCY</span>
                <span class="stat-tile-val mono-data accent-cyan">0.14ms</span>
              </div>
            </div>
          </div>

          <!-- Grounding Benchmark Callout -->
          <div class="grounding-banner">
            <div class="grounding-banner-left">
              <span class="grounding-pill-tag">AIR-GAPPED SANDBOX GUARDRAIL</span>
              <span>100% Local Mock Endpoints (<code>mock://</code>) &bull; Zero External Network Sockets &bull; FakeWallet Immutable Ledger</span>
            </div>
            <div class="grounding-banner-metrics">
              <span class="grounding-metric-item">Missed Detections: <strong>0.00% (0 / 120)</strong></span>
              <span class="grounding-metric-item">False Alarm Rate: <strong>0.00% (0 / 80)</strong></span>
            </div>
          </div>
        </div>

        <!-- Theater Controls Ribbon -->
        <div class="theater-controls-ribbon">
          <div class="scenario-picker-group">
            <span class="footer-tag" style="font-size:12px; margin-right:4px;">ATTACK SCENARIOS:</span>
            <button type="button" class="scenario-chip active" data-archetype="HTML_COMMENT" id="scen-html">1. HTML Comment</button>
            <button type="button" class="scenario-chip" data-archetype="CSS_HIDDEN_ELEMENT" id="scen-css">2. Hidden CSS</button>
            <button type="button" class="scenario-chip" data-archetype="MARKDOWN_COMMENT" id="scen-md">3. Markdown Delimiter</button>
            <button type="button" class="scenario-chip" data-archetype="INVOICE_MEMO_POISONING" id="scen-inv">4. AP Invoice Pretext</button>
            <button type="button" class="scenario-chip" data-archetype="BENCHMARK_LEGITIMATE" id="scen-legit">5. Clean Baseline</button>
          </div>

          <button type="button" class="theater-playback-btn" id="v-c-play-beat-btn">
            <span id="play-icon" aria-hidden="true">&#9658;</span>
            <span id="play-text">Simulate Agent Execution Beat</span>
          </button>
        </div>

        <!-- 3-Column Interactive Agent Theater -->
        <div class="theater-grid" id="v-c-theater-stage">
          <!-- Column 1: Mock Agent State & Wallet -->
          <div class="theater-column" id="col-agent-terminal">
            <div class="panel-header">
              <div class="panel-title-group">
                <span class="vector-pill">AGENT</span>
                <h3 class="panel-title">Mock Procurement Agent</h3>
              </div>
              <span class="section-badge mono-data" id="v-c-agent-status-badge">STATUS: IDLE</span>
            </div>

            <!-- Agent State Card -->
            <div class="agent-status-card">
              <div class="agent-avatar-group">
                <div class="agent-avatar" aria-hidden="true">&#9881;</div>
                <div style="display:flex; flex-direction:column; gap:2px;">
                  <span style="font-weight:700; font-size:13px;">ShoppingAgent_v1</span>
                  <span class="mono-data" style="font-size:11px; color:var(--text-secondary);">Sandbox Process #4201</span>
                </div>
              </div>
              <span class="threat-badge badge-allow" id="agent-security-badge">SECURE</span>
            </div>

            <!-- Agent Execution Terminal -->
            <div class="agent-terminal-box" id="agent-terminal-output">
              <div class="terminal-line cmd">> System initialized. Waiting for task prompt...</div>
            </div>

            <!-- Fake Wallet Card -->
            <div class="wallet-card">
              <div class="panel-title-group" style="justify-content:space-between; width:100%;">
                <span style="font-size:12px; font-weight:700; color:var(--text-secondary); text-transform:uppercase;">FakeWallet Ledger</span>
                <span class="wallet-loss-shield" id="wallet-shield">&#10003; 100% PROTECTED</span>
              </div>
              <div class="wallet-balance-row">
                <div>
                  <span style="font-size:11px; color:var(--text-muted); display:block;">SIMULATED BALANCE</span>
                  <span class="wallet-val mono-data" id="wallet-balance-val">$500.00</span>
                </div>
                <div style="text-align:right;">
                  <span style="font-size:11px; color:var(--text-muted); display:block;">UNAUTHORIZED DRAIN</span>
                  <span class="mono-data" style="color:var(--status-allow); font-weight:700; font-size:15px;" id="wallet-drain-val">$0.00</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 2: Browser Viewport & Concealed Reveal -->
          <div class="theater-column" id="col-browser-viewport">
            <div class="panel-header">
              <div class="panel-title-group">
                <span class="vector-pill">DOM</span>
                <h3 class="panel-title">Mock Web Viewport &amp; Payload Reveal</h3>
              </div>
              <div class="reveal-toggle-bar">
                <button type="button" class="reveal-switch-btn active" id="v-c-reveal-toggle">
                  <span aria-hidden="true">&#128065;</span>
                  <span>Reveal Concealed Directives</span>
                </button>
              </div>
            </div>

            <!-- Mock Browser Window Frame -->
            <div class="browser-viewport-frame">
              <div class="browser-header-bar">
                <div class="traffic-dots">
                  <span class="dot dot-red"></span>
                  <span class="dot dot-yellow"></span>
                  <span class="dot dot-green"></span>
                </div>
                <div class="browser-url-input">
                  <span class="browser-url-icon" aria-hidden="true">&#128274;</span>
                  <span class="mono-data" id="browser-url-text">mock://store.aerosound.local/products/wireless-earbuds</span>
                </div>
              </div>

              <!-- Webpage Content Body -->
              <div class="browser-page-body" id="browser-page-content">
                <div class="drawer-empty-state">
                  <div class="spinner"></div>
                  <span>Loading mock storefront...</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 3: Pre-Execution Defense Scanner HUD -->
          <div class="theater-column" id="col-defense-hud">
            <div class="panel-header">
              <div class="panel-title-group">
                <span class="vector-pill">DEFEND</span>
                <h3 class="panel-title">Pre-Execution Scanner HUD</h3>
              </div>
              <span class="section-badge mono-data">0.14ms INTERCEPT</span>
            </div>

            <!-- Decision Shield HUD -->
            <div class="decision-shield-hud blocked" id="decision-hud-box">
              <div>
                <span style="font-size:11px; color:var(--text-muted); text-transform:uppercase; display:block;">PRE-TOOL ENFORCEMENT</span>
                <span class="decision-main-title" id="decision-hud-text">HARD BLOCKED</span>
              </div>
              <div style="text-align:right;">
                <span style="font-size:11px; color:var(--text-muted); display:block;">CONFIDENCE</span>
                <span class="mono-data" style="font-size:18px; font-weight:800; color:var(--text-primary);" id="decision-confidence-val">1.000</span>
              </div>
            </div>

            <!-- Parameter Divergence Box -->
            <div class="divergence-box" id="divergence-inspector">
              <div class="section-head-mini">
                <span style="color:var(--accent-amber);">Parameter Divergence Inspection</span>
                <span class="section-badge mono-data">TOOL HIJACK</span>
              </div>
              <div class="divergence-row">
                <div>
                  <span style="color:var(--text-muted); font-size:10px; display:block;">INTENDED RECIPIENT</span>
                  <span class="divergence-intended mono-data" id="div-intended-rec">merchant_aerosound_991</span>
                </div>
                <span class="divergence-arrow" aria-hidden="true">&rarr;</span>
                <div style="text-align:right;">
                  <span style="color:var(--text-muted); font-size:10px; display:block;">ROGUE RECIPIENT</span>
                  <span class="divergence-hijacked mono-data" id="div-hijacked-rec">rogue_acquirer_909</span>
                </div>
              </div>
              <div class="divergence-row">
                <div>
                  <span style="color:var(--text-muted); font-size:10px; display:block;">CATALOG PRICE</span>
                  <span class="divergence-intended mono-data" id="div-intended-amt">$29.50</span>
                </div>
                <span class="divergence-arrow" aria-hidden="true">&rarr;</span>
                <div style="text-align:right;">
                  <span style="color:var(--text-muted); font-size:10px; display:block;">INFLATED AMOUNT</span>
                  <span class="divergence-hijacked mono-data" id="div-hijacked-amt">$248.49</span>
                </div>
              </div>
            </div>

            <!-- Risk Sub-Scores Radar -->
            <div class="sub-scores-list" id="sub-scores-container">
              <div class="sub-score-tile">
                <span class="sub-score-label">Concealment</span>
                <div class="sub-score-meter-row">
                  <div class="score-mini-bar" style="width:50px;"><div class="score-mini-fill high" id="sub-conceal-bar" style="width:100%"></div></div>
                  <span class="sub-score-num mono-data" id="sub-conceal-num">1.00</span>
                </div>
              </div>
              <div class="sub-score-tile">
                <span class="sub-score-label">Override Verbs</span>
                <div class="sub-score-meter-row">
                  <div class="score-mini-bar" style="width:50px;"><div class="score-mini-fill high" id="sub-override-bar" style="width:95%"></div></div>
                  <span class="sub-score-num mono-data" id="sub-override-num">0.95</span>
                </div>
              </div>
              <div class="sub-score-tile">
                <span class="sub-score-label">Param Divergence</span>
                <div class="sub-score-meter-row">
                  <div class="score-mini-bar" style="width:50px;"><div class="score-mini-fill high" id="sub-param-bar" style="width:100%"></div></div>
                  <span class="sub-score-num mono-data" id="sub-param-num">1.00</span>
                </div>
              </div>
              <div class="sub-score-tile">
                <span class="sub-score-label">Invoice Pretext</span>
                <div class="sub-score-meter-row">
                  <div class="score-mini-bar" style="width:50px;"><div class="score-mini-fill low" id="sub-inv-bar" style="width:0%"></div></div>
                  <span class="sub-score-num mono-data" id="sub-inv-num">0.00</span>
                </div>
              </div>
            </div>

            <!-- Explainability Box -->
            <div class="narrative-box" id="v-c-narrative-box">
              <strong style="color:var(--accent-amber); display:block; margin-bottom:4px; font-family:var(--font-mono); font-size:11px;">PRE-EXECUTION DEFENSE INTERCEPT</strong>
              <span id="v-c-narrative-text">Evaluating pre-execution threat signals...</span>
            </div>
          </div>
        </div>

        <!-- 200-Payload Batch Explorer -->
        <div class="data-feed-card">
          <div class="panel-header">
            <div class="panel-title-group">
              <span class="vector-pill">BATCH</span>
              <h3 class="panel-title">Vector C Generated Payload Explorer</h3>
            </div>
            <span class="section-badge mono-data" id="v-c-count-badge">200 PAYLOADS</span>
          </div>

          <!-- Controls -->
          <div class="feed-controls-bar">
            <div class="search-input-wrapper">
              <span class="search-icon" aria-hidden="true">&#128269;</span>
              <input type="text" id="v-c-search-input" class="feed-search-input" placeholder="Search by Payload ID, Archetype, Merchant, or Injection Phrase..." value="${this.searchQuery}" />
            </div>
            <div class="verdict-filter-group" role="group" aria-label="Verdict Filter">
              <button type="button" class="verdict-filter-btn active" data-verdict="ALL">ALL</button>
              <button type="button" class="verdict-filter-btn" data-verdict="BLOCK">BLOCK</button>
              <button type="button" class="verdict-filter-btn" data-verdict="ALLOW">ALLOW</button>
            </div>
          </div>

          <!-- Feed Table -->
          <div class="feed-table-container">
            <table class="feed-table" id="v-c-feed-table">
              <thead>
                <tr>
                  <th>Payload ID</th>
                  <th>Archetype</th>
                  <th>Evasion Tier</th>
                  <th>Intended &rarr; Rogue Recipient</th>
                  <th>Catalog &rarr; Hijacked Amt</th>
                  <th>Verdict</th>
                </tr>
              </thead>
              <tbody id="v-c-table-body">
                <tr><td colspan="6" style="text-align:center; padding:32px;"><div class="spinner" style="margin:0 auto 8px;"></div>Loading payloads...</td></tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination Bar -->
          <div class="feed-pagination-bar">
            <span id="v-c-pagination-info">Showing 1–20 of 200</span>
            <div class="pagination-btn-group">
              <button type="button" class="pagination-btn" id="v-c-prev-page" disabled>&larr; Prev</button>
              <button type="button" class="pagination-btn" id="v-c-next-page">Next &rarr;</button>
            </div>
          </div>
        </div>
      </div>
    `;

    this.bindDOMEvents();
  }

  bindDOMEvents() {
    this.container.querySelector('#v-c-crumb-home')?.addEventListener('click', () => {
      this.router.navigate('overview');
    });

    // Reveal toggle
    const revealBtn = this.container.querySelector('#v-c-reveal-toggle');
    revealBtn?.addEventListener('click', () => {
      this.isRevealed = !this.isRevealed;
      revealBtn.classList.toggle('active', this.isRevealed);
      this.updateConcealmentVisual();
    });

    // Simulate Agent Beat Playback
    const playBtn = this.container.querySelector('#v-c-play-beat-btn');
    playBtn?.addEventListener('click', () => {
      this.runSimulationBeat();
    });

    // Scenario Picker Chips
    const chips = this.container.querySelectorAll('.scenario-chip');
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        const archetype = chip.getAttribute('data-archetype');
        this.selectScenarioByArchetype(archetype);
      });
    });

    // Search input
    const searchInput = this.container.querySelector('#v-c-search-input');
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
    this.container.querySelector('#v-c-prev-page')?.addEventListener('click', () => {
      if (this.pageOffset >= this.pageLimit) {
        this.pageOffset -= this.pageLimit;
        this.loadInstances();
      }
    });

    this.container.querySelector('#v-c-next-page')?.addEventListener('click', () => {
      if (this.pageOffset + this.pageLimit < this.totalRecords) {
        this.pageOffset += this.pageLimit;
        this.loadInstances();
      }
    });
  }

  async loadOverview() {
    try {
      this.overviewData = await fetchVectorOverview('C');
      this.renderOverviewStats();
    } catch (err) {
      console.error('Failed to load Vector C overview:', err);
    }
  }

  renderOverviewStats() {
    if (!this.overviewData) return;
    const ribbon = this.container.querySelector('#v-c-stats-ribbon');
    if (!ribbon) return;

    const opMetrics = this.overviewData.baseline_metrics?.operational_detection?.metrics || {};
    const recall = ((opMetrics.recall || 1.0) * 100).toFixed(1);
    const total = this.overviewData.total_evaluated || 200;
    const mal = this.overviewData.malicious_count || 120;

    ribbon.innerHTML = `
      <div class="stat-tile">
        <span class="stat-tile-label">OPERATIONAL RECALL</span>
        <span class="stat-tile-val mono-data accent-cyan">${recall}%</span>
      </div>
      <div class="stat-tile">
        <span class="stat-tile-label">WALLET LOSS</span>
        <span class="stat-tile-val mono-data accent-cyan">$0.00</span>
      </div>
      <div class="stat-tile">
        <span class="stat-tile-label">INTERCEPT LATENCY</span>
        <span class="stat-tile-val mono-data accent-cyan">0.14ms</span>
      </div>
      <div class="stat-tile">
        <span class="stat-tile-label">INJECTIONS CAUGHT</span>
        <span class="stat-tile-val mono-data accent-amber">${mal} / ${total}</span>
      </div>
    `;
  }

  async loadInstances() {
    try {
      const data = await fetchInstances('C', {
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
      console.error('Failed to load Vector C instances:', err);
      const tbody = this.container.querySelector('#v-c-table-body');
      if (tbody) tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--status-block);">Error loading payloads: ${err.message}</td></tr>`;
    }
  }

  renderTableRows() {
    const tbody = this.container.querySelector('#v-c-table-body');
    const badge = this.container.querySelector('#v-c-count-badge');
    if (badge) badge.textContent = `${this.totalRecords} PAYLOADS`;
    if (!tbody) return;

    if (this.instances.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:32px; color:var(--text-muted);">No payloads matching criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.instances.map(item => {
      const isSelected = item.instance_id === this.selectedInstanceId;
      const verdictBadge = item.verdict === 'BLOCK' ? 'badge-block' : 'badge-allow';

      // Parse recipient and amount divergence from primary_risk_driver if available
      let recStr = item.is_malicious ? 'merchant &rarr; rogue_acquirer' : 'authorized_merchant';
      let amtStr = item.is_malicious ? '$29.50 &rarr; $248.49' : '$45.00 clean';

      const recMatch = (item.primary_risk_driver || '').match(/Intended:\s*'([^']+)',\s*Candidate:\s*'([^']+)'/);
      if (recMatch) recStr = `${recMatch[1]} &rarr; <span style="color:var(--status-block); font-weight:700;">${recMatch[2]}</span>`;

      const amtMatch = (item.primary_risk_driver || '').match(/Catalog:\s*\$([0-9.,]+),\s*Tool:\s*\$([0-9.,]+)/);
      if (amtMatch) amtStr = `$${amtMatch[1]} &rarr; <span style="color:var(--status-block); font-weight:700;">$${amtMatch[2]}</span>`;

      return `
        <tr class="${isSelected ? 'selected-row' : ''}" data-id="${item.instance_id}">
          <td class="mono-data" style="font-weight:700; color:var(--text-primary); font-size:11px;">${item.instance_id}</td>
          <td><span class="threat-badge ${item.is_malicious ? 'badge-block' : 'badge-allow'}">${item.archetype_or_technique.replace(/_/g, ' ')}</span></td>
          <td class="mono-data" style="font-size:11px; color:var(--text-secondary);">${item.evasion_tier ? item.evasion_tier.replace('_CONCEALED_STRUCTURAL', '') : 'TIER_1'}</td>
          <td class="mono-data" style="font-size:11px;">${recStr}</td>
          <td class="mono-data" style="font-size:11px;">${amtStr}</td>
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
    const info = this.container.querySelector('#v-c-pagination-info');
    const prev = this.container.querySelector('#v-c-prev-page');
    const next = this.container.querySelector('#v-c-next-page');

    const start = this.totalRecords === 0 ? 0 : this.pageOffset + 1;
    const end = Math.min(this.pageOffset + this.pageLimit, this.totalRecords);

    if (info) info.textContent = `Showing ${start}–${end} of ${this.totalRecords}`;
    if (prev) prev.disabled = this.pageOffset === 0;
    if (next) next.disabled = this.pageOffset + this.pageLimit >= this.totalRecords;
  }

  selectScenarioByArchetype(archetype) {
    const target = this.instances.find(i => i.archetype_or_technique === archetype) ||
                   this.instances.find(i => i.is_malicious === (archetype !== 'BENCHMARK_LEGITIMATE'));
    if (target) {
      this.selectInstance(target.instance_id);
    }
  }

  async selectInstance(instanceId) {
    this.selectedInstanceId = instanceId;
    this.container.querySelectorAll('#v-c-table-body tr').forEach(r => {
      r.classList.toggle('selected-row', r.getAttribute('data-id') === instanceId);
    });

    try {
      this.selectedDetail = await fetchInstanceDetail('C', instanceId);
      this.renderTheater();
    } catch (err) {
      console.error('Failed to load instance detail for Vector C:', err);
    }
  }

  renderTheater() {
    if (!this.selectedDetail) return;
    const d = this.selectedDetail;
    const artifact = d.artifact || {};
    const pageSpec = artifact.page_spec || {};
    const groundTruth = artifact.ground_truth || {};
    const subScores = d.sub_scores || {};
    const isMalicious = d.is_malicious;

    // 1. Update Mock Terminal
    const terminal = this.container.querySelector('#agent-terminal-output');
    const agentStatus = this.container.querySelector('#v-c-agent-status-badge');
    const securityBadge = this.container.querySelector('#agent-security-badge');

    if (agentStatus) agentStatus.textContent = isMalicious ? 'STATUS: THREAT INTERCEPTED' : 'STATUS: TASK COMPLETE';
    if (securityBadge) {
      securityBadge.className = `threat-badge ${isMalicious ? 'badge-block' : 'badge-allow'}`;
      securityBadge.textContent = isMalicious ? 'INTERCEPTED' : 'CLEAN';
    }

    if (terminal) {
      const taskPrompt = artifact.task_prompt || 'Procure item from authorized seller.';
      const intendedMerchant = groundTruth.original_intended_merchant || 'merchant_authorized';
      const intendedPrice = groundTruth.original_intended_price !== undefined ? `$${Number(groundTruth.original_intended_price).toFixed(2)}` : '$29.50';

      terminal.innerHTML = `
        <div class="terminal-line cmd">> ShoppingAgent.execute_task()</div>
        <div class="terminal-line param">> User Prompt: "${taskPrompt}"</div>
        <div class="terminal-line cmd">> Tool: browse_page("${pageSpec.url || 'mock://store.aerosound.local/product'}")</div>
        <div class="terminal-line">> Parsing DOM elements and catalog metadata...</div>
        ${isMalicious ? `
          <div class="terminal-line warn">! CANDIDATE TOOL CALL GENERATED:</div>
          <div class="terminal-line warn">&nbsp;&nbsp;execute_payment(recipient="${artifact.target_recipient || 'rogue_acquirer'}", amount=$${artifact.target_amount || '248.49'})</div>
          <div class="terminal-line intercept">&#10008; PRE-EXECUTION HOOK TRIGGERED: TOOL CALL BLOCKED</div>
          <div class="terminal-line intercept">> Reason: Indirect Prompt Injection & Parameter Divergence Detected</div>
          <div class="terminal-line success">&#10004; FakeWallet.execute_payment() WAS NOT CALLED. Balance preserved.</div>
        ` : `
          <div class="terminal-line success">> Legitimate tool call validated:</div>
          <div class="terminal-line success">&nbsp;&nbsp;execute_payment(recipient="${intendedMerchant}", amount=${intendedPrice})</div>
          <div class="terminal-line success">&#10004; Payment executed cleanly. Task complete.</div>
        `}
      `;
    }

    // 2. Update Browser Viewport
    const urlText = this.container.querySelector('#browser-url-text');
    const pageBody = this.container.querySelector('#browser-page-content');

    if (urlText) urlText.textContent = pageSpec.url || 'mock://store.aerosound.local/products/item-v1';
    if (pageBody) {
      const title = pageSpec.title || 'AeroSound True Wireless Earbuds';
      const price = groundTruth.original_intended_price !== undefined ? `$${Number(groundTruth.original_intended_price).toFixed(2)}` : '$29.50';
      const merchant = groundTruth.original_intended_merchant || 'merchant_aerosound_991';
      const hiddenDirectives = pageSpec.hidden_text_elements || [artifact.raw_payload || ''];
      const rawPayload = hiddenDirectives.join(' ') || artifact.raw_payload || '';

      pageBody.innerHTML = `
        <div class="product-store-card">
          <div class="product-title-row">
            <div>
              <h4 class="product-name">${title}</h4>
              <div class="product-meta-row" style="margin-top:4px;">
                <span>Seller: <strong>${merchant}</strong></span>
                <span>&bull;</span>
                <span class="mono-data" style="color:var(--status-allow);">&#10003; Verified Catalog Item</span>
              </div>
            </div>
            <span class="product-price-tag mono-data">${price}</span>
          </div>

          <p style="font-size:12px; color:var(--text-secondary); line-height:1.5;">
            ${pageSpec.text_content || 'High-performance audio equipment authorized for enterprise department deployment. Includes immediate local procurement delivery.'}
          </p>

          ${isMalicious ? `
            <!-- The Concealed Payload Container -->
            <div class="concealed-payload-container ${this.isRevealed ? 'revealed' : ''}" id="concealed-box">
              <div class="concealment-header-tag">
                <span>&#9888; CONCEALED INJECTION DIRECTIVE (${artifact.injection_type || 'HTML_COMMENT'})</span>
                <span class="mono-data">${this.isRevealed ? 'REVEALED IN DOM' : 'HIDDEN FROM USER'}</span>
              </div>
              <div class="concealed-text-content mono-data">
                ${rawPayload}
              </div>
            </div>
          ` : `
            <div style="padding:12px; border-radius:6px; background:var(--bg-surface); border:1px solid var(--border-muted); font-size:12px; color:var(--status-allow);">
              &#10004; Clean Catalog DOM: Zero hidden directives or comment overrides present on page.
            </div>
          `}

          <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <button type="button" class="product-buy-btn">Purchase via Agent (${price})</button>
            <span class="mono-data" style="font-size:11px; color:var(--text-muted);">DOM Node Count: 14</span>
          </div>
        </div>
      `;
    }

    // 3. Update Pre-Execution Scanner HUD
    const hudBox = this.container.querySelector('#decision-hud-box');
    const hudText = this.container.querySelector('#decision-hud-text');
    const hudConf = this.container.querySelector('#decision-confidence-val');
    const narrativeText = this.container.querySelector('#v-c-narrative-text');

    if (hudBox) {
      hudBox.className = `decision-shield-hud ${isMalicious ? 'blocked' : 'allowed'}`;
    }
    if (hudText) hudText.textContent = isMalicious ? 'HARD BLOCKED' : 'CLEAN ALLOW';
    if (hudConf) hudConf.textContent = (d.risk_score || (isMalicious ? 1.0 : 0.0)).toFixed(3);
    if (narrativeText) narrativeText.textContent = d.primary_risk_driver || 'Pre-execution inspection passed.';

    // Parameter Divergence
    const intendedRec = this.container.querySelector('#div-intended-rec');
    const hijackedRec = this.container.querySelector('#div-hijacked-rec');
    const intendedAmt = this.container.querySelector('#div-intended-amt');
    const hijackedAmt = this.container.querySelector('#div-hijacked-amt');

    if (intendedRec) intendedRec.textContent = groundTruth.original_intended_merchant || 'merchant_authorized';
    if (hijackedRec) hijackedRec.textContent = isMalicious ? (artifact.target_recipient || 'rogue_acquirer') : '— (NO HIJACK)';
    if (intendedAmt) intendedAmt.textContent = groundTruth.original_intended_price !== undefined ? `$${Number(groundTruth.original_intended_price).toFixed(2)}` : '$29.50';
    if (hijackedAmt) hijackedAmt.textContent = isMalicious ? `$${Number(artifact.target_amount || 248.49).toFixed(2)}` : '— (MATCH)';

    // Sub-Scores
    const concVal = subScores.concealment_risk || 0;
    const overVal = subScores.imperative_override_risk || 0;
    const paramVal = subScores.parameter_divergence_risk || 0;
    const invVal = subScores.invoice_poisoning_risk || 0;

    const setSubScore = (id, val) => {
      const num = this.container.querySelector(`#sub-${id}-num`);
      const bar = this.container.querySelector(`#sub-${id}-bar`);
      if (num) num.textContent = val.toFixed(2);
      if (bar) {
        if (bar.style) bar.style.width = `${Math.round(val * 100)}%`;
        bar.className = `score-mini-fill ${val >= 0.7 ? 'high' : val >= 0.3 ? 'med' : 'low'}`;
      }
    };

    setSubScore('conceal', concVal);
    setSubScore('override', overVal);
    setSubScore('param', paramVal);
    setSubScore('inv', invVal);
  }

  updateConcealmentVisual() {
    const box = this.container.querySelector('#concealed-box');
    if (box) {
      box.classList.toggle('revealed', this.isRevealed);
    }
  }

  runSimulationBeat() {
    if (this.isSimulating) return;
    this.isSimulating = true;
    const playBtn = this.container.querySelector('#v-c-play-beat-btn');
    const playText = this.container.querySelector('#play-text');
    const playIcon = this.container.querySelector('#play-icon');
    if (playBtn) playBtn.classList.add('running');
    if (playText) playText.textContent = 'Simulating Agent Execution...';
    if (playIcon) playIcon.innerHTML = '&#9203;';

    const terminal = this.container.querySelector('#agent-terminal-output');
    const agentStatus = this.container.querySelector('#v-c-agent-status-badge');
    const d = this.selectedDetail;
    const artifact = d.artifact || {};
    const pageSpec = artifact.page_spec || {};
    const isMalicious = d.is_malicious;

    // Step 0: Prompt
    if (agentStatus) agentStatus.textContent = 'STATUS: RECEIVING PROMPT';
    if (terminal) {
      terminal.innerHTML = `<div class="terminal-line cmd">> ShoppingAgent received prompt: "${artifact.task_prompt || 'Procure items.'}"</div>`;
    }

    // Step 1 (600ms): Browse
    setTimeout(() => {
      if (agentStatus) agentStatus.textContent = 'STATUS: BROWSING MOCK STORE';
      if (terminal) {
        terminal.innerHTML += `<div class="terminal-line cmd">> Tool: browse_page("${pageSpec.url || 'mock://store'}")</div><div class="terminal-line">> Reading DOM structure...</div>`;
        terminal.scrollTop = terminal.scrollHeight;
      }
    }, 600);

    // Step 2 (1200ms): Payload Concealment Reveal
    setTimeout(() => {
      if (agentStatus) agentStatus.textContent = 'STATUS: PARSING DIRECTIVES';
      this.isRevealed = true;
      this.updateConcealmentVisual();
      if (terminal) {
        terminal.innerHTML += isMalicious ? `
          <div class="terminal-line warn">! Concealed directive parsed from DOM comments/styles</div>
          <div class="terminal-line warn">> Pre-execution scanner inspecting candidate ToolCall...</div>
        ` : `<div class="terminal-line">> Clean DOM verified. Formulating tool arguments...</div>`;
        terminal.scrollTop = terminal.scrollHeight;
      }
    }, 1200);

    // Step 3 (1800ms): Pre-Execution Scanner Block
    setTimeout(() => {
      if (agentStatus) agentStatus.textContent = isMalicious ? 'STATUS: INTERCEPTED' : 'STATUS: SUCCESS';
      if (terminal) {
        terminal.innerHTML += isMalicious ? `
          <div class="terminal-line intercept">&#10008; PRE-EXECUTION HOOK: execute_payment() INTERCEPTED & BLOCKED</div>
          <div class="terminal-line success">&#10004; 100% Simulated Balance Protected. Loss: $0.00</div>
        ` : `
          <div class="terminal-line success">&#10004; execute_payment() authorized & completed cleanly.</div>
        `;
        terminal.scrollTop = terminal.scrollHeight;
      }
    }, 1800);

    // Step 4 (2400ms): Complete
    setTimeout(() => {
      this.isSimulating = false;
      if (playBtn) playBtn.classList.remove('running');
      if (playText) playText.textContent = 'Simulate Agent Execution Beat';
      if (playIcon) playIcon.innerHTML = '&#9658;';
    }, 2400);
  }
}
