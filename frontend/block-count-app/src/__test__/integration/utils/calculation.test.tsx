/**
 * Calculation Utility Tests
 */

import { describe, it, expect } from 'vitest';
import {
  parseNumericValue,
  calculateRunSubtotal,
  calculateTotals,
  formatNumber,
  hasRunData,
} from '../../utils/calculations';
import type { RunEntry } from '../../types';
import { createEmptyRunEntry } from '../../types';

describe('parseNumericValue', () => {
  it('should return 0 for empty string', () => {
    expect(parseNumericValue('')).toBe(0);
  });

  it('should return 0 for undefined', () => {
    expect(parseNumericValue(undefined)).toBe(0);
  });

  it('should return 0 for null', () => {
    expect(parseNumericValue(null)).toBe(0);
  });

  it('should parse valid numeric string', () => {
    expect(parseNumericValue('123')).toBe(123);
  });

  it('should return 0 for non-numeric string', () => {
    expect(parseNumericValue('abc')).toBe(0);
  });

  it('should parse string with leading zeros', () => {
    expect(parseNumericValue('007')).toBe(7);
  });
});

describe('calculateRunSubtotal', () => {
  it('should sum all block types correctly', () => {
    const entry: RunEntry = {
      ...createEmptyRunEntry(),
      blocks: '10',
      boneMarrowBlocks: '5',
      autopsyBlocks: '3',
      cellButtons: '2',
    };
    expect(calculateRunSubtotal(entry)).toBe(20);
  });

  it('should handle empty/undefined values as 0', () => {
    const entry: RunEntry = {
      ...createEmptyRunEntry(),
      blocks: '',
      boneMarrowBlocks: '',
      autopsyBlocks: '',
      cellButtons: '',
    };
    expect(calculateRunSubtotal(entry)).toBe(0);
  });

  it('should handle string number inputs', () => {
    const entry: RunEntry = {
      ...createEmptyRunEntry(),
      blocks: '15',
      boneMarrowBlocks: '10',
      autopsyBlocks: '0',
      cellButtons: '5',
    };
    expect(calculateRunSubtotal(entry)).toBe(30);
  });

  it('should handle mixed empty and filled values', () => {
    const entry: RunEntry = {
      ...createEmptyRunEntry(),
      blocks: '25',
      boneMarrowBlocks: '',
      autopsyBlocks: '5',
      cellButtons: '',
    };
    expect(calculateRunSubtotal(entry)).toBe(30);
  });
});

describe('calculateTotals', () => {
  it('should aggregate totals across multiple runs', () => {
    const entries: RunEntry[] = [
      {
        ...createEmptyRunEntry(),
        blocks: '10',
        boneMarrowBlocks: '5',
        autopsyBlocks: '2',
        cellButtons: '3',
      },
      {
        ...createEmptyRunEntry(),
        blocks: '20',
        boneMarrowBlocks: '10',
        autopsyBlocks: '4',
        cellButtons: '6',
      },
    ];
    
    const totals = calculateTotals(entries);
    expect(totals.blocks).toBe(30);
    expect(totals.bm).toBe(15);
    expect(totals.autopsy).toBe(6);
    expect(totals.cells).toBe(9);
    expect(totals.total).toBe(60);
  });

  it('should return zeros for empty entries array', () => {
    const totals = calculateTotals([]);
    expect(totals.blocks).toBe(0);
    expect(totals.bm).toBe(0);
    expect(totals.autopsy).toBe(0);
    expect(totals.cells).toBe(0);
    expect(totals.total).toBe(0);
  });

  it('should calculate correct grand total (blocks + bm + autopsy + cells)', () => {
    const entries: RunEntry[] = [
      {
        ...createEmptyRunEntry(),
        blocks: '100',
        boneMarrowBlocks: '25',
        autopsyBlocks: '10',
        cellButtons: '15',
      },
    ];
    
    const totals = calculateTotals(entries);
    expect(totals.total).toBe(150);
    expect(totals.total).toBe(totals.blocks + totals.bm + totals.autopsy + totals.cells);
  });

  it('should handle single entry', () => {
    const entries: RunEntry[] = [
      {
        ...createEmptyRunEntry(),
        blocks: '50',
        boneMarrowBlocks: '0',
        autopsyBlocks: '0',
        cellButtons: '0',
      },
    ];
    
    const totals = calculateTotals(entries);
    expect(totals.blocks).toBe(50);
    expect(totals.total).toBe(50);
  });

  it('should handle many runs (performance check)', () => {
    const entries: RunEntry[] = Array.from({ length: 10 }, (_, i) => ({
      ...createEmptyRunEntry(),
      id: i,
      blocks: '10',
      boneMarrowBlocks: '5',
      autopsyBlocks: '2',
      cellButtons: '3',
    }));
    
    const totals = calculateTotals(entries);
    expect(totals.blocks).toBe(100);
    expect(totals.bm).toBe(50);
    expect(totals.autopsy).toBe(20);
    expect(totals.cells).toBe(30);
    expect(totals.total).toBe(200);
  });
});

describe('formatNumber', () => {
  it('should format small numbers', () => {
    expect(formatNumber(42)).toBe('42');
  });

  it('should format large numbers with commas', () => {
    expect(formatNumber(1234)).toBe('1,234');
    expect(formatNumber(1234567)).toBe('1,234,567');
  });

  it('should format zero', () => {
    expect(formatNumber(0)).toBe('0');
  });
});

describe('hasRunData', () => {
  it('should return false for empty entry', () => {
    const entry = createEmptyRunEntry();
    expect(hasRunData(entry)).toBe(false);
  });

  it('should return true if subtotal > 0', () => {
    const entry: RunEntry = {
      ...createEmptyRunEntry(),
      blocks: '10',
    };
    expect(hasRunData(entry)).toBe(true);
  });

  it('should return true if prefixes are selected', () => {
    const entry: RunEntry = {
      ...createEmptyRunEntry(),
      selectedPrefixes: ['KS', 'KB'],
    };
    expect(hasRunData(entry)).toBe(true);
  });

  it('should return true if checkout time is set', () => {
    const entry: RunEntry = {
      ...createEmptyRunEntry(),
      checkoutTime: '14:30',
    };
    expect(hasRunData(entry)).toBe(true);
  });

  it('should return true if bone marrow case is set', () => {
    const entry: RunEntry = {
      ...createEmptyRunEntry(),
      boneMarrowCase: 'BM-123',
    };
    expect(hasRunData(entry)).toBe(true);
  });
});
