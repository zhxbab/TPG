// to run this you have to
// 1. set your chip to cn
// 2. run "rasm -c2sim "
 
# simple rasm template to get into 64 bit, linear paging , cacheoff

##########  check /n/dv/release/rasm/current/include/std.inc for struct definition ####################
include "/home/cv/tpg/TPG/include/std.inc";

############## variables definition #############
$tlb_base =  0x9000;
$idt_table_base = 0x4500;
$gdt_table_base = 0x4000;

org 0x3000;
@gdt_table_pointer = new std::table_pointer;
@gdt_table_pointer.base = $gdt_table_base;

@idt_table_pointer = new std::table_pointer;
@idt_table_pointer.base = $idt_table_base;

org $gdt_table_base;
@gdt = new std::descriptor[10];  # make 10 descriptors, note 0th descriptor is reserved 
$cs32 = 1;
$ds32 = 2;
$cs64 = 3;
$ds64 = 4;
@gdt[$cs32].type = 0xB;  #cs 32 bit desc
@gdt[$cs32].db   = 1;  #cs 32 bit desc
@gdt[$ds32].type = 0x3;  #cs 32 bit desc
@gdt[$ds32].db   = 1;  #cs 32 bit desc
@gdt[$cs64].type = 0xB;  #cs 64 bit desc
@gdt[$cs64].l    = 1;  #cs 64 bit desc
@gdt[$ds64].type = 0x3;  #cs 32 bit desc
@gdt[$ds64].l    = 1;  #cs 64 bit desc

org $idt_table_base;
@idt = new std::idt_gate_64[32];  # make idt gate for the first 32 interrupts

# map interrupt handler 6 (#UD)
@idt[6].selector = &SELECTOR($cs64);  
@idt[6].offset = $int6_handler; 

&TO_MEMORY_ALL();    # this dump all the data structures to memory

############## define interrupt handlers #############
org 0x8000;
int6_handler:
  use 64;
  mov ax,6;
  out 0x80,ax;
  iretq;

############## main code   ###########################

# reset vector, this is where the processor starts fetching
org 0xfffffff0;
 use 16;
 jmp 0x0:0x80;
 org 0x80;
 lgdt [&@gdt_table_pointer];
 lidt [&@idt_table_pointer];

# enable 32 bit protect mode
 mov edx,cr0;
 or edx,0x1;
 mov cr0,edx;
 jmpf &SELECTOR($cs32):0x00000100;

org 0x00000100;
 use 32;
 mov eax,cr4;
# enable pae sse
 or eax ,0x620;
 mov cr4,eax;
 mov eax,$tlb_base;
 mov cr3,eax;
 mov ecx,0xc0000080;
 rdmsr;
 mov eax,0x100;
 wrmsr;

# enable paging
 mov eax,cr0;
 or  eax,0x80000000;
 mov cr0,eax;

# now in 64 bit mode, turn on 64 bit tlb.
# only virtual address 0x0->0x1FFFFF  is support in the TLB 
# with the below cmds.  rasm will flag an error if you go above 
#virtual address 0x1FFFFF.  (and it'll tell you which page entry you have to specify)
$tlb_pointer = INIT_TLB $tlb_base;
PAE64_PML4E  0              0  0x00002001;
PAE64_PDPT   0  0           0  0x01000001;
PAE64_PDE    0  0 0         0  0x00000081;
PAE64_PDE    0  0 2         0  0x10000081;

PAGING $tlb_pointer;

# from now on all the code is going to be layout in virtual memory, and translated 
# into physical address automatically by rasm (by using the TLB above)

 mov eax,&SELECTOR($ds32);
 mov ds,eax;
 mov ss,eax;
$target = 0x00400000;

 jmpf &SELECTOR($cs64):$target;
# we are in 64 bit now
org $target;

// simple tbd cmd shows you how you can snoop the physical address using the virtual address
//;$ at io write 0x80 issue priority snoop 0x{&PA($target+0x30)} 
 use 64;
    mov rsp,0x1000;
    int6;
    mov r11,0x123456789ABCDEF;
    mov r11,r12;
    hlt;
