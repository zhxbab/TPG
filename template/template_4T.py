#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test module '
__author__ = 'Ken Zhao'
########################################################
# test module is used to test different function in tpg
########################################################
import sys, os, re
sys.path.append("/%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from template_tpg import Template_tpg
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Template_tpg(sys.argv[1:])
    tests.Fix_threads(4)
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        tests.Gen_mode_code()
        for j in range(0,4):
            tests.Start_user_code(j)
            if j == 0:
        ################## Thread 0 Code#################
                tests.Instr_write("mov eax,0x0",j)
            elif j == 1:
        ################# Thread 1 Code#################
                tests.Instr_write("mov eax,0x1",j)
            elif j == 2:
        ################# Thread 2 Code#################
                tests.Instr_write("mov eax,0x2",j)
            else:
        ################# Thread 3 Code#################
                tests.Instr_write("mov eax,0x3",j)                 
            tests.Gen_hlt_code(j)
            tests.Gen_sim_cmd(j)
            
    tests.Gen_file_list()


