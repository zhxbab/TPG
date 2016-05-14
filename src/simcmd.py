#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' simcmd module '
__author__ = 'Ken Zhao'
########################################################
# simcmd module is used to gen sim cmd
########################################################
from util import Util
from logging import info, error, debug, warning, critical
class Simcmd(Util):
    def __init__(self,threads):
        self.rem = [[],[],[],[],[],[],[],[]] # I don't know why not [[]]*threads
        self.sim = [[],[],[],[],[],[],[],[]]
        self.ctrl = []
        self.ctrl_id = 0
        self.current_instr = [0]*4
    def Add_sim_cmd(self,cmd,thread):
        sim_cmd = "//sim: %s"%(cmd)
        self.sim[thread].append(sim_cmd)
        
    def Add_rem_cmd(self,cmd,thread):
        rem_cmd = "//rem: %s"%(cmd)
        self.rem[thread].append(rem_cmd)
        
    def Add_ctrl_cmd(self,thread, instr_num):
        self.ctrl.append({"thread":thread,"ID":self.ctrl_id,"instr_num":instr_num})
        self.ctrl_id += 1
        return self.ctrl_id - 1
    
    def Change_ctrl_cmd(self,ctrl_id,instr_num):
        for i in self.ctrl:
            if i["ID"] == ctrl_id:
                i["instr_num"] = instr_num
                
    
    def Simcmd_write(self,thread):
        self.Comment("//sim: chain begin")
        self.Comment("//sim: assume thread %d"%(thread))
        for i in self.sim[thread]:
            self.Comment(i)
        self.Comment("//sim: chain end")
        for i in self.rem[thread]:
            self.Comment(i)
        
    def Ctrlcmd_write(self):
        for i in self.ctrl:
            self.Comment("//ctrl: thread %d exec %d"%(i["thread"],i["instr_num"]))