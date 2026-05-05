/**
 * Facility Lookup Utility Tests
 */

import { describe, it, expect } from 'vitest';
import {
  getFacilityFromPrefixes,
  isValidPrefix,
  getFacilityForPrefix,
  MULTIPLE_FACILITIES,
} from '../../utils/facilityLookup';

describe('getFacilityFromPrefixes', () => {
  it('should return correct facility for single prefix', () => {
    expect(getFacilityFromPrefixes(['KS'])).toBe('Bakersfield OP');
    expect(getFacilityFromPrefixes(['VVS'])).toBe('Visalia');
    expect(getFacilityFromPrefixes(['KAS'])).toBe('AH Bakersfield');
  });

  it('should return facility when all prefixes map to same facility', () => {
    // Bakersfield OP has: KS, KB, KN, KF
    expect(getFacilityFromPrefixes(['KS', 'KB'])).toBe('Bakersfield OP');
    expect(getFacilityFromPrefixes(['KS', 'KB', 'KN', 'KF'])).toBe('Bakersfield OP');
    
    // Visalia has: VVS, VVB, VVN, VVF, SVS
    expect(getFacilityFromPrefixes(['VVS', 'VVB', 'SVS'])).toBe('Visalia');
  });

  it('should return "Multiple Facilities" for mixed prefixes', () => {
    // KS is Bakersfield OP, VVS is Visalia
    expect(getFacilityFromPrefixes(['KS', 'VVS'])).toBe(MULTIPLE_FACILITIES);
    
    // KAS is AH Bakersfield, KDS is AH Delano
    expect(getFacilityFromPrefixes(['KAS', 'KDS'])).toBe(MULTIPLE_FACILITIES);
  });

  it('should return empty string for no prefixes', () => {
    expect(getFacilityFromPrefixes([])).toBe('');
  });

  it('should return empty string for undefined/null array', () => {
    expect(getFacilityFromPrefixes(undefined as unknown as string[])).toBe('');
    expect(getFacilityFromPrefixes(null as unknown as string[])).toBe('');
  });

  it('should handle invalid prefixes gracefully', () => {
    expect(getFacilityFromPrefixes(['INVALID'])).toBe('');
    expect(getFacilityFromPrefixes(['INVALID1', 'INVALID2'])).toBe('');
  });

  it('should return facility even with mix of valid and invalid prefixes', () => {
    // If some prefixes are invalid but valid ones all map to same facility
    expect(getFacilityFromPrefixes(['KS', 'INVALID'])).toBe('Bakersfield OP');
  });

  it('should handle TC-KPO prefix correctly', () => {
    expect(getFacilityFromPrefixes(['TC-KPO'])).toBe('Bakersfield TC');
  });

  it('should handle Kaweah Health prefixes', () => {
    expect(getFacilityFromPrefixes(['VKS', 'VKB'])).toBe('Kaweah Health Medical Center');
  });
});

describe('isValidPrefix', () => {
  it('should return true for valid prefixes', () => {
    expect(isValidPrefix('KS')).toBe(true);
    expect(isValidPrefix('VVS')).toBe(true);
    expect(isValidPrefix('TC-KPO')).toBe(true);
    expect(isValidPrefix('KAS')).toBe(true);
  });

  it('should return false for invalid prefixes', () => {
    expect(isValidPrefix('INVALID')).toBe(false);
    expect(isValidPrefix('')).toBe(false);
    expect(isValidPrefix('XYZ')).toBe(false);
  });
});

describe('getFacilityForPrefix', () => {
  it('should return correct facility for valid prefix', () => {
    expect(getFacilityForPrefix('KS')).toBe('Bakersfield OP');
    expect(getFacilityForPrefix('VVS')).toBe('Visalia');
    expect(getFacilityForPrefix('KAS')).toBe('AH Bakersfield');
    expect(getFacilityForPrefix('TC-KPO')).toBe('Bakersfield TC');
  });

  it('should return undefined for invalid prefix', () => {
    expect(getFacilityForPrefix('INVALID')).toBeUndefined();
    expect(getFacilityForPrefix('')).toBeUndefined();
  });

  it('should handle all AH facility prefixes', () => {
    expect(getFacilityForPrefix('KAB')).toBe('AH Bakersfield');
    expect(getFacilityForPrefix('KDB')).toBe('AH Delano');
    expect(getFacilityForPrefix('KHB')).toBe('AH Specialty Bakersfield');
    expect(getFacilityForPrefix('KTB')).toBe('AH Tehachapi');
  });
});
