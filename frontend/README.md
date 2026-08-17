# TRIAD Frontend Dashboard (Vite SPA)

Modern Single-Page Application (SPA) dashboard for Project TRIAD, built with Vanilla JavaScript, modular component architecture, and high-contrast HSL dark tokens.

## Design Aesthetics & Color Palette

- **Base Background:** Deep ink / midnight `#12142B`
- **Surface Elevation:** Translucent glassmorphism `#1A1D3B` with `backdrop-filter: blur(16px)`
- **Amber Warning Accent:** `#F2A93B` (flagged items, suspicious transactions, fraud alerts)
- **Cyan Adaptive Accent:** `#5FD8D0` (closed-loop tightening ring, learning telemetry)
- **Typography:** Inter & JetBrains Mono for telemetry readouts

## Key Components & Architecture

- **`Navigation.js`**: View routing between Landing, Closed Loop Dashboard, and Vector Dashboards (A, B, C).
- **`ClosingLoopGauge.js`**: Signature SVG closing ring visualization that animates inward across adversarial cycles.
- **`ClosedLoopDashboard.js`**: Interactive control center for triggering live simulation waves and inspecting cycle telemetry.
- **`VectorADashboard.js` / `VectorBDashboard.js` / `VectorCDashboard.js`**: Deep dive consoles with live scoring testers, instance inspectors, and confusion matrices.

## Development & Build

```bash
# Install dependencies
npm install

# Run local development server
npm run dev

# Build production bundle to dist/ (served by backend)
npm run build
```
