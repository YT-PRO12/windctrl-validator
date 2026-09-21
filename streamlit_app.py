"""Recruiter-facing controller validation workbench."""
from pathlib import Path
import io
import zipfile
import matplotlib.pyplot as plt
import streamlit as st
from windctrl.validation import ControllerValidator, ValidationConfig, load_csv, summarize, safe_csv
from windctrl.reporting import engineering_plot, latex_report

st.set_page_config(page_title="WindCtrl Validator", page_icon="🌀", layout="wide")
st.caption("ENGINEERING TOOLKIT / CONTROLLER VALIDATION")
st.title("WindCtrl Validator")
st.write("Inspect controller test records, validate power tracking and investigate failed conditions.")
st.info("Synthetic demonstration data · configurable limits · independent portfolio project")
sample = Path(__file__).parent / "data/controller_samples.csv"
with st.sidebar:
    st.header("Validation settings")
    tolerance = st.slider("Power / command tolerance (%)", 0.0, 20.0, 5.0, 0.5)
    zero = st.number_input("Zero-demand allowance (kW)", 0.0, 100.0, 0.5, 0.1)
    temperature = st.number_input("Generator temperature limit (°C)", -20.0, 150.0, 100.0, 1.0)
    uploaded = st.file_uploader("Upload controller CSV", type=["csv"])
    st.download_button("Download sample CSV", sample.read_bytes(), "controller_samples.csv", "text/csv")
    st.caption("Uploads stay in session memory. Maximum 5 MB / 20,000 rows.")
cfg = ValidationConfig(tolerance, zero, temperature)
try:
    frame = load_csv(uploaded if uploaded is not None else sample)
except (ValueError, OSError) as exc:
    st.error(str(exc))
    st.stop()
with st.expander("Input records and column definitions", expanded=False):
    st.dataframe(frame, use_container_width=True, hide_index=True)
    st.caption("Power and controller output: kW; wind: m/s; rotor: RPM; pitch: degrees; temperature: °C. Timestamps: ISO 8601 UTC.")
st.button("Run controller validation", type="primary", help="Recalculates with the current data and settings.")
result = ControllerValidator(cfg).validate(frame)
summary = summarize(result)
columns = st.columns(4)
for col, label, value in zip(columns, ["Records checked", "Passed", "Failed", "Pass rate"],
                            [summary["total_tests"], summary["passed_tests"], summary["failed_tests"], f'{summary["pass_pct"]:.1f}%']):
    col.metric(label, value)
cols = st.columns(2)
mean = summary["average_error_pct"]
maximum = summary["maximum_error_pct"]
cols[0].metric("Average absolute power error", "N/A" if mean is None else f"{mean:.2f}%")
cols[1].metric("Maximum power error", "N/A" if maximum is None else f"{maximum:.2f}%")
st.caption(f'Percentage metrics compare {summary["percentage_comparable_rows"]} rows with valid, positive expected power. Zero demand uses the absolute kW allowance.')
plots, records, rules = st.tabs(["Engineering plots", "Results and failures", "How validation works"])
fig = engineering_plot(result, cfg)
with plots:
    st.pyplot(fig, use_container_width=True)
with records:
    status = st.selectbox("Result filter", ["All records", "FAIL", "PASS"])
    subset = result if status == "All records" else result[result.status.eq(status)]
    st.dataframe(subset, use_container_width=True, hide_index=True)
    st.download_button("Download validation results", safe_csv(result), "validation_results.csv", "text/csv")
with rules:
    st.markdown("""1. Validate schema, finite numbers, timestamps and duplicate records.
2. Check demonstration sensor ranges and generator temperature.
3. Check RUNNING / IDLE / SHUTDOWN consistency with expected demand.
4. Compare actual power and controller command against expected power.
5. A record passes only when every check passes. Boundaries are inclusive.

**Error = |actual − expected| / expected × 100.** Zero expected output uses an absolute kW tolerance.
This is offline record validation; it does not simulate control dynamics or certify a real turbine.""")
buffer = io.BytesIO()
figure_bytes = io.BytesIO()
fig.savefig(figure_bytes, format="png", dpi=160)
plt.close(fig)
with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr("validation_report.tex", latex_report(result, cfg))
    archive.writestr("validation.png", figure_bytes.getvalue())
    archive.writestr("validation_results.csv", safe_csv(result))
st.download_button("Download LaTeX report bundle", buffer.getvalue(), "windctrl_report.zip", "application/zip")
st.caption("Compile the downloaded report with pdflatex. No Python installation is needed to use this dashboard.")
