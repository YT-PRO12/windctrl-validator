"""Schema checks should reject ambiguous frames before numeric calculations."""
import pandas as pd
import pytest

from windctrl.validation import COLUMNS, ControllerValidator


def complete_record():
    return pd.DataFrame([{column: 0 for column in COLUMNS}])


def test_empty_frame_is_rejected():
    with pytest.raises(ValueError, match="No controller records found"):
        ControllerValidator().validate(pd.DataFrame(columns=COLUMNS))


def test_missing_required_column_is_rejected():
    frame = complete_record().drop(columns=["timestamp"])
    with pytest.raises(ValueError, match="Missing columns: timestamp"):
        ControllerValidator().validate(frame)


def test_duplicate_column_names_are_rejected():
    frame = complete_record()
    frame.insert(0, "timestamp", "2026-11-13T09:00:00Z", allow_duplicates=True)
    with pytest.raises(ValueError, match="Duplicate column names"):
        ControllerValidator().validate(frame)
