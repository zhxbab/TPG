#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'Ken Zhao'
########################################################
# csmith_4T is used to convert csmith c_code to avp
########################################################
import sys, os, re
sys.path.append("%s/src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from csmith import Csmith
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Csmith(sys.argv[1:])
    tests.Fix_threads(4)
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        if tests.Gen_asm_code(0,i):
            continue
        tests.Gen_mode_code()
        for j in range(0,4):
            tests.Start_user_code(j)
            tests.Load_asm_code(j,i)
            tests.Gen_hlt_code(j)
        tests.c_parser.c_code_asm.close()
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()


