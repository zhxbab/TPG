#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' Agner diff'
__author__ = 'Ken Zhao'
##########################################################
# Agner diff is used to diff performance for different cpu
##########################################################
import os, sys, logging, random, signal, subprocess, re, csv,threading,time
from optparse import OptionParser
from logging import info, error, debug, warning, critical
############################################Class##########################################
class Agner_diff:
    def __init__(self,args):
        self.current_dir_path = os.path.abspath(".") # current dir path
        self.Parse_input(args)
        self.Set_logging() #Set logging
        signal.signal(signal.SIGINT,self.Sigint_handler)
        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="%Agner_diff *args, **kwargs", version="%Agner_diff 0.1") #2016-04-25 version 0.1
        args_parser.add_option("-f","--file", dest="csv_file", help="The Agner result file(.csv)", type="str", default = None)
        args_parser.add_option("-s","--source", dest="source_name", help="The source cpu name", type="str", default = None)
        args_parser.add_option("-t","--target", dest="target_name", help="The target cpu name", type="str", default = None)
        args_parser.add_option("-r","--range", dest="range", help="The compare range(0-100)", type="int", default = 10)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        if not self.args_option.csv_file == None:
            self.csv_file = os.path.join(self.current_dir_path,self.args_option.csv_file)
        else:
            self.Error_exit("Please input the compared file!")
        if not self.args_option.source_name == None:
            self.source_name = self.args_option.source_name
        else:
            self.Error_exit("Please input the source cpu name!")
        if not self.args_option.target_name == None:
            self.target_name = self.args_option.target_name
        else:
            self.Error_exit("Please input the target cpu name")                    
        self.range = float(self.args_option.range)/100
        
    def Set_logging(self):
        if self.args_option._debug == True: plevel = logging.DEBUG #plevel is the print information level
        else: plevel = logging.INFO
        logging.basicConfig(level=plevel, format="%(asctime)s %(filename)10s[line:%(lineno)6d] %(levelname)8s: %(message)s",
                        datefmt="%a, %d %b %Y %H:%M:%S", stream=sys.stdout)
        
    def Sigint_handler(self, signal, frame):
        critical("Ctrl+C pressed and Exit!!!")
        sys.exit(0)
        
    def Error_exit(cls,cmd):
        error(cmd)
        sys.exit(0)
        
    def Diff_perf(self):
        line_count = 0
        source_name_match = 0
        target_name_match = 0
        source_name = ""
        target_name = ""
        self.log = self.csv_file.replace(".csv",".log")
        if os.path.exists(self.csv_file):
            fl = open(self.log,"w")
            self.csv_file_tmp = file(self.csv_file,'r')
            self.csvfile = csv.DictReader(self.csv_file_tmp)
            for line in self.csvfile:
                if line_count == 0:
                    for name in line.keys():
                        m = re.search(self.source_name,name)
                        if m:
                            if source_name_match == 0:
                                source_name_match = 1
                                source_name = name
                                #info("source name match")
                            else:
                                 self.Error_exit("Double Match source name, Please check!")                               
                        m = re.search(self.target_name,name)
                        if m:
                            if target_name_match == 0:
                                target_name_match = 1
                                #info("target name match")
                                target_name = name
                            else:
                                self.Error_exit("Double Match target name, Please check!")
                    if source_name_match and target_name_match:
                        source_value = float(line[source_name])
                        target_value = float(line[target_name])
                        if source_value >= target_value:
                            delta = source_value - target_value
                            delta_name = "improve"
                        elif source_value < target_value:
                            delta = target_value - source_value
                            delta_name = "drop"
                        if float(delta/source_value) >= self.range:
                            fl.write("Instruction %s Target: %s(%.4f) compares to Source: %s(%.4f) %s %.2f%%\n"\
                             %(line["Instr/Platform"],target_name,target_value,source_name,source_value,delta_name,float(delta/source_value*100)))
                            #info("Instruction %s Target: %s(%.4f) compares to Source: %s(%.4f) %s %.2f%%"\
                            #    %(line["Instr/Platform"],target_name,target_value,source_name,source_value,delta_name,float(delta/source_value*100)))
                    else:
                        self.Error_exit("Name does't Match!")    
                else:
                    source_value = float(line[source_name])
                    target_value = float(line[target_name])
                    if source_value >= target_value:
                        delta = source_value - target_value
                        delta_name = "improve"
                    elif source_value < target_value:
                        delta = target_value - source_value
                        delta_name = "drop"
                    if float(delta/source_value) >= self.range:
                        fl.write("Instruction %s Target: %s(%.4f) compares to Source: %s(%.4f) %s %.2f%%\n"\
                             %(line["Instr/Platform"],target_name,target_value,source_name,source_value,delta_name,float(delta/source_value*100)))
                        #info("Instruction %s Target: %s(%.4f) compares to Source: %s(%.4f) %s %.2f%%"\
                             #%(line["Instr/Platform"],target_name,target_value,source_name,source_value,delta_name,float(delta/source_value*100)))
                line_count += 1
            fl.close()
        else:
            self.Error_exit("%s don't exit"%(self.csv_file))
###########################################################Main############################################
if __name__ == "__main__":
    agner_diff = Agner_diff(sys.argv[1:])
    agner_diff.Diff_perf()
    agner_diff.csv_file_tmp.close()