/* *******************************************************
   Alpha Application v1.0
   University of Reading
   School of System Engineering
   Brain Embodiment Laboratory
   Johnathan Mayke Melo Neto
   Vitor de Carvalho Hazin
   January/2015
******************************************************* */

// Includes all the libraries, defines, global variables, etc.
#include "alpha_main.h"



/* *************************************************
            Main thread. All starts here!
The main purpose of the Main thread is:
> Initialize the synchronization objects (mutexes)
> Connect to Beta Application (TCP server)
> Open all the threads and wait for their finalization
**************************************************** */
void main()
{
   // Adjust size of console.
   HANDLE hStdout = GetStdHandle(STD_OUTPUT_HANDLE);
   SMALL_RECT windowSize = {0, 0, 80, 17};
   SetConsoleWindowInfo(hStdout, TRUE, &windowSize);    

   // Enable the Event Handler to detect if the user closed the console application
   if (SetConsoleCtrlHandler((PHANDLER_ROUTINE)ConsoleHandler,TRUE)==FALSE)
   {
	   // unable to install handler... 
	   // display message to the user
	   printf("Unable to install handler!\n");
	   exit(0);
   }

   // Create a writable file to store the firing rates for an offline analysis in MATLAB.
   fopen_s(&fp,"firing_rates.txt","w");


   // Creation of mutex objects.
   hLeftChannel = CreateMutex(NULL,FALSE,L"mutex_left_channel");
   hRightChannel = CreateMutex(NULL,FALSE,L"mutex_right_channel");
   hStimuliLeft = CreateMutex(NULL,FALSE,L"mutex_stimuli_left");
   hStimuliRight = CreateMutex(NULL,FALSE,L"mutex_stimuli_right");
   hTextFile = CreateMutex(NULL,FALSE,L"mutex_text_file");

   // Defines a title for the window.
   SetConsoleTitle(L"Alpha Application v1.0");   


   /* ***************************
   Screen to configure parameters
   ****************************** */
   configurationScreen();  


   // Socket variables.
   WSADATA     wsaData;
   SOCKET      s;
   SOCKADDR_IN ServerAddr;   
   char ipaddr[30];
   int  port = 5480, status = 0, count = 0;
   

   // Gets the IP address of server.
   system("cls");
   printf("ALPHA Communication Software\n\n");
   printf("\nInsert IP Address of BETA:\n>> ");
   scanf_s("%s", ipaddr, _countof(ipaddr));  


   // Initializes Winsock's usage (version 2.2).
   status = WSAStartup(MAKEWORD(2,2), &wsaData);
   if (status != 0) 
   {
	   printf("Winsock failed during initialization. Error = %d\n", WSAGetLastError());
	   WSACleanup();
       exit(0);
   }  


   // Build the address structure that will be used in the connection with the TCP server.
   ServerAddr.sin_family = AF_INET;
   ServerAddr.sin_port = htons(port);    
   ServerAddr.sin_addr.s_addr = inet_addr(ipaddr);


   // Main loop - creates the socket and establishes connection with TCP server (BETA application).
   while(1) 
   {
		 // Creates a new socket.
		 s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

		 // Checks if an error occurred.
		 if (s == INVALID_SOCKET)
		 {
			 status = WSAGetLastError();
			 time(&rawtime);
			 localtime_s(&tm_p, &rawtime);			 
			 printf("\n[%.2d/%.2d/%d %.2d:%.2d:%.2d] Network has failed. Error code = %d. Check Microsoft website for error description.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec,status);
			 
			 WSACleanup();
			 exit(0);
		 }
		 	   
		 // Establishes an initial connection with server (three trials).
		 if(count == 0)
		 {
			 time(&rawtime);
			 localtime_s(&tm_p, &rawtime);			 
			 printf("\n[%.2d/%.2d/%d %.2d:%.2d:%.2d] Connecting...\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
		 }
		
		 status = connect(s, (SOCKADDR *) &ServerAddr, sizeof(ServerAddr));
		 if (status == SOCKET_ERROR)
		 {
			if(count >= 5)
			{
				if(count == 5)
				{
					 time(&rawtime);
					 localtime_s(&tm_p, &rawtime);
					 printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Connecting (2nd attempt)...\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);					
				}

				if(count == 10)
				{
					time(&rawtime);
					localtime_s(&tm_p, &rawtime);
					printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Connecting (3rd attempt)...\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);					
				}

				if(count == 15)
				{
					time(&rawtime);
					localtime_s(&tm_p, &rawtime);
					printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] No connection has been made.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);					
					WSACleanup();
					system("PAUSE");
					exit(0);
				}
			}
			Sleep(1000);
			count++;
			continue;			
		 }		

		// Clears the screen to initialize the main console.
		system("cls");
		printf("ALPHA Communication Software\n\n");

		time(&rawtime);
		localtime_s(&tm_p, &rawtime);
		printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Connected.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);

		// Start the timer event.
		TimerEvent::StartTimer();

		/*****************************************************
		 Creates the threads and waits for their finalization.
		****************************************************** */
		OpenThreads(s); 

		break;   	
   }

   // End of loop. Closes socket, closes the synchronization objects, and closes the Winsock2 environment.
   fclose(fp);
   closesocket(s);
   CloseHandle(hLeftChannel);
   CloseHandle(hRightChannel);
   CloseHandle(hStimuliLeft);
   CloseHandle(hStimuliRight);
   CloseHandle(hTextFile);
   WSACleanup();

   printf("ALPHA Successfully Finished\n");
   system("PAUSE");
   exit(0);
}




/* *************************************************
    Function that creates all the threads.
**************************************************** */
void OpenThreads (int ClientSock)
{
	// Creation of receiving thread.
	hThreads[0] = (HANDLE) _beginthreadex(
			NULL,
			0,
			(CAST_FUNCTION)threadReceive,
			(LPVOID)ClientSock,
			0,
			(CAST_LPDWORD)&dwThreadId
	);

	// Creation of sending thread.
	hThreads[1] = (HANDLE) _beginthreadex(
			NULL,
			0,
			(CAST_FUNCTION)threadSend,
			(LPVOID)ClientSock,
			0,
			(CAST_LPDWORD)&dwThreadId
	);

	// Creation of thread that detects spikes.
	hThreads[2] = (HANDLE) _beginthreadex(
			NULL,
			0,
			(CAST_FUNCTION)threadDetectSpike,
			NULL,
			0,
			(CAST_LPDWORD)&dwThreadId
	);

	// Creation of thread that generates stimuli files.
	hThreads[3] = (HANDLE) _beginthreadex(
			NULL,
			0,
			(CAST_FUNCTION)threadGenerateStimuli,
			NULL,
			0,
			(CAST_LPDWORD)&dwThreadId
	);

	// Waits all threads to finish.	
	dwRet = WaitForMultipleObjects(NUM_THREADS, hThreads, TRUE, INFINITE);

	for (int i=0; i<NUM_THREADS; ++i) 
	{
		GetExitCodeThread(hThreads[i], &dwExitCode);
		CloseHandle(hThreads[i]);	// clears the reference of the object.			
	}
}






/* **********************************************************
     Thread that receives messages from BETA application
************************************************************* */
DWORD WINAPI threadReceive(LPVOID s)
{
	char buf[TAMBUFFER];  // buffer that receives the messages
	int status = 0;	

	// Infinite loop that the thread runs forever.
	while(1)
	{
		memset(buf, '\0', sizeof(buf));

		// Receives the message of the server.		
		status = recv((SOCKET)s, buf, sizeof(buf), 0);			
		
		// Checks for a receiving error.
		if( (status == SOCKET_ERROR) && (endApplication == false) )
		{ 	
			int erro = WSAGetLastError();
			if(erro == 10054 || erro == 10053) 
			{				
				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] BETA Remote Server has closed.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
				endApplication = true;				
				break;
			}
			else
			{
				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Error during data reception. Error code = %d. Check Microsoft website for error description.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec,erro);
				endApplication = true;				
				break;
			}				
		}	

		// Checks if it is time to terminate the thread.
		if(endApplication == true)
		{
			_endthreadex(0);
			return(0);
		}

		// Received message: Generate stimulus due to LEFT sensor.
		if(strcmp(buf,"3000") == 0)
		{
			// Increases the 'stimuliLeft' variable.
			WaitForSingleObject(hStimuliLeft,INFINITE);
			stimuliLeft++;
			ReleaseMutex(hStimuliLeft);
		}

		// Received message: Generate stimulus due to RIGHT sensor.
		else if(strcmp(buf,"4000") == 0)
		{
			// Increases the 'stimuliRight' variable.
			WaitForSingleObject(hStimuliRight,INFINITE);
			stimuliRight++;
			ReleaseMutex(hStimuliRight);
		}

		// Received message: Start/Stop button in BETA pressed.
		else if(strcmp(buf,"0000") == 0)
		{
			// Reverses the state of the 'bStart' variable.
			bStart = !(bStart);

			time(&rawtime);
			localtime_s(&tm_p, &rawtime);

			if(bStart == true)
			{
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Robot started by BETA's operator.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);	
			}
			else if(bStart == false)
			{
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Robot stopped by BETA's operator.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
			}
		}		
	}	

	_endthreadex(0);
	return(0);
}






/* *************************************************
    Thread that sends messages to BETA application
**************************************************** */
DWORD WINAPI threadSend(LPVOID s)
{
	// Sets timeout of send function into 2 seconds.
	DWORD timeout = 2000;
	setsockopt((SOCKET)s, SOL_SOCKET, SO_SNDTIMEO, (char *) &timeout, sizeof(timeout));

	// Infinite loop that the thread runs forever.
	while(1)
	{
		if(bStart == true)
		{
			// Convert leftFiringRate from int to char to send to BETA
			char leftFiringRateMSG[5]; 
			char varLeft[4];

			sprintf_s(varLeft, sizeof(varLeft), "%03d", leftFiringRate);

			// leftFiringRateMSG = "L _ _ _". The 3 last positions have the value of the left firing rate.
			leftFiringRateMSG[0] = 'L';
			leftFiringRateMSG[1] = varLeft[0];
			leftFiringRateMSG[2] = varLeft[1];
			leftFiringRateMSG[3] = varLeft[2];
			leftFiringRateMSG[4] = varLeft[3]; // null char

			// Sends LEFT firing rate.		
			int status = send((SOCKET)s, leftFiringRateMSG, sizeof(leftFiringRateMSG), 0);	

			// Checks for a sending error.
			if( (status == SOCKET_ERROR) && (endApplication == false) )
			{ 	
				int erro = WSAGetLastError();
				if( (erro != 10054) && (erro != 10053) ) 
				{				
					time(&rawtime);
					localtime_s(&tm_p, &rawtime);
					printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Error during data sending. Error code = %d. Check Microsoft website for error description.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec,erro);
					endApplication = true;					
					break;
				}				
			}	

			// Convert rightFiringRate from int to char to send to BETA
			char rightFiringRateMSG[5]; 
			char varRight[4];

			sprintf_s(varRight, sizeof(varRight), "%03d", rightFiringRate);

			// rightFiringRateMSG = "R _ _ _". The 3 last positions have the value of the right firing rate.
			rightFiringRateMSG[0] = 'R';
			rightFiringRateMSG[1] = varRight[0];
			rightFiringRateMSG[2] = varRight[1];
			rightFiringRateMSG[3] = varRight[2];
			rightFiringRateMSG[4] = varRight[3]; // null char


			// Sends RIGHT firing rate.	
			status = send((SOCKET)s, rightFiringRateMSG, sizeof(rightFiringRateMSG), 0);	
				
			// Checks for a sending error.
			if( (status == SOCKET_ERROR) && (endApplication == false) )
			{ 	
				int erro = WSAGetLastError();
				if( (erro != 10054) && (erro != 10053) ) 
				{				
					time(&rawtime);
					localtime_s(&tm_p, &rawtime);
					printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Error during data sending. Error code = %d. Check Microsoft website for error description.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec,erro);
					endApplication = true;					
					break;
				}				
			}	
		}
		
		// Checks if it is time to terminate the thread.
		if(endApplication == true)
		{
			_endthreadex(0);
			return(0);
		}
	}

	_endthreadex(0);
	return(0);
}







/* *************************************************
     Thread that detects spikes - NÃO VAI EXISTIR FUTURAMENTE POIS O TIMER SUBSTITUIRÁ SUA FUNÇÃO !!!
**************************************************** */
DWORD WINAPI threadDetectSpike(void)
{
	FILE * fp = NULL;
	char path[500];
	char var[6];
	char buffer[10];
	int i = 1;
		
	// Infinite loop that the thread runs forever.
	while(1)
	{
		// Receives a key of the keyboard.
		//keyboard = _getch();

		if(bStart == true)
		{						
			// Clears the variables 'path' and 'var'.
			memset(path,0,strlen(path));
			memset(var,0,strlen(var));	

			// Updates the file name.
			_itoa_s(i,var,6,10);	

			strcat_s(path,sizeof(path),"D:\\Rodrigo\\Teste16 rack matlab C 25-06-2015\\Matlab\\"); // change de filepath accordingly				
			strcat_s(path,sizeof(path),var);				
			strcat_s(path,sizeof(path),"_data.txt");	

			printf("Searching for the file: %s\n",path);

			// Checks if new spike file was generated.
			fopen_s(&fp, path, "r");		
			
			if(fp == NULL) // file does NOT exist, spike not detected 
			{
				printf("No new files found!\n\n");
				Sleep(1000); // RETIRAR DEPOIS !!!!
			}

			else // file does exist, spike detected!
			{
				// Read the content of the txt file
				fread(buffer, 1, 10, fp); 

				// Detected which channel was fired
				if(buffer[0] == '1') // Bit 1
			    {
					// Increases the 'leftChannel' counter.
					WaitForSingleObject(hLeftChannel,INFINITE);	
					leftChannel++;
					ReleaseMutex(hLeftChannel);

					if(buffer[3] == '_')
					{
						printf("Channel %c detected!\n\n",buffer[2]); 
					}
					else
					{
						printf("Channel %c%c detected!\n\n",buffer[2],buffer[3]);
					}					 
			    }
				
				else if(buffer[0] == '2') // Bit 1
			    {
					// Increases the 'rightChannel' counter.
					WaitForSingleObject(hRightChannel,INFINITE);	
					rightChannel++;
					ReleaseMutex(hRightChannel);

				    if(buffer[3] == '_')
					{
						printf("Channel %c detected!\n\n",buffer[2]); 
					}
					else
					{
						printf("Channel %c%c detected!\n\n",buffer[2],buffer[3]);
					}
			    }	   
				
				// Increments the file counter.
				i++; 

				// Close file.
				fclose(fp);
			}			
						
			/*
			// Checks which key was pressed.
			if( (char) keyboard == KEY_LEFT )
			{
				// Increases the 'leftChannel' counter.
				WaitForSingleObject(hLeftChannel,INFINITE);	
				leftChannel++;
				ReleaseMutex(hLeftChannel);
			}	

			else if( (char) keyboard == KEY_RIGHT )
			{
				// Increases the 'rightChannel' counter.
				WaitForSingleObject(hRightChannel,INFINITE);	
				rightChannel++;
				ReleaseMutex(hRightChannel);
			}	
			*/

			// Checks if it is time to terminate the thread.
			if(endApplication == true)
			{
				_endthreadex(0);
				return(0);
			}
		}
	}
}





/* *************************************************
         Thread that generats stimuli files
**************************************************** */
DWORD WINAPI threadGenerateStimuli(void)
{
	// Infinite loop that the thread runs forever.
	while(1)
	{
		// If 'stimuliLeft' is positive, generates stimuli file.				
		if(stimuliLeft > 0)
		{
			// Generates the stimuli file due to LEFT sensor.
			time(&rawtime);
			localtime_s(&tm_p, &rawtime);
			printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] LEFT sensor detected obstacle! Stimuli File sent to MEA.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
			
			// Write in the text file the relevant informations for an offline analysis in MATLAB.
			WaitForSingleObject(hTextFile,INFINITE);
			fprintf(fp, "%d %d %d %d\n" , leftFiringRate, rightFiringRate, stimuliLeft, stimuliRight);
			ReleaseMutex(hTextFile);			

			// Decreases the 'stimuliLeft' variable.
			WaitForSingleObject(hStimuliLeft,INFINITE);
			stimuliLeft--;		
			ReleaseMutex(hStimuliLeft);
		}
		

		// If 'stimuliRight' is positive, generates stimuli file.			
		if(stimuliRight > 0)
		{
			// Generates the stimuli file due to RIGHT sensor.
			time(&rawtime);
			localtime_s(&tm_p, &rawtime);
			printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] RIGHT sensor detected obstacle! Stimuli File sent to MEA.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
			
			// Write in the text file the relevant informations for an offline analysis in MATLAB.
			WaitForSingleObject(hTextFile,INFINITE);
			fprintf(fp, "%d %d %d %d\n" , leftFiringRate, rightFiringRate, stimuliLeft, stimuliRight);
			ReleaseMutex(hTextFile);

			// Decreases the 'stimuliRight' variable.
			WaitForSingleObject(hStimuliRight,INFINITE);	
			stimuliRight--;		
			ReleaseMutex(hStimuliRight);
		}
		
		
		// Check if it is time to terminate the thread.
		if(endApplication == true)
		{
			_endthreadex(0);
			return(0);
		}		
	}	
}








/* ***********************************************************************************
								  SECONDARY FUNCTIONS
************************************************************************************** */


/* *************************************************************
	    Creates a configuration screen to change parameters
**************************************************************** */
void configurationScreen(void)
{
	while(1)
	{
		system("cls");
		printf("ALPHA Communication Software\n\n");
		//printf("CONFIGURATIONS:\n\n");

		printf("[ ENTER ] Start application\n");

		printf("\nSelect an option >> ");

		// Receives a key of the keyboard.
		keyboard = _getch(); 

		// Checks which key was pressed.
		if( (char)keyboard == ENTER )
		{
			break;
		}

		else
		{
			printf("Invalid option.\n\n");
			Sleep(1000);
		}
	
	}
}







/* *****************************************************						
					  TIMER EVENT
	When enabled, the timer will be triggered every
	1 second to check how many times the 'leftChannel'
	and 'rightChannel' were fired, so we can have the
	firing rate of these channels.
********************************************************/
void TimerEvent::StartTimer()
{
   // Create a new Timer with Interval set to 10 seconds.
   aTimer = gcnew System::Timers::Timer( 10000 );
  
   // Hook up the Elapsed event for the timer.
   aTimer->Elapsed += gcnew ElapsedEventHandler( TimerEvent::OnTimedEvent );

   // Set the Interval to 1 second (1000 milliseconds).
   aTimer->Interval = 1000;
   aTimer->Enabled = true;

   // If the timer is declared in a long-running method, use
   // KeepAlive to prevent garbage collection from occurring
   // before the method ends.
   GC::KeepAlive(aTimer);
}

void TimerEvent::OnTimedEvent( Object^ source, ElapsedEventArgs^ e )
{
	if(endApplication == false)
	{
	   // Store how many times the LEFT channel was fired within 1 second.
	   WaitForSingleObject(hLeftChannel,INFINITE);
	   leftFiringRate = leftChannel;
	   leftChannel = 0;
	   ReleaseMutex(hLeftChannel);

	   // Store how many times the RIGHT channel was fired within 1 second.
	   WaitForSingleObject(hRightChannel,INFINITE);
	   rightFiringRate = rightChannel;
	   rightChannel = 0;
	   ReleaseMutex(hRightChannel);

	   // DEBUG TO VERIFY THE FIRING RATES RELATED TO THE LEFT WHEEL AND RIGHT WHEEL.
	   printf("L = %d | R = %d\n", leftFiringRate, rightFiringRate); 

	   // Write in the text file the relevant informations for an offline analysis in MATLAB.
	   WaitForSingleObject(hTextFile,INFINITE);
	   fprintf(fp, "%d %d %d %d\n" , leftFiringRate, rightFiringRate, stimuliLeft, stimuliRight);
	   ReleaseMutex(hTextFile);
	}
}

TimerEvent::~TimerEvent(){} // Destructor of the TimerEvent Class




