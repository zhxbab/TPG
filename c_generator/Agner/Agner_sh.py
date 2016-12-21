#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
' Agner_sh '
__author__ = 'Ken Zhao'
########################################################
# Agner_sh is used to change Agner sh to fit Agner.py
########################################################
import os, sys, logging, random, signal, re, stat
from optparse import OptionParser
global instr
global instr1
global instr2
global mode
global imm
global regsize
global ioffset
global moffset
global scalef
global misalign
global count
global regtype1
global regtype2
global repeat2
global noplen
global nnops
global jmp_per_16b
global jmptaken
global lockprefix
global taken
global repp
global addrsize
global flag
global msize
global tcase
global addrmode
global numimm
global instr3
global divlo
global divhi
global divisor
global numop
global iregsize
def init_vars():
    global instr
    global instr1
    global instr2
    global instr3
    global mode
    global imm
    global regsize
    global ioffset
    global scalef
    global misalign
    global count
    global regtype1
    global regtype2
    global repeat2
    global noplen
    global nnops
    global jmp_per_16b
    global jmptaken
    global lockprefix
    global taken
    global repp
    global moffset
    global addrsize
    global basereg
    global flag
    global msize
    global tcase
    global addrmode
    global numimm
    global divlo
    global divhi
    global divisor
    global numop
    global iregsize
    instr=""
    instr1=""
    instr2=""
    instr3=""
    mode=""
    imm = ""
    regsize=""
    ioffset=""
    scalef=""
    misalign=""
    count=""
    regtype1=""
    regtype2=""
    repeat2=""
    nnops=""
    noplen=""
    jmp_per_16b=""
    jmptaken=""
    lockprefix=""
    taken=""
    repp=""
    addrsize=""
    moffset=""
    basereg=""
    msize=""
    tcase=""
    addrmode=""
    numimm=""
    divlo=""
    divhi=""
    divisor=""
    numop=""
    iregsize=""
    flag=0
def format_vars(var):
    index = var.find("$",0)
    if index != -1:
        if index == 0:
            var = "${%s}"%(var[1:])            
        else:
            var = "%s_${%s}"%(var[0:index],var[index+1:])
    else:
        pass
    return var
def get_name_str():
    global instr
    global instr1
    global instr2
    global instr3
    global mode
    global imm
    global regsize
    global ioffset
    global scalef
    global misalign
    global count
    global regtype1
    global regtype2
    global repeat2
    global noplen
    global nnops
    global jmp_per_16b
    global jmptaken
    global lockprefix
    global taken
    global repp
    global moffset
    global addrsize
    global basereg
    global flag
    global msize
    global tcase
    global numimm
    global divlo
    global divhi
    global divisor
    global numop
    global iregsize
    if instr != "" and instr1 !="":
        instr = "%s_"%(instr)
    if instr1 != "" and instr2 !="":
        instr1 = "%s_"%(instr1)
    if instr2 != "" and instr3 !="":
        instr2 = "%s_"%(instr2)
    if repp != "":
        repp = "%s_"%(repp)
    if flag == 1:
        flag_str = "_elf32"
    elif flag == 2:
        flag_str = "_elf64"
    else:
        print("Not flag str, Error!")
    return repp+instr+instr1+instr2+instr3+nnops+noplen+jmp_per_16b+jmptaken+lockprefix+addrsize+basereg+msize+tcase+iregsize+\
        numop+divlo+divhi+divisor+numimm+addrmode+taken+imm+regsize+regtype1+regtype2+ioffset+moffset+scalef+count+misalign+repeat2+\
        mode+flag_str

args_parser = OptionParser(usage="%Agner *args, **kwargs", version="%Agner 0.1")
args_parser.add_option("-f","--file", dest="sh_file", help="The Agner sh file", type="str", default = None)
(args_option, args_additions) = args_parser.parse_args(sys.argv[1:])
current_dir_path = os.path.abspath(".") # current dir path
if not args_option.sh_file == None:
    sh_file = os.path.join(current_dir_path,args_option.sh_file)
else:
    print("Input file wrong!")
    sys.exit(0)
new_sh_file = "%s_new.%s"%(sh_file.split(".")[0],sh_file.split(".")[1])
fn = open(new_sh_file,"w")
init_vars()
with open(sh_file,"r") as fsh:
    while True:
        line = fsh.readline()
        if line:
            line = line.strip()
            m = re.search(r">",line)
            if m:
                line =line.replace(">","#>")
            m = re.search(r"\./x",line)
            if m:
                line = "#%s"%(line)
            m = re.search(r'-Drepp=(.*?) ',line)
            if m:
                repp = format_vars(m.group(1))
            m = re.search(r'-Dinstruct=(.*?) ',line)
            if m:
                instr = format_vars(m.group(1))
                
            m = re.search(r'-Dinstruct1=(.*?) ',line)
            if m:
                instr1 = format_vars(m.group(1))
            m = re.search(r'-Dinstruct2=(.*?) ',line)
            if m:
                instr2 = format_vars(m.group(1)) 
            m = re.search(r'-Dinstruct3=(.*?) ',line)
            if m:
                instr3 = format_vars(m.group(1))                 
            m = re.search(r'-Dtmode=(.*?) ',line)
            if m:
                mode = format_vars(m.group(1))
                mode = "_%s"%(mode)  
                
            m = re.search(r'-Dimmvalue=(.*?) ',line)
            if m:
                imm = format_vars(m.group(1))
                imm = "_imm_%s"%(imm)
                
            m = re.search(r'-Dregsize=(.*?) ',line)
            if m:
                regsize = format_vars(m.group(1))
                regsize = "_regsize_%s"%(regsize)
                
            m = re.search(r'-Dscalef=(.*?) ',line)
            if m:
                scalef = format_vars(m.group(1))
                scalef = "_scalef_%s"%(scalef)
                
            m = re.search(r'-Dioffset=(.*?) ',line)
            if m:
                ioffset = format_vars(m.group(1))
                ioffset = "_ioffset_%s"%(ioffset)
                
            m = re.search(r'-Dmoffset=(.*?) ',line)
            if m:
                moffset = format_vars(m.group(1))
                moffset = "_moffset_%s"%(moffset)
                  
            m = re.search(r'-Dcount=(.*?) ',line)
            if m:
                count = format_vars(m.group(1))
                count = "_count_%s"%(count)
                
            m = re.search(r'-Dmisalign=(.*?) ',line)
            if m:
                misalign = format_vars(m.group(1))
                misalign = "_misalign_%s"%(misalign)                
            m = re.search(r'-Dregtype1=(.*?) ',line)
            if m:
                regtype1 = format_vars(m.group(1))
                regtype1 = "_regtype1_%s"%(regtype1)
            m = re.search(r'-Dregtype2=(.*?) ',line)
            if m:
                regtype2 = format_vars(m.group(1))
                regtype2 = "_regtype2_%s"%(regtype2)             
            m = re.search(r'-Drepeat2=(.*?) ',line)
            if m:
                repeat2 = format_vars(m.group(1))
                repeat2 = "_repeat2_%s"%(repeat2)
            m = re.search(r'-Dnoplen=(.*?) ',line)
            if m:
                noplen = format_vars(m.group(1))
                noplen = "_noplen_%s"%(noplen)
            m = re.search(r'-Dnnops=(.*?) ',line)
            if m:
                nnops = format_vars(m.group(1))
                nnops = "_nnops_%s"%(nnops)
            m = re.search(r'-Djmp_per_16b=(.*?) ',line)
            if m:
                jmp_per_16b = format_vars(m.group(1))
                jmp_per_16b = "_jmp_per_16b_%s"%(jmp_per_16b)
            m = re.search(r'-Djmptaken=(.*?) ',line)
            if m:
                jmptaken = format_vars(m.group(1))
                jmptaken = "_jmptaken_%s"%(jmptaken)
            m = re.search(r'-Dtaken=(.*?) ',line)
            if m:
                taken = format_vars(m.group(1))
                taken = "_taken_%s"%(taken)
            m = re.search(r'-Dlockprefix=(.*?) ',line)
            if m:
                lockprefix = format_vars(m.group(1))
                lockprefix = "_lockprefix_%s"%(lockprefix)
            m = re.search(r'-Daddrsize=(.*?) ',line)
            if m:
                addrsize = format_vars(m.group(1))
                addrsize = "_addrsize_%s"%(addrsize)
            m = re.search(r'-Dbasereg=(.*?) ',line)
            if m:
                basereg = format_vars(m.group(1))
                basereg = "_basereg_%s"%(basereg)
            m = re.search(r'-Dmsize=(.*?) ',line)
            if m:
                msize = format_vars(m.group(1))
                msize = "_msize_%s"%(msize)
            m = re.search(r'-Dtcase=(.*?) ',line)
            if m:
                tcase = format_vars(m.group(1))
                tcase = "_tcase_%s"%(tcase)
            m = re.search(r'-Daddrmode=(.*?) ',line)
            if m:
                addrmode = format_vars(m.group(1))
                addrmode = "_addrmode_%s"%(addrmode)
            m = re.search(r'-Dnumimm=(.*?) ',line)
            if m:
                numimm = format_vars(m.group(1))
                numimm = "_numimm_%s"%(numimm)
            m = re.search(r'-Ddivlo=(.*?) ',line)
            if m:
                divlo = format_vars(m.group(1))
                divlo = "_divlo_%s"%(divlo)
            m = re.search(r'-Ddivhi=(.*?) ',line)
            if m:
                divhi = format_vars(m.group(1))
                divhi = "_divhi_%s"%(divhi)
            m = re.search(r'-Ddivisor=(.*?) ',line)
            if m:
                divisor = format_vars(m.group(1))
                divisor = "_divisor_%s"%(divisor)
            m = re.search(r'-Diregsize=(.*?) ',line)
            if m:
                iregsize = format_vars(m.group(1))
                iregsize = "_iregsize_%s"%(iregsize)
            m = re.search(r'-Dnumop=(.*?) ',line)
            if m:
                numop = format_vars(m.group(1))
                numop = "_numop_%s"%(numop)
            m = re.search(r'TemplateB32.nasm',line)
            if m:
                flag = 1
            m = re.search(r'TemplateB64.nasm',line)
            if m:
                flag = 2                
                #lockprefix = "_lockprefix_%s"%(lockprefix)               
           # -Dnnops=$nnops -Djmp_per_16b=2 -Djmptaken=$jmptaken -Dlockprefix=$lockprefix -Dtaken=alternate
  #      -Dregtype1=m$regtype1 -Dregtype2=r$regtype2 -Dmoffset=$moffset
            m = re.search(r"g\+\+ -m64 a64\.o b64\.o -ox -lpthread",line)
            if m:
                name_str = get_name_str()
                fn.write("name=%s\n"%(name_str))               
                fn.write("mkdir ${name}\n")
                fn.write("g++ -m64 a64.o b64.o -o${name}/${name}.elf -lpthread -static\n")
                init_vars()
                continue
            m = re.search(r"g\+\+ a64\.o b64\.o -ox -lpthread",line)
            if m:
                name_str = get_name_str()
                fn.write("name=%s\n"%(name_str))            
                fn.write("mkdir ${name}\n")
                fn.write("g++ a64.o b64.o -o${name}/${name}.elf -lpthread -static\n")
                init_vars()
                continue
            m = re.search(r"g\+\+ -m32 a32\.o b32\.o -ox -lpthread",line)
            if m:
                name_str = get_name_str()
                fn.write("name=%s\n"%(name_str))               
                fn.write("mkdir ${name}\n")
                fn.write("g++ -m32 a32.o b32.o -o${name}/${name}.elf -lpthread -static\n")
                init_vars()
                continue
            m = re.search(r"g\+\+ a32\.o b32\.o -ox -lpthread",line)
            if m:
                name_str = get_name_str()
                fn.write("name=%s\n"%(name_str))               
                fn.write("mkdir ${name}\n")
                fn.write("g++ a32.o b32.o -o${name}/${name}.elf -lpthread -static\n")
                init_vars()
                continue
            fn.write("%s\n"%(line))
        else:
            break
fn.write("#Tested\n")
fn.close()
os.chmod(new_sh_file,stat.S_IREAD|stat.S_IWRITE|stat.S_IEXEC)
print("New sh file is %s"%(new_sh_file))



#Gather instructions:
#
#
#Test modes:
#
#NONE:         Throughput. Do nothing. Mask = 0
#
#ONE:          Throughput. Load only one data item
#
#CONTIGUOUS:   Throughput. Load contiguous data items
#
#STRIDE:       Throughput. Load data items with a stride of 4 items
#
#RANDOM:       Throughput. Load items in no particular order
#
#SAME:         Throughput. Some items are the same. Use as shuffle
#
#PART_OVERLAP: Throughput. Data items are partially overlapping
#
#LATENCY:      Latency. Load + store
#
#LATENCY_I:    Latency. Load + VPOR + store
#
#LATENCY_F:    Latency. Load + VMAXPS + store
#
#(All tests include a move instruction to set the mask register.