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
    tests.Fix_threads(8)
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        tests.Gen_mode_code()
        for j in range(0,8):
            tests.Start_user_code(j)
            if j == 0:
                pass
            elif j == 1:
                pass                         
            elif j == 2:
                pass
            else:
                pass               
            tests.Gen_hlt_code(j)
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()


