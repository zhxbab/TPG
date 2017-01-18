#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' interrupt module '
__author__ = 'Ken Zhao'
########################################################
# interrupt module is used to manage interrupt handler
########################################################
from util import Util
class Interrupt(Util):
    def __init__(self,mode,mpg):
        self.mpg = mpg
        self.mode = mode
        self.interrupt_handler = []
        for i in range(0,256):
            self.interrupt_handler.append({"index":i})
            
    def Update_interrupt_handler(self,index ,handler):
        self.interrupt_handler[index]["block"] = handler
    
    def Write_interrupt(self):
        self.Comment("###########################INT Handler######################")
        for i in range(0,256):
            self.asm_file.write(self.interrupt_handler[i]["constant"])
            self.asm_file.write(self.interrupt_handler[i]["block"])

    
    def Get_interrupt_handler(self,index):
        return self.interrupt_handler[index]
        
    def Initial_interrupt_handler(self,int_handler_base,int_handler_record_base):
        if self.mode == "protect_mode":
            use_mode = "use 32"
            iret = "iretd"
        else:
            use_mode = "use 64"
            iret = "iretq"
        for i in range(0,256):
            if i == 0x80:
                self.interrupt_handler[i]["constant"] = \
                self.Pretty_instr("org 0x%x"%(int_handler_base["start"]+i*int_handler_base["size"]/256)) + \
                self.Pretty_Tag("int%d_handler"%(i)) + \
                self.Pretty_instr("%s"%(use_mode))
                self.interrupt_handler[i]["block"] = \
                self.Pretty_instr("cmp eax,0xf3") + \
                self.Pretty_instr("je $int80_0xf3") + \
                self.Pretty_instr("%s"%(iret)) + \
                self.Pretty_instr("int80_0xf3:") + \
                self.Pretty_instr("mov eax,0x0") + \
                self.Pretty_instr("%s"%(iret))                
            else:
                self.interrupt_handler[i]["constant"] = \
                self.Pretty_instr("org 0x%x"%(int_handler_base["start"]+i*int_handler_base["size"]/256)) + \
                self.Pretty_Tag("int%d_handler"%(i)) + \
                self.Pretty_instr("%s"%(use_mode))
                self.interrupt_handler[i]["block"] = \
                self.Pretty_instr("mov ax,0x%x"%(i)) + \
                self.Pretty_instr("out 0x80,ax") + \
                self.Pretty_instr("mov ebx,[0x%08x]"%(int_handler_record_base["start"]+int_handler_record_base["size"]/256*i)) + \
                self.Pretty_instr("inc ebx") + \
                self.Pretty_instr("mov [0x%08x],ebx"%(int_handler_record_base["start"]+int_handler_record_base["size"]/256*i)) + \
                self.Pretty_instr("%s"%(iret))
            
