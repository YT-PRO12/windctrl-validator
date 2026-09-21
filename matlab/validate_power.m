function results = validate_power(expected, actual, tolerancePct, zeroToleranceKw)
%VALIDATE_POWER Vector power-tracking check; kW inputs, percent tolerance.
% Zero expected power uses an absolute allowance. Boundaries are inclusive.
% This implements the power-only subset of the Python validator.
arguments
    expected (:,1) double
    actual (:,1) double
    tolerancePct (1,1) double {mustBeFinite,mustBeNonnegative} = 5
    zeroToleranceKw (1,1) double {mustBeFinite,mustBeNonnegative} = 0.5
end
if numel(expected) ~= numel(actual)
    error('WindCtrl:SizeMismatch', 'Expected and actual vectors must have equal length.');
end
if tolerancePct > 100 || zeroToleranceKw > 100
    error('WindCtrl:InvalidTolerance', 'Tolerances must not exceed 100.');
end
valid = isfinite(expected) & isfinite(actual) & expected >= 0 & ...
        actual >= 0 & expected <= 2500 & actual <= 2500;
deviationKw = abs(actual - expected);
allowedKw = expected .* tolerancePct ./ 100;
allowedKw(expected == 0) = zeroToleranceKw;
errorPct = NaN(size(expected));
comparable = valid & expected > 0;
errorPct(comparable) = deviationKw(comparable) ./ expected(comparable) .* 100;
pass = valid & deviationKw <= allowedKw + 1e-9;
status = repmat("FAIL", size(expected));
status(pass) = "PASS";
results = table(expected, actual, deviationKw, errorPct, status);
end
