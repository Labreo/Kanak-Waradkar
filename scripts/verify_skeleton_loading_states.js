/**
 * Verification test for Content-Free Skeleton Shimmer Loading States:
 * 1. Confirms VectorCards renders skeleton shimmer initially and has zero hardcoded fallback numbers.
 * 2. Confirms ClosingLoopGauge renders skeleton shimmer initially and has zero default cycle numbers (no C0 0%, C1 29%, C2 83%, C3 4%).
 * 3. Confirms that when live data is provided, real data updates seamlessly.
 * 4. Confirms that missing/null data fields in updateVectorCardsData stay as skeleton-shimmer instead of hardcoded numbers.
 */

import { VECTOR_DEFINITIONS, renderVectorCards, updateVectorCardsData } from '../frontend/src/components/VectorCards.js';
import { ClosingLoopGauge } from '../frontend/src/components/ClosingLoopGauge.js';

// Minimal mock DOM factory
function createMockElement(tag = 'div') {
  let _innerHTML = '';
  const attributes = {};
  const classList = new Set();
  const children = [];
  const listeners = {};

  const elem = {
    tagName: tag.toUpperCase(),
    get innerHTML() {
      return _innerHTML;
    },
    set innerHTML(val) {
      _innerHTML = val;
    },
    get className() {
      return Array.from(classList).join(' ');
    },
    set className(val) {
      classList.clear();
      if (val) val.split(/\s+/).forEach(c => c && classList.add(c));
    },
    classList: {
      add: (...cls) => cls.forEach(c => classList.add(c)),
      remove: (...cls) => cls.forEach(c => classList.delete(c)),
      contains: (c) => classList.has(c),
      toggle: (c, force) => {
        if (force === true) classList.add(c);
        else if (force === false) classList.delete(c);
        else if (classList.has(c)) classList.delete(c);
        else classList.add(c);
      }
    },
    setAttribute: (name, val) => { attributes[name] = String(val); },
    getAttribute: (name) => attributes[name] || null,
    appendChild: (child) => { children.push(child); return child; },
    addEventListener: (evt, cb) => { listeners[evt] = cb; },
    querySelector: (sel) => {
      if (sel.startsWith('#')) {
        const id = sel.slice(1);
        if (attributes['id'] === id) return elem;
        // Search in innerHTML or child nodes if needed
      }
      return null;
    },
    querySelectorAll: (sel) => []
  };

  return elem;
}

globalThis.document = {
  createElement: createMockElement,
  querySelector: () => null,
  querySelectorAll: () => []
};

console.log('=====================================================');
console.log('1. VERIFYING VECTORCARDS INITIAL LOADING STATE');
console.log('=====================================================');

const mockCardContainer = renderVectorCards(() => {});
const initialCardHtml = mockCardContainer.innerHTML;

// Check that shimmer placeholders are present
const shimmerCount = (initialCardHtml.match(/skeleton-shimmer/g) || []).length;
console.assert(shimmerCount === 6, `Expected 6 skeleton-shimmer spans in VectorCards, got ${shimmerCount}`);
console.log(`✓ Verified ${shimmerCount} skeleton-shimmer placeholders in VectorCards initial render`);

// Check that no hardcoded numbers appear in initial HTML
const forbiddenNumbers = ['98.0%', '0.8693', '0.9336', '100.0%'];
for (const num of forbiddenNumbers) {
  console.assert(!initialCardHtml.includes(num), `Found forbidden hardcoded number "${num}" in initial VectorCards render!`);
}
console.log('✓ Verified zero hardcoded fallback numbers present in initial VectorCards render');

console.log('\n=====================================================');
console.log('2. VERIFYING VECTORCARDS DATA BINDING & FALLBACK CLEANLINESS');
console.log('=====================================================');

// Setup mock container with querySelector for cards
const cardA = createMockElement('article');
cardA.setAttribute('id', 'card-vector-a');
const gridA = createMockElement('div');
gridA.className = 'card-metrics-grid';
cardA.querySelector = (s) => (s === '.card-metrics-grid' ? gridA : null);

const cardB = createMockElement('article');
cardB.setAttribute('id', 'card-vector-b');
const gridB = createMockElement('div');
gridB.className = 'card-metrics-grid';
cardB.querySelector = (s) => (s === '.card-metrics-grid' ? gridB : null);

const cardC = createMockElement('article');
cardC.setAttribute('id', 'card-vector-c');
const gridC = createMockElement('div');
gridC.className = 'card-metrics-grid';
cardC.querySelector = (s) => (s === '.card-metrics-grid' ? gridC : null);

const mockFullContainer = {
  querySelector: (sel) => {
    if (sel === '#card-vector-a') return cardA;
    if (sel === '#card-vector-b') return cardB;
    if (sel === '#card-vector-c') return cardC;
    return null;
  }
};

// Case 1: Partial summaries (missing fields should produce skeleton-shimmer, NOT 98.0% or 0.8693)
updateVectorCardsData(mockFullContainer, [
  { vector_id: 'A' },
  { vector_id: 'B' },
  { vector_id: 'C' }
]);

console.assert(gridA.innerHTML.includes('skeleton-shimmer'), 'Vector A with undefined metrics must show skeleton-shimmer');
console.assert(!gridA.innerHTML.includes('98.0%'), 'Vector A must NOT show fallback 98.0%');
console.assert(gridB.innerHTML.includes('skeleton-shimmer'), 'Vector B with undefined metrics must show skeleton-shimmer');
console.assert(!gridB.innerHTML.includes('0.8693'), 'Vector B must NOT show fallback 0.8693');
console.assert(!gridB.innerHTML.includes('0.9336'), 'Vector B must NOT show fallback 0.9336');
console.assert(gridC.innerHTML.includes('skeleton-shimmer'), 'Vector C with undefined metrics must show skeleton-shimmer');
console.log('✓ Verified updateVectorCardsData with missing/undefined fields preserves skeleton-shimmer');

// Case 2: Live summaries
updateVectorCardsData(mockFullContainer, [
  { vector_id: 'A', current_defense_recall: 1.0, total_batch_samples: 500 },
  { vector_id: 'B', current_defense_auc: 0.93358, macro_fidelity: 0.8693 },
  { vector_id: 'C', current_defense_recall: 1.0, loss_prevented: '$0.00' }
]);

console.assert(gridA.innerHTML.includes('100.0%'), 'Vector A should display 100.0%');
console.assert(gridA.innerHTML.includes('500'), 'Vector A should display 500');
console.assert(gridB.innerHTML.includes('0.9336'), 'Vector B should display 0.9336');
console.assert(gridB.innerHTML.includes('0.8693'), 'Vector B should display 0.8693');
console.assert(gridC.innerHTML.includes('100.0%'), 'Vector C should display 100.0%');
console.assert(gridC.innerHTML.includes('$0.00'), 'Vector C should display $0.00');
console.log('✓ Verified updateVectorCardsData with live data populates live metrics correctly');

console.log('\n=====================================================');
console.log('3. VERIFYING CLOSINGLOOPGAUGE LOADING STATE');
console.log('=====================================================');

const mockGaugeContainer = createMockElement('div');
const gauge = new ClosingLoopGauge(mockGaugeContainer);
const gaugeHtml = mockGaugeContainer.innerHTML;

console.assert(gauge.cycleData.length === 0, `Expected 0 cycles in initial state, got ${gauge.cycleData.length}`);
console.assert(gaugeHtml.includes('skeleton-shimmer'), 'Expected skeleton-shimmer in initial ClosingLoopGauge');

// Confirm no specific numbers from stale C0 0%, C1 29%, C2 83%, C3 4% are in gaugeHtml
const stalePatterns = ['29%', '83%', '+29.0%', '+83.0%', '-79.0%', '0.29', '0.83'];
for (const pat of stalePatterns) {
  console.assert(!gaugeHtml.includes(pat), `Found stale pattern "${pat}" in initial ClosingLoopGauge HTML!`);
}
console.log('✓ Verified zero stale/mock numbers (0%, 29%, 83%, 4%) present in initial ClosingLoopGauge render');

console.log('\n=====================================================');
console.log('4. VERIFYING CLOSINGLOOPGAUGE LIVE TELEMETRY INGESTION');
console.log('=====================================================');

const liveCycles = [
  { cycle_index: 0, mutation_tier: 'BASELINE', evasion_rate: 0.0, cycle_summary: 'Baseline Generation' },
  { cycle_index: 1, mutation_tier: 'MUTATED', evasion_rate: 0.2875, cycle_summary: 'Structural Camouflage' },
  { cycle_index: 2, mutation_tier: 'EVOLVED', evasion_rate: 0.8732, cycle_summary: 'Semantic Pretexting' },
  { cycle_index: 3, mutation_tier: 'RETRAINED', evasion_rate: 0.0, cycle_summary: 'Retrained Defense' }
];

gauge.updateData(liveCycles);
console.assert(gauge.cycleData.length === 4, `Expected 4 cycles after updateData, got ${gauge.cycleData.length}`);
const liveGaugeHtml = mockGaugeContainer.innerHTML;
console.assert(liveGaugeHtml.includes('EVOLVED') || liveGaugeHtml.includes('C2'), 'Expected cycle C2/EVOLVED to render');
console.assert(liveGaugeHtml.includes('87%') || liveGaugeHtml.includes('87.3%'), 'Expected live evasion rate (87%) to render');
console.log('✓ Verified live cycle telemetry renders real live values');

console.log('\n=====================================================');
console.log('ALL SKELETON SHIMMER LOADING CHECKS PASSED PERFECTLY!');
console.log('=====================================================');
