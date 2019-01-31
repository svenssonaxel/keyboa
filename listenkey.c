//todo: exit on stdin close
//todo: exit after 20 counts events that aren't processed.
//todo: JSON output
#include "liblistenkey.c"
#include <unistd.h>
#include <stdio.h>
#include <signal.h>

BOOL opte, opti, opta, optd, opts, optv, optc, optU, optI, optO, optE, optD, optJ, optA;
int evcount;

BOOL processevent(DWORD scancode, DWORD virtualkey, DWORD flags){
 if(optI&&(flags&LLKHF_INJECTED))return FALSE;
 if(optA&&(flags&LLKHF_EXTENDED)==0&&scancode==0x021d)return optc;
 if(!(optU&&(flags&LLKHF_UP))){
  if(optJ){
   printf("{\"§\":{}");
   if(opte)printf(",\"e\":%s",(flags&LLKHF_EXTENDED)?"true":"false");
   if(opti)printf(",\"i\":%s",(flags&LLKHF_INJECTED)?"true":"false");
   if(opta)printf(",\"a\":%s",(flags&LLKHF_ALTDOWN)? "true":"false");
   if(optd)printf(",\"u\":%s",(flags&LLKHF_UP)?      "true":"false");
   if(opts)printf(",\"s\":\"%04X\"",scancode);
   if(optv)printf(",\"v\":\"%02X\"",virtualkey);
   printf("}");
  }
  else{
   if(opte)printf((flags&LLKHF_EXTENDED)?"e":"-");
   if(opti)printf((flags&LLKHF_INJECTED)?"i":"-");
   if(opta)printf((flags&LLKHF_ALTDOWN)? "a":"-");
   if(optd)printf((flags&LLKHF_UP)?      "u":"d");
   if(opts)printf("%04X",scancode);
   if(optv)printf("%02X",virtualkey);
  }
  if(printf("\n")==-1 && optO)quitlistenkey();
  fflush(stdout);
  if(optD) if(++evcount>20) quitlistenkey();}
 if(optE) if(scancode==1 && flags==128) quitlistenkey();
 return optc;}

void printhelp(){
 printf("Print Windows keyboard events on stdout.\n");
 printf("Options:\n");
 printf("-e Turn on printing e for extended keys.\n");
 printf("-i Turn on printing i for injected events.\n");
 printf("-a Turn on printing a for alt-down status.\n");
 printf("-d Turn on printing u/d for up/down events.\n");
 printf("-s Turn on printing 4-digit hex scancode.\n");
 printf("-v Turn on printing 2-digit hex virtual key code.\n");
 printf("-c Turn on event consuming (prevents applications to see the event).\n");
 printf("-U Do not print up-key events.\n");
 printf("-I Do not print or consume injected events.\n");
 printf("-A Prevent AltGr from acting like two keys.\n");
 printf("-O Exit when stdout closes.\n");
 printf("-E Exit when escape key is pressed.\n");
 printf("-D Exit after 20 events are processed.\n");
 printf("-J Output in JSON format.\n");
 printf("-h Print this help text and exit.\n");
 exit(0);}

// The main function processes the arguments and starts runlistenkey
int main(int argc, char** argv){
 if(argc==1)printhelp();
 char* progname=argv[0];
 int c;
 while ((c = getopt (argc, argv, "eiadsvcUIAOEDJh")) != -1)
  switch (c){
   case 'e': opte=TRUE;  break;
   case 'i': opti=TRUE;  break;
   case 'a': opta=TRUE;  break;
   case 'd': optd=TRUE;  break;
   case 's': opts=TRUE;  break;
   case 'v': optv=TRUE;  break;
   case 'c': optc=TRUE;  break;
   case 'U': optU=TRUE;  break;
   case 'I': optI=TRUE;  break;
   case 'A': optA=TRUE;  break;
   case 'O': optO=TRUE;  break;
   case 'E': optE=TRUE;  break;
   case 'D': optD=TRUE;  break;
   case 'J': optJ=TRUE;  break;
   case 'h': printhelp();
   default: abort();}
  signal(SIGINT,quitlistenkey);
  signal(SIGTERM,quitlistenkey);
 runlistenkey(processevent,progname);}
