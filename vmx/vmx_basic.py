#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' vmx_basic module '
__author__ = 'Ken Zhao'
########################################################
# vmx_basic module is used to supprot vmx
########################################################
import sys, os, re, random
sys.path.append("/%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from optparse import OptionParser
from vmx_mode import Vmx_mode
#####################################################Sub Classes###########################
class Vmx_basic(Test_generator):        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Vmx *args, **kwargs", version="%Vmx 0.1") #2016-04-25 version 0.1
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 1)
        args_parser.add_option("-t","--threads", dest="thread_nums", help="The vector thread nums."\
                          , type = "int", default = 1)
        args_parser.add_option("--seed", dest="seed", help="Set the seed. [default: %default]\nFor the default value, tpg will generate random seed instead."\
                          , type = "int", default = 0x0)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--intel", dest="intel", help="Support intel platform, APIC ID is 0,2,4,6", action="store_true", default = False)
        args_parser.add_option("--no_very_short", dest="very_short", help="Change -very-short to short", action="store_true", default = False)  
        (self.args_option, self.args_additions) = args_parser.parse_args(args)       
        if self.args_option.seed:
            self.seed = self.args_option.seed
        else:
            self.seed = random.randint(1,0xFFFFFFFF)                  
        self.threads = self.args_option.thread_nums
        self.intel = self.args_option.intel
        self.c_gen = 0
        self.mode = "long_mode"
        self.page_mode = "2MB"
        if self.args_option.very_short == True:
            self.very_short_cmd = "-very-short"
            self.very_short_num = "10000000"
        else:
            self.very_short_cmd = "-short"
            self.very_short_num = "100000"
            
    def Gen_mode_code(self):
        self.vmx_mode_code = Vmx_mode(self.hlt_code,self.mpg, self.instr_manager, self.ptg, self.threads, self.simcmd, self.intel, self.interrupt,self.c_parser)
        self.vmx_mode_code.asm_file = self.asm_file
        self.vmx_mode_code.inc_path = self.inc_path
        [self.stack_segs,self.user_code_segs] = self.vmx_mode_code.Mode_code(self.mode,self.c_gen)

    def Gen_hlt_code(self,thread_num):
        if thread_num == 0:
            self.Instr_write("vmclear [$vmcs_guest_ptr]")
            self.Instr_write("vmxoff")
            self.Text_write("jmp $%s"%(self.hlt_code["name"]))
            self.Text_write("org 0x%x"%(self.hlt_code["start"]))
            self.Tag_write(self.hlt_code["name"])
            self.Text_write("hlt")
        elif 0 < thread_num < 4:
            self.Text_write("jmp $%s"%(self.hlt_code["name"]))
        else:
            self.Error_exit("Invalid thread num!")

    def Start_user_code(self,thread):
        self.Comment("##Usr code")
        self.Instr_write("call [eax+&@%s]"%(self.vmx_mode_code.thread_info_pointer["name"]))
        self.Text_write("org 0x%x"%(self.user_code_segs[thread]["start"]))
        self.Tag_write(self.user_code_segs[thread]["name"])
        if self.mode == "long_mode":
            self.Text_write("use 64")
        else:
            self.Text_write("use 32") 
        self.Instr_write("vmxon [0x%x]"%(self.stack_segs[self.threads-1]["end"]),0)