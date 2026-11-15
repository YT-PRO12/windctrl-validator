"""CSV formula neutralization must preserve source data and numerical signs."""
import io

import pandas as pd

from windctrl.validation import safe_csv


def test_export_escapes_untrusted_strings_and_preserves_input():
    source = pd.DataFrame({
        "turbine_id": ["  =SUM(1,2)", "@HYPERLINK(A1)", "WT-VALID"],
        "power_kw": [-25.0, 0.0, 1750.5],
    })
    before = source.copy(deep=True)

    exported = safe_csv(source)
    restored = pd.read_csv(io.StringIO(exported), dtype={"turbine_id": str})

    pd.testing.assert_frame_equal(source, before)
    assert restored["turbine_id"].tolist() == [
        "'  =SUM(1,2)", "'@HYPERLINK(A1)", "WT-VALID",
    ]
    assert restored["power_kw"].tolist() == [-25.0, 0.0, 1750.5]
