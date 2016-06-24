#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' vmx test script '
__author__ = 'Ken Zhao'
########################################################
# vmx test is used to test vmx
########################################################
import sys, os, re
sys.path.append("/%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from vmx_basic import Vmx_basic
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Vmx_basic(sys.argv[1:])
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        tests.Gen_mode_code()
        for j in range(0,tests.threads):
            tests.Start_user_code(j)
            tests.Gen_hlt_code(j)
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()


