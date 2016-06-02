#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' mode module '
__author__ = 'Ken Zhao'
########################################################
# mode module is used to generate different mode code
########################################################
from operator import eq, ne
from util import Util
from logging import info, error, debug, warning, critical
class Mode(Util):
    def __init__(self, mpg, instr_manager, ptg, threads, simcmd, intel, interrupt,c_parser=None):
        self.mpg = mpg
        self.instr_manager = instr_manager
        self.ptg = ptg
        self.threads = threads
        self.simcmd = simcmd
        self.intel = intel
        self.interrupt = interrupt
        self.c_parser = c_parser
        
    def Set_table_pointer(self,table_name):
        table_pointer = self.mpg.Apply_mem(0x10,16,start=0x0,end=0x10000,name="%s_pointer"%(table_name)) #0x10000 = 64KB, in real mode(B=0), the limit of segment is 0xFFFF
        self.Text_write("org 0x%x"%(table_pointer["start"]))
        self.Text_write("@%s = new std::table_pointer"%(table_pointer["name"]))
        self.Text_write("@%s.base = $%s"%(table_pointer["name"],table_name))
        self.Text_write("@%s.limit = 0xFFFF"%(table_pointer["name"]))
        return table_pointer
    

    def Set_user_code_stack(self,c_gen):
        self.Comment("###########################Thread Info######################")
        stack_align = 0x100
        self.stack_segs = []
        self.user_code_segs = []
        self.thread_info_pointer = self.mpg.Apply_mem(0x100,16,start=0x0,end=0x10000,name="thread_info_pointer")
        self.Text_write("org 0x%x"%(self.thread_info_pointer["start"]))
        self.Text_write("@%s = new std::thread_info[%d]"%(self.thread_info_pointer["name"],8))#support 8 threads
        for i in range(0,self.threads):
            if c_gen == 0x0:
                self.stack_seg = self.mpg.Apply_mem(0x40000,stack_align,start=0xB00000,end=0x1000000,name="stack_seg_T%d"%(i))
                self.user_code_seg = self.mpg.Apply_mem(0x800000,stack_align,start=0x1000000,end=0x80000000,name="user_code_seg_T%d"%(i))
            else:
                self.stack_seg = self.mpg.Apply_mem(0x40000,stack_align,start=0xB00000,end=0x1000000,name="stack_seg_T%d"%(i))
                self.user_code_seg = self.mpg.Apply_mem(0x800000,stack_align,start=0x20000000,end=0x80000000,name="user_code_seg_T%d"%(i))
                self.Comment("##########Initial stack###########")
                self.Text_write("org 0x%08x"%(self.stack_seg["start"]))
                for j in range(0,0x100000,8):
                    self.Text_write("dq 0x0000000000000000")
                self.Comment("##########Initial stack end###########")
            if self.mode == "long_mode":
                self.stack_seg["end"] = self.stack_seg["start"]+self.stack_seg["size"]-stack_align+0x8
            else:
                self.stack_seg["end"] = self.stack_seg["start"]+self.stack_seg["size"]-stack_align+0x4
            # because need to execute call user_code, esp will -4,
            #so in there resever some space
            self.stack_segs.append(self.stack_seg)
            self.user_code_segs.append(self.user_code_seg)
            if self.intel:
                intel_id = i * 2
                self.Text_write("@%s[%d].stack = 0x%016x"%(self.thread_info_pointer["name"],intel_id,self.stack_seg["end"]))
                self.Text_write("@%s[%d].code = 0x%016x"%(self.thread_info_pointer["name"],intel_id,self.user_code_seg["start"]))
            else:
                self.Text_write("@%s[%d].stack = 0x%016x"%(self.thread_info_pointer["name"],i,self.stack_seg["end"]))
                self.Text_write("@%s[%d].code = 0x%016x"%(self.thread_info_pointer["name"],i,self.user_code_seg["start"]))
    
    def Mode_code(self,mode,c_gen,disable_avx,disable_pcid):
        self.disable_avx = disable_avx
        self.mode = mode
        self.disable_pcid = disable_pcid
        self.Comment("###########################vars definition######################")
        gdt_table_base = self.mpg.Apply_mem(0x1000,16,start=0,end=0x10000,name="gdt_table_base") # for 512 gdt descriptor
        idt_table_base = self.mpg.Apply_mem(0x1000,16,start=0,end=0x10000,name="idt_table_base") # 256 interrupt and every gate is 128bit
        self.Vars_write(gdt_table_base["name"],gdt_table_base["start"])
        self.Vars_write(idt_table_base["name"],idt_table_base["start"])
        self.gdt_table_base_pointer = self.Set_table_pointer(gdt_table_base["name"])
        self.idt_table_base_pointer = self.Set_table_pointer(idt_table_base["name"])
        self.Set_gdt_table(gdt_table_base,c_gen)
        self.Set_idt_table(idt_table_base)
        self.ptg.Gen_page()
        self.Set_user_code_stack(c_gen)
        self.Text_write("&TO_MEMORY_ALL()")
        self.Set_int_handler()
        if self.mode == "protect_mode":
            self.Protect_mode_code()
        else:
            self.Long_mode_code()
        return [self.stack_segs,self.user_code_segs]
    
    def Set_int_handler(self):
        self.interrupt.Write_interrupt()
    
    def Set_idt_table(self,idt_table_base):
        self.Comment("###########################IDT definition######################")       
        self.Text_write("org 0x%x"%(idt_table_base["start"]))
        if self.mode == "protect_mode":
            idt_gate_type = "idt_gate_32"
            idt_selector = self.selector_name_cs32_0
        else:
            idt_gate_type = "idt_gate_64"
            idt_selector = self.selector_name_cs64_0
        self.Text_write("@idt = new std::%s[256]"%(idt_gate_type))
        for i in range(0,256):
            self.Text_write("@idt[%d].selector = &SELECTOR($%s)"%(i,idt_selector))
            self.Text_write("@idt[%d].offset = $int%i_handler"%(i,i))

        
    def Set_gdt_table(self,gdt_table_base,c_gen):
        self.Comment("###########################GDT definition######################")
        self.Text_write("org 0x%x"%(gdt_table_base["start"]))
        self.Text_write("@gdt = new std::descriptor[10]")
        self.selector_name_cs32_0 = "cs32"
        self.selector_value_cs32_0 = 0x1
        self.Vars_write(self.selector_name_cs32_0,self.selector_value_cs32_0)
        self.Text_write("@gdt[$%s].type = 0xB"%(self.selector_name_cs32_0))
        self.Text_write("@gdt[$%s].db = 0x1"%(self.selector_name_cs32_0))
        self.selector_name_ds32_0 = "ds32"
        self.selector_value_ds32_0 = 0x2
        self.Vars_write(self.selector_name_ds32_0,self.selector_value_ds32_0)
        self.Text_write("@gdt[$%s].type = 0x3"%(self.selector_name_ds32_0))
        self.Text_write("@gdt[$%s].db = 0x1"%(self.selector_name_ds32_0))
        self.selector_name_cs64_0 = "cs64"
        self.selector_value_cs64_0 = 0x3
        self.Vars_write(self.selector_name_cs64_0,self.selector_value_cs64_0)
        self.Text_write("@gdt[$%s].type = 0xB"%(self.selector_name_cs64_0))
        self.Text_write("@gdt[$%s].l = 0x1"%(self.selector_name_cs64_0))
        self.selector_name_ds64_0 = "ds64"
        self.selector_value_ds64_0 = 0x4
        self.Vars_write(self.selector_name_ds64_0,self.selector_value_ds64_0)
        self.Text_write("@gdt[$%s].type = 0x3"%(self.selector_name_ds64_0))
        self.Text_write("@gdt[$%s].l = 0x1"%(self.selector_name_ds64_0))               
        if self.mode == "compatibility_mode" :
            self.selector_name_cs_0 = self.selector_name_cs32_0
            self.selector_name_ds_0 = self.selector_name_ds64_0
        elif self.mode == "long_mode":
            self.selector_name_cs_0 = self.selector_name_cs64_0
            self.selector_name_ds_0 = self.selector_name_ds64_0
        elif self.mode == "protect_mode":
            self.selector_name_cs_0 = self.selector_name_cs32_0
            self.selector_name_ds_0 = self.selector_name_ds32_0
        else:
            self.Error_exit("Invalid mode!")
            
        if c_gen:
            self.selector_value_c_gen_0 = 0x5
            if self.mode == "long_mode":
                self.c_parser.selector_name_c_gen_0 = "c_gen_64"
                self.selector_name_c_gen_0 = self.c_parser.selector_name_c_gen_0
                self.Vars_write(self.c_parser.selector_name_c_gen_0,self.selector_value_c_gen_0)
                self.Text_write("@gdt[$%s].type = 0x3"%(self.c_parser.selector_name_c_gen_0))
                self.Text_write("@gdt[$%s].l = 0x1"%(self.c_parser.selector_name_c_gen_0))
                if self.c_parser.c_code_mem_info.has_key(".tbss"):
                    self.Text_write("@gdt[$%s].base = 0x%08x"%(self.c_parser.selector_name_c_gen_0,self.c_parser.c_code_mem_info[".tbss"]["start"]))
                else:
                    #self.Text_write("@gdt[$%s].base = 0x%08x"%(self.c_parser.selector_name_c_gen_0,self.c_parser.c_code_mem_info[".tbss"]["start"]))
                    warning("This elf file don't have tbss seg")
            else:
                self.c_parser.selector_name_c_gen_0 = "c_gen_32"
                self.selector_name_c_gen_0 = self.c_parser.selector_name_c_gen_0
                self.Vars_write(self.c_parser.selector_name_c_gen_0,self.selector_value_c_gen_0)
                self.Text_write("@gdt[$%s].type = 0x3"%(self.c_parser.selector_name_c_gen_0))
                self.Text_write("@gdt[$%s].db = 0x1"%(self.c_parser.selector_name_c_gen_0))
                if self.c_parser.c_code_mem_info.has_key(".tbss"):
                    self.Text_write("@gdt[$%s].base = 0x%08x"%(self.c_parser.selector_name_c_gen_0,self.c_parser.c_code_mem_info[".tbss"]["start"]))
                else:
                    warning("This elf file don't have tbss seg")


            
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
        if self.disable_avx == False:
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
        self.ptg.Write_page()
        self.long_mode_code_start = self.mpg.Apply_mem(0x1000,16,start=0x1000,end=0xA0000,name="long_mode_code_start")
        ########enter compatibility_mode######################
        self.Comment("##enable IA32e mode")
        self.Msr_Rmw(0xc0000080,"s8")
        self.Instr_write("mov eax,cr0")
        self.Instr_write("and eax,0x9fffffff")
        self.Instr_write("or eax,0x80000020")
        self.Instr_write("mov cr0,eax")
        if self.disable_pcid == False:
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
            self.Instr_write("call [rax+&@%s]"%(self.thread_info_pointer["name"]))
        else:
            self.Instr_write("mov esp,[eax+&@%s+8]"%(self.thread_info_pointer["name"]))
            self.Instr_write("call [eax+&@%s]"%(self.thread_info_pointer["name"]))


        
        for i in range(0,self.threads):
            if i == 0x0:
                self.instr_manager.Set_instr(69,0)
            else:
                self.instr_manager.Set_instr(65,i)
        
    def Protect_mode_code(self):
        self.Comment("###########################Protect mode code######################")
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
        self.Comment("##enable pse,fxsave(sse),simd,global page, disable pae")
        self.Instr_write("mov eax,cr4")
        self.Instr_write("or eax,0x690")
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
        if self.disable_avx == False:
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
        self.ptg.Write_page()
        self.protect_mode_code_continue = self.mpg.Apply_mem(0x1000,16,start=0x0,end=0xA0000,name="protect_mode_code_continue")
        ########set protect_mode######################
        self.Instr_write("mov eax,cr0")
        self.Instr_write("and eax,0x9fffffff")
        self.Instr_write("or eax,0x80000020")
        self.Instr_write("mov cr0,eax")
        ########enter protect_mode###############################
        self.Instr_write("jmpf &SELECTOR($%s):0x%x"%(self.selector_name_cs_0,self.protect_mode_code_continue["start"]))         
        self.Text_write("org 0x%x"%(self.protect_mode_code_continue["start"]))
        self.Text_write("use 32")
        self.Instr_write("mov ebx,&SELECTOR($%s)"%(self.selector_name_ds_0))
        self.Instr_write("mov es,bx")
        self.Instr_write("mov fs,bx")
        self.Instr_write("mov gs,bx")
        self.Instr_write("mov eax,0xfee00020")
        self.Instr_write("mov eax,dword [eax]") # get apic id        
        self.Instr_write("shr eax, 24 - (8 / 2)")
        if self.intel:
            for i in range(0,self.threads):
                if i == 0x0:
                    self.instr_manager.Set_instr(61,0)
                    self.simcmd.Add_sim_cmd("at $y%d >= %d set register EAX to 0x000000%02x"%(i,self.instr_manager.Get_instr(i),i*0x20),i)
                else:
                    self.instr_manager.Set_instr(57,i)
                    self.simcmd.Add_sim_cmd("at $y%d >= %d set register EAX to 0x000000%02x"%(i,self.instr_manager.Get_instr(i),i*0x20),i)
                    
        self.Comment("##set stack")
        self.Instr_write("mov esp,[eax+&@%s+8]"%(self.thread_info_pointer["name"]))
        self.Instr_write("call [eax+&@%s]"%(self.thread_info_pointer["name"]))
           
        for i in range(0,self.threads):
            if i == 0x0:
                self.instr_manager.Set_instr(63,0)
            else:
                self.instr_manager.Set_instr(59,i)
