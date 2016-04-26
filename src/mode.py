#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' mode module '
__author__ = 'Ken Zhao'
########################################################
# mode module is used to generate different mode code
########################################################
from operator import eq, ne
from util import Util
class Mode:
    def __init__(self, mpg, mode, asm_file, instr_manager):
        self.mpg = mpg
        self.asm_file = asm_file
        self.instr_manager = instr_manager
        if(mode,"long_mode"):
            self.Long_mode()
        elif(mode,"protect_mode"):
            pass
        elif(mode, "compatibility_mode"):
            pass
        else:
            Util.Error_exit("Invalid mode!")
            
    def Set_table_pointer(self,table_name):
        table_pointer = self.mpg.Apply_mem(0x10,16,start=0x10000,end=0x100000,name="%s_pointer"%(table_name))
        Util.Text_write(self.asm_file,"org 0x%x"%(table_pointer["start"]))
        Util.Text_write(self.asm_file,"@%s = new std::table_pointer"%(table_pointer["name"]))
        Util.Text_write(self.asm_file,"@%s.base = $%s"%(table_pointer["name"],table_name))
        Util.Text_write(self.asm_file,"@%s.limit = 0xFFFF"%(table_pointer["name"]))
        return table_pointer
        
    def Long_mode(self):
        Util.Text_write(self.asm_file,"include \"std.inc\"")
        Util.Comment(self.asm_file,"###########################vars definition######################")
        gdt_table_base = self.mpg.Apply_mem(0x1000,16,start=0x10000,end=0x100000,name="gdt_table_base")
        idt_table_base = self.mpg.Apply_mem(0x1000,16,start=0x10000,end=0x100000,name="idt_table_base")
        tlb_base = self.mpg.Apply_mem(0x400000,16,start=0x100000,end=0xa00000,name="tlb_base")
        Util.Vars_write(self.asm_file,gdt_table_base["name"],gdt_table_base["start"])
        Util.Vars_write(self.asm_file,idt_table_base["name"],idt_table_base["start"])
        Util.Vars_write(self.asm_file,tlb_base["name"],tlb_base["start"])
        gdt_table_base_pointer = self.Set_table_pointer(gdt_table_base["name"])
        idt_table_base_pointer = self.Set_table_pointer(idt_table_base["name"])
        self.Set_gdt_table(gdt_table_base)
        Util.Text_write(self.asm_file,"&TO_MEMORY_ALL()")
        self.Main_code()
        
        
    def Set_gdt_table(self,gdt_table_base):
        Util.Comment(self.asm_file,"###########################GDT definition######################")
        Util.Text_write(self.asm_file,"org 0x%x"%(gdt_table_base["start"]))
        Util.Text_write(self.asm_file,"@gdt = new std::descriptor[10]")
        selector_name = "cs32"
        selector_value = 0x1
        Util.Vars_write(self.asm_file,selector_name,selector_value)
        Util.Text_write(self.asm_file,"@gdt[$%s].tybe = 0xB"%(selector_name))
        Util.Text_write(self.asm_file,"@gdt[$%s].db = 0x1"%(selector_name))
        selector_name = "ds32"
        selector_value = 0x2
        Util.Vars_write(self.asm_file,selector_name,selector_value)
        Util.Text_write(self.asm_file,"@gdt[$%s].tybe = 0x3"%(selector_name))
        Util.Text_write(self.asm_file,"@gdt[$%s].db = 0x1"%(selector_name))
        selector_name = "cs64"
        selector_value = 0x3
        Util.Vars_write(self.asm_file,selector_name,selector_value)
        Util.Text_write(self.asm_file,"@gdt[$%s].tybe = 0xB"%(selector_name))
        Util.Text_write(self.asm_file,"@gdt[$%s].l = 0x1"%(selector_name))
        selector_name = "ds64"
        selector_value = 0x4
        Util.Vars_write(self.asm_file,selector_name,selector_value)
        Util.Text_write(self.asm_file,"@gdt[$%s].tybe = 0x3"%(selector_name))
        Util.Text_write(self.asm_file,"@gdt[$%s].l = 0x1"%(selector_name))
        
    def Main_code(self):
        Util.Comment(self.asm_file,"###########################main code######################")
        Util.Text_write(self.asm_file,"org 0xFFFFFFF0")
        Util.Text_write(self.asm_file,"use 16")
        real_mode_code_start = self.mpg.Apply_mem(0x1000,16,start=0x0,end=0x8000,name="real_mode_code_start")
        Util.Instr_write(self.asm_file,"jmp 0x0:0x%x"%(real_mode_code_start["start"]),self.instr_manager)