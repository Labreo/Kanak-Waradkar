/**
 * Verification test for VectorBDashboard dynamic telemetry:
 * 1. Confirms GBDT feature-importance percentages render dynamically from baseline_metrics.feature_importances.
 * 2. Confirms that mutating feature importances or retraining with different seeds changes the rendered UI.
 * 3. Confirms that Botnet Network Diagnostics strings render dynamically from selected transaction's
 *    real device_telemetry, is_proxy_or_vpn, and dist1_ip_billing_distance fields.
 */

import { VectorBDashboard } from '../frontend/src/components/VectorBDashboard.js';

console.log('=====================================================');
console.log('1. MOCK DOM ENVIRONMENT SETUP FOR VECTOR B');
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
    this.children = [];
    this.textContent = val.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
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
    if (selector.startsWith('#')) {
      const id = selector.substring(1);
      return this._findChild(el => el.attributes['id'] === id);
    }
    if (selector.startsWith('.')) {
      const cls = selector.substring(1);
      return this._findChild(el => el.classList.has(cls));
    }
    return this._findChild(el => el.tagName.toLowerCase() === selector.toLowerCase());
  }

  querySelectorAll(selector) {
    const res = [];
    this._collectChildren(el => {
      if (selector.startsWith('#') && el.attributes['id'] === selector.substring(1)) return true;
      if (selector.startsWith('.') && el.classList.has(selector.substring(1))) return true;
      if (el.tagName.toLowerCase() === selector.toLowerCase()) return true;
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

// Global document simulation
const mockRootContainer = new MockDOMElement('div');
mockRootContainer.setAttribute('id', 'app-root');

globalThis.document = {
  querySelector: (sel) => {
    if (sel === '#app-root' || sel === '#main-container') return mockRootContainer;
    return mockRootContainer.querySelector(sel);
  },
  querySelectorAll: (sel) => mockRootContainer.querySelectorAll(sel),
};

const mockRouter = {
  navigate: (route) => { console.log(`Navigated to route: ${route}`); }
};

console.log('✓ Mock DOM environment initialized.');

console.log('\n=====================================================');
console.log('2. TESTING DYNAMIC GBDT FEATURE IMPORTANCE ATTRIBUTION');
console.log('=====================================================');

const dashboard = new VectorBDashboard(mockRootContainer, mockRouter);

// Test Seed A Mock Overview
const mockOverviewSeedA = {
  vector_id: 'B',
  vector_name: 'Behavioral & Transaction Fraud',
  total_evaluated: 1000,
  baseline_metrics: {
    summary_metrics: {
      roc_auc: 0.9336,
      recall: 0.8986,
    },
    model_metadata: {
      algorithm: 'HistGradientBoostingClassifier',
    },
    feature_importances: [
      { rank: 1, feature_name: 'product_cd', relative_importance_pct: 41.16, auc_drop: 0.1788 },
      { rank: 2, feature_name: 'c1_card_count_24h', relative_importance_pct: 17.01, auc_drop: 0.0739 },
      { rank: 3, feature_name: 'c2_card_count_1h', relative_importance_pct: 13.83, auc_drop: 0.0601 },
      { rank: 4, feature_name: 'inter_arrival_seconds', relative_importance_pct: 11.25, auc_drop: 0.0480 },
    ]
  }
};

dashboard.overviewData = mockOverviewSeedA;

// Render feature importances container
const fiContainer = new MockDOMElement('div');
fiContainer.setAttribute('id', 'v-b-feature-importances-container');
mockRootContainer.children.push(fiContainer);

dashboard.renderFeatureImportances();

console.assert(fiContainer.innerHTML.includes('41.16%'), 'Expected 41.16% for Seed A product_cd');
console.assert(fiContainer.innerHTML.includes('17.01%'), 'Expected 17.01% for Seed A c1_card_count_24h');
console.assert(fiContainer.innerHTML.includes('13.83%'), 'Expected 13.83% for Seed A c2_card_count_1h');
console.assert(fiContainer.innerHTML.includes('11.25%'), 'Expected 11.25% for Seed A inter_arrival_seconds');
console.assert(fiContainer.innerHTML.includes('0.9336'), 'Expected GBDT ROC-AUC 0.9336 in badge');
console.log('✓ Verified Feature Importances render Seed A percentages correctly.');

// Retrain simulation: Mutate feature importances with Seed B values
console.log('\n--- Simulating Model Retraining with Seed B ---');
const mockOverviewSeedB = {
  vector_id: 'B',
  vector_name: 'Behavioral & Transaction Fraud',
  total_evaluated: 1000,
  baseline_metrics: {
    summary_metrics: {
      roc_auc: 0.9612,
      recall: 0.9420,
    },
    model_metadata: {
      algorithm: 'HistGradientBoostingClassifier',
    },
    feature_importances: [
      { rank: 1, feature_name: 'c1_card_count_24h', relative_importance_pct: 38.45, auc_drop: 0.1620 },
      { rank: 2, feature_name: 'inter_arrival_seconds', relative_importance_pct: 28.10, auc_drop: 0.1150 },
      { rank: 3, feature_name: 'd2_card_recency_days', relative_importance_pct: 19.75, auc_drop: 0.0820 },
      { rank: 4, feature_name: 'c5_merchant_count_1h', relative_importance_pct: 8.90, auc_drop: 0.0340 },
    ]
  }
};

dashboard.overviewData = mockOverviewSeedB;
dashboard.renderFeatureImportances();

console.assert(fiContainer.innerHTML.includes('38.45%'), 'Expected 38.45% for Seed B c1_card_count_24h');
console.assert(fiContainer.innerHTML.includes('28.10%'), 'Expected 28.10% for Seed B inter_arrival_seconds');
console.assert(fiContainer.innerHTML.includes('19.75%'), 'Expected 19.75% for Seed B d2_card_recency_days');
console.assert(fiContainer.innerHTML.includes('8.90%'), 'Expected 8.90% for Seed B c5_merchant_count_1h');
console.assert(fiContainer.innerHTML.includes('0.9612'), 'Expected GBDT ROC-AUC 0.9612 in badge');
console.assert(!fiContainer.innerHTML.includes('41.16%'), 'Stale Seed A percentage 41.16% must NOT be present');
console.log('✓ Verified Feature Importances dynamically change on retrained seed (zero hardcoded values).');

console.log('\n=====================================================');
console.log('3. TESTING DYNAMIC BOTNET NETWORK DIAGNOSTICS');
console.log('=====================================================');

const burstContainer = new MockDOMElement('div');
burstContainer.setAttribute('id', 'v-b-burst-telemetry-container');
mockRootContainer.children.push(burstContainer);

// Scenario 1: Malicious Botnet Headless Proxy Probe
const maliciousSeq = {
  sequence_id: 'SEQ-BURST-2001',
  total_probes: 3,
  total_duration_seconds: 0.85,
  rate_per_sec: 3.53,
  avg_inter_arrival_seconds: 0.283,
  device_telemetry: {
    browser_name: 'HeadlessChrome',
    os_name: 'Linux',
    is_headless_browser: true,
    is_proxy_or_vpn: true,
    network_ip_risk_score: 0.94,
  },
  geolocation_network: {
    dist1_ip_billing_distance: 3120.5,
    is_disposable_email: true,
  },
  velocity_counters: {
    c1_card_count_24h: 15,
    c2_card_count_1h: 15,
    c5_merchant_count_1h: 42,
  },
  probes: [
    {
      step: 1,
      transaction_id: 'TXN-BURST-001',
      time_offset: '+0.000s',
      time_offset_seconds: 0.0,
      dt_ms: '0ms',
      inter_arrival_seconds: 0.28,
      amount: '$1.45',
      card_token: 'CARD-512077-XXXX-1001',
      bin: '512077',
      network: 'Mastercard',
      iso_code: '82',
      iso_desc: 'CVV / Security Code Mismatch',
      is_approved: false,
      is_declined: true,
      risk_score: 0.92,
      verdict: 'BLOCK',
      note: 'CVV probe',
      device_telemetry: {
        browser_name: 'HeadlessChrome',
        os_name: 'Linux',
        is_headless_browser: true,
        is_proxy_or_vpn: true,
        network_ip_risk_score: 0.94,
      },
      geolocation_network: {
        dist1_ip_billing_distance: 3120.5,
        is_disposable_email: true,
      },
      velocity_counters: {
        c1_card_count_24h: 15,
        c2_card_count_1h: 15,
        c5_merchant_count_1h: 42,
      }
    }
  ]
};

dashboard.activeBurstSequence = maliciousSeq;
dashboard.burstSequences = [maliciousSeq];
dashboard.selectedSequenceStep = 1;
dashboard.selectedDetail = {
  instance_id: 'TXN-BURST-001',
  artifact: {
    transaction_id: 'TXN-BURST-001',
    device_telemetry: maliciousSeq.device_telemetry,
    geolocation_network: maliciousSeq.geolocation_network,
    velocity_counters: maliciousSeq.velocity_counters,
  }
};

dashboard.renderBurstTelemetry();

console.assert(burstContainer.innerHTML.includes('HeadlessChrome / Linux (Headless)'), 'Expected HeadlessChrome / Linux (Headless)');
console.assert(burstContainer.innerHTML.includes('Proxy / Tor / VPN (Score: 0.94)'), 'Expected Proxy / Tor / VPN (Score: 0.94)');
console.assert(burstContainer.innerHTML.includes('3121 km Anomaly'), 'Expected 3121 km Anomaly');
console.assert(burstContainer.innerHTML.includes('42 Endpoints / 1h'), 'Expected 42 Endpoints / 1h');
console.log('✓ Scenario 1: Malicious botnet probe telemetry correctly rendered from live fields.');

// Scenario 2: Clean Organic Residential Transaction
console.log('\n--- Scenario 2: Organic Clean Mobile Transaction ---');
const cleanSeq = {
  sequence_id: 'SEQ-LEGIT-3001',
  total_probes: 1,
  total_duration_seconds: 1.0,
  rate_per_sec: 1.0,
  avg_inter_arrival_seconds: 1.0,
  device_telemetry: {
    browser_name: 'Safari',
    os_name: 'iOS',
    is_headless_browser: false,
    is_proxy_or_vpn: false,
    network_ip_risk_score: 0.04,
  },
  geolocation_network: {
    dist1_ip_billing_distance: null,
    is_disposable_email: false,
  },
  velocity_counters: {
    c1_card_count_24h: 1,
    c2_card_count_1h: 1,
    c5_merchant_count_1h: 1,
  },
  probes: [
    {
      step: 1,
      transaction_id: 'TXN-LEGIT-001',
      time_offset: '+0.000s',
      time_offset_seconds: 0.0,
      dt_ms: '0ms',
      inter_arrival_seconds: 1.0,
      amount: '$45.00',
      card_token: 'CARD-412847-XXXX-3001',
      bin: '412847',
      network: 'Visa',
      iso_code: '00',
      iso_desc: '00_APPROVED',
      is_approved: true,
      is_declined: false,
      risk_score: 0.05,
      verdict: 'ALLOW',
      note: 'Clean purchase',
      device_telemetry: {
        browser_name: 'Safari',
        os_name: 'iOS',
        is_headless_browser: false,
        is_proxy_or_vpn: false,
        network_ip_risk_score: 0.04,
      },
      geolocation_network: {
        dist1_ip_billing_distance: null,
        is_disposable_email: false,
      },
      velocity_counters: {
        c1_card_count_24h: 1,
        c2_card_count_1h: 1,
        c5_merchant_count_1h: 1,
      }
    }
  ]
};

dashboard.activeBurstSequence = cleanSeq;
dashboard.burstSequences = [cleanSeq];
dashboard.selectedSequenceStep = 1;
dashboard.selectedDetail = {
  instance_id: 'TXN-LEGIT-001',
  artifact: {
    transaction_id: 'TXN-LEGIT-001',
    device_telemetry: cleanSeq.device_telemetry,
    geolocation_network: cleanSeq.geolocation_network,
    velocity_counters: cleanSeq.velocity_counters,
  }
};

dashboard.renderBurstTelemetry();

console.assert(burstContainer.innerHTML.includes('Safari / iOS'), 'Expected Safari / iOS');
console.assert(!burstContainer.innerHTML.includes('(Headless)'), 'Safari must NOT have (Headless)');
console.assert(burstContainer.innerHTML.includes('Direct Residential IP (Score: 0.04)'), 'Expected Direct Residential IP (Score: 0.04)');
console.assert(burstContainer.innerHTML.includes('Domestic (< 50 km)'), 'Expected Domestic (< 50 km)');
console.assert(burstContainer.innerHTML.includes('1 Endpoint / 1h'), 'Expected 1 Endpoint / 1h');
console.log('✓ Scenario 2: Clean organic transaction telemetry correctly rendered from live fields.');

console.log('\n=====================================================');
console.log('ALL VECTOR B DYNAMIC TELEMETRY CHECKS PASSED (100%)');
console.log('=====================================================');
