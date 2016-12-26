#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' csmith module '
__author__ = 'Ken Zhao'
########################################################
# csmith module is used to converting csmith c_code to avp
########################################################
import sys, os, re, random
sys.path.append("/%s/../../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from optparse import OptionParser
from c_parser import C_parser
from util import Util
#####################################################Sub Classes###########################
class Csmith(Test_generator):
    def __init__(self,args):
        Test_generator.__init__(self,args)       
        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Template_tpg *args, **kwargs", version="%Template_tpg 0.1") #2016-04-25 version 0.1
        args_parser.add_option("-m","--mode", dest="mode", help="The csmith vector mode. [default: %default]\n0x0: 64bit mode\n0x1: 32bit mode\n0x2: compatibility mode\nin 64bit machine use -m32 option relate to compatibility mode"\
                          , type = "int", default = 0)
        args_parser.add_option("-p","--page", dest="page_mode", help="The page mode. [default: %default]\n0x0: normal(4KB in 32/64bit)\n0x1: big(2MB in 64bit and 4MB in 32bit)\n0x2: huge(1G in 64bit)"\
                          , type = "int", default = 1)
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 1)
        args_parser.add_option("-g","--generator", dest="generator", help="0x0: Use Csmith, 0x1: Use randprog"\
                          , type = "int", default = 0)
        args_parser.add_option("-t","--threads", dest="thread_nums", help="The vector thread nums."\
                          , type = "int", default = 1)
        args_parser.add_option("--seed", dest="seed", help="Set the seed. [default: %default]\nFor the default value, tpg will generate random seed instead."\
                          , type = "int", default = 0x0)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--intel", dest="intel", help="Support intel platform, APIC ID is 0,2,4,6", action="store_true", default = False)
        args_parser.add_option("--very_short", dest="very_short", help="Change -short to -very-short", action="store_true", default = False)
        args_parser.add_option("--gcc", dest="gcc", help="Force use gcc", action="store_true", default = False)
        args_parser.add_option("--clang", dest="clang", help="Force use clang", action="store_true", default = False)
        args_parser.add_option("--set_Op", dest="Op", help="Set the Op level", type="str", default = None)
        args_parser.add_option("-f","--file", dest="elf_file", help="The elf file, when input a elf file, the TPG function will cancel", type="str", default = None)
        args_parser.add_option("--disable_avx", dest="disable_avx", help="disable AVX for support old intel platform", action="store_true", default = False)
        args_parser.add_option("--disable_pcid", dest="disable_pcid", help="disable PCID for support old intel platform", action="store_true", default = False)
        args_parser.add_option("--instr_only", dest="instr_only", help="Cnsim instr only", action="store_true", default = False)
        args_parser.add_option("--c_plus", dest="c_plus", help="Gen c++ code", action="store_true", default = False)
        args_parser.add_option("--wc", dest="wc_feature", help="Enable PAT WC", action="store_true", default = False)
        #args_parser.add_option("--pae", dest="pae", help="enable pae in 32bit mode", action="store_true", default = False)           
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        if not self.args_option.elf_file == None:
            self.elf_file = os.path.join(self.current_dir_path,self.args_option.elf_file)
        else:
            self.elf_file = None
        if self.args_option.seed:
            self.seed = self.args_option.seed
        else:
            self.seed = random.randint(1,0xFFFFFFFF)
            
        if self.args_option.mode == 0:
            self.mode = "long_mode"
            if self.args_option.page_mode == 0:
                self.page_mode = "4KB_64bit"
            elif self.args_option.page_mode == 1:
                self.page_mode = "2MB"
            elif self.args_option.page_mode == 2:
                self.page_mode = "1GB"
            else:
                Util.Error_exit("Invalid Page mode for long mode!")
        elif self.args_option.mode == 1:
            self.mode = "protect_mode"
            if self.args_option.page_mode == 0:
                self.page_mode = "4KB_32bit"
            elif self.args_option.page_mode == 1:
                self.page_mode = "4MB"
            else:
                Util.Error_exit("Invalid Page mode for protect mode!")
        elif self.args_option.mode == 2:
            self.mode = "compatibility_mode"
            if self.args_option.page_mode == 0:
                self.page_mode = "4KB_64bit"
            elif self.args_option.page_mode == 1:
                self.page_mode = "2MB"
            elif self.args_option.page_mode == 2:
                self.page_mode = "1GB"
            else:
                Util.Error_exit("Invalid Page mode for compatibility mode!")
        else:
            Util.Error_exit("Invalid Mode!")
            
        self.threads = self.args_option.thread_nums
        if self.threads>1:
            self.multi_page=1
        else:
            self.multi_page=0            
        self.intel = self.args_option.intel
        if self.mode != "protect_mode" and self.page_mode == "4KB_64bit":
            Util.Error_exit("Not support convert csmith code to avp in 4KB page Mode!")
        else:
            self.c_gen = 1
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
            Util.Error_exit("Invalid optimize level!")
        self.disable_avx = self.args_option.disable_avx
        self.disable_pcid = self.args_option.disable_pcid
        self.c_plus = self.args_option.c_plus
        self.wc_feature = self.args_option.wc_feature
        self.pae = False
        self.generator = self.args_option.generator
#        if self.page_mode != "4KB_32bit":
#            self.pae = self.args_option.pae
#        else:
#            Util.Error_exit("Don't use pae in 4KB 32bit")
        
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
            
    def Gen_asm_code(self,thread, num):
        self.c_parser = C_parser(self.bin_path,self.avp_dir_path,self.mode,self.instr_manager,self.mpg, self.c_plus, self.generator)
        self.c_parser.asm_file = self.asm_file
        self.c_parser.wc_feature = self.wc_feature
        if self.elf_file != None:
            ret_gen_asm_code = self.c_parser.Get_fix_c_asm(self.elf_file)
        else:
            self.Force_compiler_and_optimize()
            ret_gen_asm_code = self.c_parser.Gen_c_asm(thread,num,self.Op)
        if ret_gen_asm_code:
            del_asm = self.asm_list.pop()
            os.system("rm -f %s"%(del_asm))
            warning("%s's c code can't be executed successfully, so remove it from asm list"%(del_asm))
        return ret_gen_asm_code
    
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Csmith(sys.argv[1:])
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
            tests.Load_asm_code(j,i)
            tests.Gen_hlt_code(j)
        tests.c_parser.c_code_asm.close()
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()







