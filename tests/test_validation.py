import io
import json
import numpy as np
import pandas as pd
import pytest
from windctrl.validation import ControllerValidator, ValidationConfig, summarize, load_csv, safe_csv
from windctrl.reporting import write_report, latex_escape

def test_normal_response_and_metrics(row):
    result = ControllerValidator().validate(row)
    assert result.status.iloc[0] == "PASS"
    assert result.power_error_pct.iloc[0] == pytest.approx(2.2222222222)
    assert summarize(result)["maximum_deviation_kw"] == 40
    assert summarize(result)["pass_pct"] == 100

@pytest.mark.parametrize("actual,status", [(1710,"PASS"),(1890,"PASS"),(1709.99,"FAIL"),(1890.01,"FAIL")])
def test_inclusive_power_boundary(row, actual, status):
    row.loc[0, "actual_power_kw"] = actual
    assert ControllerValidator().validate(row).status.iloc[0] == status

@pytest.mark.parametrize("column,value,reason", [
    ("wind_speed_mps", np.nan, "missing"), ("rotor_speed_rpm", -1, "outside"),
    ("generator_temp_c", 100.01, "over-temperature"),
    ("controller_state", "BROKEN", "unexpected controller state"),
    ("controller_state", "IDLE", "positive demand requires"),
    ("controller_output_kw", 1600, "controller deviation"),
    ("actual_power_kw", np.inf, "non-finite"), ("blade_pitch_deg", 91, "outside"),
    ("timestamp", "nonsense", "timestamp"), ("turbine_id", " ", "turbine ID"),
    ("expected_power_kw", -1, "outside"), ("generator_temp_c", True, "non-finite"),
])
def test_failure_reasons(row, column, value, reason):
    row[column] = row[column].astype(object)
    row.loc[0, column] = value
    result = ControllerValidator().validate(row)
    assert result.status.iloc[0] == "FAIL"
    assert reason in result.failure_reasons.iloc[0]

@pytest.mark.parametrize("actual,status", [(0,"PASS"),(.5,"PASS"),(.5001,"FAIL")])
def test_zero_expected_output(row, actual, status):
    row.loc[0, ["expected_power_kw", "controller_output_kw"]] = 0
    row.loc[0, "controller_state"] = "IDLE"
    row.loc[0, "actual_power_kw"] = actual
    result = ControllerValidator().validate(row)
    assert result.status.iloc[0] == status
    assert np.isnan(result.power_error_pct.iloc[0])
    summary = summarize(result)
    assert summary["average_error_pct"] is None
    json.dumps(summary, allow_nan=False)

def test_zero_with_running_state_fails(row):
    row.loc[0, ["expected_power_kw", "actual_power_kw", "controller_output_kw"]] = 0
    assert "zero demand requires" in ControllerValidator().validate(row).failure_reasons.iloc[0]

def test_temperature_limit_is_inclusive(row):
    row.loc[0, "generator_temp_c"] = 100
    assert ControllerValidator().validate(row).status.iloc[0] == "PASS"

@pytest.mark.parametrize("config", [{"tolerance_pct":-1},{"tolerance_pct":101},{"tolerance_pct":float("nan")},
    {"tolerance_pct":True},{"zero_tolerance_kw":-1},{"max_generator_temp_c":200}])
def test_invalid_configuration(config):
    with pytest.raises(ValueError):
        ValidationConfig(**config)

def test_duplicate_records_fail(row):
    result = ControllerValidator().validate(pd.concat([row, row], ignore_index=True))
    assert result.status.eq("FAIL").all()
    assert result.failure_reasons.str.contains("duplicate").all()

def test_schema_and_empty_input(row):
    with pytest.raises(ValueError, match="Missing columns"):
        ControllerValidator().validate(row.drop(columns="timestamp"))
    with pytest.raises(ValueError, match="No controller"):
        ControllerValidator().validate(row.iloc[:0])
    with pytest.raises(ValueError, match="Maximum"):
        ControllerValidator().validate(pd.concat([row] * 20001, ignore_index=True))
    with pytest.raises(ValueError, match="Duplicate column"):
        ControllerValidator().validate(pd.concat([row, row[["timestamp"]]], axis=1))

def test_csv_round_trip_and_bad_csv(row):
    assert len(load_csv(io.StringIO(row.to_csv(index=False)))) == 1
    for value in ["", '"unclosed']:
        with pytest.raises(ValueError):
            load_csv(io.StringIO(value))

def test_report_bundle_and_escaping(row, tmp_path):
    row.loc[0, "turbine_id"] = "WT_01%&"
    row.loc[0, "generator_temp_c"] = 110
    cfg = ValidationConfig()
    result = ControllerValidator(cfg).validate(row)
    write_report(result, cfg, tmp_path)
    assert (tmp_path / "validation.png").stat().st_size > 1000
    assert json.loads((tmp_path / "summary.json").read_text())["metrics"]["failed_tests"] == 1
    assert "WT\\_01\\%\\&" in (tmp_path / "validation_report.tex").read_text()
    assert latex_escape("a#b") == "a\\#b"

def test_csv_formula_escape():
    output = safe_csv(pd.DataFrame({"turbine_id":["=1+1", " +cmd", "WT-001"], "reading":[-2, 3, 4]}))
    assert "'=1+1" in output
    assert "' +cmd" in output
    assert ",-2" in output
