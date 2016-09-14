#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__author__ = 'Ken Zhao'
########################################################
# test_regression is used to test regression function
########################################################
import sys, os, re, logging
sys.path.append("%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from regression import Regression
##############################################MAIN##########################################
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(filename)10s[line:%(lineno)6d] %(levelname)8s: %(message)s",
                        datefmt="%a, %d %b %Y %H:%M:%S", stream=sys.stdout)
    vector = Regression(0)
    vector.Reset_remove_flag()
    vector.Handle_vecor("%s/test_fail_reset.ic.gz"%(os.path.abspath(".")),20)
    #vector.Parse_pclmsi_log_sum("test.sum")
    #tests.Gen_pclmsi_file_list()
