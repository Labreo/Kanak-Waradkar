/**
 * PROJECT TRIAD — CLIENT-SIDE NAVIGATION & ROUTER
 * 
 * Handles tab switching, URL hash synchronization, and keyboard shortcuts.
 */

import {
  renderOverviewView,
  renderVectorAShell,
  renderVectorBShell,
  renderVectorCShell,
  renderLoopShell
} from './Views.js';

export class Router {
  constructor(viewRootElement) {
    this.viewRoot = viewRootElement;
    this.currentView = null;
    this.routes = {
      'overview': renderOverviewView,
      'vector-a': renderVectorAShell,
      'vector-b': renderVectorBShell,
      'vector-c': renderVectorCShell,
      'loop': renderLoopShell
    };

    this.init();
  }

  init() {
    // Single source of truth: listen to hash changes in browser URL
    window.addEventListener('hashchange', () => {
      const hash = window.location.hash.replace('#', '').trim();
      const target = this.routes[hash] ? hash : 'overview';
      this.navigate(target, false);
    });

    // Listen to navigation tab button clicks
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const viewId = tab.getAttribute('data-view');
        this.navigate(viewId, true);
      });
    });

    // Keyboard shortcuts (1-5 for views)
    window.addEventListener('keydown', (e) => {
      // Don't trigger if user is typing in an input/textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
        return;
      }

      if (e.key === '1') this.navigate('overview', true);
      else if (e.key === '2') this.navigate('vector-a', true);
      else if (e.key === '3') this.navigate('vector-b', true);
      else if (e.key === '4') this.navigate('vector-c', true);
      else if (e.key === '5') this.navigate('loop', true);
    });

    // Initial load from URL hash or default to overview
    const initialHash = window.location.hash.replace('#', '').trim();
    const initialTarget = this.routes[initialHash] ? initialHash : 'overview';
    this.navigate(initialTarget, false);
  }

  navigate(viewId, updateHash = true) {
    if (!this.routes[viewId]) {
      viewId = 'overview';
    }

    // Prevent redundant execution if view is already rendered and target matches
    if (this.currentView === viewId && this.viewRoot.hasChildNodes() && !updateHash) {
      return;
    }

    if (updateHash && window.location.hash !== `#${viewId}`) {
      window.location.hash = viewId;
      // hashchange event listener will trigger navigate(viewId, false) cleanly
      return;
    }

    this.currentView = viewId;

    // Update active tab styling in header
    document.querySelectorAll('.nav-tab').forEach(tab => {
      const tabView = tab.getAttribute('data-view');
      const isActive = tabView === viewId;
      tab.classList.toggle('active', isActive);
      tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    // Synchronize global header cycle status based on active view context
    if (typeof document !== 'undefined') {
      const headerCycle = document.querySelector('#header-cycle-val');
      if (headerCycle) {
        if (viewId === 'vector-a') headerCycle.textContent = 'C2 // MUTATED (VECT A)';
        else if (viewId === 'vector-b') headerCycle.textContent = 'C2 // ORGANIC (VECT B)';
        else if (viewId === 'vector-c') headerCycle.textContent = 'C2 // PRETEXT (VECT C)';
        else if (viewId === 'loop') headerCycle.textContent = 'C2 // ADAPTED';
        else if (viewId === 'overview') headerCycle.textContent = 'C2 // ADAPTED';
      }
    }

    // Clear and render new view exactly once
    this.viewRoot.innerHTML = '';
    const renderFn = this.routes[viewId];
    if (renderFn) {
      const viewElement = renderFn(this);
      this.viewRoot.appendChild(viewElement);
    }

    // Smooth scroll to top of stage
    window.scrollTo({ top: 0, behavior: 'instant' });
  }
}
