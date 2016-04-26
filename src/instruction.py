#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' instruction module '
__author__ = 'Ken Zhao'
########################################################
# instruction module is used to manage instructions
########################################################
class Instr:
    def __init__(self):
        self.instr_count = 0
    def Set_instr(self,value):
        self.instr_count = value
    def Add_instr(self):
        self.instr_count += 1
    def Sub_instr(self):
        self.instr_count -= 1
    def Get_instr(self):
        return self.instr_count
    def Reset_instr(self):
        self.instr_count = 0
        