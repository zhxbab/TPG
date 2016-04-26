#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' util module '
__author__ = 'Ken Zhao'
########################################################
# util module is used to do somethings which support tpg
########################################################
import sys, os, signal
from logging import info, error, debug, warning, critical
#from instruction import Instr 
class Util:
    def __init__(self):
        pass
    def Sigint_handler(self, signal, frame):
        critical("Ctrl+C pressed and Exit!!!")
        sys.exit(0)
    @classmethod
    def Error_exit(cls,cmd):
        error(cmd)
        sys.exit(0)
    @classmethod
    def Text_write(cls,file,text):
        file.write("%s;\n"%(text))
        
    @classmethod
    def Vars_write(cls,file,name,value):
        file.write("$%s = 0x%x;\n"%(name,value))
    
    @classmethod
    def Comment(cls,file,comment):
        file.write("%s\n"%(comment))
        
    @classmethod
    def Instr_write(cls,file,instr_cmd, instr_manager):
        instr_manager.Add_instr()
        file.write("%s; #Instr:0x%x\n"%(instr_cmd,instr_manager.Get_instr()))

        
    