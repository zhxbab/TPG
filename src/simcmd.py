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
    def Add_sim_cmd(self,cmd,thread):
        sim_cmd = "//sim: %s"%(cmd)
        self.sim[thread].append(sim_cmd)
#        info(1)
#        for i in self.sim[1]:
#            info(i)
#        info(2)
#        for i in self.sim[thread]:
#            info(i)
#        info(3)
#        for i in self.sim[thread]:
#            info(i)
    def Add_rem_cmd(self,cmd,thread):
        rem_cmd = "//rem: %s"%(cmd)
        self.rem[thread].append(rem_cmd)
        
    def Simcmd_write(self,thread):
        self.Comment("//sim: chain begin")
        self.Comment("//sim: assume thread %d"%(thread))
        for i in self.sim[thread]:
            self.Comment(i)
        self.Comment("//sim: chain end")
        for i in self.rem[thread]:
            self.Comment(i)
