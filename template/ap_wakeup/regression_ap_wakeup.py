#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test module '
__author__ = 'Ken Zhao'
########################################################
# test module is used to test different function in tpg
########################################################
import sys, os, re, random, time
sys.path.append("/%s/../../src"%(sys.path[0]))
sys.path.append("/%s/../../metasm"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from ap_wakeup import Ap_wakeup
from optparse import OptionParser
from regression import Regression
##############################################CLASSES#######################################
class Regression_ap_wakeup(Ap_wakeup): 
    def __init__(self,args):
        Ap_wakeup.__init__(self,args)
        
    def Parse_input(self,args):
        args_parser = OptionParser(usage="Regression_csmith *args, **kwargs", version="%Regression_csmith 0.1") #2016-04-25 version 0.1
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--dual", dest="dual", help="For dual die", action="store_true", default = False)
        args_parser.add_option("-n","--nums", dest="nums", help="The vector nums."\
                          , type = "int", default = 10000)
        args_parser.add_option("-d","--device", dest="device", help="Set device num. But if run with balancer, the device num will be changed by balancer.", type="int", default = None)
        args_parser.add_option("--arch", dest="arch", help="Set architecture, for tune clk and feature list", type="str", default = "default_arch")
        args_parser.add_option("--bustool", dest="bustool", help="For support bustool", action="store_true", default = False)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        self.seed = str(time.time())
        self.seed = int(self.seed.replace(".","0"))
        if self.args_option.device == None:
            self.Error_exit("You must set a device num!")
        else:
            self.device = self.args_option.device
        self.c_gen = 0
        self.vector_nums = self.args_option.nums
        self.very_short_cmd = "-very-short"
        self.very_short_num = "50000000"
        self.arch = self.args_option.arch
        self.bustool = self.args_option.bustool
        self.regression = Regression(self.device,self.arch,self.bustool)
        self.regression.rerun_times = 10
        self.elf_file = None
        self.disable_avx = 0
        self.disable_pcid = 0
        self.intel = 0 
        self.dual = self.args_option.dual      
        self.multi_page = 0
        
    def Regression_vector(self):
        time = 300
        self.reglog_name = "/tmp/%s"%(self.avp_dir_name)
        self.regression.freglog = open(self.reglog_name,"w")
        info("Log is %s"%(self.reglog_name))
        self.regression.Set_remove_flag()
        self.regression.Handle_vecor(self.ic_file,time)
        self.regression.freglog.close()
        
    def Set_fail_dir(self):
        if os.getenv("LOCATION_CVREG_VECTOR") == None:
            error("Not env para LOCATION_CVREG_VECTOR")
            sys.exit(0)
            
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Regression_ap_wakeup(sys.argv[1:])
    mode = ["long_mode","protect_mode","compatibility_mode"][random.randint(0,2)]   
    if mode == "protect_mode":
        tests.pae = [True,False][random.randint(0,1)]
    else:
        tests.pae = False
    tests.Set_total_threads(8)
    tests.Fix_threads(5)
    tests.Set_mode(mode,8)  
    tests.Create_dir()
    tests.Check_fail_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Use_random_ap()
        tests.Create_asm(i)
        tests.Ap_wake_up_code()
        tests.Initial_interrupt()
        tests.Initial_metasm(i,tests.mode)
        spin_lock_0 = tests.Spin_lock_create(0)
        tests.Gen_mode_code()
        tests.Check_instr_num_all(tests.apic_id_list_all)
        tests.Sync_threads(tests.apic_id_list_all)
        for j in tests.apic_id_list_all:
            tests.Start_user_code(j)
#            tests.Print_instructions(j,10000)
#            tests.instr_manager.Add_instr(j,10000)
            if j == 0:
                tests.Sync_spin_lock(spin_lock_0,j)
#                tests.Instr_write("mov edx,3000",j)
#                tests.Tag_write("nop_loop_0")
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("dec edx",j)
#                tests.Instr_write("jnz $nop_loop_0",j) 
                tests.Sync_thread(j)
                tests.Instr_write("mov eax,0xfee00310",j)
                tests.Instr_write("mov dword [eax],0x00000000")
                tests.Instr_write("mov eax,0xfee00300",j)
                tests.Instr_write("mov dword [eax],0xc0500",j)
                tests.Print_instructions(j,1000)
#                for apic_id in tests.mode_code.apic_id_list:
#                    tests.Instr_write("mov eax,0xfee00310",j)
#                    tests.Instr_write("mov dword [eax],0x%08x"%(apic_id<<24),j)
#                    tests.Instr_write("mov eax,0xfee00300",j)
#                    tests.Instr_write("mov dword [eax],0x00500",j)
#                tests.Instr_write("mov edx,3000",j)
#                tests.Tag_write("nop_loop_1")
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("nop",j)
#                tests.Instr_write("dec edx",j)
#                tests.Instr_write("jnz $nop_loop_1",j)                                        
                for apic_id in tests.mode_code.apic_id_list:
                    tests.Instr_write("mov eax,0xfee00310",j)
                    tests.Instr_write("mov dword [eax],0x%08x"%(apic_id<<24),j)
                    tests.Instr_write("mov eax,0xfee00300",j)
                    tests.Instr_write("mov dword [eax],0x006%02x"%(tests.apic_jmp_addr_loop["start"]/0x1000),j)
        ################## Thread 0 Code#################
            else:
                tests.Sync_spin_lock(spin_lock_0,j)
                tests.Instr_write("hlt",j)
                tests.Sync_thread(j)
        ################# Thread 3 Code#################         
            tests.Gen_hlt_code(j)
            tests.Gen_sim_cmd(j)
        tests.Check_instr_num_all(tests.apic_id_list_all)
        tests.Sync_threads(tests.apic_id_list_all)
        tests.Gen_ctrl_cmd()
        tests.Gen_vector()
        if os.path.exists(tests.ic_file):
            tests.Regression_vector()
    tests.Remove_dir()


