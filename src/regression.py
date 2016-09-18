#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' regression module '
__author__ = 'Ken Zhao'
########################################################
# regression module is used for regression
########################################################
import sys, os, re, random, subprocess,json, logging, time, smtplib, threading, signal, datetime
sys.path.append("/%s/../../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from util import Util
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
    def __init__(self,device):
        signal.signal(signal.SIGINT,self.Sigint_handler)
        self.runpclmsi = os.getenv("LOCATION_RUN_PCLMSI")
        self.device = device
        self.test_list = "%s/bjcvreg/test.ic.gz"%(os.getenv("LOCATION_TPG"))
        self.runpclmsi_test_cmd = "%s +device:%d +load:%s +no_log:1 +ignore_all_checks:1"%(self.runpclmsi,self.device,self.test_list)
        self.clk_list = [4,4.5,5,5.5,6]
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

    def Handle_vecor(self,ic_file,time,c_code_base_name=None):
        self.runpclmsi_time = time
        self.c_code_base_name = c_code_base_name
        self.ic_file = ic_file
        self.base_name = self.ic_file.replace(".ic.gz","")
        self.base_name_path = os.path.split(self.ic_file)[0]
        self.pclmsi_log_name = self.base_name.split("/")[-1]
        self.fail_log_name = "%s.%s"%(self.base_name,self.fail_log_base_name)
#        self.fail_ic_new_name = "%s_%s.ic.gz"%(self.base_name,time.time())
#        self.fail_ic_new_name = self.fail_ic_new_name.split("/")[-1]
        #info("base name is %s"%(self.base_name))
        self.temp_list = "%s_temp_list"%(self.base_name)
        os.system("ls %s > %s"%(self.ic_file,self.temp_list))
        self.Tune_clk()
        self.Check_result()
        os.system("rm -f %s*"%(self.temp_list))

    def Remove_all(self):
        if self.remove_flag:
            info("rm -f %s.*"%(self.base_name))
            os.system("rm -f %s.*"%(self.base_name))
            if self.c_code_base_name != None:
                info("rm -f %s*"%(self.c_code_base_name))
                os.system("rm -f %s*"%(self.c_code_base_name))
    
    def Copy_ic_log(self,file,file_log):
        new_fail_dir = self.fail_dir
        if os.path.exists("%s/%s"%(self.fail_dir,datetime.date.today())):
            info("%s/%s has existed"%(self.fail_dir,datetime.date.today()))
        else:
            info("mkdir  %s/%s"%(self.fail_dir,datetime.date.today()))
            os.system("mkdir  %s/%s"%(self.fail_dir,datetime.date.today()))
        new_fail_dir = "%s/%s"%(self.fail_dir,datetime.date.today())              
        if os.path.exists(file):
            fail_asm_file = file.split(".")[0]+".asm"
            if os.path.exists(fail_asm_file):
                info("cp  %s %s"%(fail_asm_file,new_fail_dir))
                os.system("cp  %s %s"%(fail_asm_file,new_fail_dir))
            else:
                warning("Copy asm file %s don't exist"%(file))                
            info(new_fail_dir)
            info("cp  %s %s"%(file,new_fail_dir))
            os.system("cp  %s %s"%(file,new_fail_dir))
            info("cp  %s %s"%(file_log,new_fail_dir))
            os.system("cp  %s %s"%(file_log,new_fail_dir))
        else:
            error("Copy vector %s don't exist"%(file))
            
        if self.c_code_base_name != None:
            info("cp  %s.* %s"%(self.c_code_base_name,new_fail_dir))
            os.system("cp  %s* %s"%(self.c_code_base_name,new_fail_dir))
        
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
                            info(fail_vector)
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
                        
                    m = re.search(r'RATIO = (\d+)',line)
                    if m:
                        ratio = m.group(1)
                        
                    m = re.search(r'test (.*) pass = (\d+) fail = (\d+) hang = (\d+)',line)
                    if m:
                        pass_flag = int(m.group(2))
                        fail_flag = int(m.group(3))
                        hang_flag = int(m.group(4))
                        if (fail_flag-last_fail) or (hang_flag-last_hang):
                            if not fail_vectors.has_key(vector):
                                fail_vectors[vector] = "%s PCLMSI FAIL IN RATIO %s IN DEVICE %d"%(vector,ratio,self.device)
                                fail_log = self.Record_fail_log(vector,fail_vectors[vector])                     
                                self.Copy_ic_log(vector,fail_log)

                    m = re.search(r'\*\*\*\*\*\*',line)
                    if m:
                        last_pass = pass_flag
                        last_fail = fail_flag
                        last_hang = hang_flag
                        not_finish = 0
                else:
                    if line_num == 1:
                        result = 2
                        return result
                    else:
                        if not_finish == 0:
                            pass
                        else:
                            if not fail_vectors.has_key(vector):
                                fail_vectors[vector] = "%s PCLMSI FAIL(RESET or HANG) IN RATIO %s IN DEVICE %d"%(vector,ratio,self.device)
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
    
    def Tune_clk(self):
        result = 0
        for clc in self.clk_list:
            info("runpclmsi -d %d -f %s --rerun=1000 -c %d"%(self.device,self.temp_list,clc*2))
            os.system("runpclmsi -d %d -f %s --rerun=1000 -c %d"%(self.device,self.temp_list,clc*2))
            runpclmsi_cmd = "%s +device:%d +avpl:%s +log_name:%s +clkRatio:%s +check_run_time:1000"%(self.runpclmsi,self.device,self.temp_list,self.base_name,clc)
            runpclmsi_p_ret = self.Do_runpclmsi(runpclmsi_cmd,self.runpclmsi_time)
            if runpclmsi_p_ret == 0x0:
                info("PCLMSI SUCCESSFULLY")
                if not self.skip_check_fail:
                    result = self.Parse_pclmsi_log_jtrk("%s.jtrk"%(self.base_name))
                if result:
                    #sys.exit(0) #for debug fail case.
                    break
#            elif runpclmsi_p_ret == 1:
#                if self.runpclmsi_time<= 20: #run_pclmsi end self
#                    self.Error_exit("Device is not ready, Please try again!")
            else:
                info("PCLMSI RESET or HANG")
                if os.path.exists("%s.sum"%(self.base_name)):
                    result = self.Parse_pclmsi_log_sum("%s.sum"%(self.base_name))
                    if result == 2:
                        self.Error_exit("Device connect fail! Please check the device connection!")
                    else:
                        self.sleep_flag = 1
                        info("Sleep 60s!")
                        time.sleep(60)
                        test_result = self.Do_runpclmsi(self.runpclmsi_test_cmd,20)
                        if test_result == 0x0:
                            info("HOST %s DEVICE %s RESET SUCCESSFULLY"%(os.getenv("HOSTNAME"),self.device))
                            continue
                        else:
                            info("Send Mail and Sleep forever until reset!")
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
#                    else:
#                        pass
                else:
                    self.Error_exit("sum file is not exist! Please check!")
                continue
        self.result = result
        
    def Check_result(self):
        self.Remove_all()
        
    def Set_remove_flag(self):
        self.remove_flag = 1
    def Reset_remove_flag(self):
        self.remove_flag = 0
        
   
        

    def Send_mail_vectors(self,fail_vectors):
        info("Send Mail")
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
            info("Reset successfully!")
        else:
            if self.mail_num < 3:
                info("Send Mail for notice reset num %d"%(self.mail_num))
                self.Send_info("HOST %s DEVICE %s Need RESET!"%(os.getenv("HOSTNAME"),self.device))
            self.sleep_timer_start = 1
        return

                
    def Do_runpclmsi(self,cmd,time):
        self.stop_flag = 0
        info(cmd)
        runpclmsi_p = subprocess.Popen(cmd,stdout=None, stderr=None, shell=True)
        runpclmsi_p_ret = runpclmsi_p.poll()
        info("The test_runpclmsi subprocess pid is %d"%(runpclmsi_p.pid))
        t = threading.Timer(time,self.timer_function,(runpclmsi_p,))
        t.start()
        while runpclmsi_p_ret == None and self.stop_flag == 0:
            runpclmsi_p_ret = runpclmsi_p.poll()
        t.cancel()
        self.stop_flag = 0
        del t
        #info("Do teset result is %d"%(test_runpclmsi_p_ret))
        return runpclmsi_p_ret
