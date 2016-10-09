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
        args_parser.add_option("--dual", dest="dual", help="For dual die", action="store_true", default = False)
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 10000)
        args_parser.add_option("-d","--device", dest="device", help="Set device num. But if run with balancer, the device num will be changed by balancer.", type="int", default = None)
        args_parser.add_option("--arch", dest="arch", help="Set architecture, for tune clk and feature list", type="str", default = "default_arch")
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
        self.arch = self.args_option.arch
        self.regression = Regression(self.device,self.arch)
        self.elf_file = None
        self.disable_avx = 0
        self.disable_pcid = 0
        self.intel = 0 
        self.dual = self.args_option.dual      
        self.multi_page = 0
        
    def Regression_vector(self):
        time = 300
        self.reglog_name = "/tmp/%s"%(self.avp_dir_name)
        self.regression.freglog = open(self.reglog_name,"w")
        info("Log is %s"%(self.reglog_name))
        self.regression.Set_remove_flag()
        self.regression.Handle_vecor(self.ic_file,time)
        self.regression.freglog.close()
        
    def Set_fail_dir(self):
        if os.getenv("LOCATION_CVREG_VECTOR") == None:
            error("Not env para LOCATION_CVREG_VECTOR")
            sys.exit(0)



##############################################MAIN##########################################
if __name__ == "__main__":
    mode = ["long_mode","protect_mode","compatibility_mode"][random.randint(0,2)]
    tests = Regression_metasm(sys.argv[1:])
    if tests.dual:
        threads = [1,8][random.randint(0,1)]
    else:
        threads = [1,4][random.randint(0,1)]      
    if mode == "protect_mode":
        tests.pae = [True,False][random.randint(0,1)]
    else:
        tests.pae = False
    tests.Fix_threads(threads)
    tests.Set_mode(mode,threads)    
    tests.Create_dir()
    tests.Check_fail_dir()
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
