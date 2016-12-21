#!/usr/bin/env python2.7
import os,sys
path = os.getcwd()
if path == "/media/Data_Linux/tools/tpg/c_generator/Agner/TestScripts":
    all_list = os.listdir(path)
    for item in all_list:
        real_path = os.path.join(os.getcwd(),item)
        if os.path.isdir(real_path):
            print("rm -rf %s"%(real_path))
            os.system("rm -rf %s"%(real_path))
else:
    print("This script only can use in /media/Data_Linux/tools/tpg/c_generator/Agner/TestScripts")