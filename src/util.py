#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' util module '
__author__ = 'Ken Zhao'
########################################################
# util module is used to do somethings which support tpg
########################################################
import sys, os, signal, re
from logging import info, error, debug, warning, critical
#from instruction import Instr 
class Util:
    def __init__(self):
        self.asm_file = ""
        self.instr_manager = ""
    def Sigint_handler(self, signal, frame):
        critical("Ctrl+C pressed and Exit!!!")
        sys.exit(0)
        
    @classmethod
    def Error_exit(cls,cmd):
        error(cmd)
        sys.exit(0)
    
    def Text_write(self,text):
        self.asm_file.write("%s;\n"%(text))
        
    
    def Vars_write(self,name,value):
        self.asm_file.write("$%s = 0x%x;\n"%(name,value))
    
    
    def Comment(self,comment):
        self.asm_file.write("%s\n"%(comment))
        
    
    def Instr_write(self,instr_cmd,thread=0x0):
        self.instr_manager.Add_instr(thread)
        self.asm_file.write("\t%s;\n"%(instr_cmd))
    
    def Tag_write(self,tag):
        self.asm_file.write(":%s\n"%(tag))
        
    def Msr_Read(self,msr,thread=0x0):
        self.Comment("#RDMSR 0x%x")
        self.Instr_write("mov ecx,0x%x"%(msr),thread)
        self.Instr_write("rdmsr",thread)
        #self.Runlog("RDMSR 0x%x"%(msr))
        
    def Msr_Write(self,msr,thread=0x0,**value):
        self.Comment("#WRMSR 0x%x"%(msr))
        self.Instr_write("mov ecx,0x%x"%(msr),thread)
        self.Instr_write("rdmsr",thread)
        if "eax" in value.keys():
            self.Instr_write("mov eax,0x%x"%(value["eax"]),thread)
        if "edx" in value.keys():
            self.Instr_write("mov edx,0x%x"%(value["edx"]),thread)
        self.Instr_write("wrmsr",thread)
        #self.Runlog("WRMSR 0x%x"%(msr))
        
    def Msr_Rmw(self,msr,rmwcmd,thread=0x0):
        self.Comment("#RMWMSR 0x%x %s"%(msr,rmwcmd))
        self.Instr_write("mov ecx,0x%x"%(msr),thread)
        self.Instr_write("rdmsr",thread)
        s_pattern = re.compile('s[0-9]{1,2}')
        r_pattern = re.compile('r[0-9]{1,2}')
        sbits = s_pattern.findall(rmwcmd)
        rbits = r_pattern.findall(rmwcmd)
        for i in sbits:
            num = i[1:]
            if int(num) >= 32:
                self.Instr_write("bts edx,%d"%(int(num)-32),thread)
            else:
                self.Instr_write("bts eax,%d"%(int(num)),thread)
        for i in rbits:
            num = i[1:]
            if int(num) >= 32:
                self.Instr_write("btr edx,%d"%(int(num)-32),thread)
            else:
                self.Instr_write("btr eax,%d"%(int(num)),thread)
        self.Instr_write("wrmsr",thread)
        #self.Runlog("RMWMSR 0x%x %s"%(msr,rmwcmd))
        
#    def Runlog(self,runlog_cmd,thread=0x0):
#        self.asm_file.write("//rem: $y%d %d \"//runlog: Instr %d - %s\"\n"%(thread,self.instr_manager.Get_instr(thread),self.instr_manager.Get_instr(thread),runlog_cmd))


        
    