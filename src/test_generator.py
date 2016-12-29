#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' test_generator module '
__author__ = 'Ken Zhao'
##########################################################
# test_generator module is used to merge differnet classes
# and generate the test vectors
##########################################################
import sys, os, signal, random, subprocess
from logging import info, error, debug, warning, critical
from args import Args
from util import Util
from mem import Mem
from mode import Mode
from osystem import Osystem
from instruction import Instr
from page import Page
from simcmd import Simcmd
from c_parser import C_parser
from interrupt import Interrupt
class Test_generator(Args,Util):
    def __init__(self,args):
        signal.signal(signal.SIGINT,self.Sigint_handler)
        Args.__init__(self,args)
        self.total_threads = 8
        self.threads_flag = "fix"
        self.spin_lock_num = 0x0 
        self.apic_id_list = []
        self.apic_id_list_all = []
        
    def Create_dir(self):
        self.avp_dir_seed = random.randint(1,0xFFFF)
        self.avp_dir_name = "%s_%sT_%s_%d"%(self.realbin_name,self.threads,self.mode,self.avp_dir_seed)
        cmd = "mkdir %s/%s"%(self.realbin_path,self.avp_dir_name)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        self.avp_dir_path = os.path.join(self.realbin_path,self.avp_dir_name)
        self.cnsim_fail_dir = os.path.join(self.avp_dir_path,"cnsim_fail")
        self.fail_dir =  os.path.join(self.avp_dir_path,"fail")
        cmd = "mkdir %s"%(self.cnsim_fail_dir)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        cmd = "mkdir %s"%(self.fail_dir)
        info("create dir cmd is %s"%(cmd))
        os.system(cmd)
        self.Create_global_info()
        
    def Set_total_threads(self,total_thread):
        self.total_threads = total_thread
        
    def Fix_threads(self,threads):
        self.threads = threads
        self.apic_id_list_all = self.threads
        if self.threads > 1 and self.c_gen==1:
            self.multi_page=1
            
    def Use_random_ap(self):
        self.threads_flag = "random"
        self.apic_id_list = []
        if self.threads > 1:
            if self.threads > self.total_threads:
                self.Error_exit("current thread num %d is greater than total thread num %d"%(self.threads,self.total_threads))
            else:
                thread_list = range(1,self.total_threads)
                for i in range(1,self.threads):
                    index = random.randint(0,self.total_threads-1-i)
                    self.apic_id_list.append(thread_list[index])
                    del thread_list[index]
            info("ap is %s"%(self.apic_id_list))
        self.apic_id_list_all = [0]+self.apic_id_list 
            
    def Create_global_info(self):
        self.asm_list = []
        self.inc_path = "%s/include"%(self.tpg_path)
        self.bin_path = "%s/bin"%(self.tpg_path)
        self.ic_list = []
        self.fail_list = []
        self.pclmsi_list_file = "%s/%s_pclmsi.list"%(self.avp_dir_path,self.avp_dir_name)
        self.mpg = Mem()
        self.c_parser = None
        #info(self.avp_dir_path)
    def Create_asm(self,index=0x0):
        self.asm_name = "%s_%s_%sT_%s_%d.asm"%(self.realbin_name,index,self.threads,self.mode,self.seed)
        self.page_file_name = "%s_%s_%sT_%s_%d.page"%(self.realbin_name,index,self.threads,self.mode,self.seed)
        self.asm_path = os.path.join(self.avp_dir_path,self.asm_name)
        self.page_file = os.path.join(self.avp_dir_path,self.page_file_name)
        self.asm_file = open(self.asm_path,"w")
        self.asm_list.append(self.asm_path)
        self.osystem.asm_file = self.asm_file
        self.ptg.page_file = self.page_file
        self.ptg.asm_file = self.asm_file
        self.mpg.asm_file = self.asm_file
        self.simcmd.asm_file = self.asm_file
        self.interrupt.asm_file = self.asm_file
        self.Text_write("include \"%s/std.inc\""%(self.inc_path))
        self.hlt_code = self.mpg.Apply_mem(0x200,16,start=0x10000,end=0xA0000,name="hlt_code")#below 0x10000 has problem for mem 0xF4F4

        
    def Gen_mode_code(self):
        self.mode_code = Mode(self.mpg, self.instr_manager, self.ptg, self.threads, self.simcmd, self.intel, self.interrupt,self.c_parser)
        self.mode_code.asm_file = self.asm_file
        self.ptg.c_gen = self.c_gen
        self.ptg.intel = self.intel
        self.ptg.mode = self.mode
        self.ptg.pae = self.pae
        self.mode_code.osystem = self.osystem
        if self.c_gen:
            self.c_parser.multi_page = self.multi_page
            #info("c plus is %d"%(self.c_parser.c_plus))
        self.ptg.multi_page = self.multi_page
        self.mode_code.pae = self.pae
        self.mode_code.threads_flag = self.threads_flag
        self.mode_code.apic_id_list = self.apic_id_list
        [self.stack_segs,self.user_code_segs] = self.mode_code.Mode_code(self.mode,self.c_gen,self.disable_avx,self.disable_pcid)

    def Gen_cnsim_param(self):
        if self.intel:
            intel_cnsim_cmd = "-apic-id-increment 2 "
        else:
            intel_cnsim_cmd = " "
        cnsim_param_pclmsi = " "
        cnsim_param_normal = "-ma %s  -va -no-mask-page -trait-change %s "%(self.very_short_num,self.very_short_cmd)
        cnsim_param_mem = "-mem 0xF4 "
        if self.total_threads != self.threads and self.threads_flag == "random":
            cnsim_param_thread = "-threads %d "%(self.total_threads)
        else:
            cnsim_param_thread = "-threads %d "%(self.threads)            
        #-no-tbdm-warnings
        # remove no stack, -no-apic-intr -all-mem -addr-chk -memread-chk 
        self.cnsim_param = cnsim_param_pclmsi + cnsim_param_normal + cnsim_param_mem + cnsim_param_thread + intel_cnsim_cmd
        
        
    def Gen_hlt_code(self,thread_num):
        #print("thread_num is %d"%(thread_num))
        if thread_num == 0:
            self.Text_write("jmp $%s"%(self.hlt_code["name"]))
            self.Text_write("org 0x%x"%(self.hlt_code["start"]))
            self.Tag_write(self.hlt_code["name"])
            self.Text_write("hlt")
        elif 0 < thread_num < 8:
            self.Text_write("jmp $%s"%(self.hlt_code["name"]))
        else:
            self.Error_exit("Invalid thread num!")
        self.instr_manager.Add_instr(thread_num,2)
        
    def Gen_sim_cmd(self,thread_num):
        self.simcmd.Simcmd_write(thread_num)
        
    def Gen_ctrl_cmd(self):
        self.simcmd.Ctrlcmd_write()
        
    def Reset_asm(self):
        self.mpg.Reset_mem()
        self.instr_manager = Instr(self.total_threads)
        self.osystem = Osystem(self.threads,self.instr_manager)
        self.ptg = Page(self.page_mode,self.tpg_path,self.mpg,self.instr_manager,self.threads)
        self.simcmd = Simcmd(self.threads)
        self.spin_lock_num = 0x0
        self.interrupt = Interrupt(self.mode,self.mpg)
        
    def Gen_del_file(self):
        self.del_file_name = "%s.del"%(self.avp_dir_path)
        self.del_file = open(self.del_file_name,"w")
        self.del_file.write("rm -rf %s\n"%(self.avp_dir_path))
        self.del_file.close()
        os.system("chmod 777 %s"%(self.del_file_name))
    
    def Gen_vector(self):
        self.Gen_cnsim_param()
        self.asm_file.close()
        os.chdir(self.avp_dir_path)
        asm_file = os.path.join(self.avp_dir_path,self.asm_name)
        rasm_cmd = "%s/rasm -raw %s"%(self.bin_path,asm_file)
        avp_file = asm_file.replace(".asm",".avp")
        self.vector_base_name = asm_file.replace(".asm","")
        rasm_p = subprocess.Popen(rasm_cmd,stdout=None, stderr=None, shell=True)
        ret = rasm_p.poll()
        while ret == None:
            ret = rasm_p.poll()
        cnsim_cmd = "%s/cnsim %s %s"%(self.bin_path,self.cnsim_param,avp_file)     
        info(cnsim_cmd)
        cnsim_p = subprocess.Popen(cnsim_cmd,stdout=None, stderr=None, shell=True)
        ret = cnsim_p.poll()
        while ret == None:
            ret = cnsim_p.poll()
        if ret != 0x0:
            error("Gen vector fail, Please check!")
            self.fail_list.append(avp_file)
            self.ic_file = avp_file.replace(".avp",".ic")
            if self.c_gen:
                info("cp %s.* %s"%(os.path.join(self.avp_dir_path,self.c_parser.base_name),self.cnsim_fail_dir))
                os.system("cp %s* %s"%(os.path.join(self.avp_dir_path,self.c_parser.base_name),self.cnsim_fail_dir))
                info("cp %s.* %s"%(os.path.join(self.avp_dir_path,self.vector_base_name),self.cnsim_fail_dir))
                os.system("cp %s.* %s"%(os.path.join(self.avp_dir_path,self.vector_base_name),self.cnsim_fail_dir))
            else:
                info("cp %s.* %s"%(os.path.join(self.avp_dir_path,self.vector_base_name),self.cnsim_fail_dir))
                os.system("cp %s.* %s"%(os.path.join(self.avp_dir_path,self.vector_base_name),self.cnsim_fail_dir))   
        else:
            self.ic_file = avp_file.replace(".avp",".ic")
            gzip_cmd = "gzip %s"%(self.ic_file)
            info(gzip_cmd)
            os.system(gzip_cmd)
            self.ic_file = "%s.gz"%(self.ic_file)
            self.ic_list.append(self.ic_file)
        os.chdir(self.realbin_path)
        
    def Gen_pclmsi_file_list(self):
        pclmsi_list = open(self.pclmsi_list_file,"w")
        for ic_file in self.ic_list:
            pclmsi_list.write("+load:%s +rerun_times:100 +ignore_all_checks:1\n"%(ic_file))
        for fail_ic in self.fail_list:
            info("cnsim fail vector is %s"%(fail_ic))
        info("%s Done"%(self.pclmsi_list_file))
        pclmsi_list.close()
#-pclmsi                                             test for PCLMSI compatibility and expose errors
#-pclmsi-limit                          0x12345678   Change the memory limit for pclmsi checks (0x200000000)
#-pclsmi-allow_io                                    Allow any I/O operation for PCLSMI tests
#-wc/(-no-wc)                                        check all writes for results cards
#(-uchk)/-no-uchk                                    disable check for undefined results
#(-port-chk)/-no-port-chk                            checking for undefined I/O addresses
#-no-ma                                              don't fail on max instruction count
#-no-warnings/(-warnings)                            disable/enable warnings
#(-warn-once)/-no-warn-once                          only issue one warning per warning type
#-no-shutdown                                        fail AVP on shutdown
#(-addr-chk)/-no-addr-chk                            disable check for undefined addresses
#-warn-addr-chk/(-no-warn-addr-chk)                  warning instead of fail on undefined address check
#-memread-chk/(-no-memread-chk)                      enable check for undefined memory reads
#(-cr)/-no-cr                                        check final results (reports first mismatch)
#-cr-full/(-no-cr-full)                              check final results (reports all mismatches
#-intr                                  #,#,(r|p)    intr support
#-nexm                                               check for non-existent memory accesses
#-chk-dup-tlb-tags/(-no-chk-dup-tlb-tag              check for duplicate tags in TLBs
#-case-g/(-no-case-g)                                warn on paging case G
#-thread-sync                                        Add thread pause directives for system model on shared memory accesses
#-add-shared-mask                                    add masking for all shared memory locations
#-add-shared-locked-mask                             add masking for all locked shared memory locations
#(-vmem)/-no-vmem                                    include virtual memory comments
#-all-mem/(-no-all-mem)                              output all initial memory cards
#-mem                                   0x12345678   default value for uninitialized memory
#-mem-code                              0x12345678   default value for uninitialized code
#-mem-data                              0x12345678   default value for uninitialized data
#(-wp)/-no-wp                                        enable/disable write protect memory
#-trait-change/(-no-trait-change)                    Don't allow trait change WB->WC
#-use-sim-mask                                       use //sim: memory masking in results
#-check-global-pages/(-no-check-global-              global pages must maintain consistant mapping
#-inject-page-fault                     12345678     Inject page faults randomly by percentage
#-mask-page/(-no-mask-page)                          mask page table access & dirty bits (CN bringup only)
    
    def Spin_lock_create(self,thread,flag=0):
      spin_lock = self.mpg.Apply_mem(0x4,0x4,start=0x1000000,end=0xB0000000,name="spin_lock")
      self.simcmd.Add_sim_cmd("at $y%d >= 1 set memory 0x%08x to 0x00000000"%(thread,spin_lock["start"]),thread)
      if flag == 0:
          self.simcmd.Add_tbdm_cmd("at instruction 1 set memory 0x%08x to 0x00000000"%(spin_lock["start"]),thread)
      else:
          self.simcmd.Add_tbdm_cmd("and set memory 0x%08x to 0x00000000"%(spin_lock["start"]),thread)
      #self.simcmd.Add_sim_cmd("at $y%d >= 1 set register RAX to 0x00000000:0x00000000"%(thread),thread)
      spin_lock["num"] = self.spin_lock_num
      spin_lock["ctrl_id"] = [0]*8
      self.spin_lock_num += 1
      return spin_lock
      #//sim: at $y0 >= 1 set memory 0x09ac8008 to 0x00000000:0x00000000
    def Sync_spin_lock(self,spin_lock,thread,unlock_thread=0x0):
      self.simcmd.Add_sim_cmd("at $y%d >= %d disable intermediate checking"%(thread,self.instr_manager.Get_instr(thread)+1),thread)
      self.Text_write("db 0xF0")
      self.Instr_write("inc dword [0x%08x]"%(spin_lock["start"]),thread)
      self.Tag_write("spin_lock_T%d_%d"%(thread,spin_lock["num"]))
      self.Instr_write("cmp dword [0x%08x],0x%x"%(spin_lock["start"],self.threads),thread)
      if unlock_thread == thread:
          #self.simcmd.Add_sim_cmd("at $y%d >= %d set memory 0x%08x to 0x00000004"%(thread,self.instr_manager.Get_instr(thread),spin_lock["start"]),thread)
          for i in self.apic_id_list_all:
              if i != unlock_thread:
                  spin_lock["ctrl_id"][i] = self.Sync_thread(i)
              else:
                  pass
      else:
          instr_num = self.instr_manager.Get_instr(thread)-self.simcmd.current_instr[thread]
          self.simcmd.Change_ctrl_cmd(spin_lock["ctrl_id"][thread],instr_num)
          self.simcmd.current_instr[thread] = self.instr_manager.Get_instr(thread)
          self.instr_manager.Set_instr(self.instr_manager.Get_instr(thread)+2,thread) # +2 is for core 1, 2, 3 to sync instr num
      self.Instr_write("jne $spin_lock_T%d_%d"%(thread,spin_lock["num"]),thread)
      self.simcmd.Add_sim_cmd("at $y%d >= %d enable intermediate checking"%(thread,self.instr_manager.Get_instr(thread)+1),thread)

    def Check_instr_num_all(self,apic_id_list_all=None):
        if apic_id_list_all == None:
            for i in range(0,self.threads):
                self.Check_instr_num(i)
        else:
            for i in apic_id_list_all:
                self.Check_instr_num(i)
                
    def Check_instr_num(self,thread):
        info("thread %d current instr num is %d"%(thread,self.instr_manager.Get_instr(thread)))    
    
    
    def Sync_threads(self,apic_id_list_all=None):
        if apic_id_list_all == None:
            for i in range(0,self.threads):
                self.Sync_thread(i)
        else:
            for i in apic_id_list_all:
                self.Sync_thread(i)            
            
    def Sync_thread(self,thread):
        #if self.instr_manager.Get_instr(thread)-self.simcmd.current_instr[thread] > 0:
        ctrl_id = self.simcmd.Add_ctrl_cmd(thread,self.instr_manager.Get_instr(thread)-self.simcmd.current_instr[thread])
        self.simcmd.current_instr[thread] = self.instr_manager.Get_instr(thread)
        return ctrl_id
    
    def Load_asm_code(self,thread, num):
        self.c_parser.Load_c_asm(thread,self.hlt_code,num)
        if self.multi_page:
            self.c_parser.Parse_c_asm(thread)
        elif self.multi_page == 0 and thread == 0:
            self.c_parser.Parse_c_asm(thread)
        else:
            pass            
            
    def Vmx_load_asm_code(self,thread):
        self.c_parser.Vmx_load_c_asm(thread)
     
    def Updata_interrupt(self,index,handler):
        self.interrupt.Update_interrupt_handler(index,handler)
        
    def Initial_interrupt(self):
        self.int_handler_base = self.mpg.Apply_mem(0x100000,16,start=0xa00000,end=0x1000000,name="int_handler_base")
        self.int_handler_record_base = self.mpg.Apply_mem(0x800,16,start=0x0,end=0xA0000,name="int_handler_record_base")
        self.interrupt.Initial_interrupt_handler(self.int_handler_base,self.int_handler_record_base)
        self.osystem.int_handler["base"] = self.int_handler_base["start"]
        self.osystem.int_handler["size"] = self.int_handler_base["size"]
           
    def Start_user_code(self,thread):
        self.Comment("##Usr code")
        if self.multi_page:
            self.Text_write("PAGING $tlb_pointer_%d"%(thread))
        self.Text_write("org 0x%x"%(self.user_code_segs[thread]["start"]))
        if self.multi_page:
            self.Instr_write("mov ebx,[eax+&@%s]"%(self.ptg.page_info_pointer["name"])) # +2
            self.Instr_write("mov cr3,ebx")
        self.Tag_write(self.user_code_segs[thread]["name"])
        if self.mode == "long_mode":
            self.Text_write("use 64")
        else:
            self.Text_write("use 32")
                   
    def Remove_dir(self):
        if not os.listdir(self.cnsim_fail_dir):
            rmcmd = "rm -rf %s"%(self.avp_dir_path)
            info(rmcmd)
            os.system(rmcmd)
            os.system("rm -f %s.del"%(self.avp_dir_path))
            
    def Init_PMC(self,thread):
        #### set PMC0
        self.Instr_write("mov ecx,0x186",thread)
        self.Instr_write("rdmsr",thread)
        self.Instr_write("or eax,0x0003003C",thread)
        self.Instr_write("and eax,0x0003003C",thread)
        self.Instr_write("wrmsr",thread)
        ####enable global ctrl       
        self.Instr_write("mov ecx,0x38f",thread)
        self.Instr_write("rdmsr",thread)
        self.Instr_write("or eax,0x1",thread)
        self.Instr_write("wrmsr",thread)
        
    def Enable_PMC0(self,thread):
        self.Instr_write("mov ecx,0x186",thread)
        self.Instr_write("rdmsr",thread)
        self.Instr_write("or eax,0x400000",thread)
        self.Instr_write("wrmsr",thread)
        
    def Disable_PMC0(self,thread):
        self.Instr_write("mov ecx,0x186",thread)
        self.Instr_write("rdmsr",thread)
        self.Instr_write("or eax,0xBfffff",thread)
        self.Instr_write("wrmsr",thread)
        
    def Read_PMC0(self,addr,thread):
        self.Instr_write("mfence",thread)
        self.Instr_write("mov eax,0x0",thread)
        #self.Instr_write("cpuid")
        self.Instr_write("mov ecx,0x0",thread)
        self.Instr_write("rdpmc",thread)
        self.Instr_write("mov [%s],eax"%(addr),thread)
        self.Instr_write("mov [%s+0x4],edx"%(addr),thread)
        self.Instr_write("mov eax,0x0",thread)
        self.Instr_write("mov edx,0x0",thread)
        
    def Set_mode(self,mode,threads,force_disable_multi_page = 0):
        if mode == "protect_mode":
            self.page_mode = "4MB"
        else:
            self.page_mode = "2MB"
        self.mode = mode
        if threads == 1:
            self.multi_page = 0
        else:
            if force_disable_multi_page == 1:
                self.multi_page = 0
            elif self.c_gen == 1 and threads > 1:
                self.multi_page = 1
            else:
                self.multi_page = 0
                
    def Check_fail_dir(self):
        if os.getenv("LOCATION_CVREG_VECTOR") == None:
            error("Not env para LOCATION_CVREG_VECTOR")
            sys.exit(0)
            
    def Enable_apic(self,thread):
        self.Instr_write("mov ecx,0x1b",thread)
        self.Instr_write("rdmsr",thread)
        self.Instr_write("bts eax,11",thread)
        self.Instr_write("wrmsr",thread)
        self.Instr_write("mov esi, 0xfee000f0",thread)
        self.Instr_write("mov eax,[esi]",thread)
        self.Instr_write("bts eax,8",thread)
        self.Instr_write("mov ds:[esi],eax",thread)
        
    def Set_PMC_vector(self,thread,vector):
        self.Instr_write("mov esi,0xfee00340",thread)
        self.Instr_write("mov [esi],0x000000%s"%(vector),thread)
        self.Instr_write("mov esi,0xfee00080",thread)
        self.Instr_write("xor eax,eax",thread)
        self.Instr_write("mov [esi],eax",thread)
        self.Instr_write("sti",thread)
        
    def PXP_PMC_setting(self,thread):
        self.Msr_Write(0x38f,thread,eax=0,edx=0)
        self.Msr_Write(0x390,thread,eax=7,edx=7)
        self.Msr_Write(0x38d,thread,eax=0,edx=0)
        self.Msr_Write(0x309,thread,eax=0,edx=0)
        self.Msr_Write(0x30a,thread,eax=0,edx=0)
        self.Msr_Write(0x30b,thread,eax=0,edx=0)
        self.Msr_Write(0x38d,thread,eax=0x333,edx=0)
        self.Msr_Write(0x186,thread,eax=0x0,edx=0)
        self.Msr_Write(0x187,thread,eax=0x0,edx=0)
        self.Msr_Write(0x188,thread,eax=0x0,edx=0)
        self.Msr_Write(0xC2,thread,eax=0x0,edx=0)
        self.Msr_Write(0xC3,thread,eax=0x0,edx=0)
        self.Instr_write("mov eax, 0xFFFFFFFF",thread)
        self.Instr_write("sub eax, 0x2625A00",thread)
        self.Instr_write("mov ecx,0xC1",thread)
        self.Instr_write("wrmsr",thread)
        self.Msr_Write(0x186,thread,eax=0x005300C0,edx=0)
        self.Msr_Write(0x186,thread,eax=0x00430001,edx=0)
        self.Msr_Write(0x38f,thread,eax=0x3,edx=0x7)
        self.Instr_write("mov eax, 0xa5a5a5a5",thread)
        self.Instr_write("out 0x80, eax",thread)
        
    def Report_PMC(self,pmc_addr,thread):
        self.Instr_write("mov eax, [0x%x]"%(pmc_addr["start"]),thread)
        self.Instr_write("mov ebx, [0x%x]"%(pmc_addr["start"]+0x4),thread)        
        self.Instr_write("mov ecx, [0x%x]"%(pmc_addr["start"]+0x8),thread)
        self.Instr_write("mov edx, [0x%x]"%(pmc_addr["start"]+0xC),thread)        
        self.Instr_write("sub ecx,eax",thread)
        self.Instr_write("sub edx,ebx",thread)
        self.Instr_write("mov [0x%x], ecx"%(pmc_addr["start"]+0x10),thread)
        self.Instr_write("mov [0x%x], edx"%(pmc_addr["start"]+0x14),thread)
        self.Instr_write("mov dword ptr [0x%x], 0x0"%(pmc_addr["start"]),thread)
        self.Instr_write("mov dword ptr [0x%x], 0x0"%(pmc_addr["start"]+0x8),thread)
        
    def Vmread_all(self,vmcs,thread):
        self.Vmread_16bit_guest_state(vmcs,thread)
        
        
    def Vmread_16bit_guest_state(self,vmcs,thread):
        self.Text_write("use 64")
        self.Instr_write("mov rbx,0x%x"%(vmcs),thread)        
        self.Instr_write("push rax",thread)
        self.Instr_write("mov rax, @std_vmcs_encoding.guest_es_sel");
        self.Instr_write("vmread [rbx + disp32 &OFFSET(@std_vmcs_data.guest_es_sel)],rax")
        self.Instr_write("pop rax",thread)
        
    def Change_vm_rip(self,vmcs,guest_rip,host_rip,thread):
        self.Text_write("use 64")
        self.Instr_write("mov rbx,0x%x"%(vmcs),thread)
        self.Instr_write("mov rax,%s"%(guest_rip),thread)  
        self.Instr_write("mov qword ptr [rbx + disp32 &OFFSET(@std_vmcs_data.guest_rip)], rax")
        self.Instr_write("mov rax,%s"%(host_rip),thread)  
        self.Instr_write("mov qword ptr [rbx + disp32 &OFFSET(@std_vmcs_data.host_rip)], rax")     
        self.Instr_write("push rax",thread)
        self.Instr_write("mov rax, @std_vmcs_encoding.guest_rip");
        self.Instr_write("vmwrite rax,[rbx + disp32 &OFFSET(@std_vmcs_data.guest_rip)]")
        self.Instr_write("mov rax, @std_vmcs_encoding.host_rip");
        self.Instr_write("vmwrite rax,[rbx + disp32 &OFFSET(@std_vmcs_data.host_rip)]")
        self.Instr_write("pop rax",thread)  
        
    def Reflush_cache(self,eptp_pointer, eptp, thread):
        #ZXC only support type 2
        self.Text_write("use 64")
        self.Instr_write("mov rax,0x%x"%(eptp),thread)
        self.Instr_write("mov [0x%x], rax"%(eptp_pointer),thread)
        self.Instr_write("mov qword ptr [0x%x+8], 0x0"%(eptp_pointer),thread)        
        self.Instr_write("mov rax,0x2",thread)
        self.Instr_write("invept rax,[0x%x]"%(eptp_pointer),thread)

    def Reflush_vpid(self,rax, vpid_pointer, linear_addr, vpid, thread):
        #ZXC only support type 2
        self.Text_write("use 64")
        self.Instr_write("mov rax,0x%x"%(vpid_pointer),thread)
        self.Instr_write("mov qword ptr [rax+8], 0x%x"%(linear_addr),thread)
        self.Instr_write("mov word ptr [rax], 0x%x"%(vpid),thread)
        self.Instr_write("mov word ptr [rax+2], 0x0",thread)
        self.Instr_write("mov dword ptr [rax+4], 0x0",thread)
        self.Instr_write("mov rax,0x%x"%(rax),thread)    
        self.Instr_write("invvpid rax,[0x%x]"%(vpid_pointer),thread)

         
    def Set_std_vmcs_initialize_16bit_control_state(self,thread):
        self.Text_write("use 64")
        self.Instr_write("push rax",thread)
        self.Instr_write("mov rax,@std_vmcs_encoding.vpid",thread);
        self.Instr_write("vmwrite rax,[rbx + disp32 &OFFSET(@std_vmcs_data.vpid)]",thread)
        self.Instr_write("pop rax",thread)
        
    def Vmfunc(self,thread):
        self.Text_write("use 64")
        #ZXC don't support vmfun
        self.Instr_write("mov rax,0x0",thread)
        self.Instr_write("mov rcx,0x0",thread)            
        
    def Close_page_table(self):
        if self.page_mode == "4KB_32bit":
            self.ptg.Mapping_func()
        #self.ptg.Check_page_frame_info()