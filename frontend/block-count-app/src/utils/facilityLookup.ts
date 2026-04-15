/**
 * Facility Lookup Utilities for YPB Daily Count Form
 */

import { PREFIX_TO_FACILITY } from '../constants/facilities';

/**
 * Multiple facilities indicator constant
 */
export const MULTIPLE_FACILITIES = 'Multiple Facilities';

/**
 * Get facility name from selected prefixes
 * 
 * - Returns the facility name if all prefixes map to the same facility
 * - Returns "Multiple Facilities" if prefixes map to different facilities
 * - Returns empty string if no prefixes are selected
 * 
 * @param selectedPrefixes - Array of selected prefix strings
 * @returns Facility name, "Multiple Facilities", or empty string
 */
export const getFacilityFromPrefixes = (selectedPrefixes: string[]): string => {
  if (!selectedPrefixes || selectedPrefixes.length === 0) {
    return '';
  }

  // Get unique facilities from selected prefixes
  const facilities = [...new Set(
    selectedPrefixes
      .map((prefix) => PREFIX_TO_FACILITY[prefix])
      .filter((facility) => facility !== undefined)
  )];

  if (facilities.length === 0) {
    return '';
  }

  if (facilities.length === 1) {
    return facilities[0];
  }

  return MULTIPLE_FACILITIES;
};

/**
 * Check if a prefix is valid (exists in the mapping)
 * 
 * @param prefix - Prefix to validate
 * @returns True if prefix is valid
 */
export const isValidPrefix = (prefix: string): boolean => {
  return prefix in PREFIX_TO_FACILITY;
};

/**
 * Get facility for a single prefix
 * 
 * @param prefix - Prefix to look up
 * @returns Facility name or undefined
 */
export const getFacilityForPrefix = (prefix: string): string | undefined => {
  return PREFIX_TO_FACILITY[prefix];
};
