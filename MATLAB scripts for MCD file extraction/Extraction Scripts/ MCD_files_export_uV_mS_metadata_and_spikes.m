%Brain Embodiment Laboratory%
%University of Reading%

%-------------------------------------------------------------------------%

%BEL's Script to extract the raw data recorded from a folder containing *.mcd files%

%The *.mcd format is property of http://www.multichannelsystems.com/%
   
%This script goes through your folders to find the MCD files

%It exports to some *.mat files%

%-------------------------------------------------------------------------%

%Written by Rodrigo Kazu%
%Any enquiries to r.siqueiradesouza@pgr.reading.ac.uk%

%-------------------------------------------------------------------------%

%This script uses functions from mcintfac that are no longer supported%

%You need to have the methods from mcintfac, meatools, from MultiChannel Systems added to your PATH

%First, it gets all the *.mcd files from your directory%

%Add your folder in both variables (folder_name and folder)%

%-------------------------------------------------------------------------%

%main_folder_name = input('\n Welcome to the University of Reading - Brain Embodiment Laboratory (SBS - BEL) \n This script was designed to extract the raw data and spike data recorded from a folder containing *.mcd files. \n \n \n You NEED to have the methods from mcintfac, meatools, from MultiChannel Systems added to your PATH!\n \n \n Please enter the folder where you have your recordings AS A STRING (inside simple quotation marks) and press return. \n \n \n Your *.mcd files must be inside folders named with the MEA number \n \n \n');

main_folder_name='C:\Ephys data\DIV 21\'

%-------------------------------------------------------------------------%

% Function dir() lists the contents of a folder and has the variable isdir%
% isdir = 1 means that it is a directory, 0 means false%

% Add *.mcd at the end if you want to extract only the *.mcd files%

%-------------------------------------------------------------------------%

main_folder = dir(main_folder_name); 

total_folder_num = length(main_folder([main_folder.isdir])); % Don't know why it happens, but it adds two ghost folders to the count, so you may need to subtract them;

for folders = 1:total_folder_num
    
    if main_folder(folders).isdir == 1 %Run the loop only for the folders
    
        conditional = size(main_folder(folders).name); %size() function returns a matrix, god knows why
        
        if conditional(1,2) > 3 %dir returns two ghost directories, as mentioned

            folder_analysed = strcat(main_folder_name, main_folder(folders).name);

            folder_analysed = strcat(folder_analysed, '\'); %Adds the backslash to the folder name
            
            folder_analysed_mcd = strcat(folder_analysed, '\*.mcd');

            folder_analysed_contents = dir(folder_analysed_mcd);

            total_mcd_num = length(folder_analysed_contents(not([folder_analysed_contents.isdir]))); 

            metadata_cell = cell(total_mcd_num,8); %Creates a cell to store the files and the information needed for the current analysis

            %-------------------------------------------------------------------------%

            %This step will iterate through your folder%

            for mcs_data = 1:total_mcd_num  %Use this for all files in the folder being checked%

                mcd_file = strcat(folder_analysed,folder_analysed_contents(mcs_data,1).name); %This concatenate the two strings so you have the whole file name.

            %datastrm is a data object constructor for data recorded with MC_Rack%

                data = datastrm(mcd_file);

                metadata_cell{mcs_data,1} = mcd_file; % It adds the file name to the cell
                metadata_cell{mcs_data,2} = data; % It adds the data object generated by datastrm() to the cell

                stream_names = getfield (data, 'StreamNames'); %It gets the streams from the file
                metadata_cell{mcs_data,3} = stream_names; %It adds the stream names to the cell

            %-------------------------------------------------------------------------%

            %nextdata reads data from an MCRack OLE Object opened with datastrm.m%

            %It gets the electrode (channel) order right, check nextdata's help for details% 

            %The streamname can be any of the streams present in the raw data%

            %Also, gets the full record time in ms%

            %-------------------------------------------------------------------------%

               start = getfield(data,'sweepStartTime'); %Gets when the record started
               finish = getfield(data,'sweepStopTime'); %And when it ended.

               metadata_cell{mcs_data,4}= [start finish]; %It adds to the cell the lenght of the recorded file

               microseconds_pertick = getfield(data,'MicrosecondsPerTick');
               milisamples_persecond = getfield(data,'MillisamplesPerSecond2');

               metadata_cell{mcs_data,5} = microseconds_pertick;
               metadata_cell{mcs_data,6} = milisamples_persecond;

               u_data = nextdata (data, 'startend', [start finish], 'streamname','Electrode Raw Data 1');
               s_data = nextdata (data, 'startend', [start finish], 'streamname','Spikes 1');


            %Put the channel names in the recorded order into a Matrix%

            %-------------------------------------------------------------------------%

              streamID = getstreamnumber(data, 'Electrode Raw Data 1'); %Gets the Stream Number of the Raw Data
              channel_names = getfield(data, 'HardwareChannelNames2'); %Get the correct channels from where the raw data is
              channelID_matrix = channel_names{streamID}; %Add the channel names to a new cell

            %-------------------------------------------------------------------------%

            %Acquiring spiketime data%

            %-------------------------------------------------------------------------%   
              
              spiketimes=s_data.spiketimes; %It is given in ms
              
              
            %-------------------------------------------------------------------------%

            %Conversion to ms using the MCS sample code%

            %-------------------------------------------------------------------------%   

                 ticks = 1000/getfield(data,'MicrosecondsPerTick');
                 timedata = [start*ticks:finish*ticks]/ticks;

                 metadata_cell{mcs_data,7} = ticks;
                 metadata_cell{mcs_data,8} = timedata;  

            %-------------------------------------------------------------------------%

            %Converting to uV%

            %-------------------------------------------------------------------------%

            chunk_size = finish; % Size of the file part you want to analyse, use the variable finish for the whole recording
           
            voltage_columns = size(timedata);
            
            voltagedata_cell = zeros(60, voltage_columns(1,2));
            
            voltagedata_cell = ad2muvolt(data, u_data.data, 'Electrode Raw Data 1');
            
            spikedata_cell = {}; 
            
            for firingchannel = 1:60
            
                spikedata_cell{firingchannel, 1} = ad2muvolt(data, s_data.spikevalues{firingchannel}, 'Spikes 1'); %Converting spikedata to mV
            
            end

            %-------------------------------------------------------------------------%

            %This was a loop to convert channel by channel%

            %-------------------------------------------------------------------------%

            %   for firingchannel = 1:60

             %       for chunk = 1:chunk_size       

             %          u_data.data(firingchannel, chunk) = ad2muvolt(data, u_data.data(firingchannel, chunk), 'Electrode Raw Data 1');     
             %         voltagedata_cell{firingchannel, chunk+1} = u_data.data(firingchannel, chunk);
             %     end
             %  end


            %-------------------------------------------------------------------------%

            %Exporting the Data to various aligned *.mat files%

            %-------------------------------------------------------------------------%


                file_name=strrep(mcd_file,'.mcd',''); %Removes the " .mcd "

                data_exported=strcat(file_name, '_RAW_voltage_data'); %This adds a description to your filename

                save (data_exported, 'voltagedata_cell', '-v7.3'); %Variable cannot be saved to a MAT-file whose version is older than 7.3. To save this variable, use the -v7.3 switch.
                
                channels_exported=strcat(file_name, '_correct_electrode_order'); %This adds a description to your filename
                
                save (channels_exported,'channelID_matrix');
               
                time_exported=strcat(file_name, '_time_array_ms'); %This adds a description to your filename
                
                save (time_exported,'timedata');

                metadata_exported = strcat(file_name, '_METADATA'); %This adds a description to your filename

                save (metadata_exported, 'metadata_cell');    
                
                spiketimes_exported = strcat(file_name, '_spiketimes_ms'); %This adds a description to your filename
                
                save (spiketimes_exported,'spiketimes');
                
                spikevalues_exported = strcat(file_name, '_spikevalues_uV'); %This adds a description to your filename
                
                save (spikevalues_exported,'spikedata_cell');
                

            %Gets rid of the 'B'%

            %-------------------------------------------------------------------------%

            %channelID_matrix = strrep(channelID_matrix,'B',''); 

            %-------------------------------------------------------------------------%

            %Data type conversion, from string to numeric %

            %-------------------------------------------------------------------------%

            %channelID_matrix = str2mat(channelID_matrix);
            %channelID_matrix = str2num(channelID_matrix);

            %-------------------------------------------------------------------------%


            end
        end
    end
end 

%-------------------------------------------------------------------------%

%Portable asset: Plot function for data files converted with the old MCS support methods %

%-------------------------------------------------------------------------%


%  for node = 1:60
      
      
%    subplot(8,8,node); %Please note that the graph is rotated!
%    plot(u_data.data(node,1:chunk_size)); 
%    title(channelID_matrix(node));
%    xlim([0 chunk_size]);
%    ylim([-35 35]);
    
%  end
