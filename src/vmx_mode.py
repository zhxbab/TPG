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
        #self.multi_ept = 0
        
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
            vmxon = self.mpg.Apply_mem(0x2000,0x1000,start=0x1000000,end=0x8000000,name="vmxon_%d"%(i)) #vmxon is most 0x1000
            vmxon_pointer = self.mpg.Apply_mem(0x8,16,start=0x1000000,end=0x8000000,name="vmxon_pointer_%d"%(i))
            vmcs = self.mpg.Apply_mem(0x2000,0x1000,start=0x1000000,end=0x8000000,name="vmcs_%d"%(i))
            vmcs_pointer = self.mpg.Apply_mem(0x8,16,start=0x1000000,end=0x8000000,name="vmcs_pointer_%d"%(i))
            vmx_guest_entry_0 = self.mpg.Apply_mem(0x10000,16,start=0x1000000,end=0x8000000,name="vmx_guest_entry_0_%d"%(i))
            vmcs_data = self.mpg.Apply_mem(0x2000,0x1000,start=0x1000000,end=0x8000000,name="vmcs_data_%d"%(i))# because some field has two id, so it is twice of vmcs
            vmcs_initial_code = self.mpg.Apply_mem(0x1000,0x1000,start=0x1000000,end=0x8000000,name="vmcs_initial_code_%d"%(i))
            vmx_exit_addr = self.mpg.Apply_mem(0x200,0x20,start=0x1000000,end=0x8000000,name="vmx_exit_addr_%d"%(i))
            self.vmxon.append(vmxon)
            self.vmxon_pointer.append(vmxon_pointer)
            self.vmcs.append(vmcs)
            self.vmcs_pointer.append(vmcs_pointer)
            self.vmx_guest_entry_0.append(vmx_guest_entry_0)
            self.vmcs_data.append(vmcs_data)
            self.vmcs_initial_code.append(vmcs_initial_code)
            self.vmx_exit_addr.append(vmx_exit_addr)
            del vmxon,vmxon_pointer,vmcs,vmcs_pointer,vmx_guest_entry_0,vmcs_data,vmcs_initial_code,vmx_exit_addr
        
        
        for index in range(0,self.threads):
            self.Text_write("org 0x%x"%(self.vmcs_data[index]["start"]))
            self.Comment("#### Set host ####")
            vmcs_name = "vmcs_%d"%(index)
            self.Text_write("@%s = new std::vmcs::data"%(vmcs_name))
            self.Text_write("@%s.host_gdtr_base = 0x%x"%(vmcs_name,self.gdt_table_base_pointer["start"]))
            self.Text_write("@%s.host_cs_sel = &SELECTOR($%s)"%(vmcs_name,self.selector_name_cs_0))
            self.Text_write("@%s.host_ss_sel = &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds_0))
            self.Text_write("@%s.host_ds_sel = &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds_0))
            self.Text_write("@%s.host_tr_sel = &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds_0)) #FIXME - must point to a tss selector
            self.Text_write("@%s.virtual_apic_page_addr_full = 0x%x"%(vmcs_name,self.ptg.vmx_tlb_base["start"]))
            if self.multi_ept:
                self.Text_write("@%s.ept_pointer_full = 0x%x"%(vmcs_name,self.ptg.ept_tlb_base[index]["start"]))# $std_vmcs_initialize_guest_vmcs will handle this address(or 0x1E)
            else:
                self.Text_write("@%s.ept_pointer_full = 0x%x"%(vmcs_name,self.ptg.ept_tlb_base["start"]))# $std_vmcs_initialize_guest_vmcs will handle this address(or 0x1E)                
            self.Text_write("@%s.host_rip = 0x%x"%(vmcs_name,self.vmx_exit_addr[index]["start"]))
            self.Text_write("@%s.host_rsp = 0x%x"%(vmcs_name,self.stack_segs[index]["end"]))
            self.Text_write("@%s.host_cr3 = 0x%x"%(vmcs_name,self.ptg.tlb_base["start"]))
            self.Comment("#### Set client ####")
            self.Text_write("@%s.guest_gdtr_base = 0x%x"%(vmcs_name,self.gdt_table_base_pointer["start"])) #FIXME - must point to a tss selector
            if self.vmx_client_mode == "long_mode":
                self.Text_write("@%s.guest_cs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_cs64_0))
                self.Text_write("@%s.guest_ss_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds64_0))
                self.Text_write("@%s.guest_ds_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds64_0))
                self.Text_write("@%s.guest_tr_sel = &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds64_0)) #FIXME - must point to a tss selector
                if self.c_gen:
                    self.Text_write("@%s.guest_fs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_c_gen_0))
                    self.Text_write("@%s.guest_fs_base = 0x%08x"%(vmcs_name,self.c_parser.c_code_mem_info[".tbss"]["start"]))
                self.Text_write("@%s.entry_controls = 0x000053ff"%(vmcs_name))
                
            elif self.vmx_client_mode == "compatibility_mode":
                self.Text_write("@%s.guest_cs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_cs32_0))
                self.Text_write("@%s.guest_cs_attr = 0xC09b"%(vmcs_name))
                self.Text_write("@%s.guest_ss_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                self.Text_write("@%s.guest_ss_attr= 0xC093"%(vmcs_name))
                self.Text_write("@%s.guest_ds_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                self.Text_write("@%s.guest_ds_attr= 0xC093"%(vmcs_name))
                self.Text_write("@%s.guest_es_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                self.Text_write("@%s.guest_es_attr= 0xC093"%(vmcs_name))
                self.Text_write("@%s.guest_tr_sel = &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0)) #FIXME - must point to a tss selector
                if self.c_gen:            
                    self.Text_write("@%s.guest_gs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_c_gen_0))
                    self.Text_write("@%s.guest_fs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                    self.Text_write("@%s.guest_gs_base = 0x%08x"%(vmcs_name,self.c_parser.c_code_mem_info[".tbss"]["start"]))       
                else:
                    self.Text_write("@%s.guest_gs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                    self.Text_write("@%s.guest_fs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))    
                self.Text_write("@%s.guest_gs_attr= 0xC093"%(vmcs_name))              
                self.Text_write("@%s.guest_fs_attr= 0xC093"%(vmcs_name))
                self.Text_write("@%s.entry_controls = 0x000053ff"%(vmcs_name))
                
            elif self.vmx_client_mode == "protect_mode":
                self.Text_write("@%s.guest_cs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_cs32_0))
                self.Text_write("@%s.guest_cs_attr = 0xC09b"%(vmcs_name))
                self.Text_write("@%s.guest_ss_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                self.Text_write("@%s.guest_ss_attr= 0xC093"%(vmcs_name))
                self.Text_write("@%s.guest_ds_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                self.Text_write("@%s.guest_ds_attr= 0xC093"%(vmcs_name))
                self.Text_write("@%s.guest_es_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                self.Text_write("@%s.guest_es_attr= 0xC093"%(vmcs_name))
                self.Text_write("@%s.guest_tr_sel = &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0)) #FIXME - must point to a tss selector
                if self.c_gen:            
                    self.Text_write("@%s.guest_gs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_c_gen_0))
                    self.Text_write("@%s.guest_fs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                    self.Text_write("@%s.guest_gs_base = 0x%08x"%(vmcs_name,self.c_parser.c_code_mem_info[".tbss"]["start"]))       
                else:
                    self.Text_write("@%s.guest_gs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))
                    self.Text_write("@%s.guest_fs_sel= &SELECTOR($%s)"%(vmcs_name,self.selector_name_ds32_0))    
                self.Text_write("@%s.guest_gs_attr= 0xC093"%(vmcs_name))              
                self.Text_write("@%s.guest_fs_attr= 0xC093"%(vmcs_name))
                self.Text_write("@%s.entry_controls = 0x000051ff"%(vmcs_name))
                if self.ptg.vmx_client_pae == False:
                    self.Text_write("@%s.guest_cr4 = 0x00042690"%(vmcs_name))                    
                else:
                    self.Text_write("@%s.guest_cr4 = 0x000426B0"%(vmcs_name))
                    self.Text_write("@%s.guest_ia32_pdpte0_full = 0x%05x001"%(vmcs_name,self.ptg.vmx_pae_pde_0["start"]/self.ptg.vmx_pae_pde_0["size"]))
                    self.Text_write("@%s.guest_ia32_pdpte1_full = 0x%05x001"%(vmcs_name,self.ptg.vmx_pae_pde_1["start"]/self.ptg.vmx_pae_pde_0["size"])) 
                    self.Text_write("@%s.guest_ia32_pdpte2_full = 0x%05x001"%(vmcs_name,self.ptg.vmx_pae_pde_2["start"]/self.ptg.vmx_pae_pde_0["size"])) 
                    self.Text_write("@%s.guest_ia32_pdpte3_full = 0x%05x001"%(vmcs_name,self.ptg.vmx_pae_pde_3["start"]/self.ptg.vmx_pae_pde_0["size"]))         

            self.Text_write("@%s.guest_rip = 0x%x"%(vmcs_name,self.vmx_guest_entry_0[index]["start"]))
            self.Text_write("@%s.guest_rsp = 0x%x"%(vmcs_name,self.stack_segs[index]["end"]-0x8))
            self.Text_write("@%s.guest_cr3 = 0x%x"%(vmcs_name,self.ptg.vmx_tlb_base["start"]))
            self.Text_write("@%s.guest_ia32_pat_full = 0x00070406"%(vmcs_name))
            self.Text_write("@%s.guest_ia32_pat_high = 0x00070406"%(vmcs_name))
            self.Text_write("@%s.proc_vm_exec_controls2 = 0x22"%(vmcs_name))
            self.Text_write("@%s.vpid = %d"%(vmcs_name,index+1))         
            #del vmcs_name
    def Exit_code_addr(self,thread):
        self.Text_write("org 0x%x"%(self.vmx_exit_addr[thread]["start"]))
        
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
        if self.vmx_client_mode == "protect_mode":
            self.ptg.Gen_vmx_page_4M_addr()
        else:
            self.ptg.Gen_vmx_page_2M_addr()            

    def Write_vmx_page(self):
        if self.vmx_client_mode == "protect_mode":        
            self.ptg.Write_vmx_page_4M()
        else:
            self.ptg.Write_vmx_page_2M()            
        self.ptg.Write_ept_2M()


    def Set_user_code_stack(self,c_gen):
        self.Comment("###########################Thread Info######################")
        stack_align = 0x100
        self.stack_segs = []
        self.user_code_segs = []
        self.thread_info_pointer = self.mpg.Apply_mem(0x100,16,start=0x0,end=0x10000,name="thread_info_pointer")
        self.ptg.thread_info_pointer = self.thread_info_pointer
        self.Text_write("org 0x%x"%(self.thread_info_pointer["start"]))
        self.Text_write("@%s = new std::thread_info[%d]"%(self.thread_info_pointer["name"],8))#support 8 threads
        for i in range(0,self.threads):
            if c_gen == 0x0:
                self.stack_seg = self.mpg.Apply_mem(0x40000,stack_align,start=0xB00000,end=0x1000000,name="stack_seg_T%d"%(i))
                self.user_code_seg = self.mpg.Apply_mem(0x800000,stack_align,start=0x1000000,end=0x40000000,name="user_code_seg_T%d"%(i))
                #because if enable multi page, above addr 0x40000000 is different for different core 
            else:
                if self.vmx_client_mode == "long_mode":
                    if i == 0:
                        for k in range(0,self.threads):
                            if k != 0:
                                self.mpg.Apply_fix_mem("csmith_code_%d"%(k),0x400000+128*0x200000*k,0x400000)# 0x400000 and 0x600000
                else:
                    if i == 0:
                        for k in range(0,self.threads):
                            if k != 0:
                                self.mpg.Apply_fix_mem("csmith_code_%d"%(k),0x8000000+128*k*0x400000,0x400000)                    
                self.stack_seg = self.mpg.Apply_mem(0x40000,stack_align,start=0xB00000,end=0x1000000,name="stack_seg_T%d"%(i))
                self.user_code_seg = self.mpg.Apply_mem(0x800000,stack_align,start=0x20000000,end=0x40000000,name="user_code_seg_T%d"%(i))
#                self.Comment("##########Initial stack###########")
#                self.Text_write("org 0x%08x"%(self.stack_seg["start"]))
#                for j in range(0,0x100000,8):
#                    self.Text_write("dq 0x0000000000000000")
#                self.Comment("##########Initial stack end###########")
            if self.mode == "long_mode":
                self.stack_seg["end"] = self.stack_seg["start"]+self.stack_seg["size"]-stack_align+0x8
            else:
                self.stack_seg["end"] = self.stack_seg["start"]+self.stack_seg["size"]-stack_align+0x4
            # because need to execute call user_code, esp will -4,
            #so in there resever some space
            self.stack_segs.append(self.stack_seg)
            self.user_code_segs.append(self.user_code_seg)
            if self.intel:
                intel_id = i * 2
                self.Text_write("@%s[%d].stack = 0x%016x"%(self.thread_info_pointer["name"],intel_id,self.stack_seg["end"]))
                self.Text_write("@%s[%d].code = 0x%016x"%(self.thread_info_pointer["name"],intel_id,self.user_code_seg["start"]))
            else:
                self.Text_write("@%s[%d].stack = 0x%016x"%(self.thread_info_pointer["name"],i,self.stack_seg["end"]))
                self.Text_write("@%s[%d].code = 0x%016x"%(self.thread_info_pointer["name"],i,self.user_code_seg["start"]))


 
