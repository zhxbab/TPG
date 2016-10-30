#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' regression module '
__author__ = 'Ken Zhao'
########################################################
# regression module is used for regression
########################################################
import sys, os, re, random, subprocess,json, logging, time, smtplib, threading, signal, datetime, random
sys.path.append("/%s/../../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from util import Util,Info
from operator import eq,ne
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
###########################################Sub routines###########################
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
                        Header(name, 'utf-8').encode(), \
                        addr.encode('utf-8') if isinstance(addr, unicode) else addr))     
############################################Classes################################
class Regression(Util):
    def __init__(self,device,arch):
        signal.signal(signal.SIGINT,self.Sigint_handler)
        self.runpclmsi = os.getenv("LOCATION_RUN_PCLMSI")
        self.device = device
        self.test_list = "%s/bjcvreg/test.ic.gz"%(os.getenv("LOCATION_TPG"))
        self.runpclmsi_test_cmd = "%s +device:%d +load:%s +no_log:1 +ignore_all_checks:1"%(self.runpclmsi,self.device,self.test_list)
        self.fail_dir = os.getenv("LOCATION_CVREG_VECTOR")
        self.result = 0
        self.fail_log_base_name = "fail"
        self.remove_flag = 0
        self.stop_flag = 0
        self.c_code_base_name = None
        self.sleep_flag = 0        
        self.mail_num = 0
        self.sleep_timer_start = 0
        self.runpclmsi_time = 20
        self.skip_check_fail = False
        self.cnr001a1_feature_list =[{"Name":"speculative table walk","Location":"0x1203[61]"},\
                                     {"Name":"loop queue","Location":"0x1257[0]"}]
        self.cnr002_feature_list =[{"Name":"speculative table walk","Location":"0x1203[61]"}]
        self.chx001a0_feature_list =[{"Name":"speculative table walk","Location":"0x1203[61]"},\
                                     {"Name":"hif speculative read","Location":"0x160f[1]"}]
        if arch == "default_arch":
            self.rerun_times = 1000
            self.clk_list = [6]
            self.feature_list = []
        elif arch == "cnr001a1":
            self.rerun_times = 1000
            self.clk_list = [4,4.5,5,5.5,6]
            self.feature_list = self.cnr001a1_feature_list
        elif arch == "cnr002":
            self.rerun_times = 1000
            self.clk_list = [4,4.5,5,5.5,6]
            self.feature_list = self.cnr002_feature_list            
        elif arch == "chx001a0":
            #self.clk_list = [8,9,10,11,12,13,14,15,16,17,18,19,20]
            self.rerun_times = 25000
            self.clk_list = [8]
            self.feature_list = self.chx001a0_feature_list
        else:
            self.Error_exit("Invalid Architecture")
        self.freglog = None
                              
    def Handle_vecor(self,ic_file,time,c_code_base_name=None,cases=None):
        self.runpclmsi_time = time
        self.c_code_base_name = c_code_base_name
        self.ic_file = ic_file
        if cases != None:
            self.base_name = self.ic_file.replace(".ic.gz","") + "_%d"%(random.randint(1,0xFFFFF))
        else:
            self.base_name = self.ic_file.replace(".ic.gz","")
        self.base_name_path = os.path.split(self.ic_file)[0]
        self.pclmsi_log_name = self.base_name.split("/")[-1]
        self.fail_log_name = "%s.%s"%(self.base_name,self.fail_log_base_name)
#        self.fail_ic_new_name = "%s_%s.ic.gz"%(self.base_name,time.time())
#        self.fail_ic_new_name = self.fail_ic_new_name.split("/")[-1]
        #info("base name is %s"%(self.base_name))
        self.temp_list = "%s_temp_list"%(self.base_name)
        os.system("ls %s > %s"%(self.ic_file,self.temp_list))
        self.Tune_clk_and_feature()
        self.Check_result()
        os.system("rm -f %s*"%(self.temp_list))

    def Remove_all(self):
        if self.remove_flag:
            Info("rm -f %s.*"%(self.base_name),self.freglog)
            os.system("rm -f %s.*"%(self.base_name))
            if self.c_code_base_name != None:
                Info("rm -f %s*"%(self.c_code_base_name),self.freglog)
                os.system("rm -f %s*"%(self.c_code_base_name))
                
    def Copy_ic_log(self,file,file_log):
        new_fail_dir = self.fail_dir
        if os.path.exists("%s/%s"%(self.fail_dir,datetime.date.today())):
            Info("%s/%s has existed"%(self.fail_dir,datetime.date.today()),self.freglog)
        else:
            Info("mkdir  %s/%s"%(self.fail_dir,datetime.date.today()),self.freglog)
            os.system("mkdir  %s/%s"%(self.fail_dir,datetime.date.today()))
        new_fail_dir = "%s/%s"%(self.fail_dir,datetime.date.today())
        if file ==  None:
            Info("cp  %s %s"%(file_log,new_fail_dir),self.freglog)
            os.system("cp  %s %s"%(file_log,new_fail_dir))            
        else:            
            if os.path.exists(file):
                fail_asm_file = file.split(".")[0]+".asm"
                if os.path.exists(fail_asm_file):
                    Info("cp  %s %s"%(fail_asm_file,new_fail_dir),self.freglog)
                    os.system("cp  %s %s"%(fail_asm_file,new_fail_dir))
                else:
                    warning("Copy asm file %s don't exist"%(fail_asm_file))                
                Info(new_fail_dir,self.freglog)
                Info("cp  %s %s"%(file,new_fail_dir),self.freglog)
                os.system("cp  %s %s"%(file,new_fail_dir))
                Info("cp  %s %s"%(file_log,new_fail_dir),self.freglog)
                os.system("cp  %s %s"%(file_log,new_fail_dir))
            else:
                error("Copy vector %s don't exist"%(file))
            
#        if self.c_code_base_name != None:
#            Info("cp  %s.* %s"%(self.c_code_base_name,new_fail_dir),self.freglog)
#            os.system("cp  %s* %s"%(self.c_code_base_name,new_fail_dir))
        
    def Parse_pclmsi_log_jtrk(self,log_file):
        result = 0
        fail_vectors = {}
        file_type = log_file.split(".")[-1]
        if not eq(file_type,"jtrk"):
            self.Error_exit("log type is not jtrk!")
        with open(log_file,'r') as fl:
            while True:
                line = fl.readline()
                if line:
                    line = line.strip()
                    line_decode = json.loads(line)
                    if eq(line_decode["status"], "FAIL"):
                        result = 1
                        if not fail_vectors.has_key(line_decode["avp"]):
                            fail_vectors[line_decode["avp"]] = line
                            fail_vector = os.path.join(self.base_name_path,line_decode["avp"])
                            Info(fail_vector,self.freglog)
                            fail_log = self.Record_fail_log(fail_vector,line)
                            self.Copy_ic_log(fail_vector,fail_log)
                else:
                    break
        if len(fail_vectors) != 0:
            #pass
            self.Send_mail_vectors(fail_vectors)
        return result
    
    def Parse_pclmsi_log_sum(self,log_file):
        result = 0
        fail_vectors = {}
        line_num = 0
        file_type = log_file.split(".")[-1]
        not_finish = 0
        last_pass = 0
        last_fail = 0
        last_hang = 0
        feature = "No feature"
        if not eq(file_type,"sum"):
            self.Error_exit("log type is not sum!")
        with open(log_file,'r') as fl:
            while True:
                line = fl.readline()
                line_num = line_num + 1
                if line:
                    line = line.strip()
                    m = re.search(r'Attempting to load test (.*)',line)
                    if m:
                        vector = m.group(1)
                        not_finish = 1
                        
                    m = re.search(r'RATIO = (\S+) ',line)
                    if m:
                        ratio = m.group(1)

                    m = re.search(r'Changing msr (.*)',line)
                    if m:
                        feature = m.group(1)
                        
                    m = re.search(r'test (.*) pass = (\d+) fail = (\d+) hang = (\d+)',line)
                    if m:
                        pass_flag = int(m.group(2))
                        fail_flag = int(m.group(3))
                        hang_flag = int(m.group(4))
                        if (fail_flag-last_fail) or (hang_flag-last_hang):
                            if not fail_vectors.has_key(vector):
                                fail_vectors[vector] = "%s PCLMSI FAIL IN RATIO %s IN FEATURE %s IN DEVICE %d"%(vector,ratio,feature,self.device)
                                fail_log = self.Record_fail_log(vector,fail_vectors[vector])                     
                                self.Copy_ic_log(vector,fail_log)

                    m = re.search(r'\*\*\*\*\*\*',line)
                    if m:
                        last_pass = pass_flag
                        last_fail = fail_flag
                        last_hang = hang_flag
                else:
                    if line_num == 1:
                        result = 2
                        return result
                    else:
                        if not_finish == 0:
                            self.Send_info("Fail before load avp, Please check! log_file name is"%(log_file))
                            self.Copy_ic_log(None,log_file) 
                            return 3                          
                            #self.Error_exit("Load avp fail, Please check!")
                        else:
                            if not fail_vectors.has_key(vector):
                                fail_vectors[vector] = "%s PCLMSI FAIL(RESET or HANG) IN RATIO %s IN FEATURE %s IN DEVICE %d"%(vector,ratio,feature,self.device)
                                fail_log = self.Record_fail_log(vector,fail_vectors[vector])
                                self.Copy_ic_log(vector,fail_log)
                                result = 1
                        break
        if len(fail_vectors) != 0:
            #pass
            self.Send_mail_vectors(fail_vectors)
        return result                   
    
    def Record_fail_log(self,file,line):
        file_log = "%s.fail_log"%(file.split(".")[0])
        with open(file_log,"w") as ff:
            ff.write("%s\n"%(line))
        return file_log
    
    def Tune_clk_and_feature(self):
        for clc in self.clk_list:
            Info("runpclmsi -d %d -f %s --rerun=%d"%(self.device,self.temp_list,self.rerun_times),self.freglog)
            os.system("runpclmsi -d %d -f %s --rerun=%d"%(self.device,self.temp_list,self.rerun_times))
            runpclmsi_cmd = "%s +device:%d +avpl:%s +log_name:%s +clkRatio:%s +check_run_time:%d"%(self.runpclmsi,self.device,self.temp_list,self.base_name,clc,self.rerun_times)
            self.Run_Check(runpclmsi_cmd)
            if len(self.feature_list) == 0:
                continue
            else:
                for feature in self.feature_list:
                    runpclmsi_cmd = "%s +device:%d +avpl:%s +log_name:%s +clkRatio:%s +check_run_time:1000 +flip_msr_bit:\"%s\""\
                    %(self.runpclmsi,self.device,self.temp_list,self.base_name,clc,feature["Location"])
                    self.Run_Check(runpclmsi_cmd)
                
                
    def Run_Check(self,runpclmsi_cmd):
        result = 0
        runpclmsi_p_ret = self.Do_runpclmsi(runpclmsi_cmd,self.runpclmsi_time)
        if runpclmsi_p_ret == 0x0:
            Info("PCLMSI SUCCESSFULLY",self.freglog)
            if not self.skip_check_fail:
                result = self.Parse_pclmsi_log_jtrk("%s.jtrk"%(self.base_name))
            if result:
                Info("Find Fail Sleep 5s!",self.freglog)
                time.sleep(5)
                return 
        else:
            test_result = self.Do_runpclmsi(self.runpclmsi_test_cmd,20)
            if test_result == 0x0:
                Info("Perhaps PCLMSI Link Unstable",self.freglog)
                self.Send_info("HOST %s DEVICE %s Link Unstable!"%(os.getenv("HOSTNAME"),self.device))
                self.result = result
                return                 
            Info("PCLMSI RESET or HANG",self.freglog)
            if os.path.exists("%s.sum"%(self.base_name)):
                result = self.Parse_pclmsi_log_sum("%s.sum"%(self.base_name))
                if result == 2:
                    self.Error_exit("Device connect fail! Please check the device connection!")
                else:
                    self.sleep_flag = 1
                    Info("Sleep 60s!",self.freglog)
                    time.sleep(60)
                    test_result = self.Do_runpclmsi(self.runpclmsi_test_cmd,20)
                    if test_result == 0x0:
                        self.Send_info("HOST %s DEVICE %s Has RESET AUTOMATICALLY!"%(os.getenv("HOSTNAME"),self.device))
                        Info("HOST %s DEVICE %s Has RESET AUTOMATICALLY!"%(os.getenv("HOSTNAME"),self.device),self.freglog)
                        return 
                    else:
                        Info("Send Mail and Sleep forever until reset!",self.freglog)
                        check_reset_time = 60*30#60*30 is good,20 is used for test
                        self.Send_info("HOST %s DEVICE %s HANG!"%(os.getenv("HOSTNAME"),self.device))
                        sleep_t = threading.Timer(check_reset_time,self.sleep_timer_function,())#60*30 is good,20 is used for test
                        sleep_t.start()
                        while self.sleep_flag:
                            time.sleep(1)
                            if self.sleep_timer_start:
                                del sleep_t
                                sleep_t = threading.Timer(check_reset_time,self.sleep_timer_function,())
                                sleep_t.start()
                                self.sleep_timer_start = 0
                        sleep_t.cancel()
                        del sleep_t
                        self.mail_num = 0
            else:
                self.Error_exit("sum file is not exist! Please check!")
        self.result = result
        
    def Check_result(self):
        self.Remove_all()
        
    def Set_remove_flag(self):
        self.remove_flag = 1
    def Reset_remove_flag(self):
        self.remove_flag = 0
        
   
        

    def Send_mail_vectors(self,fail_vectors):
        Info("Send Mail",self.freglog)
        content = "fail vector:"
        for key in fail_vectors:
            content = content + "\t%s\t\n"%(fail_vectors[key]) 
        self.Send_mail(content)

        
    def Send_mail(self,content):
        #info("Send Mail 1111")
        #sender = "%s@zhaoxin.com"%(os.getenv("HOSTNAME"))
        sender = "%s@ic.com"%(os.getenv("HOSTNAME"))#can't use zhaoxin.com
        receivers = 'KenZhao@zhaoxin.com'
        msg = MIMEText('%s'%(content), 'plain', 'utf-8')
        msg['From'] = _format_addr(u'PCLMSI <%s>' % sender)
        msg['To'] = _format_addr(u'KenZhao <%s>' % receivers)
        msg['Subject'] = Header(u'"PCLMSI FAIL NOTITION', 'utf-8').encode()
        smtpObj = smtplib.SMTP('localhost') 
        smtpObj.sendmail(sender, [receivers,"zhxbab@163.com"], msg.as_string())
           
    def Send_info(self,content):
        self.Send_mail(content)

        
    def timer_function(self,Popen):
        returncode = Popen.poll()
        if returncode == None:
            warning("Stop runpclmsi subprocess %d!"%(Popen.pid))
            self.stop_flag = 1
            Popen.kill()
        else:
            return None
        
    def sleep_timer_function(self):
        self.mail_num = self.mail_num + 1
        #info("send mail num is %d"%(self.mail_num))
        test_result = self.Do_runpclmsi(self.runpclmsi_test_cmd,20)
        if test_result == 0x0:
            self.sleep_flag = 0
            self.Send_info("HOST %s DEVICE %s Has RESET!"%(os.getenv("HOSTNAME"),self.device))
            Info("Reset successfully!",self.freglog)
        else:
            if self.mail_num < 3:
                Info("Send Mail for notice reset num %d"%(self.mail_num),self.freglog)
                self.Send_info("HOST %s DEVICE %s Need RESET!"%(os.getenv("HOSTNAME"),self.device))
            self.sleep_timer_start = 1
        return

                
    def Do_runpclmsi(self,cmd,time):
        self.stop_flag = 0
        Info(cmd,self.freglog)
        runpclmsi_p = subprocess.Popen(cmd,stdout=None, stderr=None, shell=True)
        runpclmsi_p_ret = runpclmsi_p.poll()
        Info("The test_runpclmsi subprocess pid is %d"%(runpclmsi_p.pid),self.freglog)
        t = threading.Timer(time,self.timer_function,(runpclmsi_p,))
        t.start()
        while runpclmsi_p_ret == None and self.stop_flag == 0:
            runpclmsi_p_ret = runpclmsi_p.poll()
        t.cancel()
        self.stop_flag = 0
        del t
        #info("Do teset result is %d"%(test_runpclmsi_p_ret))
        return runpclmsi_p_ret
