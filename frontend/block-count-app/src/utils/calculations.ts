/**
 * Calculation Utilities for YPB Daily Count Form
 */

import type { RunEntry, Totals } from '../types';

/**
 * Parse a string value to a number, treating empty/undefined as 0
 * @param value - String value to parse
 * @returns Parsed number or 0
 */
export const parseNumericValue = (value: string | undefined | null): number => {
  if (value === undefined || value === null || value === '') {
    return 0;
  }
  const parsed = parseInt(value, 10);
  return isNaN(parsed) ? 0 : parsed;
};

/**
 * Calculate the subtotal for a single run entry
 * Subtotal = blocks + boneMarrowBlocks + autopsyBlocks + cellButtons
 * 
 * @param entry - Run entry to calculate subtotal for
 * @returns Subtotal number
 */
export const calculateRunSubtotal = (entry: RunEntry): number => {
  return (
    parseNumericValue(entry.blocks) +
    parseNumericValue(entry.boneMarrowBlocks) +
    parseNumericValue(entry.autopsyBlocks) +
    parseNumericValue(entry.cellButtons)
  );
};

/**
 * Calculate totals across all run entries
 * 
 * @param entries - Array of run entries
 * @returns Totals object with blocks, bm, autopsy, cells, and total
 */
export const calculateTotals = (entries: RunEntry[]): Totals => {
  if (!entries || entries.length === 0) {
    return {
      blocks: 0,
      bm: 0,
      autopsy: 0,
      cells: 0,
      total: 0,
    };
  }

  const totals = entries.reduce(
    (acc, entry) => {
      acc.blocks += parseNumericValue(entry.blocks);
      acc.bm += parseNumericValue(entry.boneMarrowBlocks);
      acc.autopsy += parseNumericValue(entry.autopsyBlocks);
      acc.cells += parseNumericValue(entry.cellButtons);
      return acc;
    },
    { blocks: 0, bm: 0, autopsy: 0, cells: 0 }
  );

  return {
    ...totals,
    total: totals.blocks + totals.bm + totals.autopsy + totals.cells,
  };
};

/**
 * Format a number for display (with commas for thousands)
 * 
 * @param value - Number to format
 * @returns Formatted string
 */
export const formatNumber = (value: number): string => {
  return value.toLocaleString();
};

/**
 * Check if a run entry has any data entered
 * 
 * @param entry - Run entry to check
 * @returns True if entry has any data
 */
export const hasRunData = (entry: RunEntry): boolean => {
  return (
    calculateRunSubtotal(entry) > 0 ||
    entry.selectedPrefixes.length > 0 ||
    entry.boneMarrowCase.trim() !== '' ||
    entry.checkoutTime.trim() !== ''
  );
};
