"""Deterministic engineering plots and LaTeX report source."""
import json
from dataclasses import asdict
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .validation import safe_csv, summarize

def engineering_plot(result, config):
    fig, axes = plt.subplots(2, 1, figsize=(9, 4.8), constrained_layout=True)
    for turbine, group in result.groupby("turbine_id", dropna=False):
        axes[0].plot(group.test_id, group.actual_power_kw, linewidth=1.3, label=str(turbine))
    axes[0].plot(result.test_id, result.expected_power_kw, "--", color="#24374b", alpha=.65, label="Expected")
    axes[0].set(ylabel="Power (kW)", title="Controller power tracking by test record")
    axes[0].legend(ncol=4, fontsize=8)
    colors = result.status.map({"PASS": "#087e8b", "FAIL": "#c34b4b"})
    axes[1].scatter(result.test_id, result.power_error_pct, c=colors, s=14)
    axes[1].axhline(config.tolerance_pct, color="#c34b4b", linestyle="--", label="Tolerance")
    axes[1].set(xlabel="Test record", ylabel="Absolute power error (%)", title="Failures include sensor and state checks")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=.16)
        ax.spines[["top", "right"]].set_visible(False)
    return fig

def latex_escape(value):
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
                    "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(ch, ch) for ch in str(value))

def latex_report(result, config):
    summary = summarize(result)
    metrics = "\n".join(latex_escape(key.replace("_", " ").title()) + " & " + latex_escape(value if value is not None else "N/A") + r" \\" for key, value in summary.items())
    failed = result[result.status.eq("FAIL")].head(20)
    failures = "\n".join(f"{int(row.test_id)} & {latex_escape(row.turbine_id)} & {latex_escape(row.failure_reasons)}" + r" \\ \hline" for row in failed.itertuples())
    if not failures:
        failures = r"\multicolumn{3}{l}{No failed tests.} \\"
    template = r"""\documentclass[10pt,a4paper]{article}
\usepackage[margin=20mm]{geometry}
\usepackage[T1]{fontenc}
\usepackage{graphicx,longtable,booktabs}
\usepackage[hidelinks]{hyperref}
\title{WindCtrl Validator\\\large Controller Validation Report}
\author{Engineering demonstration}
\date{}
\begin{document}
\maketitle
\section*{Scope and assumptions}
Offline row-level validation of simulated or user-supplied test records.
This is an independent portfolio project, not a turbine certification tool.
Demonstration limits are configurable and are not manufacturer specifications.
Controller output is interpreted as a power command in kW. Each record is
checked for data validity, range, state consistency, temperature and tracking error.
\section*{Configuration}
Power and controller tolerance: TOL\%. Zero-demand absolute tolerance: ZERO kW.
Maximum generator temperature: TEMP degrees C. Boundaries are inclusive.
\section*{Validation summary}
\begin{tabular}{lr}\toprule Metric & Value \\ \midrule
METRICS
\bottomrule\end{tabular}
\paragraph{Metric denominator.} Percentage error excludes zero or invalid expected
power and invalid observed power. Sensor failures remain included when power
values are valid. Zero-demand records use absolute error; consult the comparable
row count. Maximum deviation in kW includes valid zero-demand comparisons.
\section*{Engineering plots}
\IfFileExists{validation.png}{\includegraphics[width=\linewidth]{validation.png}}{Plot unavailable.}
\section*{Failure detail (first 20)}
\begin{longtable}{r p{20mm} p{110mm}}\toprule ID & Turbine & Reasons \\ \midrule
FAILURES
\bottomrule\end{longtable}
Full results: \texttt{validation\_results.csv}. Structured metrics:
\texttt{summary.json}. The application does not model controller dynamics,
transient response, interlocks or hardware-in-the-loop behaviour.
\end{document}
"""
    for key, value in {"TOL": config.tolerance_pct, "ZERO": config.zero_tolerance_kw,
                       "TEMP": config.max_generator_temp_c, "METRICS": metrics, "FAILURES": failures}.items():
        template = template.replace(key, str(value))
    return template

def write_report(result, config, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "validation_results.csv").write_text(safe_csv(result), encoding="utf-8")
    payload = {"configuration": asdict(config), "metrics": summarize(result)}
    (out / "summary.json").write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    fig = engineering_plot(result, config)
    fig.savefig(out / "validation.png", dpi=160)
    plt.close(fig)
    (out / "validation_report.tex").write_text(latex_report(result, config), encoding="utf-8")
    return out
