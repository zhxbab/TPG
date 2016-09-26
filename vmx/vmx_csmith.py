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
from c_parser import C_parser
#####################################################Sub Classes###########################
class Vmx_csmith(Test_generator):        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Vmx *args, **kwargs", version="%Vmx 0.1") #2016-04-25 version 0.1
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 1)
        args_parser.add_option("-t","--threads", dest="thread_nums", help="The vector thread nums."\
                          , type = "int", default = 1)
        args_parser.add_option("-m","--vmc_mode", dest="client_mode", help="The vmx client mode.\n0x0: long mode\n0x1: compatibility mode\n"\
                          , type = "int", default = 0)
        args_parser.add_option("--seed", dest="seed", help="Set the seed. [default: %default]\nFor the default value, tpg will generate random seed instead."\
                          , type = "int", default = 0x0)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--intel", dest="intel", help="Support intel platform, APIC ID is 0,2,4,6", action="store_true", default = False)
        args_parser.add_option("--very_short", dest="very_short", help="Change -short to -very-short", action="store_true", default = False)
        args_parser.add_option("-f","--file", dest="elf_file", help="The elf file, when input a elf file, the TPG function will cancel", type="str", default = None)
        args_parser.add_option("--gcc", dest="gcc", help="Force use gcc", action="store_true", default = False)
        args_parser.add_option("--clang", dest="clang", help="Force use clang", action="store_true", default = False)
        args_parser.add_option("--set_Op", dest="Op", help="Set the Op level", type="str", default = None)
        args_parser.add_option("--ma", dest="ma", help="Set cnsim instruction num", type="int", default = None)
        args_parser.add_option("--disable_avx", dest="disable_avx", help="disable AVX for support old intel platform", action="store_true", default = False)
        args_parser.add_option("--disable_pcid", dest="disable_pcid", help="disable PCID for support old intel platform", action="store_true", default = False)
        args_parser.add_option("--instr_only", dest="instr_only", help="Cnsim instr only", action="store_true", default = False)
        args_parser.add_option("--c_plus", dest="c_plus", help="Gen c++ code", action="store_true", default = False)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        if not self.args_option.elf_file == None:
            self.elf_file = os.path.join(self.current_dir_path,self.args_option.elf_file)
        else:
            self.elf_file = None     
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
        self.c_gen = 1
        self.mode = "long_mode"
        self.page_mode = "2MB"
        if self.args_option.very_short == True:
            self.very_short_cmd = "-very-short"
            self.very_short_num = "%d"%(100000000*self.threads)
        else:
            if self.args_option.instr_only:
                self.very_short_cmd = "-instr-only"
                self.very_short_num = "%d"%(50000000*self.threads)                
            else:
                self.very_short_cmd = "-short"
                self.very_short_num = "%d"%(500000*self.threads)
                
        if self.args_option.client_mode == 0x0:
            self.vmx_client_mode = "long_mode"
        elif self.args_option.client_mode == 0x1:
            self.vmx_client_mode = "compatibility_mode"
        else:
            self.Error_exit("Invalid vmx client mode!")
        if self.args_option.gcc == True:
            self.force_gcc = 1
        else:
            self.force_gcc = 0
        if self.args_option.clang == True:
            self.force_clang = 1
        else:
            self.force_clang = 0
        if self.args_option.Op == "O0" or self.args_option.Op == "O1" or self.args_option.Op == "O2" \
        or self.args_option.Op == "Os" or self.args_option.Op == "O3" or self.args_option.Op == None:
            self.Op = self.args_option.Op
        else:
            self.Error_exit("Invalid optimize level!")
            
        if self.args_option.ma == None:
            pass
        else:
            self.very_short_num = self.args_option.ma
        self.disable_avx = self.args_option.disable_avx
        self.disable_pcid = self.args_option.disable_pcid
        self.multi_page = 0
        self.c_plus = self.args_option.c_plus
                
    def Force_compiler_and_optimize(self):
        if self.force_gcc == 1:
            self.c_parser.c_compiler = self.c_parser.gcc
            self.c_parser.cplus_compiler = self.c_parser.gcc_cplus
        elif self.force_clang == 1:
            self.c_parser.c_compiler = self.c_parser.clang
            self.c_parser.cplus_compiler = self.c_parser.clang_cplus
        elif self.force_clang == 0 and self.force_gcc == 0:
            self.c_parser.c_compiler = [self.c_parser.gcc,self.c_parser.clang][random.randint(0,1)]
            self.c_parser.cplus_compiler = [self.c_parser.gcc_cplus,self.c_parser.clang_cplus][random.randint(0,1)]
        else:
            self.Error("Compiler is not used")
            
    def Create_asm(self,index=0x0):
        self.asm_name = "%s_%s_%sT_%s_%d.asm"%(self.realbin_name,index,self.threads,self.vmx_client_mode,self.seed)
        self.asm_path = os.path.join(self.avp_dir_path,self.asm_name)
        self.asm_file = open(self.asm_path,"w")
        self.asm_list.append(self.asm_path)
        self.ptg.asm_file = self.asm_file
        self.mpg.asm_file = self.asm_file
        self.simcmd.asm_file = self.asm_file
        self.interrupt.asm_file = self.asm_file
        self.Text_write("include \"%s/std.inc\""%(self.inc_path))
        self.hlt_code = self.mpg.Apply_mem(0x200,16,start=0x0,end=0xA0000,name="hlt_code")
        
    def Create_dir(self):
        self.avp_dir_seed = random.randint(1,0xFFFF)
        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.threads,self.vmx_client_mode,self.avp_dir_seed)
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
            
    def Gen_asm_code(self,thread, num):
        self.c_parser = C_parser(self.bin_path,self.avp_dir_path,self.vmx_client_mode,self.instr_manager,self.mpg)
        self.c_parser.asm_file = self.asm_file
        self.c_parser.c_plus = self.c_plus  
        if self.elf_file != None:
            ret_gen_asm_code = self.c_parser.Get_fix_c_asm(self.elf_file)
        else:
            self.Force_compiler_and_optimize()
            ret_gen_asm_code = self.c_parser.Gen_c_asm(thread,num)
        if ret_gen_asm_code:
            del_asm = self.asm_list.pop()
            #info("rm -f %s"%(del_asm))
            os.system("rm -f %s"%(del_asm))
            warning("%s's c code can't be executed successfully, so remove it from asm list"%(del_asm))
        return ret_gen_asm_code 
            
            
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

    def Set_exit_code(self,thread):
        self.Vmx_exit(thread)
        self.Text_write("jmp $%s"%(self.hlt_code["name"]))
        
    def Start_user_code(self,thread):
        self.Comment("##Usr code")
        #self.Instr_write("call [eax+&@%s]"%(self.vmx_mode_code.thread_info_pointer["name"]))
        self.Text_write("org 0x%x"%(self.user_code_segs[thread]["start"]))
        self.Tag_write(self.user_code_segs[thread]["name"])
        self.Text_write("use 64")
        self.Instr_write("mov eax,&SELECTOR($%s)"%(self.c_parser.selector_name_c_gen_0),thread)
        self.Instr_write("mov fs,eax",thread)
        self.Vmx_initial(thread)
        self.Vmx_vmcs_initial(thread)
        self.Vmx_entry(thread)
        self.Set_guest_entry(thread)
        self.vmx_mode_code.Exit_code_addr(thread)
        self.Set_exit_code(thread)

        
    def Vmx_initial(self,thread):
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
        self.Instr_write("vmxon [0x%x]"%(self.vmx_mode_code.vmxon_pointer[thread]["start"]),0)
        
        
        
        
    def Vmx_vmcs_initial(self,thread):
        
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
        self.Instr_write("vmlaunch")

    def Vmx_exit(self,thread):
        self.Instr_write("vmclear [0x%x]"%(self.vmx_mode_code.vmcs_pointer[thread]["start"]),0)
        self.Instr_write("vmxoff",0)
        
    def Set_vmcs_id(self,vmcs,vmcs_pointer):
        self.Msr_Read(0x480,0)
        self.Instr_write("mov ebx, 0x%x"%(vmcs))
        self.Instr_write("mov [0x%x], ebx"%(vmcs_pointer))
        self.Instr_write("mov [0x%x], 0x0"%(vmcs_pointer+4))
        self.Instr_write("mov [0x%x], eax"%(vmcs))
        
    def Set_guest_entry(self,thread):
        self.Text_write("org 0x%x"%(self.vmx_mode_code.vmx_guest_entry_0[thread]["start"]))
        self.Text_write("use 64")
        self.Instr_write("call $_init_%d"%(thread),0)
        self.Instr_write("call $main_%d"%(thread),0)  
        #self.Instr_write("mov qword ptr [0x40000000], r8")
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
    
    def Fix_threads(self,threads):
        self.threads = threads
        if self.threads > 1 and self.c_gen==1:
            self.multi_ept = 1
            self.multi_page = 0
            
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Vmx_csmith(sys.argv[1:])
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        if tests.Gen_asm_code(0,i):
            continue
        tests.Gen_mode_code()
        for j in range(0,tests.threads):
            tests.Start_user_code(j)
            tests.Vmx_load_asm_code(j,i)
        #tests.Instr_write("vmxon [$vmxon_ptr]",0)
        tests.c_parser.c_code_asm.close()
        tests.Gen_hlt_code()
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()