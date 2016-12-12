#!/usr/bin/env python
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
#    def __init__(self,args):
#        signal.signal(signal.SIGINT,self.Sigint_handler)
#        self.current_dir_path = os.path.abspath(".") # current dir path
#        self.realbin_path = sys.path[0] # realbin path 
#        self.realbin_name = os.path.realpath(sys.argv[0]).split(".")[0].split("/")[-1] # realbin name
#        self.tpg_path = os.getenv("LOCATION_TPG") 
#
#        self.Parse_input(args)
#        self.Set_logging()
#        self.avp_dir_seed = random.randint(1,0xFFFF)
#        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.threads,self.mode,self.avp_dir_seed)
#        self.asm_list = []
#        self.inc_path = "%s/include"%(self.tpg_path)
#        self.bin_path = "%s/bin"%(self.tpg_path)
#        self.mpg = Mem()
#        self.c_parser = ""

    def Create_dir(self):
        self.avp_dir_seed = random.randint(1,0xFFFF)
        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.threads,self.mode,self.avp_dir_seed)
        cmd = "mkdir %s/%s"%(self.realbin_path,self.avp_dir_name)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        self.avp_dir_path = os.path.join(self.realbin_path,self.avp_dir_name)
        #self.cnsim_fail_dir = os.path.join(self.avp_dir_path,"cnsim_fail")
        #self.fail_dir =  os.path.join(self.avp_dir_path,"fail")
        #cmd = "mkdir %s"%(self.cnsim_fail_dir)
        #info("create dir cmd is %s"%(cmd))
        #os.system(cmd)
        #cmd = "mkdir %s"%(self.fail_dir)
        #info("create dir cmd is %s"%(cmd))
        #os.system(cmd)
        self.Create_global_info()

    def Gen_test_list(self):
        cmd = "cp %s %s"%(self.ic_file,self.target_dir)
        info(cmd)
        os.system(cmd)
        cmd = "del.py"
        #info(cmd)
        os.system(cmd)
        os.chdir(self.target_dir)
        ic_file_name = self.ic_file.split("/")[-1]
        new_ic_file_location = "%s/%s"%(self.target_dir,ic_file_name)
        cmd = "%s/avp2json.rb -tc %s"%(os.getenv("LOCATION_AVPPARSER"),new_ic_file_location)
        info(cmd)
        os.system(cmd)
        ic_file_name_main = ic_file_name.split(".")[0]
        ic_json = ic_file_name_main + ".jic"
        ic_json_path = "%s/%s"%(self.target_dir,ic_json)
        info("mv %s/%s.json %s/%s.jic"%(self.target_dir, ic_file_name_main, self.target_dir, ic_file_name_main))
        os.system("mv %s/%s.json %s/%s.jic"%(self.target_dir, ic_file_name_main, self.target_dir, ic_file_name_main))
        #info("gzip %s/%s.jic"%(self.target_dir, ic_file_name_main))
        #os.system("gzip %s/%s.jic"%(self.target_dir, ic_file_name_main))
        ft = open("test_%d.list"%(self.seed),"w")
        new_ic_file_location = "%s/%s"%(self.target_dir,ic_file_name)
        ft.write("+load:%s +Max:700000 +MaxCMP:28000 "%(new_ic_file_location))
        ft.write("+apic:1 +blow_fuse:FCR4_SKIP_MWAIT_ON_DEADLOCK_BIT +cores:%d +maxJ:400000 "%(self.threads))
        ft.write("+opgfile:/haydn/kenzh-h/env/opgen/fast.opgen ")
        ft.write("+ucode_update_block:%s "%(self.ucode_patch_path))
        ft.write("+load_json:%s"%(ic_json_path))
        ft.close()

 #+STPG_VERSION:20160321231915 
     
    def Parse_input(self,args):
        args_parser = OptionParser(usage="%pclmsi_spc *args, **kwargs", version="%pclmsi_spc 0.1")
        args_parser.add_option("-u","--ucode_patch", dest="ucode_patch", help="The ucode patch file.", type = "str", default = None)
        args_parser.add_option("-d","--target_dir", dest="target_dir", help="The target dir.", type = "str", default = None)
        args_parser.add_option("-r","--reload_addr", dest="reload_addr", help="The reload_addr(msr 0x124A).", type = "int", default = None)
        args_parser.add_option("-t","--threads", dest="threads", help="The threads.", type = "int", default = 0x4)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--converse", dest="converse", help="Converse preamble timing",type="int", default = 0x0)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        if self.args_option.ucode_patch and self.args_option.reload_addr:
            self.ucode_patch_path = os.path.join(self.current_dir_path,self.args_option.ucode_patch)
            self.reload_addr = self.args_option.reload_addr # for example 0xC100
        else:
            self.Error_exit("--ucode_patch and --reload_addr is indispensable")
        if self.args_option.target_dir == None:
            self.Error_exit("No Target dir!")
        else:
            self.target_dir = self.args_option.target_dir
        self.c_gen = 0
        self.seed =  self.args_option.converse 
        self.mode = "long_mode"
        self.page_mode = "2MB"
        self.intel = 0
        self.threads = self.args_option.threads
        self.very_short_cmd = "-short"
        self.very_short_num = "100000"
        self.multi_page = 0
        self.disable_avx = 0
        self.disable_pcid = 0
        self.pae = 0
        
    def Load_ucode_patch(self,thread):

        self.ucode_patch = []
        with open(self.ucode_patch_path,'r') as fu:
            while True:
                line = fu.readline()
                if line:
                    line = line.strip()
                    for i in range(0,32,2):
                        ucode_patch = "\tdb 0x%s;"%(line[32-i-2:32-i])
                        self.ucode_patch.append(ucode_patch)
                else:
                    break
        self.ucode_patch_addr = self.mpg.Apply_mem(0x2000,0x1000,start=0x1000000,end=0xB0000000,name="ucode_patch_addr")
        self.Msr_Write(0x8b,thread,eax=0,edx=0)
        ucode_patch_size = len(self.ucode_patch)
        self.simcmd.Add_sim_cmd("at WRMSR 0x0079 set patch size %d"%(ucode_patch_size),0)
        self.Msr_Write(0x79,thread,eax=self.ucode_patch_addr["start"],edx=0)
        
    def Ucode_patch_to_file(self):
        self.Comment("##ucode patch")
        self.Text_write("org 0x%x"%(self.ucode_patch_addr["start"]))
        for i in self.ucode_patch:
            self.Comment(i)
            
    def Sprc_reset(self,thread):
        self.Msr_Write(0x1523,thread,eax=0x9e53492e,edx=0x67fd3795)
        self.Msr_Rmw(0x160f,"s2",thread)
        self.Msr_Rmw(0x1625,"s27",thread)
        self.Msr_Rmw(0x1200,"r56",thread)
        if thread == 0 and self.seed >= 1:
            for i in range(0,1):
                C2M_addr = self.mpg.Apply_mem(0x8,0x40,start=0xC0000000,end=0xD0000000,name="C2M_addr_%d"%(i))
                self.Instr_write("mov qword ptr [0x%x],0xABCDEF"%(C2M_addr["start"]),thread)
                self.Instr_write("mov qword ptr [0x%x+8],0xABCDEF"%(C2M_addr["start"]),thread)
                del C2M_addr
        self.Msr_Write(0x1523,thread,eax=0xe174dde8,edx=0xb474bf31)
        self.Msr_Write(0x1249,thread,eax=0x40,edx=0)
        self.simcmd.Add_sim_cmd("after $y%d >= %d set register RCX to 0x00001203:0x00000000"%(thread,self.instr_manager.Get_instr(thread)-1),thread)
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
    if pclmsi_spc.threads>1:
        pclmsi_spc.Sync_threads()
    else:
        print("instr %d"%(pclmsi_spc.instr_manager.Get_instr(0)))	
    for i in range(0,pclmsi_spc.threads):
    	pclmsi_spc.Text_write("org 0x%x"%(pclmsi_spc.user_code_segs[i]["start"]))
    	pclmsi_spc.Tag_write(pclmsi_spc.user_code_segs[i]["name"])
        if i == 0:
            if pclmsi_spc.threads > 1:
    			spin_lock_0 = pclmsi_spc.Spin_lock_create(i)
    			spin_lock_1 = pclmsi_spc.Spin_lock_create(i,1)
    			spin_lock_2 = pclmsi_spc.Spin_lock_create(i,1)
    			pclmsi_spc.Sync_spin_lock(spin_lock_0,i)
    			pclmsi_spc.Load_ucode_patch(i)
    			pclmsi_spc.Sync_thread(i)
    			pclmsi_spc.Sync_spin_lock(spin_lock_1,i)
    			pclmsi_spc.Msr_Write(0x124A,i,eax=pclmsi_spc.reload_addr,edx=0)
    			pclmsi_spc.Sync_thread(i)
    			pclmsi_spc.Sync_spin_lock(spin_lock_2,i)
            else:
    			pclmsi_spc.Load_ucode_patch(i)
    			pclmsi_spc.Msr_Write(0x124A,i,eax=pclmsi_spc.reload_addr,edx=0)
				
        else:
    		pclmsi_spc.Sync_spin_lock(spin_lock_0,i)
    		pclmsi_spc.Sync_spin_lock(spin_lock_1,i)
    		pclmsi_spc.Sync_spin_lock(spin_lock_2,i)
    	pclmsi_spc.Sprc_reset(i)
        for j in range(0,90):
        	pclmsi_spc.Instr_write("pause",i)
    	pclmsi_spc.Gen_hlt_code(i)
    	pclmsi_spc.Gen_sim_cmd(i)
    
    pclmsi_spc.Sync_threads()
    pclmsi_spc.Gen_ctrl_cmd()
    pclmsi_spc.Ucode_patch_to_file()
    pclmsi_spc.Gen_vector()
    #pclmsi_spc.Gen_pclmsi_file_list()
    pclmsi_spc.Gen_test_list()

