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
        args_parser.add_option("--dual", dest="dual", help="For dual die", action="store_true", default = False)
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 10000)
        #args_parser.add_option("--intel", dest="intel", help="Support intel platform, APIC ID is 0,2,4,6", action="store_true", default = False)
        args_parser.add_option("-d","--device", dest="device", help="Set device num. But if run with balancer, the device num will be changed by balancer.", type="int", default = None)
        args_parser.add_option("--arch", dest="arch", help="Set architecture, for tune clk and feature list", type="str", default = "default_arch") 
        args_parser.add_option("--bustool", dest="bustool", help="For support bustool", action="store_true", default = False)    
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
        self.very_short_num = "50000000"
        self.arch = self.args_option.arch
        self.bustool = self.args_option.bustool
        self.regression = Regression(self.device,self.arch,self.bustool)
        self.elf_file = None
        self.disable_avx = 0
        self.disable_pcid = 0
        self.intel = 0
        self.multi_page = 0
        if random.randint(0,1):
            self.c_plus = True
        else:
            self.c_plus = False            
        self.dual = self.args_option.dual 
        self.pae = False
        sefl.wc_feature = False
        
        
    def Regression_vector(self):
        if self.wc_feature:
            time = 900
        else:
            time = 300
        self.reglog_name = "/tmp/%s"%(self.avp_dir_name)
        self.regression.freglog = open(self.reglog_name,"w")
        info("Log is %s"%(self.reglog_name))
        self.c_code_base_name = os.path.join(self.avp_dir_path,self.c_parser.base_name)
        self.regression.Set_remove_flag()
        self.regression.Handle_vecor(self.ic_file,time,self.c_code_base_name)
        self.regression.freglog.close()

        
##############################################MAIN##########################################
if __name__ == "__main__":
    mode = ["long_mode","protect_mode","compatibility_mode"][random.randint(0,2)]
    tests = Regression_csmith(sys.argv[1:])
    if tests.dual:
        threads = [1,8][random.randint(0,1)]
    else:
        threads = [1,4][random.randint(0,1)]
    tests.wc_feature = [False,True][random.randint(0,1)]
    if tests.wc_feature:
        tests.regression.rerun_times = 100
    #tests.generator = [0,1][random.randint(0,1)]
    tests.generator = 0
    tests.Set_mode(mode,threads,0)
    tests.Fix_threads(threads)
    tests.Create_dir()
    tests.Check_fail_dir()
    tests.Gen_del_file()
    for i in range(0,tests.vector_nums):
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
        if os.path.exists(tests.ic_file):
            tests.Regression_vector()
    tests.Remove_dir()

