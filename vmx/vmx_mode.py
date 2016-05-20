#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' vmx mode module '
__author__ = 'Ken Zhao'
########################################################
# vmx mode module inherit from mode
########################################################
import os, sys
from operator import eq, ne
sys.path.append("/%s/../src"%(sys.path[0]))
from mode import Mode
class Vmx_mode(Mode):
    def __init__(self,hlt_code,mpg, instr_manager, ptg, threads, simcmd, intel, interrupt,c_parser=None):
        self.inc_path = ""
        self.hlt_code = hlt_code
        Mode.__init__(self,mpg, instr_manager, ptg, threads, simcmd, intel, interrupt,c_parser)
        
    def Mode_code(self,mode,c_gen):
        self.mode = mode
        self.Comment("###########################vars definition######################")
        gdt_table_base = self.mpg.Apply_mem(0x1000,16,start=0,end=0x10000,name="gdt_table_base") # for 512 gdt descriptor
        idt_table_base = self.mpg.Apply_mem(0x1000,16,start=0,end=0x10000,name="idt_table_base") # 256 interrupt and every gate is 128bit
        self.Vars_write(gdt_table_base["name"],gdt_table_base["start"])
        self.Vars_write(idt_table_base["name"],idt_table_base["start"])
        self.gdt_table_base_pointer = self.Set_table_pointer(gdt_table_base["name"])
        self.idt_table_base_pointer = self.Set_table_pointer(idt_table_base["name"])
        self.Set_gdt_table(gdt_table_base,c_gen)
        self.Set_idt_table(idt_table_base)
        self.Set_user_code_stack(c_gen)
        self.Comment("#### VMX PAGE ####")
        self.Gen_vmx_page_addr()
        self.Set_guest_entry()
        self.Set_vmcs()
        self.Text_write("&TO_MEMORY_ALL()")
        self.Set_int_handler()
        if self.mode == "protect_mode":
            self.Protect_mode_code()
        else:
            self.Long_mode_code()
        return [self.stack_segs,self.user_code_segs]
    
    def Set_vmcs(self):
        #self.Text_write("include \"%s/std_vmx_code.inc\""%(self.inc_path))
        self.vmcs = self.mpg.Apply_mem(0x2000,16,start=0x1000,end=0xA0000,name="vmcs")
        self.Text_write("org 0x%x"%(self.vmcs["start"]))
        self.Comment("#### Set host ####")
        self.Text_write("@vmcs = new std::vmcs::data")
        self.Text_write("@vmcs.host_gdtr_base = 0x%x"%(self.gdt_table_base_pointer["start"]))
        self.Text_write("@vmcs.host_cs_sel = &SELECTOR($%s)"%(self.selector_name_cs_0))
        self.Text_write("@vmcs.host_ss_sel = &SELECTOR($%s)"%(self.selector_name_ds_0))
        self.Text_write("@vmcs.host_tr_sel = &SELECTOR($%s)"%(self.selector_name_ds_0)) #FIXME - must point to a tss selector
        self.Text_write("@vmcs.virtual_apic_page_addr_full = 0x%x"%(self.ptg.vmx_tlb_base["start"]))
        self.Text_write("@vmcs.ept_pointer_full = 0x%x"%(self.ptg.ept_tlb_base["start"]))
        self.Text_write("@vmcs.host_rip = 0x%x"%(self.hlt_code["start"]))
        self.Text_write("@vmcs.host_rsp = 0x%x"%(self.stack_segs[self.threads-1]["end"]))
        self.Comment("#### Set client ####")
        self.Text_write("@vmcs.guest_gdtr_base = 0x%x"%(self.gdt_table_base_pointer["start"])) #FIXME - must point to a tss selector
        self.Text_write("@vmcs.guest_cs_sel= &SELECTOR($%s)"%(self.selector_name_cs_0))
        self.Text_write("@vmcs.guest_tr_sel = &SELECTOR($%s)"%(self.selector_name_ds_0)) #FIXME - must point to a tss selector
        self.Text_write("@vmcs.guest_rip = 0x%x"%(self.vmx_guest_entry_0["start"]))
        self.Text_write("@vmcs.guest_rsp = 0x%x"%(self.stack_segs[self.threads-1]["end"]))
        
    def Gen_vmx_page_addr(self):
        self.ptg.Gen_vmx_page_2M_addr()
        self.ptg.Gen_ept_2M_addr()

    def Write_vmx_page(self):
        self.ptg.Write_vmx_page_2M()
        self.ptg.Write_ept_2M()


    def Set_guest_entry(self):
        self.vmx_guest_entry_0 = self.mpg.Apply_mem(0x100,16,start=0x1000,end=0xA0000,name="vmx_guest_entry_0")
        self.Text_write("org 0x%x"%(self.vmx_guest_entry_0["start"]))
        self.Text_write("use 64")
        self.Instr_write("mov qword ptr [0x40000000], r8")
        self.Instr_write("vmcall")
        self.Instr_write("hlt")



    def Long_mode_code(self):
        self.Comment("###########################Long mode code######################")
        self.Text_write("org 0xFFFFFFF0")
        self.Text_write("use 16")
        real_mode_code_start = self.mpg.Apply_mem(0x100,16,start=0x1000,end=0x10000,name="real_mode_code_start")
        self.Instr_write("jmp 0x0:0x%x"%(real_mode_code_start["start"]))
        ########################################################################
        if self.threads > 1:
            self.Comment("##########AP init address and code###############")
            self.apic_jmp_addr = self.mpg.Apply_mem(0x100,0x1000,start=0x1000,end=0xA0000,name="apic_jmp_addr") # used for apic jmp
            self.Text_write("org 0x%x"%(self.apic_jmp_addr["start"]))
            self.Text_write("use 16")
            self.Instr_write("jmp 0x0:0x%x"%(real_mode_code_start["start"]))
        ########################################################################
        self.Comment("##real mode code")    
        self.Text_write("org 0x%x"%(real_mode_code_start["start"]))
        self.Instr_write("lgdt [&@%s]"%(self.gdt_table_base_pointer["name"]))
        self.Instr_write("lidt [&@%s]"%(self.idt_table_base_pointer["name"]))
        self.Comment("##enable 32bit mode")
        protect_mode_code_start = self.mpg.Apply_mem(0x1000,16,start=0x1000,end=0xA0000,name="protect_mode_code_start")#0xA0000-0x100000 is for BIOS
        self.Instr_write("mov edx,cr0")
        self.Instr_write("or edx,0x1")
        self.Instr_write("mov cr0,edx")
        self.Instr_write("jmpf &SELECTOR($%s):0x%x"%(self.selector_name_cs32_0,protect_mode_code_start["start"]))
        self.Text_write("org 0x%x"%(protect_mode_code_start["start"]))
        self.Text_write("use 32")
        self.Comment("##enable pae,fxsave(sse),simd,global page")
        self.Instr_write("mov eax,cr4")
        self.Instr_write("or eax,0x6A0")
        self.Instr_write("mov cr4,eax")
        self.Comment("##set IA32_EFER eax to 0x0")
        self.Comment("#In Intel spec IA32_EFER bit 9 is reversed, if write this bit, it fails in pclmsi")
        self.Msr_Write(0xc0000080,eax=0x0)
        self.Comment("#enable fpu")
        self.Instr_write("finit")
        self.Comment("#change to ds32")
        self.Instr_write("mov ebx,&SELECTOR($%s)"%(self.selector_name_ds32_0))
        self.Instr_write("mov ds,bx")
        self.Instr_write("mov ss,bx")
        #################################For multi threads#####################################
        if self.threads > 1:
            self.Msr_Write(0x200,0,edx=0x0,eax=0xfee00000)
            self.Msr_Write(0x201,0,edx=0xF,eax=0xfffff800)
            self.Instr_write("mov eax,0xfee00020")
            self.Instr_write("mov eax,dword [eax]") # get apic id
            self.Instr_write("cmp eax,0x0")
            self.Instr_write("jne $SKIP_WAKEUP")
            self.Comment("#####Set ICR(0x300,0x310), and INIT AP")
            self.Instr_write("mov eax,0xfee00310")
            self.Instr_write("mov dword [eax],(0<<24)")
            self.Instr_write("mov eax,0xfee00300")
            self.Instr_write("mov dword [eax],0xc06%02x"%(self.apic_jmp_addr["start"]/0x1000))
            self.Tag_write("SKIP_WAKEUP")
        #######################################################################################
        self.Comment("##enable xsave(xset/xget), this will fail in intel celeron platform")
        self.Instr_write("mov eax,cr4")
        self.Instr_write("bts eax,0x12")
        self.Instr_write("mov cr4,eax")
        self.Comment("##enable avx")
        self.Instr_write("mov ecx,0x0") #ecx must be 0 for xgetbv
        self.Instr_write("xgetbv")
        self.Instr_write("bts eax,0x1")
        self.Instr_write("bts eax,0x2")
        self.Instr_write("xsetbv")
        self.Comment("##set cache default")
        self.Msr_Write(0x2ff,eax=0x806,edx=0x0)
        ####### set page and cr3##################
        self.ptg.Gen_page()
        self.long_mode_code_start = self.mpg.Apply_mem(0x1000,16,start=0x1000,end=0xA0000,name="long_mode_code_start")
        ########enter compatibility_mode######################
        self.Comment("##enable IA32e mode")
        self.Msr_Rmw(0xc0000080,"s8")
        self.Instr_write("mov eax,cr0")
        self.Instr_write("and eax,0x9fffffff")
        self.Instr_write("or eax,0x80000020")
        self.Instr_write("mov cr0,eax")
        self.Comment("##enable PCID")
        self.Instr_write("mov eax, 0x606A0")
        self.Instr_write("mov cr4,eax")
        ########enter long mode###############################
        self.Instr_write("jmpf &SELECTOR($%s):0x%x"%(self.selector_name_cs_0,self.long_mode_code_start["start"]))         
        self.Text_write("org 0x%x"%(self.long_mode_code_start["start"]))
        if self.mode == "long_mode":
            self.Text_write("use 64")
        else:
            self.Text_write("use 32")  
        self.Instr_write("mov ebx,&SELECTOR($%s)"%(self.selector_name_ds_0))
        self.Instr_write("mov es,bx")#compatibility_mode need to set es
        self.Instr_write("mov fs,bx")
        self.Instr_write("mov gs,bx")
        self.Instr_write("mov eax,0xfee00020")
        self.Instr_write("mov eax,dword [eax]") # get apic id        
        self.Instr_write("shr eax, 24 - (8 / 2)")
        if self.intel:
            for i in range(0,self.threads):
                if i == 0x0:
                    self.instr_manager.Set_instr(67,0)
                    self.simcmd.Add_sim_cmd("at $y%d >= %d set register EAX to 0x000000%02x"%(i,self.instr_manager.Get_instr(i),i*0x20),i)
                else:
                    self.instr_manager.Set_instr(63,i)
                    self.simcmd.Add_sim_cmd("at $y%d >= %d set register EAX to 0x000000%02x"%(i,self.instr_manager.Get_instr(i),i*0x20),i)
                    
        self.Comment("##set stack")
        if self.mode == "long_mode":
            self.Instr_write("mov rsp,[eax+&@%s+8]"%(self.thread_info_pointer["name"]))
        else:
            self.Instr_write("mov esp,[eax+&@%s+8]"%(self.thread_info_pointer["name"]))
        self.Comment("#### initialize feature control msr ####")
        self.Instr_write("mov ecx, 0x3a")
        self.Instr_write("rdmsr")
        self.Instr_write("bt eax, 0")
        self.Instr_write("jc $skip_wrmsr")
        self.Msr_Write(0x3a,0,edx=0,eax=5)
        self.Tag_write("skip_wrmsr")
        self.Comment("#### initialize_revision_id ####")
        self.Msr_Read(0x480,0)
        self.Instr_write("mov ebx,[0x%x]"%(self.stack_segs[self.threads-1]["end"]))
        self.Instr_write("mov [ebx], eax")
        #self.Instr_write("mov ebx, [$vmcs_guest_ptr]")
        #self.Instr_write("mov [ebx], eax")
        self.Instr_write("ret")

        for i in range(0,self.threads):
            if i == 0x0:
                self.instr_manager.Set_instr(69,0)
            else:
                self.instr_manager.Set_instr(65,i)
 
