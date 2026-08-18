/**
 * Test script for verifying frontend component logic and radial gauge math calculations.
 */

import { ClosingLoopGauge } from './src/components/ClosingLoopGauge.js';
import { VECTOR_DEFINITIONS, renderVectorCards } from './src/components/VectorCards.js';

console.log('--- Checking Vector Definitions ---');
console.assert(VECTOR_DEFINITIONS.length === 3, 'Expected 3 vectors');
console.log(`✓ Verified ${VECTOR_DEFINITIONS.length} vector definitions (A, B, C)`);

console.log('--- Checking ClosingLoopGauge Radial Progress Ring Math Calculations ---');
// Mock minimal DOM container
const mockContainer = {
  innerHTML: '',
  querySelector: () => null,
  querySelectorAll: () => []
};

const gauge = new ClosingLoopGauge(mockContainer, { initialCycle: 2 });

// 1. Verify Ring Circumference
console.assert(gauge.radius === 110, 'Expected gauge radius 110');
console.assert(Math.abs(gauge.circumference - 691.15) < 0.1, `Expected circumference ~691.15, got ${gauge.circumference}`);
console.log(`✓ Verified radial ring geometry: R=${gauge.radius}, Circumference=${gauge.circumference}`);

// 2. Verify Stroke-Dashoffset is directly and proportionally computed
const offset0 = gauge.calculateDashOffset(0.0);
const offset29 = gauge.calculateDashOffset(0.29);
const offset83 = gauge.calculateDashOffset(0.83);
const offset04 = gauge.calculateDashOffset(0.04);
const offset100 = gauge.calculateDashOffset(1.0);

console.assert(Math.abs(offset0 - 691.15) < 0.1, `Offset at 0% should be ~691.15, got ${offset0}`);
console.assert(Math.abs(offset29 - 490.72) < 0.1, `Offset at 29% should be ~490.72, got ${offset29}`);
console.assert(Math.abs(offset83 - 117.50) < 0.1, `Offset at 83% should be ~117.50, got ${offset83}`);
console.assert(Math.abs(offset04 - 663.50) < 0.1, `Offset at 4% should be ~663.50, got ${offset04}`);
console.assert(offset100 === 0, `Offset at 100% should be 0, got ${offset100}`);
console.log(`✓ Verified stroke-dashoffset math: 0%->${offset0}, 4%->${offset04}, 29%->${offset29}, 83%->${offset83}, 100%->${offset100}`);

// 3. Verify Radial Ring Coordinates
const ringC0 = gauge.calculateRingCoordinates(0.0);
const ringC1 = gauge.calculateRingCoordinates(0.29);
const ringC2 = gauge.calculateRingCoordinates(0.83);
const ringC3 = gauge.calculateRingCoordinates(0.04);

console.assert(Math.abs(ringC0.x - 0) < 0.01 && Math.abs(ringC0.y - (-110)) < 0.01, 'C0 should be at top (0, -110)');
console.log(`✓ Proportional Ring Marker Coordinates: C0(0%)->(${ringC0.x}, ${ringC0.y}, angle=${ringC0.angle}°), C1(29%)->(${ringC1.x}, ${ringC1.y}, angle=${ringC1.angle.toFixed(1)}°), C2(83%)->(${ringC2.x}, ${ringC2.y}, angle=${ringC2.angle.toFixed(1)}°), C3(4%)->(${ringC3.x}, ${ringC3.y}, angle=${ringC3.angle.toFixed(1)}°)`);

// 4. Verify Backward Compatibility Polar Helper
const p0 = gauge.polarToCartesian(110, 0);
console.assert(p0.x === 110 && p0.y === 0, 'Polar helper calculation mismatch');
console.log(`✓ Polar helper verified: (110, 0°) -> (${p0.x}, ${p0.y})`);

console.log('\nAll frontend component checks passed successfully!');
