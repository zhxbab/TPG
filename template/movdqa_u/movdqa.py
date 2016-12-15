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
#instruction_set = ["movdqa","movdqu"]
instruction_set = ["movdqu"]
instruction_test_mode = ["R","W","C"]
#instruction_test_mode = [""]
mov_count = [10,20,30,40,50,60,70,80,90,100,200,300,400,500,600,700,800,900,1000,1500,2000,2500,3000,3500,4000,4500,5000]
#mov_count = [10,20,30,40,50,60,70,80,90]
#mov_count = [4000,4500,5000]
##############################################CLASSES#######################################
class MOVDQA(Template_tpg): 
    def Parse_input(self,args):
        Template_tpg.Parse_input(self,args)
        self.mode = "long_mode"
        self.page_mode = "2MB"

        
    def Create_wrap_dir(self,instruction,test_mode,count):
        self.wrap_dir_name = "%sT_%s_%s_%s_count_%d"%(self.threads,self.mode,instruction,test_mode,count)
        cmd = "mkdir %s/%s"%(self.realbin_path,self.wrap_dir_name)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        
    def Create_dir(self,instruction,test_mode,count):
        self.Create_wrap_dir(instruction,test_mode,count)
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
        if instruction == "movdqa":
            offset = 0
        elif instruction == "movdqu":
            offset = 0x3
        else:
            print("No expected instruction is %s!"%(instruction))
            sys.exit(0)            
        for test_mode in instruction_test_mode:
            for count in mov_count:
                tests = MOVDQA(sys.argv[1:])
                tests.Fix_threads(1)
                tests.Create_dir(instruction,test_mode,count)
                tests.Gen_del_file()
                for i in range(0,tests.args_option.nums):
                    tests.Reset_asm()
                    tests.Create_asm(i)
                    tests.Initial_interrupt()
                    pmc0_addr = tests.mpg.Apply_fix_mem("pmc0_addr",0x20000000,0x20)
                    mov_code_addr = tests.mpg.Apply_fix_mem("mov_code_addr",0x40000000,0x40000000)
                    mem_address_addr = tests.mpg.Apply_fix_mem("mem_address_addr",0x30000000,0x10000000)
                    mem_address_addr1 = tests.mpg.Apply_fix_mem("mem_address_addr1",0x10000000,0x10000000)
                    tests.Gen_mode_code()
                    tests.Start_user_code(0)
                    tests.Init_PMC(0)
                    tests.Enable_PMC0(0)
                    tests.Instr_write("call %s"%(mov_code_addr["start"]),0)
                    tests.Text_write("org 0x%x"%(mov_code_addr["start"]))
                    tests.Read_PMC0("0x%x"%(pmc0_addr["start"]),0)
                    tests.Instr_write("mov r8, 10000")
                    tests.Tag_write("loop")
                    for j in range(0,count/10):
                        if test_mode == "R":
                            tests.Instr_write("%s xmm0, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset),0)
                            tests.Instr_write("%s xmm1, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x10),0)
                            tests.Instr_write("%s xmm2, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x20),0)
                            tests.Instr_write("%s xmm3, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x30),0)
                            tests.Instr_write("%s xmm4, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x40),0)
                            tests.Instr_write("%s xmm5, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x50),0)
                            tests.Instr_write("%s xmm6, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x60),0)
                            tests.Instr_write("%s xmm7, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x70),0)
                            tests.Instr_write("%s xmm8, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x80),0)
                            tests.Instr_write("%s xmm9, [%s]"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x90),0)
                        elif test_mode == "W":
                            tests.Instr_write("%s [%s], xmm0"%(instruction,mem_address_addr["start"]+j*0xa0+offset),0)
                            tests.Instr_write("%s [%s], xmm1"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x10),0)
                            tests.Instr_write("%s [%s], xmm2"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x20),0)
                            tests.Instr_write("%s [%s], xmm3"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x30),0)
                            tests.Instr_write("%s [%s], xmm4"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x40),0)
                            tests.Instr_write("%s [%s], xmm5"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x50),0)
                            tests.Instr_write("%s [%s], xmm6"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x60),0)
                            tests.Instr_write("%s [%s], xmm7"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x70),0)
                            tests.Instr_write("%s [%s], xmm8"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x80),0)
                            tests.Instr_write("%s [%s], xmm9"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x90),0)
                        elif test_mode == "C":
                            tests.Instr_write("%s xmm0, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset),0)
                            tests.Instr_write("%s [%s], xmm0"%(instruction,mem_address_addr["start"]+j*0xa0+offset),0)
                            tests.Instr_write("%s xmm1, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset+0x10),0)
                            tests.Instr_write("%s [%s], xmm1"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x10),0)
                            tests.Instr_write("%s xmm2, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset+0x20),0)
                            tests.Instr_write("%s [%s], xmm2"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x20),0)
                            tests.Instr_write("%s xmm3, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset+0x30),0)
                            tests.Instr_write("%s [%s], xmm3"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x30),0)
                            tests.Instr_write("%s xmm4, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset+0x40),0)
                            tests.Instr_write("%s [%s], xmm4"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x40),0)
                            tests.Instr_write("%s xmm5, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset+0x50),0)
                            tests.Instr_write("%s [%s], xmm5"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x50),0)
                            tests.Instr_write("%s xmm6, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset+0x60),0)
                            tests.Instr_write("%s [%s], xmm6"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x60),0)
                            tests.Instr_write("%s xmm7, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset+0x70),0)
                            tests.Instr_write("%s [%s], xmm7"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x70),0)
                            tests.Instr_write("%s xmm8, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset+0x80),0)
                            tests.Instr_write("%s [%s], xmm8"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x80),0)
                            tests.Instr_write("%s xmm9, [%s]"%(instruction,mem_address_addr1["start"]+j*0xa0+offset+0x90),0)
                            tests.Instr_write("%s [%s], xmm9"%(instruction,mem_address_addr["start"]+j*0xa0+offset+0x90),0)
                        else:
                            print("No expected test mode %s!"%(test_mode))
                            sys.exit(0)
                    tests.Instr_write("dec r8")
                    tests.Instr_write("jne $loop")
                    tests.Read_PMC0("0x%x"%(pmc0_addr["start"]+0x8),0)
                    tests.Report_PMC(pmc0_addr,0)
                    tests.Gen_hlt_code(0)
                    tests.Gen_sim_cmd(0)
                    tests.Gen_vector()
                tests.Gen_pclmsi_file_list()
                del tests
        

