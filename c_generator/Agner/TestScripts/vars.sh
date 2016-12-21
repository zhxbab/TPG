#!/bin/bash
# vars.sh                                                        2014-10-01 Agner Fog
# (c) Copyright 2014 by Agner Fog. GNU General Public License www.gnu.org/licenses

# Code to initialize environment variables etc. inside test scripts
# NOTE: run as . vars.sh, not as ./vars.sh

# Choose assembler and possibly extra options
# NASM:
ass="nasm "
# or YASM:
# ass="yasm "

# Is 32-bit mode supported?
if [ `uname -o` = Cygwin ] ; then
support32bit=0
else
support32bit=1
fi

# Variables that depend on CPU brand
# CPUbrand: AMD, Intel, VIA
# blockports: execution ports or pipes that we want to block in order to detect which port or pipe a specific instruction uses
# PMCs: list of PMC counters to use during test. See counter definitions in PMCTestA.cpp (separated by comma without space)
# PMClist: multiple sets of PMC counters if we can't have all desired counters simultaneously (lists separated by space)

# Extract CPU family and model number from cpuinfo.txt
# imodel=`cat cpuinfo.txt | sed -r 's/model[ :\t]+([0-9]+).*/\1/;tx;d;:x;q'`
# ifamily=`cat cpuinfo.txt | sed -r 's/cpu family[ :\t]+([0-9]+).*/\1/;tx;d;:x;q'`

# Get CPU brand, family and model from cpugetinfo program
#CPUbrand=`./cpugetinfo vendor`
CPUbrand='Unknown'
ifamily=`./cpugetinfo family`
imodel=`./cpugetinfo model`

if   [ "$CPUbrand" = "AMD" ] ; then
  blockports="0 1"
  PMCs="9,100,162,150"
  PMClist="9,100,160,150  9,100,161,151 9,100,162,152  9,100,162,153"
  BranchPMCs="9,100,201,204"
  LoopPMCs="9,100,150,310"
  CachePMCs="9,100,311,320"

elif [ "$CPUbrand" = "Intel"  ] ; then
  blockports=
  # blockports="0 1 5"
  BranchPMCs="1,9,100,201,207"
  CachePMCs="1,9,100,311,320"

  if [ $imodel -eq 55 -o $imodel -eq 74 -o $imodel -eq 77 ] ; then
     # Silvermont
     PMCs="1,9,100,150"
     PMClist="1,9,100,158  1,9,150,151  1,9,152,153"
     BranchPMCs="1,9,100,207"
     LoopPMCs="1,9,100,209"
     blockports="0 1 9"
     
  elif [ $imodel -ge 60 ] ; then
     # Haswell
     PMCs="1,9,104,100,150,220"
     PMClist="1,9,100,150,151,152  1,9,100,153,154,155  1,9,100,156,157,104"     
     LoopPMCs="1,9,100,24,26,25"

  elif [ $imodel -ge 58 ] ; then
     # Ivy Bridge
     PMCs="1,9,104,100,150,220"
     PMClist="1,9,104,100,150,151  1,9,152,153,154,155  1,9,220,221"
     LoopPMCs="1,9,100,24,26,25"
  
  elif [ $imodel -ge 42 ] ; then
     # Sandy Bridge
     PMCs="1,9,104,100,150,151"
     PMClist="1,9,100,150,151,152  1,9,100,153,154,155"
     LoopPMCs="1,9,100,24,26,25"
     
else
     # Other
     PMCs="1,9,100,150,160"
     PMClist="1,9,100,150,151  1,9,150,151,155"
     LoopPMCs="1,9,100,104"
     
  fi

elif [ "$CPUbrand" = "VIA"  ] ; then
  blockports=
  PMCs="9,100"
  PMClist="9,100"
  BranchPMCs="9,100"
  
else
  # Unknown vendor
  blockports=
  PMCs="9"
  #PMCs="9,100"
  #PMClist="9,100"
  #BranchPMCs="9,100"
  PMClist="9"
  BranchPMCs="9"
fi
