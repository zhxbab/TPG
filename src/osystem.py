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
from copy import deepcopy
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
        self.gdtr = {"base":0x0,"limit":0xFFFF}
        self.idtr = {"base":0x0,"limit":0xFFFF}
        self.gdt = [{"name":"dummy","data":{"limit":0xFFFFF,"base":0x0,"type":0x0,"s":0x1,"dpl":0x0,"p":0x1,"avl":0x0,"l":0x0,"db":0x0,"g":0x1}},]
        self.idt = [{"name":"dummy","data":{"offset":0xFFFFF,"selector":0x0,"ist":0x0,"type":0xE,"dpl":0x0,"p":0x1}},]
        self.int_handler = {"base":0x0,"size":0x0}
        self.os_name = ["real_mode","protect_mode","ia32e_mode"]
        self.page_mode_name = ["no_page","en_page"]
        self.current_mode = 0
        self.current_page_mode = 0
        self.instr_manager = instr_manager
        self.pae = 0
        self.pse = 0
        self.msr_table = {"IA32_EFER":{"index":0xc0000080,"value_l":[0x00000000]*self.threads,"value_h":[0x00000000]*self.threads},\
                          }
        #self.page_file_name = None
        
    def reset_osystem(self):
        sefl.__init(self.threads)
        
#    def init_page_file(self):
#        self.set_org(org_add, thread)
        
    def update_gdtr(self,base):
        self.gdtr["base"] = base
        
    def update_idtr(self,base):
        self.idtr["base"] = base
                
    def update_gdt_entry(self,name,index,**gdt_value):
        if index <= len(self.gdt)-1:
                self.update_gdt_one_entry(name,index,**gdt_value)
        else:
            for i in range(0,(index-len(self.gdt)+1)):
                self.gdt.append(deepcopy(self.gdt[0]))
            self.update_gdt_one_entry(name,index,**gdt_value)
                   
    def update_gdt_one_entry(self,name,index,**gdt_value):
        self.gdt[index]["name"] = name
        if "limit" in gdt_value.keys():
            self.gdt[index]["data"]["limit"] = gdt_value["limit"]
        if "base" in gdt_value.keys():
            self.gdt[index]["data"]["base"] = gdt_value["base"]
        if "type" in gdt_value.keys():
            self.gdt[index]["data"]["type"] = gdt_value["type"]
        if "s" in gdt_value.keys():
            self.gdt[index]["data"]["s"] = gdt_value["s"]
        if "dpl" in gdt_value.keys():
            self.gdt[index]["data"]["dpl"] = gdt_value["dpl"]
        if "p" in gdt_value.keys():
            self.gdt[index]["data"]["p"] = gdt_value["p"]
        if "avl" in gdt_value.keys():
            self.gdt[index]["data"]["avl"] = gdt_value["avl"]
        if "l" in gdt_value.keys():
            self.gdt[index]["data"]["l"] = gdt_value["l"]
        if "db" in gdt_value.keys():
            self.gdt[index]["data"]["db"] = gdt_value["db"]
        if "g" in gdt_value.keys():
            self.gdt[index]["data"]["g"] = gdt_value["g"]
            
    def show_gdt_info(self):
        info("GDTR is %s"%(self.gdtr))
        info("GDT is %s"%(self.gdt))
        
    def update_idt_entry(self,name,index,**idt_value):
        if index <= len(self.idt)-1:
                self.update_idt_one_entry(name,index,**idt_value)
        else:
            for i in range(0,(index-len(self.idt)+1)):
                self.idt.append(deepcopy(self.idt[0]))
            self.update_idt_one_entry(name,index,**idt_value)

    def update_idt_one_entry(self,name,index,**idt_value):
        self.idt[index]["name"] = name
        if "offset" in idt_value.keys():
            if idt_value["offset"] == 0x0:
                self.idt[index]["data"]["offset"] = (self.int_handler["base"]+index*self.int_handler["size"]/256)
        if "selector" in idt_value.keys():
            self.idt[index]["data"]["selector"] = idt_value["selector"]
        if "type" in idt_value.keys():
            self.idt[index]["data"]["type"] = idt_value["type"]
        if "ist" in idt_value.keys():
            self.idt[index]["data"]["ist"] = idt_value["ist"]
        if "dpl" in idt_value.keys():
            self.idt[index]["data"]["dpl"] = idt_value["dpl"]
        if "p" in idt_value.keys():
            self.idt[index]["data"]["p"] = idt_value["p"]

    def show_idt_info(self):
        info("IDTR is %s"%(self.idtr))
        info("IDT is %s"%(self.idt))

        
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