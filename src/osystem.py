#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' os module '
__author__ = 'Ken Zhao'
########################################################
# mode module is used to generate different mode code
########################################################
from operator import eq, ne
from util import Util
from logging import info, error, debug, warning, critical
import re, sys, os
class Osystem(Util):
    def __init__(self,threads,instr_manager):
        self.threads = threads
        self.control_regs = {"cr0_l":[0x60000010]*self.threads,\
                             "cr0_h":[0x00000000]*self.threads,\
                             "cr3_l":[0x00000000]*self.threads,\
                             "cr3_h":[0x00000000]*self.threads,\
                             "cr4_l":[0x00000000]*self.threads,\
                             "cr4_h":[0x00000000]*self.threads,\
                             }
        self.seg_selector = {"cs":[0x0000]*self.threads,\
                             "ds":[0x0000]*self.threads,\
                             "ss":[0x0000]*self.threads,\
                             "es":[0x0000]*self.threads,\
                             "fs":[0x0000]*self.threads,\
                             "gs":[0x0000]*self.threads,\
                             }
        self.gdt = [{"value_h":0x0,"value_l":0x0},]*self.threads
        self.os_name = ["real_mode","protect_mode","ia32e_mode"]
        self.page_mode_name = ["no_page","en_page"]
        self.current_mode = 0
        self.current_page_mode = 0
        self.instr_manager = instr_manager
        self.pae = 0
        self.pse = 0
        self.msr_table = {"IA32_EFER":{"index":0xc0000080,"value_l":[0x00000000]*self.threads,"value_h":[0x00000000]*self.threads},\
                          }
        
    def reset_osystem(self):
        sefl.__init(self.threads)
        
    def add_gdt_entry(self,index,**gdt_value):
        pass
#                  15..0  limit = 0xfffff;
#  39..16 base  = 0x0;
#  43..40 type = 0x0;
#  44..44 s    = 0x1;
#  46..45 dpl  = 0x0;
#  47..47 p    = 0x1;
#  51..48 limit(19..16);
#  52 avl;
#  53 l;
#  54 db = 0;
#  55 g = 1;
#  63..56 base(31..24) = 0;
  
    def update_msr_table(self,key_name,value_l,value_h,thread=0):
        if self.msr_table.has_key(key_name):
            self.msr_table[key_name]["value_l"][thread] = value_l
            self.msr_table[key_name]["value_h"][thread] = value_h
        else:
            error("Msr %s isn't in msr table"%(key_name))
      
    def get_msr_table(self,key_name,thread=0):
        if self.msr_table.has_key(key_name):
            value_l = self.msr_table[key_name]["value_l"][thread] 
            value_h = self.msr_table[key_name]["value_h"][thread]
            return [value_h, value_l]
        else:
            error("Msr %s isn't in msr table"%(key_name))
    
    def Msr_Write(self,msr_name,value_l,value_h,flag=0x0,thread=0x0):
        if flag == "all":
            for i in range(0,self.threads):
                self.update_msr_table(msr_name,value_l,value_h,i)
        else:
            self.update_msr_table(msr_name,value_l,value_h,thread)
        cmd = {"eax":value_l,"edx":value_h}
        Util.Msr_Write(self,self.msr_table[msr_name]["index"],thread,**cmd)
        self.Comment("######Msr %s index is 0x%x, eax=0x%x, edx=0x%x#####"%(msr_name,self.msr_table[msr_name]["index"],\
                                                                            self.msr_table[msr_name]["value_l"][thread],\
                                                                            self.msr_table[msr_name]["value_h"][thread],\
                                                                            ))          
    
    def update_control_reg(self,reg,value,thread=0):
        if self.control_regs.has_key(reg):
            self.control_regs[reg][thread] = value
        else:
            error("%s isn't in control regs"%(reg))
            
    def get_control_reg(self,reg,thread=0):
        if self.control_regs.has_key(reg):
            value = self.control_regs[reg][thread]
            return value
        else:
            error("%s isn't in control regs"%(reg))    
            
    def check_current_mode(self,thread=0):
        #0:real mode
        #1:protect_mode
        #2:ia32e mode
        cr0_l = self.get_control_reg("cr0_l",thread)
        
        if(cr0_l & 0x00000001):
            self.current_mode = 1
        else:
            self.current_mode = 0
            
    def check_current_page_mode(self,thread=0):
        #0:no-page mode
        #1:page_mode
        cr0_l = self.get_control_reg("cr0_l",thread)
        
        if(cr0_l & 0x10000000):
            self.current_page_mode = 1
        else:
            self.current_page_mode = 0
        
        current_mode = self.check_current_mode(thread)
        if current_mode == 0:
            self.Error_exit("real mode don't support page")
        elif current_mode == 1:
            cr4_l = self.get_control_reg("cr4_l",thread)
            if(cr4_l & 0x10):
                self.pse = 1
            else:
                self.pse = 0
            if(cr4_l & 0x20):
                self.pae = 1
            else:
                self.pae = 0
        
    def set_org(self,org_add,thread=0):
        current_mode = self.check_current_mode(thread)
        if current_mode == 0:
            org_add = org_add
        else:
            current_page_mode = self.check_current_page_mode(thread)
            if current_page_mode:
                pass
            else:
                org_add = org_add                
        text = "org 0x%x"%(org_add)
        self.Comment("####os mode: %s && page mode: %s####"%(self.os_name[self.current_mode],self.page_mode_name[self.current_page_mode]))
        self.Text_write(text)
        
    def cr_read(self,cr,thread=0x0):
        self.Comment("#Read reg %s"%(cr))
        current_mode = self.check_current_mode(thread)
        if current_mode == 2:
            self.Instr_write("mov rbx,%s"%(cr),thread)
        else:
            self.Instr_write("mov ebx,%s"%(cr),thread)            
        #self.Runlog("RDMSR 0x%x"%(msr))
        
    def cr_write(self,cr,value,flag=0x0, thread=0x0):
        self.Comment("#Write reg %s 0x%x"%(cr,value))
        current_mode = self.check_current_mode(thread)
        if current_mode == 2:
            self.Instr_write("mov rbx, 0x%x"%(value),thread)
            self.Instr_write("mov %s,rbx"%(cr),thread)
            if value <= 0xFFFFFFFF:
                ori_value_h = 0x0
                ori_value_l = value
            else:
                ori_value_l = value & 0xFFFFFFFF
                ori_value_h = (value >> 32) & 0xFFFFFFFF
            if flag == "all":
                for i in range(0,self.threads):
                    self.update_control_reg(cr+"_l",ori_value_l,thread)
                    self.update_control_reg(cr+"_h",ori_value_h,thread)
            else:
                self.update_control_reg(cr+"_l",ori_value_l,thread)
                self.update_control_reg(cr+"_h",ori_value_h,thread)
            self.Comment("####%s_l is 0x%x####"%(cr,self.get_control_reg(cr+"_l", thread)))
            self.Comment("####%s_h is 0x%x####"%(cr,self.get_control_reg(cr+"_h", thread)))                        
        else:
            self.Instr_write("mov ebx, 0x%x"%(value),thread)
            self.Instr_write("mov %s,ebx"%(cr),thread)
            new_cr = cr + "_l"
            if flag == "all":
                for i in range(0,self.threads):
                    self.update_control_reg(new_cr, value, i)
            else:
                self.update_control_reg(new_cr, value, thread)  
            self.Comment("####%s_l is 0x%x####"%(cr,self.get_control_reg(cr+"_l", thread)))
              
    def cr_rmw(self,cr,cmd,flag=0x0,thread=0x0):
        self.Comment("#Rmw reg %s %s"%(cr,cmd))
        current_mode = self.check_current_mode(thread)
        if current_mode == 2:
            ori_value_l = self.get_control_reg(cr+"_l", thread)
            ori_value_h = self.get_control_reg(cr+"_h", thread)
            self.Instr_write("mov rbx,%s"%(cr),thread)
            s_pattern = re.compile('s[0-9]{1,2}')
            r_pattern = re.compile('r[0-9]{1,2}')
            sbits = s_pattern.findall(cmd)
            rbits = r_pattern.findall(cmd)
            for i in sbits:
                num = i[1:]
                self.Instr_write("bts rbx,%d"%(int(num)),thread)
                if int(num) > 32:
                    ori_value_h = ori_value_h | (0x1<<int(num))
                else:
                    ori_value_l = ori_value_l | (0x1<<int(num))
            for i in rbits:
                num = i[1:]
                self.Instr_write("btr rbx,%d"%(int(num)),thread)
                if int(num) > 32:
                    ori_value_h = ori_value_h & (~(0x1<<int(num)))
                else:
                    ori_value_l = ori_value_l & (~(0x1<<int(num)))
            self.Instr_write("mov %s, rbx"%(cr),thread)
            if flag == "all":
                for i in range(0,self.threads):
                    self.update_control_reg(cr+"_l", ori_value_l, thread)
                    self.update_control_reg(cr+"_h", ori_value_h, thread)  
            else:  
                self.update_control_reg(cr+"_l", ori_value_l, thread)
                self.update_control_reg(cr+"_h", ori_value_h, thread)
            self.Comment("####%s_l is 0x%x####"%(cr,self.get_control_reg(cr+"_l", thread)))
            self.Comment("####%s_h is 0x%x####"%(cr,self.get_control_reg(cr+"_h", thread)))
        else:
            new_cr = cr + "_l"
            ori_value = self.get_control_reg(new_cr, thread)
            self.Instr_write("mov ebx,%s"%(cr),thread)
            s_pattern = re.compile('s[0-9]{1,2}')
            r_pattern = re.compile('r[0-9]{1,2}')
            sbits = s_pattern.findall(cmd)
            rbits = r_pattern.findall(cmd)
            for i in sbits:
                num = i[1:]
                self.Instr_write("bts ebx,%d"%(int(num)),thread)
                ori_value = ori_value | (0x1<<int(num))
            for i in rbits:
                num = i[1:]
                self.Instr_write("btr ebx,%d"%(int(num)),thread)
                ori_value = ori_value & (~(0x1<<int(num)))
            self.Instr_write("mov %s, ebx"%(cr),thread)       
            if flag == "all":
                for i in range(0,self.threads):
                    self.update_control_reg(new_cr, ori_value, i)
            else:
                self.update_control_reg(new_cr, ori_value, thread)  
            self.Comment("####%s_l is 0x%x####"%(cr,self.get_control_reg(cr+"_l", thread)))