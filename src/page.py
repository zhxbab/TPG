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
    def __init__(self,page_mode,tpg_path,mpg,instr_manager):
        self.page_mode = page_mode
        self.tpg_path = tpg_path
        self.mpg = mpg
        self.instr_manager = instr_manager
        
    def Gen_page(self,instr_manager):

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
        self.tlb_base = self.mpg.Apply_fix_mem("tlb_base",0x100000,0x400000)
        
    def Gen_page_4K_64(self,page_file):

        self.Text_write("include \"%s\""%(page_file))
        self.Instr_write("mov eax,$ptgen_tlb_0_base")
        self.Instr_write("mov cr3,eax")
        self.tlb_base = self.mpg.Apply_fix_mem("tlb_base",0x100000,0x800000)
        
    def Gen_page_4M(self):

        self.tlb_base = self.mpg.Apply_mem(0x4000,0x1000,start=0x100000,end=0xa00000,name="tlb_base") # 8MB for page_table above 1MB
        self.Vars_write(self.tlb_base["name"],self.tlb_base["start"])
        self.Instr_write("mov eax,$%s"%(self.tlb_base["name"]))
        self.Instr_write("mov cr3,eax")
        self.Text_write("$tlb_pointer = INIT_TLB $%s"%(self.tlb_base["name"]))
        self.Text_write("PAGING $tlb_pointer")
        for i in range(0,1024):
            if i < 768:
                self.Text_write("PAGE_PDE\t%d\t0x%05x087"%(i,i*0x400000/0x1000))
            else:
                self.Text_write("PAGE_PDE\t%d\t0x%05x19f"%(i,i*0x400000/0x1000))
        
        
    def Gen_page_2M(self):

        self.tlb_base = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="tlb_base") # allocate 4KB for PML4E, one entry include 512G.
        self.pdpte = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="pdpte") # allocate 4KB for PDPTE, all the PML4E point to the same pdpte base. 
        self.pde0 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="pde0")
        self.pde1 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="pde1")
        self.pde2 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="pde2")
        self.pde3 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="pde3") # allocate 4*4KB for PDE, PDPTE(0-3) use different PDE 
        pdes = [self.pde0,self.pde1,self.pde2,self.pde3]
        self.Vars_write(self.tlb_base["name"],self.tlb_base["start"])
        self.Instr_write("mov eax,$%s"%(self.tlb_base["name"]))
        self.Instr_write("mov cr3,eax")
        self.Text_write("$tlb_pointer = INIT_TLB $%s"%(self.tlb_base["name"]))
        self.Text_write("PAGING $tlb_pointer")

        for i in range(0,512):
            if i == 0:
                self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007"%(i,self.pdpte["start"]/self.pdpte["size"]))
            else:
                self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007\t0"%(i,self.pdpte["start"]/self.pdpte["size"]))
                
        for i in range(0,512):
            if 0x0 <= i <=0x3:
                self.Text_write("PAE64_PDPT\t0\t%d\t0x0\t0x%05x007"%(i,pdes[i%4]["start"]/pdes[i%4]["size"])) 
            else:
                self.Text_write("PAE64_PDPT\t0\t%d\t0x0\t0x%05x007\t%d"%(i,pdes[i%4]["start"]/pdes[i%4]["size"],i%4))
                
        for i in range(0,4):
            for j in range(0,512):
                addr = (j*0x200000+i*0x40000000)/0x1000
                if i == 0x3:
                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x19F"%(i,j,addr))
                elif i == 0x1:
                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x187"%(i,j,addr))
                else:
                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))
                
            
                
    def Gen_page_1G(self): # intel platform use this page pattern fails

        self.tlb_base = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="tlb_base") # allocate 4KB for PML4E, one entry include 512G.
        self.pdpte = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="pdpte") # allocate 4KB for PDPTE, all the PML4E point to the same pdpte base. 
        self.Vars_write(self.tlb_base["name"],self.tlb_base["start"])
        self.Instr_write("mov eax,$%s"%(self.tlb_base["name"]))
        self.Instr_write("mov cr3,eax")
        self.Text_write("$tlb_pointer = INIT_TLB $%s"%(self.tlb_base["name"]))
        self.Text_write("PAGING $tlb_pointer")

        for i in range(0,512):
            if i == 0:
                self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007"%(i,self.pdpte["start"]/self.pdpte["size"]))
            else:
                self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007\t0"%(i,self.pdpte["start"]/self.pdpte["size"]))
                
        for i in range(0,512):
            if i%0x4 == 0x0:
                self.Text_write("PAE64_PDPT\t0\t%d\t0x0\t0x00000087"%(i))
            elif i%04 == 0x1:
                self.Text_write("PAE64_PDPT\t0\t%d\t0x0\t0x40000187"%(i))
            elif i%04 == 0x2:
                self.Text_write("PAE64_PDPT\t0\t%d\t0x0\t0x80000087"%(i))
            else:
                self.Text_write("PAE64_PDPT\t0\t%d\t0x0\t0xC000019F"%(i)) 
        