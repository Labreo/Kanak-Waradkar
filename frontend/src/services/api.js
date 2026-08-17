/**
 * PROJECT TRIAD — FRONTEND API CLIENT
 * 
 * Interacts with the stateless FastAPI backend endpoints:
 * - GET /api/health
 * - GET /api/vectors
 * - GET /api/vectors/{id}/overview
 * - GET /api/metrics?vector={A|B|C}
 * - GET /api/instances?vector={A|B|C}&limit=...&offset=...&verdict=...&search=...
 * - GET /api/instances/{vector_id}/{instance_id}
 * - GET /api/loop/history?vector={A|B|C}
 */

function getApiBase() {
  if (typeof window !== 'undefined' && window.location) {
    return '/api';
  }
  // Node.js test environment fallback
  return (typeof process !== 'undefined' && process.env && process.env.API_BASE_URL) || 'http://127.0.0.1:8000/api';
}

export async function fetchHealth() {
  const base = getApiBase();
  const res = await fetch(`${base}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return await res.json();
}

export async function fetchVectors() {
  const base = getApiBase();
  const res = await fetch(`${base}/vectors`);
  if (!res.ok) throw new Error(`Fetch vectors failed: ${res.status}`);
  return await res.json();
}

export async function fetchVectorOverview(vectorId) {
  const base = getApiBase();
  const res = await fetch(`${base}/vectors/${vectorId}/overview`);
  if (!res.ok) throw new Error(`Fetch vector ${vectorId} overview failed: ${res.status}`);
  return await res.json();
}

export async function fetchVectorMetrics(vectorId) {
  const base = getApiBase();
  const res = await fetch(`${base}/metrics?vector=${vectorId}`);
  if (!res.ok) throw new Error(`Fetch vector ${vectorId} metrics failed: ${res.status}`);
  return await res.json();
}

export async function fetchInstances(vectorId, options = {}) {
  const base = getApiBase();
  const { limit = 50, offset = 0, verdict = null, search = null, cycle = null } = options;
  const params = new URLSearchParams({
    vector: vectorId,
    limit: limit.toString(),
    offset: offset.toString()
  });

  if (verdict && verdict !== 'ALL') {
    params.append('verdict', verdict);
  }
  if (search && search.trim()) {
    params.append('search', search.trim());
  }
  if (cycle !== null && cycle !== undefined) {
    params.append('cycle', cycle.toString());
  }

  const res = await fetch(`${base}/instances?${params.toString()}`);
  if (!res.ok) throw new Error(`Fetch instances for vector ${vectorId} failed: ${res.status}`);
  return await res.json();
}

export async function fetchInstanceDetail(vectorId, instanceId, cycle = null) {
  const base = getApiBase();
  const params = cycle !== null && cycle !== undefined ? `?cycle=${cycle}` : '';
  const res = await fetch(`${base}/instances/${vectorId}/${instanceId}${params}`);
  if (!res.ok) throw new Error(`Fetch instance detail ${vectorId}/${instanceId} failed: ${res.status}`);
  return await res.json();
}

export async function fetchLoopHistory(vectorId = null) {
  const base = getApiBase();
  const params = vectorId ? `?vector=${vectorId}` : '';
  const res = await fetch(`${base}/loop/history${params}`);
  if (!res.ok) throw new Error(`Fetch loop history failed: ${res.status}`);
  return await res.json();
}

export async function fetchLoopCycleDetail(vectorId, cycleIndex) {
  const base = getApiBase();
  const res = await fetch(`${base}/loop/cycle/${vectorId}/${cycleIndex}`);
  if (!res.ok) throw new Error(`Fetch loop cycle detail ${vectorId}/${cycleIndex} failed: ${res.status}`);
  return await res.json();
}

export async function triggerLoopWave(vectorId, options = {}) {
  const base = getApiBase();
  const { cycles = 3, batch_size = 100, seed = 42 } = options;
  const res = await fetch(`${base}/loop/trigger`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      vector: vectorId,
      cycles: Number(cycles),
      batch_size: Number(batch_size),
      seed: Number(seed),
    }),
  });

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Trigger loop wave failed: ${res.status}`);
  }
  return await res.json();
}
