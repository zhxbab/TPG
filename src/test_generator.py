#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test_generator module '
__author__ = 'Ken Zhao'
##########################################################
# test_generator module is used to merge differnet classes
# and generate the test vectors
##########################################################
import sys, os, signal, random
from logging import info, error, debug, warning, critical
from args import Args
from util import Util
from mem import Mem
from mode import Mode
from instruction import Instr
class Test_generator(Args,Util):
    def __init__(self,args):
        signal.signal(signal.SIGINT,self.Sigint_handler)
        Args.__init__(self,args)
        self.avp_dir_seed = random.randint(1,0xFFFF)
        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.args_option.thread_nums,self.mode,self.avp_dir_seed)
        self.mem = Mem()
        self.instr_manager = Instr()
        #self.Create_asm()
    def Create_dir(self):
        cmd = "mkdir %s/%s"%(self.realbin_path,self.avp_dir_name)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        self.avp_dir_path = os.path.join(self.realbin_path,self.avp_dir_name)
        #info(self.avp_dir_path)
    def Create_asm(self,index):
        self.asm_name = "%s_%s_%sT_%s_%d.asm"%(self.realbin_name,index,self.args_option.thread_nums,self.mode,self.seed)
        self.asm_path = os.path.join(self.avp_dir_path,self.asm_name)
        self.asm_file = open(self.asm_path,"w")
    
    def Gen_mode_code(self):

        self.mode = Mode(self.mem, self.mode, self.asm_file, self.instr_manager)
            
    def Reset_asm(self):
        pass