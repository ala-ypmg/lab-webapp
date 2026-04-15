/**
 * Facility-Prefix Mapping Constants
 * 
 * Prefixes auto-populate the facility name. One facility can have multiple prefixes.
 */

import type { FacilityPrefixMap, PrefixToFacilityMap } from '../types';

/**
 * Mapping of facility names to their associated case prefixes
 */
export const FACILITY_PREFIX_MAP: FacilityPrefixMap = {
  'AH Bakersfield': ['KAS', 'KAB', 'KAN', 'KAF'],
  'AH Delano': ['KDS', 'KDB', 'KDN', 'KDF'],
  'AH Specialty Bakersfield': ['KHS', 'KHB', 'KHN', 'KHF'],
  'AH Tehachapi': ['KTS', 'KTB', 'KTN', 'KTF'],
  'Bakersfield OP': ['KS', 'KB', 'KN', 'KF'],
  'Bakersfield TC': ['TC-KPO'],
  'Kaweah Health Medical Center': ['VKS', 'VKB', 'VKN', 'VKF'],
  'Visalia': ['VVS', 'VVB', 'VVN', 'VVF', 'SVS'],
};

/**
 * Reverse lookup: prefix → facility
 * Generated from FACILITY_PREFIX_MAP
 */
export const PREFIX_TO_FACILITY: PrefixToFacilityMap = Object.entries(FACILITY_PREFIX_MAP).reduce(
  (acc, [facility, prefixes]) => {
    prefixes.forEach((prefix) => {
      acc[prefix] = facility;
    });
    return acc;
  },
  {} as PrefixToFacilityMap
);

/**
 * All available prefixes (flat array)
 */
export const ALL_PREFIXES: string[] = Object.values(FACILITY_PREFIX_MAP).flat();

/**
 * All facility names
 */
export const ALL_FACILITIES: string[] = Object.keys(FACILITY_PREFIX_MAP);

/**
 * Prefixes grouped by facility for organized display
 */
export const PREFIXES_BY_FACILITY = Object.entries(FACILITY_PREFIX_MAP).map(([facility, prefixes]) => ({
  facility,
  prefixes,
}));
