#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'Ken Zhao'
########################################################
# debug_csmith is used to debug csmith code
########################################################
import sys, os, re
sys.path.append("%s/src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from csmith import Csmith
##############################################MAIN##########################################
i = 0
if __name__ == "__main__":
    tests = Csmith(sys.argv[1:])
    tests.Create_dir()
    tests.Gen_del_file()
    tests.Reset_asm()
    tests.Create_asm(i)
    tests.Initial_interrupt()
    tests.Gen_asm_code(0,i)
    tests.Gen_mode_code()
        ################## Thread 0 Code#################
    for j in range(0,tests.args_option.thread_nums):
        tests.Start_user_code(j)
        tests.Load_asm_code(j,i)   
        tests.Gen_hlt_code(j)
    tests.c_parser.c_code_asm.close()
    tests.Gen_vector()
    tests.Gen_pclmsi_file_list()
    
