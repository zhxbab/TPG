//                       PMCTestA.cpp                2015-12-22 Agner Fog
//
//          Multithread PMC Test program for Windows and Linux
//
//
// This program is intended for testing the performance of a little piece of 
// code written in C, C++ or assembly. 
// The code to test is inserted at the place marked "Test code start" in
// PMCTestB.cpp, PMCTestB32.asm or PMCTestB64.asm.
// 
// In 64-bit Windows: Run as administrator, with driver signature enforcement
// off.
//
// See PMCTest.txt for further instructions.
//
// To turn on counters for use in another program, run with command line option
//     startcounters
// To turn counters off again, use command line option 
//     stopcounters
//
// © 2000-2015 GNU General Public License www.gnu.org/licenses
//////////////////////////////////////////////////////////////////////////////

#include "PMCTest.h"


//////////////////////////////////////////////////////////////////////
//
//        Thread synchronizer
//
//////////////////////////////////////////////////////////////////////
int main(){

int thread = 0;
int ret;
// set PMC0
__asm__ __volatile__("movl $0x186,%ecx");
__asm__ __volatile__("rdmsr");
__asm__ __volatile__("or $0x0003003C,%eax");
__asm__ __volatile__("and $0x0003003C,%eax");
__asm__ __volatile__("wrmsr");
//enable global ctrl
__asm__ __volatile__("movl $0x38f,%ecx");
__asm__ __volatile__("rdmsr");
__asm__ __volatile__("or $0x1,%eax");
__asm__ __volatile__("wrmsr");
// enable PMC0
__asm__ __volatile__("movl $0x186,%ecx");
__asm__ __volatile__("rdmsr");
__asm__ __volatile__("or $0x400000,%eax");
__asm__ __volatile__("wrmsr");
ret = TestLoop(1);
__asm__ __volatile__("movl $0x186,%ecx");
__asm__ __volatile__("rdmsr");
__asm__ __volatile__("and $0xBfffff,%eax");
__asm__ __volatile__("wrmsr");
return ret;
}
