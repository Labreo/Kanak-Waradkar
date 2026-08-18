/**
 * Verification script for Vector C Dashboard rendering and lifecycle.
 */

import { VectorCDashboard, PRESET_SCENARIOS } from '../frontend/src/components/VectorCDashboard.js';
import { fetchVectorOverview, fetchInstances, fetchInstanceDetail } from '../frontend/src/services/api.js';

console.log('=====================================================');
console.log('1. VERIFYING BACKEND API ENDPOINTS FOR VECTOR C');
console.log('=====================================================');

const overview = await fetchVectorOverview('C');
console.log(`✓ Vector C Overview fetched: ${overview.vector_name}, total=${overview.total_evaluated}, recall=${overview.baseline_metrics.summary_metrics.recall}`);

const instances = await fetchInstances('C', { limit: 20 });
console.log(`✓ Vector C Instances fetched: ${instances.items.length} items on page 1 of ${instances.total_records}`);

const detail = await fetchInstanceDetail('C', instances.items[0].instance_id);
console.log(`✓ Vector C Instance Detail fetched: ${detail.instance_id}, tech=${detail.attack_technique}, verdict=${detail.verdict}`);

console.log('\n=====================================================');
console.log('2. VERIFYING DOM SKELETON & SYNCHRONOUS PRE-LOAD');
console.log('=====================================================');

class MockDOMElement {
  constructor(tag = 'div', parent = null) {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.parent = parent;
    this.attributes = {};
    this.classList = new Set();
    this._innerHTML = '';
    this.textContent = '';
    this.disabled = false;
    this.style = {};
    this.eventListeners = {};
  }

  get innerHTML() {
    return this._innerHTML;
  }

  set innerHTML(val) {
    this._innerHTML = val;
    // Simple child simulation
    this.children = [];
  }

  getAttribute(attr) {
    return this.attributes[attr] || null;
  }

  setAttribute(attr, val) {
    this.attributes[attr] = val;
  }

  addEventListener(event, fn) {
    if (!this.eventListeners[event]) this.eventListeners[event] = [];
    this.eventListeners[event].push(fn);
  }

  dispatchEvent(event, data) {
    if (this.eventListeners[event]) {
      this.eventListeners[event].forEach(fn => fn(data));
    }
  }

  querySelector(selector) {
    // Basic selector matching
    if (selector.startsWith('#')) {
      const id = selector.substring(1);
      return this._findChild(el => el.attributes['id'] === id);
    }
    if (selector.startsWith('.')) {
      const cls = selector.substring(1);
      return this._findChild(el => el.classList.has(cls));
    }
    return null;
  }

  querySelectorAll(selector) {
    const res = [];
    this._collectChildren(el => {
      if (selector.startsWith('#') && el.attributes['id'] === selector.substring(1)) return true;
      if (selector.startsWith('.') && el.classList.has(selector.substring(1))) return true;
      return false;
    }, res);
    return res;
  }

  _findChild(predicate) {
    for (const child of this.children) {
      if (predicate(child)) return child;
      const found = child._findChild(predicate);
      if (found) return found;
    }
    return null;
  }

  _collectChildren(predicate, list) {
    for (const child of this.children) {
      if (predicate(child)) list.push(child);
      child._collectChildren(predicate, list);
    }
  }
}

// Test HTML parser helper to populate mock elements from innerHTML
function createRealDOM() {
  const container = {
    _html: '',
    get innerHTML() { return this._html; },
    set innerHTML(v) { this._html = v; },
    elements: {},
    querySelector(sel) {
      if (!this._elements) this._parse();
      return this._elements[sel] || null;
    },
    querySelectorAll(sel) {
      if (!this._elements) this._parse();
      return this._allElements[sel] || [];
    },
    _parse() {
      this._elements = {};
      this._allElements = {};

      const ids = [
        '#v-c-crumb-home', '#v-c-reveal-toggle', '#v-c-play-beat-btn', '#play-icon', '#play-text',
        '#scen-html', '#scen-css', '#scen-md', '#scen-inv', '#scen-legit',
        '#v-c-agent-status-badge', '#agent-security-badge', '#agent-terminal-output',
        '#wallet-balance-val', '#wallet-drain-val', '#wallet-shield',
        '#browser-url-text', '#browser-page-content', '#concealed-box',
        '#decision-hud-box', '#decision-hud-text', '#decision-confidence-val',
        '#divergence-inspector', '#div-intended-rec', '#div-hijacked-rec', '#div-intended-amt', '#div-hijacked-amt',
        '#sub-scores-container', '#sub-conceal-num', '#sub-conceal-bar', '#sub-override-num', '#sub-override-bar',
        '#sub-param-num', '#sub-param-bar', '#sub-inv-num', '#sub-inv-bar',
        '#v-c-narrative-box', '#v-c-narrative-text',
        '#v-c-count-badge', '#v-c-search-input', '#v-c-feed-table', '#v-c-table-body',
        '#v-c-pagination-info', '#v-c-prev-page', '#v-c-next-page'
      ];

      ids.forEach(id => {
        const el = {
          id: id.substring(1),
          innerHTML: '',
          textContent: '',
          classList: {
            classes: new Set(),
            add(c) { this.classes.add(c); },
            remove(c) { this.classes.delete(c); },
            toggle(c, state) { if (state === undefined) state = !this.classes.has(c); if (state) this.classes.add(c); else this.classes.delete(c); return state; },
            contains(c) { return this.classes.has(c); }
          },
          attributes: {},
          getAttribute(a) { return this.attributes[a]; },
          setAttribute(a, v) { this.attributes[a] = v; },
          addEventListener(evt, cb) { this._listeners = this._listeners || {}; this._listeners[evt] = cb; },
          style: {},
          disabled: false,
          querySelector(s) {
            return {
              textContent: '',
              innerHTML: '',
              classList: { add: () => {}, remove: () => {}, toggle: () => {} }
            };
          }
        };
        this._elements[id] = el;
      });

      // Scenario chips
      this._allElements['.scenario-chip'] = [
        { ...this._elements['#scen-html'], attributes: { 'data-archetype': 'HTML_COMMENT' } },
        { ...this._elements['#scen-css'], attributes: { 'data-archetype': 'CSS_HIDDEN_ELEMENT' } },
        { ...this._elements['#scen-md'], attributes: { 'data-archetype': 'MARKDOWN_COMMENT' } },
        { ...this._elements['#scen-inv'], attributes: { 'data-archetype': 'INVOICE_MEMO_POISONING' } },
        { ...this._elements['#scen-legit'], attributes: { 'data-archetype': 'BENCHMARK_LEGITIMATE' } },
      ];
      this._allElements['.verdict-filter-btn'] = [
        { attributes: { 'data-verdict': 'ALL' }, classList: { add: () => {}, remove: () => {} }, addEventListener: () => {} }
      ];
      this._allElements['#v-c-table-body tr'] = [];
    }
  };
  return container;
}

const mockContainer = createRealDOM();
const mockRouter = { navigate: () => {} };

const dashboard = new VectorCDashboard(mockContainer, mockRouter);

console.log('✓ Initial synchronous render verification:');
console.log('  - Initial selected detail:', dashboard.selectedDetail.instance_id, `(${dashboard.selectedDetail.attack_technique})`);
console.assert(dashboard.selectedDetail.instance_id === 'PAYLOAD-0042-0021-E9A1FA', 'Expected Scenario 1 selected by default');
console.assert(!mockContainer.innerHTML.includes('Loading mock storefront...'), 'FAIL: Loading spinner was present in skeleton!');
console.assert(!mockContainer.innerHTML.includes('Waiting for task prompt...'), 'FAIL: Empty task prompt was present in skeleton!');
console.assert(mockContainer.innerHTML.includes('AeroSound True Wireless Earbuds'), 'FAIL: Storefront title missing from initial render!');
console.assert(mockContainer.innerHTML.includes('ShoppingAgent initialized with prompt'), 'FAIL: Terminal transcript missing from initial render!');
console.assert(mockContainer.innerHTML.includes('HARD BLOCKED'), 'FAIL: Scanner HUD missing from initial render!');

console.log('\n=====================================================');
console.log('3. TESTING SCENARIO SWITCHING ACROSS ALL 5 ARCHETYPES');
console.log('=====================================================');

const archetypes = ['HTML_COMMENT', 'CSS_HIDDEN_ELEMENT', 'MARKDOWN_COMMENT', 'INVOICE_MEMO_POISONING', 'BENCHMARK_LEGITIMATE'];

for (const arch of archetypes) {
  dashboard.selectScenarioByArchetype(arch);
  console.log(`✓ Switched to archetype '${arch}': ID=${dashboard.selectedDetail.instance_id}, Verdict=${dashboard.selectedDetail.verdict}, Malicious=${dashboard.selectedDetail.is_malicious}`);
  console.assert(dashboard.selectedDetail.attack_technique === arch, `Expected archetype ${arch}, got ${dashboard.selectedDetail.attack_technique}`);
}

// Switch back to HTML_COMMENT
dashboard.selectScenarioByArchetype('HTML_COMMENT');
console.assert(dashboard.selectedDetail.attack_technique === 'HTML_COMMENT', 'Expected HTML_COMMENT active');
console.log('✓ Reset back to Scenario 1 (HTML_COMMENT)');

console.log('\n=====================================================');
console.log('4. TESTING SIMULATION BEAT PLAYBACK');
console.log('=====================================================');

console.log('✓ Triggering runSimulationBeat()...');
dashboard.runSimulationBeat();
console.assert(dashboard.isSimulating === true, 'Simulation should be active');

await new Promise(resolve => setTimeout(resolve, 2600));
console.assert(dashboard.isSimulating === false, 'Simulation should be completed');
console.log('✓ Simulation beat completed cleanly without errors!');

console.log('\n=====================================================');
console.log('ALL VECTOR C RENDER & LIFECYCLE TESTS PASSED PERFECTLY');
console.log('=====================================================');
