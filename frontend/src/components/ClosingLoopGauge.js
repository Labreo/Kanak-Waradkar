/**
 * PROJECT TRIAD — SIGNATURE CLOSING LOOP CONCENTRIC GAUGE
 * 
 * Renders an interactive SVG concentric ring/spiral visualization representing
 * closed-loop adversarial evasion trajectories across cycles (C0 -> C1 -> C2).
 * Color Palette: Cool Cyan (#5FD8D0) & Warm Amber (#F2A93B).
 */

export class ClosingLoopGauge {
  constructor(containerElement, options = {}) {
    this.container = containerElement;
    this.onCycleSelect = options.onCycleSelect || (() => {});
    this.currentCycle = options.initialCycle !== undefined ? options.initialCycle : 2;
    
    // Default 4-cycle progression representative of TRIAD telemetry
    this.cycleData = [
      {
        id: 'C0',
        label: 'Cycle 0 // Baseline',
        evasionRate: 0.0,
        detectionRate: 1.0,
        radius: 120,
        angle: 0,
        tier: 'Tier 1: Direct Probes',
        mutation: 'Naive Attack Signatures (Baseline Generation)',
        delta: '0.0%',
        deltaType: 'neutral'
      },
      {
        id: 'C1',
        label: 'Cycle 1 // Mutated',
        evasionRate: 0.29,
        detectionRate: 0.71,
        radius: 95,
        angle: 100,
        tier: 'Tier 2: Structural Camouflage',
        mutation: 'Repaired Barcodes, Session Dilation & CSS Cloaking',
        delta: '+29.0%',
        deltaType: 'positive'
      },
      {
        id: 'C2',
        label: 'Cycle 2 // Evolved',
        evasionRate: 0.83,
        detectionRate: 0.17,
        radius: 70,
        angle: 200,
        tier: 'Tier 3: Semantic Pretexting',
        mutation: 'Native EXIF, Organic Basket Sizes & AP Invoice Pretexts',
        delta: '+83.0%',
        deltaType: 'positive'
      },
      {
        id: 'C3',
        label: 'Cycle 3 // Retrained',
        evasionRate: 0.04,
        detectionRate: 0.96,
        radius: 48,
        angle: 300,
        tier: 'Tier 3: Retrained Defense',
        mutation: 'Closed-Loop Defense Retraining & Parameter Surface Adaptation',
        delta: '-79.0% RECOVERY',
        deltaType: 'positive'
      }
    ];

    this.render();
  }

  setCycle(cycleIndex) {
    if (cycleIndex >= 0 && cycleIndex < this.cycleData.length) {
      this.currentCycle = cycleIndex;
      this.updateHUD();
      this.updateActiveClasses();
      this.onCycleSelect(this.cycleData[this.currentCycle]);
    }
  }

  updateData(cycles) {
    if (Array.isArray(cycles) && cycles.length > 0) {
      const radii = [120, 95, 70, 48, 35];
      const count = cycles.length;

      this.cycleData = cycles.map((c, i) => {
        const evas = c.evasion_rate !== undefined ? c.evasion_rate : (c.evasionRate || 0);
        const muts = c.mutations_applied || [];
        let mutText = c.cycle_summary || (muts.length > 0 ? muts.map(m => m.parameter).join(', ') : 'Baseline Generation');
        
        let deltaVal = '0.0%';
        let deltaType = 'neutral';
        if (i > 0) {
          const prevEvas = cycles[i - 1].evasion_rate !== undefined ? cycles[i - 1].evasion_rate : 0;
          const diff = evas - prevEvas;
          if (diff < -0.05) {
            deltaVal = `-${(Math.abs(diff) * 100).toFixed(1)}% RECOV`;
            deltaType = 'positive';
          } else if (diff > 0.05) {
            deltaVal = `+${(diff * 100).toFixed(1)}% GAIN`;
            deltaType = 'positive';
          } else {
            deltaVal = `${diff >= 0 ? '+' : ''}${(diff * 100).toFixed(1)}%`;
          }
        }

        const angle = count > 1 ? (i / count) * 360 : 0;

        return {
          id: `C${c.cycle_index !== undefined ? c.cycle_index : i}`,
          label: `Cycle ${c.cycle_index !== undefined ? c.cycle_index : i} // ${c.mutation_tier || 'MUTATED'}`,
          evasionRate: evas,
          detectionRate: 1.0 - evas,
          radius: radii[Math.min(i, radii.length - 1)],
          angle: angle,
          tier: c.mutation_tier ? c.mutation_tier.replace(/_/g, ' ') : `Cycle ${i}`,
          mutation: mutText,
          delta: deltaVal,
          deltaType: deltaType
        };
      });

      this.currentCycle = this.cycleData.length - 1;
      this.render();
      this.onCycleSelect(this.cycleData[this.currentCycle]);
    }
  }

  nextCycle() {
    const next = (this.currentCycle + 1) % this.cycleData.length;
    this.setCycle(next);
  }

  render() {
    this.container.innerHTML = `
      <div class="loop-gauge-container">
        <div class="loop-gauge-viewport">
          <svg class="loop-svg" viewBox="-160 -160 320 320" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="spiralGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#5FD8D0" />
                <stop offset="55%" stop-color="#F2A93B" />
                <stop offset="100%" stop-color="#E09B32" />
              </linearGradient>
              <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="rgba(95, 216, 208, 0.12)" />
                <stop offset="100%" stop-color="transparent" />
              </radialGradient>
            </defs>

            <!-- Center ambient glow -->
            <circle cx="0" cy="0" r="140" fill="url(#centerGlow)" />

            <!-- Concentric Guide Rings -->
            ${this.cycleData.map((c, i) => `
              <circle cx="0" cy="0" r="${c.radius}" class="gauge-track ${this.currentCycle === i ? 'active-track' : ''}" id="track-${i}" />
            `).join('')}

            <!-- Dynamic Tightening Spiral Curve -->
            <path id="spiral-path" class="gauge-spiral-path" d="${this.calculateSpiralPath()}" />

            <!-- Cycle Marker Nodes -->
            ${this.renderCycleNodes()}
          </svg>

          <!-- Center Information HUD -->
          <div class="gauge-center-hud">
            <span class="gauge-cycle-tag" id="hud-cycle-tag">CYCLE 3</span>
            <span class="gauge-rate-number mono-data" id="hud-rate-number">4%</span>
            <span class="gauge-rate-label">EVASION RATE</span>
            <span class="gauge-delta-pill positive" id="hud-delta-pill">RECOVERY</span>
          </div>
        </div>

        <!-- Interactive Cycle Selector Controls -->
        <div class="loop-controls-bar" role="group" aria-label="Closed Loop Cycle Selector">
          ${this.cycleData.map((c, i) => `
            <button type="button" class="cycle-btn ${i === this.currentCycle ? 'active' : ''}" data-cycle="${i}" id="cycle-btn-${i}">
              <span class="cycle-btn-id">${c.id}</span>
              <span class="cycle-btn-metric">${(c.evasionRate * 100).toFixed(0)}% Evas.</span>
            </button>
          `).join('')}
        </div>

        <!-- Loop Evolution Summary -->
        <div class="loop-summary-text" id="loop-summary-text">
          ${this.cycleData[this.currentCycle].mutation}
        </div>
      </div>
    `;

    this.bindEvents();
    this.updateHUD();
  }

  calculateSpiralPath() {
    if (this.cycleData.length < 2) return '';
    const points = this.cycleData.map(c => this.polarToCartesian(c.radius, c.angle));
    let path = `M ${points[0].x} ${points[0].y}`;
    for (let i = 0; i < points.length - 1; i++) {
      const p0 = points[i];
      const p1 = points[i + 1];
      path += ` Q ${p0.x * 0.7 + p1.x * 0.4} ${p0.y * 0.4 + p1.y * 0.7} ${p1.x} ${p1.y}`;
    }
    return path;
  }

  polarToCartesian(radius, angleInDegrees) {
    const angleInRadians = (angleInDegrees * Math.PI) / 180.0;
    return {
      x: +(radius * Math.cos(angleInRadians)).toFixed(2),
      y: +(radius * Math.sin(angleInRadians)).toFixed(2)
    };
  }

  renderCycleNodes() {
    return this.cycleData.map((c, i) => {
      const pos = this.polarToCartesian(c.radius, c.angle);
      const isSelected = i === this.currentCycle;
      return `
        <g class="cycle-node-group" data-cycle="${i}">
          <circle cx="${pos.x}" cy="${pos.y}" r="8" class="cycle-node-outer ${isSelected ? 'selected' : ''}" id="node-outer-${i}" />
          <circle cx="${pos.x}" cy="${pos.y}" r="3.5" class="cycle-node-inner" id="node-inner-${i}" />
        </g>
      `;
    }).join('');
  }

  bindEvents() {
    const buttons = this.container.querySelectorAll('.cycle-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const idx = parseInt(btn.getAttribute('data-cycle'), 10);
        this.setCycle(idx);
      });
    });

    const nodeGroups = this.container.querySelectorAll('.cycle-node-group');
    nodeGroups.forEach(g => {
      g.addEventListener('click', () => {
        const idx = parseInt(g.getAttribute('data-cycle'), 10);
        this.setCycle(idx);
      });
    });
  }

  updateHUD() {
    const current = this.cycleData[this.currentCycle];
    const hudTag = this.container.querySelector('#hud-cycle-tag');
    const hudNumber = this.container.querySelector('#hud-rate-number');
    const hudDelta = this.container.querySelector('#hud-delta-pill');
    const summaryText = this.container.querySelector('#loop-summary-text');

    if (hudTag) hudTag.textContent = current.id + ' // ' + current.tier.split(':')[0];
    if (hudNumber) hudNumber.textContent = `${(current.evasionRate * 100).toFixed(0)}%`;
    if (hudDelta) {
      hudDelta.textContent = current.delta + ' GAIN';
      hudDelta.className = `gauge-delta-pill ${current.deltaType}`;
    }
    if (summaryText) {
      summaryText.textContent = `${current.tier}: ${current.mutation}`;
    }
  }

  updateActiveClasses() {
    this.cycleData.forEach((_, i) => {
      const btn = this.container.querySelector(`#cycle-btn-${i}`);
      const track = this.container.querySelector(`#track-${i}`);
      const outerNode = this.container.querySelector(`#node-outer-${i}`);
      
      if (btn) btn.classList.toggle('active', i === this.currentCycle);
      if (track) track.classList.toggle('active-track', i === this.currentCycle);
      if (outerNode) outerNode.classList.toggle('selected', i === this.currentCycle);
    });
  }
}
