#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test module '
__author__ = 'Ken Zhao'
########################################################
# test module is used to test different function in tpg
########################################################
import sys, os, re
from logging import info, error, debug, warning, critical
sys.path.append("%s/src"%(sys.path[0]))
from test_generator import Test_generator







##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Test_generator(sys.argv[1:])
    tests.Create_dir()
    for i in range(0,tests.args_option.nums):
        tests.Create_asm(i)
        tests.Gen_mode_code()
        tests.Reset_asm()
