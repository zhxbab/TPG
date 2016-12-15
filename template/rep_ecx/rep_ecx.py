#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' movdqa module '
__author__ = 'Ken Zhao'
########################################################
# MOVDQA
########################################################
import sys, os, re, random
sys.path.append("/%s/../../src"%(sys.path[0]))
sys.path.append("/%s/../"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from template_tpg import Template_tpg
##############################################GLOBAL VARS###################################
instruction_set = ["rep_stosq"]
#instruction_test_mode = ["R","W","C"]
#instruction_test_mode = ["reg","imm"]
instruction_test_mode = ["imm"]
#mov_count = [10,20,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900,1000,1500,2000,2500,3000,3500,4000,4500,5000]
#mov_count = [10,20,30,40,50,60,70,80,90]
rep_ecx_count = range(1,257)
#rep_ecx_count = [1]
#OFFSET = [0,3]
OFFSET = [0]
##############################################CLASSES#######################################
class REP_ECX(Template_tpg): 
    def Parse_input(self,args):
        Template_tpg.Parse_input(self,args)
        self.mode = "long_mode"
        self.page_mode = "2MB"

        
    def Create_wrap_dir(self,instruction,test_mode,count,offset):
        self.wrap_dir_name = "%sT_%s_%s_%s_count_%d_offset_%d"%(self.threads,self.mode,instruction,test_mode,count,offset)
        cmd = "mkdir %s/%s"%(self.realbin_path,self.wrap_dir_name)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        
    def Create_dir(self,instruction,test_mode,count,offset):
        self.Create_wrap_dir(instruction,test_mode,count,offset)
        self.avp_dir_seed = random.randint(1,0xFFFF)
        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.threads,self.mode,self.avp_dir_seed)
        cmd = "mkdir %s/%s/%s"%(self.realbin_path,self.wrap_dir_name,self.avp_dir_name)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        self.avp_dir_path = os.path.join("%s/%s"%(self.realbin_path,self.wrap_dir_name),self.avp_dir_name)
        self.cnsim_fail_dir = os.path.join(self.avp_dir_path,"cnsim_fail")
        self.fail_dir =  os.path.join(self.avp_dir_path,"fail")
        cmd = "mkdir %s"%(self.cnsim_fail_dir)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        cmd = "mkdir %s"%(self.fail_dir)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        self.Create_global_info()
        
##############################################MAIN##########################################
if __name__ == "__main__":
    for instruction in instruction_set:
        instruction_name = "rep stosq"
        for offset in OFFSET:
            for test_mode in instruction_test_mode:
                for count in rep_ecx_count:
                    tests = REP_ECX(sys.argv[1:])
                    tests.Fix_threads(1)
                    tests.Create_dir(instruction,test_mode,count,offset)
                    tests.Gen_del_file()
                    for i in range(0,tests.args_option.nums):
                        tests.Reset_asm()
                        tests.Create_asm(i)
                        tests.Initial_interrupt()
                        pmc0_addr = tests.mpg.Apply_fix_mem("pmc0_addr",0x20000000,0x20)
                        rep_code_addr = tests.mpg.Apply_fix_mem("rep_code_addr",0x40000000,0x40000000)
                        mem_address_addr = tests.mpg.Apply_fix_mem("mem_address_addr",0x30000000,0x10000000)
                        #mem_address_addr1 = tests.mpg.Apply_fix_mem("mem_address_addr1",0x10000000,0x10000000)
                        tests.Gen_mode_code()
                        tests.Start_user_code(0)
                        tests.Init_PMC(0)
                        tests.Enable_PMC0(0)
                        tests.Instr_write("call %s"%(rep_code_addr["start"]),0)
                        tests.Text_write("org 0x%x"%(rep_code_addr["start"]))
                        if test_mode == "reg":
                            tests.Instr_write("mov eax,%d"%(count),0)                              
                            tests.Instr_write("mov ecx,eax",0)
                        elif test_mode == "imm":
                            tests.Instr_write("mov ecx,%d"%(count),0)                             
                        else:
                            print("No expected test mode!")
                            sys.exit(0)
                        tests.Instr_write("mov rdi,0x%x"%(mem_address_addr["start"]+offset),0)   
                        tests.Instr_write("%s"%(instruction_name),0)  
                        tests.Read_PMC0("0x%x"%(pmc0_addr["start"]),0)
                        for j in range(0,10000):
                            if test_mode == "reg":
                                tests.Instr_write("mov eax,%d"%(count),0)                              
                                tests.Instr_write("mov ecx,eax",0)
                            elif test_mode == "imm":
                                tests.Instr_write("mov ecx,%d"%(count),0)                             
                            else:
                                print("No expected test mode!")
                                sys.exit(0)
                            tests.Instr_write("mov rdi,0x%x"%(mem_address_addr["start"]+offset),0)   
                            tests.Instr_write("%s"%(instruction_name),0)  
                    tests.Read_PMC0("0x%x"%(pmc0_addr["start"]+0x8),0)
                    tests.Report_PMC(pmc0_addr,0)
                    tests.Gen_hlt_code(0)
                    tests.Gen_sim_cmd(0)
                    tests.Gen_vector()
                    tests.Gen_pclmsi_file_list()
                    del tests
        

