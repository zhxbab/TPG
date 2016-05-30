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
from vmx_csmith import Vmx_csmith
##############################################MAIN##########################################
if __name__ == "__main__":
    i = 0
    tests = Vmx_csmith(sys.argv[1:])
    tests.Fix_threads(1)
    tests.Create_dir()
    tests.Gen_del_file()
    tests.Reset_asm()
    tests.Create_asm(i)
    tests.Initial_interrupt()
    tests.Gen_asm_code(0,i)
    tests.Gen_mode_code()
    tests.Start_user_code(0)
    tests.Vmx_load_asm_code(0,i)
    tests.Gen_hlt_code(0)
    tests.Gen_vector()
    tests.Gen_pclmsi_file_list()


