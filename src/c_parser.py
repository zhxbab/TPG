#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from __future__ import division 
' C_parser module '
__author__ = 'Ken Zhao'
########################################################
# C parser module is used to parseing C code to data
########################################################
import random, os, re, subprocess,threading,math
from util import Util
from logging import info, error, debug, warning, critical
from operator import eq, ne
from copy import deepcopy
class C_parser(Util):
    def __init__(self, bin_path, avp_dir_path, mode, instr_manager, mpg):
        self.cmsith = "%s/csmith"%(bin_path)
        self.objdump = "%s/objdump"%(bin_path)
        self.readelf = "%s/readelf"%(bin_path)
        self.gcc = "%s/gcc"%(bin_path)
        self.clang = "%s/clang"%(bin_path)
        self.gcc_cplus = "%s/gcc++"%(bin_path)
        self.clang_cplus = "%s/clang++"%(bin_path)
        self.avp_dir_path = avp_dir_path
        self.c_compiler = [self.gcc, self.clang][random.randint(0,1)]
        self.cplus_compiler = [self.gcc_cplus, self.clang_cplus][random.randint(0,1)]
        self.mode = mode
        self.instr_manager = instr_manager
        self.mpg = mpg
        self.stop_flag = 0
        self.c_code_sec_info = []
        self.c_code_mem_info ={}
        self.c_code_rel_info = []
        self.multi_page=0
        
    def Gen_c_asm(self,thread,num,optimize=None):
        self.base_name = "c_code_%d"%(num)
        c_file = "c_code_%d.c"%(num)
        elf_file = "c_code_%d.elf"%(num)
        disasm_file = "c_code_%d"%(num)
        #self.disasm_file = disasm_file
        c_code_sec = "c_code_%d.sec"%(num)
        c_code_rel = elf_file.replace(".elf",".rel")
        if optimize == None:
            self.optimize = ["O2","O3","Os","O0","O1"][random.randint(0,4)]
        else:
            self.optimize = optimize
        os.chdir(self.avp_dir_path)
        if self.mode == "protect_mode" or self.mode == "compatibility_mode":
            extra_cmd = "-m32"
        else:
            extra_cmd = ""
        info("%s -o c_code_%d.c"%(self.cmsith,num))
        csmith_extra_cmd ="--max-funcs 10"
        if os.system("%s %s -o %s"%(self.cmsith,csmith_extra_cmd,c_file)):
            self.Error_exit("Execute csmith error!")
        info("%s -w %s -%s -static -fPIC %s -o %s"%(self.c_compiler,extra_cmd,self.optimize,c_file,elf_file))
        if os.system("%s -w %s -%s -static -fPIC %s -o %s"%(self.c_compiler,extra_cmd,self.optimize,c_file,elf_file)):
            self.Error_exit("Execute %s error!"%(self.c_compiler)) # use -static need glibc-static.x86-64 and i686
        csmith_cmd = "./%s"%(elf_file)
        csmith_p = subprocess.Popen(csmith_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        ret = csmith_p.poll()
        info("The csmith subprocess pid is %d"%(csmith_p.pid))
        t = threading.Timer(10,self.timer_function,(csmith_p,))
        t.start()
        while ret == None and self.stop_flag == 0:
            ret = csmith_p.poll()
        t.cancel()
        self.stop_flag = 0
        if ret != 0x0:
            os.system("rm -f %s*"%(self.base_name))
            os.chdir("../")
            return 1
        if os.system("%s -s -d %s > %s"%(self.objdump,elf_file,disasm_file)):
            self.Error_exit("Execute %s error!"%(self.objdump))
        if os.system("%s -S %s > %s"%(self.readelf,elf_file,c_code_sec)):
            self.Error_exit("Execute %s error!"%(self.readelf))
        if os.system("%s -r %s > %s"%(self.readelf,elf_file,c_code_rel)):
            self.Error_exit("Execute %s -r error!"%(self.readelf))
        else:
            self.c_code_sec_file = open(c_code_sec,"r")
            if self.mode == "long_mode":
                self.Parse_c_sec_long_mode()
            else:
                self.Parse_c_sec()
            self.c_code_re_file = open(c_code_rel,"r")
            self.rela_dyn_flag = self.Parse_c_rel()
            self.c_code_re_file.close()
            for list_index in self.c_code_sec_info:
                #info(list_index) # for debug
                if ne(int(list_index["Addr"],16),0x0) and ne(list_index["Name"],".tbss") and ne(list_index["Name"],".got.plt"):
                    if self.rela_dyn_flag and eq(list_index["Name"],".got"):
                        continue
                    self.c_code_mem_info[list_index["Name"]] = self.mpg.Apply_fix_mem(list_index["Name"],int(list_index["Addr"],16),int(list_index["Size"],16))
                    # in 32bit single thread, .tbss is overlap with .ctors and .dtors, so need to find a new mem and intial to 0x0. then set gs to this location
                    # in 64bit single thread, .tbss is overlap with .init_array and .fini_array and .jcr, so need to find a new mem and intial to 0x0. then set fs to this location
                elif eq(list_index["Name"],".tbss"):                   
                    self.c_code_mem_info[list_index["Name"]] = self.mpg.Apply_mem(int(list_index["Size"],16),16,start=0x1000000,end=0x8000000,name=list_index["Name"])
            #info(self.c_code_mem_info)
            self.c_code_sec_file.close()
        self.c_code_asm = open(disasm_file,"r")
        os.chdir("../")

        return 0
    
    def Get_fix_c_asm(self,elf_file):
        self.base_name = elf_file.split(".")[0]
        disasm_file = elf_file.split(".")[0]
        c_code_sec = elf_file.replace(".elf",".sec")
        c_code_rel = elf_file.replace(".elf",".rel")
        if os.system("%s -s -d %s > %s"%(self.objdump,elf_file,disasm_file)):
            self.Error_exit("Execute %s -s -d error!"%(self.objdump))
        if os.system("%s -S %s > %s"%(self.readelf,elf_file,c_code_sec)):
            self.Error_exit("Execute %s -S error!"%(self.readelf))
        if os.system("%s -r %s > %s"%(self.readelf,elf_file,c_code_rel)):
            self.Error_exit("Execute %s -r error!"%(self.readelf))
        else:
            self.c_code_sec_file = open(c_code_sec,"r")
            if self.mode == "long_mode":
                self.Parse_c_sec_long_mode()
            else:
                self.Parse_c_sec()
            self.c_code_re_file = open(c_code_rel,"r")
            self.rela_dyn_flag = self.Parse_c_rel()
            self.c_code_re_file.close()
            for list_index in self.c_code_sec_info:
                #info(list_index) # for debug
                if ne(int(list_index["Addr"],16),0x0) and ne(list_index["Name"],".tbss") and ne(list_index["Name"],".got.plt"):
                #and ne(list_index["Name"],".got"):
                    if self.rela_dyn_flag and eq(list_index["Name"],".got"):
                        continue
                    self.c_code_mem_info[list_index["Name"]] = self.mpg.Apply_fix_mem(list_index["Name"],int(list_index["Addr"],16),int(list_index["Size"],16))
                    # in 32bit single thread, .tbss is overlap with .ctors and .dtors, so need to find a new mem and intial to 0x0. then set gs to this location
                    # in 64bit single thread, .tbss is overlap with .init_array and .fini_array and .jcr, so need to find a new mem and intial to 0x0. then set fs to this location
                    # .got.plt need rewrite data
                elif eq(list_index["Name"],".tbss"):                   
                    self.c_code_mem_info[list_index["Name"]] = self.mpg.Apply_mem(int(list_index["Size"],16),16,start=0x10000000,end=0x80000000,name=list_index["Name"])
                #info("Name is %s and Addr is %08x"%(list_index["Name"],int(list_index["Addr"],16)))
                else:
                    pass
            self.c_code_sec_file.close() 
        self.c_code_asm = open(disasm_file,"r")
        return 0
    
    def Parse_c_rel(self):
        i = 0
        start = 0
        rela_dyn_flag = 0
        while True:
            line = self.c_code_re_file.readline()
            if line:
                line = line.strip()
                m = re.search(r"Relocation section \'(.*)\'",line)
                if m:
                    if m.group(1) == ".rela.dyn" or m.group(1) == ".rel.dyn":
                        rela_dyn_flag = 1
                    start = 1
                    continue 
                if start == 1:
                    #info(line)
                    addr = line.split(" ")[0]
                    if addr != "Offset" and addr != "":
                        if self.mode == "long_mode":
                            #self.mpg.check_spare_mem()
                            #self.mpg.check_selected_mem()
                            addr_hash = self.mpg.Apply_fix_mem("rel_entry_%d"%(i),int(addr,16),0x8)
                            self.c_code_rel_info.append(addr_hash)
                            del addr_hash
                        else:
                            addr_hash = self.mpg.Apply_fix_mem("rel_entry_%d"%(i),int(addr,16),0x4)
                            self.c_code_rel_info.append(addr_hash)
                            del addr_hash
                        i = i+1
            else:
                break
        self.real_rel_entry = self.mpg.Apply_mem(0x20,0x10,start=0x1000,end=0xA0000,name="real_rel_entry")
        return rela_dyn_flag
    
    def Load_c_rel(self):
        for rel in self.c_code_rel_info:
            self.Text_write("org 0x%x"%(rel["start"]))
            self.Text_write("dd 0x%x"%(self.real_rel_entry["start"]))
            self.Text_write("dd 0x00000000")
        self.Text_write("org 0x%x"%(self.real_rel_entry["start"]))
#        if self.mode == "long_mode":
#            self.Instr_write("add rsp,0x8")
#        else:
#            self.Instr_write("add esp,0x8")
        self.Instr_write("ret")
        
    def Load_c_asm(self,thread,hlt_code,num):
        self.Instr_write("mov eax,&SELECTOR($%s)"%(self.selector_name_c_gen_0),thread)
        if self.mode == "long_mode": 
            self.Instr_write("mov fs,eax",thread)
        else:
            self.Instr_write("mov gs,eax",thread)
        self.Instr_write("mov eax,cr4",thread)
        self.Instr_write("or eax,0x104",thread)
        self.Instr_write("mov cr4,eax",thread)       
        self.Instr_write("call $_init_%d"%(thread),thread)
        self.Instr_write("call $main_%d"%(thread),thread)
        self.Text_write("jmp $%s"%(hlt_code["name"]))
        if self.multi_page:
            self.Text_write("PAGING $tlb_pointer_%d"%(thread))
        self.Parse_c_asm(thread)
        return 0
    
    def Vmx_load_c_asm(self,thread,hlt_code,num):
        if self.multi_ept:
            self.Text_write("EPT $ept_tlb_pointer_%d"%(thread))
            self.Parse_c_asm(thread)
        else:
            self.Parse_c_asm(thread)
    
    def Parse_c_asm(self,thread):
        #self.c_code_asm = open(self.disasm_file,"r")
        cnt = 0
        self.c_code_asm.seek(0,0)
        stop_asm_flag = 0
        #end_flag = 0
        while True:
            line = self.c_code_asm.readline()
            if line:
                line = line.strip()
                if cnt == 0:
                    m = re.search(r'(\w+) <(.*)>:',line)
                    if m:
                        stop_asm_flag = 0
                        self.Comment("#### %s"%(line))           
                        self.Text_write("org 0x%s"%(m.group(1)))  
                        if eq(m.group(2),"main"):
                            self.Tag_write("main_%d"%(thread))
                            debug("Main match")
                        elif eq(m.group(2),"_init"):
                            self.Tag_write("_init_%d"%(thread))
                            if self.mode == "long_mode":
                                self.Text_write("use 64")
                            elif self.mode == "compatibility_mode":
                                self.Text_write("use 32")
                            debug("Init match")
                        elif eq(m.group(2),"__init_cpu_features"):
                            self.Text_write("ret")
                            stop_asm_flag = 1
                    else:
                        if stop_asm_flag == 0:
                            asm_code_list = line.split("\t") # the data before program use " " split
                            if len(asm_code_list) > 1:
                            #info(asm_code_list)
                                self.Asm_write(asm_code_list,thread)
                                #pass
                    m = re.search(r"Disassembly of section (\..*):",line)
                    if m:
#                        #info(m.group(1))
                        for index in self.c_code_sec_info:
                            if eq(m.group(1),index["Name"]):
                                index["Load"] = 1
                elif cnt == 1:
                    name_match = 0
                    m = re.search(r"Contents of section (.*):",line)
                    if m:
                        name = m.group(1)
                        if eq(name,"__libc_thread_freeres_fn"):
                            name = "__libc_thread_fre"
                        if eq(name,"__libc_thread_subfreeres"):
                            name = "__libc_thread_sub"
                        if eq(name,".note.gnu.build-id"):
                            name = ".note.gnu.build-i"
                        for index in self.c_code_sec_info:
                            if eq(name,index["Name"]):
                                name_match = 1
                                if not index["Load"]:
                                    if self.mode == "long_mode":
                                        if ne(index["Addr"],"0000000000000000"):
                                            self.Load_c_asm_sec(index)
                                    else:
                                        if ne(index["Addr"],"00000000"):
                                            self.Load_c_asm_sec(index)
                                else:
                                    pass
                        if not name_match:
                            error("section %s is not in sec file"%(name))
                else:
                    self.Error_exit("file seek cnt is error!")
            else:
                if cnt == 0:
                    self.c_code_asm.seek(0,0)
                    cnt += 1
                    continue
                else:
                    break
        self.Load_c_asm_NOBITS()
        self.Load_c_rel()

#
#        for index in self.c_code_sec_info:
#            if not index["Load"]:
#                info("%s is not in dis"%(index["Name"]))
    def Load_c_asm_NOBITS(self): # for .bss and .tbss
        for index in self.c_code_sec_info:
            if eq(index["Type"],"NOBITS"):
                # in 32bit single thread, .tbss is overlap with .ctors and .dtors
                default_line_num = int(index["Size"],16)//0x4
                self.Comment("#####%s"%(index["Name"]))
                self.Text_write("org 0x%08x"%(self.c_code_mem_info[index["Name"]]["start"]))
                for i in range(0,default_line_num):
                    self.Text_write("dd 0x00000000")
                for j in range(0,int(index["Size"],16)%0x4):
                    self.Text_write("db 0x00")
                    
                    
        
        
        
    def Load_c_asm_sec(self,sec_info):
        if sec_info["Name"] == ".got.plt":
            return
        elif sec_info["Name"] == ".got" and self.rela_dyn_flag:
            return
        line_num = int(math.ceil(int(sec_info["Size"],16)/0x10))
        extra_data_size = int(sec_info["Size"],16)%0x10
        self.Comment("#####%s"%(sec_info["Name"]))
        self.Text_write("org 0x%08x"%(self.c_code_mem_info[sec_info["Name"]]["start"]))
        for i in range(0,line_num):
            line = self.c_code_asm.readline()
            line = line.strip()
            line_list = line.split()
#             if eq(sec_info["Name"],"__libc_subfreeres"):
#                 info(line_list)
            del line_list[0]
            if i < line_num-1 or extra_data_size == 0:
                extra_data_size_num = 4
            else:
                extra_data_size_num = int(math.ceil(extra_data_size/0x4))
            for j in line_list[0:extra_data_size_num]:
                new_data_str = self.Convert_data(j)
                #new_data_str = j
                if len(new_data_str) == 0x8:
                    self.Text_write("dd 0x%s"%(new_data_str))
                else:
                    for k in range(0,len(new_data_str),2):
                        self.Text_write("db 0x%s"%(new_data_str[len(new_data_str)-2-k:len(new_data_str)-k]))
                        

    def Convert_data(self,data_str):
        new_data_str=""
        for i in range(0,len(data_str),2):
            new_data_str = data_str[i:i+2]+new_data_str
        return new_data_str
                
    def Parse_c_sec(self):
        start = 0
        num = 0
        sec_hash = {}
        key_list = ['Nr', 'Name', 'Type', 'Addr', 'Off', 'Size', 'ES', 'Flg', 'Lk', 'Inf', 'Al','Load']
        while True:
            line = self.c_code_sec_file.readline()
            if line:
                line = line.strip()
                m = re.search(r'Key to Flags:',line)
                if m:
                    start = 0
                    
                if start:
                    sec_list = line.split()
                    #info(sec_list)  
                    if eq(sec_list[0],"[Nr]"):
                        pass
                    else:
                        if num < 10 :
                            del sec_list[1]
                            del sec_list[0]
                            if num == 0:
                                sec_list.insert(0,".null")
                        else:
                            del sec_list[0]
                        #info(sec_list)
                        if len(sec_list)==10:
                            pass
                        elif len(sec_list)==9:
                            sec_list.insert(6,"")
                        else:
                            warning("Invalid sec list length! Please check!")
                        sec_hash[key_list[0]] = num
                        for i in range(0,10):
                            sec_hash[key_list[i+1]] = sec_list[i]
                        sec_hash[key_list[11]] = 0x0
                        sec_hash_temp = deepcopy(sec_hash)
                        num += 1
                        self.c_code_sec_info.append(sec_hash_temp)
                                           
                m = re.search(r'Section Headers:',line)
                if m:
                    start = 1
            else:
                break

    def Parse_c_sec_long_mode(self):
        start = 0
        num = 0
        sec_hash = {}
        key_list_even = ['Nr', 'Name', 'Type', 'Addr', 'Off'] 
        key_list_older  = ['Size', 'ES', 'Flg', 'Lk', 'Inf', 'Al','Load']
        num_even = 0
        while True:
            line = self.c_code_sec_file.readline()
            if line:
                line = line.strip()
                m = re.search(r'Key to Flags:',line)
                if m:
                    start = 0
                    
                if start:
                    sec_list = line.split()
                    #info(sec_list)  
                    if eq(sec_list[0],"[Nr]"):
                        self.c_code_sec_file.readline()
                        continue
                    else:
                        if num_even == 0:
                            num_even = 1
                            if num < 10 :
                                del sec_list[1]
                                del sec_list[0]
                                if num == 0:
                                    sec_list.insert(0,".null")
                            else:
                                del sec_list[0]
                            for i in range(1,len(key_list_even)):
                                sec_hash[key_list_even[i]] = sec_list[i-1]
                            sec_hash[key_list_even[0]] = num
                            continue
                        else:
                            num_even = 0
                            #info(sec_list)
                            if len(sec_list)==len(key_list_older)-1:
                                pass
                            elif len(sec_list)==len(key_list_older)-2:
                                sec_list.insert(2,"")
                            else:
                                warning("Invalid sec list length! Please check!")
                            for j in range(0,len(key_list_older)-1):
                                sec_hash[key_list_older[j]] = sec_list[j]
                            sec_hash[key_list_older[-1]] = 0x0
                            sec_hash_temp = deepcopy(sec_hash)
                            num += 1
                            self.c_code_sec_info.append(sec_hash_temp)
                                                   
                m = re.search(r'Section Headers:',line)
                if m:
                    start = 1
            else:
                break                 
                 

    def timer_function(self,Popen):
        returncode = Popen.poll()
        if returncode == None:
            warning("Stop csmith subprocess %d!"%(Popen.pid))
            self.stop_flag = 1
            Popen.kill()
        else:
            return None