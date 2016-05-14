#!/usr/bin/env python2.7
from __future__ import division 
# -*- coding: utf-8 -*-
' mem module '
__author__ = 'Ken Zhao'
########################################################
# mem module is used to generate different mem parten
########################################################

from operator import eq, ne
from util import Util
import math, random
from logging import info, error, debug, warning, critical

#############################################Decorator##########################################
#def deFind_mem(cls):
#    def _deFind_mem(func):
#        def __deFind_mem(self,size,align,unit,mem,**cond):
#
#        return __deFind_mem
#    return _deFind_mem


#################################################Classes########################################
class Mem(Util):
    def __init__(self):
        self.spare_range = [{"start":0x0,"size":0xFFFFFFFF}]
        self.selected = []
        self.asm_file = ""
    def check_selected_mem(self,name=""):
        if eq(name,""):
            for mem in self.selected:
                info("%s: start addr is 0x%x and size is 0x%x"%(mem["name"],mem["start"],mem["size"]))
        else:
            for mem in self.selected:
                if eq(mem["name"],name):
                    debug("%s: start addr is 0x%x and size is 0x%x"%(mem["name"],mem["start"],mem["size"]))
                    self.Comment("#### %s: start addr is 0x%x and size is 0x%x"%(mem["name"],mem["start"],mem["size"]))
                    checking_mem = mem
            for mem in self.selected:
                if ne(mem["name"],checking_mem["name"]):
                    if checking_mem["start"] + checking_mem["size"] <= mem["start"]:
                        pass
                    elif checking_mem["start"] >= mem["start"] + mem["size"]:
                        pass
                    else:
                        error("%s: start addr is 0x%x and size is 0x%x"%(checking_mem["name"],checking_mem["start"],checking_mem["size"]))
                        error("%s: start addr is 0x%x and size is 0x%x"%(mem["name"],mem["start"],mem["size"]))
                        self.Error_exit("selected mem %s and selected mem %s overlap!"%(checking_mem["name"],mem["name"]))
                else:
                    pass
            for mem in self.spare_range:
                if checking_mem["start"] + checking_mem["size"] <= mem["start"]:
                    pass
                elif checking_mem["start"] >= mem["start"] + mem["size"]:
                    pass
                else:
                    error("%s: start addr is 0x%x and size is 0x%x"%(checking_mem["name"],checking_mem["start"],checking_mem["size"]))
                    error("spare mem: start addr is 0x%x and size is 0x%x"%(mem["start"],mem["size"]))
                    self.Error_exit("selected mem %s and spare mem overlap!"%(checking_mem["name"]))

    def check_spare_mem(self):
        for mem in self.spare_range:
            info("start addr is 0x%x, end addr is 0x%x and size is 0x%x"%(mem["start"],mem["start"]+mem["size"],mem["size"]))
        
    def Apply_mem(self,size,align,**cond):
        mems = []
        for mem in self.spare_range:
            tmp_mem = self.Find_mem(size,align,mem,**cond)
            if tmp_mem:
                mems.append(tmp_mem)
        if not mems:
            self.Error_exit("For start 0x%x, size 0x%x and align 0x%x, there is no matched mem in spare range!"%(cond["start"],size,align))
        selected_mem = random.choice(mems)
        self.selected.append(selected_mem)
        self.Update_mem(selected_mem)
        self.check_selected_mem(selected_mem["name"])
        return selected_mem
    
    def Apply_fix_mem(self,name,start,size):
        selected_mem = {"start":start,"size":size,"name":name}
        self.selected.append(selected_mem)
        self.Update_mem(selected_mem)
        self.check_selected_mem(selected_mem["name"])
        return selected_mem
    
    
    def Reset_mem(self):
        self.spare_range = [{"start":0x0,"size":0xFFFFFFFF}]
        self.selected = []
        
    def Del_mem(self):
        pass
    def Update_mem(self,selected_mem):
        n = 0
        #self.check_spare_mem()
        #self.check_selected_mem()
        for i,mem in enumerate(self.spare_range):
            if selected_mem["start"] >= mem["start"] and (selected_mem["start"]+selected_mem["size"]) <= (mem["start"]+mem["size"]):
                n = n + 1
                if selected_mem["start"] == mem["start"]:
                    update_mem_0 = {"start":(selected_mem["start"]+selected_mem["size"]),"size":(mem["size"]-selected_mem["size"])}
                    del self.spare_range[i]
                    self.spare_range.insert(i,update_mem_0)
                else:
                    update_mem_0 = {"start":mem["start"],"size":(selected_mem["start"]-mem["start"])}
                    update_mem_1 = {"start":(selected_mem["start"]+selected_mem["size"]),"size":(mem["size"]+mem["start"]-selected_mem["start"]-selected_mem["size"])}
                    del self.spare_range[i]
                    self.spare_range.insert(i,update_mem_0)
                    self.spare_range.insert(i+1,update_mem_1)
                    #self.check_spare_mem()
                    #debug("update mem type 2")
                    #debug("update_mem_0 start addr is 0x%x, end addr is 0x%x and size is 0x%x"%(update_mem_0["start"],update_mem_0["start"]+update_mem_0["size"],update_mem_0["size"]))
                    #debug("update_mem_1 start addr is 0x%x, end addr is 0x%x and size is 0x%x"%(update_mem_1["start"],update_mem_1["start"]+update_mem_1["size"],update_mem_1["size"]))
        if n > 1:
            warning("Error mem %s start is %x and size is %x"%(selected_mem["name"],selected_mem["start"],selected_mem["size"]))
            self.Error_exit("Update mem error!")
        
       
    def Find_mem(self,size,align,mem,**cond):
        if "start" in cond.keys(): 
            cond["start"] = cond["start"]
        else: 
            cond["start"] = mem["start"]
        if "end" in cond.keys(): 
            cond["end"] = cond["end"]
        else: 
            cond["end"] = mem["start"]+mem["size"]
        if "name" not in cond.keys():
            cond["name"] = "No_Name"
        size = size
        cond["start"] = int(align*math.ceil(cond["start"]/align))
        tmp_mem_start = int(align*math.ceil(mem["start"]/align))  
        if cond["start"] >= mem["start"] and cond["start"]+size <= cond["end"] <= mem["start"]+mem["size"]:#included case
            debug("mem match type 1")
            return {"start":random.randrange(cond["start"],cond["end"]-size+1,align),"size":size, "name":cond["name"]}
        elif mem["start"] <= cond["start"] and mem["size"]+mem["start"] >= cond["start"] + size:
            debug("mem match type 2")
            return {"start":random.randrange(cond["start"],mem["start"]+mem["size"]-size+1,align),"size":size, "name":cond["name"]}
        elif cond["end"] >= tmp_mem_start >= cond["start"] and tmp_mem_start+size <= min(mem["start"]+mem["size"],cond["end"]):
            #debug("1 mem_start is %x"%(mem["start"]))
            debug("mem match type 3")
            #debug("2 mem_start is %x and align is %x,mem size is %x"%(tmp_mem_start,align,mem["size"]))
            debug("mem type3: start addr is 0x%x and size is 0x%x"%(mem["start"],mem["size"]))
            debug("tmp_mem_start is 0x%x"%(tmp_mem_start))
            debug("range end is 0x%x"%(min(mem["start"]+mem["size"],cond["end"])-size+1))
            random_mem_type3 = {"start":random.randrange(tmp_mem_start,(min(mem["start"]+mem["size"],cond["end"])-size+1),align),"size":size, "name":cond["name"]}
            debug("random mem type3: start addr is 0x%x and size is 0x%x"%(random_mem_type3["start"],random_mem_type3["size"]))
            return random_mem_type3
        else:
            pass