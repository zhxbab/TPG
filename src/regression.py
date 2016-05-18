#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' regression module '
__author__ = 'Ken Zhao'
########################################################
# regression module is used for regression
########################################################
import sys, os, re, random, subprocess,json, logging, time, smtplib, threading
sys.path.append("/%s/../../src"%(sys.path[0]))
from logging import info, error, debug, warning, critical
from util import Util
from operator import eq,ne
class Regression(Util):
    def __init__(self,device):
        self.runpclmsi = os.getenv("LOCATION_RUN_PCLMSI")
        self.device = device
        self.test_list = "%s/bjcvreg/test.ic.gz"%(os.getenv("LOCATION_TPG"))
        self.runpclmsi_test_cmd = "%s +device:%d +load:%s +no_log:1"%(self.runpclmsi,self.device,self.test_list)
        self.clk_list = [12,11,10,9,8]
        self.fail_dir = os.getenv("LOCATION_CVREG_VECTOR")
        self.result = 0
        self.fail_log_base_name = "fail"
        self.remove_flag = 0
        self.stop_flag = 0
        
    def Handle_vecor(self,ic_file,c_code_base_name=None):
        self.c_code_base_name = c_code_base_name
        self.ic_file = ic_file
        self.base_name = self.ic_file.replace(".ic.gz","")
        self.base_name_path = os.path.split(self.ic_file)[0]
        self.pclmsi_log_name = self.base_name.split("/")[-1]
        self.fail_log_name = "%s.%s"%(self.base_name,self.fail_log_base_name)
#        self.fail_ic_new_name = "%s_%s.ic.gz"%(self.base_name,time.time())
#        self.fail_ic_new_name = self.fail_ic_new_name.split("/")[-1]
        info("base name is %s"%(self.base_name))
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
        info("cp  %s %s"%(file,self.fail_dir))
        os.system("cp  %s %s"%(file,self.fail_dir))
        info("cp  %s %s"%(file_log,self.fail_dir))
        os.system("cp  %s %s"%(file_log,self.fail_dir))
        if self.c_code_base_name != None:
            info("cp  %s.* %s"%(self.c_code_base_name,self.fail_dir))
            os.system("cp  %s* %s"%(self.c_code_base_name,self.fail_dir))
        
    def Parse_pclmsi_log(self,log_file):
        result = 0
        fail_vectors = {}
        line_num = 0
        with open(log_file,'r') as fl:
            while True:
                line = fl.readline()
                if line:
                    line = line.strip()
                    if log_file.split(".")[-1] == "jtrk":
                        if len(line) == 0x0 and line_num == 0:
                            result = 2
                            return result
                        else:
                            line_decode = json.loads(line)
                    #info(line_decode)
                            if eq(line_decode["status"], "FAIL"):
                                result = 1
                                if not fail_vectors.has_key(line_decode["avp"]):
                                    fail_vectors[line_decode["avp"]] = line
                                    fail_vector = os.path.join(self.base_name_path,line_decode["avp"])
                                    info(fail_vector)
                                    fail_log = self.Record_fail_log(fail_vector,line)
                                    self.Copy_ic_log(fail_vector,fail_log)
                                    break
                            line_num = line_num + 1
                    elif log_file.split(".")[-1] == "sum":
                        m = re.search(r'Ratio = (\d+)',line)
                        if m:
                            ratio = m.group(1)
                            
                        m = re.search(r'Attempting to load test (.*)',line)
                        if m:
                            fail_log = self.Record_fail_log(m.group(1),"PCLMSI FAIL IN RATIO %d"%(ratio))
                            self.Copy_ic_log(m.group(1),fail_log)
                else:
                    break
        if len(fail_vectors) != 0:
            self.Send_mail(fail_vectors)
        return result
    
    def Record_fail_log(self,file,line):
        file_log = "%s.fail_log"%(file.split(".")[0])
        with open(file_log,"w") as ff:
            ff.write("%s\n"%(line))
        return file_log
    
    def Tune_clk(self):
        result = 0
        for clc in self.clk_list:
            info("runpclmsi -d %d -f %s --rerun=1000 -c %d"%(self.device,self.temp_list,clc))
            os.system("runpclmsi -d %d -f %s --rerun=1000 -c %d"%(self.device,self.temp_list,clc))
            runpclmsi_cmd = "%s +device:%d +avpl:%s +log_name:%s"%(self.runpclmsi,self.device,self.temp_list,self.base_name)
            info(runpclmsi_cmd)
            runpclmsi_p = subprocess.Popen(runpclmsi_cmd,stdout=None, stderr=None, shell=True)
            runpclmsi_p_ret = runpclmsi_p.poll()
            info("The runpclmsi subprocess pid is %d"%(runpclmsi_p.pid))
            t = threading.Timer(20,self.timer_function,(runpclmsi_p,))
            t.start()
            while runpclmsi_p_ret == None and self.stop_flag == 0:
                runpclmsi_p_ret = runpclmsi_p.poll()
            t.cancel()
            if runpclmsi_p_ret == 0x0:
                info("PCLMSI SUCCESSFULLY")
                result = self.Parse_pclmsi_log("%s.jtrk"%(self.base_name))
                if result:
                    break
            else:
                info("PCLMSI RESET or HANG")
                if os.path.exists("%s.jtrk"%(self.base_name)):
                    result = self.Parse_pclmsi_log("%s.jtrk"%(self.base_name))
                if result == 0x2:
                    self.Parse_pclmsi_log("%s.sum"%(self.base_name))
                self.Copy_ic_log()
                self.stop_flag = 0
                break
        self.result = result
        
    def Check_result(self):
        self.Remove_all()
        
    def Set_remove_flag(self):
        self.remove_flag = 1
    def Reset_remove_flag(self):
        self.remove_flag = 0
        
    def Send_mail(self,fail_vectors):
        sender = os.getenv("HOSTNAME") 
        receivers = 'KenZhao@zhaoxin.com'
        subject = "PCLMSI FAIL NOTITION"
        content = ""
        for key in fail_vectors:
            content = content + "fail vector: %s\n"%(fail_vectors[key]) 
        message = self.Gen_mail_message(sender,receivers,subject,content)
        smtpObj = smtplib.SMTP('localhost') 
        smtpObj.sendmail(sender, receivers, message)
           
    def Gen_mail_message(self,sender,receivers,subject,content):
        message = """From: %s 
        To: %s 
        Subject: %s
        %s"""%(sender,receivers,subject,content) #From is the sender
        return message

        while ret == None and self.stop_flag == 0:
            ret = csmith_p.poll()

        
    def timer_function(self,Popen):
        returncode = Popen.poll()
        if returncode == None:
            warning("Stop runpclmsi subprocess %d!"%(Popen.pid))
            self.stop_flag = 1
            Popen.kill()
        else:
            return None