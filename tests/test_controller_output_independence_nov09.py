"""Measured power and controller output are separately constrained."""
from windctrl.validation import ControllerValidator


def test_bad_controller_output_fails_even_if_measured_power_is_correct(row):
    data = row.copy()
    data.loc[0, "actual_power_kw"] = 1800
    data.loc[0, "controller_output_kw"] = 1600
    result = ControllerValidator().validate(data)
    assert result.loc[0, "status"] == "FAIL"
    assert "controller deviation" in result.loc[0, "failure_reasons"]


def test_bad_measured_power_fails_even_if_controller_command_is_correct(row):
    data = row.copy()
    data.loc[0, "actual_power_kw"] = 1600
    data.loc[0, "controller_output_kw"] = 1800
    result = ControllerValidator().validate(data)
    assert result.loc[0, "status"] == "FAIL"
    assert "power deviation" in result.loc[0, "failure_reasons"]
