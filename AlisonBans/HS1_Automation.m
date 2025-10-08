% ----------------------------------------------------------------------------
% Author:           Alison Bans
% Last Update:      09-10-2025
% Description:      Automated generation of HS1 stent designs based on design 
                    variables x values
%                   Randomised variable assignment using latin hypercube sampling.
% Acknowledgement:  Based on work from Ankush Kapoor
% ----------------------------------------------------------------------------

clc;
close all;
clear all;

% ----------------------------------------------------------------------------
% 1. Set the base values of x which will remain constant across designs
% ----------------------------------------------------------------------------

% x(1) = 19;% Number of unit struts in a helix    --> CHANGE
x(2) = 0.46;% Crimped radius                    
x(3) = 18;% Stent length SL x(5)
x(4) = 0.95; %End Row height (6)
% x(5) = 0.1; %Width of the S Connector          --> CHANGE
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

% ----------------------------------------------------------------------------
% 2. Define the latin hypercube space sampling algorithm 
% ----------------------------------------------------------------------------

% Define design space
N = 0;
x1_levels = [17,18,19,20,21];
x5_min = 0.09;
x5_max = 0.11;
x17_min = 0.054;
x17_max = 0.066;
x18_min = 0.054;
x18_max = 0.066;

% Randomly select values following latin hypercube space sampling

% Concatenate the different variable values together
design_space = [x1, x5, x17, x18];

% ----------------------------------------------------------------------------
% 3. Iterate over the different design definitions
% ----------------------------------------------------------------------------

% Add hs1 folder in the path and call the function for stent generation
hs1_folder = fullfile(pwd, '...', 'HS1');
addpath(hs1_folder);
for design_nb = 1:Number
    design_def = design_space(design_nb,:);
    [x(1), x(5), x(17), x(18)] = design_def;
    Main(x);
end

rmpath(hs1_folder);

% ADD automated labelling. 