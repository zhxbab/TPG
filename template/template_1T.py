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
from template_tpg import Template_tpg
##############################################MAIN##########################################
if __name__ == "__main__":
    tests = Template_tpg(sys.argv[1:])
    tests.Fix_threads(1)
    tests.Create_dir()
    tests.Gen_del_file()
    for i in range(0,tests.args_option.nums):
        tests.Reset_asm()
        tests.Create_asm(i)
        tests.Initial_interrupt()
        pmc0_addr = tests.mpg.Apply_fix_mem("pmc0_addr",0x80000000,0x20)
        mov_code_addr = tests.mpg.Apply_fix_mem("mov_code_addr",0x40000000,0x10000000)
        mem_address_addr = tests.mpg.Apply_fix_mem("mem_address_addr",0x30000000,0x10000000)
        tests.Gen_mode_code()
        tests.Start_user_code(0)
        tests.Init_PMC(0)
#        tests.Enable_PMC0(0)
#        tests.Read_PMC0("0x%x"%(pmc0_addr["start"]),0)
#        tests.Instr_write("call %s"%(mov_code_addr["start"]),0)
#        tests.Text_write("org 0x%x"%(mov_code_addr["start"]))
#        for i in range(0,1000):
#            tests.Instr_write("movdqa xmm1, [%s]"%(mem_address_addr["start"]+i*16),0)
#            tests.Instr_write("movdqa [%s], xmm2"%(mem_address_addr["start"]+i*16),0)
#        tests.Read_PMC0("0x%x"%(pmc0_addr["start"]+0x8),0)
#        tests.Report_PMC(pmc0_addr,0)
        tests.Gen_hlt_code(0)
        tests.Gen_sim_cmd(0)
        tests.Gen_vector()
    tests.Gen_pclmsi_file_list()

