#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' Agner '
__author__ = 'Ken Zhao'
########################################################
# Agner is used to change Agner C code to AVP
########################################################
import os, sys, logging, random, signal, subprocess, re, csv,threading,time, gzip
from optparse import OptionParser
from logging import info, error, debug, warning, critical
global_counter = None
global_counter_rate = 1
############################################Class##########################################
class Agner:
    def __init__(self,args):
            self.all_list = 0
            self.current_dir_path = os.path.abspath(".") # current dir path
            self.cpus = [#{"cpu":"CNR001A1","device":"0","fre":"2G","ref":"333M"},\
                         {"cpu":"CNR002","device":"3","fre":"2G","ref":"333M"},\
                         #{"cpu":"Intel_E6300","device":"4","fre":"2G","ref":"333M"},\
                         #{"cpu":"Intel_I5_3470","device":"3","fre":"2G","ref":"100M"},\
                         #{"cpu":"Intel_Skylake_6600","device":"4","fre":"2G","ref":"100M"},\
                         #{"cpu":"Intel_I5_4590","device":"4","fre":"2G","ref":"100M"},\
                         {"cpu":"ZX-D","device":"0","fre":"2G","ref":"100M"},\
                         #{"cpu":"Intel_Nehalem_K655","device":"2","fre":"2G","ref":"100M"},\
                         ]
            self.result_csv = os.path.join(self.current_dir_path,"result.csv")
            self.Agner2avp_cmd = "%s --disable_pcid -p 1"%(os.path.join(self.current_dir_path,"Agner2avp"))
            self.realbin_path = sys.path[0] # realbin path 
            self.realbin_name = os.path.realpath(sys.argv[0]).split(".")[0].split("/")[-1] # realbin name
            self.tpg_path = os.getenv("LOCATION_TPG")
            self.Parse_input(args)
            self.Set_logging() #Set logging
            signal.signal(signal.SIGINT,self.Sigint_handler)
            self.total_cnt = 0

            
    def Parse_input(self,args):
        args_parser = OptionParser(usage="%Agner *args, **kwargs", version="%Agner 0.1") #2016-04-25 version 0.1
        args_parser.add_option("-f","--file", dest="elf_file", help="The elf file", type="str", default = None)
        args_parser.add_option("-l","--list", dest="list_file", help="The pclmsi list file", type="str", default = None)
        args_parser.add_option("-i","--instr", dest="instr", help="The instr name for list file", type="str", default = None)
        args_parser.add_option("--debug", dest="_debug", help="Enable the debug mode", action="store_true", default = False)
        args_parser.add_option("--enable_avx", dest="enable_avx", help="Enable AVX for some AVX test", action="store_true", default = False)
        args_parser.add_option("--all", dest="all", help="Change All Agner elf in target dir to avp", action="store_true", default = False)
        args_parser.add_option("--all_list", dest="all_list", help="Run all the pclmsi list file in the target dir", action="store_true", default = False)
        args_parser.add_option("-d","--dir", dest="dir", help="The target dir", type="str", default = None)
        args_parser.add_option("--update", dest="update_flag", help="Run pclmsi and updata csv file", action="store_true", default = False)
        args_parser.add_option("--very_short", dest="very_short", help="use -very-shot mode in cnsim", action="store_true", default = False)
        args_parser.add_option("--disable_instr_only", dest="instr_only", help="Cnsim instr only", action="store_false", default = True)
        (self.args_option, self.args_additions) = args_parser.parse_args(args)
        if not self.args_option.elf_file == None:
            self.elf_file = os.path.join(self.current_dir_path,self.args_option.elf_file)
            self.all_elf = None
            self.list_file =None
        else:
            self.elf_file = None
            if self.args_option.all == True and self.args_option.all_list == False:
                self.all_elf = 1
                if self.args_option.dir == None:
                    self.Error_exit("Must input a target dir!")
                else:
                    self.all_dir = os.path.join(self.current_dir_path ,self.args_option.dir)
                self.list_file = None
                self.all_list = 0
            elif self.args_option.all == False and self.args_option.all_list == True:
                self.all_list=1
                if self.args_option.dir == None:
                    self.Error_exit("Must input a target dir!")
                else:
                    self.all_dir = os.path.join(self.current_dir_path ,self.args_option.dir)
                self.list_file = None
            elif self.args_option.all == True and self.arg_option.all_list == True:
                self.Error_exit("Not use --all and --all_list")
            else:
                self.all_list = 0
                if self.args_option.list_file == None:
                    self.Error_exit("--all, --all_list, -f or -l need one, Please use -h to see the doc")
                else:
                    self.list_file = os.path.join(self.current_dir_path,self.args_option.list_file)
                    if self.args_option.instr == None:
                        self.Error_exit("You must set instr name for update to CSV file")
                    else:
                        self.instr_name = self.args_option.instr
                        self.all_elf = None
                        self.args_option.update_flag = True
                    
        if self.args_option.enable_avx == True:
            self.enable_avx = 1
        else:
            self.enable_avx = 0
            
        if self.args_option.update_flag == True:
            self.update_flag = 1
#            if os.path.exists(self.result_csv):
#                self.csvfile = file(self.result_csv, 'ab+')
#                self.csv_file = csv.writer(self.csvfile)
#            else:
            self.csvfile = file(self.result_csv, 'wb')
            self.csv_file = csv.writer(self.csvfile)
            label_list = ["Instr/Platform"]
            for item in self.cpus:
                label_list.append("%s_%s_%s(cpi)"%(item["cpu"],item["fre"],item["ref"]))
            self.csv_file.writerow(label_list)
        else:
            self.update_flag = 0
        if self.args_option.very_short == True:
            self.very_short_cmd = "--very_short"
        else:
            if self.args_option.instr_only:
                self.very_short_cmd = "--instr_only"               
            else:
                self.very_short_cmd = ""
        
    def Set_logging(self):
        if self.args_option._debug == True: plevel = logging.DEBUG #plevel is the print information level
        else: plevel = logging.INFO
        logging.basicConfig(level=plevel, format="%(asctime)s %(filename)10s[line:%(lineno)6d] %(levelname)8s: %(message)s",
                        datefmt="%a, %d %b %Y %H:%M:%S", stream=sys.stdout)
        
    def Sigint_handler(self, signal, frame):
        critical("Ctrl+C pressed and Exit!!!")
        sys.exit(0)
        
    def Error_exit(cls,cmd):
        error(cmd)
        sys.exit(0)
        
    def Handle_elf(self):
        if self.all_elf:
            dir_list = os.listdir(self.all_dir)
            for dir in dir_list:
                if os.path.isdir("%s/%s"%(self.all_dir,dir)):
                    self.elf_file = "%s/%s/%s.elf"%(self.all_dir,dir,dir)
                    self.total_cnt = self.total_cnt + 1
                    self.Handle_single_elf()
        else:
            self.Handle_single_elf()
            
    def Handle_single_elf(self):
        info(self.elf_file)
        self.elf_dir = os.path.split(self.elf_file)[0]
        self.elf_dir_name = self.elf_dir.split("/")[-1]
        self.format = self.Check_format()
        if self.enable_avx:
            self.Agner2avp_cmd = "%s %s %s -f %s"%(self.Agner2avp_cmd,self.format,self.very_short_cmd,self.elf_file)
        else:
            self.Agner2avp_cmd = "%s %s %s --disable_avx -f %s"%(self.Agner2avp_cmd,self.format,self.very_short_cmd,self.elf_file)
        self.ic_file_list = self.Run_agner2avp(10)
        
    def Check_format(self):
        check_format_cmd = "objdump -a %s"%(self.elf_file)
        check_p = subprocess.Popen(check_format_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (stdoutput,erroutput) = check_p.communicate()
        stdoutput = stdoutput.strip()
        stdoutput_list = stdoutput.split("\n")
        for line in stdoutput_list:
            m = re.search(r"file format elf32-i386",line)
            if m:
                return "-m 2"
            m = re.search(r"file format elf64-x86-64",line)
            if m:
                return "-m 0"     
            
            
    def Run_agner2avp(self,counter=1):
        find_dir = 0
        pclmsi_list = "Not found"
        run_p = subprocess.Popen(self.Agner2avp_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (stdoutput,erroutput) = run_p.communicate()
        stdoutput = stdoutput.strip()
        stdoutput_list = stdoutput.split("\n")
        for line in stdoutput_list:
            if find_dir == 0:
                m = re.search(r"create dir cmd is mkdir (.*)",line)
                if m :
                    avp_dir = m.group(1)
                    find_dir = 1
            m = re.search(r"INFO: (.*) Done",line)
            if m:
                pclmsi_list = m.group(1)
            m = re.search(r"INFO: gzip (.*)",line)
            if m:
                ic_file = m.group(1)
        info(avp_dir)
        info(pclmsi_list)
        self.Get_instruction_num(pclmsi_list,self.elf_dir_name)
        info("total instruction num %d"%(global_counter))
        if self.update_flag:
            core_clk_list = [self.elf_dir_name]
            new_elf_dir = os.path.join(self.current_dir_path,"vectors/%s"%(self.elf_dir_name))
            if os.path.exists(new_elf_dir):
                info("rm -rf %s"%(new_elf_dir))
                os.system("rm -rf %s"%(new_elf_dir))
            info("cp -rf %s vectors"%(self.elf_dir))
            os.system("cp -rf %s vectors"%(self.elf_dir))
            info("cp -rf %s vectors/%s"%(avp_dir,self.elf_dir_name))
            os.system("cp -rf %s vectors/%s"%(avp_dir,self.elf_dir_name))
            self.instr_name = self.elf_dir_name
            avp_dir_name = avp_dir.split("/")[-1]
            pclmsi_list_name = os.path.split(pclmsi_list)[-1]
            ic_file_name = os.path.split(ic_file)[-1]
            real_pclmsi_list = os.path.join(self.current_dir_path,"vectors/%s/%s/%s"%(self.elf_dir_name,avp_dir_name,pclmsi_list_name))
            real_ic_file_path = os.path.join(self.current_dir_path,"vectors/%s/%s"%(self.elf_dir_name,avp_dir_name))
            info(real_ic_file_path)
            for item in self.cpus:
                average_clk = 0
                temp_core_clk = 0xFFFFFFFF
                final_core_clk = 0xFFFFFFFF
                self.stop_flag = 0
                change_path_cmd ="runpclmsi -d %s --rerun=%d -p %s -f %s"%(item["device"],counter,real_ic_file_path,real_pclmsi_list)
                os.system(change_path_cmd)
                run_pclmsi_cmd = "run_pclmsi +device:%s +avpl:%s +no_log:1"%(item["device"],real_pclmsi_list)
                info(run_pclmsi_cmd)
                run_pclmsi_p = subprocess.Popen(run_pclmsi_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                run_pclmsi_p_ret = run_pclmsi_p.poll()
                info("The test_runpclmsi subprocess pid is %d"%(run_pclmsi_p.pid))
                t = threading.Timer(50,self.timer_function,(run_pclmsi_p,))
                t.start()
                while run_pclmsi_p_ret == None and self.stop_flag == 0:
                    run_pclmsi_p_ret = run_pclmsi_p.poll()
                t.cancel()
                if self.stop_flag:
                    run_pclmsi_p.kill()
                    final_core_clk = "N/A"
                    core_clk_list.append(final_core_clk)
                    info("Stop flag is 1 and sleep 10s")
                    time.sleep(10)
                    continue
                else:
                    (stdoutput,erroutput) = run_pclmsi_p.communicate()
                    stdoutput = stdoutput.strip()
                    stdoutput_list = stdoutput.split("\n")
                    for line in stdoutput_list:
                        m = re.search(r"pclmsi-warn: 0x(\w+) mismatches expected 0x00000000 actual 0x(\w+) mask 0x00000000",line)
                        if m :
                            core_clk = int(m.group(2),16)
                            if core_clk > 0xD0000000:
                                pass
                            else:
                                final_core_clk = min(core_clk/global_counter,temp_core_clk)
                                average_clk = average_clk + final_core_clk
                                #info("final core is %f"%(final_core_clk))
                    average_clk = "%.3f"%(float(average_clk/counter))
                    if final_core_clk == 0xFFFFFFFF:
                        average_clk = "N/A"
                        time.sleep(40)
                        info("sleep 40s")
                    else:
                        info("CPU: %s INSTRUCTION: %s CPI is %s"%(item["cpu"],self.instr_name,average_clk)) 
                    core_clk_list.append(average_clk)
            self.csv_file.writerow(core_clk_list)
            
    def Check_dir_name(self,dir_name):
        temp = dir_name.split("_")[0]
        m = re.search("enter",temp)
        if m:
            temp = "enter"
        m = re.search("shl",temp)
        if m:
            n = re.search("shl_cntop",dir_name)
            if n:
                temp = "sal"
        return temp
    
    def Get_pclmsi_list(self):
        info(self.all_dir)
        counter = 10
        dir_list = os.listdir(self.all_dir)
        for dir in dir_list:
            if os.path.isdir("%s/%s"%(self.all_dir,dir)):
                #info("%s/%s"%(self.all_dir,dir))
                file_list = os.listdir("%s/%s"%(self.all_dir,dir))
                for pclmsi_list in file_list:
                    if os.path.isdir("%s/%s/%s"%(self.all_dir,dir,pclmsi_list)):
                        #info(pclmsi_list)
                        files = os.listdir("%s/%s/%s"%(self.all_dir,dir,pclmsi_list))
                        for file in files:
                            if file.split(".")[-1] == "list":
                                ic_path = "%s/%s/%s/"%(self.all_dir,dir,pclmsi_list)
                                self.list_file = "%s/%s/%s/%s"%(self.all_dir,dir,pclmsi_list,file)
                                #info(self.list_file)
                                run_pclmsi_cmd = "runpclmsi -d 0 -f %s --rerun=%d -p %s"%(self.list_file,counter,ic_path)
                                os.system(run_pclmsi_cmd)
                                self.instr_name = dir
                                #info(self.instr_name)
                                self.total_cnt = self.total_cnt +1
                                self.Get_instruction_num(self.list_file,dir)
                                self.Only_update_csv(counter)
    
    def Get_instruction_num(self,file,dir_name):
        global global_counter
        rdpmc_num = 0
        fl = open(file,"r")
        ic_file = None
        instruction_num = 0
        start = 0 
        end = 0
        instr_count = -1
        #instr_name = self.Check_dir_name(dir_name)
        #info("instr name is %s"%(instr_name))
        while True:
            line = fl.readline()
            if line:
                line = line.strip()
                m = re.search(r"load:(.*) \+rerun",line)
                if m :
                    ic_file = m.group(1)
            else:
                break
        fl.close()
        info(ic_file)
        if ic_file == None:
            self.Error_exit("No ic file in list")
        else:
            if ic_file.split(".")[-1] == "gz":
                fic = gzip.open(ic_file,"r")
            else:
                fic = open(ic_file,"r")                
            while True:
                #info(line)
                line = fic.readline()
                if line:
                    line = line.strip()
                    m = re.search(r"RDPMC",line)
                    if m :
                        if start == 0 and end == 0:
                            start = 1
                        elif start == 1 and end == 0:
                            end = 1
                        else:
                            pass
                        rdpmc_num +=1
                    if start == 1 and end == 0:
                        m = re.search(" [I,F,X,K,M]:",line)
                        if m:
                            instr_count += 1
                            
                else:
                    break
        fic.close()
        if instr_count != 0 and rdpmc_num%2 == 0 and rdpmc_num != 0:
            global_counter = float(instr_count*(rdpmc_num/2))
        elif instr_count == 0:
            self.Error_exit("Instr num is 0!")
        else:
            self.Error_exit("RDPMC num %d is wrong!"%(rdpmc_num))           
        #global_counter = float((last_instruction_num-first_instruction_num)/global_counter_rate)
#        if 121000 >= instruction_num > 120000:
#            global_counter = float(100)
#        elif 131000 >= instruction_num > 121000:
#            global_counter = float(1000)
#        elif 200000 >= instruction_num > 131000:
#            global_counter = float(10000)
#        elif 1000000 > instruction_num > 200000:
#            global_counter = float(100000)
#        elif instruction_num > 1000000:
#            global_counter = float(1000000)
#        else:
#            self.Error_exit("Error Instruction Num %d"%(instruction_num))
    
                 
    def Only_update_csv(self,counter=1):
        core_clk_list = [self.instr_name]
        info("total instruction num %d"%(global_counter))    
        for item in self.cpus:
            average_clk = 0
            temp_core_clk = 0xFFFFFFFF
            final_core_clk = 0xFFFFFFFF
            self.stop_flag = 0
            run_pclmsi_cmd = "run_pclmsi +device:%s +avpl:%s +no_log:1"%(item["device"],self.list_file)
            info(run_pclmsi_cmd)
            run_pclmsi_p = subprocess.Popen(run_pclmsi_cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            run_pclmsi_p_ret = run_pclmsi_p.poll()
            info("The test_runpclmsi subprocess pid is %d"%(run_pclmsi_p.pid))
            t = threading.Timer(50,self.timer_function,(run_pclmsi_p,))
            t.start()
            while run_pclmsi_p_ret == None and self.stop_flag == 0:
                run_pclmsi_p_ret = run_pclmsi_p.poll()
            t.cancel()
            if self.stop_flag:
                run_pclmsi_p.kill()
                final_core_clk = "N/A"
                core_clk_list.append(final_core_clk)
                info("Stop flag is 1 and sleep 20s")
                time.sleep(20)
                continue
            else:
                (stdoutput,erroutput) = run_pclmsi_p.communicate()
                stdoutput = stdoutput.strip()
                stdoutput_list = stdoutput.split("\n")
                for line in stdoutput_list:
                    m = re.search(r"pclmsi-warn: 0x(\w+) mismatches expected 0x00000000 actual 0x(\w+) mask 0x00000000",line)
                    if m :
                        core_clk = int(m.group(2),16)
                        if core_clk > 0xD0000000:
                            pass
                        else:
                            final_core_clk = min(core_clk/global_counter,temp_core_clk)
                            average_clk = average_clk + final_core_clk
                            #info(final_core_clk)
                            #info(average_clk)
                average_clk = "%.3f"%(float(average_clk/counter))
                if final_core_clk == 0xFFFFFFFF:
                    average_clk = "N/A"
                    time.sleep(40)
                    info("sleep 40s")
                else:                
                    info("CPU: %s INSTRUCTION: %s CPI is %s"%(item["cpu"],self.instr_name,average_clk)) 
                #info(average_clk)
                core_clk_list.append(average_clk)
        self.csv_file.writerow(core_clk_list)
        
    def timer_function(self,Popen):
        returncode = Popen.poll()
        if returncode == None:
            warning("Stop runpclmsi subprocess %d!"%(Popen.pid))
            self.stop_flag = 1
        else:
            return None
###########################################################Main############################################
if __name__ == "__main__":
    agner = Agner(sys.argv[1:])
    if agner.all_list:
        agner.Get_pclmsi_list()
    else:
        if agner.list_file != None:
            agner.Only_update_csv(10)
        else:
            agner.Handle_elf()
    if agner.update_flag:
        agner.csvfile.close()
    info("Total %d tests"%(agner.total_cnt))