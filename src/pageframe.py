#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' pageframe module '
__author__ = 'Ken Zhao'
########################################################
# pageframe module is the date struct for ktpg page
########################################################
from operator import eq, ne
from util import Util
from copy import deepcopy
from logging import info, error, debug, warning, critical

        
class Pageframe():
    def __init__(self,page_mode):
        self.page_mode = page_mode
        if page_mode == "4KB_32bit":
            self.single_page_size = 0x1000
            self.pde_array = [{"name":"PAGE_PDE","index":None,"data":None,"used":0x0}]
            self.pte_array = [{"name":"PAGE_PTE","index":None,"data":None,"used":0x0,"pde":None,"attr":None}]
                
#    def show_frame(self):
#        if self.page_mode == "4KB_32bit":
#            for i in self.pde_array:
#                info("PDE info: Name %s, Index %d, Data 0x%08x, Used %d"%(i.pde["name"],i.pde["index"],i.pde["data"],i.pde["used"]))
#                for j in i.pde["PTE"]:
#                    info("PTE info: Name %s, Index %d, Data 0x%08x, Used %d"%(j["name"],j["index"],j["data"],j["used"]))                    
