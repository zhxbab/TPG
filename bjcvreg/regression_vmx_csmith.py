#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' regression_csmith module '
__author__ = 'Ken Zhao'
########################################################
# regression_csmith module is base class for regression csmith code
########################################################
import sys, os, re, random, time
sys.path.append("/%s/../src"%(sys.path[0]))
sys.path.append("/%s/../vmx"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from optparse import OptionParser
from c_parser import C_parser
from vmx_csmith import Vmx_csmith
from regression import Regression
#####################################################Sub Classes###########################
class Regression_vmx_csmith(Vmx_csmith):
    def __init__(self,args):

        Vmx_csmith.__init__(self,args)
        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Regression_csmith *args, **kwargs", version="%Regression_csmith 0.1") #2016-04-25 version 0.1
#        args_parser.add_option("--seed", dest="seed", help="Set the seed. [default: %default]\nFor the default value, tpg will generate random seed instead."\
#                          , type = "int", default = 0x0)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 10000)
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
        self.c_gen = 1
        self.vector_nums = self.args_option.nums
        self.very_short_cmd = "-very-short"
        self.very_short_num = "400000000"
        self.regression = Regression(self.device)
        self.elf_file = None
        self.disable_avx = 0
        self.disable_pcid = 0
        self.multi_page = 0
        self.multi_ept = 0
        self.intel = 0
        
    def Regression_vector(self):
        time = 2000
        self.c_code_base_name = os.path.join(self.avp_dir_path,self.c_parser.base_name)
        self.regression.Set_remove_flag()
        self.regression.Handle_vecor(self.ic_file,time,self.c_code_base_name)
            
    def Set_fail_dir(self):
        self.regression.fail_dir = self.fail_dir

    def Set_mode(self,mode,page_mode,vmx_client_mode,multi_ept):
        self.mode = mode
        self.page_mode = page_mode
        self.vmx_client_mode = vmx_client_mode
        self.multi_ept = multi_ept