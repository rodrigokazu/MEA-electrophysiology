clear all;
close all;
clc;

OldFile = 0;

tic ; % We will measure elapsed time in a loop  
 FS = stoploop({'Stop me before', '300 seconds have elapsed'}) ;  % Set up the stop box: 
 %fprintf('\nSTOPLOOP: elapsed time (s): %5.2f\n',toc) % Display elapsed time 
 
                   
     while(~FS.Stop() && toc < 300), % Check if the loop has to be stopped % start the loop 
         fprintf('%c',repmat(8,6,1)) ; % clear up previous time 
        % fprintf('%5.2f\n',toc) ; % display elapsed time 

listing = dir('D:\Rodrigo\Teste12 matlab (22-23) bit 1-2 27-05-2015\*.mcd');% Modify the filepath
File = size(listing,1) - 2;

if(OldFile ~= File)
    if size(listing,1) > 2
       if  listing(File).bytes > 100000
            if File < 10 
            f = fullfile('D:','Rodrigo','Teste12 matlab (22-23) bit 1-2 27-05-2015',sprintf('datoca000%d.mcd',File));% Modify the filepath
            else
                if File < 100 
            f = fullfile('D:','Rodrigo','Teste12 matlab (22-23) bit 1-2 27-05-2015',sprintf('datoca00%d.mcd',File)); % Modify the filepath
                else
                  if  File < 1000 
                      f = fullfile('D:','Rodrigo','Teste12 matlab (22-23) bit 1-2 27-05-2015',sprintf('datoca0%d.mcd',File)); % Modify the filepath
                  else
                      f = fullfile('D:','Rodrigo','Teste12 matlab (22-23) bit 1-2 27-05-2015',sprintf('datoca%d.mcd',File)); % Modify the filepath
                  end
                end
            end

            a = datastrm(f); 
            b = nextdata(a, 'streamname', 'Digital Data');
            data = b.data;

            if  sum(data(:) == 4) > 0
                disp('Valor 4!')
                sum(data(:) == 4)
                  disp('BIT 2')
            else
                disp('Nenhum valor 4!')
            end

            if  sum(data(:) == 2) > 0
                disp('Valor 2!')
                sum(data(:) == 2)
                  disp('BIT 1')
            else
                disp('Nenhum valor 2!')
            end

            disp('Number of files = ')
            File
       else
           disp('empty file')
       end

    else
        disp('no files')
    end
else
    disp('same file again')
end

OldFile = File;
pause(0.1);             %# Pause for 0.5 second
 end 
     FS.Clear() ; % Clear up the box 
     clear FS ; % this structure has no use anymore
    