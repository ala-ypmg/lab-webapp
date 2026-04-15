/**
 * Case number validation — mirrors utils/case_number.py.
 *
 * Format: [YY][PREFIX]-[NNNNN]
 *   YY     — exactly 2 digit year
 *   PREFIX — 2-3 uppercase alpha characters (input silently normalized)
 *   -      — literal hyphen
 *   NNNNN  — exactly 5 digits
 */

export const CASE_NUMBER_PATTERN = /^\d{2}[A-Za-z]{2,3}-\d{5}$/;

const PREFIX_RE = /^(\d+)([A-Z]+)$/;

export type ValidationResult =
  | { valid: true; normalized: string }
  | { valid: false; error: string };

export function validateCaseNumber(raw: string): ValidationResult {
  if (typeof raw !== 'string') {
    return { valid: false, error: 'Case number must be a string' };
  }

  const normalized = raw.trim().toUpperCase();

  if (!normalized) {
    return { valid: false, error: 'Case number cannot be empty' };
  }

  // Rule 1: hyphen is required
  if (!normalized.includes('-')) {
    return {
      valid: false,
      error: 'Case number must include a hyphen separator (e.g. 25RR-15616)',
    };
  }

  const hyphenIdx = normalized.indexOf('-');
  const prefixPart = normalized.slice(0, hyphenIdx);
  const suffixPart = normalized.slice(hyphenIdx + 1);

  // Rule 2: prefix part must match digits then letters
  const m = PREFIX_RE.exec(prefixPart);
  if (!m) {
    if (/^\d+$/.test(prefixPart)) {
      return {
        valid: false,
        error: 'Prefix letters are missing — format must be YY + 2-3 letters before the hyphen (e.g. 25RR)',
      };
    }
    return {
      valid: false,
      error: 'Characters before the hyphen must be 2-digit year followed by 2-3 letters (e.g. 25RR)',
    };
  }

  const yearSeg = m[1];
  const alphaSeg = m[2];

  // Rule 3: year must be exactly 2 digits
  if (yearSeg.length !== 2) {
    return {
      valid: false,
      error: `Year segment must be exactly 2 digits (got '${yearSeg}' — ${yearSeg.length} digit(s))`,
    };
  }

  // Rule 4: prefix must be 2-3 letters
  if (alphaSeg.length < 2 || alphaSeg.length > 3) {
    return {
      valid: false,
      error: `Prefix must be 2-3 letters (got '${alphaSeg}' — ${alphaSeg.length} letter(s))`,
    };
  }

  // Rule 5: suffix must be exactly 5 digits
  if (suffixPart.length !== 5 || !/^\d+$/.test(suffixPart)) {
    if (!/^\d+$/.test(suffixPart)) {
      return {
        valid: false,
        error: `Suffix after the hyphen must be digits only (got '${suffixPart}')`,
      };
    }
    return {
      valid: false,
      error: `Suffix must be exactly 5 digits (got '${suffixPart}' — ${suffixPart.length} digit(s))`,
    };
  }

  return { valid: true, normalized };
}
