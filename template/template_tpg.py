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
    def Fix_threads(self,threads):
        self.threads = threads
        
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
        args_parser.add_option("--no_very_short", dest="very_short", help="Change -very-short to short", action="store_false", default = True) 
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
        self.c_gen = 0
        if self.args_option.very_short == True:
            self.very_short_cmd = "-very-short"
            self.very_short_num = "10000000"
        else:
            self.very_short_cmd = "-short"
            self.very_short_num = "100000"
            
    def Create_dir(self):
        self.avp_dir_seed = random.randint(1,0xFFFF)
        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.threads,self.mode,self.avp_dir_seed)
        cmd = "mkdir %s/%s"%(self.realbin_path,self.avp_dir_name)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        self.avp_dir_path = os.path.join(self.realbin_path,self.avp_dir_name)
        self.Create_global_info()

