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
from template_tpg import Template_tpg
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Template_tpg(sys.argv[1:])
    tests.Fix_threads(1)
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        tests.Gen_mode_code()
        tests.Start_user_code(0)
        tests.Instr_write("mov eax,0x1",0)
        tests.Gen_hlt_code(0)
    tests.Gen_file_list()


