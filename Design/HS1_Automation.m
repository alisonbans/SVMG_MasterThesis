% -------------------------------------------------------------------------
% Author:           Alison Bans
% Last Update:      09-10-2025
% Description:      Automated generation of HS1 stent designs based on design 
%                   variables x values
%                   Randomised variable assignment using latin hypercube sampling.
% Acknowledgement:  Based on work from Ankush Kapoor
% -------------------------------------------------------------------------

clc;
close all;
clear all;

% -------------------------------------------------------------------------
% 1. Set the base values of x which will remain constant across designs
% -------------------------------------------------------------------------

% x(1) = 19;% Number of unit struts in a helix    --> CHANGE
x(2) = 0.46;% Crimped radius                    
x(3) = 18;% Stent length SL x(5)
x(4) = 0.95; %End Row height (6)
x(5) = 0.1; %Width of the S Connector --> CHANGE
x(6) = 1.63339;% ww_ab(1)
x(7) = 0.39003;% ww_ab(2) 
x(8) = 0.75959;% ww_ab(3)
x(9) = 0.81258;% ww_ab(4)
x(10) = 1.31384;% ww_da(1)
x(11) = 0.04872;% ww_da(2)
x(12) = 0.00164;% ww_da(3)
x(13) = 0.07540;% ww_connector(1)
x(14) = 0.61571;% ww_connector(2)
x(15) = 4.16285;% ww_connector(3)
x(16) = 1.79921;% ww_connector(4)
% x(17) = 0.06;% strut width                      --> CHANGE
% x(18) = 0.06;% strut_thickness                  --> CHANGE

% -------------------------------------------------------------------------
% 2. Define the latin hypercube space sampling algorithm 
% -------------------------------------------------------------------------

% Define design space -----------------------------------------------------
N = 30;
x1_levels = [15,16,17,18,19,20,21,22,23,24,25];
x1_levels = [17,18,19,20,21];
x17_min = 0.08;
x17_max = 0.12;
x18_min = 0.055;
x18_max = 0.065;

% Set a seed and randomly select values following latin hypercube space sampling
rng(123);
lhs_matrix = lhsdesign(N,3);
%x1 = x1_levels(1)+ round(lhs_matrix(:,1)*(x1_levels(end)-x1_levels(1)));
[~, x1_idx] = sort(lhs_matrix(:,1));
x1 = x1_levels(mod(x1_idx - 1, numel(x1_levels)) + 1);
x17 = x17_min + lhs_matrix(:,2)*(x17_max-x17_min);
x18 = x18_min + lhs_matrix(:,2)*(x18_max-x18_min);

% Concatenate the different variable values together ----------------------
% Ensure column vectors
x1 = x1(:);
x17 = x17(:);
x17 = round(x17, 4);
x18 = x18(:);
x18 = round(x18, 4);
design_space = [x1 x17 x18];

% Visualise the sampling space to ensure correct implementation -----------
figure;
varNames = {'NUS', 'SW', 'ST'};
[~, ax] = plotmatrix(design_space);
for i = 1:length(varNames)
    ylabel(ax(i,1), varNames{i});
    xlabel(ax(end,i), varNames{i});
end
title('Pairwise Scatter Plots of Design Space')

% REMOVE THIS -------------------------------------------------------------
%x1_default x2_default x5_default x17_default x18_default;
%values = 16:2:22;
%design_space = [17, 0.052674418, 0.051782946];

% -----------------------------------------------------------------------
%N=1;
labeled_space = [design_space, NaN(N,1)];
disp(labeled_space);

% -------------------------------------------------------------------------
% 3. Iterate over the different design definitions
% -------------------------------------------------------------------------

% Add hs1 folder in the path and call the function for stent generation
hs1_folder = fullfile(pwd, 'HS1');
addpath(hs1_folder);
for design_nb = 1:N
    disp(design_nb);
    design_def = design_space(design_nb,:);
    x(1)= design_def(1);
    x(17)= design_def(2);
    x(18) = design_def(3);
    geometry_success = Main(x);
    labeled_space(design_nb, end) = geometry_success;
end
% Convert matrix to table
labeled_space_csv = array2table(labeled_space, 'VariableNames', {'NUS', 'SW', 'ST', 'Label'});

% Save table as CSV
writetable(labeled_space_csv, 'labeled_design_space.csv');

rmpath(hs1_folder);