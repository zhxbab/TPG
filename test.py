#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test module '
__author__ = 'Ken Zhao'
########################################################
# test module is used to test different function in tpg
########################################################
import sys, os, re
sys.path.append("%s/src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from test_generator import Test_generator
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Test_generator(sys.argv[1:])
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        if tests.c_gen:
            tests.Gen_asm_code(4,i)
        else:
            pass
        ######################### If you want to change default interrupt handler##################
#        interrupt_index = 6
#        interrupt_handler = \
#        tests.Pretty_instr("mov eax,0x1") + \
#        tests.Pretty_instr("mov ebx,0x2")
#        tests.Updata_interrupt(interrupt_index,interrupt_handler)
        ###########################################################################################
        tests.Gen_mode_code()
        if tests.threads == 0x4:
        ################## Thread 0 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[0]["start"]))
            tests.Tag_write(tests.user_code_segs[0]["name"])
            tests.Instr_write("mov eax,0x0")
            tests.Gen_hlt_code(0)
            tests.Gen_sim_cmd(0)
        ################# Thread 1 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[1]["start"]))
            tests.Tag_write(tests.user_code_segs[1]["name"])
            tests.Instr_write("mov eax,0x1",1)
            tests.Gen_hlt_code(1)
            tests.Gen_sim_cmd(1)
        ################# Thread 2 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[2]["start"]))
            tests.Tag_write(tests.user_code_segs[2]["name"])
            tests.Instr_write("mov eax,0x2",2)
            tests.Gen_hlt_code(2)
            tests.Gen_sim_cmd(2)
        ################# Thread 3 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[3]["start"]))
            tests.Tag_write(tests.user_code_segs[3]["name"])
            tests.Instr_write("mov eax,0x3",3)
            tests.Gen_hlt_code(3)
            tests.Gen_sim_cmd(3)
        elif tests.threads == 0x3:
        ################## Thread 0 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[0]["start"]))
            tests.Tag_write(tests.user_code_segs[0]["name"])
            tests.Instr_write("mov eax,0x0")
            tests.Gen_hlt_code(0)
        ################# Thread 1 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[1]["start"]))
            tests.Tag_write(tests.user_code_segs[1]["name"])
            tests.Instr_write("mov eax,0x1",1)
            tests.Gen_hlt_code(1)
        ################# Thread 2 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[2]["start"]))
            tests.Tag_write(tests.user_code_segs[2]["name"])
            tests.Instr_write("mov eax,0x2",2)
            tests.Gen_hlt_code(2)
        elif tests.threads == 0x2:
        ################## Thread 0 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[0]["start"]))
            tests.Tag_write(tests.user_code_segs[0]["name"])
            tests.Instr_write("mov eax,0x0")
            tests.Gen_hlt_code(0)
        ################# Thread 1 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[1]["start"]))
            tests.Tag_write(tests.user_code_segs[1]["name"])
            tests.Instr_write("mov eax,0x1",1)
            tests.Gen_hlt_code(1)
        elif tests.threads == 0x1:
        ################## Thread 0 Code#################
            tests.Text_write("org 0x%x"%(tests.user_code_segs[0]["start"]))
            tests.Tag_write(tests.user_code_segs[0]["name"])
            if tests.c_gen:
                tests.Load_asm_code(0,i)
            else:
                tests.Instr_write("mov eax,0x1",0)

            tests.Gen_hlt_code(0)
        else:
            tests.Error_exit("Invalid threads num!")
        #info(tests.instr_manager.Get_instr(2))
    tests.Gen_file_list()
        #info(tests.instr_manager.Get_instr())
        #tests.Msr_Rmw(0x80,"s8r16s0s3r56s63")

