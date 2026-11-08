"""The validator works on a copy of the caller's DataFrame."""
import pandas as pd

from windctrl.validation import ControllerValidator


def test_validation_does_not_change_original_frame(row):
    before = row.copy(deep=True)
    result = ControllerValidator().validate(row)
    pd.testing.assert_frame_equal(row, before)

    # Result mutations must not write back into the submitted fixture.
    result.loc[0, "actual_power_kw"] = 0.0
    pd.testing.assert_frame_equal(row, before)
