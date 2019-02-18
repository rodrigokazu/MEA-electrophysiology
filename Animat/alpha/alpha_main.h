/* *******************************************************
   Alpha Application v1.0
   University of Reading
   School of System Engineering
   Brain Embodiment Laboratory
   Johnathan Mayke Melo Neto
   Vitor de Carvalho Hazin
   January/2015
******************************************************* */

// Includes
#define WIN32_LEAN_AND_MEAN  // This define MUST be here.
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
#include <iostream>
#include <ObjIdl.h>

// Libraries and DLL's for the Timer Event
#using <system.dll>
using namespace System;
using namespace System::Timers;

// Defines
#define TAMBUFFER 5       // length of the messages transmitted between client and server
#define NUM_THREADS	4     // number of threads
#define KEY_LEFT 75
#define KEY_RIGHT 77
#define ENTER	0xD
#define ESC		0x1B

// Casting for the third and sixth parameters of function _beginthreadex
typedef unsigned (WINAPI *CAST_FUNCTION)(LPVOID);
typedef unsigned *CAST_LPDWORD;

// Functions prototypes
void OpenThreads (int ClientSock);

// Threads
DWORD WINAPI threadReceive(LPVOID);
DWORD WINAPI threadSend(LPVOID);
DWORD WINAPI threadDetectSpike();
DWORD WINAPI threadGenerateStimuli();

// Synchronization objects that will be shared between threads
HANDLE hLeftChannel;     // Handle for mutex_left_channel
HANDLE hRightChannel;    // Handle for mutex_right_channel
HANDLE hStimuliLeft;     // Handle for mutex_stimuli_left
HANDLE hStimuliRight;    // Handle for mutex_stimuli_right
HANDLE hTextFile;        // Handle for mutex_text_file

HANDLE hThreads[NUM_THREADS];
DWORD dwThreadId;
DWORD dwExitCode = 0;
DWORD dwRet;

// Functions prototypes
void configurationScreen(void);


// Global variables that are responsible communicate commands between threads.
int leftChannel  = 0;  // when a spike is detected in the channel(s) related to the left wheel, this counter increases
int rightChannel = 0;  // when a spike is detected in the channel(s) related to the right wheel, this counter increases

int leftFiringRate = 0;	  // stores how many times the left channel was fired within 1 second.
int rightFiringRate = 0;  // stores how many times the right channel was fired within 1 second.

short int stimuliLeft  = 0;  // number of stimuli to be generated due to the left sensor
short int stimuliRight = 0;  // number of stimuli to be generated due to the right sensor

int keyboard;          // receive the key pressed
bool bStart = false;   // detects if ENTER/ESC was pressed in the BETA Application

// Global variable that acts like a flag to end all the threads.
bool endApplication = false;

// Global variables to read current time.
time_t rawtime;
struct tm tm_p;

// Text file to store the Firing Rates of the Left channel and Right channel.
FILE *fp;

// Declaration of the Timer Event Class 
// For more information, see <https://msdn.microsoft.com/pt-br/library/system.timers.elapsedeventhandler(v=vs.110).aspx>
#ifndef TIMEREVENT_H
#define TIMEREVENT_H
public ref class TimerEvent
{
	private: 
	   static System::Timers::Timer^ aTimer;

	public:
	   ~TimerEvent();
	   static void StartTimer();

	private:
	   // Specify what you want to happen when the Elapsed event is raised.
	   static void OnTimedEvent( Object^ source, ElapsedEventArgs^ e );
};
#endif

// Functions prototypes to detect a event when closing the console application
BOOL WINAPI SetConsoleCtrlHandler(
  _In_opt_ PHANDLER_ROUTINE HandlerRoutine,
  _In_     BOOL             Add
);

BOOL WINAPI HandlerRoutine(
    DWORD dwCtrlType  
);


// Event handler to detect if the console application was closed by the user.
BOOL WINAPI ConsoleHandler(DWORD CEvent)
{
	switch(CEvent)
    {
	   case CTRL_CLOSE_EVENT:

		   printf("\n\nClosing ALPHA, please wait...\n\n\n");

		   // Waits all threads to finish.
	       dwRet = WaitForMultipleObjects(NUM_THREADS, hThreads, TRUE, INFINITE);

		   // Clears the reference of the object.
		   for (int i=0; i<NUM_THREADS; ++i) 
		   {
			  GetExitCodeThread(hThreads[i], &dwExitCode);
			  CloseHandle(hThreads[i]);	
		   }	

			// End of loop. Closes the synchronization objects, and closes the Winsock2 environment.
		   CloseHandle(hLeftChannel);
		   CloseHandle(hRightChannel);
		   CloseHandle(hStimuliLeft);
		   CloseHandle(hStimuliRight);
		   CloseHandle(hTextFile);
		   WSACleanup();
		   fclose(fp);		   

	   break;
    }
    return TRUE;
}