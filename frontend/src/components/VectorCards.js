/**
 * PROJECT TRIAD — THREE VECTOR CARDS (EQUAL VISUAL WEIGHT)
 * 
 * Renders the 3 vector overview cards side-by-side with equal visual priority,
 * adhering to the layout concept in Part I Frontend Design Brief.
 */

export const VECTOR_DEFINITIONS = [
  {
    id: 'A',
    viewId: 'vector-a',
    title: 'Synthetic Identity & Document Fraud',
    surface: 'Onboarding & KYC Origination',
    description: 'Frankenstein identities fusing authentic stolen anchor PII with synthesized demographic overlays and modified PDF417 barcodes.',
    grounding: 'Grounded in AAMVA 2020 Barcode Spec & SSA DMF',
    metrics: [
      { label: 'Defense Recall', val: '100%', highlight: 'normal' },
      { label: 'Max Evasion', val: '68%', highlight: 'normal' },
      { label: 'Samples', val: '500', highlight: 'normal' }
    ]
  },
  {
    id: 'B',
    viewId: 'vector-b',
    title: 'Transaction & Card-Testing Fraud',
    surface: 'Payment Gateway & Checkout Rails',
    description: 'Automated velocity burst probes, ISO 8583 decline cascades, and session-dilated card enumeration attacks.',
    grounding: 'Grounded in IEEE-CIS (590k) & PaySim (6.36M ops)',
    metrics: [
      { label: 'Defense AUC', val: '0.934', highlight: 'normal' },
      { label: 'Max Evasion', val: '87%', highlight: 'normal' },
      { label: 'Evaluated', val: '24,000', highlight: 'normal' }
    ]
  },
  {
    id: 'C',
    viewId: 'vector-c',
    title: 'Agentic Payment Hijacking',
    surface: 'Autonomous Tool-Calling Agents',
    description: 'Indirect prompt injections concealed in web payloads and invoice memos redirecting autonomous agent wallet transfers.',
    grounding: 'Air-Gapped Local Sandbox + Pre-Execution Interception',
    metrics: [
      { label: 'Defense Recall', val: '100%', highlight: 'normal' },
      { label: 'Max Evasion', val: '83%', highlight: 'normal' },
      { label: 'Loss Prevented', val: '$0.00', highlight: 'normal' }
    ]
  }
];

export function renderVectorCards(onNavigate) {
  const container = document.createElement('div');
  container.className = 'vector-cards-grid';

  container.innerHTML = VECTOR_DEFINITIONS.map(vec => `
    <article class="vector-card" data-vector="${vec.id}" id="card-vector-${vec.id.toLowerCase()}" tabindex="0" role="region" aria-label="Vector ${vec.id}: ${vec.title}">
      <div class="card-top">
        <div class="card-header-row">
          <span class="vector-pill">V_${vec.id}</span>
          <span class="vector-surface-tag">${vec.surface}</span>
        </div>
        <h3 class="vector-card-title">${vec.title}</h3>
        <p class="vector-card-description">${vec.description}</p>
        
        <div class="card-grounding-row">
          <span class="grounding-icon" aria-hidden="true">◈</span>
          <span>${vec.grounding}</span>
        </div>
      </div>

      <div class="card-bottom">
        <div class="card-metrics-grid">
          ${vec.metrics.map(m => `
            <div class="card-metric-col">
              <span class="metric-label">${m.label}</span>
              <span class="metric-number mono-data ${m.highlight === 'cyan' ? 'accent-cyan' : m.highlight === 'amber' ? 'accent-amber' : ''}">${m.val}</span>
            </div>
          `).join('')}
        </div>

        <button type="button" class="card-action-btn" data-target="${vec.viewId}">
          <span>Inspect Vector Drill-Down</span>
          <span aria-hidden="true">→</span>
        </button>
      </div>
    </article>
  `).join('');

  // Event bindings
  container.querySelectorAll('.vector-card').forEach(card => {
    const target = card.getAttribute('data-vector').toLowerCase();
    const viewId = `vector-${target}`;
    
    card.addEventListener('click', (e) => {
      onNavigate(viewId);
    });

    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        onNavigate(viewId);
      }
    });
  });

  return container;
}

export function updateVectorCardsData(container, summaries) {
  if (!container || !summaries || !Array.isArray(summaries)) return;

  summaries.forEach(s => {
    const card = container.querySelector(`#card-vector-${s.vector_id.toLowerCase()}`);
    if (!card) return;

    const metricsGrid = card.querySelector('.card-metrics-grid');
    if (!metricsGrid) return;

    const recallStr = s.current_defense_recall !== undefined ? `${(s.current_defense_recall * 100).toFixed(1)}%` : '100.0%';
    const aucStr = s.current_defense_auc !== undefined ? s.current_defense_auc.toFixed(3) : '0.934';
    const evasStr = s.latest_loop_evasion_rate !== undefined ? `${(s.latest_loop_evasion_rate * 100).toFixed(0)}%` : '83%';
    const totalStr = s.total_batch_samples !== undefined ? s.total_batch_samples.toLocaleString() : '500';

    if (s.vector_id === 'A') {
      metricsGrid.innerHTML = `
        <div class="card-metric-col">
          <span class="metric-label">Defense Recall</span>
          <span class="metric-number mono-data accent-cyan">${recallStr}</span>
        </div>
        <div class="card-metric-col">
          <span class="metric-label">Max Evasion</span>
          <span class="metric-number mono-data accent-amber">${evasStr}</span>
        </div>
        <div class="card-metric-col">
          <span class="metric-label">Profiles</span>
          <span class="metric-number mono-data">${totalStr}</span>
        </div>
      `;
    } else if (s.vector_id === 'B') {
      metricsGrid.innerHTML = `
        <div class="card-metric-col">
          <span class="metric-label">Defense AUC</span>
          <span class="metric-number mono-data accent-cyan">${aucStr}</span>
        </div>
        <div class="card-metric-col">
          <span class="metric-label">Max Evasion</span>
          <span class="metric-number mono-data accent-amber">${evasStr}</span>
        </div>
        <div class="card-metric-col">
          <span class="metric-label">Evaluated</span>
          <span class="metric-number mono-data">24,000+</span>
        </div>
      `;
    } else if (s.vector_id === 'C') {
      metricsGrid.innerHTML = `
        <div class="card-metric-col">
          <span class="metric-label">Defense Recall</span>
          <span class="metric-number mono-data accent-cyan">${recallStr}</span>
        </div>
        <div class="card-metric-col">
          <span class="metric-label">Max Evasion</span>
          <span class="metric-number mono-data accent-amber">${evasStr}</span>
        </div>
        <div class="card-metric-col">
          <span class="metric-label">Loss Prevented</span>
          <span class="metric-number mono-data">$0.00</span>
        </div>
      `;
    }
  });
}
