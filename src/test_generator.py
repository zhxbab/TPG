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
from instruction import Instr
from page import Page
from simcmd import Simcmd
from c_parser import C_parser
from interrupt import Interrupt
class Test_generator(Args,Util):
    def __init__(self,args):
        signal.signal(signal.SIGINT,self.Sigint_handler)
        Args.__init__(self,args)
        
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

    def Fix_threads(self,threads):
        self.threads = threads
        if self.threads > 1 and self.c_gen==1:
            self.multi_page=1
    def Create_global_info(self):
        self.asm_list = []
        self.inc_path = "%s/include"%(self.tpg_path)
        self.bin_path = "%s/bin"%(self.tpg_path)
        self.ic_list = []
        self.fail_list = []
        self.pclmsi_list_file = "%s/%s_pclmsi.list"%(self.avp_dir_path,self.avp_dir_name)
        self.mpg = Mem()
        self.c_parser = None
        self.Gen_cnsim_param()
        #info(self.avp_dir_path)
    def Create_asm(self,index=0x0):
        self.asm_name = "%s_%s_%sT_%s_%d.asm"%(self.realbin_name,index,self.threads,self.mode,self.seed)
        self.asm_path = os.path.join(self.avp_dir_path,self.asm_name)
        self.asm_file = open(self.asm_path,"w")
        self.asm_list.append(self.asm_path)
        self.ptg.asm_file = self.asm_file
        self.mpg.asm_file = self.asm_file
        self.simcmd.asm_file = self.asm_file
        self.interrupt.asm_file = self.asm_file
        self.Text_write("include \"%s/std.inc\""%(self.inc_path))
        self.hlt_code = self.mpg.Apply_mem(0x200,16,start=0x0,end=0xA0000,name="hlt_code")

        
    def Gen_mode_code(self):
        self.mode_code = Mode(self.mpg, self.instr_manager, self.ptg, self.threads, self.simcmd, self.intel, self.interrupt,self.c_parser)
        self.mode_code.asm_file = self.asm_file
        self.ptg.c_gen = self.c_gen
        self.ptg.intel = self.intel
        if self.c_gen:
            self.c_parser.multi_page = self.multi_page
        self.ptg.multi_page = self.multi_page
        [self.stack_segs,self.user_code_segs] = self.mode_code.Mode_code(self.mode,self.c_gen,self.disable_avx,self.disable_pcid)

    def Gen_cnsim_param(self):
        if self.intel:
            intel_cnsim_cmd = "-apic-id-increment 2 "
        else:
            intel_cnsim_cmd = " "
        cnsim_param_pclmsi = " "
        cnsim_param_normal = "-ma %s -no-tbdm-warnings -va -no-mask-page -trait-change %s "%(self.very_short_num,self.very_short_cmd)
        cnsim_param_mem = "-mem 0xF4 "
        cnsim_param_thread = "-threads %d "%(self.threads)
        # remove no stack, -no-apic-intr -all-mem -addr-chk -memread-chk 
        self.cnsim_param = cnsim_param_pclmsi + cnsim_param_normal + cnsim_param_mem + cnsim_param_thread + intel_cnsim_cmd
        
        
    def Gen_hlt_code(self,thread_num):
        if thread_num == 0:
            self.Text_write("jmp $%s"%(self.hlt_code["name"]))
            self.Text_write("org 0x%x"%(self.hlt_code["start"]))
            self.Tag_write(self.hlt_code["name"])
            self.Text_write("hlt")
        elif 0 < thread_num < 4:
            self.Text_write("jmp $%s"%(self.hlt_code["name"]))
        else:
            self.Error_exit("Invalid thread num!")

    def Gen_sim_cmd(self,thread_num):
        self.simcmd.Simcmd_write(thread_num)
        
    def Gen_ctrl_cmd(self):
        self.simcmd.Ctrlcmd_write()
        
    def Reset_asm(self):
        self.mpg.Reset_mem()
        self.instr_manager = Instr(self.threads)
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
    def Spin_lock_create(self,thread):
        spin_lock = self.mpg.Apply_mem(0x4,0x4,start=0x1000000,end=0xB0000000,name="spin_lock")
        self.simcmd.Add_sim_cmd("at $y%d >= 1 set memory 0x%08x to 0x00000000"%(thread,spin_lock["start"]),thread)
        #self.simcmd.Add_sim_cmd("at $y%d >= 1 set register RAX to 0x00000000:0x00000000"%(thread),thread)
        spin_lock["num"] = self.spin_lock_num
        spin_lock["ctrl_id"] = [0]*4
        self.spin_lock_num += 1
        return spin_lock
    #//sim: at $y0 >= 1 set memory 0x09ac8008 to 0x00000000:0x00000000

    def Sync_spin_lock(self,spin_lock,thread,unlock_thread=0x0):
        self.simcmd.Add_sim_cmd("at $y%d >= %d disable intermediate checking"%(thread,self.instr_manager.Get_instr(thread)+1),thread)
        self.Instr_write("inc dword [0x%08x]"%(spin_lock["start"]),thread)
        self.Tag_write("spin_lock_T%d_%d"%(thread,spin_lock["num"]))
        self.Instr_write("cmp dword [0x%08x],0x4"%(spin_lock["start"]),thread)
        if unlock_thread == thread:
            #self.simcmd.Add_sim_cmd("at $y%d >= %d set memory 0x%08x to 0x00000004"%(thread,self.instr_manager.Get_instr(thread),spin_lock["start"]),thread)
            for i in range(0,self.threads):
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
    #def Spin_lock_ctrl(self,thread):
    
    def Sync_threads(self):
        for i in range(0,self.threads):
            self.Sync_thread(i)
            
    def Sync_thread(self,thread):
        #if self.instr_manager.Get_instr(thread)-self.simcmd.current_instr[thread] > 0:
        ctrl_id = self.simcmd.Add_ctrl_cmd(thread,self.instr_manager.Get_instr(thread)-self.simcmd.current_instr[thread])
        self.simcmd.current_instr[thread] = self.instr_manager.Get_instr(thread)
        return ctrl_id
    
    def Load_asm_code(self,thread, num):
        self.c_parser.Load_c_asm(thread,self.hlt_code,num)
        
    def Vmx_load_asm_code(self,thread,num):
        self.c_parser.Vmx_load_c_asm(thread,self.hlt_code,num)
    
    def Gen_asm_code(self,thread, num):
        self.c_parser = C_parser(self.bin_path,self.avp_dir_path,self.mode,self.instr_manager,self.mpg)
        self.c_parser.asm_file = self.asm_file
        ret_gen_asm_code = self.c_parser.Gen_c_asm(thread,num)
        if ret_gen_asm_code:
            del_asm = self.asm_list.pop()
            os.system("rm -f %s"%(self.asm_file))
            warning("%s's c code can't be executed successfully, so remove it from asm list"%(del_asm))
        return ret_gen_asm_code
     
    def Updata_interrupt(self,index,handler):
        self.interrupt.Update_interrupt_handler(index,handler)
        
    def Initial_interrupt(self):
        self.int_handler_base = self.mpg.Apply_mem(0x100000,16,start=0xa00000,end=0x1000000,name="int_handler_base")
        self.int_handler_record_base = self.mpg.Apply_mem(0x800,16,start=0x0,end=0xA0000,name="int_handler_record_base")
        self.interrupt.Initial_interrupt_handler(self.int_handler_base,self.int_handler_record_base)
        
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