#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'Ken Zhao'
########################################################
# regression_csmith_1T_64bit is used to regression csmith code
########################################################
import sys, os, re
sys.path.append("%s/src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from regression_csmith import Regression_csmith
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Regression_csmith(sys.argv[1:])
    tests.Set_mode("long_mode","2MB",1)
    tests.Fix_threads(4)
    tests.Create_dir()
    tests.Set_fail_dir()
    tests.Gen_del_file()
    for i in range(0,tests.vector_nums):
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
        tests.Regression_vector()
    tests.Remove_dir()


