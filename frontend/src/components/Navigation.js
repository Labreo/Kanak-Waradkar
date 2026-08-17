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
    this.currentView = 'overview';
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
    // Listen to hash changes in browser URL
    window.addEventListener('hashchange', () => {
      const hash = window.location.hash.replace('#', '').trim();
      if (this.routes[hash]) {
        this.navigate(hash, false);
      }
    });

    // Listen to navigation tab button clicks
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const viewId = tab.getAttribute('data-view');
        this.navigate(viewId);
      });
    });

    // Keyboard shortcuts (1-5 for views)
    window.addEventListener('keydown', (e) => {
      // Don't trigger if user is typing in an input/textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
        return;
      }

      if (e.key === '1') this.navigate('overview');
      else if (e.key === '2') this.navigate('vector-a');
      else if (e.key === '3') this.navigate('vector-b');
      else if (e.key === '4') this.navigate('vector-c');
      else if (e.key === '5') this.navigate('loop');
    });

    // Initial load from URL hash or default to overview
    const initialHash = window.location.hash.replace('#', '').trim();
    if (this.routes[initialHash]) {
      this.navigate(initialHash, false);
    } else {
      this.navigate('overview', true);
    }
  }

  navigate(viewId, updateHash = true) {
    if (!this.routes[viewId]) {
      viewId = 'overview';
    }

    this.currentView = viewId;

    if (updateHash) {
      window.location.hash = viewId;
    }

    // Update active tab styling in header
    document.querySelectorAll('.nav-tab').forEach(tab => {
      const tabView = tab.getAttribute('data-view');
      const isActive = tabView === viewId;
      tab.classList.toggle('active', isActive);
      tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });

    // Clear and render new view
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
