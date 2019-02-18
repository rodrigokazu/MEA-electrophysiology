/* *******************************************************
   Beta Application v1.0
   University of Reading
   School of System Engineering
   Brain Embodiment Laboratory
   Johnathan Mayke Melo Neto
   January/2015
******************************************************* */

// Includes
#define WIN32_LEAN_AND_MEAN // This define MUST be here.
#include <windows.h>
#include <stdlib.h>
#include <stdio.h>
#include <conio.h>     
#include <errno.h>
#include <winsock2.h>
#include <cstdlib>
#include <process.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <iostream>
#include <ObjIdl.h>
#include "extApi.h"   // library to use the V-REP Remote C++ API functions

// Defines
#define MAX_CONNECTIONS 1   // maximum length of the queue of pending connections; here 1 client is enough.
#define ESC			0x1B
#define ENTER		0xD
#define SPACE       0X20
#define TAMBUFFER 5         // length of the messages transmitted between client and server
#define NUM_THREADS	6       // number of threads

// Casting for the third and sixth parameters of function _beginthreadex
typedef unsigned (WINAPI *CAST_FUNCTION)(LPVOID);
typedef unsigned *CAST_LPDWORD;

// Functions prototypes
int connectSimulation(int,int);
int min2(int,int);
int min5(int,int,int,int,int);
SOCKET socketInitializationALPHA(SOCKET, SOCKADDR_IN);
void configurationScreen(void);
void configurationMaximumSpeedRobot(void);
void configurationDecodingMethod(void);
void adjustParameters(void);
int discreteDecoding(void);
int WTADecoding(void);
void configurationSensoryPatterns(void);
void InterrompeErro (char *erro);  //função que interrompe a execução em caso de erro - RETIRAR !!!
void OpenThreads (int ClientSock, int clientID);

// Threads
DWORD WINAPI threadReceive(LPVOID);
DWORD WINAPI threadSend(LPVOID);
DWORD WINAPI threadTurn(LPVOID);
DWORD WINAPI threadSensor(LPVOID);
DWORD WINAPI threadReadKeyboard(LPVOID);
DWORD WINAPI threadSpeedDecoding();

// Synchronization objects that will be shared between threads
HANDLE hLeftWheel;      // Handle for mutex_left_wheel
HANDLE hRightWheel;     // Handle for mutex_right_wheel
HANDLE hDoStimuliLeft;  // Handle for mutex_doStimuli_left
HANDLE hDoStimuliRight; // Handle for mutex_doStimuli_right
HANDLE hButton;         // Handle for mutex_button
HANDLE hSim;            // Handle for mutex_sim

HANDLE hThreads[NUM_THREADS];
DWORD dwThreadId;
DWORD dwExitCode = 0;
DWORD dwRet;

// GLOBAL VARIABLES

// Client ID of the V-Rep Simulation
int clientID = 0;

// Simulation's handles of the Left and Right motors
simxInt leftMotorHandle;
simxInt rightMotorHandle;

// Global variables that are responsible communicate commands between threads.
short int leftWheel = 0;       // speed of the left wheel
short int rightWheel = 0;      // speed of the right wheel
short int doStimuliLeft = 0;   // when left sensor detected obstacle, this variable increases
short int doStimuliRight = 0;  // when right sensor detected obstacle, this variable increases

int leftFiringRate = 0;	  // stores how many times the left channel was fired within 1 second.
int rightFiringRate = 0;  // stores how many times the right channel was fired within 1 second.


// Global variables to control the robot.
int keyboard = 0;         // receive the key pressed
bool buttonPressed = false; // detect if ENTER or ESC have been pressed
bool spacePressed = false;  // detects if SPACEBAR is pressed so the robot can go backwards
bool startRobot = false;  // detects if ENTER/ESC is pressed so the robot can move or not

// Global variable that acts like a flag to end all the threads.
bool endApplication = false;   

short int decodingMethod = 1; // speed decoding method

// Global variables to read current time.
time_t rawtime;    
struct tm tm_p;

// Winner-Takes-All Parameters
float C_L = 5; // normalized coefficient related to the left wheel	
float C_R = 5; // normalized coefficient related to the right wheel

// Global configuration variables.
short int period_binary = 1000;        // period of stimulation in binary coding pattern (ms) - Martinoia, 2007
short int max_period_stimulus = 2000;  // max period of stimulation in proportional coding pattern (msec) - Martinoia, 2007
short int min_period_stimulus = 500;   // min period of stimulation in proportional coding pattern (msec) - Martinoia, 2007
bool binaryCoding = false;       // switch between binary and proportional coding
float w_backwards = 10;           // angular speed to drive backwards due to the user command

short int w_0 = 10; // maximum angular speed (rad/s) of the robot
short int w_b = 1;  // constant reverse angular (rad/s) in WTA strategy (winner-takes-all) - Martinoia, 2007


// Functions prototypes to detect a event when closing the console application
BOOL WINAPI SetConsoleCtrlHandler(
  _In_opt_ PHANDLER_ROUTINE HandlerRoutine,
  _In_     BOOL             Add
);

BOOL WINAPI HandlerRoutine(
    DWORD dwCtrlType  
);

// Event handler to detect if the console application was closed by the user.
// If it was closed, the robot will stop.
BOOL WINAPI ConsoleHandler(DWORD CEvent)
{
	switch(CEvent)
    {
	   case CTRL_CLOSE_EVENT:

		    printf("Closing BETA, please wait...\n");

			// Sends command to simulation to stop the simulation.
			WaitForSingleObject(hSim,INFINITE);	
			simxStopSimulation((int)clientID,simx_opmode_oneshot);
			Sleep(1000);
			ReleaseMutex(hSim);

		    // Waits the finalization of all threads except threadReadKeyboard.
		    dwRet = WaitForSingleObject(hThreads[0], INFINITE);
		    dwRet = WaitForSingleObject(hThreads[1], INFINITE);
		    dwRet = WaitForSingleObject(hThreads[2], INFINITE);
		    dwRet = WaitForSingleObject(hThreads[3], INFINITE);
		    dwRet = WaitForSingleObject(hThreads[5], INFINITE);

			// Clears the reference of the object.
			for (int i=0; i<NUM_THREADS; ++i) 
			{
				GetExitCodeThread(hThreads[i], &dwExitCode);
				CloseHandle(hThreads[i]);	
			}										

			// Close simulation socket, and handles.
			WSACleanup();
			CloseHandle(hLeftWheel);
			CloseHandle(hRightWheel);
			CloseHandle(hDoStimuliLeft);
			CloseHandle(hDoStimuliRight);
			CloseHandle(hButton);
			CloseHandle(hSim);
			simxFinish((int)clientID);		

	   break;
    }
    return TRUE;
}