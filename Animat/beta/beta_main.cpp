/* *******************************************************
   Beta Application v1.0
   University of Reading
   School of System Engineering
   Brain Embodiment Laboratory
   Johnathan Mayke Melo Neto
   January/2015
******************************************************* */

// Includes all the libraries, defines, global variables, etc.
#include "beta_main.h"

/* *************************************************
             Main thread. All starts here!
The main purpose of the Main thread is:
> Initialize the synchronization objects (mutexes)
> Configure the user settings (e.g. robot speed, etc.)
> Connect to V-REP simulation
> Connect to Alpha Application (TCP client)
> Open all the threads and wait for their finalization
**************************************************** */
int main(int argc, char *argv[])
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
		return(-1);
	}

	// Creation of mutex objects.
    hLeftWheel = CreateMutex(NULL,FALSE,L"mutex_left_wheel");
	hRightWheel = CreateMutex(NULL,FALSE,L"mutex_right_wheel");
    hDoStimuliLeft = CreateMutex(NULL,FALSE,L"mutex_doStimuli_left");
	hDoStimuliRight = CreateMutex(NULL,FALSE,L"mutex_doStimuli_right");
	hButton = CreateMutex(NULL,FALSE,L"mutex_button");
	hSim = CreateMutex(NULL,FALSE,L"mutex_sim");

	// Defines a title for the window.
	SetConsoleTitle(L"Beta Application v1.0");		

	
	/* ***************************
	Screen to configure parameters
	****************************** */
	configurationScreen();
	

	/* ************************************
	Connection with simulation V-REP server
    *************************************** */
	int portNb = atoi(argv[1]);	
	clientID = connectSimulation(clientID, portNb);	


	/* ********************************************
	Socket Initialization to communicate with APLHA
	*********************************************** */
	SOCKET ServSock = NULL;
	SOCKET ClientSock;
    SOCKADDR_IN ServerAddress ;
	SOCKADDR_IN ClientAddress;	
	int clntLen;
	memset(&ServerAddress, '\0', sizeof(ServerAddress));

	ServSock = socketInitializationALPHA(ServSock, ServerAddress);
	

	/* **********************************************
	       Connection with ALPHA application.
	Waits indefinitely by the contact of ALPHA client
	************************************************* */
    while(1)
    {
		clntLen = sizeof(ClientAddress);

		time(&rawtime);
		localtime_s(&tm_p, &rawtime);
		printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Waiting for ALPHA connection request...\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
		
		// Accepts connection with client.
		ClientSock = accept(ServSock, (struct sockaddr *) &ClientAddress, &clntLen);
		if( ClientSock == INVALID_SOCKET )
		{
			InterrompeErro("accept() failed");
		}	

		// Inform the selected configurations.
		system("cls");
		printf("BETA Communication Software\n\n");

		time(&rawtime);
		localtime_s(&tm_p, &rawtime);		
		printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Connected. Press ENTER to start the robot.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
		 		
		/*****************************************************
		 Creates the threads and waits for their finalization.
		****************************************************** */
		OpenThreads(ClientSock,clientID); 
		
		// Close connecting socket (client).
		closesocket(ClientSock);
		break;
	}
	
	// Close listening socket, simulation socket, and handles.	
	closesocket(ServSock);
	WSACleanup();
	CloseHandle(hLeftWheel);
	CloseHandle(hRightWheel);
    CloseHandle(hDoStimuliLeft);
	CloseHandle(hDoStimuliRight);
	CloseHandle(hButton);
	CloseHandle(hSim);
	simxFinish((int)clientID);

	printf("BETA Successfully Finished\n");
	system("PAUSE");	
	return EXIT_SUCCESS;
}



/* *************************************************
    Function that creates all the threads.
**************************************************** */
void OpenThreads (int ClientSock, int clientID)
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
		
	// Creation of thread that commands the robot.
	hThreads[2] = (HANDLE) _beginthreadex(
			NULL,
			0,
			(CAST_FUNCTION)threadTurn,
			(LPVOID)clientID,
			0,
			(CAST_LPDWORD)&dwThreadId
	);

	// Creation of thread that receives robot's sensor values.
	hThreads[3] = (HANDLE) _beginthreadex(
			NULL,
			0,
			(CAST_FUNCTION)threadSensor,
			(LPVOID)clientID,
			0,
			(CAST_LPDWORD)&dwThreadId
	);

	// Creation of thread that reads the keyboard.
	hThreads[4] = (HANDLE) _beginthreadex(
			NULL,
			0,
			(CAST_FUNCTION)threadReadKeyboard,
			NULL,
			0,
			(CAST_LPDWORD)&dwThreadId
	);

	// Creation of thread that processes the electrophysiological signals and translates them into motor commands.
	hThreads[5] = (HANDLE) _beginthreadex(
			NULL,
			0,
			(CAST_FUNCTION)threadSpeedDecoding,
			NULL,
			0,
			(CAST_LPDWORD)&dwThreadId
	);

	// Waits the finalization of all threads except threadReadKeyboard.
	dwRet = WaitForSingleObject(hThreads[0], INFINITE);
	dwRet = WaitForSingleObject(hThreads[1], INFINITE);
	dwRet = WaitForSingleObject(hThreads[2], INFINITE);
	dwRet = WaitForSingleObject(hThreads[3], INFINITE);
	dwRet = WaitForSingleObject(hThreads[5], INFINITE);

	for (int i=0; i<NUM_THREADS; ++i) 
	{
		GetExitCodeThread(hThreads[i], &dwExitCode);
		CloseHandle(hThreads[i]);	// clears the reference of the object.
	}			
}




/* **********************************************************
     Thread that receives messages from APLHA application
************************************************************* */
DWORD WINAPI threadReceive(LPVOID sClientSock)
{
	char buf[TAMBUFFER]; // buffer that receives the messages
	char aux[4];
	int status = 0;	
	
	// Infinite loop that the thread runs forever.
	while(1)
	{		
		memset(buf, '\0', sizeof(buf));
		memset(aux, '\0', sizeof(aux));

		// Receives the message of the client.
		status = recv((SOCKET)sClientSock, buf, sizeof(buf), 0);			

		// Checks for a receiving error.
		if( (status == SOCKET_ERROR) && (endApplication == false) )
		{ 
			int erro = WSAGetLastError();
			if(erro == 10054) 
			{				
				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] ALPHA Remote Client has closed.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
				endApplication = true; // sets the flag to end all threads
				break;
			}
			else
			{
				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Error during data reception. Error code = %d. Check Microsoft website for error description.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec,erro);
				endApplication = true; // sets the flag to end all threads
				break;
			}
		}

		// Checks if it is time to terminate the thread.
		if(endApplication == true)
		{
			_endthreadex(0);
			return(0);
		}

		// Fill 'aux' with the firing rate information
		aux[0] = buf[1]; // firing rate value
		aux[1] = buf[2]; // firing rate value
		aux[2] = buf[3]; // firing rate value
		aux[3] = buf[4]; // null

		// Check if the received message is LEFT FIRING RATE.
		if(buf[0] == 'L')
		{			
			// Store the LEFT firing rate value.
			leftFiringRate = atoi(aux);
		}

		// Check if the received message is RIGHT FIRING RATE.
		else if(buf[0] == 'R')
		{
			// Store the RIGHT firing rate value.
			rightFiringRate = atoi(aux);
		}		
	}	

	_endthreadex(0);
	return(0);
}



/* *************************************************
    Thread that sends messages to APLHA application
**************************************************** */
DWORD WINAPI threadSend(LPVOID sClientSock)
{	
	// Sets timeout of send function into 2 seconds.
	DWORD timeout = 2000;
	setsockopt((SOCKET)sClientSock, SOL_SOCKET, SO_SNDTIMEO, (char *) &timeout, sizeof(timeout));
	
	const char stimuliLeft_MSG[TAMBUFFER] = "3000";  // left sensor detected obstacle, so generate stimulus
	const char stimuliRight_MSG[TAMBUFFER] = "4000";  // right sensor detected obstacle, so generate stimulus
	const char start[TAMBUFFER] = "0000";    // start alpha
	int status;

	// Infinite loop that the thread runs forever.
	while(1)
	{
		/**************************************
		    SEND MESSAGE DUE TO LEFT SENSOR
		*************************************** */
		// If 'doStimuliLeft' is positive, sends message to stimulate the MEA.		
		if(doStimuliLeft > 0)
		{
			// Sends message.
			status = send((SOCKET)sClientSock, stimuliLeft_MSG, sizeof(stimuliLeft_MSG), 0);  

			// Checks for a sending error.
			if( (status == SOCKET_ERROR) && (endApplication == false) )
			{ 		
				int erro = WSAGetLastError();
				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Error during data sending. Error code = %d. Check Microsoft website for error description.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec,erro);
				endApplication = true; // sets the flag to end all threads
				break;
			}			

			// Decreases the 'doStimuli' variable.
			WaitForSingleObject(hDoStimuliLeft,INFINITE);
			doStimuliLeft--;		
			ReleaseMutex(hDoStimuliLeft);				
		}
		


		/**************************************
		    SEND MESSAGE DUE TO RIGHT SENSOR
		*************************************** */
		// If 'doStimuliRight' is positive, sends message to stimulate the MEA.		
		if(doStimuliRight > 0)
		{
			// Sends message.
			status = send((SOCKET)sClientSock, stimuliRight_MSG, sizeof(stimuliRight_MSG), 0);  

			// Checks for a sending error.
			if( (status == SOCKET_ERROR) && (endApplication == false) )
			{ 		
				int erro = WSAGetLastError();
				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Error during data sending. Error code = %d. Check Microsoft website for error description.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec,erro);
				endApplication = true; // sets the flag to end all threads
				break;
			}		

			// Decreases the 'doStimuli' variable.
			WaitForSingleObject(hDoStimuliRight,INFINITE);
			doStimuliRight--;		
			ReleaseMutex(hDoStimuliRight);			
		}
		


		/****************************************
		    SEND MESSAGE DUE TO BUTTON PRESSED
		***************************************** */
		// If button ENTER or ESC are pressed, sends message to APLHA.		
		if(buttonPressed == true)
		{
			// Sends message.
			status = send((SOCKET)sClientSock, start, sizeof(start), 0);  

			// Checks for a sending error.
			if( (status == SOCKET_ERROR) && (endApplication == false) )
			{ 		
				int erro = WSAGetLastError();
				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Error during data sending. Error code = %d. Check Microsoft website for error description.\n\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec,erro);
				endApplication = true; // sets the flag to end all threads
				break;
			}	

			// Resets the 'buttonPressed' variable.
			WaitForSingleObject(hButton,INFINITE);
			buttonPressed = false;
			ReleaseMutex(hButton);
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
	   Thread that sends commands to the robot
**************************************************** */
DWORD WINAPI threadTurn(LPVOID clientID)
{		
	simxFloat motorSpeeds[2];

	// Initial state: robot stopped
	motorSpeeds[0] = 0;
	motorSpeeds[1] = 0;

	// Gets the handles of the robot's motors of simulation.
	WaitForSingleObject(hSim,INFINITE);
	simxGetObjectHandle((int)clientID, "KJunior_motorLeft", &leftMotorHandle, simx_opmode_oneshot_wait);
	simxGetObjectHandle((int)clientID, "KJunior_motorRight", &rightMotorHandle, simx_opmode_oneshot_wait);
	ReleaseMutex(hSim);			

	// Infinite loop that the thread runs forever.
	while( simxGetConnectionId((int)clientID) != -1 )
	{
		// ENTER button pressed.
		if(startRobot == true)
		{
			// Set the speed of the LEFT wheel.
			WaitForSingleObject(hLeftWheel,INFINITE);
			motorSpeeds[0] = leftWheel;
			ReleaseMutex(hLeftWheel);

			// Set the speed of the RIGHT wheel.
			WaitForSingleObject(hRightWheel,INFINITE);
			motorSpeeds[1] = rightWheel;
			ReleaseMutex(hRightWheel);

			// Sends command to simulation.
			WaitForSingleObject(hSim,INFINITE);
			simxSetJointTargetVelocity((int)clientID, leftMotorHandle, motorSpeeds[0], simx_opmode_oneshot);
			simxSetJointTargetVelocity((int)clientID, rightMotorHandle, motorSpeeds[1], simx_opmode_oneshot);
			ReleaseMutex(hSim);	
		}

		// ESC button pressed.
		else if(startRobot == false)
		{
			// Stop robot.
			if(spacePressed == false)
			{
				motorSpeeds[0] = 0;
				motorSpeeds[1] = 0;

				// Sends command to simulation.
				WaitForSingleObject(hSim,INFINITE);
				simxSetJointTargetVelocity((int)clientID, leftMotorHandle, motorSpeeds[0], simx_opmode_oneshot);	
				simxSetJointTargetVelocity((int)clientID, rightMotorHandle, motorSpeeds[1], simx_opmode_oneshot);
				ReleaseMutex(hSim);
			}

			// Go backwards for 2 seconds.
			else if(spacePressed == true) 
			{
				DWORD start = GetTickCount();
				while(GetTickCount() - start < 2000)
				{
					motorSpeeds[0] = -w_backwards;
					motorSpeeds[1] = -w_backwards;

					// Sends command to simulation.
					WaitForSingleObject(hSim,INFINITE);
					simxSetJointTargetVelocity((int)clientID, leftMotorHandle, motorSpeeds[0], simx_opmode_oneshot);	
					simxSetJointTargetVelocity((int)clientID, rightMotorHandle, motorSpeeds[1], simx_opmode_oneshot);
					ReleaseMutex(hSim);
				}

				WaitForSingleObject(hButton,INFINITE);
				spacePressed = false;
				ReleaseMutex(hButton);
			}			
		}

		// Checks if it is time to terminate the thread.
		if(endApplication == true)
		{			
			// Sends command to simulation to stop the simulation.
			WaitForSingleObject(hSim,INFINITE);			
			simxStopSimulation((int)clientID,simx_opmode_oneshot);
			Sleep(1000);
			ReleaseMutex(hSim);		
			_endthreadex(0);
			return(0);
		}
	}

	_endthreadex(0);
	return(0);
}



/* *************************************************
	      Thread that reads the robot sensors
**************************************************** */
DWORD WINAPI threadSensor(LPVOID clientID)
{	
	// Sensor parameters
	int maxValue[5] = {-1,-1,-1,-1,-1};  // maximum values that the sensor can read when detect an obstacle
	int minValue[5] = {40,40,40,40,40};   // minimum value that the sensor can read (when the robot is in the front of a wall)
	int periodStimulation[5] = {10000,10000,10000,10000,10000}; // period of stimulation calculated by each sensor.

	/* 
	   Variable to identify the obstacle location.
	   sensorOn[0] -> Left sensor
	   sensorOn[1] -> Left-center sensor
	   sensorOn[2] -> Center sensor
	   sensorOn[3] -> Right-center sensor
	   sensorOn[4] -> Right sensor
	*/
	bool sensorOn[5] = {false,false,false,false,false};

	// Simulation variables.
	int code = 0;
	char handleString[25];
	simxFloat detectedPoint[3];
	simxUChar sensorTrigger = 0;
	int proxSensorHandles[5];
	char buf[3];

	/* 
	   Get the handles of the sensors.
	   proxSensorHandles[0] -> Left sensor
	   proxSensorHandles[1] -> Left-center sensor
	   proxSensorHandles[2] -> Center sensor
	   proxSensorHandles[3] -> Right-center sensor
	   proxSensorHandles[4] -> Right sensor
	*/
	WaitForSingleObject(hSim,INFINITE);
	for(int i = 0; i < 5; i++)
	{		
		memset(buf, '\0', strlen(buf));
		memset(handleString, '\0', strlen(handleString));
		sprintf_s(buf, sizeof(buf), "%d", i+1);
		strcat_s(handleString,sizeof(handleString),"KJunior_proxSensor");
		strcat_s(handleString,sizeof(handleString),buf);
		simxGetObjectHandle((int)clientID,handleString,&proxSensorHandles[i],simx_opmode_oneshot_wait);
	}
	ReleaseMutex(hSim);	

	// Infinite loop that the thread runs forever.
	while( simxGetConnectionId((int)clientID) != -1 )
	{
		// ENTER button pressed.
		if(startRobot == true)
		{
			/***********************************
				    SENSORS DETECTION
			************************************ */
			for(int i = 0; i < 5; i++)
			{
				sensorTrigger = 0;
				periodStimulation[i] = 10000;

				// Reads the sensor's value.
				WaitForSingleObject(hSim,INFINITE);
				code = simxReadProximitySensor((int)clientID,proxSensorHandles[i],&sensorTrigger,detectedPoint,NULL,NULL,simx_opmode_streaming);
				ReleaseMutex(hSim);
				
				if(code == simx_return_ok)
				{			
					// Checks if the sensor 'i' has found an obstacle.
					if(sensorTrigger != 0) // Sensor 'i' has found an obstacle!
					{
						sensorOn[i]	 = true;

						// Proportional Coding - Martinoia, 2007.						
						if(binaryCoding == false)
						{
							// Calculates the distance between the sensor 'i' and the obstacle.
							int point = (int) 1000 * sqrt( (detectedPoint[0]*detectedPoint[0])+(detectedPoint[1]*detectedPoint[1])+(detectedPoint[2]*detectedPoint[2]) );
							
							// Update the maximum value of the sensor 'i' (if exists).
							if(point > maxValue[i])
							{
								maxValue[i] = point;
							}

							// Update the minimum value of the sensor 'i' (if exists).
							if(point < minValue[i])
							{
								minValue[i] = point;
							}


							// Safe verification to avoid division by zero
							if(minValue[i] != maxValue[i])
							{
								// Equation that calculates the frequency of the stimuli based on the sensor's value and of the max stimuli frequency set by the operator. 
								// The closer the robot is of the obstacle, the higher the frequency of the stimuli (and vice-versa).
								periodStimulation[i] = ( (max_period_stimulus - min_period_stimulus) * point + min_period_stimulus * maxValue[i] 
									- max_period_stimulus * minValue[i] ) / (maxValue[i] - minValue[i]);  
								
								// Safe verification to avoid high stimulus frequency.
								if(periodStimulation[i] <= min_period_stimulus)
								{
									periodStimulation[i] = min_period_stimulus;
								}

								// Safe verification to avoid low stimulus frequency.
								if(periodStimulation[i] >= max_period_stimulus)
								{
									periodStimulation[i] = max_period_stimulus;
								}
							}
							else
							{
								periodStimulation[i] = max_period_stimulus;
							}
						}
					}
					else // Sensor 'i' has NOT found an obstacle!
					{
						sensorOn[i] = false;
					}
				}
			}

			/* 
				IDENTIFY WHICH STIMULUS (LEFT or RIGHT) WE SHOULD SEND TO ALPHA APPLICATION.
			*/
			

			// It has found an obstacle on the front due to the CENTER SENSOR
			if( (sensorOn[0] == false && sensorOn[1] == false && sensorOn[2] == true && sensorOn[3] == false && sensorOn[4] == false)
				  || (sensorOn[0] == false && sensorOn[1] == true && sensorOn[2] == true && sensorOn[3] == true && sensorOn[4] == false)
				    || (sensorOn[0] == true && sensorOn[1] == true && sensorOn[2] == true && sensorOn[3] == true && sensorOn[4] == true) )
			{
				// do something due to the center obstacle
				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] CENTER sensor detected obstacle!\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
			
				// Proportional Coding - Martinoia, 2007.
				if(binaryCoding == false)
				{						
					int period = min5(periodStimulation[0],periodStimulation[1],periodStimulation[2],periodStimulation[3],periodStimulation[4]);
					printf("Period Stimulation: %d\n\n", period);
					Sleep(period); 
				}
			}

			// It has found an obstacle on the left due to the LEFT SENSORS
			else if( (sensorOn[0] == true || sensorOn[1] == true) && (sensorOn[4] == false) )
			{
				// Increases the 'doStimuliLeft' variable.
				WaitForSingleObject(hDoStimuliLeft,INFINITE);		
				doStimuliLeft++;   
				ReleaseMutex(hDoStimuliLeft);	

				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] LEFT sensor detected obstacle!\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
					
				// Proportional Coding - Martinoia, 2007.
				if(binaryCoding == false)
				{						
					int period = min2(periodStimulation[0],periodStimulation[1]);
					printf("Period Stimulation: %d\n\n", period);
					Sleep(period); 
				}			
			}

			// It has found an obstacle on the right due to the RIGHT SENSORS
			else if( (sensorOn[3] == true || sensorOn[4] == true) && (sensorOn[0] == false) )
			{
				// Increases the 'doStimuliRight' variable.
				WaitForSingleObject(hDoStimuliRight,INFINITE);		
				doStimuliRight++;   
				ReleaseMutex(hDoStimuliRight);

				time(&rawtime);
				localtime_s(&tm_p, &rawtime);
				printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] RIGHT sensor detected obstacle!\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);					
					
				// Proportional Coding - Martinoia, 2007.
				if(binaryCoding == false)
				{						
					int period = min2(periodStimulation[3],periodStimulation[4]);
					printf("Period Stimulation: %d\n\n", period);
					Sleep(period); 
				}			
			}

			// Binary Coding - Martinoia, 2007.
			if(binaryCoding == true)
			{
				Sleep(period_binary);   
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
	      Thread that reads the keyboard
**************************************************** */
DWORD WINAPI threadReadKeyboard(LPVOID)
{	
	while(1)
	{
		// Receives a key of the keyboard.
		keyboard = _getch();  

		// Checks which key was pressed.
		switch ( (char)keyboard )
		{
			case ESC:		
				if(startRobot == true)
				{
					startRobot = false;					
					
					WaitForSingleObject(hButton,INFINITE);
					buttonPressed = true;
					ReleaseMutex(hButton);

					time(&rawtime);
					localtime_s(&tm_p, &rawtime);
					printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Robot stopped by operator. ENTER: start | SPACE: go back\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);				
				}
				break;

			case ENTER:

				// DEBUG to check the speed of the wheels!!!
				printf("W_L = %d | W_R = %d\n",leftWheel,rightWheel);

				if( (startRobot == false) && (spacePressed == false) )
				{
					startRobot = true;

					WaitForSingleObject(hButton,INFINITE);
					buttonPressed = true;
					ReleaseMutex(hButton);
		
					time(&rawtime);
					localtime_s(&tm_p, &rawtime);
					printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Robot started by operator. Press ESC to stop it.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);				
				}
				break;

			case SPACE:
				if( (startRobot == false) && (spacePressed == false) )
				{
					WaitForSingleObject(hButton,INFINITE);
					spacePressed = true;
					ReleaseMutex(hButton);

					time(&rawtime);
					localtime_s(&tm_p, &rawtime);
					printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Robot going backwards. ENTER: restart | SPACE: go back.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);				
				}
				break;
		}
		
		// Checks if it is time to terminate the thread.
		if(endApplication == true)
		{
			_endthreadex(0);
			return(0);
		}
	}
}


/* ***************************************************************************************************
     Thread that processes the electrophysiological signals and translates them into motor commands.
****************************************************************************************************** */
DWORD WINAPI threadSpeedDecoding(void)
{		
	switch (decodingMethod)
	{
		/************************************************
			DISCRETE DECODING METHOD - TURN LEFT/RIGHT
		*************************************************/
		case 1:				
			discreteDecoding();
			break;

		/*****************************************************
			WINNER-TAKES-ALL METHOD (WTA) - MARTINOIA, 2007
		******************************************************/
		case 2:
			WTADecoding();
			break;

		/*****************************************************			
			SPACE TO INSERT ANOTHER DECODIND METHOD
		******************************************************/
		//case 3:
	}
		
	_endthreadex(0);
	return(0);
}




/* **********************************************************************
	                      SECONDARY FUNCTIONS
************************************************************************* */




/* *************************************************************
	    Creates a configuration screen to change parameters
**************************************************************** */
void configurationScreen(void)
{
	while(1)
	{
		system("cls");
		printf("BETA Communication Software\n\n");
		printf("CONFIGURATIONS:\n\n");

		printf("[ ENTER ] Start application\n");

		if(decodingMethod == 1)
		{
			printf("[   M   ] Speed decoding method | Discrete commands\n");
		}
		else if(decodingMethod == 2)
		{
			printf("[   M   ] Speed decoding method | Winner-Takes-All (C_L = %.2f | C_R = %.2f)\n", C_L, C_R);
		}

		printf("[   S   ] Maximum robot speed | %d rad/s\n", w_0);

		if(binaryCoding == true)
		{
			printf("[   E   ] External sensory input patterns | Binary Coding (%d ms)\n", period_binary);
		}
		else if(binaryCoding == false)
		{
			printf("[   E   ] External sensory input patterns | Proportional Coding (Min: %d ms)\n", min_period_stimulus);
		}

		printf("\nSelect an option >> ");

		// Receives a key of the keyboard.
		keyboard = _getch(); 

		// Checks which key was pressed.
		if( (char)keyboard == ENTER )
		{
			break;
		}

		else if( (char)keyboard == 'm' || (char)keyboard == 'M' )
		{	
			configurationDecodingMethod();			
		}

		else if( (char)keyboard == 's' || (char)keyboard == 'S' )
		{	
			configurationMaximumSpeedRobot();			
		}

		else if( (char)keyboard == 'e' || (char)keyboard == 'E' )
		{		
			configurationSensoryPatterns();			
		}

		else
		{
			printf("Invalid option.\n\n");
			Sleep(1000);
		}	
	}
}

/* *****************************************************
	        Changes the speed decoding method
******************************************************** */
void configurationDecodingMethod(void)
{
	while(1)
	{				
		system("cls");
		printf("BETA Communication Software\n\n");
		printf("CONFIGURATIONS -  Decoding Method\n\n");
		printf("[  D  ] Discrete commands (left/right)\n");
		printf("[  W  ] Winner-Takes-All (Martinoia, 2007)\n");
		printf("[ ESC ] Back\n\n");
		printf("Select an option >> ");

		// Receives a key of the keyboard.
		keyboard = _getch();		

		// Checks which key was pressed.
		if( (char)keyboard == 'd' || (char)keyboard == 'D' )
		{
			decodingMethod = 1;
			break;
		}

		else if( (char)keyboard == 'w' || (char)keyboard == 'W' )
		{
			decodingMethod = 2;
			adjustParameters();
			break;
		}

		else if( (char)keyboard == ESC )
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
	      Adjust the Winner-Takes-All Parameters
******************************************************** */
void adjustParameters(void)
{
	char str[10];

	// LEFT WHEEL PARAMETER
	while(1)
	{
		system("cls");
		printf("BETA Communication Software\n\n");
		printf("CONFIGURATIONS -  Winner-Takes-All Parameters\n");
		printf("Type the coefficient of the LEFT WHEEL and press ENTER >> ");

		memset(str, '\0',  sizeof(str));
		scanf_s("%s", str, _countof(str));

		if(sscanf_s(str, "%f", &C_L) != 0) // checks if the input is float type
		{
			if(w_0 > 0)
			{
				break; // valid option
			}
			else
			{
				printf("Invalid option.\n\n");
				Sleep(1000);
			}
		}
		else
		{
			printf("Invalid option.\n\n");
			Sleep(1000);
		}
	}

	// RIGHT WHEEL PARAMETER
	while(1)
	{
		system("cls");
		printf("BETA Communication Software\n\n");
		printf("CONFIGURATIONS -  Winner-Takes-All Parameters\n");
		printf("Type the coefficient of the RIGHT WHEEL and press ENTER >> ");

		memset(str, '\0',  sizeof(str));
		scanf_s("%s", str, _countof(str));

		if(sscanf_s(str, "%f", &C_R) != 0) // checks if the input is float type
		{
			if(w_0 > 0)
			{
				break; // valid option
			}
			else
			{
				printf("Invalid option.\n\n");
				Sleep(1000);
			}
		}
		else
		{
			printf("Invalid option.\n\n");
			Sleep(1000);
		}
	}
}



/* *****************************************************
	        Changes the maximum robot speed
******************************************************** */
void configurationMaximumSpeedRobot(void)
{
	char str[10];
	while(1)
	{				
		system("cls");
		printf("BETA Communication Software\n\n");
		printf("CONFIGURATIONS -  Maximum robot speed (rad/s)\n");
		printf("Choose a speed and press ENTER >> ");
		
		memset(str, '\0',  sizeof(str));
		scanf_s("%s", str, _countof(str));

		if(sscanf_s(str, "%d", &w_0) != 0) // checks if the input is int type
		{
			if(w_0 > 0)
			{
				break; // valid option
			}
			else
			{
				printf("Invalid option.\n\n");
				Sleep(1000);
			}
		}
		else
		{
			printf("Invalid option.\n\n");
			Sleep(1000);
		}
	}
}



/* *****************************************************
	    Changes the external sensory input patterns
******************************************************** */
void configurationSensoryPatterns(void)
{
	char str[10];
	bool exit = false;
	while(1)
	{
		system("cls");
		printf("BETA Communication Software\n\n");
		printf("CONFIGURATIONS -  External sensory input patterns\n\n");
		printf("[  P  ] Proportional coding\n");
		printf("[  B  ] Binary coding\n");
		printf("[ ESC ] Back\n\n");
		printf("Select an option >> ");
		
		// Receives a key of the keyboard.
		keyboard = _getch();

		// Checks which key was pressed.
		if( (char)keyboard == 'p' || (char)keyboard == 'P' ) // PROPORTIONAL CODING SELECTED
		{
			binaryCoding = false;

			while(1)
			{
				system("cls");
				printf("BETA Communication Software\n\n");
				printf("CONFIGURATIONS -  Proportional coding selected\n");					
				printf("Choose the MINIMUM stimulation period (in milliseconds) and press ENTER >> ");
				
				memset(str, '\0', sizeof(str));
				scanf_s("%s", str, _countof(str));

				if(sscanf_s(str, "%d", &min_period_stimulus) != 0) // checks if the input is integer type
				{
					if(min_period_stimulus >= 500)
					{
						exit = true;   // valid option
						break;
					}
					else
					{
						printf("Period of stimulus less than 500 ms is unsafe.\n\n");
						Sleep(2000);
					}					
				}
				else
				{
					printf("Invalid option.\n\n");
					Sleep(1000);
				}
			}
		}

		else if( (char)keyboard == 'b' || (char)keyboard == 'B' ) // BINARY CODING SELECTED
		{
			binaryCoding = true;

			while(1)
			{
				system("cls");
				printf("BETA Communication Software\n\n");
				printf("CONFIGURATIONS -  Binary coding selected\n");					
				printf("Choose the stimulation period (in milliseconds) and press ENTER >> ");

				memset(str, '\0', sizeof(str));
				scanf_s("%s", str, _countof(str));

				if(sscanf_s(str, "%d", &period_binary) != 0) // checks if the input is integer type
				{
					if(period_binary >= 500)
					{
						exit = true;  // valid option
						break;
					}
					else 
					{					
						printf("Period of stimulus less than 500 ms is unsafe.\n\n");
						Sleep(2000);
					}
				}
				else
				{
					printf("Invalid option.\n\n");
					Sleep(1000);
				}
			}
		}	

		else if( (char)keyboard == ESC )
		{
			exit = true;
		}

		else
		{
			printf("Invalid option.\n\n");
			Sleep(1000);
		}

		if(exit == true)
		{
			break;
		}
	}
}


/* *********************************************************************************
	     					DISCRETE DECODING METHOD
	  Decoding method that sends discrete commands to the robot (left/right)
	  based on the detection of the Left and Right keyboard arrows.
	  This method is used mainly for testing purpose and should be removed soon.
************************************************************************************ */
int discreteDecoding()
{	
	// Infinite loop that the thread runs forever.
	while(1)
	{
		// Checks if no command was pressed.						
		if( leftFiringRate == 0 && rightFiringRate == 0 )
		{
			// Go straight
			WaitForSingleObject(hLeftWheel,INFINITE);
			leftWheel = w_0;
			ReleaseMutex(hLeftWheel);
							
			WaitForSingleObject(hRightWheel,INFINITE);
			rightWheel = w_0;
			ReleaseMutex(hRightWheel);
		}		


		// Checks if the turn LEFT command was pressed.					
		if( leftFiringRate > 0 )
		{
			// Turn LEFT.
			WaitForSingleObject(hLeftWheel,INFINITE);
			leftWheel = -w_0/2;
			ReleaseMutex(hLeftWheel);
							
			WaitForSingleObject(hRightWheel,INFINITE);
			rightWheel = w_0/2;
			ReleaseMutex(hRightWheel);

			Sleep(500); // turn for 500 ms
		}		

		// Checks if the turn RIGHT command was pressed.
		if( rightFiringRate > 0 )
		{
			// Turn RIGHT.
			WaitForSingleObject(hLeftWheel,INFINITE);
			leftWheel = w_0/2;
			ReleaseMutex(hLeftWheel);
							
			WaitForSingleObject(hRightWheel,INFINITE);
			rightWheel = -w_0/2;
			ReleaseMutex(hRightWheel);

			Sleep(500); // turn for 500 ms
		}

		// Check if it is time to terminate the thread.
		if(endApplication == true)
		{
			return(0);
		}
	}
}



/* ******************************************************************************
				  WINNER-TAKES-ALL DECODING METHOD - Martinoia, 2007.
	   Decoding method that is based on the instantaneous firing rate of the
	   recording sites. These recording sites are divided into two groups,
	   respectively used for controlling the left and right wheel.
	   For more details of the implementation, see the Research Article
	   "Connecting Neurons to a Mobile Robot: An In Vitro Bidirectional Neural
	   Interface", page 4.

********************************************************************************* */
int WTADecoding()
{
	short int w_L = w_0; // current left speed
	short int w_R = w_0; // current right speed		

	// Infinite loop that the thread runs forever.
	while(1)
	{
		if( leftFiringRate == 0 && rightFiringRate == 0 )
		{
			w_L = w_0;
			w_R = w_0;
		}

		else
		{
			// The implementation of the Winner-Takes-All Method is placed here:
			if( w_L >= w_R )
			{
				w_L = w_0 - C_L * leftFiringRate;
			}
			else
			{
				w_L = - w_b;
			}

			if( w_R >= w_L )
			{
				w_R = w_0 - C_R * rightFiringRate;
			}
			else
			{
				w_R = - w_b;
			}
		}

		// DEBUG !
		//w_R = - w_R;
		//w_L = -w_L;


		// LEFT Wheel Speed
		WaitForSingleObject(hLeftWheel,INFINITE);
		leftWheel = w_L;
		ReleaseMutex(hLeftWheel);

		// RIGHT Wheel Speed
		WaitForSingleObject(hRightWheel,INFINITE);
		rightWheel = w_R;
		ReleaseMutex(hRightWheel);


		// Check if it is time to terminate the thread.
		if(endApplication == true)
		{			
			return(0);
		}		
	}
}



/* *******************************************
	Connection with simulation V-REP server
********************************************** */
int connectSimulation(int clientID, int portNb)
{
	while(1)
	{
		system("cls");
		printf("BETA Communication Software\n\n");

		clientID = simxStart((simxChar*)"127.0.0.1",portNb,true,true,2000,5);
		if(clientID != -1)
		{
			time(&rawtime);
			localtime_s(&tm_p, &rawtime);
			printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Connected with simulation.\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
			break;
		}
		else
		{
			time(&rawtime);
			localtime_s(&tm_p, &rawtime);
			printf("[%.2d/%.2d/%d %.2d:%.2d:%.2d] Connection with simulation failed. Trying again...\n",tm_p.tm_mday,tm_p.tm_mon+1,tm_p.tm_year+1900,tm_p.tm_hour,tm_p.tm_min,tm_p.tm_sec);
			continue;
		}
	}
	return(clientID);
}



/* *****************************************************
	Socket Initialization to communicate with APLHA
******************************************************** */
SOCKET socketInitializationALPHA(SOCKET ServSock, SOCKADDR_IN ServerAddress)
{
	unsigned short PortaServ = 5480;  // standard chosen port
	
	int wstatus;

	// Initializes Winsock's usage (version 2.2).
	WSADATA WsaDat;
    if (WSAStartup(MAKEWORD(2,2), &WsaDat) != 0)
	{
		InterrompeErro("WSAStartup() falhou");
    }		

	// Creates socket.
	ServSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (ServSock == INVALID_SOCKET)
	{
		InterrompeErro("socket() failed");
    }    
    
    // Builds the local address structure.    
    ServerAddress.sin_family = AF_INET;
    ServerAddress.sin_addr.s_addr = INADDR_ANY;
    ServerAddress.sin_port = htons(PortaServ);

	// Associates local address with a socket.
	wstatus = bind(ServSock, (struct sockaddr *) &ServerAddress, sizeof(ServerAddress));
	if(wstatus == SOCKET_ERROR)
	{
		InterrompeErro("Error: only one BETA application can be opened at a time."); // bind failed
	}

	// Make the socket passive (server).
	wstatus = listen(ServSock, MAX_CONNECTIONS);
	if(wstatus != 0)
	{
	    InterrompeErro("listen() failed");
	}
	
	return(ServSock);
}


/**********************************************
   Return the less number between 2 numbers.
*********************************************** */
int min2(int a, int b)
{
	if (a <= b)
	{
		return a;
	}
	return b;
}

/**********************************************
   Return the less number between 5 numbers.
*********************************************** */
int min5(int a, int b, int c, int d, int e)
{
	int var1 = min2(a,b);
	int var2 = min2(c,d);
	int minVar = min2(var1,var2);
	int min = min2(minVar,e);
	return min;
}


/**********************************************
     Interrompe a execução em caso de erro.
*********************************************** */
void InterrompeErro (char *erro)
{
	printf("%s Error code: %d\n\n", erro, WSAGetLastError());
	system("pause");
	WSACleanup();
	exit(0);
}