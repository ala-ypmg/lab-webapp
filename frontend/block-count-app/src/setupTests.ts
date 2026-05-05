/**
 * Test Setup Configuration
 */

import '@testing-library/jest-dom';
import { vi, beforeEach } from 'vitest';

// Mock window.matchMedia for MUI components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock scrollIntoView
Element.prototype.scrollIntoView = vi.fn();

// Mock ResizeObserver
(globalThis as unknown as { ResizeObserver: unknown }).ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock global fetch to handle relative URLs that jsdom cannot resolve.
// In the jsdom test environment there is no real origin, so fetch('/path')
// throws "TypeError: Failed to parse URL from /path". Providing a mock
// avoids this and lets save-related tests verify UI behaviour.
beforeEach(() => {
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ success: true }),
  } as Response);
});
