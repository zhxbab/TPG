#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test module '
__author__ = 'Ken Zhao'
########################################################
# test module is used to test different function in tpg
########################################################
import sys, os, re
sys.path.append("/%s/../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
from template_tpg import Template_tpg
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Template_tpg(sys.argv[1:])
    tests.Fix_threads(4)
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        tests.Gen_mode_code()
        tests.Sync_threads()
        for j in range(0,4):
            tests.Start_user_code(j)
            if j == 0:
        ################## Thread 0 Code#################
                tests.Msr_Write(0x144f,0,eax=0x0C50C6,edx=0x0)
                tests.Instr_write("mov ecx, 0x0",0)
                tests.Instr_write("mov edx, 0x0",0)
                tests.Instr_write("mov eax, 0x40000000",0) #use 0x40000000 as trigger address
                tests.Instr_write("mov ebx,0x40000020",0) #use 0x40000010 as spin lock address0
                tests.Instr_write("mov [ebx],0xDEADDEAD",0)         
                tests.Instr_write("monitor",0)# mwait must follow monitor, if there is some other instructions, maybe mwait is not able to work well
                tests.Instr_write("mov eax, 0x10", 0)
                tests.Instr_write("mwait")
                #pass
            elif j == 1:
        ################# Thread 1 Code#################
                tests.Tag_write("Spin_lock_0")
                tests.Instr_write("mov eax,[0x40000020]",j)
                tests.Instr_write("cmp eax, 0xDEADDEAD",j)
                tests.Instr_write("jne $Spin_lock_0",j)
                tests.Msr_Write(0x1483,0,eax=0x2f5,edx=0)
                tests.Msr_Write(0x1485,0,eax=0x0,edx=0)
                tests.Msr_Write(0x1481,0,eax=0x32803c0f,edx=0x5d0c)
                base_addr = 0x30000000
                tests.Instr_write("mov eax,50000")
                tests.Tag_write("pause_tag")
                for k in range(0, 1):        
                    for i in range(0,1000):
                        tests.Instr_write("pause",j)
                    tests.Instr_write("dec eax",j)
                    tests.Instr_write("jne $pause_tag")                    
                    tests.Msr_Read(0x1487)
                    tests.Instr_write("mov [%s],ecx"%(base_addr))# use 0x30000000 as MSR printf address
                    tests.Instr_write("mov [%s],eax"%(base_addr+0x4))
                    tests.Instr_write("mov [%s],edx"%(base_addr+0x8))
                    tests.simcmd.Add_sim_cmd("at RDMSR 0x1487 set register ECX to 0x0",1)
                    tests.Msr_Read(0x1489)
                    tests.Instr_write("mov [%s],ecx"%(base_addr+0x10))# use 0x30000000 as MSR printf address
                    tests.Instr_write("mov [%s],eax"%(base_addr+0x14))
                    tests.Instr_write("mov [%s],edx"%(base_addr+0x18))
                    tests.simcmd.Add_sim_cmd("at RDMSR 0x1489 set register ECX to 0x0",1)
                    base_addr = base_addr + 0x20                                      
                tests.Instr_write("mov [0x40000000],0x1")# end core 0 C state
#                 pass                         
            elif j == 2:
        ################# Thread 2 Code#################
                pass
                #tests.Instr_write("mov eax,[0x40000010]",j)
            else:
        ################# Thread 3 Code#################
                pass
                #tests.Instr_write("mov eax,[0x40000010]",j)                 
            tests.Gen_hlt_code(j)
            tests.Gen_sim_cmd(j)
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()


