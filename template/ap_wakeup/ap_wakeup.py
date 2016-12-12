#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test module '
__author__ = 'Ken Zhao'
########################################################
# test module is used to test different function in tpg
########################################################
import sys, os, re
sys.path.append("/%s/../../src"%(sys.path[0]))
sys.path.append("/%s/../../metasm"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from metasm import Metasm
##############################################CLASSES#######################################
class Ap_wakeup(Metasm): 
    def __init__(self,args):
        Metasm.__init__(self,args)
        
    def Gen_cnsim_param(self):
        if self.intel:
            intel_cnsim_cmd = "-apic-id-increment 2 "
        else:
            intel_cnsim_cmd = " "
        cnsim_param_pclmsi = " "
        cnsim_param_normal = "-ma %s  -va -no-mask-page -trait-change %s -hlts 10 "%(self.very_short_num,self.very_short_cmd)
        cnsim_param_mem = "-mem 0xF4 "
        if self.total_threads != self.threads and self.threads_flag == "random":
            cnsim_param_thread = "-threads %d "%(self.total_threads)
        else:
            cnsim_param_thread = "-threads %d "%(self.threads)            
        #-no-tbdm-warnings
        # remove no stack, -no-apic-intr -all-mem -addr-chk -memread-chk 
        self.cnsim_param = cnsim_param_pclmsi + cnsim_param_normal + cnsim_param_mem + cnsim_param_thread + intel_cnsim_cmd
        
    def Ap_wake_up_code(self):
        self.Comment("##########Loop AP init address and code###############")
        self.apic_jmp_addr_loop = self.mpg.Apply_mem(0x100,0x1000,start=0x1000,end=0xA0000,name="apic_jmp_addr_loop") # used for apic jmp
        self.osystem.set_org(self.apic_jmp_addr_loop["start"])
        self.Text_write("use 16")
        for k in range(0,10):
            self.Instr_write("mov ax,0x88")
        self.Instr_write("hlt")
        
    def Spin_lock_create(self,thread,flag=0):
      spin_lock = self.mpg.Apply_mem(0x4,0x4,start=0x90000000,end=0xB0000000,name="spin_lock")
      self.osystem.set_org(spin_lock["start"])
      self.Text_write("dd 0x0")
      spin_lock["num"] = self.spin_lock_num
      spin_lock["ctrl_id"] = [0]*8
      self.spin_lock_num += 1
      return spin_lock
  
    def Sync_spin_lock(self,spin_lock,thread,unlock_thread=0x0):
      #self.simcmd.Add_sim_cmd("at $y%d >= %d disable intermediate checking"%(thread,self.instr_manager.Get_instr(thread)+1),thread)
      self.Text_write("db 0xF0")
      self.Instr_write("inc dword [0x%08x]"%(spin_lock["start"]),thread)
      self.Tag_write("spin_lock_T%d_%d"%(thread,spin_lock["num"]))
      self.Instr_write("cmp dword [0x%08x],0x%x"%(spin_lock["start"],self.threads),thread)
      if unlock_thread == thread:
          #self.simcmd.Add_sim_cmd("at $y%d >= %d set memory 0x%08x to 0x00000004"%(thread,self.instr_manager.Get_instr(thread),spin_lock["start"]),thread)
          for i in self.apic_id_list_all:
              if i != unlock_thread:
                  spin_lock["ctrl_id"][i] = self.Sync_thread(i)
              else:
                  pass
      else:
          instr_num = self.instr_manager.Get_instr(thread)-self.simcmd.current_instr[thread]
          self.simcmd.Change_ctrl_cmd(spin_lock["ctrl_id"][thread],instr_num)
          self.simcmd.current_instr[thread] = self.instr_manager.Get_instr(thread)
          self.instr_manager.Set_instr(self.instr_manager.Get_instr(thread)+2,thread) # +2 is for core 1, 2, 3 to sync instr num
      self.Instr_write("jne $spin_lock_T%d_%d"%(thread,spin_lock["num"]),thread)
      #self.simcmd.Add_sim_cmd("at $y%d >= %d enable intermediate checking"%(thread,self.instr_manager.Get_instr(thread)+1),thread)
            
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Ap_wakeup(sys.argv[1:])
    tests.Set_total_threads(8)
    tests.Fix_threads(4)
    tests.Create_dir()
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
            tests.Print_instructions(j,10000)
            tests.instr_manager.Add_instr(j,10000)
            if j == 0:
                pass
                tests.Sync_spin_lock(spin_lock_0,j)
                tests.Instr_write("mov edx,3000",j)
                tests.Tag_write("nop_loop_0")
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("dec edx",j)
                tests.Instr_write("jnz $nop_loop_0",j) 
                tests.Sync_thread(j)
                for apic_id in tests.mode_code.apic_id_list:
                    tests.Instr_write("mov eax,0xfee00310")
                    tests.Instr_write("mov dword [eax],0x%08x"%(apic_id<<24))
                    tests.Instr_write("mov eax,0xfee00300")
                    tests.Instr_write("mov dword [eax],0x00500")
                tests.Instr_write("mov edx,3000",j)
                tests.Tag_write("nop_loop_1")
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("nop",j)
                tests.Instr_write("dec edx",j)
                tests.Instr_write("jnz $nop_loop_1",j)                                        
                for apic_id in tests.mode_code.apic_id_list:
                    tests.Instr_write("mov eax,0xfee00310")
                    tests.Instr_write("mov dword [eax],0x%08x"%(apic_id<<24))
                    tests.Instr_write("mov eax,0xfee00300")
                    tests.Instr_write("mov dword [eax],0x006%02x"%(tests.apic_jmp_addr_loop["start"]/0x1000))
        ################## Thread 0 Code#################
            else:
                pass
                tests.Sync_spin_lock(spin_lock_0,j)
                tests.Instr_write("hlt",j)
                tests.Sync_thread(j)
        ################# Thread 3 Code#################
                pass                 
            tests.Gen_hlt_code(j)
            tests.Gen_sim_cmd(j)
        tests.Check_instr_num_all(tests.apic_id_list_all)
        tests.Sync_threads(tests.apic_id_list_all)
        tests.Gen_ctrl_cmd()
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()


