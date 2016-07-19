#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' regression_metasm module '
__author__ = 'Ken Zhao'
########################################################
# regression_metasm module 
########################################################
import sys, os, re, random, time
sys.path.append("/%s/../src"%(sys.path[0]))
from regression import Regression
sys.path.append("/%s/../metasm"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from optparse import OptionParser
from metasm import Metasm
#####################################################Sub Classes###########################
class Regression_metasm(Metasm):
    def __init__(self,args):

        Metasm.__init__(self,args)
        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Regression_csmith *args, **kwargs", version="%Regression_csmith 0.1") #2016-04-25 version 0.1
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 10000)
        args_parser.add_option("-d","--device", dest="device", help="Set device num. But if run with balancer, the device num will be changed by balancer.", type="int", default = None)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        self.seed = str(time.time())
        self.seed = int(self.seed.replace(".","0"))
        if self.args_option.device == None:
            self.Error_exit("You must set a device num!")
        else:
            self.device = self.args_option.device
        self.c_gen = 0
        self.vector_nums = self.args_option.nums
        self.very_short_cmd = "-very-short"
        self.very_short_num = "50000000"
        self.regression = Regression(self.device)
        self.elf_file = None
        self.disable_avx = 0
        self.disable_pcid = 0
        self.intel = 0          
        
    def Regression_vector(self):
        time = 300
        self.regression.Set_remove_flag()
        self.regression.Handle_vecor(self.ic_file,time)
            
    def Set_fail_dir(self):
        if os.getenv("LOCATION_CVREG_VECTOR") == None:
            error("Not env para LOCATION_CVREG_VECTOR")
            sys.exit(0)



##############################################MAIN##########################################
if __name__ == "__main__":
    threads = [1,4][random.randint(0,1)]
    mode = ["long_mode","protect_mode","compatibility_mode"][random.randint(0,2)]
    tests = Regression_metasm(sys.argv[1:])
    tests.Fix_threads(threads)
    tests.Set_mode(mode,threads)    
    tests.Create_dir()
    tests.Set_fail_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        tests.Initial_metasm(i,tests.mode)
        tests.Gen_mode_code()
        for j in range(0,threads):
            tests.Start_user_code(j)
            tests.Print_instructions(j,10000)
            tests.Gen_hlt_code(j)
        tests.Gen_vector()
        tests.Regression_vector()
    tests.Remove_dir()
