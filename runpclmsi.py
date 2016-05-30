#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
########################################################
# change_pclmsi_list is used for modifying the pclmsi.list
#
########################################################
import sys, os, logging, re, signal, subprocess
from optparse import OptionParser
from logging import info,debug,error,warning,critical
from operator import eq
global run_pclmsi_p
#########################################Sub route##################################
def Sigint_handler(signal, frame):
    critical("Ctrl+C pressed and Exit!!!")
    run_pclmsi_p.kill()
    sys.exit(0)
def Sigstop_handler(signal, frame):
    global run_pclmsi_p
    run_pclmsi_p.kill()
    sys.exit(0)
#########################################MAIN#######################################
signal.signal(signal.SIGINT,Sigint_handler)
signal.signal(signal.SIGTERM,Sigstop_handler)
parser = OptionParser(usage="%prog arg1 arg2", version="%prog 0.1") #2016-01-15 version 0.2
parser.add_option("-f","--file", dest="list_file", help="The pclmsi list file", default = "None", type = "str")
parser.add_option("--rerun", dest="rerun_times", help="change pclmsi list rerun_times", default = -1, type = "int")
parser.add_option("-p","--path", dest="files_path", help="change pclmsi list path", default = "Not Change", type = "str")
parser.add_option("-c", dest="core_ratio", help="set core ratio(only 8 - 15 is available), don't use this parameter if you want the default core ratio", default = 0, type = "int")
parser.add_option("-l", dest="log_level", help="set log level, 0:no_log; 1:normal; 2:log_name. [default:%default]", default = 0, type = "int")
parser.add_option("--name", dest="log_name", help="when log level = 2, set log name", default = "None", type = "str")
parser.add_option("--debug", dest="_debug", help="Enable the debug mode for change_pclmsi_list", action="store_true", default = False)
parser.add_option("-r", dest="enable_run_pclmsi", help="Enable run_pclmsi", action="store_true", default = False)
parser.add_option("-d", dest="device_num", help="set device num", default = 0, type = "int")
(option, additions) = parser.parse_args(sys.argv[1:])
if len(sys.argv[1:]) == 0:
    error("No parameters! Please use -h")
    sys.exit()
if eq(option.list_file,"None"):
    error("You must input a list file!")
    sys.exit()
if option._debug == True: plevel = logging.DEBUG #plevel is the print information level
else: plevel = logging.INFO
logging.basicConfig(level=plevel, format="%(asctime)s %(filename)10s[line:%(lineno)6d] %(levelname)8s: %(message)s",datefmt="%a, %d %b %Y %H:%M:%S", stream=sys.stdout)
path = os.path.abspath(".")
list_file_full_path = os.path.join(path,option.list_file)
(new_file_path, new_list_file) = os.path.split(list_file_full_path)
new_list_file = "new_"+ new_list_file
new_list_file_full_path = os.path.join(new_file_path,new_list_file)
#info(new_list_file_full_path)
new_file = ""
with open(list_file_full_path,"r") as f_old:
    while True:
        line = f_old.readline()
        new_line = ""
        if line: 
            line = line.strip()
            line = line.split()[0]
            m = re.match(r"\+load:",line)
            if m:
                m = re.match(r"\+load:(.*)",line)
                if m:
                    if eq(option.files_path,"Not Change"):
                        ic_file = m.group(1)
                    else:
                        ic_file = option.files_path + "/" + m.group(1).split('/')[-1]
                    #info(ic_file)
            else:
                if eq(option.files_path,"Not Change"):
                    ic_file = line
                else:
                    ic_file = option.files_path + "/" + line.split('/')[-1]
                #info(ic_file)
            new_line = "+load:"+ ic_file
            if option.rerun_times != -1:
                new_rerun_times = " +rerun_times:"+str(option.rerun_times)
                new_line = new_line + new_rerun_times
            new_line = new_line + " +ignore_all_checks:1"
            if not option.core_ratio == 0:
                if option.core_ratio <= 15 and option.core_ratio >= 8:
                    new_line = new_line + " +clkRatio:%d"%(option.core_ratio)
                else:
                    error("Invalidate pstate!")
            new_file = new_file + new_line + "\n"
        else:
            break;
        
with open(new_list_file_full_path,"w") as f_new:
    f_new.write(new_file)
    
os.system("mv -f %s %s"%(list_file_full_path,list_file_full_path+".org"))
os.system("mv -f %s %s"%(new_list_file_full_path,list_file_full_path))
info("update %s"%(list_file_full_path))
if option.log_level > 2 or option.log_level < 0:
    error("Invalidate log level!")
    sys.exit()    
if eq(option.log_name, "None"):
    if option.log_level == 0:
        log_cmd = "+no_log:1"
    elif option.log_level == 1:
        log_cmd = ""
    else:
        error("When log level is 2, you must set log name")
        sys.exit()
else:
    if option.log_level == 2:
        log_cmd = "+log_name:%s"%(option.log_name)
    else:
        error("When log level is not 2, you must not set log name")
        sys.exit()
if option.enable_run_pclmsi == True:
    run_pclmsi_location = os.getenv("LOCATION_RUN_PCLMSI")
    run_pclmsi_cmd = "%s +device:%d +avpl:%s %s"%(run_pclmsi_location,option.device_num,list_file_full_path,log_cmd)
    info("%s +device:%d +avpl:%s %s"%(run_pclmsi_location,option.device_num,list_file_full_path,log_cmd))
    run_pclmsi_p = subprocess.Popen(run_pclmsi_cmd,stdout=None, stderr=None, shell=True)
    ret = run_pclmsi_p.poll()
    while ret == None:
        ret = run_pclmsi_p.poll()
info("runpclmsi done!")
