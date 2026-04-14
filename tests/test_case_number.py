"""
Unit tests for utils/case_number.py

Covers all acceptance criteria from T01:
  - validate_case_number("25RR-15616")      → (True, "25RR-15616")
  - validate_case_number("26crn-40013")     → (True, "26CRN-40013")   lowercase normalized
  - validate_case_number("26Crn-40013")     → (True, "26CRN-40013")   mixed-case normalized
  - validate_case_number("2025CN-01234")    → (False, ...) year segment error
  - validate_case_number("26C-01234")       → (False, ...) prefix length error
  - validate_case_number("26KAS-1234")      → (False, ...) suffix length error
  - validate_case_number("26kas01234")      → (False, ...) missing hyphen error
"""

import sys
import os
import importlib.util

# Load utils/case_number directly to avoid triggering utils/__init__.py
# which imports Flask-dependent audit module.
_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, _ROOT)

def _load_module(rel_path, module_name):
    spec = importlib.util.spec_from_file_location(
        module_name,
        os.path.join(_ROOT, rel_path)
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_cn = _load_module("utils/case_number.py", "case_number")
validate_case_number = _cn.validate_case_number
CASE_NUMBER_PATTERN = _cn.CASE_NUMBER_PATTERN

import pytest


# ---------------------------------------------------------------------------
# Valid cases
# ---------------------------------------------------------------------------

def test_valid_standard():
    ok, result = validate_case_number("25RR-15616")
    assert ok is True
    assert result == "25RR-15616"


def test_valid_lowercase_prefix_normalized():
    """Lowercase prefix is silently normalized to uppercase — not an error."""
    ok, result = validate_case_number("26crn-40013")
    assert ok is True
    assert result == "26CRN-40013"


def test_valid_mixed_case_prefix_normalized():
    """Mixed-case prefix is also silently normalized — not an error."""
    ok, result = validate_case_number("26Crn-40013")
    assert ok is True
    assert result == "26CRN-40013"


def test_valid_two_letter_prefix():
    ok, result = validate_case_number("26KA-01200")
    assert ok is True
    assert result == "26KA-01200"


def test_valid_three_letter_prefix():
    ok, result = validate_case_number("26KAA-01200")
    assert ok is True
    assert result == "26KAA-01200"


def test_valid_zero_padded_suffix():
    ok, result = validate_case_number("25CN-00001")
    assert ok is True
    assert result == "25CN-00001"


# ---------------------------------------------------------------------------
# Invalid cases — year segment
# ---------------------------------------------------------------------------

def test_invalid_four_digit_year():
    """2025CN-01234 has a 4-digit year — error must mention year segment."""
    ok, msg = validate_case_number("2025CN-01234")
    assert ok is False
    assert "year" in msg.lower() or "digit" in msg.lower()


def test_invalid_one_digit_year():
    ok, msg = validate_case_number("5CN-01234")
    assert ok is False
    assert "year" in msg.lower() or "digit" in msg.lower()


# ---------------------------------------------------------------------------
# Invalid cases — prefix length
# ---------------------------------------------------------------------------

def test_invalid_one_letter_prefix():
    """26C-01234 has only 1 prefix letter — error must mention prefix."""
    ok, msg = validate_case_number("26C-01234")
    assert ok is False
    assert "prefix" in msg.lower() or "letter" in msg.lower()


def test_invalid_four_letter_prefix():
    ok, msg = validate_case_number("26KAST-01234")
    assert ok is False
    assert "prefix" in msg.lower() or "letter" in msg.lower()


# ---------------------------------------------------------------------------
# Invalid cases — suffix
# ---------------------------------------------------------------------------

def test_invalid_four_digit_suffix():
    """26KAS-1234 has only 4 suffix digits — error must mention suffix."""
    ok, msg = validate_case_number("26KAS-1234")
    assert ok is False
    assert "suffix" in msg.lower() or "digit" in msg.lower()


def test_invalid_six_digit_suffix():
    ok, msg = validate_case_number("26KAS-123456")
    assert ok is False
    assert "suffix" in msg.lower() or "digit" in msg.lower()


# ---------------------------------------------------------------------------
# Invalid cases — missing hyphen
# ---------------------------------------------------------------------------

def test_invalid_missing_hyphen():
    """26kas01234 has no hyphen — error must mention hyphen separator."""
    ok, msg = validate_case_number("26kas01234")
    assert ok is False
    assert "hyphen" in msg.lower() or "separator" in msg.lower()


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_invalid_empty_string():
    ok, msg = validate_case_number("")
    assert ok is False


def test_invalid_non_string():
    ok, msg = validate_case_number(123)  # type: ignore
    assert ok is False


def test_never_raises():
    """validate_case_number must never raise an exception."""
    bad_inputs = [None, 123, [], {}, "", "garbage", "!!-????"]
    for val in bad_inputs:
        result = validate_case_number(val)  # type: ignore
        assert isinstance(result, tuple)
        assert len(result) == 2


def test_case_number_pattern_exported():
    """CASE_NUMBER_PATTERN must be importable and be a non-empty string."""
    import re
    assert isinstance(CASE_NUMBER_PATTERN, str)
    assert len(CASE_NUMBER_PATTERN) > 0
    # Must compile without error
    re.compile(CASE_NUMBER_PATTERN)


def test_md_list_count():
    """MD_LIST must contain exactly 27 entries."""
    _md = _load_module("data/md_list.py", "md_list")
    assert len(_md.MD_LIST) == 27


def test_bone_marrow_eligible_count():
    """BONE_MARROW_ELIGIBLE must contain exactly 3 entries."""
    _md = _load_module("data/md_list.py", "md_list")
    assert len(_md.BONE_MARROW_ELIGIBLE) == 3


def test_bone_marrow_eligible_names():
    _md = _load_module("data/md_list.py", "md_list")
    last_names = {e["last"] for e in _md.BONE_MARROW_ELIGIBLE}
    assert last_names == {"Babaidorabad", "Hardee", "Starshak"}
