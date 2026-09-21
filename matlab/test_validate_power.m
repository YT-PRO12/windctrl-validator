function tests = test_validate_power
tests = functiontests(localfunctions);
end
function testBoundaries(testCase)
r = validate_power([1800; 1000; 1000; 0; 0; NaN; -1], ...
                   [1760; 1050; 1051; 0.5; 0.6; 1; 0], 5, 0.5);
verifyEqual(testCase, r.status, ["PASS"; "PASS"; "FAIL"; "PASS"; "FAIL"; "FAIL"; "FAIL"]);
verifyEqual(testCase, r.errorPct(1), 100 * 40 / 1800, 'AbsTol', 1e-10);
verifyTrue(testCase, isnan(r.errorPct(4)));
end
function testSizeMismatch(testCase)
verifyError(testCase, @() validate_power([1; 2], 1), 'WindCtrl:SizeMismatch');
end
