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
        self.tbdm = [[],[],[],[],[],[],[],[]]
        self.current_instr = [0]*8
        self.chain = [0,0,0,0,0,0,0,0]
    def Add_sim_cmd(self,cmd, thread, chain=0):
        if len(self.sim[thread]) == 0:
            self.Create_sim_chain(thread)
        if 0< len(self.sim[thread]) < chain+1:
            for i in range(len(self.sim[thread]), chain+1):
                self.Create_sim_chain(thread)
            self.sim[thread][chain].append(cmd)
        else:
            self.sim[thread][chain].append(cmd)                      
        
    def Create_sim_chain(self,thread):
        self.chain[thread] = self.chain[thread] + 1
        self.sim[thread].append([])
        
    def Add_rem_cmd(self,cmd,thread):
        rem_cmd = "//rem: %s"%(cmd)
        self.rem[thread].append(rem_cmd)
        
    def Add_ctrl_cmd(self,thread, instr_num):
        self.ctrl.append({"thread":thread,"ID":self.ctrl_id,"instr_num":instr_num})
        self.ctrl_id += 1
        return self.ctrl_id - 1
    
    def Add_tbdm_cmd(self,cmd,thread):
        tbdm_cmd = "//;$ %s"%(cmd)
        self.tbdm[thread].append(tbdm_cmd)
        
    def Change_ctrl_cmd(self,ctrl_id,instr_num):
        for i in self.ctrl:
            if i["ID"] == ctrl_id:
                i["instr_num"] = instr_num
                
    
    def Simcmd_write(self,thread):
        for chain in range(0, self.chain[thread]):
            self.Comment("//sim: chain begin %d"%(chain))
            self.Comment("//sim: assume thread %d"%(thread))
            for i in self.sim[thread][chain]:
                self.Comment("//sim: %s"%(i))
            self.Comment("//sim: chain end")
        for t in self.rem[thread]:
            self.Comment("//rem: %s"%(i))
            
        self.Comment("//;$ assume thread %d"%(thread))
        for tbdm_cmd in self.tbdm[thread]:
            self.Comment(tbdm_cmd)

        
    def Ctrlcmd_write(self):
        for i in self.ctrl:
            self.Comment("//ctrl: thread %d exec %d"%(i["thread"],i["instr_num"]))
            
