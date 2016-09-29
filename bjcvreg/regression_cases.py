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
from optparse import OptionParser
from regression import Regression
from test_generator import Test_generator
###########################################Sub Classes######################################
class Regression_cases(Test_generator):
    def __init__(self,args):
        self.file_list = []
        Test_generator.__init__(self,args)
        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Regression_csmith *args, **kwargs", version="%Regression_csmith 0.1") #2016-04-25 version 0.1
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--skip_fail", dest="skip_fail", help="Skip check fail", action="store_true", default = False)
        args_parser.add_option("--dir", dest="avp_dir", help="Set the avp dir", type="str", default = None)        
        args_parser.add_option("-d","--device", dest="device", help="Set device num. But if run with balancer, the device num will be changed by balancer.", type="int", default = None)
        args_parser.add_option("--arch", dest="arch", help="Set architecture, for tune clk and feature list", type="str", default = "default_arch")     
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        if not self.args_option.avp_dir == None:
            self.avp_dir = os.path.join(self.current_dir_path,self.args_option.avp_dir)
            os.chdir(self.avp_dir)
        else:
            self.Error_exit("Please set the avp dir!")
        if self.args_option.device == None:
            self.Error_exit("You must set a device num!")
        else:
            self.device = self.args_option.device
        self.arch = self.args_option.arch
        self.regression = Regression(self.device,self.arch)
         
        
    def Regression_vector(self):
        time = 300
        self.regression.Set_remove_flag()
        info(self.avp_dir)
        dir_file_list = os.listdir(self.avp_dir)
        for file in dir_file_list:
            m = re.search("\.ic\.gz",file)
            if m:
                self.file_list.append(file)
                if self.args_option.skip_fail:      
                    self.regression.skip_check_fail = True
                self.regression.Handle_vecor(file,time,None,1)            

##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Regression_cases(sys.argv[1:])
    tests.Check_fail_dir()
    tests.Regression_vector()

