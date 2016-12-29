#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' regression_test '
__author__ = 'Ken Zhao'
import os, signal, sys
from optparse import OptionParser
result = 0
all_scripts = []



def Sigint_handler(self, signal, frame):
    critical("Ctrl+C pressed and Exit!!!")
    result = 1
    sys.exit(0)
def Parse_input(args):
    args_parser = OptionParser(usage="%tpg *args, **kwargs", version="%tpg 0.1") #2016-04-25 version 0.1
    args_parser.add_option("-s", dest="script", help="script path", type="str", default = None)
    args_parser.add_option("-d","--device", dest="device", help="device num", type="int", default = None)
    args_parser.add_option("--dual", dest="dual", help="For dual die", action="store_true", default = False)
    args_parser.add_option("--arch", dest="arch", help="Set architecture, for tune clk and feature list", type="str", default = None)
    (args_option, args_additions) = args_parser.parse_args(args)
    return (args_option, args_additions)
if __name__ == "__main__":
    (args_option, args_additions) = Parse_input(sys.argv[1:]) 
    signal.signal(signal.SIGINT,Sigint_handler)
    n = 0
    plusargs = ""
    current_dir_path = os.path.abspath(".") # current dir path
    if args_option.device == None or args_option.script == None:
        print("Need device num and script name")
        sys.exit(0)
    script = os.path.join(current_dir_path,args_option.script)
    if args_option.dual == True:
        plusargs = "--dual"
    if args_option.arch != None:
        plusargs = plusargs + " --arch=\"%s\""%(args_option.arch)
    while True:
        print("Regression Count %d"%(n))
        result = os.system("%s -d %d -n 1 %s"%(script, args_option.device, plusargs))
        n = n + 1
        if result != 0:
            sys.exit(0)