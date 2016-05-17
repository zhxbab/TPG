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
#####################################################Sub Classes###########################
class Csmith(Test_generator):
    def Fix_threads(self,threads):
        self.threads = threads
        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.threads,self.mode,self.avp_dir_seed)
        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Template_tpg *args, **kwargs", version="%Template_tpg 0.1") #2016-04-25 version 0.1
        args_parser.add_option("-m","--mode", dest="mode", help="The vector mode. [default: %default]\n0x0: 64bit mode\n0x1: 32bit mode\n0x2: compatibility mode"\
                          , type = "int", default = 0)
        args_parser.add_option("-p","--page", dest="page_mode", help="The page mode. [default: %default]\n0x0: normal(4KB in 32/64bit)\n0x1: big(2MB in 64bit and 4MB in 32bit)\n0x2: huge(1G in 64bit)"\
                          , type = "int", default = 1)
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 1)
        args_parser.add_option("-t","--threads", dest="thread_nums", help="The vector thread nums."\
                          , type = "int", default = 1)
        args_parser.add_option("--seed", dest="seed", help="Set the seed. [default: %default]\nFor the default value, tpg will generate random seed instead."\
                          , type = "int", default = 0x0)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--intel", dest="intel", help="Support intel platform, APIC ID is 0,2,4,6", action="store_true", default = False)
        args_parser.add_option("--no_very_short", dest="very_short", help="Change -very-short to short", action="store_false", default = True)
        args_parser.add_option("--gcc", dest="gcc", help="Force use gcc", action="store_true", default = False)
        args_parser.add_option("--clang", dest="clang", help="Force use clang", action="store_true", default = False)
        args_parser.add_option("--set_Op", dest="Op", help="Set the Op level", type="str", default = None)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        
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
        self.intel = self.args_option.intel
        if self.mode != "protect_mode" and self.page_mode == "4KB_64bit":
            Util.Error_exit("Not support convert csmith code to avp in 4KB page Mode!")
        else:
            self.c_gen = 1
        if self.args_option.very_short == True:
            self.very_short_cmd = "-very-short"
            self.very_short_num = "100000000"
        else:
            self.very_short_cmd = "-short"
            self.very_short_num = "200000"
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
            
    def Force_compiler_and_optimize(self):
        if self.force_gcc == 1:
            self.c_parser.c_compiler = self.c_parser.gcc
            self.c_parser.cplus_compiler = self.c_parser.gcc_cplus
        if self.force_clang == 1:
            self.c_parser.c_compiler = self.c_parser.clang
            self.c_parser.cplus_compiler = self.c_parser.clang_cplus
        if self.Op != None:
            self.c_parser.optimize = self.Op
            
    def Gen_asm_code(self,thread, num):
        self.c_parser = C_parser(self.bin_path,self.avp_dir_name,self.mode,self.instr_manager,self.mpg)
        self.c_parser.asm_file = self.asm_file
        self.Force_compiler_and_optimize()
        ret_gen_asm_code = self.c_parser.Gen_c_asm(thread,num,self.mode)
        if ret_gen_asm_code:
            del_asm = self.asm_list.pop()
            warning("%s's c code can't be executed successfully, so remove it from asm list"%(del_asm))
        return ret_gen_asm_code

