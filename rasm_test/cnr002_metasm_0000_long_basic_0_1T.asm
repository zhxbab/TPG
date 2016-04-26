
   //##############################################################
   //OWNER:         root
   //PLUSARGS:       +MaxCMP:3000 +Max:100000 +apic:1  +cores:1 +STPG_VERSION:SIDE
   //INSTRUCTION:   
   //UNIT:          
   //MODE:          
   //EXCEPTIONS:     
   //KEYWORDS:      
   //DESCRIPTION:   
   //DATE ADDED:    Thu Apr 21 18:35:44 2016
   //##############################################################

// Found free low space at 0xc300 (0x100) for APIC_STORAGE0
# SETTING MEMORY ADDRESS 0x0000c300 SIZE 4 VALUE 0x0 (LINE = -1)
# SETTING MEMORY ADDRESS 0x0000c304 SIZE 4 VALUE 0x0 (LINE = -1)
# SETTING MEMORY ADDRESS 0x0000c308 SIZE 4 VALUE 0x0 (LINE = -1)
// APIC STORAGE AT 0x0000c300
// TLB BASE
// Found free low space at 0x33000 (0x1000) for TLB BASE
// Found free low space at 0xa450 (0x200) for THREAD TABLE
// Found free low space at 0xf800 (0x100) for JMP START
// Found free low space at 0xc400 (0x800) for JMP PM
// Found free low space at 0xa200 (0x100) for GDT TABLE
// Found free low space at 0x5900 (0x100) for IDT TABLE
// Found free low space at 0x36500 (0x100) for PM STACK BASE
// Found free low space at 0x97c00 (0x4000) for INTERRUPT BASE
// Found free low space at 0x14000 (0x8000) for INTERRUPT TABLE BASE
// Found free low space at 0x51400 (0x1000) for GDT START
// Found free low space at 0x32400 (0x800) for T0 STACK BASE
// T0 CODE START -- 0x6fa58000
// Found free low space at 0x54300 (0x100) for HALT

$gdt_table = 41472;
$idt_table = 22784;
$tlb_base =  208896;

org $gdt_table;
  dw 0x30;
  dd 332800;

org $idt_table;
  dw 0x4000;
  dd 81920;

org 332800;
  dd 0x00000000;
  dd 0x00000000;
  dd 0x0000FFFF;
  dd 0x00DF9B00; # cs 32 bit descriptor 
  dd 0x0000FFFF;
  dd 0x00DF9300; # ds 32bit
  dd 0x0000FFFF;
  dd 0x00CF9300; # ds 64bit
  dd 0x00000000;
  dd 0x00000000;
  dd 0x00000000;
  dd 0x00209B00;  # cs 64 bit descriptor code
  dd 0x00000000;
  dd 0x00000000;
  dd 0x0000FFFF;
  dd 0x00AF9B00;  # cs 64 bit descriptor code
  dd 0x0000FFFF;
  dd 0x004F9300;  # ds 32 bit descriptor code, G = 0 

use 16;
org 0xfffffff0;
	jmp 0x0:63488;
org 0x0000f800;
	lgdt [$gdt_table];
	lidt [$idt_table];
# enable 32 bit protect mode
	mov edx, cr0;
	or edx, 0x1;
	mov cr0, edx;
	mov esp, 0x000365c0;
	jmpf 0x0008:50176;
org 0x0000c400;
use 32;
include "/media/Data_Linux/centaur/bin/releases/stpg/page_tables/64bit/ia32e_4K.rasm"
	mov eax, $ptgen_tlb_0_base;
	mov cr3,eax;
	finit;
// Found free low space at 0x96000 (0x100) for APIC_STARTUP
	mov ebx,0x10;
	mov ds,ebx;
	mov ss,ebx;
	mov eax, 0x6A0;
	mov cr4, eax;
	mov eax, cr4;
	bts eax, 0x00000012;
	mov cr4, eax;
	mov ecx, 0x0;
	xgetbv;
	bts eax, 1;
	bts eax, 2;
	xsetbv;
	mov eax, 0x00000806;
	mov edx, 0;
	mov ecx, 0x000002ff;
//rem: $y0 28 "//runlog: Instr 28 - WRMSR IA32_MTRR_DEF_TYPE 0x02ff 0x00000000 0x00000806"
	wrmsr;
	mov ecx, 0xc0000080;
	rdmsr;
	bts eax, 8;
//rem: $y0 32 "//runlog: Instr 32 - RMWMSR IA32_EFER 0xc0000080 s8"
	wrmsr;
	mov eax,cr0;
	and eax,0x9fffffff;
	 or eax,0x80000020;
	mov cr0,eax;
	mov eax, 0x606A0;
	mov cr4,eax;
	jmpf 0x0028:$CODE_START;
org 0x00014000;

      dw ($int_0 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_0 >> 16) & 0xffff);
      dd (($int_0 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_1 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_1 >> 16) & 0xffff);
      dd (($int_1 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_2 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_2 >> 16) & 0xffff);
      dd (($int_2 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_3 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_3 >> 16) & 0xffff);
      dd (($int_3 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_4 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_4 >> 16) & 0xffff);
      dd (($int_4 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_5 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_5 >> 16) & 0xffff);
      dd (($int_5 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_6 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_6 >> 16) & 0xffff);
      dd (($int_6 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_7 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_7 >> 16) & 0xffff);
      dd (($int_7 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_8 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_8 >> 16) & 0xffff);
      dd (($int_8 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_9 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_9 >> 16) & 0xffff);
      dd (($int_9 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_10 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_10 >> 16) & 0xffff);
      dd (($int_10 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_11 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_11 >> 16) & 0xffff);
      dd (($int_11 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_12 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_12 >> 16) & 0xffff);
      dd (($int_12 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_13 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_13 >> 16) & 0xffff);
      dd (($int_13 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_14 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_14 >> 16) & 0xffff);
      dd (($int_14 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_15 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_15 >> 16) & 0xffff);
      dd (($int_15 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_16 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_16 >> 16) & 0xffff);
      dd (($int_16 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_17 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_17 >> 16) & 0xffff);
      dd (($int_17 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_18 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_18 >> 16) & 0xffff);
      dd (($int_18 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_19 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_19 >> 16) & 0xffff);
      dd (($int_19 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_20 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_20 >> 16) & 0xffff);
      dd (($int_20 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_21 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_21 >> 16) & 0xffff);
      dd (($int_21 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_22 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_22 >> 16) & 0xffff);
      dd (($int_22 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_23 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_23 >> 16) & 0xffff);
      dd (($int_23 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_24 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_24 >> 16) & 0xffff);
      dd (($int_24 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_25 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_25 >> 16) & 0xffff);
      dd (($int_25 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_26 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_26 >> 16) & 0xffff);
      dd (($int_26 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_27 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_27 >> 16) & 0xffff);
      dd (($int_27 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_28 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_28 >> 16) & 0xffff);
      dd (($int_28 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_29 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_29 >> 16) & 0xffff);
      dd (($int_29 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_30 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_30 >> 16) & 0xffff);
      dd (($int_30 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_31 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_31 >> 16) & 0xffff);
      dd (($int_31 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_32 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_32 >> 16) & 0xffff);
      dd (($int_32 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_33 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_33 >> 16) & 0xffff);
      dd (($int_33 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_34 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_34 >> 16) & 0xffff);
      dd (($int_34 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_35 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_35 >> 16) & 0xffff);
      dd (($int_35 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_36 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_36 >> 16) & 0xffff);
      dd (($int_36 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_37 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_37 >> 16) & 0xffff);
      dd (($int_37 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_38 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_38 >> 16) & 0xffff);
      dd (($int_38 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_39 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_39 >> 16) & 0xffff);
      dd (($int_39 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_40 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_40 >> 16) & 0xffff);
      dd (($int_40 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_41 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_41 >> 16) & 0xffff);
      dd (($int_41 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_42 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_42 >> 16) & 0xffff);
      dd (($int_42 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_43 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_43 >> 16) & 0xffff);
      dd (($int_43 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_44 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_44 >> 16) & 0xffff);
      dd (($int_44 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_45 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_45 >> 16) & 0xffff);
      dd (($int_45 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_46 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_46 >> 16) & 0xffff);
      dd (($int_46 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_47 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_47 >> 16) & 0xffff);
      dd (($int_47 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_48 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_48 >> 16) & 0xffff);
      dd (($int_48 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_49 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_49 >> 16) & 0xffff);
      dd (($int_49 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_50 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_50 >> 16) & 0xffff);
      dd (($int_50 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_51 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_51 >> 16) & 0xffff);
      dd (($int_51 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_52 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_52 >> 16) & 0xffff);
      dd (($int_52 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_53 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_53 >> 16) & 0xffff);
      dd (($int_53 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_54 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_54 >> 16) & 0xffff);
      dd (($int_54 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_55 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_55 >> 16) & 0xffff);
      dd (($int_55 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_56 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_56 >> 16) & 0xffff);
      dd (($int_56 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_57 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_57 >> 16) & 0xffff);
      dd (($int_57 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_58 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_58 >> 16) & 0xffff);
      dd (($int_58 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_59 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_59 >> 16) & 0xffff);
      dd (($int_59 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_60 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_60 >> 16) & 0xffff);
      dd (($int_60 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_61 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_61 >> 16) & 0xffff);
      dd (($int_61 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_62 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_62 >> 16) & 0xffff);
      dd (($int_62 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_63 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_63 >> 16) & 0xffff);
      dd (($int_63 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_64 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_64 >> 16) & 0xffff);
      dd (($int_64 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_65 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_65 >> 16) & 0xffff);
      dd (($int_65 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_66 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_66 >> 16) & 0xffff);
      dd (($int_66 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_67 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_67 >> 16) & 0xffff);
      dd (($int_67 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_68 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_68 >> 16) & 0xffff);
      dd (($int_68 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_69 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_69 >> 16) & 0xffff);
      dd (($int_69 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_70 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_70 >> 16) & 0xffff);
      dd (($int_70 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_71 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_71 >> 16) & 0xffff);
      dd (($int_71 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_72 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_72 >> 16) & 0xffff);
      dd (($int_72 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_73 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_73 >> 16) & 0xffff);
      dd (($int_73 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_74 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_74 >> 16) & 0xffff);
      dd (($int_74 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_75 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_75 >> 16) & 0xffff);
      dd (($int_75 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_76 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_76 >> 16) & 0xffff);
      dd (($int_76 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_77 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_77 >> 16) & 0xffff);
      dd (($int_77 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_78 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_78 >> 16) & 0xffff);
      dd (($int_78 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_79 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_79 >> 16) & 0xffff);
      dd (($int_79 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_80 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_80 >> 16) & 0xffff);
      dd (($int_80 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_81 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_81 >> 16) & 0xffff);
      dd (($int_81 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_82 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_82 >> 16) & 0xffff);
      dd (($int_82 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_83 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_83 >> 16) & 0xffff);
      dd (($int_83 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_84 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_84 >> 16) & 0xffff);
      dd (($int_84 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_85 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_85 >> 16) & 0xffff);
      dd (($int_85 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_86 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_86 >> 16) & 0xffff);
      dd (($int_86 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_87 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_87 >> 16) & 0xffff);
      dd (($int_87 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_88 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_88 >> 16) & 0xffff);
      dd (($int_88 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_89 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_89 >> 16) & 0xffff);
      dd (($int_89 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_90 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_90 >> 16) & 0xffff);
      dd (($int_90 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_91 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_91 >> 16) & 0xffff);
      dd (($int_91 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_92 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_92 >> 16) & 0xffff);
      dd (($int_92 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_93 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_93 >> 16) & 0xffff);
      dd (($int_93 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_94 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_94 >> 16) & 0xffff);
      dd (($int_94 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_95 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_95 >> 16) & 0xffff);
      dd (($int_95 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_96 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_96 >> 16) & 0xffff);
      dd (($int_96 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_97 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_97 >> 16) & 0xffff);
      dd (($int_97 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_98 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_98 >> 16) & 0xffff);
      dd (($int_98 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_99 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_99 >> 16) & 0xffff);
      dd (($int_99 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_100 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_100 >> 16) & 0xffff);
      dd (($int_100 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_101 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_101 >> 16) & 0xffff);
      dd (($int_101 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_102 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_102 >> 16) & 0xffff);
      dd (($int_102 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_103 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_103 >> 16) & 0xffff);
      dd (($int_103 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_104 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_104 >> 16) & 0xffff);
      dd (($int_104 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_105 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_105 >> 16) & 0xffff);
      dd (($int_105 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_106 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_106 >> 16) & 0xffff);
      dd (($int_106 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_107 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_107 >> 16) & 0xffff);
      dd (($int_107 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_108 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_108 >> 16) & 0xffff);
      dd (($int_108 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_109 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_109 >> 16) & 0xffff);
      dd (($int_109 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_110 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_110 >> 16) & 0xffff);
      dd (($int_110 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_111 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_111 >> 16) & 0xffff);
      dd (($int_111 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_112 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_112 >> 16) & 0xffff);
      dd (($int_112 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_113 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_113 >> 16) & 0xffff);
      dd (($int_113 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_114 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_114 >> 16) & 0xffff);
      dd (($int_114 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_115 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_115 >> 16) & 0xffff);
      dd (($int_115 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_116 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_116 >> 16) & 0xffff);
      dd (($int_116 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_117 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_117 >> 16) & 0xffff);
      dd (($int_117 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_118 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_118 >> 16) & 0xffff);
      dd (($int_118 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_119 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_119 >> 16) & 0xffff);
      dd (($int_119 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_120 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_120 >> 16) & 0xffff);
      dd (($int_120 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_121 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_121 >> 16) & 0xffff);
      dd (($int_121 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_122 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_122 >> 16) & 0xffff);
      dd (($int_122 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_123 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_123 >> 16) & 0xffff);
      dd (($int_123 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_124 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_124 >> 16) & 0xffff);
      dd (($int_124 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_125 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_125 >> 16) & 0xffff);
      dd (($int_125 >> 32) & 0xffffffff);
      dd 0x00000000;

      dw ($int_126 & 0xffff);
      dw 0x28;
      db 0x00;
      db 0x8E;
      dw (($int_126 >> 16) & 0xffff);
      dd (($int_126 >> 32) & 0xffffffff);
      dd 0x00000000;
// Found free low space at 0x60100 (0xa00) for $INTERRUPT_TOTAL
// Found free low space at 0x6a600 (0x100) for $SCRATCH_SPACE
// INTERRUPT TOTAL COUNT 0x060100
org 0x00097c00;
use 64;
:int_0
	add rsp, 0x8;
	push rbx;
# SETTING MEMORY ADDRESS 0x00060100 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393472];
	 iretq;
:int_1
# SETTING MEMORY ADDRESS 0x00060104 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393476];
	 iretq;
:int_2
# SETTING MEMORY ADDRESS 0x00060108 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393480];
	 iretq;
:int_3
# SETTING MEMORY ADDRESS 0x0006010c SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393484];
	 iretq;
:int_4
# SETTING MEMORY ADDRESS 0x00060110 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393488];
	 iretq;
:int_5
# SETTING MEMORY ADDRESS 0x00060114 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393492];
	 iretq;
:int_6
# SETTING MEMORY ADDRESS 0x00060118 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393496];
	 iretq;
:int_7
# SETTING MEMORY ADDRESS 0x0006011c SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393500];
	 iretq;
:int_8
# SETTING MEMORY ADDRESS 0x00060120 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393504];
	 iretq;
:int_9
# SETTING MEMORY ADDRESS 0x00060124 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393508];
	 iretq;
:int_10
# SETTING MEMORY ADDRESS 0x00060128 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393512];
	 iretq;
:int_11
# SETTING MEMORY ADDRESS 0x0006012c SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393516];
	 iretq;
:int_12
# SETTING MEMORY ADDRESS 0x00060130 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393520];
	 iretq;
:int_13
	 add rsp, 0x8;
# SETTING MEMORY ADDRESS 0x00060134 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393524];
	 iretq;
:int_14
# SETTING MEMORY ADDRESS 0x00060138 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393528];
	 iretq;
:int_15
# SETTING MEMORY ADDRESS 0x0006013c SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393532];
	 iretq;
:int_16
# SETTING MEMORY ADDRESS 0x0006a600 SIZE 4 VALUE 0x37f (LINE = -1)
	 fnclex;
	 fldcw [435712];
# SETTING MEMORY ADDRESS 0x00060140 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393536];
	 iretq;
:int_17
# SETTING MEMORY ADDRESS 0x00060144 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393540];
	 iretq;
:int_18
# SETTING MEMORY ADDRESS 0x00060148 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393544];
	 iretq;
:int_19
# SETTING MEMORY ADDRESS 0x0006a604 SIZE 4 VALUE 0x1f80 (LINE = -1)
	 ldmxcsr [435716];
# SETTING MEMORY ADDRESS 0x0006014c SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393548];
	 iretq;
:int_20
# SETTING MEMORY ADDRESS 0x00060150 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393552];
	 iretq;
:int_21
# SETTING MEMORY ADDRESS 0x00060154 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393556];
	 iretq;
:int_22
# SETTING MEMORY ADDRESS 0x00060158 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393560];
	 iretq;
:int_23
# SETTING MEMORY ADDRESS 0x0006015c SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393564];
	 iretq;
:int_24
# SETTING MEMORY ADDRESS 0x00060160 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393568];
	 iretq;
:int_25
# SETTING MEMORY ADDRESS 0x00060164 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393572];
	 iretq;
:int_26
# SETTING MEMORY ADDRESS 0x00060168 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393576];
	 iretq;
:int_27
# SETTING MEMORY ADDRESS 0x0006016c SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393580];
	 iretq;
:int_28
# SETTING MEMORY ADDRESS 0x00060170 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393584];
	 iretq;
:int_29
# SETTING MEMORY ADDRESS 0x00060174 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393588];
	 iretq;
:int_30
# SETTING MEMORY ADDRESS 0x00060178 SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393592];
	 iretq;
:int_31
# SETTING MEMORY ADDRESS 0x0006017c SIZE 4 VALUE 0x0 (LINE = -1)
	 db 0xf0; inc dword [393596];
	 iretq;
:int_32
use 64;
 cli;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 32;
 mov [49928], 32;
 push rax;
 mov rax,0xF3;
 out 0x80,al;
mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
 sti;
 iretq;

:int_33
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 33;
 mov [49928], 33;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_34
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 34;
 mov [49928], 34;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_35
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 35;
 mov [49928], 35;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_36
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 36;
 mov [49928], 36;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_37
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 37;
 mov [49928], 37;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_38
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 38;
 mov [49928], 38;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_39
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 39;
 mov [49928], 39;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_40
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 40;
 mov [49928], 40;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_41
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 41;
 mov [49928], 41;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_42
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 42;
 mov [49928], 42;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_43
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 43;
 mov [49928], 43;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_44
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 44;
 mov [49928], 44;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_45
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 45;
 mov [49928], 45;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_46
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 46;
 mov [49928], 46;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_47
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 47;
 mov [49928], 47;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_48
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 48;
 mov [49928], 48;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_49
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 49;
 mov [49928], 49;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_50
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 50;
 mov [49928], 50;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_51
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 51;
 mov [49928], 51;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_52
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 52;
 mov [49928], 52;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_53
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 53;
 mov [49928], 53;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_54
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 54;
 mov [49928], 54;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_55
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 55;
 mov [49928], 55;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_56
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 56;
 mov [49928], 56;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_57
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 57;
 mov [49928], 57;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_58
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 58;
 mov [49928], 58;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_59
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 59;
 mov [49928], 59;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_60
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 60;
 mov [49928], 60;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_61
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 61;
 mov [49928], 61;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_62
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 62;
 mov [49928], 62;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_63
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 63;
 mov [49928], 63;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_64
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 64;
 mov [49928], 64;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_65
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 65;
 mov [49928], 65;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_66
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 66;
 mov [49928], 66;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_67
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 67;
 mov [49928], 67;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_68
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 68;
 mov [49928], 68;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_69
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 69;
 mov [49928], 69;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_70
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 70;
 mov [49928], 70;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_71
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 71;
 mov [49928], 71;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_72
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 72;
 mov [49928], 72;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_73
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 73;
 mov [49928], 73;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_74
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 74;
 mov [49928], 74;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_75
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 75;
 mov [49928], 75;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_76
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 76;
 mov [49928], 76;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_77
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 77;
 mov [49928], 77;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_78
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 78;
 mov [49928], 78;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_79
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 79;
 mov [49928], 79;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_80
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 80;
 mov [49928], 80;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_81
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 81;
 mov [49928], 81;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_82
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 82;
 mov [49928], 82;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_83
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 83;
 mov [49928], 83;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_84
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 84;
 mov [49928], 84;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_85
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 85;
 mov [49928], 85;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_86
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 86;
 mov [49928], 86;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_87
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 87;
 mov [49928], 87;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_88
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 88;
 mov [49928], 88;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_89
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 89;
 mov [49928], 89;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_90
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 90;
 mov [49928], 90;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_91
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 91;
 mov [49928], 91;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_92
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 92;
 mov [49928], 92;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_93
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 93;
 mov [49928], 93;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_94
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 94;
 mov [49928], 94;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_95
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 95;
 mov [49928], 95;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_96
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 96;
 mov [49928], 96;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_97
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 97;
 mov [49928], 97;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_98
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 98;
 mov [49928], 98;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_99
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 99;
 mov [49928], 99;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_100
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 100;
 mov [49928], 100;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_101
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 101;
 mov [49928], 101;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_102
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 102;
 mov [49928], 102;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_103
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 103;
 mov [49928], 103;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_104
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 104;
 mov [49928], 104;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_105
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 105;
 mov [49928], 105;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_106
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 106;
 mov [49928], 106;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_107
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 107;
 mov [49928], 107;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_108
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 108;
 mov [49928], 108;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_109
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 109;
 mov [49928], 109;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_110
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 110;
 mov [49928], 110;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_111
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 111;
 mov [49928], 111;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_112
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 112;
 mov [49928], 112;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_113
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 113;
 mov [49928], 113;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_114
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 114;
 mov [49928], 114;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_115
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 115;
 mov [49928], 115;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_116
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 116;
 mov [49928], 116;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_117
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 117;
 mov [49928], 117;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_118
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 118;
 mov [49928], 118;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_119
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 119;
 mov [49928], 119;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_120
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 120;
 mov [49928], 120;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_121
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 121;
 mov [49928], 121;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_122
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 122;
 mov [49928], 122;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_123
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 123;
 mov [49928], 123;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_124
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 124;
 mov [49928], 124;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_125
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 125;
 mov [49928], 125;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:int_126
use 64;
 db 0xf0; inc dword [49920];
 db 0xf0; add dword [49924], 126;
 mov [49928], 126;
 sti;
 push rax;
 mov rax, 4276093104;
 mov dword [eax],0x0;
 pop rax;
iretq;

:CODE_START
use 64;
	mov ebx,0x18;
	mov ds,ebx;
	mov ss,ebx;
	mov eax, 0xfee00020;
	mov eax, dword [eax];
	shr eax, 24 - (8 / 2);
	mov rsp, [eax + ($THREAD_DATA + 8)];
	call [eax + $THREAD_DATA];
org 0x0000a450;
:THREAD_DATA
	 dd 0x6fa58000;
	 dd 0x00000000;
	 dd 0x000327c0;
	 dd 0x00000000;
	 dd 0x6fa58000;
	 dd 0x00000000;
	 dd 0x000327c0;
	 dd 0x00000000;
	 dd 0x6fa58000;
	 dd 0x00000000;
	 dd 0x000327c0;
	 dd 0x00000000;
	 dd 0x6fa58000;
	 dd 0x00000000;
	 dd 0x000327c0;
	 dd 0x00000000;
	 dd 0x6fa58000;
	 dd 0x00000000;
	 dd 0x000327c0;
	 dd 0x00000000;
	 dd 0x6fa58000;
	 dd 0x00000000;
	 dd 0x000327c0;
	 dd 0x00000000;
	 dd 0x6fa58000;
	 dd 0x00000000;
	 dd 0x000327c0;
	 dd 0x00000000;
	 dd 0x6fa58000;
	 dd 0x00000000;
	 dd 0x000327c0;
	 dd 0x00000000;
use 16;
org 0x00096000;
	jmp 0x0:63488;
use 64;
$T0_code1 = $curraddr;
org 0x6fa58000;
# starting the test for thread 0
# THREAD 0 INSTRUCTION COUNT = 48
# Tag 1
$T0_code2 = $curraddr;
org $T0_code2;
# THREAD 0 INSTRUCTION COUNT = 48
mov eax,0x1;
$T0_code3 = $curraddr;
org $T0_code3;
# THREAD 0 INSTRUCTION COUNT = 48
	jmp $halt_location;
org 0x00054300;
:halt_location
	hlt;
	hlt;
	hlt;
	hlt;
$T0_code4 = $curraddr;
org $T0_code4;
# THREAD 0 INSTRUCTION COUNT = 50
//ctrl: thread 0 exec 50
// cnsim -va -no-tbdm-warnings -check-unused-directives  -no-apic-intr -no-stack -short -trait-change -als -mem 0xF4 -seed 3075530756
