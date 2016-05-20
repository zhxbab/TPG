#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import os, sys
from operator import eq
filelist = os.listdir(os.getcwd())
for i in filelist:
    if eq(i.split(".")[-1],"del"):
        print("Detele %s and its files"%(i))
        os.system("sh %s"%(i))
        os.system("rm -rf %s"%(i))