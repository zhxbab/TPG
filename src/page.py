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
    def __init__(self,page_mode,tpg_path,mpg,instr_manager,threads):
        self.page_mode = page_mode
        self.tpg_path = tpg_path
        self.mpg = mpg
        self.instr_manager = instr_manager
        self.threads = threads
        self.page_info_pointer={}
        self.c_gen = 0
        self.intel = 0
        self.vmx_client_mode = "long_mode"
        self.mode = "long_mode"
        
    def Gen_page(self):
        self.Comment("######################gen page addr#######################")

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
              
    def Write_page(self):
        self.Comment("######################set page and cr3#######################")
        if eq(self.page_mode,"4KB_64bit"):
            self.Write_page_4K_64()
        elif eq(self.page_mode,"4KB_32bit"):
            self.Write_page_4K_32()
        elif eq(self.page_mode,"4MB"):
            self.Write_page_4M()
        elif eq(self.page_mode,"2MB"):
            self.Write_page_2M()
        elif eq(self.page_mode,"1GB"):
            self.Write_page_1G()
        else:
            Util.Error_exit("Invalid page mode!")
            
    def Gen_page_4K_32(self,page_file):

        self.Text_write("include \"%s\""%(page_file))
        self.tlb_base = self.mpg.Apply_fix_mem("tlb_base",0x100000,0x400000)
        
    def Write_page_4K_32(self):
        self.Instr_write("mov eax,$ptgen_tlb_0_base")
        self.Instr_write("mov cr3,eax")
        
    def Gen_page_4K_64(self,page_file):

        self.Text_write("include \"%s\""%(page_file))
        self.tlb_base = self.mpg.Apply_fix_mem("tlb_base",0x100000,0x800000)
        
    def Write_page_4K_64(self):
        self.Instr_write("mov eax,$ptgen_tlb_0_base")
        self.Instr_write("mov cr3,eax")
        
    def Gen_page_4M(self):
        if self.multi_page == 0:
            self.tlb_base = self.mpg.Apply_mem(0x4000,0x1000,start=0x100000,end=0x400000,name="tlb_base") # 8MB for page_table above 1MB
        else:
            self.tlb_base = []
            for i in range(0,self.threads):
                tlb_base = self.mpg.Apply_mem(0x4000,0x1000,start=0x100000,end=0x400000,name="tlb_base_%d"%(i)) # 8MB for page_table above 1MB
                if self.intel:
                    intel_id = i * 2
                    self.Text_write("@%s[%d].cr3 = 0x%016x"%(self.page_info_pointer["name"],intel_id,tlb_base["start"]))
                else:
                    self.Text_write("@%s[%d].cr3 = 0x%016x"%(self.page_info_pointer["name"],i,tlb_base["start"]))
                self.tlb_base.append(tlb_base)
                del tlb_base
                
    def Write_page_4M(self):
        if self.multi_page == 0:
            self.Comment("####Page Info####")
            self.Vars_write(self.tlb_base["name"],self.tlb_base["start"])
            self.Text_write("$tlb_pointer = INIT_TLB $%s"%(self.tlb_base["name"]))
            self.Instr_write("mov eax,$%s"%(self.tlb_base["name"]))
            self.Instr_write("mov cr3,eax")
            self.Text_write("PAGING $tlb_pointer")
            for i in range(0,1024):
                if i < 758:
                    self.Text_write("PAGE_PDE\t%d\t0x%05x087"%(i,i*0x400000/0x1000))         
                else:
                    self.Text_write("PAGE_PDE\t%d\t0x%05x19f"%(i,i*0x400000/0x1000))
        else:
            n = 0
            if self.c_gen == 0:
                for tlb_base in self.tlb_base:
                    self.Comment("####Core %d page####"%(n))
                    self.Vars_write(tlb_base["name"],tlb_base["start"])
                    self.Text_write("$tlb_pointer_%d = INIT_TLB $%s"%(n,tlb_base["name"]))
                    if n == 0:
                        self.Instr_write("mov eax,$%s"%(tlb_base["name"]))
                        self.Instr_write("mov cr3,eax")
                        self.Text_write("PAGING $tlb_pointer_0")
                    for i in range(0,1024):
                        if i < 256:
                            self.Text_write("PAGE_PDE\t%d\t0x%05x087"%(i,i*0x400000/0x1000))
                        elif 256 <=i<384:
                            new_i = i + n*128
                            self.Text_write("PAGE_PDE\t%d\t0x%05x087"%(i,new_i*0x400000/0x1000))
                        elif 384 <=i<512:
                            new_i = i - 128 + n*128
                            self.Text_write("PAGE_PDE\t%d\t0x%05x087"%(i,new_i*0x400000/0x1000))
                        elif 512 <=i<640:
                            new_i = i - 128*2 + n*128
                            self.Text_write("PAGE_PDE\t%d\t0x%05x087"%(i,new_i*0x400000/0x1000))
                        elif 640 <=i<758:
                            new_i = i - 128*3 + n*128
                            self.Text_write("PAGE_PDE\t%d\t0x%05x087"%(i,new_i*0x400000/0x1000))           
                        else:
                            self.Text_write("PAGE_PDE\t%d\t0x%05x19f"%(i,i*0x400000/0x1000))
                    n=n+1
            else:
                #csmith_page_num = 32 #0x8000000/0x400000
                #offset = 128
                for tlb_base in self.tlb_base:
                    self.Comment("####Core %d page####"%(n))
                    self.Vars_write(tlb_base["name"],tlb_base["start"])
                    self.Text_write("$tlb_pointer_%d = INIT_TLB $%s"%(n,tlb_base["name"]))
                    if n == 0:
                        self.Instr_write("mov eax,$%s"%(tlb_base["name"]))
                        self.Instr_write("mov cr3,eax")
                        self.Text_write("PAGING $tlb_pointer_0")
                    for i in range(0,1024):
                        if i < 758 and i != 32:
                            self.Text_write("PAGE_PDE\t%d\t0x%05x087"%(i,i*0x400000/0x1000))
                        elif i==32:
                            new_i = i + n*128
                            self.Text_write("PAGE_PDE\t%d\t0x%05x087"%(i,new_i*0x400000/0x1000)) 
                        else:
                            self.Text_write("PAGE_PDE\t%d\t0x%05x19f"%(i,i*0x400000/0x1000))
                    n=n+1
            
    def Write_page_2M(self):
        if self.multi_page == 0:
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
        else:
            if self.c_gen == 0:
                for index in range(0,len(self.tlb_base)):
                    pdes = [self.pde0[index],self.pde1[index],self.pde2[index],self.pde3[index]]
                    self.Vars_write(self.tlb_base[index]["name"],self.tlb_base[index]["start"])
                    self.Text_write("$tlb_pointer_%d = INIT_TLB $%s"%(index,self.tlb_base[index]["name"]))
                    if index == 0:
                        self.Instr_write("mov eax,$%s"%(self.tlb_base[index]["name"]))
                        self.Instr_write("mov cr3,eax")
                        self.Text_write("PAGING $tlb_pointer_0")
                    for i in range(0,512):
                        if i == 0:
                            self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007"%(i,self.pdpte[index]["start"]/self.pdpte[index]["size"]))
                        else:
                            self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007\t0"%(i,self.pdpte[index]["start"]/self.pdpte[index]["size"]))
                            
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
                            elif i == 0x1 or i == 0x2:
                                if j<128:
                                    new_j = j + index*128
                                    addr = (new_j*0x200000+i*0x40000000)/0x1000
                                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))
                                elif 128<=j<256:
                                    new_j = j + (index-1)*128
                                    addr = (new_j*0x200000+i*0x40000000)/0x1000
                                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))
                                elif 256<=j<384:
                                    new_j = j+ (index-2)*128
                                    addr = (new_j*0x200000+i*0x40000000)/0x1000
                                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))
                                else:
                                    new_j = j+ (index-3)*128
                                    addr = (new_j*0x200000+i*0x40000000)/0x1000
                                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))                                    
                            else:
                                self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x187"%(i,j,addr))
                    
            else:
                #csmith_page_num = 2 , 3
                #offset = 128
                for index in range(0,len(self.tlb_base)):
                    pdes = [self.pde0[index],self.pde1[index],self.pde2[index],self.pde3[index]]
                    self.Vars_write(self.tlb_base[index]["name"],self.tlb_base[index]["start"])
                    self.Text_write("$tlb_pointer_%d = INIT_TLB $%s"%(index,self.tlb_base[index]["name"]))
                    if index == 0:
                        self.Instr_write("mov eax,$%s"%(self.tlb_base[index]["name"]))
                        self.Instr_write("mov cr3,eax")
                        self.Text_write("PAGING $tlb_pointer_0")
                    for i in range(0,512):
                        if i == 0:
                            self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007"%(i,self.pdpte[index]["start"]/self.pdpte[index]["size"]))
                        else:
                            self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007\t0"%(i,self.pdpte[index]["start"]/self.pdpte[index]["size"]))
                            
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
                            elif i == 0x1 or i == 0x2:
                                self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))                                    
                            else:
                                if self.mode == "long_mode":
                                    if 2<=j<=3:
                                        new_j = j+ index*128
                                        addr = (new_j*0x200000+i*0x40000000)/0x1000
                                        self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))
    
                                    else:
                                        self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))
                                else:
                                    if 64<=j<=65:
                                        new_j = j+ index*128
                                        addr = (new_j*0x200000+i*0x40000000)/0x1000
                                        self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))
    
                                    else:
                                        self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))
    def Gen_page_2M(self):
        if self.multi_page == 0:
            self.tlb_base = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="tlb_base") # allocate 4KB for PML4E, one entry include 512G.
            self.pdpte = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pdpte") # allocate 4KB for PDPTE, all the PML4E point to the same pdpte base. 
            self.pde0 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pde0")
            self.pde1 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pde1")
            self.pde2 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pde2")
            self.pde3 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pde3") # allocate 4*4KB for PDE, PDPTE(0-3) use different PDE 
        else:
            self.tlb_base=[]
            self.pdpte=[]
            self.pde0=[]
            self.pde1=[]
            self.pde2=[]
            self.pde3=[]
            for i in range(0,self.threads):
                tlb_base = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="tlb_base_%d"%(i)) # allocate 4KB for PML4E, one entry include 512G.
                pdpte = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pdpte_%d"%(i)) # allocate 4KB for PDPTE, all the PML4E point to the same pdpte base. 
                pde0 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pde0_%d"%(i))
                pde1 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pde1_%d"%(i))
                pde2 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pde2_%d"%(i))
                pde3 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="pde3_%d"%(i)) # allocate 4*4KB for PDE, PDPTE(0-3) use different PDE
                if self.intel:
                    intel_id = i * 2
                    self.Text_write("@%s[%d].cr3 = 0x%016x"%(self.page_info_pointer["name"],intel_id,tlb_base["start"]))
                else:
                    self.Text_write("@%s[%d].cr3 = 0x%016x"%(self.page_info_pointer["name"],i,tlb_base["start"]))
                self.tlb_base.append(tlb_base)
                self.pdpte.append(pdpte)
                self.pde0.append(pde0)
                self.pde1.append(pde1)
                self.pde2.append(pde2)
                self.pde3.append(pde3)
                del tlb_base,pdpte,pde0,pde1,pde2,pde3
                    
    def Gen_vmx_page_2M_addr(self):

        self.vmx_tlb_base = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="vmx_tlb_base") # allocate 4KB for PML4E, one entry include 512G.
        self.vmx_pdpte = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="vmx_pdpte") # allocate 4KB for PDPTE, all the PML4E point to the same pdpte base. 
        self.vmx_pde0 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="vmx_pde0")
        self.vmx_pde1 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="vmx_pde1")
        self.vmx_pde2 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="vmx_pde2")
        self.vmx_pde3 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="vmx_pde3") # allocate 4*4KB for PDE, PDPTE(0-3) use different PDE 
                  
    def Write_vmx_page_2M(self):
        vmx_pdes = [self.vmx_pde0,self.vmx_pde1,self.vmx_pde2,self.vmx_pde3]
        self.Vars_write(self.vmx_tlb_base["name"],self.vmx_tlb_base["start"])
        self.Text_write("$vmx_tlb_pointer = INIT_TLB $%s"%(self.vmx_tlb_base["name"]))
        self.Text_write("PAGING $vmx_tlb_pointer")
        for i in range(0,512):
            if i == 0:
                self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007"%(i,self.vmx_pdpte["start"]/self.vmx_pdpte["size"]))
            else:
                self.Text_write("PAE64_PML4E\t%d\t\t0x0\t0x%05x007\t0"%(i,self.vmx_pdpte["start"]/self.vmx_pdpte["size"]))
                
        for i in range(0,512):
            if 0x0 <= i <=0x3:
                self.Text_write("PAE64_PDPT\t0\t%d\t0x0\t0x%05x007"%(i,vmx_pdes[i%4]["start"]/vmx_pdes[i%4]["size"])) 
            else:
                self.Text_write("PAE64_PDPT\t0\t%d\t0x0\t0x%05x007\t%d"%(i,vmx_pdes[i%4]["start"]/vmx_pdes[i%4]["size"],i%4))
                
        for i in range(0,4):
            for j in range(0,512):
                addr = (j*0x200000+i*0x40000000)/0x1000
                if i == 0x3:
                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x19F"%(i,j,addr))
                elif i == 0x1:
                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x187"%(i,j,addr))
                else:
                    self.Text_write("PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x087"%(i,j,addr))  

           
    def Gen_ept_2M_addr(self):
        if self.multi_ept == 0:
            self.ept_tlb_base = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_tlb_base") # allocate 4KB for PML4E, one entry include 512G.
            self.ept_pdpte = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pdpte") # allocate 4KB for PDPTE, all the PML4E point to the same pdpte base. 
            self.ept_pde0 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pde0")
            self.ept_pde1 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pde1")
            self.ept_pde2 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pde2")
            self.ept_pde3 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pde3") # allocate 4*4KB for PDE, PDPTE(0-3) use different PDE 
        else:
            self.ept_tlb_base=[]
            self.ept_pdpte=[]
            self.ept_pde0=[]
            self.ept_pde1=[]
            self.ept_pde2=[]
            self.ept_pde3=[]
            for i in range(0,self.threads):
                ept_tlb_base = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_tlb_base_%d"%(i)) # allocate 4KB for PML4E, one entry include 512G.
                ept_pdpte = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pdpte_%d"%(i)) # allocate 4KB for PDPTE, all the PML4E point to the same pdpte base. 
                ept_pde0 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pde0_%d"%(i))
                ept_pde1 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pde1_%d"%(i))
                ept_pde2 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pde2_%d"%(i))
                ept_pde3 = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0x400000,name="ept_pde3_%d"%(i)) # allocate 4*4KB for PDE, PDPTE(0-3) use different PDE
#                if self.intel:
#                    intel_id = i * 2
#                    self.Text_write("@%s[%d].cr3 = 0x%016x"%(self.page_info_pointer["name"],intel_id,tlb_base["start"]))
#                else:
#                    self.Text_write("@%s[%d].cr3 = 0x%016x"%(self.page_info_pointer["name"],i,tlb_base["start"]))
                self.ept_tlb_base.append(ept_tlb_base)
                self.ept_pdpte.append(ept_pdpte)
                self.ept_pde0.append(ept_pde0)
                self.ept_pde1.append(ept_pde1)
                self.ept_pde2.append(ept_pde2)
                self.ept_pde3.append(ept_pde3)
                del ept_tlb_base,ept_pdpte,ept_pde0,ept_pde1,ept_pde2,ept_pde3            
                    
    def Write_ept_2M(self):
        if self.multi_ept == 0:
            ept_pdes = [self.ept_pde0,self.ept_pde1,self.ept_pde2,self.ept_pde3]
            self.Vars_write(self.ept_tlb_base["name"],self.ept_tlb_base["start"])
            #self.Instr_write("mov eax,$%s"%(self.ept_tlb_base["name"]))
            #self.Instr_write("mov cr3,eax")
            self.Text_write("$ept_tlb_pointer = INIT_TLB $%s"%(self.ept_tlb_base["name"]))
    
    
            for i in range(0,512):
                if i == 0:
                    self.Text_write("EPT_PAE64_PML4E\t%d\t\t0x0\t0x%05x007"%(i,self.ept_pdpte["start"]/self.ept_pdpte["size"]))
                else:
                    self.Text_write("EPT_PAE64_PML4E\t%d\t\t0x0\t0x%05x007\t0"%(i,self.ept_pdpte["start"]/self.ept_pdpte["size"]))
                    
            for i in range(0,512):
                if 0x0 <= i <=0x3:
                    self.Text_write("EPT_PAE64_PDPT\t0\t%d\t0x0\t0x%05x007"%(i,ept_pdes[i%4]["start"]/ept_pdes[i%4]["size"])) 
                else:
                    self.Text_write("EPT_PAE64_PDPT\t0\t%d\t0x0\t0x%05x007\t%d"%(i,ept_pdes[i%4]["start"]/ept_pdes[i%4]["size"],i%4))
                    
            for i in range(0,4):
                for j in range(0,512):
                    addr = (j*0x200000+i*0x40000000)/0x1000
                    if i == 0x3:
                        self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x19F"%(i,j,addr))
                    elif i == 0x1:
                        self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x1B7"%(i,j,addr))#ept is different from 2M page
                    else:
                        self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))# for ept, if want to ignore pat, need to set ipat = 1
            self.Text_write("EPT $ept_tlb_pointer")#this cmd must put the finall for ept, but not mush for page
        else:
            if self.c_gen == 0:
                for index in range(0,len(self.ept_tlb_base)):
                    ept_pdes = [self.ept_pde0[index],self.ept_pde1[index],self.ept_pde2[index],self.ept_pde3[index]]
                    self.Vars_write(self.ept_tlb_base[index]["name"],self.ept_tlb_base[index]["start"])
                    self.Text_write("$ept_tlb_pointer_%d = INIT_TLB $%s"%(index,self.ept_tlb_base[index]["name"]))
#                    if index == 0:
#                        self.Instr_write("mov eax,$%s"%(self.tlb_base[index]["name"]))
#                        self.Instr_write("mov cr3,eax")
#                        self.Text_write("PAGING $tlb_pointer_0")
                    for i in range(0,512):
                        if i == 0:
                            self.Text_write("EPT_PAE64_PML4E\t%d\t\t0x0\t0x%05x007"%(i,self.ept_pdpte[index]["start"]/self.ept_pdpte[index]["size"]))
                        else:
                            self.Text_write("EPT_PAE64_PML4E\t%d\t\t0x0\t0x%05x007\t0"%(i,self.ept_pdpte[index]["start"]/self.ept_pdpte[index]["size"]))
                            
                    for i in range(0,512):
                        if 0x0 <= i <=0x3:
                            self.Text_write("EPT_PAE64_PDPT\t0\t%d\t0x0\t0x%05x007"%(i,ept_pdes[i%4]["start"]/ept_pdes[i%4]["size"])) 
                        else:
                            self.Text_write("EPT_PAE64_PDPT\t0\t%d\t0x0\t0x%05x007\t%d"%(i,ept_pdes[i%4]["start"]/ept_pdes[i%4]["size"],i%4))
                            
                    for i in range(0,4):
                        for j in range(0,512):
                            addr = (j*0x200000+i*0x40000000)/0x1000
                            if i == 0x3:
                                self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x19F"%(i,j,addr))
                            elif i == 0x1 or i == 0x2:
                                if j<128:
                                    new_j = j + index*128
                                    addr = (new_j*0x200000+i*0x40000000)/0x1000
                                    self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))
                                elif 128<=j<256:
                                    new_j = j + (index-1)*128
                                    addr = (new_j*0x200000+i*0x40000000)/0x1000
                                    self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))
                                elif 256<=j<384:
                                    new_j = j+ (index-2)*128
                                    addr = (new_j*0x200000+i*0x40000000)/0x1000
                                    self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))
                                else:
                                    new_j = j+ (index-3)*128
                                    addr = (new_j*0x200000+i*0x40000000)/0x1000
                                    self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))                                    
                            else:
                                self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x1B7"%(i,j,addr))
                    #self.Text_write("EPT $ept_tlb_pointer_%d"%(index))#this cmd must put the finall for ept, but not mush for page
            else:
                #csmith_page_num = 2 , 3
                #offset = 128
                for index in range(0,len(self.ept_tlb_base)):
                    ept_pdes = [self.ept_pde0[index],self.ept_pde1[index],self.ept_pde2[index],self.ept_pde3[index]]
                    self.Vars_write(self.ept_tlb_base[index]["name"],self.ept_tlb_base[index]["start"])
                    self.Text_write("$ept_tlb_pointer_%d = INIT_TLB $%s"%(index,self.ept_tlb_base[index]["name"]))
#                    if index == 0:
#                        self.Instr_write("mov eax,$%s"%(self.tlb_base[index]["name"]))
#                        self.Instr_write("mov cr3,eax")
#                        self.Text_write("PAGING $tlb_pointer_0")
                    for i in range(0,512):
                        if i == 0:
                            self.Text_write("EPT_PAE64_PML4E\t%d\t\t0x0\t0x%05x007"%(i,self.ept_pdpte[index]["start"]/self.ept_pdpte[index]["size"]))
                        else:
                            self.Text_write("EPT_PAE64_PML4E\t%d\t\t0x0\t0x%05x007\t0"%(i,self.ept_pdpte[index]["start"]/self.ept_pdpte[index]["size"]))
                            
                    for i in range(0,512):
                        if 0x0 <= i <=0x3:
                            self.Text_write("EPT_PAE64_PDPT\t0\t%d\t0x0\t0x%05x007"%(i,ept_pdes[i%4]["start"]/ept_pdes[i%4]["size"])) 
                        else:
                            self.Text_write("EPT_PAE64_PDPT\t0\t%d\t0x0\t0x%05x007\t%d"%(i,ept_pdes[i%4]["start"]/ept_pdes[i%4]["size"],i%4))
                            
                    for i in range(0,4):
                        for j in range(0,512):
                            if self.vmx_client_mode == "long_mode":
                                addr = (j*0x200000+i*0x40000000)/0x1000
                                if i == 0x3:
                                    self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x19F"%(i,j,addr))
                                elif i == 0x1 or i == 0x2:
                                    self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))                                    
                                else:
                                    if 2<=j<=3:
                                        new_j = j+ index*128
                                        addr = (new_j*0x200000+i*0x40000000)/0x1000
                                        self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))
    
                                    else:
                                        self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))
                            else:
                                addr = (j*0x200000+i*0x40000000)/0x1000
                                if i == 0x3:
                                    self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x19F"%(i,j,addr))
                                elif i == 0x1 or i == 0x2:
                                    self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))                                    
                                else:
                                    if 64<=j<=65:
                                        new_j = j+ index*128
                                        addr = (new_j*0x200000+i*0x40000000)/0x1000
                                        self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))
    
                                    else:
                                        self.Text_write("EPT_PAE64_PDE\t0\t%d\t%d\t0x0\t0x%05x0B7"%(i,j,addr))                               
                    #self.Text_write("EPT $ept_tlb_pointer_%d"%(index))#this cmd must put the finall for ept, but not mush for page                   
   
    def Gen_page_1G(self): # intel platform use this page pattern fails

        self.tlb_base = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="tlb_base") # allocate 4KB for PML4E, one entry include 512G.
        self.pdpte = self.mpg.Apply_mem(0x1000,0x1000,start=0x100000,end=0xa00000,name="pdpte") # allocate 4KB for PDPTE, all the PML4E point to the same pdpte base. 

                 
    def Write_page_1G(self):
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