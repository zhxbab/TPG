#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' template module '
__author__ = 'Ken Zhao'
########################################################
# template module is used to gen a template for tpg
########################################################
import sys, os, re, random
sys.path.append("/%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from optparse import OptionParser
#####################################################Sub Classes###########################
class Template_tpg(Test_generator):      
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Template_tpg *args, **kwargs", version="%Template_tpg 0.1") #2016-04-25 version 0.1
        args_parser.add_option("-m","--mode", dest="mode", help="The vector mode. [default: %default]\n0x0: 64bit mode\n0x1: 32bit mode\n0x2: compatibility mode"\
                          , type = "int", default = 0)
        args_parser.add_option("-p","--page", dest="page_mode", help="The page mode. [default: %default]\n0x0: normal(4KB in 32/64bit)\n0x1: big(2MB in 64bit and 4MB in 32bit)\n0x2: huge(1G in 64bit)"\
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
        args_parser.add_option("--multi_page", dest="multi_page", help="enable_multi_page", action="store_true", default = False)
        args_parser.add_option("--pae", dest="pae", help="enable pae in 32bit mode", action="store_true", default = False)    
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
                self.Error_exit("Invalid Page mode for long mode!")
        elif self.args_option.mode == 1:
            self.mode = "protect_mode"
            if self.args_option.page_mode == 0:
                self.page_mode = "4KB_32bit"
            elif self.args_option.page_mode == 1:
                self.page_mode = "4MB"
            else:
                self.Error_exit("Invalid Page mode for protect mode!")
        elif self.args_option.mode == 2:
            self.mode = "compatibility_mode"
            if self.args_option.page_mode == 0:
                self.page_mode = "4KB_64bit"
            elif self.args_option.page_mode == 1:
                self.page_mode = "2MB"
            elif self.args_option.page_mode == 2:
                self.page_mode = "1GB"
            else:
                self.Error_exit("Invalid Page mode for compatibility mode!")
        else:
            self.Error_exit("Invalid Mode!")
            
        self.threads = self.args_option.thread_nums
        self.intel = self.args_option.intel
        self.c_gen = 0
        if self.args_option.very_short == True:
            self.very_short_cmd = "-very-short"
            self.very_short_num = "1000000000"
        else:
            self.very_short_cmd = "-short"
            self.very_short_num = "100000"
        self.disable_avx = self.args_option.disable_avx
        self.disable_pcid = self.args_option.disable_pcid
        self.multi_page = self.args_option.multi_page
        if self.page_mode != "4KB_32bit":
            self.pae = self.args_option.pae
        else:
            if self.args_option.pae:
                self.Error_exit("Don't use pae in 4KB 32bit")
            else:
                self.pae = self.args_option.pae
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Template_tpg(sys.argv[1:])
    tests.Fix_threads(tests.threads)
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        tests.Gen_mode_code()
        tests.Sync_threads()
        for j in range(0,tests.threads):
            tests.Start_user_code(j)
            if j == 0:
                pass
            else:
                pass               
            tests.Gen_hlt_code(j)
            tests.Gen_sim_cmd(j)
        tests.Close_page_table()
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()


