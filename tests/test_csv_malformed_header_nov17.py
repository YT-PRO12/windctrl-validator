"""Malformed CSV headers fail closed without altering input streams."""
from io import StringIO

import pytest

from windctrl.validation import COLUMNS, load_csv


def test_missing_required_columns_fail_before_numeric_validation():
    with pytest.raises(ValueError, match="Missing columns"):
        load_csv(StringIO("timestamp,turbine_id\n2026-11-17T10:00:00Z,WT-A\n"))


def test_headers_without_rows_are_rejected():
    csv_text = ",".join(COLUMNS) + "\n"
    with pytest.raises(ValueError, match="No controller records"):
        load_csv(StringIO(csv_text))


def test_unreadable_empty_file_has_useful_error():
    with pytest.raises(ValueError, match="readable UTF-8 table"):
        load_csv(StringIO(""))
