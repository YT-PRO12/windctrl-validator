"""CSV exports cannot interpret user-controlled IDs as spreadsheet formulas."""
import io

import pandas as pd
import pytest

from windctrl.validation import safe_csv


@pytest.mark.parametrize("identifier", [
    "=1+1", "+SUM(A1)", "-10+20", "@cmd", "  =HYPERLINK(1)",
])
def test_formula_like_ids_are_prefixed(identifier):
    csv_text = safe_csv(pd.DataFrame({"turbine_id": [identifier]}))
    restored = pd.read_csv(io.StringIO(csv_text), dtype=str)
    assert restored.loc[0, "turbine_id"] == "'" + identifier


def test_safe_text_does_not_acquire_prefix():
    csv_text = safe_csv(pd.DataFrame({"turbine_id": ["WT-001"]}))
    restored = pd.read_csv(io.StringIO(csv_text), dtype=str)
    assert restored.loc[0, "turbine_id"] == "WT-001"
