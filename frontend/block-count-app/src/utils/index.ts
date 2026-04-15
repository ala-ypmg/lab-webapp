/**
 * Utility Functions Index
 */

export {
  parseNumericValue,
  calculateRunSubtotal,
  calculateTotals,
  formatNumber,
  hasRunData,
} from './calculations';

export {
  getFacilityFromPrefixes,
  isValidPrefix,
  getFacilityForPrefix,
  MULTIPLE_FACILITIES,
} from './facilityLookup';

/**
 * Get today's date in YYYY-MM-DD format
 */
export const getTodayDateString = (): string => {
  return new Date().toISOString().split('T')[0];
};

/**
 * Format time string (HH:MM) for display
 * @param time - Time string in HH:MM format
 * @returns Formatted time string
 */
export const formatTime = (time: string): string => {
  if (!time) return '';
  
  const [hours, minutes] = time.split(':');
  const hour = parseInt(hours, 10);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  
  return `${displayHour}:${minutes} ${ampm}`;
};
