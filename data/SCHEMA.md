# Controller CSV contract

UTF-8 with header. At most 20,000 rows; dashboard upload limit 5 MB. Extra columns are
ignored. One unique turbine/timestamp pair per record. All data here is synthetic.

| Column | Unit / accepted values | Demonstration range |
|---|---|---|
| timestamp | ISO 8601, interpreted as UTC if no offset | Valid timestamp |
| turbine_id | Nonblank text | Unique per timestamp |
| wind_speed_mps | m/s | 0–50 |
| rotor_speed_rpm | RPM | 0–30 |
| blade_pitch_deg | degrees | 0–90 |
| generator_temp_c | °C | −20–150; operational limit defaults to 100 |
| expected_power_kw | kW | 0–2500 |
| actual_power_kw | kW | 0–2500 |
| controller_output_kw | Commanded power, kW | 0–2500 |
| controller_state | RUNNING, IDLE, SHUTDOWN | Case-insensitive |

These generic demonstration limits are not Siemens Gamesa specifications.

The seeded sample has ordinary tracking noise, injected power deviations,
over-temperature, one missing wind sensor, one unknown state, one invalid negative
rotor reading and one command mismatch per turbine. Each turbine also has a passing
zero-demand record. No proprietary or personal data is used.
