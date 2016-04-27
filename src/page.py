#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' page module '
__author__ = 'Ken Zhao'
########################################################
# page module is used to generate different page parten
########################################################
from operator import eq, ne
from util import Util
from logging import info, error, debug, warning, critical
class Page(Util):
    def __init__(self,page_mode,tpg_path):
        self.page_mode = page_mode
        self.tpg_path = tpg_path
        
    def Gen_page(self,instr_manager):
        self.instr_manager = instr_manager
        self.Comment("######################set page and cr3#######################")
        if eq(self.page_mode,"4KB_64bit"):
            page_file = "%s/page_tables/64bit/ia32e_4K.rasm"%(self.tpg_path)
            self.Gen_page_4K_64(page_file)
        elif eq(self.page_mode,"4KB_32bit"):
            page_file = "%s/page_tables/32bit/pde_4K.rasm"%(self.tpg_path)
            self.Gen_page_4K_32(page_file)
        elif eq(self.page_mode,"4MB"):
            self.Gen_page_4M()
        elif eq(self.page_mode,"2MB"):
            self.Gen_page_2M()
        elif eq(self.page_mode,"1GB"):
            self.Gen_page_1G()
        else:
            Util.Error_exit("Invalid page mode!")
              
    def Gen_page_4K_32(self,page_file):

        self.Text_write("include \"%s\""%(page_file))
        self.Instr_write("mov eax,$ptgen_tlb_0_base")
        self.Instr_write("mov cr3,eax")

        
    def Gen_page_4K_64(self,page_file):

        self.Text_write("include \"%s\""%(page_file))
        self.Instr_write("mov eax,$ptgen_tlb_0_base")
        self.Instr_write("mov cr3,eax")
    
    def Gen_page_4M(self):

        self.tlb_base = self.mpg.Apply_mem(0x800000,16,start=0x100000,end=0xa00000,name="tlb_base") # 8MB for page_table above 1MB
        self.Vars_write(self.tlb_base["name"],self.tlb_base["start"])
        
    def Gen_page_2M(self):

        self.tlb_base = self.mpg.Apply_mem(0x800000,16,start=0x100000,end=0xa00000,name="tlb_base") # 8MB for page_table above 1MB
        self.Vars_write(self.tlb_base["name"],self.tlb_base["start"])
        
    def Gen_page_1G(self):

        self.tlb_base = self.mpg.Apply_mem(0x800000,16,start=0x100000,end=0xa00000,name="tlb_base") # 8MB for page_table above 1MB
        self.Vars_write(self.tlb_base["name"],self.tlb_base["start"])