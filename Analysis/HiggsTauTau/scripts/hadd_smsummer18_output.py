#!/usr/bin/env python

import sys
import os
from optparse import OptionParser
import math
import fnmatch

parser = OptionParser()

parser.add_option("--folder", dest = "folder",
                  help="Specify folder that contains the output to be hadded")
parser.add_option("--ignore_nfiles", dest= "ignore", default=False, action='store_true',
                  help="Ignore number of files per sample")
parser.add_option("--sample_list", dest = "samplelist", default="./jobs/files_per_sample.txt",
                  help="list of files per sample you want to use for hadding")
parser.add_option("--batch", dest= "batch", default=False, action='store_true',
                  help="Submit as batch jobs")

def list_paths(path):
    directories = []
    for item in os.listdir(path):
      if os.path.isdir(os.path.join(path, item)):
        directories.append(item)
    return directories

(options,args) = parser.parse_args()

if not options.folder:
  parser.error('No folder specified')

outputf = options.folder
samplelist = options.samplelist
ignore = options.ignore
batch = options.batch

JOBWRAPPER      = './scripts/generate_job.sh'
JOBSUBMIT       = './scripts/submit_ic_batch_job.sh "hep.q -l h_rt=0:180:0"'


sample_list = [
    'SingleMuonA',
    'SingleMuonB',
    'SingleMuonC',
    'SingleMuonD',
    'DYJetsToLL',
    'DY1JetsToLL-LO',
    'DY2JetsToLL-LO',
    'DY3JetsToLL-LO',
    'DY4JetsToLL-LO',
    'DYJetsToLL-LO',
    'DYJetsToLL_M-10-50-LO',
    'EWKWMinus2Jets',
    'EWKWPlus2Jets',
    'EWKZ2Jets',#new
    'T-t',
    'T-tW-ext1',
    'TTTo2L2Nu',
    'TTToHadronic',
    'TTToSemiLeptonic',
    'Tbar-t',
    'Tbar-tW-ext1',
    'W1JetsToLNu-LO',
    'W2JetsToLNu-LO',
    'W3JetsToLNu-LO',
    'W4JetsToLNu-LO',
    'WGToLNuG',
    # 'WGToLNuG_01J_5f-ext1',
    'WJetsToLNu-LO',
    'WWTo1L1Nu2Q',
    'WWTo2L2Nu',#new
    'WWTo4Q',#new
    'WWToLNuQQ',#new
    'WZTo1L3Nu',
    'WZTo2L2Q',
    'WZTo3LNu',#new
    'WZTo3LNu-ext1',
    'ZZTo2L2Nu-ext1',
    'ZZTo2L2Nu-ext2',
    'ZZTo2L2Q',
    'ZZTo4L',
    'ZZTo4L-ext',
    'VBFHToTauTau_M-125-ext1',
    'GluGluHToTauTau_M-125',
    'WminusHToTauTau_M-125',
    'WplusHToTauTau_M-125',
	]


channel = ['em','et','mt','tt','zee','zmm','wmnu','tpzee','tpzmm','tpmt','tpem']
with open("%(samplelist)s"%vars(),"r") as inf:
  lines = inf.readlines()

subdirs=list_paths(outputf)
#print subdirs
#subdirs = ["JES_UP","JES_DOWN"]
subdirs = []
# subdirs = ['TSCALE_DOWN','TSCALE_UP','TSCALE0PI_UP','TSCALE0PI_DOWN','TSCALE1PI_UP','TSCALE1PI_DOWN','TSCALE3PRONG_UP','TSCALE3PRONG_DOWN','JES_UP','JES_DOWN', 'BTAG_UP','BTAG_DOWN','BFAKE_UP','BFAKE_DOWN','MET_SCALE_UP','MET_SCALE_DOWN','MET_RES_UP','MET_RES_DOWN', 'EFAKE0PI_UP', 'EFAKE0PI_DOWN', 'EFAKE1PI_UP', 'EFAKE1PI_DOWN','MUFAKE0PI_UP','MUFAKE0PI_DOWN','MUFAKE1PI_UP','MUFAKE1PI_DOWN','METUNCL_UP','METUNCL_DOWN','METCL_UP','METCL_DOWN','MUSCALE_UP','MUSCALE_DOWN','ESCALE_UP','ESCALE_DOWN','JESFULL_DOWN','JESFULL_UP','JESCENT_UP','JESCENT_DOWN','JESHF_UP','JESHF_DOWN','JESRBAL_UP','JESRBAL_DOWN','MET_SCALE_NJETS0_DOWN','MET_SCALE_NJETS0_UP','MET_SCALE_NJETS1_DOWN','MET_SCALE_NJETS1_UP','MET_SCALE_NJETS2_DOWN','MET_SCALE_NJETS2_UP','MET_RES_NJETS0_DOWN','MET_RES_NJETS0_UP','MET_RES_NJETS1_DOWN','MET_RES_NJETS1_UP','MET_RES_NJETS2_DOWN','MET_RES_NJETS2_UP','JES_UNCORR_DOWN','JES_UNCORR_UP','JES_CORR_DOWN','JES_CORR_UP','JESFULL_CORR_DOWN','JESFULL_CORR_UP','JESCENT_CORR_UP','JESCENT_CORR_DOWN','JESHF_CORR_UP','JESHF_CORR_DOWN','JESFULL_UNCORR_DOWN','JESFULL_UNCORR_UP','JESCENT_UNCORR_UP','JESCENT_UNCORR_DOWN','JESHF_UNCORR_UP','JESHF_UNCORR_DOWN','JESRSAMP_DOWN','JESRSAMP_UP','JESBBEE1_DOWN','JESBBEE1_UP','JESBBEE1_UNCORR_DOWN','JESBBEE1_UNCORR_UP','JESBBEE1_CORR_DOWN','JESBBEE1_CORR_UP','JESEE2_DOWN','JESEE2_UP','JESEE2_UNCORR_DOWN','JESEE2_UNCORR_UP','JESEE2_CORR_DOWN','JESEE2_CORR_UP']

nfiles={}

for ind in range(0,len(lines)):
  nfiles[lines[ind].split()[0]]=int(lines[ind].split()[1])
for sa in sample_list:
  command=''
  if batch:
    JOB='jobs/hadd_%s.sh' % sa
    os.system('%(JOBWRAPPER)s "" %(JOB)s' %vars())
  for ch in channel:
    if os.path.isfile('%(outputf)s/%(sa)s_2018_%(ch)s_0.root'%vars()):
      if "%(sa)s_2018"%vars() in nfiles or ignore==True:
        if ignore==True or len(fnmatch.filter(os.listdir('%(outputf)s'%vars()),'%(sa)s_2018_%(ch)s_*'%vars())) == nfiles["%(sa)s_2018"%vars()]:
          if not batch:  
            print "Hadding %(sa)s_%(ch)s"%vars()
            os.system('hadd -f %(outputf)s/%(sa)s_%(ch)s_2018.root %(outputf)s/%(sa)s_2018_%(ch)s_* &> ./haddout.txt'% vars()) 
            os.system("sed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./haddout.txt")
            filetext = open("./haddout.txt").read()
            if 'Warning' in filetext or 'Error' in filetext:
              print "Hadd had a problem:"
              print filetext 
            else :
              os.system('rm %(outputf)s/%(sa)s_2018_%(ch)s_*' %vars())
          else:
            haddout='haddout_%s.txt' % sa 
            command+="echo \"Hadding %(sa)s_%(ch)s\"\nhadd -f %(outputf)s/%(sa)s_%(ch)s_2018.root %(outputf)s/%(sa)s_2018_%(ch)s_* &> ./%(haddout)s\nsed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./%(haddout)s\nif [ \"$(cat %(haddout)s | grep -e Warning -e Error)\" != \"\" ]; then echo \"Hadd had a problem:\"\ncat %(haddout)s ; else \nrm %(outputf)s/%(sa)s_2018_%(ch)s_*; fi\n" % vars()
        else :
          print "Incorrect number of files for sample %(sa)s_2018_%(ch)s!"%vars()
    for sdir in subdirs:
      if os.path.isfile('%(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_0.root'%vars()):
        if "%(sa)s_2018"%vars() in nfiles or ignore==True:
          if ignore ==True or len(fnmatch.filter(os.listdir('%(outputf)s/%(sdir)s'%vars()),'%(sa)s_2018_%(ch)s_*'%vars())) == nfiles["%(sa)s_2018"%vars()]:
            if not batch:  
              print "Hadding in subdir %(sdir)s"%vars()
              print "Hadding %(sa)s_%(ch)s in %(sdir)s"%vars()
              os.system('hadd -f %(outputf)s/%(sdir)s/%(sa)s_%(ch)s_2018.root %(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_* &> ./haddout.txt'% vars()) 
              os.system("sed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./haddout.txt")
              filetext = open("./haddout.txt").read()
              if 'Warning' in filetext or 'Error' in filetext:
                print "Hadd had a problem:"
                print filetext 
              else :
                os.system('rm %(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_*' %vars())
            else:
              haddout='haddout_%s_%s.txt' % (sa,sdir)  
              command+="echo \"Hadding %(sa)s_%(ch)s in %(sdir)s\"\necho \"Hadding %(sa)s_%(ch)s\"\nhadd -f %(outputf)s/%(sdir)s/%(sa)s_%(ch)s_2018.root %(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_* &> ./%(haddout)s\nsed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./%(haddout)s\nif [ \"$(cat %(haddout)s | grep -e Warning -e Error)\" != \"\" ]; then echo \"Hadd had a problem:\"\ncat %(haddout)s ;\nelse rm %(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_*; fi\n" % vars()     
          else :
            print "Incorrect number of files for sample %(sa)s_2018_%(ch)s! in %(sdir)s"%vars()

  if batch and command:
    with open(JOB, "a") as file: file.write("\n%s" % command)
    os.system('%(JOBSUBMIT)s %(JOB)s' % vars())
