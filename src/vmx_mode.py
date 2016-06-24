#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' vmx mode module '
__author__ = 'Ken Zhao'
########################################################
# vmx mode module inherit from mode
########################################################
import os, sys
from operator import eq, ne
sys.path.append("/%s/src"%(sys.path[0]))
from mode import Mode
class Vmx_mode(Mode):
    def __init__(self,hlt_code,mpg, instr_manager, ptg, threads, simcmd, intel, interrupt,c_parser=None):
        self.inc_path = ""
        self.hlt_code = hlt_code
        Mode.__init__(self,mpg, instr_manager, ptg, threads, simcmd, intel, interrupt,c_parser)
        self.vmxon = []
        self.vmxon_pointer = []
        self.vmcs = []
        self.vmcs_pointer = []
        self.vmx_guest_entry_0 = []
        self.vmcs_data=[]
        self.vmcs_initial_code = []
        self.vmx_exit_addr = []
    def Mode_code(self,mode,c_gen,vmx_client_mode,disable_avx,disable_pcid):
        self.mode = mode
        self.disable_avx = disable_avx
        self.disable_pcid = disable_pcid
        self.c_gen = c_gen
        self.vmx_client_mode = vmx_client_mode
        self.Comment("###########################vars definition######################")
        gdt_table_base = self.mpg.Apply_mem(0x1000,16,start=0,end=0x10000,name="gdt_table_base") # for 512 gdt descriptor
        idt_table_base = self.mpg.Apply_mem(0x1000,16,start=0,end=0x10000,name="idt_table_base") # 256 interrupt and every gate is 128bit
        self.Vars_write(gdt_table_base["name"],gdt_table_base["start"])
        self.Vars_write(idt_table_base["name"],idt_table_base["start"])
        self.gdt_table_base_pointer = self.Set_table_pointer(gdt_table_base["name"])
        self.idt_table_base_pointer = self.Set_table_pointer(idt_table_base["name"])
        self.Set_gdt_table(gdt_table_base,c_gen)
        self.Set_idt_table(idt_table_base)
        self.ptg.Gen_page()
        self.Set_user_code_stack(c_gen)
        self.Comment("#### SET VMX PAGE AND VMCS DATA ####")
        self.Gen_vmx_page_addr()
        self.Set_vmcs_data()
        self.Text_write("&TO_MEMORY_ALL()")
        self.Set_int_handler()
        self.Long_mode_code()
        return [self.stack_segs,self.user_code_segs]
    
    def Set_vmcs_data(self):
        #self.Text_write("include \"%s/std_vmx_code.inc\""%(self.inc_path))
        for i in range(0,self.threads):
            vmxon = self.mpg.Apply_mem(0x1000,0x1000,start=0x1000000,end=0x80000000,name="vmxon") #vmxon is most 0x1000
            vmxon_pointer = self.mpg.Apply_mem(0x8,16,start=0x1000000,end=0x80000000,name="vmxon_pointer")
            vmcs = self.mpg.Apply_mem(0x1000,0x1000,start=0x1000000,end=0x80000000,name="vmcs")
            vmcs_pointer = self.mpg.Apply_mem(0x8,16,start=0x1000000,end=0x80000000,name="vmcs_pointer")
            vmx_guest_entry_0 = self.mpg.Apply_mem(0x100,16,start=0x1000000,end=0x80000000,name="vmx_guest_entry_0")
            vmcs_data = self.mpg.Apply_mem(0x1000,0x1000,start=0x1000000,end=0x80000000,name="vmcs_data")# because some field has two id, so it is twice of vmcs
            vmcs_initial_code = self.mpg.Apply_mem(0x1000,0x1000,start=0x1000000,end=0x80000000,name="vmcs_initial_code")
            vmx_exit_addr = self.mpg.Apply_mem(0x200,0x20,start=0x1000,end=0xA0000,name="vmx_exit_addr")
            self.vmxon.append(vmxon)
            self.vmxon_pointer.append(vmxon_pointer)
            self.vmcs.append(vmcs)
            self.vmcs_pointer.append(vmcs)
            self.vmx_guest_entry_0.append(vmx_guest_entry_0)
            self.vmcs_data.append(vmcs_data)
            self.vmcs_initial_code.append(vmcs_initial_code)
            self.vmx_exit_addr.append(vmx_exit_addr)
            del vmxon,vmxon_pointer,vmcs,vmcs_pointer,vmx_guest_entry_0,vmcs_data,vmcs_initial_code,vmx_exit_addr
            
        for index in range(0,self.threads):
            self.Text_write("org 0x%x"%(self.vmcs_data[index]["start"]))
            self.Comment("#### Set host ####")
            self.Text_write("@vmcs = new std::vmcs::data")
            self.Text_write("@vmcs.host_gdtr_base = 0x%x"%(self.gdt_table_base_pointer["start"]))
            self.Text_write("@vmcs.host_cs_sel = &SELECTOR($%s)"%(self.selector_name_cs_0))
            self.Text_write("@vmcs.host_ss_sel = &SELECTOR($%s)"%(self.selector_name_ds_0))
            self.Text_write("@vmcs.host_ds_sel = &SELECTOR($%s)"%(self.selector_name_ds_0))
            self.Text_write("@vmcs.host_tr_sel = &SELECTOR($%s)"%(self.selector_name_ds_0)) #FIXME - must point to a tss selector
            self.Text_write("@vmcs.virtual_apic_page_addr_full = 0x%x"%(self.ptg.vmx_tlb_base["start"]))
            self.Text_write("@vmcs.ept_pointer_full = 0x%x"%(self.ptg.ept_tlb_base["start"]))# $std_vmcs_initialize_guest_vmcs will handle this address(or 0x1E)
            self.Text_write("@vmcs.host_rip = 0x%x"%(self.vmcs_initial_code[index]["start"]))
            self.Text_write("@vmcs.host_rsp = 0x%x"%(self.stack_segs[index]["end"]))
            self.Text_write("@vmcs.host_cr3 = 0x%x"%(self.ptg.tlb_base["start"]))
            self.Comment("#### Set client ####")
            self.Text_write("@vmcs.guest_gdtr_base = 0x%x"%(self.gdt_table_base_pointer["start"])) #FIXME - must point to a tss selector
            if self.vmx_client_mode == "long_mode":
                self.Text_write("@vmcs.guest_cs_sel= &SELECTOR($%s)"%(self.selector_name_cs64_0))
                self.Text_write("@vmcs.guest_ss_sel= &SELECTOR($%s)"%(self.selector_name_ds64_0))
                self.Text_write("@vmcs.guest_ds_sel= &SELECTOR($%s)"%(self.selector_name_ds64_0))
                self.Text_write("@vmcs.guest_tr_sel = &SELECTOR($%s)"%(self.selector_name_ds64_0)) #FIXME - must point to a tss selector
                if self.c_gen:
                    self.Text_write("@vmcs.guest_fs_sel= &SELECTOR($%s)"%(self.selector_name_c_gen_0))
                    self.Text_write("@vmcs.guest_fs_base = 0x%08x"%(self.c_parser.c_code_mem_info[".tbss"]["start"]))
                
            elif self.vmx_client_mode == "compatibility_mode":
                self.Text_write("@vmcs.guest_cs_sel= &SELECTOR($%s)"%(self.selector_name_cs32_0))
                self.Text_write("@vmcs.guest_cs_attr = 0xC09b")
                self.Text_write("@vmcs.guest_ss_sel= &SELECTOR($%s)"%(self.selector_name_ds32_0))
                self.Text_write("@vmcs.guest_ss_attr= 0xC093")
                self.Text_write("@vmcs.guest_ds_sel= &SELECTOR($%s)"%(self.selector_name_ds32_0))
                self.Text_write("@vmcs.guest_ds_attr= 0xC093")
                self.Text_write("@vmcs.guest_es_sel= &SELECTOR($%s)"%(self.selector_name_ds32_0))
                self.Text_write("@vmcs.guest_es_attr= 0xC093")
                self.Text_write("@vmcs.guest_tr_sel = &SELECTOR($%s)"%(self.selector_name_ds32_0)) #FIXME - must point to a tss selector
                if self.c_gen:            
                    self.Text_write("@vmcs.guest_gs_sel= &SELECTOR($%s)"%(self.selector_name_c_gen_0))
                    self.Text_write("@vmcs.guest_fs_sel= &SELECTOR($%s)"%(self.selector_name_ds32_0))
                    self.Text_write("@vmcs.guest_gs_base = 0x%08x"%(self.c_parser.c_code_mem_info[".tbss"]["start"]))       
                else:
                    self.Text_write("@vmcs.guest_gs_sel= &SELECTOR($%s)"%(self.selector_name_ds32_0))
                    self.Text_write("@vmcs.guest_fs_sel= &SELECTOR($%s)"%(self.selector_name_ds32_0))    
                self.Text_write("@vmcs.guest_gs_attr= 0xC093")              
                self.Text_write("@vmcs.guest_fs_attr= 0xC093")
            
            self.Text_write("@vmcs.entry_controls = 0x000053ff")
            self.Text_write("@vmcs.guest_rip = 0x%x"%(self.vmx_guest_entry_0[index]["start"]))
            self.Text_write("@vmcs.guest_rsp = 0x%x"%(self.stack_segs[index]["end"]-0x8))
            self.Text_write("@vmcs.guest_cr3 = 0x%x"%(self.ptg.vmx_tlb_base["start"]))
            self.Text_write("@vmcs.guest_ia32_pat_full = 0x00070406")
            self.Text_write("@vmcs.guest_ia32_pat_high = 0x00070406")

            
    def Set_gdt_table(self,gdt_table_base,c_gen):
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
        if self.mode == "compatibility_mode" :
            self.selector_name_cs_0 = self.selector_name_cs32_0
            self.selector_name_ds_0 = self.selector_name_ds64_0
        elif self.mode == "long_mode":
            self.selector_name_cs_0 = self.selector_name_cs64_0
            self.selector_name_ds_0 = self.selector_name_ds64_0
        elif self.mode == "protect_mode":
            self.selector_name_cs_0 = self.selector_name_cs32_0
            self.selector_name_ds_0 = self.selector_name_ds32_0
        else:
            self.Error_exit("Invalid mode!")
            
        if c_gen:
            self.selector_value_c_gen_0 = 0x5
            if self.vmx_client_mode == "long_mode":
                self.c_parser.selector_name_c_gen_0 = "c_gen_64"
                self.selector_name_c_gen_0 = self.c_parser.selector_name_c_gen_0
                self.Vars_write(self.c_parser.selector_name_c_gen_0,self.selector_value_c_gen_0)
                self.Text_write("@gdt[$%s].type = 0x3"%(self.c_parser.selector_name_c_gen_0))
                self.Text_write("@gdt[$%s].l = 0x1"%(self.c_parser.selector_name_c_gen_0))
                self.Text_write("@gdt[$%s].base = 0x%08x"%(self.c_parser.selector_name_c_gen_0,self.c_parser.c_code_mem_info[".tbss"]["start"]))
            else:
                self.c_parser.selector_name_c_gen_0 = "c_gen_32"
                self.selector_name_c_gen_0 = self.c_parser.selector_name_c_gen_0
                self.Vars_write(self.c_parser.selector_name_c_gen_0,self.selector_value_c_gen_0)
                self.Text_write("@gdt[$%s].type = 0x3"%(self.c_parser.selector_name_c_gen_0))
                self.Text_write("@gdt[$%s].db = 0x1"%(self.c_parser.selector_name_c_gen_0))
                self.Text_write("@gdt[$%s].base = 0x%08x"%(self.c_parser.selector_name_c_gen_0,self.c_parser.c_code_mem_info[".tbss"]["start"]))
        
    def Gen_vmx_page_addr(self):
        self.ptg.Gen_ept_2M_addr()
        self.ptg.Gen_vmx_page_2M_addr()


    def Write_vmx_page(self):
        self.ptg.Write_vmx_page_2M()
        self.ptg.Write_ept_2M()





 
