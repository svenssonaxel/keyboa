// Copyright © 2019 Axel Svensson <mail@axelsvensson.com>
// Legal: See COPYING.txt
#include "common.h"
#include "json-str.c"
#include <stdio.h>

//This code is an adaptation of:
//http://www.reocities.com/timessquare/cauldron/1299/hooknodll.html

typedef bool (*KEYEVENTPROCESSOR)(WPARAM, KBDLLHOOKSTRUCT*);
KEYEVENTPROCESSOR keyEventProcessor;
HHOOK hKeyHook;
typedef bool (*MOUSEEVENTPROCESSOR)(WPARAM, MSLLHOOKSTRUCT*);
MOUSEEVENTPROCESSOR mouseEventProcessor;
HHOOK hMouseHook;
bool quitListenKey;

void quitlistenkey() {
	quitListenKey = true;
	PostMessage(NULL, 0, 0, 0);
}

__declspec(dllexport) LRESULT CALLBACK
KeyEvent (int nCode, WPARAM wParam, LPARAM lParam) {
	if (nCode == HC_ACTION) {
		if(keyEventProcessor(wParam, (KBDLLHOOKSTRUCT*)lParam)) {
			return 1;
		}
	}
	return CallNextHookEx(hKeyHook, nCode, wParam, lParam);
}

__declspec(dllexport) LRESULT CALLBACK
MouseEvent (int nCode, WPARAM wParam, LPARAM lParam) {
	if (nCode == HC_ACTION) {
		if(mouseEventProcessor(wParam, (MSLLHOOKSTRUCT*)lParam)) {
			return 1;
		}
	}
	return CallNextHookEx(hMouseHook, nCode, wParam, lParam);
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

DWORD WINAPI EventReader(LPVOID lpParameter) {
	HINSTANCE hExe = GetModuleHandle(NULL);
	if(!hExe) {
		hExe = LoadLibrary((LPCSTR) lpParameter);
	}
	if(!hExe) {
		return 1;
	}
	if(keyEventProcessor)
		hKeyHook = SetWindowsHookEx(WH_KEYBOARD_LL, (HOOKPROC)KeyEvent, hExe, 0);
	if(mouseEventProcessor)
		hMouseHook = SetWindowsHookEx(WH_MOUSE_LL, (HOOKPROC)MouseEvent, hExe, 0);
	MsgLoop();
	if(keyEventProcessor)
		UnhookWindowsHookEx(hKeyHook);
	if(mouseEventProcessor)
		UnhookWindowsHookEx(hMouseHook);
	return 0;
}

// The runlistenkey function starts the thread that
// installs the keyboard hook and waits until it
// terminates.

int runlistenkey(KEYEVENTPROCESSOR kep, MOUSEEVENTPROCESSOR mep, char* progname) {
	quitListenKey = false;
	keyEventProcessor = kep;
	mouseEventProcessor = mep;
	HANDLE hThread;
	DWORD dwThread;
	DWORD exThread;
	hThread =
		CreateThread(
			NULL,
			0,
			(LPTHREAD_START_ROUTINE)EventReader,
			(LPVOID)progname,
			0,
			&dwThread
		);
	if(hThread) {
		return WaitForSingleObject(hThread, INFINITE);
	}
	else return 1;
}
