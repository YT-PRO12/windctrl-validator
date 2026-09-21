% Run from the repository root in MATLAB R2020b or newer.
addpath('matlab');
input = readtable(fullfile('data', 'controller_samples.csv'));
results = validate_power(input.expected_power_kw, input.actual_power_kw, 5, 0.5);
results.turbine_id = input.turbine_id;
if ~exist('outputs', 'dir'), mkdir('outputs'); end
writetable(results, fullfile('outputs', 'matlab_power_results.csv'));
figure('Name', 'Power tracking validation');
plot(input.expected_power_kw, '--'); hold on;
plot(input.actual_power_kw); grid on;
xlabel('Test record'); ylabel('Power (kW)');
legend('Expected', 'Actual'); title('WindCtrl power tracking');
exportgraphics(gcf, fullfile('outputs', 'matlab_power_tracking.png'));
disp(groupsummary(results, 'status'));
