close all; clear all; clc;

% create a tcpip object
t = tcpip('localhost', 12345);

% open the connection
fopen(t);

% Initialize the Robot Simulation
Robot = initializeRobotDH();

Robot.plot([deg2rad(00), ...   % Base
            deg2rad(90), ...   % Shoulder 
            deg2rad(00), ...   % Elbow
            deg2rad(90), ...   % End Effector
            deg2rad(00)]);     % Pitch of End Effector

% Main Loop
while true

    % read some data (read until terminator)
    data = fscanf(t);
    
    try
        %%%%%% Code to parse the data into sections %%%%%% 

        % Split the string by commas
        numbersCellArray = strsplit(data, ',')
        
        % Remove square brackets and convert to numbers
        resultNumbers = zeros(size(numbersCellArray)); % Initialize an array to store the results

        for i = 1:numel(numbersCellArray)
            % Remove square brackets, leading/trailing spaces, and convert to a number
            cleanedStr = strrep(numbersCellArray{i}, '[', ''); % Remove '['
            cleanedStr = strrep(cleanedStr, ']', ''); % Remove ']'
            cleanedStr = strtrim(cleanedStr); % Remove leading/trailing spaces
            resultNumbers(i) = str2double(cleanedStr); % Convert to a number
        end

        % Convert the cell array to an array of numbers
        % numbersArray = str2double(results);

        base_deg = resultNumbers(1);   % Base
        shld_deg = resultNumbers(2);   % Shoulder 
        elbw_deg = resultNumbers(3);   % Elbow
        eeff_deg = resultNumbers(4);   % End Effector
        effp_deg = resultNumbers(5);   % Pitch of End Effector


    %%%%%%--------------------------------------%%%%%%

        % check if data is not empty
        if ~isempty(data)   % Check about offset if needed here or in python 
    
            fprintf('Received data: %s\n', data);
    
            Robot.plot([deg2rad(00 + base_deg), ...   % Base
                        deg2rad(90 + shld_deg), ...   % Shoulder 
                        deg2rad(00 + elbw_deg), ...   % Elbow
                        deg2rad(90 + eeff_deg), ...   % End Effector
                        deg2rad(00 + effp_deg)]);     % Pitch of End Effector
        end

    % if isempty(data)
    %     fprintf('Closing Connection...');
    %     fclose(t);
    %     break;
    % end
        
    catch exception
        % base_deg = 0;   % Base
        % shld_deg = 0;   % Shoulder 
        % elbw_deg = 0;   % Elbow
        % eeff_deg = 0;   % End Effector
        % effp_deg = 0;   % Pitch of End Effector   
        % 
        % if ~isempty(data)   % Check about offset if needed here or in python 
        % 
        % fprintf('Received data catch: %s\n', data);
        % 
        % Robot.plot([deg2rad(00 + base_deg), ...   % Base
        %             deg2rad(90 + shld_deg), ...   % Shoulder 
        %             deg2rad(00 + elbw_deg), ...   % Elbow
        %             deg2rad(90 + eeff_deg), ...   % End Effector
        %             deg2rad(00 + effp_deg)]);     % Pitch of End Effector
        % end
    end
end

function Robot = initializeRobotDH()
    % Twist angle
    Alpha1 = deg2rad(90);
    Alpha2 = deg2rad(0);
    Alpha3 = deg2rad(0);
    Alpha4 = deg2rad(90);
    Alpha5 = deg2rad(0);

    % Link length
    a1 = 0;
    a2 = 165;
    a3 = 150;
    a4 = 0;
    a5 = 0;

    % Link offset
    d1 = 185;
    d2 = -100;
    d3 = 100;
    d4 = 0;
    d5 = 110;

    % Build up arm in terms of serial links using the DH params
    L(1) = Link([0 d1 a1 Alpha1]);
    L(2) = Link([0 d2 a2 Alpha2]);
    L(3) = Link([0 d3 a3 Alpha3]);
    L(4) = Link([0 d4 a4 Alpha4]);
    L(5) = Link([0 d5 a5 Alpha5]);

    % Set the joints limits
    L(1).qlim = [deg2rad(-120) deg2rad(120)];
    L(2).qlim = [deg2rad(0) deg2rad(180)];
    L(3).qlim = [deg2rad(-90) deg2rad(90)];
    L(4).qlim = [deg2rad(15) deg2rad(165)];
    L(5).qlim = [deg2rad(-180) deg2rad(180)];

    % Compute all serial links and state the name
    Robot = SerialLink(L);
    Robot.name = 'Robot';
end

function result = replaceNaNWithZero(inputMatrix)
    [m, n] = size(inputMatrix);
    result = inputMatrix; % Initialize result with the input matrix

    for i = 1:m
        for j = 1:n
            if isnan(inputMatrix(i, j))
                result(i, j) = 0;
            end
        end
    end
end