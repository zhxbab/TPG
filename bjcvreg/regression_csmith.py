#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' regression_csmith module '
__author__ = 'Ken Zhao'
########################################################
# regression_csmith module is base class for regression csmith code
########################################################
import sys, os, re, random, time
sys.path.append("/%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from optparse import OptionParser
from c_parser import C_parser
from csmith import Csmith
from regression import Regression
#####################################################Sub Classes###########################
class Regression_csmith(Csmith):
    def __init__(self,args):

        Csmith.__init__(self,args)
        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Regression_csmith *args, **kwargs", version="%Regression_csmith 0.1") #2016-04-25 version 0.1
#        args_parser.add_option("--seed", dest="seed", help="Set the seed. [default: %default]\nFor the default value, tpg will generate random seed instead."\
#                          , type = "int", default = 0x0)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 10000)
        args_parser.add_option("--intel", dest="intel", help="Support intel platform, APIC ID is 0,2,4,6", action="store_true", default = False)
        args_parser.add_option("-d","--device", dest="device", help="Set device num. But if run with balancer, the device num will be changed by balancer.", type="int", default = None)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        self.force_clang = 0
        self.force_gcc = 0
        self.Op = None
        self.seed = str(time.time())
        self.seed = int(self.seed.replace(".","0"))
        if self.args_option.device == None:
            self.Error_exit("You must set a device num!")
        else:
            self.device = self.args_option.device
        self.intel = self.args_option.intel
        self.c_gen = 1
        self.vector_nums = self.args_option.nums
        self.threads = 1
        self.very_short_cmd = "-very-short"
        self.very_short_num = "10000000"
        self.regression = Regression(self.device)
        self.elf_file = None
        
    def Regression_vector(self):
        time = 200
        self.c_code_base_name = os.path.join(self.avp_dir_path,self.c_parser.base_name)
        self.regression.Set_remove_flag()
        self.regression.Handle_vecor(self.ic_file,time,self.c_code_base_name)
            
    def Set_fail_dir(self):
        self.regression.fail_dir = self.fail_dir

    def Set_mode(self,mode,page_mode):
        self.mode = mode
        self.page_mode = page_mode

