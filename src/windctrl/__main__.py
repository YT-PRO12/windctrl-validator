"""python -m windctrl --input data/controller_samples.csv --output outputs"""
import argparse
import json
from .validation import ControllerValidator, ValidationConfig, load_csv, summarize
from .reporting import write_report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="outputs")
    parser.add_argument("--tolerance", type=float, default=5.0)
    parser.add_argument("--fail-on-validation", action="store_true", help="Exit 1 when any record fails")
    args = parser.parse_args()
    try:
        cfg = ValidationConfig(tolerance_pct=args.tolerance)
        result = ControllerValidator(cfg).validate(load_csv(args.input))
        write_report(result, cfg, args.output)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(summarize(result), indent=2, allow_nan=False))
    return 1 if args.fail_on_validation and result.status.eq("FAIL").any() else 0

if __name__ == "__main__":
    raise SystemExit(main())
