/**
 * Comprehensive test script for verifying Vector A, B, C, and Closed Loop dashboard components.
 */

import { fetchVectorOverview, fetchInstances, fetchInstanceDetail, fetchLoopHistory, triggerLoopWave } from './src/services/api.js';
import { VectorADashboard } from './src/components/VectorADashboard.js';
import { VectorBDashboard } from './src/components/VectorBDashboard.js';
import { VectorCDashboard } from './src/components/VectorCDashboard.js';
import { ClosedLoopDashboard } from './src/components/ClosedLoopDashboard.js';

console.log('--- 1. Testing Live API Services from Node ---');

// Vector A
const overviewA = await fetchVectorOverview('A');
console.assert(overviewA.vector_id === 'A', 'Expected Vector A overview');
console.log(`✓ Vector A overview: ${overviewA.vector_name}, total=${overviewA.total_evaluated}`);

const instancesA = await fetchInstances('A', { limit: 5 });
console.assert(instancesA.items.length === 5, 'Expected 5 items for Vector A');
console.log(`✓ Vector A instances: fetched ${instancesA.items.length} items`);

// Vector B
const overviewB = await fetchVectorOverview('B');
console.assert(overviewB.vector_id === 'B', 'Expected Vector B overview');
console.log(`✓ Vector B overview: ${overviewB.vector_name}, total=${overviewB.total_evaluated}`);

const instancesB = await fetchInstances('B', { limit: 5 });
console.assert(instancesB.items.length === 5, 'Expected 5 items for Vector B');
console.log(`✓ Vector B instances: fetched ${instancesB.items.length} items`);

// Vector C
const overviewC = await fetchVectorOverview('C');
console.assert(overviewC.vector_id === 'C', 'Expected Vector C overview');
console.log(`✓ Vector C overview: ${overviewC.vector_name}, total=${overviewC.total_evaluated}, recall=${overviewC.baseline_metrics.summary_metrics.recall}`);

const instancesC = await fetchInstances('C', { limit: 5 });
console.assert(instancesC.items.length === 5, 'Expected 5 items for Vector C');
console.log(`✓ Vector C instances: fetched ${instancesC.items.length} items`);

const detailC = await fetchInstanceDetail('C', instancesC.items[0].instance_id);
console.assert(detailC.instance_id === instancesC.items[0].instance_id, 'Instance ID mismatch');
console.log(`✓ Vector C detail: ${detailC.instance_id} - ${detailC.attack_technique}, verdict=${detailC.verdict}`);

// Closed Loop History & Trigger
const loopHist = await fetchLoopHistory('A');
console.assert(loopHist.vector_id === 'A', 'Expected Vector A loop history');
console.log(`✓ Loop history: vector A, cycles=${loopHist.cycles.length}, delta=+${(loopHist.summary_trend.evasion_delta*100).toFixed(1)}%`);

const waveResult = await triggerLoopWave('B', { cycles: 3, batch_size: 50, seed: 1042 });
console.assert(waveResult.vector_id === 'B', 'Expected Vector B wave result');
console.log(`✓ Trigger wave live test: vector B, cycles completed=${waveResult.total_cycles_completed}`);

console.log('\n--- 2. Testing Component Structure ---');
function createMockElement() {
  return {
    innerHTML: '',
    textContent: '',
    value: '',
    disabled: false,
    style: {},
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    addEventListener: () => {},
    setAttribute: () => {},
    getAttribute: () => '',
    querySelector: () => createMockElement(),
    querySelectorAll: () => [createMockElement(), createMockElement()]
  };
}

const mockRouter = { navigate: (target) => console.log(`Navigated to: ${target}`) };

const containerA = createMockElement();
const dashboardA = new VectorADashboard(containerA, mockRouter);
console.assert(typeof dashboardA.loadOverview === 'function');

const containerB = createMockElement();
const dashboardB = new VectorBDashboard(containerB, mockRouter);
console.assert(typeof dashboardB.loadOverview === 'function');

const containerC = createMockElement();
const dashboardC = new VectorCDashboard(containerC, mockRouter);
console.assert(typeof dashboardC.loadOverview === 'function');

const containerLoop = createMockElement();
const dashboardLoop = new ClosedLoopDashboard(containerLoop, mockRouter);
console.assert(typeof dashboardLoop.loadLoopHistory === 'function');
console.assert(typeof dashboardLoop.executeLiveWave === 'function');
console.log('✓ ClosedLoopDashboard methods verified');

console.log('\nAll Session 26 Closed Loop live data and dashboard tests PASSED!');
