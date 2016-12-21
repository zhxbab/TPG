#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' Manage_vectors '
__author__ = 'Ken Zhao'
########################################################
# Manage_vectors is used to manage Agner vectors
########################################################
import os, sys, logging, random, signal, subprocess, re, csv,threading,time
from optparse import OptionParser
from logging import info, error, debug, warning, critical
args_parser = OptionParser(usage="%Agner *args, **kwargs", version="%Agner 0.1") #2016-04-25 version 0.1
args_parser.add_option("-d","--dir", dest="dir", help="The source dir", type="str", default = None)
args_parser.add_option("-n","--name", dest="name", help="The instr name for list file", type="str", default = None)
(args_option, args_additions) = args_parser.parse_args(sys.argv[1:])
current_dir_path = os.path.abspath(".") # current dir path
if not args_option.dir == None:
    all_dir = os.path.join(current_dir_path,args_option.dir)
    if args_option.name ==None:
        print("Name is must!")
        sys.exit(0)
    else:
        os.system("mkdir %s/vectors/%s"%(current_dir_path,args_option.name))
else:
    print("Dir is must!")
    sys.exit(0)
dir_list = os.listdir(all_dir)
for dir in dir_list:
    if os.path.isdir("%s/%s"%(all_dir,dir)):
        print("mv vectors/%s vectors/%s/%s "%(dir,args_option.name,dir))
        os.system("mv vectors/%s vectors/%s/%s "%(dir,args_option.name,dir))