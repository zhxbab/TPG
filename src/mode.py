#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' mode module '
__author__ = 'Ken Zhao'
########################################################
# mode module is used to generate different mode code
########################################################
from operator import eq, ne
from util import Util
class Mode(Util):
    def __init__(self, mpg, instr_manager, ptg):
        self.mpg = mpg
        self.instr_manager = instr_manager
        self.ptg = ptg
            
    def Set_table_pointer(self,table_name):
        table_pointer = self.mpg.Apply_mem(0x10,16,start=0x0,end=0x10000,name="%s_pointer"%(table_name)) #0x10000 = 64KB, in real mode(B=0), the limit of segment is 0xFFFF
        self.Text_write("org 0x%x"%(table_pointer["start"]))
        self.Text_write("@%s = new std::table_pointer"%(table_pointer["name"]))
        self.Text_write("@%s.base = $%s"%(table_pointer["name"],table_name))
        self.Text_write("@%s.limit = 0xFFFF"%(table_pointer["name"]))
        return table_pointer
        
    def Long_mode(self):
        self.Comment("###########################vars definition######################")
        gdt_table_base = self.mpg.Apply_mem(0x1000,16,start=0,end=0x10000,name="gdt_table_base") # for 512 gdt descriptor
        idt_table_base = self.mpg.Apply_mem(0x1000,16,start=0,end=0x10000,name="idt_table_base") # 256 interrupt and every gate is 128bit
        self.Vars_write(gdt_table_base["name"],gdt_table_base["start"])
        self.Vars_write(idt_table_base["name"],idt_table_base["start"])
        self.gdt_table_base_pointer = self.Set_table_pointer(gdt_table_base["name"])
        self.idt_table_base_pointer = self.Set_table_pointer(idt_table_base["name"])
        self.Set_gdt_table(gdt_table_base)
        self.Text_write("&TO_MEMORY_ALL()")
        self.Main_code()
        
        
    def Set_gdt_table(self,gdt_table_base):
        self.Comment("###########################GDT definition######################")
        self.Text_write("org 0x%x"%(gdt_table_base["start"]))
        self.Text_write("@gdt = new std::descriptor[10]")
        self.selector_name_cs32_0 = "cs32"
        self.selector_value_cs32_0 = 0x1
        self.Vars_write(self.selector_name_cs32_0,self.selector_value_cs32_0)
        self.Text_write("@gdt[$%s].type = 0xB"%(self.selector_name_cs32_0))
        self.Text_write("@gdt[$%s].db = 0x1"%(self.selector_name_cs32_0))
        self.selector_name_ds32_0 = "ds32"
        self.selector_value_ds32_0 = 0x2
        self.Vars_write(self.selector_name_ds32_0,self.selector_value_ds32_0)
        self.Text_write("@gdt[$%s].type = 0x3"%(self.selector_name_ds32_0))
        self.Text_write("@gdt[$%s].db = 0x1"%(self.selector_name_ds32_0))
        self.selector_name_cs64_0 = "cs64"
        self.selector_value_cs64_0 = 0x3
        self.Vars_write(self.selector_name_cs64_0,self.selector_value_cs64_0)
        self.Text_write("@gdt[$%s].type = 0xB"%(self.selector_name_cs64_0))
        self.Text_write("@gdt[$%s].l = 0x1"%(self.selector_name_cs64_0))
        self.selector_name_ds64_0 = "ds64"
        self.selector_value_ds64_0 = 0x4
        self.Vars_write(self.selector_name_ds64_0,self.selector_value_ds64_0)
        self.Text_write("@gdt[$%s].type = 0x3"%(self.selector_name_ds64_0))
        self.Text_write("@gdt[$%s].l = 0x1"%(self.selector_name_ds64_0))
        
    def Main_code(self):
        self.Comment("###########################main code######################")
        self.Text_write("org 0xFFFFFFF0")
        self.Text_write("use 16")
        real_mode_code_start = self.mpg.Apply_mem(0x100,16,start=0x0,end=0x10000,name="real_mode_code_start")
        self.Instr_write("jmp 0x0:0x%x"%(real_mode_code_start["start"]))
        self.Text_write("org 0x%x"%(real_mode_code_start["start"]))
        self.Instr_write("lgdt [&@%s]"%(self.gdt_table_base_pointer["name"]))
        self.Instr_write("lidt [&@%s]"%(self.idt_table_base_pointer["name"]))
        self.Comment("##enable 32bit mode")
        protect_mode_code_start = self.mpg.Apply_mem(0x1000,16,start=0x0,end=0x100000,name="protect_mode_code_start")
        self.Instr_write("mov edx,cr0")
        self.Instr_write("or edx,0x1")
        self.Instr_write("mov cr0,edx")
        self.Instr_write("jmpf &SELECTOR($%s):0x%x"%(self.selector_name_cs32_0,protect_mode_code_start["start"]))
        self.Text_write("org 0x%x"%(protect_mode_code_start["start"]))
        self.Text_write("use 32")
        self.Comment("##enable pae,fxsave(sse),simd,global page")
        self.Instr_write("mov eax,cr4")
        self.Instr_write("or eax,0x6A0")
        self.Instr_write("mov cr4,eax")
        self.Comment("##set IA32_EFER eax to 0x0")
        self.Comment("#In Intel spec IA32_EFER bit 9 is reversed, if write this bit, it fails in pclmsi")
        self.Msr_Write(0xc0000080,eax=0x0)
        self.ptg.Gen_page(self.instr_manager)
        self.Comment("#enable fpu")
        self.Instr_write("finit")
        self.Comment("#change to ds32")
        self.Instr_write("mov ebx,0x10")
        self.Instr_write("mov ds,ebx")
        self.Instr_write("mov ss,ebx")
        self.Comment("##enable xsave(xset/xget), this will fail in intel celeron platform")
        self.Instr_write("mov eax,cr4")
        self.Instr_write("bts eax,0x12")
        self.Instr_write("mov cr4,eax")
        self.Comment("##enable avx")
        self.Instr_write("mov ecx,0x0") #ecx must be 0 for xgetbv
        self.Instr_write("xgetbv")
        self.Instr_write("bts eax,0x1")
        self.Instr_write("bts eax,0x2")
        self.Instr_write("xsetbv")
#    		self.Comment("#enable paging")  
#		self.Instr_write("mov eax,cr0")
#		self.Instr_write("or eax,0x80000000")
#		self.Instr_write("mov cr0,eax")    
        
        
        