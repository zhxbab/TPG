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
from simcmd import Simcmd
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
        args_parser.add_option("-m", dest="client_mode", help="The client_mode. 0x0: long mode, 0x1: protect mode, 0x2: compatibility mode", type = "int", default = 0)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)       
        if self.args_option.seed:
            self.seed = self.args_option.seed
        else:
            self.seed = random.randint(1,0xFFFFFFFF)                  
        self.threads = self.args_option.thread_nums
        if self.threads > 1:
            self.multi_ept = 1
        else:
            self.multi_ept = 0
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
        if self.args_option.client_mode == 0:
            self.vmx_client_mode = "long_mode"
        elif self.args_option.client_mode == 1:
            self.vmx_client_mode = "protect_mode"
        elif self.args_option.client_mode == 2:
            self.vmx_client_mode = "compatibility_mode"
        else:
            self.Error_exit("Invalid vm client mode!")
        self.disable_avx = False
        self.disable_pcid = False
        self.multi_page = 0 
        self.simcmd = Simcmd(self.threads)     
        
        
    def Create_dir(self):
        self.avp_dir_seed = random.randint(1,0xFFFF)
        self.avp_dir_name = "%s_%sT_%s_vmx_%s_%d"%(self.realbin_name,self.threads,self.mode,self.vmx_client_mode,self.avp_dir_seed)
        cmd = "mkdir %s/%s"%(self.realbin_path,self.avp_dir_name)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        self.avp_dir_path = os.path.join(self.realbin_path,self.avp_dir_name)
        self.cnsim_fail_dir = os.path.join(self.avp_dir_path,"cnsim_fail")
        self.fail_dir =  os.path.join(self.avp_dir_path,"fail")
        cmd = "mkdir %s"%(self.cnsim_fail_dir)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        cmd = "mkdir %s"%(self.fail_dir)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        self.Create_global_info()        
        
        
    def Gen_mode_code(self):
        self.vmx_mode_code = Vmx_mode(self.hlt_code,self.mpg, self.instr_manager, self.ptg, self.threads, self.simcmd, self.intel, self.interrupt,self.c_parser)
        self.vmx_mode_code.asm_file = self.asm_file
        self.vmx_mode_code.inc_path = self.inc_path
        self.vmx_mode_code.multi_ept = self.multi_ept
        self.ptg.c_gen = self.c_gen
        self.ptg.intel = self.intel
        self.ptg.vmx_client_mode = self.vmx_client_mode
        if self.c_gen:
            self.c_parser.multi_page = self.multi_page
            self.c_parser.multi_ept = self.multi_ept
        self.ptg.multi_page = self.multi_page
        self.ptg.multi_ept = self.multi_ept
        [self.stack_segs,self.user_code_segs] = self.vmx_mode_code.Mode_code(self.mode,self.c_gen,self.vmx_client_mode,self.disable_avx,self.disable_pcid)

    def Gen_hlt_code(self):
        self.Text_write("org 0x%x"%(self.hlt_code["start"]))
        self.Tag_write(self.hlt_code["name"])
        self.Text_write("hlt")

    def Start_user_code(self,thread):
        self.Comment("##Usr code")
        self.Instr_write("call [eax+&@%s]"%(self.vmx_mode_code.thread_info_pointer["name"]))
        self.Text_write("org 0x%x"%(self.user_code_segs[thread]["start"]))
        self.Tag_write(self.user_code_segs[thread]["name"])
        self.Text_write("use 64")
        self.Vmx_initial(thread)
        self.Vmx_vmcs_initial(thread)
        self.Vmx_entry(thread)
        self.Set_guest_entry(thread)
        self.vmx_mode_code.Exit_code_addr(thread)
        self.Set_exit_code(thread)
        
    def Set_exit_code(self,thread):
        self.Vmx_exit(thread)
        self.Text_write("jmp $%s"%(self.hlt_code["name"]))
        
    def Vmx_initial(self,thread): #Ivybridge cannot run the vmx code, but Skylake can
        self.Vmcs_extra_setting()
        self.Comment("#### enable cr4 bit 13 vmex")
        self.Instr_write("mov eax,cr4")
        self.Instr_write("bts eax,0xd")
        self.Instr_write("mov cr4,eax")       
        self.Comment("#### initialize feature control msr ####")
        self.Instr_write("mov ecx, 0x3a")
        self.Instr_write("rdmsr")
        self.Instr_write("bt eax, 0")
        self.Instr_write("jc $skip_wrmsr_%d"%(thread))
        self.Msr_Write(0x3a,0,edx=0,eax=5)
        self.Tag_write("skip_wrmsr_%d"%(thread))
        self.Comment("#### initialize_revision_id ####")
        self.Set_vmcs_id(self.vmx_mode_code.vmxon[thread]["start"],self.vmx_mode_code.vmxon_pointer[thread]["start"])
        self.Instr_write("vmxon [0x%x]"%(self.vmx_mode_code.vmxon_pointer[thread]["start"]),thread)
        if self.intel:
            self.simcmd.Add_sim_cmd("at RDMSR 0x480 set msr 0x480 to 0x12:0x00",0,0) #Intel is about 0x12, 0x10
            self.simcmd.Add_sim_cmd("at halt set memory 0x%x mask range 0x14"%((self.vmx_mode_code.vmxon[thread]["start"])),thread,0)
            self.simcmd.Add_sim_cmd("at halt set memory 0x%x mask range 0x1000"%(self.vmx_mode_code.vmcs[thread]["start"]),thread,1)
        else:
            self.simcmd.Add_sim_cmd("at halt set memory 0x%x mask range 0x20"%((self.vmx_mode_code.vmcs[thread]["start"]+0x3a0)),thread,0)
#        ### test #####
#        self.Instr_write("vmxoff",thread)
#        self.Instr_write("hlt",thread)      
         
    def Vmx_vmcs_initial(self,thread):
        #info("vmcs_pointer_%d is 0x%x"%(thread,self.vmx_mode_code.vmcs_pointer[thread]["start"]))
        self.Set_vmcs_id(self.vmx_mode_code.vmcs[thread]["start"],self.vmx_mode_code.vmcs_pointer[thread]["start"])
        self.Instr_write("vmclear [0x%x]"%(self.vmx_mode_code.vmcs_pointer[thread]["start"]))
        self.Instr_write("vmptrld [0x%x]"%(self.vmx_mode_code.vmcs_pointer[thread]["start"]))
        self.Comment("#now initialize the guest vmcs")
        self.Instr_write("mov rbx,0x%x"%(self.vmx_mode_code.vmcs_data[thread]["start"]))
        self.Instr_write("call $std_vmcs_initialize_guest_vmcs_%d"%(thread))  # this label is from "std_vmx_code.inc"
        self.Tag_write("vmcs_initialize_end_%d"%(thread))
        self.Text_write("org 0x%x"%(self.vmx_mode_code.vmcs_initial_code[thread]["start"]));  
        self.Text_write("include \"%s/std_vmx_code_%d.inc\""%(self.inc_path,thread));  # this is the code to setup vm guest
        self.Text_write("org $vmcs_initialize_end_%d"%(thread))
        if thread == 0:
            self.vmx_mode_code.Write_vmx_page()
        
    def Vmx_entry(self,thread):
        self.Set_std_vmcs_initialize_16bit_control_state(thread)
        self.Instr_write("vmlaunch")
        
    def Vmx_exit(self,thread):
        self.eptp_pointer = self.mpg.Apply_mem(0x10,16,start=0x1000000,end=0x8000000,name="eptp_pointer")
        self.vpid_pointer = self.mpg.Apply_mem(0x10,16,start=0x1000000,end=0x8000000,name="vpid_pointer") 
        vmcs = self.mpg.Apply_mem(0x2000,0x1000,start=0x1000000,end=0x8000000,name="vmcs_exit")
        current_vmcs_pointer = self.mpg.Apply_mem(0x8,16,start=0x1000000,end=0x8000000,name="vmcs_exit_pointer")
        self.Instr_write("vmptrst [0x%x]"%(current_vmcs_pointer["start"]))#store current vmcs addr
        self.Vmread_all(vmcs["start"],thread)
        self.Change_vm_rip(vmcs["start"],"$vmx_exit_%d"%(thread),"$host_vmx_exit_%d"%(thread),thread) 
        if self.multi_ept:          
            self.Reflush_cache(self.eptp_pointer["start"],self.vmx_mode_code.ptg.ept_tlb_base[thread]["start"],thread)
        else:
            self.Reflush_cache(self.eptp_pointer["start"],self.vmx_mode_code.ptg.ept_tlb_base["start"],thread)            
        self.Reflush_vpid(0,self.vpid_pointer["start"],self.vmx_mode_code.vmcs[thread]["start"],thread+1,thread)
        self.Reflush_vpid(1,self.vpid_pointer["start"],self.vmx_mode_code.vmcs[thread]["start"],thread+1,thread)
        self.Reflush_vpid(2,self.vpid_pointer["start"],self.vmx_mode_code.vmcs[thread]["start"],thread+1,thread)
        self.Reflush_vpid(3,self.vpid_pointer["start"],self.vmx_mode_code.vmcs[thread]["start"],thread+1,thread)
        self.Instr_write("vmresume",thread)
        self.Tag_write("host_vmx_exit_%d"%(thread))
        self.Instr_write("vmclear [0x%x]"%(self.vmx_mode_code.vmcs_pointer[thread]["start"]),thread)
        self.Instr_write("vmxoff",thread)
        
    def Set_vmcs_id(self,vmcs,vmcs_pointer):
        self.Msr_Read(0x480,0)
        self.Instr_write("mov ebx, 0x%x"%(vmcs))
        self.Instr_write("mov [0x%x], ebx"%(vmcs_pointer))
        self.Instr_write("mov [0x%x], 0x0"%(vmcs_pointer+4))
        self.Instr_write("mov [0x%x], eax"%(vmcs))
        
    def Set_guest_entry(self,thread):
        self.Text_write("org 0x%x"%(self.vmx_mode_code.vmx_guest_entry_0[thread]["start"]))
        if self.vmx_client_mode == "long_mode":
            self.Text_write("use 64")
            for i in range(0,1000):
                self.Instr_write("mov r8,qword ptr [0x40000000]")
        #self.Instr_write("mov rbx,0x%x"%(self.vmx_mode_code.vmcs_data["start"]))
        #self.Instr_write("mov [rbx + disp32 &OFFSET(@std_vmcs_data.host_cr3)],0x%x"%(self.vmx_mode_code.ptg.tlb_base["start"]));
        #self.Instr_write("mov rax, @std_vmcs_encoding.host_cr3")
        #self.Instr_write("vmwrite rax, [rbx + disp32 &OFFSET(@std_vmcs_data.host_cr3)]");
        else:
            self.Text_write("use 32")
            for i in range(0,1000):
                self.Instr_write("mov edx,dword ptr [0x40000000]")
        self.Instr_write("vmcall",thread)
        self.Tag_write("vmx_exit_%d"%(thread))
        self.Instr_write("vmcall",thread)         
        #self.Instr_write("hlt")
    
    def Vmcs_extra_setting(self):
        #self.Text_write("@vmcs.guest_cr0= 0xC0000031")
        #self.Text_write("&TO_MEMORY_ALL()")
        pass
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Vmx_basic(sys.argv[1:])
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        tests.Gen_mode_code()
        for j in range(0,tests.threads):
            tests.Start_user_code(j)
            tests.simcmd.Simcmd_write(j)
        tests.Gen_hlt_code()
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()