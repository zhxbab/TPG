#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test module '
__author__ = 'Ken Zhao'
########################################################
# test module is used to test different function in tpg
########################################################
import sys, os, re
sys.path.append("%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from optparse import OptionParser
import signal,random
from mem import Mem
##############################################Sub Class#####################################
class Pclmsi_spc(Test_generator):
    def __init__(self,args):
        signal.signal(signal.SIGINT,self.Sigint_handler)
        self.current_dir_path = os.path.abspath(".") # current dir path
        self.realbin_path = sys.path[0] # realbin path 
        self.realbin_name = os.path.realpath(sys.argv[0]).split(".")[0].split("/")[-1] # realbin name
        self.tpg_path = os.getenv("LOCATION_TPG") 
        self.mode = "long_mode"
        self.page_mode = "2MB"
        self.intel = 0
        self.threads = 4
        self.Parse_input(args)
        self.Set_logging()
        self.avp_dir_seed = random.randint(1,0xFFFF)
        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.threads,self.mode,self.avp_dir_seed)
        self.asm_list = []
        self.inc_path = "%s/include"%(self.tpg_path)
        self.bin_path = "%s/bin"%(self.tpg_path)
        self.seed = 0x0
        self.mpg = Mem()
        self.c_parser = ""
        self.c_gen = 0
        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="%pclmsi_spc *args, **kwargs", version="%pclmsi_spc 0.1")
        args_parser.add_option("-u","--ucode_patch", dest="ucode_patch", help="The ucode patch file.", type = "str", default = None)
        args_parser.add_option("-r","--reload_addr", dest="reload_addr", help="The reeload_addr(msr 0x124A).", type = "int", default = None)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        if self.args_option.ucode_patch and self.args_option.reload_addr:
            self.ucode_patch_path = os.path.join(self.current_dir_path,self.args_option.ucode_patch)
            self.reload_addr = self.args_option.reload_addr # for example 0xC100
        else:
            self.Error_exit("--ucode_patch and --reload_addr is indispensable")
    def Load_ucode_patch(self):

        self.ucode_path = []
        with open(self.ucode_patch_path,'r') as fu:
            while True:
                line = fu.readline()
                if line:
                    line = line.strip()
                    for i in range(0,32,2):
                        ucode_path = "\tdb 0x%s;"%(line[32-i-2:32-i])
                        self.ucode_path.append(ucode_path)
                else:
                    break
        self.ucode_patch_addr = self.mpg.Apply_mem(0x2000,32,start=0x1000000,end=0xB0000000,name="ucode_patch_addr")
        self.Msr_Write(0x8b,eax=0,edx=0)
        self.simcmd.Add_sim_cmd("at WRMSR 0x0079 set patch size 6832",0)
        self.Msr_Write(0x79,eax=self.ucode_patch_addr["start"],edx=0)
        
    def Ucode_patch_to_file(self):
        self.Comment("##ucode patch")
        self.Text_write("org 0x%x"%(self.ucode_patch_addr["start"]))
        for i in self.ucode_path:
            self.Comment(i)
            
    def Sprc_reset(self,thread):
        pclmsi_spc.Msr_Write(0x1523,thread,eax=0xe174dde8,edx=0xb474bf31)
        pclmsi_spc.Msr_Write(0x1249,thread,eax=0x40,edx=0)
        self.simcmd.Add_sim_cmd("after $y%d >= %d set register RCX to 0x00001203:0x00000000"%(thread,pclmsi_spc.instr_manager.Get_instr(thread)-1),thread)
        # this sim cmd is indispensable, if not cnsim will stop. so 1203 can be change to whatever
##############################################MAIN##########################################
if __name__ == "__main__":
    pclmsi_spc = Pclmsi_spc(sys.argv[1:])
    pclmsi_spc.Create_dir()
    pclmsi_spc.Gen_del_file()
    pclmsi_spc.Reset_asm()
    pclmsi_spc.Create_asm()
    pclmsi_spc.Initial_interrupt()
    pclmsi_spc.Gen_mode_code()
    pclmsi_spc.Sync_threads()
        ################## Thread 0 Code#################
    pclmsi_spc.Text_write("org 0x%x"%(pclmsi_spc.user_code_segs[0]["start"]))
    pclmsi_spc.Tag_write(pclmsi_spc.user_code_segs[0]["name"])
    spin_lock_0 = pclmsi_spc.Spin_lock_create(0)
    spin_lock_1 = pclmsi_spc.Spin_lock_create(0)
    spin_lock_2 = pclmsi_spc.Spin_lock_create(0)
    pclmsi_spc.Sync_spin_lock(spin_lock_0,0)
    pclmsi_spc.Load_ucode_patch()
    pclmsi_spc.Sync_thread(0)
    pclmsi_spc.Sync_spin_lock(spin_lock_1,0)
    pclmsi_spc.Msr_Write(0x124A,eax=pclmsi_spc.reload_addr,edx=0)
    pclmsi_spc.Sync_thread(0)
    pclmsi_spc.Sync_spin_lock(spin_lock_2,0)
    pclmsi_spc.Sprc_reset(0)
    for i in range(0,90):
        pclmsi_spc.Instr_write("pause",0)
    pclmsi_spc.Gen_hlt_code(0)
    pclmsi_spc.Gen_sim_cmd(0)
        ################# Thread 1 Code#################
    pclmsi_spc.Text_write("org 0x%x"%(pclmsi_spc.user_code_segs[1]["start"]))
    pclmsi_spc.Tag_write(pclmsi_spc.user_code_segs[1]["name"])
    pclmsi_spc.Sync_spin_lock(spin_lock_0,1)
    pclmsi_spc.Sync_spin_lock(spin_lock_1,1)
    pclmsi_spc.Sync_spin_lock(spin_lock_2,1)
    pclmsi_spc.Sprc_reset(1)
    for i in range(0,90):
        pclmsi_spc.Instr_write("pause",1)
    pclmsi_spc.Gen_hlt_code(1)
    pclmsi_spc.Gen_sim_cmd(1)
        ################# Thread 2 Code#################
    pclmsi_spc.Text_write("org 0x%x"%(pclmsi_spc.user_code_segs[2]["start"]))
    pclmsi_spc.Tag_write(pclmsi_spc.user_code_segs[2]["name"])
    pclmsi_spc.Sync_spin_lock(spin_lock_0,2)
    pclmsi_spc.Sync_spin_lock(spin_lock_1,2)
    pclmsi_spc.Sync_spin_lock(spin_lock_2,2)
    pclmsi_spc.Sprc_reset(2)
    for i in range(0,90):
        pclmsi_spc.Instr_write("pause",2)
    pclmsi_spc.Gen_hlt_code(2)
    pclmsi_spc.Gen_sim_cmd(2)
        ################# Thread 3 Code#################
    pclmsi_spc.Text_write("org 0x%x"%(pclmsi_spc.user_code_segs[3]["start"]))
    pclmsi_spc.Tag_write(pclmsi_spc.user_code_segs[3]["name"])
    pclmsi_spc.Sync_spin_lock(spin_lock_0,3)
    pclmsi_spc.Sync_spin_lock(spin_lock_1,3)
    pclmsi_spc.Sync_spin_lock(spin_lock_2,3)
    pclmsi_spc.Sprc_reset(3)
    for i in range(0,90):
        pclmsi_spc.Instr_write("pause",3)
    pclmsi_spc.Gen_hlt_code(3)
    pclmsi_spc.Gen_sim_cmd(3)
    ########################################################
    
    pclmsi_spc.Sync_threads()
    pclmsi_spc.Gen_ctrl_cmd()
    pclmsi_spc.Ucode_patch_to_file()
    pclmsi_spc.Gen_file_list()


