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
        
    
    def Instr_write(self,instr_cmd):
        self.instr_manager.Add_instr()
        self.asm_file.write("\t%s; #Instr:%d\n"%(instr_cmd,self.instr_manager.Get_instr()))
    
    def Tag_write(self,tag):
        self.asm_file.write(":%s\n"%(tag))
        
    def Msr_Read(self,msr):
        self.Instr_write("mov ecx,0x%x"%(msr))
        self.Instr_write("rdmsr")
    
    def Msr_Write(self,msr,**value):
        self.Instr_write("mov ecx,0x%x"%(msr))
        self.Instr_write("rdmsr")
        if "eax" in value.keys():
            self.Instr_write("mov eax,0x%x"%(value["eax"]))
        if "edx" in value.keys():
            self.Instr_write("mov edx,0x%x"%(value["edx"]))
        self.Instr_write("wrmsr")
        
    def Msr_Rmw(self,msr,rmwcmd):
        self.Instr_write("mov ecx,0x%x"%(msr))
        self.Instr_write("rdmsr")
        s_pattern = re.compile('s[0-9]{1,2}')
        r_pattern = re.compile('r[0-9]{1,2}')
        sbits = s_pattern.findall(rmwcmd)
        rbits = r_pattern.findall(rmwcmd)
        for i in sbits:
            num = i[1:]
            if int(num) >= 32:
                self.Instr_write("bts edx,%d"%(int(num)-32))
            else:
                self.Instr_write("bts eax,%d"%(int(num)))
        for i in rbits:
            num = i[1:]
            if int(num) >= 32:
                self.Instr_write("btr edx,%d"%(int(num)-32))
            else:
                self.Instr_write("btr eax,%d"%(int(num)))
        self.Instr_write("wrmsr")

    

        
    