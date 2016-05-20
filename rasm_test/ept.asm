include "/media/Data_Linux/tools/tpg/include/std.inc";


#&VALID_MEMORY_CHECKING(1);
&VALID_MEMORY_RANGE("jason",0x1000,0x2000);

#################################
# vmcs
#################################
org 0x3000;
@vmcs = new std::vmcs::data;

@vmcs.host_gdtr_base = $gdt32_start;
@vmcs.host_cs_sel = 0x8;
@vmcs.host_ss_sel = 0x18;
@vmcs.host_tr_sel = 0x18; #FIXME - must point to a tss selector
@vmcs.virtual_apic_page_addr_full = 0xB000; 
@vmcs.ept_pointer_full = 0xC000;
@vmcs.host_rip = $v0_return; 
@vmcs.host_rsp = 0x9000; 


@vmcs.guest_gdtr_base = $gdt32_start;
@vmcs.guest_cs_sel= 0x20;
@vmcs.guest_tr_sel = 0x18; #FIXME - must point to a tss selector
@vmcs.guest_rip = $guest_entry_point; 
@vmcs.guest_rsp = 0x9000; 

&TO_MEMORY_ALL();    # this dump all the data structures to memory

#################################$
#stack
#################################$
org 0x8000;
:mystack

#################################$
#GDT
#################################$
org 0x1a0;
gdt32_start:
dq 0;
dq 0x00C09b000000ffff;
dq 0x00cf93000000ffff;
stack_sel:
dq 0x00Cf9b000000ffff;
guest_code_sel:
dq 0x00Af9b000000ffff;
cs64_sel:
dq 0x00Af9b000000ffff;
gdt32_end:
gdtr:
dw      $gdt32_end-$gdt32_start-1;
gdtr_base:
dd      $gdt32_start;
#################################$

org       0xfffffff0;
use 16;
jmpf      0x0:0x0;

org       0x00000000;
mov ebx, cr0;
or  ebx, 0x00000021;
and ebx, 0x9FFFFFFF;
mov cr0, ebx;

mov ecx, 0x2ff;
mov eax, 0x806;
xor edx, edx;
wrmsr;


mov edx, cr4;
or edx, 0x2620;
mov cr4, edx;

lgdt [$gdtr];

jmp 0x8:$blah;
hlt;

org 0x1000;
use 32;
:blah
nop;
$tlb_base =  0x7000;
mov edx, $tlb_base;
mov cr3, edx;

#enable efer[lme]
mov ecx, 0xC0000080;
rdmsr;
bts eax, 8;
wrmsr;

#now enable paging
mov eax, cr0;
bts eax, 31;
mov cr0,eax;

$tlb_pointer = INIT_TLB $tlb_base;
PAE64_PML4E  0              0  0x00002001;
PAE64_PDPT   0  0           0  0x00005001;
PAE64_PDE    0  0 0         0  0x00000081;
PAE64_PDE    0  0 2         0  0x10000081;

PAGING $tlb_pointer;

jmp 0x28:$inlongmode;


:inlongmode
use 64;
mov rsp, $mystack;

#initialize feature control msr
mov ecx, 0x3a;
rdmsr;
bt eax, 0;
jc $skip_wrmsr;
mov eax, 5;
mov edx, 0;
wrmsr;

skip_wrmsr:
call $initialize_revision_id;

#do vmxon,vmclear,vmptrld sequence
vmxon [$vmxon_ptr];
jbe $test_fail;

vmclear [$vmcs_guest_ptr];
jbe $test_fail;

vmptrld [$vmcs_guest_ptr];
jbe $test_fail;

#now initialize the guest vmcs
mov rbx,&@vmcs;
call $std_vmcs_initialize_guest_vmcs;  # this label is from "std_vmx_code.inc"

#finally launch the vm
vmlaunch;

test_fail:
mov eax, 0xdead;
test_end:
hlt;

initialize_revision_id:
  mov ecx, 0x480;
  rdmsr;
  mov ebx, [$vmxon_ptr];
  mov [ebx], eax;
  mov ebx, [$vmcs_guest_ptr];
  mov [ebx], eax;
  ret;
  vmxon_ptr:
  dq 0x9000;
  vmcs_guest_ptr:
  dq 0xA000;

org 0x100000;  
include "/media/Data_Linux/tools/tpg/include/std_vmx_code.inc";  # this is the code to setup vm guest


$ept_base = 0xc000;
$ept_pointer = INIT_TLB $ept_base;

EPT_PAE64_PML4E  0              0  0x0000f007;
EPT_PAE64_PDPT   0  0           0  0x20000007;
EPT_PAE64_PDPT   0  8           0  0x00000007 1GB;
EPT_PAE64_PDE    0  0  0        0  0x00000087;

EPT $ept_pointer;

$tlb_base1 = 0xB000;
$tlb_pointer1 = INIT_TLB $tlb_base1;
PAE64_PML4E  0              0  0x0000D007;
PAE64_PDPT   0  0           0  0x0000E007;
PAE64_PDPT   0  1           2  0x00000007 1GB;
PAE64_PDE    0  0 0         0  0x00000087;
PAE64_PDE    0  0 2         0  0x10000087;

PAGING $tlb_pointer1;

$target_write = 0x40000000;
org 0x6000;
use 64;
guest_entry_point:
mov qword ptr [$target_write], r8;
vmcall;
hlt;

org $target_write;
 dd 0x1;

EPT 0;
org 0x20000;
PAGING $tlb_pointer;

v0_return:
vmclear [$vmcs_guest_ptr];
vmxoff;
hlt;

