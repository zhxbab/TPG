#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test_generator module '
__author__ = 'Ken Zhao'
##########################################################
# test_generator module is used to merge differnet classes
# and generate the test vectors
##########################################################
import sys, os, signal, random, subprocess
from logging import info, error, debug, warning, critical
from args import Args
from util import Util
from mem import Mem
from mode import Mode
from instruction import Instr
from page import Page
from simcmd import Simcmd
class Test_generator(Args,Util):
    def __init__(self,args):
        signal.signal(signal.SIGINT,self.Sigint_handler)
        Args.__init__(self,args)
        self.avp_dir_seed = random.randint(1,0xFFFF)
        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.args_option.thread_nums,self.mode,self.avp_dir_seed)
        self.asm_list = []
        self.inc_path = "%s/include"%(self.tpg_path)
        self.bin_path = "%s/bin"%(self.tpg_path)
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
        self.asm_list.append(self.asm_path)
        self.ptg.asm_file = self.asm_file
        self.mpg.asm_file = self.asm_file
        self.simcmd.asm_file = self.asm_file
        self.Text_write("include \"%s/std.inc\""%(self.inc_path))

        
    def Gen_mode_code(self):
        self.mode_code = Mode(self.mpg, self.instr_manager, self.ptg, self.threads, self.simcmd, self.intel)
        self.mode_code.asm_file = self.asm_file
        if(self.mode,"long_mode"):
            [self.stack_segs,self.user_code_segs] = self.mode_code.Long_mode()
        elif(self.mode,"protect_mode"):
            pass
        elif(self.mode, "compatibility_mode"):
            pass
        else:
            self.Error_exit("Invalid mode!")

    def Gen_hlt_code(self,thread_num):
        #self.mpg.check_spare_mem()
        if thread_num == 0:
            self.hlt_code = self.mpg.Apply_mem(0x200,16,start=0x0,end=0xA0000,name="hlt_code")
            self.Instr_write("jmp $%s"%(self.hlt_code["name"]))
            self.Text_write("org 0x%x"%(self.hlt_code["start"]))
            self.Tag_write(self.hlt_code["name"])
            self.Instr_write("hlt")
        elif 0 < thread_num < 4:
            self.Instr_write("jmp $%s"%(self.hlt_code["name"]))
        else:
            self.Error_exit("Invalid thread num!")
    def Gen_sim_cmd(self,thread_num):
        self.simcmd.Simcmd_write(thread_num)
        
    def Reset_asm(self):
        self.mpg = Mem()
        self.instr_manager = Instr(self.threads)
        self.ptg = Page(self.page_mode,self.tpg_path,self.mpg,self.instr_manager)
        self.simcmd = Simcmd(self.threads)
        
    def Gen_del_file(self):
        self.del_file_name = "%s.del"%(self.avp_dir_path)
        self.del_file = open(self.del_file_name,"w")
        self.del_file.write("rm -rf %s\n"%(self.avp_dir_path))
        self.del_file.close()
        os.system("chmod 777 %s"%(self.del_file_name))
    
    def Gen_file_list(self):
        self.asm_file.close()
        if self.intel:
            intel_cnsim_cmd = "-apic-id-increment 2"
        else:
            intel_cnsim_cmd = ""
        ic_list = []
        os.chdir(self.avp_dir_path)
        self.pclmsi_list_file = "%s/%s_pclmsi.list"%(self.avp_dir_path,self.avp_dir_name)
        pclmsi_list = open(self.pclmsi_list_file,"w")
        cnsim_path = os.getenv("LOCATION_TPG")
        for asm_file in self.asm_list:
            rasm_cmd = "%s/rasm -raw %s"%(self.bin_path,asm_file)
            avp_file = asm_file.replace("asm","avp")
            rasm_p = subprocess.Popen(rasm_cmd,stdout=None, stderr=None, shell=True)
            ret = rasm_p.poll()
            while ret == None:
                ret = rasm_p.poll()
            cnsim_cmd = "%s/cnsim -mem 0xF4 -short %s -threads %d %s"%(self.bin_path,intel_cnsim_cmd,self.threads,avp_file)             
            info(cnsim_cmd)
            cnsim_p = subprocess.Popen(cnsim_cmd,stdout=None, stderr=None, shell=True)
            ret = cnsim_p.poll()
            while ret == None:
                ret = cnsim_p.poll()
            ic_file = avp_file.replace("avp","ic")
            gzip_cmd = "gzip %s"%(ic_file)
            info(gzip_cmd)
            os.system(gzip_cmd)
            ic_list.append("%s.gz"%(ic_file))
        for ic_file in ic_list:
            pclmsi_list.write("+load:%s +rerun_times:100 +ignore_all_checks:1\n"%(ic_file))
        info("%s Done"%(self.pclmsi_list_file))
        pclmsi_list.close()