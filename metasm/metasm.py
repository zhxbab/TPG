#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' metasm module '
__author__ = 'Ken Zhao'
########################################################
# csmith module is used to converting csmith c_code to avp
########################################################
import sys, os, re, random
sys.path.append("%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from optparse import OptionParser
import metasm_functions
#####################################################Sub Classes###########################
class Metasm(Test_generator):
    def __init__(self,args):
        self.instructions_set0 = {"instr_set_name":"basic","metasm_set_name":"PCLMSI","metasm_X86_name":""}      
        self.instructions_set1 = {"instr_set_name":"fpu","metasm_set_name":"[FPU]","metasm_X86_name":"[FPU]"} 
        self.instructions_set2 = {"instr_set_name":"avx","metasm_set_name":"[AVX]","metasm_X86_name":"[AVX]"} 
        self.instructions_set3 = {"instr_set_name":"aes","metasm_set_name":"[AES]","metasm_X86_name":"[AES]"}
        self.metasm_mode_name = ["LONG","PROT32","COMPAT32"]
        self.metasm_code_start = 0x10000000
        self.metasm_code_offset = 0x10000000
        Test_generator.__init__(self,args)

       
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Metasm *args, **kwargs", version="%Metasm 0.1") #2016-04-25 version 0.1
        args_parser.add_option("-m","--mode", dest="mode", help="The csmith vector mode. [default: %default]\n0x0: 64bit mode\n0x1: 32bit mode\n0x2: compatibility mode\nin 64bit machine use -m32 option relate to compatibility mode"\
                          , type = "int", default = 0)
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 1)
        args_parser.add_option("-t","--threads", dest="thread_nums", help="The vector thread nums."\
                          , type = "int", default = 1)
        args_parser.add_option("--seed", dest="seed", help="Set the seed. [default: %default]\nFor the default value, tpg will generate random seed instead."\
                          , type = "int", default = 0x0)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--intel", dest="intel", help="Support intel platform, APIC ID is 0,2,4,6", action="store_true", default = False)
        args_parser.add_option("--very_short", dest="very_short", help="Change -short to -very-short", action="store_true", default = False)
        args_parser.add_option("--disable_avx", dest="disable_avx", help="disable AVX for support old intel platform", action="store_true", default = False)
        args_parser.add_option("--disable_pcid", dest="disable_pcid", help="disable PCID for support old intel platform", action="store_true", default = False)
        args_parser.add_option("--instr_only", dest="instr_only", help="Cnsim instr only", action="store_true", default = False)            
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        if self.args_option.seed:
            self.seed = self.args_option.seed
        else:
            self.seed = random.randint(1,0xFFFFFFFF)            
        if self.args_option.mode == 0:
            self.mode = "long_mode"
            self.page_mode = "2MB"
            self.metasm_mode_name = "LONG"
        elif self.args_option.mode == 1:
            self.mode = "protect_mode"
            self.page_mode = "4MB"
            self.metasm_mode_name = "PROT32"
        elif self.args_option.mode == 2:
            self.mode = "compatibility_mode"
            self.page_mode = "2MB"
            self.metasm_mode_name = "COMPAT32"
        else:
            Util.Error_exit("Invalid Mode!")
            
        self.threads = self.args_option.thread_nums
        if self.threads>1:
            self.multi_page=1
        else:
            self.multi_page=0            
        self.intel = self.args_option.intel
        self.c_gen = 0
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
        self.disable_avx = self.args_option.disable_avx
        self.disable_pcid = self.args_option.disable_pcid
        
    def Initial_metasm(self, times,  mode):
        if times == 0:
            metasm_functions.reset_for_next_test(1)
        else:
            metasm_functions.reset_for_next_test(0)
        if mode == "long_mode":
            index = 0
        elif mode == "protect_mode":
            index = 1
        else:
            index = 2  
        info("?>SET MODE(%s)"%(self.metasm_mode_name[index]))
        metasm_functions.parse("?>SET MODE(%s)"%(self.metasm_mode_name[index]))
        
    def Print_instructions(self,thread,instr_num):
        instructions_set = [self.instructions_set0,self.instructions_set1,self.instructions_set2,self.instructions_set3][random.randint(0,3)]
        metasm_code_start = self.metasm_code_start + thread*self.metasm_code_offset
        mem_select = "MEM(RANDOM(0x%x..0x%x:16))"%(metasm_code_start,metasm_code_start+self.metasm_code_offset)
        self.mpg.Apply_fix_mem("Metasm_code%d_code"%(thread),metasm_code_start,self.metasm_code_offset)
        info("?>SET INST(%s),X86(%s),%s,GET(%d)"%(instructions_set["metasm_set_name"],instructions_set["metasm_X86_name"],mem_select,instr_num))
        metasm_functions.parse("?>SET INST(%s),X86(%s),%s,GET(%d)"%(instructions_set["metasm_set_name"],instructions_set["metasm_X86_name"],mem_select,instr_num));  
        self.asm_file.write(metasm_functions.output())
        
###############################################MAIN##########################################
if __name__ == "__main__":
    tests = Metasm(sys.argv[1:])
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        tests.Initial_metasm(i,tests.mode)
        tests.Gen_mode_code()
        for j in range(0,tests.threads):
            tests.Start_user_code(j)
            tests.Print_instructions(j,10000)
            tests.Gen_hlt_code(j)
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()









