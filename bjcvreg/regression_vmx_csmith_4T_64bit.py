#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' vmx test script '
__author__ = 'Ken Zhao'
########################################################
# vmx test is used to test vmx
########################################################
import sys, os, re
sys.path.append("/%s/../src"%(sys.path[0]))
sys.path.append("/%s/../vmx"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from regression_vmx_csmith import Regression_vmx_csmith
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Regression_vmx_csmith(sys.argv[1:])
    tests.Set_mode("long_mode","2MB","long_mode",1)
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
        for j in range(0,tests.threads):
            tests.Start_user_code(j)
            tests.Vmx_load_asm_code(j,i)
        #tests.Instr_write("vmxon [$vmxon_ptr]",0)
        tests.Gen_hlt_code()
        tests.c_parser.c_code_asm.close()
        tests.Gen_vector()
        tests.Regression_vector()
    tests.Remove_dir()

