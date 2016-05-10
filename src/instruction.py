#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' instruction module '
__author__ = 'Ken Zhao'
########################################################
# instruction module is used to manage instructions
########################################################
class Instr:
    def __init__(self,threads):
        self.instr_count = [0]*threads
    def Set_instr(self,value,thread):
        self.instr_count[thread] = value
    def Add_instr(self,thread):
        self.instr_count[thread] += 1
    def Sub_instr(self,thread):
        self.instr_count[thread] -= 1
    def Get_instr(self,thread):
        return self.instr_count[thread]
    def Reset_instr(self,threads):
        self.instr_count = [0]*threads
        