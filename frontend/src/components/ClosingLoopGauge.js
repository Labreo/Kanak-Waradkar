/**
 * PROJECT TRIAD — SIGNATURE CLOSING LOOP RADIAL PROGRESS GAUGE
 * 
 * Renders a genuine radial progress ring visualization representing
 * closed-loop adversarial evasion trajectories across cycles (C0 -> C1 -> C2 -> C3).
 * 
 * Geometry:
 * - Single continuous circular ring (radius R = 110, circumference C = 2 * PI * R ≈ 691.15).
 * - Arc fill length is computed directly and proportionally from current evasion rate:
 *   stroke-dashoffset = C * (1.0 - evasionRate)
 * - Cycle markers sit as labeled points along that single continuous ring
 *   at their exact proportional angular positions (angle = evasionRate * 360°).
 * - Smooth CSS transitions animate the ring filling/emptying when switching cycles.
 * - Initial state renders pure content-free skeleton shimmer blocks with zero hardcoded digits.
 * - Color Palette: Cool Cyan (#5FD8D0) & Warm Amber (#F2A93B).
 */

export class ClosingLoopGauge {
  constructor(containerElement, options = {}) {
    this.container = containerElement;
    this.onCycleSelect = options.onCycleSelect || (() => {});
    this.currentCycle = options.initialCycle !== undefined ? options.initialCycle : 0;
    this.radius = 110;
    this.circumference = +(2 * Math.PI * this.radius).toFixed(2); // ~691.15

    // Initialize with provided cycle data if passed, otherwise empty array for shimmer loading state
    const initialCycles = options.cycleData || options.cycles || [];
    this.cycleData = [];
    if (Array.isArray(initialCycles) && initialCycles.length > 0) {
      this.updateData(initialCycles, false);
    } else {
      this.render();
    }
  }

  setCycle(cycleIndex) {
    if (this.cycleData && this.cycleData.length > 0 && cycleIndex >= 0 && cycleIndex < this.cycleData.length) {
      this.currentCycle = cycleIndex;
      this.updateHUD();
      this.updateArc();
      this.updateActiveClasses();
      this.onCycleSelect(this.cycleData[this.currentCycle]);
    }
  }

  updateData(cycles, triggerSelect = true) {
    if (Array.isArray(cycles) && cycles.length > 0) {
      this.cycleData = cycles.map((c, i) => {
        const evas = c.evasion_rate !== undefined ? c.evasion_rate : (c.evasionRate || 0);
        const muts = c.mutations_applied || [];
        const mutText = c.cycle_summary || (muts.length > 0 ? muts.map(m => m.parameter).join(', ') : 'Baseline Generation');
        
        let deltaVal = '0.0%';
        let deltaType = 'neutral';
        if (i > 0) {
          const prevEvas = cycles[i - 1].evasion_rate !== undefined ? cycles[i - 1].evasion_rate : (cycles[i - 1].evasionRate || 0);
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

        return {
          id: c.id || `C${c.cycle_index !== undefined ? c.cycle_index : i}`,
          label: c.label || `Cycle ${c.cycle_index !== undefined ? c.cycle_index : i} // ${c.mutation_tier ? c.mutation_tier.replace(/_/g, ' ') : 'MUTATED'}`,
          evasionRate: evas,
          detectionRate: 1.0 - evas,
          tier: c.tier || (c.mutation_tier ? c.mutation_tier.replace(/_/g, ' ') : `Cycle ${i}`),
          mutation: mutText,
          delta: c.delta || deltaVal,
          deltaType: c.deltaType || deltaType
        };
      });

      if (this.currentCycle >= this.cycleData.length || this.currentCycle < 0) {
        this.currentCycle = Math.min(2, this.cycleData.length - 1);
      }
      this.render();
      if (triggerSelect && this.cycleData[this.currentCycle]) {
        this.onCycleSelect(this.cycleData[this.currentCycle]);
      }
    } else {
      this.cycleData = [];
      this.render();
    }
  }

  nextCycle() {
    if (!this.cycleData || this.cycleData.length === 0) return;
    const next = (this.currentCycle + 1) % this.cycleData.length;
    this.setCycle(next);
  }

  /**
   * Computes Cartesian coordinate (x, y) on the radial ring for a given evasion rate percentage.
   * Angle starts at 12 o'clock (0°) and progresses clockwise (0.25 -> 3 o'clock, 0.5 -> 6 o'clock, etc.).
   */
  calculateRingCoordinates(evasionRate, radius = this.radius) {
    const angleDeg = (evasionRate || 0) * 360;
    const angleRad = (angleDeg * Math.PI) / 180.0;
    return {
      x: +(radius * Math.sin(angleRad)).toFixed(2),
      y: +(-radius * Math.cos(angleRad)).toFixed(2),
      angle: angleDeg
    };
  }

  /**
   * Backward-compatible polarToCartesian helper.
   * Angle in degrees where 0° is right (+X) or standard trigonometry.
   */
  polarToCartesian(radius, angleInDegrees) {
    const angleInRadians = (angleInDegrees * Math.PI) / 180.0;
    return {
      x: +(radius * Math.cos(angleInRadians)).toFixed(2),
      y: +(radius * Math.sin(angleInRadians)).toFixed(2)
    };
  }

  /**
   * Computes stroke-dashoffset for a given evasion rate.
   * 0.0 -> offset = C (empty)
   * 1.0 -> offset = 0 (full circle)
   */
  calculateDashOffset(evasionRate) {
    const clamped = Math.max(0, Math.min(1, evasionRate || 0));
    return +(this.circumference * (1.0 - clamped)).toFixed(2);
  }

  render() {
    if (!this.cycleData || this.cycleData.length === 0) {
      this.renderLoadingState();
      return;
    }

    const current = this.cycleData[this.currentCycle] || this.cycleData[0];
    const initialDashOffset = this.calculateDashOffset(current.evasionRate);
    const headPos = this.calculateRingCoordinates(current.evasionRate);

    this.container.innerHTML = `
      <div class="loop-gauge-container">
        <div class="loop-gauge-viewport">
          <svg class="loop-svg" viewBox="-160 -160 320 320" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="gaugeArcGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#5FD8D0" />
                <stop offset="45%" stop-color="#7CE3DC" />
                <stop offset="80%" stop-color="#F2A93B" />
                <stop offset="100%" stop-color="#FF9E1B" />
              </linearGradient>
              <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="rgba(95, 216, 208, 0.14)" />
                <stop offset="70%" stop-color="rgba(242, 169, 59, 0.04)" />
                <stop offset="100%" stop-color="transparent" />
              </radialGradient>
              <filter id="arcGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            <!-- Center ambient glow -->
            <circle cx="0" cy="0" r="135" fill="url(#centerGlow)" />

            <!-- Calibrated Radial Scale Ticks -->
            ${this.renderScaleTicks()}

            <!-- Background Continuous Track Ring -->
            <circle cx="0" cy="0" r="${this.radius}" class="gauge-track-bg" />

            <!-- Genuine Proportional Radial Progress Ring -->
            <circle
              id="gauge-progress-arc"
              cx="0"
              cy="0"
              r="${this.radius}"
              class="gauge-progress-arc"
              stroke-dasharray="${this.circumference}"
              stroke-dashoffset="${initialDashOffset}"
              transform="rotate(-90)"
            />

            <!-- Leading Edge Indicator Head -->
            <circle
              id="gauge-indicator-head"
              cx="${headPos.x}"
              cy="${headPos.y}"
              r="4.5"
              class="gauge-indicator-head ${current.evasionRate > 0 ? 'active' : ''}"
            />

            <!-- Cycle Marker Nodes positioned proportionally along the single continuous ring -->
            ${this.renderCycleMarkers()}
          </svg>

          <!-- Center Information HUD -->
          <div class="gauge-center-hud">
            <span class="gauge-cycle-tag" id="hud-cycle-tag">${current.id} // ${(current.tier || '').split(':')[0]}</span>
            <span class="gauge-rate-number mono-data" id="hud-rate-number">${(current.evasionRate * 100).toFixed(0)}%</span>
            <span class="gauge-rate-label">EVASION RATE</span>
            <span class="gauge-delta-pill ${current.deltaType}" id="hud-delta-pill">${current.delta}</span>
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
          ${current.tier}: ${current.mutation}
        </div>
      </div>
    `;

    this.bindEvents();
    this.updateHUD();
  }

  renderLoadingState() {
    this.container.innerHTML = `
      <div class="loop-gauge-container">
        <div class="loop-gauge-viewport">
          <svg class="loop-svg" viewBox="-160 -160 320 320" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="gaugeArcGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#5FD8D0" />
                <stop offset="45%" stop-color="#7CE3DC" />
                <stop offset="80%" stop-color="#F2A93B" />
                <stop offset="100%" stop-color="#FF9E1B" />
              </linearGradient>
              <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="rgba(95, 216, 208, 0.14)" />
                <stop offset="70%" stop-color="rgba(242, 169, 59, 0.04)" />
                <stop offset="100%" stop-color="transparent" />
              </radialGradient>
            </defs>

            <!-- Center ambient glow -->
            <circle cx="0" cy="0" r="135" fill="url(#centerGlow)" />

            <!-- Calibrated Radial Scale Ticks -->
            ${this.renderScaleTicks()}

            <!-- Background Continuous Track Ring -->
            <circle cx="0" cy="0" r="${this.radius}" class="gauge-track-bg" />

            <!-- Empty Progress Ring -->
            <circle
              id="gauge-progress-arc"
              cx="0"
              cy="0"
              r="${this.radius}"
              class="gauge-progress-arc"
              stroke-dasharray="${this.circumference}"
              stroke-dashoffset="${this.circumference}"
              transform="rotate(-90)"
            />
          </svg>

          <!-- Center Information HUD Shimmer -->
          <div class="gauge-center-hud">
            <span class="gauge-cycle-tag" id="hud-cycle-tag"><span class="skeleton-shimmer" style="width:72px; height:18px; border-radius:var(--radius-xs); display:inline-block;" aria-label="Loading cycle..."></span></span>
            <span class="gauge-rate-number mono-data" id="hud-rate-number"><span class="skeleton-shimmer skeleton-lg" style="width:80px; height:38px; border-radius:var(--radius-sm); display:inline-block;" aria-label="Loading evasion rate..."></span></span>
            <span class="gauge-rate-label">EVASION RATE</span>
            <span class="gauge-delta-pill neutral" id="hud-delta-pill"><span class="skeleton-shimmer" style="width:56px; height:18px; border-radius:9999px; display:inline-block;" aria-label="Loading delta..."></span></span>
          </div>
        </div>

        <!-- Interactive Cycle Selector Shimmer Controls -->
        <div class="loop-controls-bar" role="group" aria-label="Closed Loop Cycle Selector">
          <span class="skeleton-shimmer" style="width:84px; height:42px; border-radius:var(--radius-md); display:inline-block;" aria-label="Loading cycle controls..."></span>
          <span class="skeleton-shimmer" style="width:84px; height:42px; border-radius:var(--radius-md); display:inline-block;" aria-label="Loading cycle controls..."></span>
          <span class="skeleton-shimmer" style="width:84px; height:42px; border-radius:var(--radius-md); display:inline-block;" aria-label="Loading cycle controls..."></span>
          <span class="skeleton-shimmer" style="width:84px; height:42px; border-radius:var(--radius-md); display:inline-block;" aria-label="Loading cycle controls..."></span>
        </div>

        <!-- Loop Evolution Summary Shimmer -->
        <div class="loop-summary-text" id="loop-summary-text">
          <span class="skeleton-shimmer skeleton-text" style="width:240px; height:14px; border-radius:var(--radius-xs); display:inline-block;" aria-label="Loading summary..."></span>
        </div>
      </div>
    `;
  }

  /**
   * Renders calibrated tick marks around the ring to allow immediate visual estimation.
   */
  renderScaleTicks() {
    const ticks = [];
    // Major ticks every 25% (0%, 25%, 50%, 75%), Minor ticks every 5%
    for (let p = 0; p < 1.0; p += 0.05) {
      const isMajor = Math.abs(p % 0.25) < 0.001;
      const rInner = isMajor ? this.radius - 8 : this.radius - 4;
      const rOuter = isMajor ? this.radius + 8 : this.radius + 4;
      const pInner = this.calculateRingCoordinates(p, rInner);
      const pOuter = this.calculateRingCoordinates(p, rOuter);
      
      ticks.push(`
        <line
          x1="${pInner.x}"
          y1="${pInner.y}"
          x2="${pOuter.x}"
          y2="${pOuter.y}"
          class="gauge-scale-tick ${isMajor ? 'major' : 'minor'}"
        />
      `);

      if (isMajor) {
        const pLabel = this.calculateRingCoordinates(p, this.radius - 18);
        ticks.push(`
          <text
            x="${pLabel.x}"
            y="${pLabel.y + 3}"
            class="gauge-scale-label"
            text-anchor="middle"
          >${Math.round(p * 100)}%</text>
        `);
      }
    }
    return ticks.join('');
  }

  /**
   * Renders cycle markers positioned along the single continuous ring at their exact proportional angle.
   */
  renderCycleMarkers() {
    if (!this.cycleData || this.cycleData.length === 0) return '';

    return this.cycleData.map((c, i) => {
      const pos = this.calculateRingCoordinates(c.evasionRate, this.radius);
      const isSelected = i === this.currentCycle;

      // Calculate radial badge position with smart offset to prevent overlapping
      // (e.g. C0 at 0% and C3 at 4%)
      let badgeAngle = c.evasionRate * 360;
      if (c.evasionRate === 0 && this.cycleData.some((other, idx) => idx !== i && other.evasionRate > 0 && other.evasionRate <= 0.06)) {
        badgeAngle = -12; // nudge C0 slightly left if near C3
      } else if (c.evasionRate > 0 && c.evasionRate <= 0.06 && this.cycleData.some((other, idx) => idx !== i && other.evasionRate === 0)) {
        badgeAngle = 18; // nudge C3 slightly right if near C0
      }

      const badgeRad = (badgeAngle * Math.PI) / 180.0;
      const badgeR = this.radius + 26;
      const badgeX = +(badgeR * Math.sin(badgeRad)).toFixed(2);
      const badgeY = +(-badgeR * Math.cos(badgeRad)).toFixed(2);

      return `
        <g class="cycle-marker-group ${isSelected ? 'selected' : ''}" data-cycle="${i}" id="marker-group-${i}">
          <!-- Radial connector tick line from ring to badge -->
          <line
            x1="${pos.x}"
            y1="${pos.y}"
            x2="${badgeX}"
            y2="${badgeY}"
            class="cycle-marker-connector"
          />

          <!-- Node Ring Pin -->
          <circle cx="${pos.x}" cy="${pos.y}" r="8" class="cycle-marker-node ${isSelected ? 'selected' : ''}" id="node-outer-${i}" />
          <circle cx="${pos.x}" cy="${pos.y}" r="3.5" class="cycle-marker-inner" id="node-inner-${i}" />

          <!-- Node Label Badge -->
          <g class="cycle-marker-badge-group" transform="translate(${badgeX}, ${badgeY})">
            <rect
              x="-18"
              y="-10"
              width="36"
              height="20"
              rx="4"
              class="cycle-marker-badge-bg ${isSelected ? 'selected' : ''}"
              id="node-badge-bg-${i}"
            />
            <text
              x="0"
              y="3.5"
              text-anchor="middle"
              class="cycle-marker-badge-text ${isSelected ? 'selected' : ''}"
              id="node-badge-text-${i}"
            >${c.id}</text>
          </g>
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

    const markerGroups = this.container.querySelectorAll('.cycle-marker-group');
    markerGroups.forEach(g => {
      g.addEventListener('click', () => {
        const idx = parseInt(g.getAttribute('data-cycle'), 10);
        this.setCycle(idx);
      });
    });
  }

  /**
   * Dynamically updates the radial progress arc offset and indicator head position
   * with smooth transition animations.
   */
  updateArc() {
    if (!this.cycleData || this.cycleData.length === 0) return;
    const current = this.cycleData[this.currentCycle];
    if (!current) return;

    const arc = this.container.querySelector('#gauge-progress-arc');
    if (arc) {
      const newOffset = this.calculateDashOffset(current.evasionRate);
      arc.style.strokeDashoffset = newOffset;
    }

    const head = this.container.querySelector('#gauge-indicator-head');
    if (head) {
      const pos = this.calculateRingCoordinates(current.evasionRate);
      head.setAttribute('cx', pos.x);
      head.setAttribute('cy', pos.y);
      head.classList.toggle('active', current.evasionRate > 0);
    }
  }

  updateHUD() {
    if (!this.cycleData || this.cycleData.length === 0) return;
    const current = this.cycleData[this.currentCycle];
    if (!current) return;

    const hudTag = this.container.querySelector('#hud-cycle-tag');
    const hudNumber = this.container.querySelector('#hud-rate-number');
    const hudDelta = this.container.querySelector('#hud-delta-pill');
    const summaryText = this.container.querySelector('#loop-summary-text');

    if (hudTag) hudTag.textContent = `${current.id} // ${(current.tier || '').split(':')[0]}`;
    if (hudNumber) hudNumber.textContent = `${(current.evasionRate * 100).toFixed(0)}%`;
    if (hudDelta) {
      hudDelta.textContent = current.delta;
      hudDelta.className = `gauge-delta-pill ${current.deltaType}`;
    }
    if (summaryText) {
      summaryText.textContent = `${current.tier}: ${current.mutation}`;
    }
  }

  updateActiveClasses() {
    if (!this.cycleData || this.cycleData.length === 0) return;
    this.cycleData.forEach((_, i) => {
      const isCurrent = i === this.currentCycle;
      const btn = this.container.querySelector(`#cycle-btn-${i}`);
      const group = this.container.querySelector(`#marker-group-${i}`);
      const outerNode = this.container.querySelector(`#node-outer-${i}`);
      const badgeBg = this.container.querySelector(`#node-badge-bg-${i}`);
      const badgeText = this.container.querySelector(`#node-badge-text-${i}`);

      if (btn) btn.classList.toggle('active', isCurrent);
      if (group) group.classList.toggle('selected', isCurrent);
      if (outerNode) outerNode.classList.toggle('selected', isCurrent);
      if (badgeBg) badgeBg.classList.toggle('selected', isCurrent);
      if (badgeText) badgeText.classList.toggle('selected', isCurrent);
    });
  }
}
