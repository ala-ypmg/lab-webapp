"""
Case number validation for the accessioning workflow.

Format: [YY][PREFIX]-[NNNNN]
  YY     — exactly 2 digit year
  PREFIX — 2-3 uppercase alpha characters (case-insensitive on input)
  -      — literal hyphen separator
  NNNNN  — exactly 5 numeric digits

Input is silently normalized to uppercase before validation.
Invalid format always returns a human-readable error string; never raises.
"""

import re

# Exported regex for reuse in frontend validation (case-insensitive flag applied at call site)
CASE_NUMBER_PATTERN = r'^\d{2}[A-Za-z]{2,3}-\d{5}$'

# Internal compiled pattern (uppercase input only)
_COMPILED = re.compile(r'^(\d+)([A-Z]+)$')


def validate_case_number(value: str) -> tuple[bool, str]:
    """
    Validate and normalize a case number string.

    Returns:
        (True, normalized_value)  — on success; normalized_value is always uppercase
        (False, error_message)    — on failure; message describes the specific violation
    """
    if not isinstance(value, str):
        return (False, "Case number must be a string")

    normalized = value.strip().upper()

    if not normalized:
        return (False, "Case number cannot be empty")

    # Rule 1: hyphen separator is required
    if '-' not in normalized:
        return (False, "Case number must include a hyphen separator (e.g. 25RR-15616)")

    prefix_part, _, suffix_part = normalized.partition('-')

    # Rule 2: prefix part must be digits then letters with no other characters
    m = _COMPILED.match(prefix_part)
    if not m:
        if prefix_part.isdigit():
            return (False, "Prefix letters are missing — format must be YY + 2-3 letters before the hyphen (e.g. 25RR)")
        return (False, "Characters before the hyphen must be 2-digit year followed by 2-3 letters (e.g. 25RR)")

    year_seg = m.group(1)
    alpha_seg = m.group(2)

    # Rule 3: year must be exactly 2 digits
    if len(year_seg) != 2:
        return (False, f"Year segment must be exactly 2 digits (got '{year_seg}' — {len(year_seg)} digit(s))")

    # Rule 4: prefix letters must be 2-3 characters
    if not (2 <= len(alpha_seg) <= 3):
        return (False, f"Prefix must be 2-3 letters (got '{alpha_seg}' — {len(alpha_seg)} letter(s))")

    # Rule 5: suffix must be exactly 5 digits
    if len(suffix_part) != 5 or not suffix_part.isdigit():
        if not suffix_part.isdigit():
            return (False, f"Suffix after the hyphen must be digits only (got '{suffix_part}')")
        return (False, f"Suffix must be exactly 5 digits (got '{suffix_part}' — {len(suffix_part)} digit(s))")

    return (True, normalized)
