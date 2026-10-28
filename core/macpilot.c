// macpilot - general macOS input control via CGEvent (HID level).
// Works with EVERY app: native, Electron/CEF, browsers and page content.
// build: make   (or: clang -O2 -o bin/macpilot core/macpilot.c -framework ApplicationServices -framework Carbon)
#include <ApplicationServices/ApplicationServices.h>
#include <Carbon/Carbon.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static void snooze(int ms){ if(ms>0) usleep(ms*1000); }
static CGPoint cur(void){ CGEventRef e=CGEventCreate(NULL); CGPoint p=CGEventGetLocation(e); CFRelease(e); return p; }
static void post(CGEventRef e){ CGEventPost(kCGHIDEventTap,e); CFRelease(e); }

static void mouseTo(double x,double y){
  post(CGEventCreateMouseEvent(NULL,kCGEventMouseMoved,CGPointMake(x,y),kCGMouseButtonLeft));
}
static CGEventType dnType(int b){ return b==1?kCGEventRightMouseDown:b==2?kCGEventOtherMouseDown:kCGEventLeftMouseDown; }
static CGEventType upType(int b){ return b==1?kCGEventRightMouseUp  :b==2?kCGEventOtherMouseUp  :kCGEventLeftMouseUp; }
static CGMouseButton btn(int b){ return b==1?kCGMouseButtonRight:b==2?kCGMouseButtonCenter:kCGMouseButtonLeft; }

static void clickAt(double x,double y,int n,int b){
  mouseTo(x,y); snooze(90);
  for(int i=1;i<=n;i++){
    CGPoint p=CGPointMake(x,y);
    CGEventRef d=CGEventCreateMouseEvent(NULL,dnType(b),p,btn(b));
    CGEventRef u=CGEventCreateMouseEvent(NULL,upType(b),p,btn(b));
    CGEventSetIntegerValueField(d,kCGMouseEventClickState,i);
    CGEventSetIntegerValueField(u,kCGMouseEventClickState,i);
    post(d); snooze(40); post(u); snooze(60);
  }
}
static void dragTo(double x1,double y1,double x2,double y2,int ms){
  mouseTo(x1,y1); snooze(120);
  post(CGEventCreateMouseEvent(NULL,kCGEventLeftMouseDown,CGPointMake(x1,y1),kCGMouseButtonLeft));
  snooze(80);
  int steps=ms/12; if(steps<12) steps=12;
  for(int i=1;i<=steps;i++){
    double t=(double)i/steps, e=t*t*(3-2*t);          // ease: apps ignore teleporting drags
    CGPoint p=CGPointMake(x1+(x2-x1)*e, y1+(y2-y1)*e);
    post(CGEventCreateMouseEvent(NULL,kCGEventLeftMouseDragged,p,kCGMouseButtonLeft));
    snooze(ms/steps);
  }
  snooze(80);
  post(CGEventCreateMouseEvent(NULL,kCGEventLeftMouseUp,CGPointMake(x2,y2),kCGMouseButtonLeft));
}
static void scrollAt(int dx,int dy,int hasPos,double x,double y){
  if(hasPos){ mouseTo(x,y); snooze(90); }
  int steps=8;
  for(int i=0;i<steps;i++){
    CGEventRef e=CGEventCreateScrollWheelEvent(NULL,kCGScrollEventUnitPixel,2,dy/steps,dx/steps);
    post(e); snooze(20);
  }
}
static void sendText(const char*s){
  CFStringRef cf=CFStringCreateWithCString(NULL,s,kCFStringEncodingUTF8);
  CFIndex n=CFStringGetLength(cf);
  UniChar *buf=malloc(sizeof(UniChar)*(n>0?n:1));
  CFStringGetCharacters(cf,CFRangeMake(0,n),buf);
  for(CFIndex i=0;i<n;i++){                            // one char at a time = reliable in every app
    CGEventRef d=CGEventCreateKeyboardEvent(NULL,0,true);
    CGEventRef u=CGEventCreateKeyboardEvent(NULL,0,false);
    CGEventKeyboardSetUnicodeString(d,1,&buf[i]);
    CGEventKeyboardSetUnicodeString(u,1,&buf[i]);
    post(d); snooze(8); post(u); snooze(8);
  }
  free(buf); CFRelease(cf);
}
struct KM { const char*n; CGKeyCode k; };
static struct KM KEYS[]={
 {"a",0},{"s",1},{"d",2},{"f",3},{"h",4},{"g",5},{"z",6},{"x",7},{"c",8},{"v",9},
 {"b",11},{"q",12},{"w",13},{"e",14},{"r",15},{"y",16},{"t",17},{"1",18},{"2",19},{"3",20},
 {"4",21},{"6",22},{"5",23},{"equal",24},{"9",25},{"7",26},{"minus",27},{"8",28},{"0",29},
 {"rightbracket",30},{"o",31},{"u",32},{"leftbracket",33},{"i",34},{"p",35},{"return",36},
 {"enter",36},{"l",37},{"j",38},{"quote",39},{"k",40},{"semicolon",41},{"backslash",42},
 {"comma",43},{"slash",44},{"n",45},{"m",46},{"period",47},{"tab",48},{"space",49},
 {"grave",50},{"delete",51},{"backspace",51},{"escape",53},{"esc",53},
 {"left",123},{"right",124},{"down",125},{"up",126},
 {"home",115},{"end",119},{"pageup",116},{"pagedown",121},{"forwarddelete",117},
 {"f1",122},{"f2",120},{"f3",99},{"f4",118},{"f5",96},{"f6",97},{"f7",98},{"f8",100},
 {"f9",101},{"f10",109},{"f11",103},{"f12",111},{NULL,0}};
static int lookupKey(const char*s,CGKeyCode*out){
  for(int i=0;KEYS[i].n;i++) if(!strcasecmp(s,KEYS[i].n)){ *out=KEYS[i].k; return 1; }
  return 0;
}
static void keyCombo(char*spec){
  CGEventFlags f=0; CGKeyCode kc=0; int have=0;
  for(char*t=strtok(spec,"+");t;t=strtok(NULL,"+")){
    if(!strcasecmp(t,"cmd")||!strcasecmp(t,"command"))   f|=kCGEventFlagMaskCommand;
    else if(!strcasecmp(t,"shift"))                      f|=kCGEventFlagMaskShift;
    else if(!strcasecmp(t,"alt")||!strcasecmp(t,"option"))f|=kCGEventFlagMaskAlternate;
    else if(!strcasecmp(t,"ctrl")||!strcasecmp(t,"control"))f|=kCGEventFlagMaskControl;
    else if(!strcasecmp(t,"fn"))                         f|=kCGEventFlagMaskSecondaryFn;
    else if(lookupKey(t,&kc)) have=1;
    else { fprintf(stderr,"unknown key: %s\n",t); exit(2); }
  }
  if(!have){ fprintf(stderr,"no base key in combo\n"); exit(2); }
  CGEventRef d=CGEventCreateKeyboardEvent(NULL,kc,true);
  CGEventRef u=CGEventCreateKeyboardEvent(NULL,kc,false);
  CGEventSetFlags(d,f); CGEventSetFlags(u,f);
  post(d); snooze(40); post(u);
}
static CFStringRef axStr(AXUIElementRef e,CFStringRef attr){
  CFTypeRef v=NULL;
  if(AXUIElementCopyAttributeValue(e,attr,&v)==kAXErrorSuccess && v){
    if(CFGetTypeID(v)==CFStringGetTypeID()) return (CFStringRef)v;
    CFRelease(v);
  }
  return NULL;
}
static void show(const char*label,CFStringRef s){
  if(!s) return;
  char b[512]; if(CFStringGetCString(s,b,sizeof b,kCFStringEncodingUTF8) && b[0])
    printf("  %-10s %s\n",label,b);
  CFRelease(s);
}
static void peek(double x,double y){                    // what is actually under that point?
  AXUIElementRef sys=AXUIElementCreateSystemWide(), el=NULL;
  if(AXUIElementCopyElementAtPosition(sys,(float)x,(float)y,&el)==kAXErrorSuccess && el){
    printf("element at %.0f,%.0f:\n",x,y);
    show("role",   axStr(el,kAXRoleAttribute));
    show("subrole",axStr(el,kAXSubroleAttribute));
    show("title",  axStr(el,kAXTitleAttribute));
    show("value",  axStr(el,kAXValueAttribute));
    show("desc",   axStr(el,kAXDescriptionAttribute));
    show("help",   axStr(el,kAXHelpAttribute));
    CFRelease(el);
  } else printf("no accessibility element at %.0f,%.0f (likely web/canvas content)\n",x,y);
  CFRelease(sys);
}
// Proves Accessibility is granted to whatever launched us (the terminal app), by
// doing a harmless read that only works with the grant. Never prompts, never clicks.
// exit 0 = granted, 3 = not granted.
static int access_check(void){
  int trusted=AXIsProcessTrusted();
  AXUIElementRef sys=AXUIElementCreateSystemWide(), el=NULL;
  CFTypeRef v=NULL;
  AXError err=AXUIElementCopyAttributeValue(sys,kAXFocusedApplicationAttribute,&v);
  if(v) CFRelease(v);
  if(err!=kAXErrorSuccess && err!=kAXErrorNoValue){   // some apps do not answer; try the menu bar corner
    err=AXUIElementCopyElementAtPosition(sys,1.0f,1.0f,&el);
    if(el) CFRelease(el);
  }
  CFRelease(sys);
  int readable = err==kAXErrorSuccess || err==kAXErrorNoValue;
  if(trusted && readable){ printf("granted\n"); return 0; }
  printf("not granted (trusted=%d, read error %d)\n",trusted,(int)err);
  return 3;
}
static void screens(void){
  CGDirectDisplayID ids[8]; uint32_t n=0;
  CGGetActiveDisplayList(8,ids,&n);
  for(uint32_t i=0;i<n;i++){
    CGRect r=CGDisplayBounds(ids[i]);
    size_t pw=CGDisplayPixelsWide(ids[i]), ph=CGDisplayPixelsHigh(ids[i]);
    CGDisplayModeRef m=CGDisplayCopyDisplayMode(ids[i]);
    size_t bw=m?CGDisplayModeGetPixelWidth(m):pw;
    if(m) CGDisplayModeRelease(m);
    printf("display %u: logical %.0fx%.0f at (%.0f,%.0f)  backing %zux%zu  scale %.2f\n",
      i,r.size.width,r.size.height,r.origin.x,r.origin.y,bw,
      (size_t)((double)bw*ph/pw),(double)bw/r.size.width);
  }
  printf("NOTE: screencapture writes BACKING pixels; this tool takes LOGICAL points.\n");
  printf("      divide screenshot coords by scale.\n");
}
int main(int argc,char**argv){
  if(argc<2) goto usage;
  const char*c=argv[1];
  if(!strcmp(c,"access")) return access_check();
  if(!strcmp(c,"pos")){ CGPoint p=cur(); printf("%.0f %.0f\n",p.x,p.y); }
  else if(!strcmp(c,"screen")) screens();
  else if(!strcmp(c,"peek")){
    if(argc>=4) peek(atof(argv[2]),atof(argv[3]));
    else { CGPoint p=cur(); peek(p.x,p.y); } }
  else if(!strcmp(c,"move")){ if(argc<4) goto usage; mouseTo(atof(argv[2]),atof(argv[3])); }
  else if(!strcmp(c,"click")){
    if(argc<4) goto usage;
    int n=argc>4?atoi(argv[4]):1, b=0;
    if(argc>5){ if(!strcmp(argv[5],"right"))b=1; else if(!strcmp(argv[5],"middle"))b=2; }
    clickAt(atof(argv[2]),atof(argv[3]),n,b);
    printf("clicked %dx button%d at %s,%s\n",n,b,argv[2],argv[3]); }
  else if(!strcmp(c,"drag")){
    if(argc<6) goto usage;
    dragTo(atof(argv[2]),atof(argv[3]),atof(argv[4]),atof(argv[5]),argc>6?atoi(argv[6]):500);
    printf("dragged %s,%s -> %s,%s\n",argv[2],argv[3],argv[4],argv[5]); }
  else if(!strcmp(c,"scroll")){
    if(argc<4) goto usage;
    scrollAt(atoi(argv[2]),atoi(argv[3]),argc>=6,argc>=6?atof(argv[4]):0,argc>=6?atof(argv[5]):0); }
  else if(!strcmp(c,"type")){ if(argc<3) goto usage; sendText(argv[2]); }
  else if(!strcmp(c,"key")){  if(argc<3) goto usage; keyCombo(argv[2]); }
  else goto usage;
  return 0;
usage:
  fprintf(stderr,
   "macpilot - macOS input control (logical points, not screenshot pixels)\n\n"
   "  access                       is Accessibility granted? (exit 0 yes, 3 no)\n"
   "  pos                          print cursor position\n"
   "  screen                       displays + Retina scale factor\n"
   "  peek [X Y]                   what UI element is under the point\n"
   "  move X Y\n"
   "  click X Y [n] [left|right|middle]\n"
   "  drag X1 Y1 X2 Y2 [ms]\n"
   "  scroll DX DY [X Y]\n"
   "  type \"text\"                  types unicode into the focused field\n"
   "  key cmd+shift+4              modifiers: cmd shift alt ctrl fn\n");
  return 2;
}
