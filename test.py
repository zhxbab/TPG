#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test module '
__author__ = 'Ken Zhao'
########################################################
# test module is used to test different function in tpg
########################################################
import sys, os, re
sys.path.append("%s/src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator







##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Test_generator(sys.argv[1:])
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Gen_mode_code()
        tests.Gen_hlt_code()
    tests.Gen_file_list()
        #info(tests.instr_manager.Get_instr())
        #tests.Msr_Rmw(0x80,"s8r16s0s3r56s63")

