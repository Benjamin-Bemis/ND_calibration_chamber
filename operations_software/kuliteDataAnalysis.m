clc; clear; close all; format longG

omega = load("D:\omega.mat"); 
filepaths = ["D:\C1--kulite_test_calibration_mean_2sec--00000.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00001.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00002.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00003.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00004.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00005.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00006.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00007.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00008.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00009.txt",...
    "D:\C1--kulite_test_calibration_mean_2sec--00010.txt"];

mean_voltages = zeros(1, length(filepaths));
mean_pressures_kpa = omega.pressure_kpa_mean;
voltages = struct();
names = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',...
    'r','s','t','u','v','w','x','y','z'];

for path = 1:length(filepaths)
    data = readmatrix(filepaths(path),'Delimiter',{',',''});
    data = data(3:end,1:2);
    voltages = setfield(voltages, names(path), data(:,2));
    mean_voltages(path) = mean(data(:,2));
end

% Use the linear region if the ends have bad data points
mean_voltages = mean_voltages(2:10);
mean_pressures_kpa = mean_pressures_kpa(2:10);

plot(mean_voltages, mean_pressures_kpa, 'o'); hold on
ylabel('Chamber Pressure, kPa')
xlabel('Voltage, V')
legend()

f = polyfit(mean_voltages, mean_pressures_kpa, 1);
plot(mean_voltages, f(1)*mean_voltages + f(2));

disp(['slope: ', num2str(f(1)), 'kPa/V'])
disp(['Pressure at 0V ', num2str(f(2)), 'kPa'])

psi2kPa = 6.89475728;
Sensitivity = 9.998; % mV/Psi A
Sens = Sensitivity/psi2kPa;

%% Uncertainty
meanVoltage = abs(mean(mean_voltages));
meanPressure = mean(mean_pressures_kpa);

driftVoltage = mean_voltages - meanVoltage;
driftPressure = mean_pressures_kpa - meanPressure;

readingVoltage = 0.00005; readingPressure = 0.00005;

% use maximum functions again to find the max accuracy
SystematicVoltage = 0.0017*mean_voltages; % 1.7% of reading
SystematicPressure = 0.0008*mean_pressures_kpa; % 0.08% of reading

UncertaintyVoltage = sqrt(driftVoltage.^2 + readingVoltage.^2 + SystematicVoltage.^2);
UncertaintyPressure = sqrt(driftPressure.^2 + readingPressure.^2 + SystematicPressure.^2);

% Put the errorbars on the graph
errorbar(mean_voltages, mean_pressures_kpa, UncertaintyPressure);
errorbar(mean_voltages, mean_pressures_kpa, UncertaintyVoltage, 'horizontal');
legend('Kulite', 'polyfit', 'Uncertainty in Pressure','Uncertainty in Voltage', 'Location','southeast')

% propagate the reading uncertainties to find uncertainty in slope, Rumbach
% book cited in manual page 144, F is slope = Pressure/Voltage

slopeError = meanPressure/meanVoltage*...
    sqrt((UncertaintyPressure./meanPressure).^2 + (UncertaintyVoltage./meanVoltage).^2);
disp(['Slope error: ', num2str(slopeError)])


