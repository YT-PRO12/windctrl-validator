"""Empty result summaries must have stable, JSON-serializable contracts."""
import json

import pandas as pd

from windctrl.validation import summarize


def test_empty_summary_is_finite_and_json_serializable():
    result = pd.DataFrame({
        "status": pd.Series(dtype="str"),
        "power_error_pct": pd.Series(dtype="float64"),
        "power_deviation_kw": pd.Series(dtype="float64"),
    })
    summary = summarize(result)
    assert summary["total_tests"] == 0
    assert summary["passed_tests"] == 0
    assert summary["failed_tests"] == 0
    assert summary["pass_pct"] == 0.0
    assert summary["percentage_comparable_rows"] == 0
    assert summary["average_error_pct"] is None
    assert summary["maximum_error_pct"] is None
    assert summary["maximum_deviation_kw"] is None
    json.dumps(summary, allow_nan=False)
