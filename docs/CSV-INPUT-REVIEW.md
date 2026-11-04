# Controller CSV input and export review

Input data is synthetic controller telemetry, not certified hardware data.

Review the [schema](../data/SCHEMA.md) before testing uploads. Confirm headers, required columns, numerical ranges, timestamps, identities, duplicate turbine/timestamp pairs, and the maximum row count.

Power deviations at positive demand use relative tolerance. At zero expected power, use the configured absolute kW tolerance instead of dividing by zero. Validate both measured power and controller output.

For exported CSV, test untrusted text beginning with `=`, `+`, `-`, or `@`; the export utility must escape spreadsheet formula prefixes. Do not publish real controller datasets without permission.

This document defines checks to perform, not a claim that all checks ran today.
