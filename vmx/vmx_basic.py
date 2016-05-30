#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' vmx_basic module '
__author__ = 'Ken Zhao'
########################################################
# vmx_basic module is used to supprot vmx
########################################################
import sys, os, re, random
sys.path.append("/%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from optparse import OptionParser
from vmx_mode import Vmx_mode
#####################################################Sub Classes###########################
class Vmx_basic(Test_generator):        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Vmx *args, **kwargs", version="%Vmx 0.1") #2016-04-25 version 0.1
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 1)
        args_parser.add_option("-t","--threads", dest="thread_nums", help="The vector thread nums."\
                          , type = "int", default = 1)
        args_parser.add_option("--seed", dest="seed", help="Set the seed. [default: %default]\nFor the default value, tpg will generate random seed instead."\
                          , type = "int", default = 0x0)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--intel", dest="intel", help="Support intel platform, APIC ID is 0,2,4,6", action="store_true", default = False)
        args_parser.add_option("--no_very_short", dest="very_short", help="Change -very-short to short", action="store_true", default = False)  
        (self.args_option, self.args_additions) = args_parser.parse_args(args)       
        if self.args_option.seed:
            self.seed = self.args_option.seed
        else:
            self.seed = random.randint(1,0xFFFFFFFF)                  
        self.threads = self.args_option.thread_nums
        self.intel = self.args_option.intel
        self.c_gen = 0
        self.mode = "long_mode"
        self.page_mode = "2MB"
        if self.args_option.very_short == True:
            self.very_short_cmd = "-very-short"
            self.very_short_num = "10000000"
        else:
            self.very_short_cmd = "-short"
            self.very_short_num = "100000"
        self.vmx_client_mode = "long_mode"
            
    def Gen_mode_code(self):
        self.vmx_mode_code = Vmx_mode(self.hlt_code,self.mpg, self.instr_manager, self.ptg, self.threads, self.simcmd, self.intel, self.interrupt,self.c_parser)
        self.vmx_mode_code.asm_file = self.asm_file
        self.vmx_mode_code.inc_path = self.inc_path
        [self.stack_segs,self.user_code_segs] = self.vmx_mode_code.Mode_code(self.mode,self.c_gen,self.vmx_client_mode)

    def Gen_hlt_code(self,thread_num):
        if thread_num == 0:
            self.Text_write("jmp $%s"%(self.hlt_code["name"]))
            self.Text_write("org 0x%x"%(self.hlt_code["start"]))
            self.Tag_write(self.hlt_code["name"])
            self.Vmx_exit()
            self.Text_write("hlt")
        elif 0 < thread_num < 4:
            self.Text_write("jmp $%s"%(self.hlt_code["name"]))
        else:
            self.Error_exit("Invalid thread num!")

    def Start_user_code(self,thread):
        self.Comment("##Usr code")
        self.Instr_write("call [eax+&@%s]"%(self.vmx_mode_code.thread_info_pointer["name"]))
        self.Text_write("org 0x%x"%(self.user_code_segs[thread]["start"]))
        self.Tag_write(self.user_code_segs[thread]["name"])
        self.Text_write("use 64")
        self.Vmx_initial()
        self.Vmx_vmcs_initial()
        self.Vmx_entry()
        self.Set_guest_entry()

        
    def Vmx_initial(self):
        self.Vmcs_extra_setting()
        self.Comment("#### enable cr4 bit 13 vmex")
        self.Instr_write("mov eax,cr4")
        self.Instr_write("bts eax,0xd")
        self.Instr_write("mov cr4,eax")
        self.Comment("#### initialize feature control msr ####")
        self.Instr_write("mov ecx, 0x3a")
        self.Instr_write("rdmsr")
        self.Instr_write("bt eax, 0")
        self.Instr_write("jc $skip_wrmsr")
        self.Msr_Write(0x3a,0,edx=0,eax=5)
        self.Tag_write("skip_wrmsr")
        self.Comment("#### initialize_revision_id ####")
        self.Set_vmcs_id(self.vmx_mode_code.vmxon["start"],self.vmx_mode_code.vmxon_pointer["start"])
        self.Instr_write("vmxon [0x%x]"%(self.vmx_mode_code.vmxon_pointer["start"]),0)
        
    def Vmx_vmcs_initial(self):
        self.Set_vmcs_id(self.vmx_mode_code.vmcs["start"],self.vmx_mode_code.vmcs_pointer["start"])
        self.Instr_write("vmclear [0x%x]"%(self.vmx_mode_code.vmcs_pointer["start"]))
        self.Instr_write("vmptrld [0x%x]"%(self.vmx_mode_code.vmcs_pointer["start"]))
        self.Comment("#now initialize the guest vmcs")
        self.Instr_write("mov rbx,0x%x"%(self.vmx_mode_code.vmcs_data["start"]))
        self.Instr_write("call $std_vmcs_initialize_guest_vmcs")  # this label is from "std_vmx_code.inc"
        self.Tag_write("vmcs_initialize_end")
        self.Text_write("org 0x%x"%(self.vmx_mode_code.vmcs_initial_code["start"]));  
        self.Text_write("include \"%s/std_vmx_code.inc\""%(self.inc_path));  # this is the code to setup vm guest
        self.Text_write("org $vmcs_initialize_end")
        self.vmx_mode_code.Write_vmx_page()
        
    def Vmx_entry(self):
        self.Instr_write("vmlaunch")
        
    def Vmx_exit(self):
        self.Instr_write("vmclear [0x%x]"%(self.vmx_mode_code.vmcs_pointer["start"]),0)
        self.Instr_write("vmxoff",0)
        
    def Set_vmcs_id(self,vmcs,vmcs_pointer):
        self.Msr_Read(0x480,0)
        self.Instr_write("mov ebx, 0x%x"%(vmcs))
        self.Instr_write("mov [0x%x], ebx"%(vmcs_pointer))
        self.Instr_write("mov [0x%x], 0x0"%(vmcs_pointer+4))
        self.Instr_write("mov [0x%x], eax"%(vmcs))
        
    def Set_guest_entry(self):
        self.Text_write("org 0x%x"%(self.vmx_mode_code.vmx_guest_entry_0["start"]))
        self.Text_write("use 64")
        for i in range(0,100):
            self.Instr_write("mov r8,qword ptr [0x40000000]")
        #self.Instr_write("mov rbx,0x%x"%(self.vmx_mode_code.vmcs_data["start"]))
        #self.Instr_write("mov [rbx + disp32 &OFFSET(@std_vmcs_data.host_cr3)],0x%x"%(self.vmx_mode_code.ptg.tlb_base["start"]));
        #self.Instr_write("mov rax, @std_vmcs_encoding.host_cr3")
        #self.Instr_write("vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_cr3)]");
        self.Instr_write("vmcall")
        #self.Instr_write("hlt")
    
    def Vmcs_extra_setting(self):
        #self.Text_write("@vmcs.guest_cr0= 0xC0000031")
        #self.Text_write("&TO_MEMORY_ALL()")
        pass