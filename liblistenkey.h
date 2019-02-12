#include "common.h"
#include <stdio.h>

//This code is an adaptation of:
//http://www.reocities.com/timessquare/cauldron/1299/hooknodll.html

typedef bool (*EVENTPROCESSOR)(DWORD, DWORD, DWORD);
EVENTPROCESSOR eventProcessor;
HHOOK hKeyHook;
bool quitListenKey;

void quitlistenkey() {
	quitListenKey = true;
	PostMessage(NULL, 0, 0, 0);
}

__declspec(dllexport) LRESULT CALLBACK
KeyEvent (int nCode, WPARAM wParam, LPARAM lParam) {
	if (nCode == HC_ACTION) {
		KBDLLHOOKSTRUCT hooked = *((KBDLLHOOKSTRUCT*)lParam);
		if(eventProcessor(hooked.scanCode, hooked.vkCode, hooked.flags)) {
			return 1;
		}
	}
	return CallNextHookEx(hKeyHook, nCode, wParam, lParam);
}

// This is a simple message loop that will be used
// to block while we are reading keys. It does not
// perform any real task.

void MsgLoop() {
	MSG message;
	while (GetMessage(&message, NULL, 0, 0)) {
		TranslateMessage(&message);
		DispatchMessage(&message);
		if(quitListenKey) {
			break;
		}
	}
}

// This thread is started by the main routine to install
// the low level keyboard hook and start the message loop
// to loop forever while waiting for keyboard events.

DWORD WINAPI KeyReader(LPVOID lpParameter) {
	HINSTANCE hExe = GetModuleHandle(NULL);
	if(!hExe) {
		hExe = LoadLibrary((LPCSTR) lpParameter);
	}
	if(!hExe) {
		return 1;
	}
	hKeyHook = SetWindowsHookEx(WH_KEYBOARD_LL, (HOOKPROC)KeyEvent, hExe, 0);
	MsgLoop();
	UnhookWindowsHookEx(hKeyHook);
	return 0;
}

// The runlistenkey function starts the thread that
// installs the keyboard hook and waits until it
// terminates.

int runlistenkey(EVENTPROCESSOR ep, char* progname) {
	quitListenKey = false;
	eventProcessor = ep;
	HANDLE hThread;
	DWORD dwThread;
	DWORD exThread;
	hThread =
		CreateThread(
			NULL,
			0,
			(LPTHREAD_START_ROUTINE)KeyReader,
			(LPVOID)progname,
			0,
			&dwThread
		);
	if(hThread) {
		return WaitForSingleObject(hThread, INFINITE);
	}
	else return 1;
}
