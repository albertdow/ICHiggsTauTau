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
   'T-tW',
	]

# sample_list = [
#    'gluglutohtotautau_m-110',
#    'gluglutohtotautau_m-120',
#    'gluglutohtotautau_m-125',
#    'gluglutohtotautau_m-130',
#    'gluglutohtotautau_m-140',
#    'tthtotautau_m-120',
#    'tthtotautau_m-125',
#    'tthtotautau_m-130',
#    'vbfhtotautau_m-110',
#    'vbfhtotautau_m-120',
#    'vbfhtotautau_m-125',
#    'vbfhtotautau_m-130',
#    'vbfhtotautau_m-140',
#    'wminushtotautau_m-110',
#    'wminushtotautau_m-120',
#    'wminushtotautau_m-125',
#    'wminushtotautau_m-130',
#    'wminushtotautau_m-140',
#    'wplushtotautau_m-110',
#    'wplushtotautau_m-120',
#    'wplushtotautau_m-125',
#    'wplushtotautau_m-130',
#    'wplushtotautau_m-140',
#    'zhtotautau_m-110',
#    'zhtotautau_m-120',
#    'zhtotautau_m-125',
#    'zhtotautau_m-130',
#    'zhtotautau_m-140',
#    'glugluhtowwto2l2nu_m-125',
#    'vbfhtowwto2l2nu_m-125',
#    'qcdmuenrichedpt15',
#    'tt',
#    'wjetstolnu',
#    'wjetstolnu-lo',
#    'wjetstolnu-lo-ext',
#    'vvto2l2nu',
#    'vvto2l2nu-ext1',
#    'zzto2l2q',
#    'zzto4l',
#    'zzto4l-amcat',
#    'wwto1l1nu2q',
#    'wwtolnuqq',
#    'wwtolnuqq-ext',
#    'wzjtolllnu',
#    'wzto1l3nu',
#    'wzto2l2q',
#    'wzto1l1nu2q',
#    't-t',
#    'tbar-t',
#    't-tw',
#    'tbar-tw',
#    'dyjetstoll',
#    'dyjetstoll-lo',
#    'dyjetstoll-lo-ext1',
#    'dyjetstoll-lo-ext2',
#    'dyjetstoll_m-10to50-ext',
#    'dyjetstoll_m-10to50',
#    'dyjetstoll_m-10-50-lo',
#    'dy1jetstoll_m-10-50-lo',
#    'dy2jetstoll_m-10-50-lo',
#    'dy3jetstoll_m-10-50-lo',
#    'dyjetstoll_m-150-lo',
#    'dy1jetstoll-lo',
#    'dy2jetstoll-lo',
#    'dy3jetstoll-lo',
#    'dy4jetstoll-lo',
#    'w1jetstolnu-lo',
#    'w2jetstolnu-lo',
#    'w2jetstolnu-lo-ext',
#    'w3jetstolnu-lo',
#    'w3jetstolnu-lo-ext',
#    'w4jetstolnu-lo',
#    'w4jetstolnu-lo-ext1',
#    'w4jetstolnu-lo-ext2',
#    'wgtolnug',
#    'wgtolnug-ext',
#    'wgstartolnuee',
#    'wgstartolnumumu',
#    'singlemuonb',
#    'singleelectronb',
#    'muonegb',
#    'taub',
#    'singlemuonc',
#    'singleelectronc',
#    'muonegc',
#    'tauc',
#    'singlemuond',
#    'singleelectrond',
#    'muonegd',
#    'taud',
#    'singlemuone',
#    'singleelectrone',
#    'muonege',
#    'taue',
#    'singlemuonf',
#    'singleelectronf',
#    'muonegf',
#    'tauf',
#    'singlemuong',
#    'singleelectrong',
#    'muonegg',
#    'taug',
#    'singlemuonhv2',
#    'singleelectronhv2',
#    'muoneghv2',
#    'tauhv2',
#    'singlemuonhv3',
#    'singleelectronhv3',
#    'muoneghv3',
#    'tauhv3',
#    'ewkwminus2jets_wtolnu-ext1',
#    'ewkwminus2jets_wtolnu-ext2',
#    'ewkwminus2jets_wtolnu',
#    'ewkwplus2jets_wtolnu-ext1',
#    'ewkwplus2jets_wtolnu-ext2',
#    'ewkwplus2jets_wtolnu',
#    'ewkz2jets_ztoll-ext',
#    'ewkz2jets_ztoll',
#    'ewkz2jets_ztonunu-ext',
#    'ewkz2jets_ztonunu',
#    'glugluh2jetstotautau_m125_cpmixing_pseudoscalar',
#    'glugluh2jetstotautau_m125_cpmixing_maxmix',
#    'glugluh2jetstotautau_m125_cpmixing_sm',
#    'vbfhiggs0m_m-125',
#    'vbfhiggs0mf05ph0_m-125',
#    'vbfhiggs0pm_m-125',
#    'gluglutohtotautau_amcnlo_m-125',
#    'vbfhtotautau_amcnlo_m-125',
#    # 'embeddingmutaub',
#    # 'embeddingmutauc',
#    # 'embeddingmutaud',
#    # 'embeddingmutaue',
#    # 'embeddingmutauf',
#    # 'embeddingmutaug',
#    # 'embeddingmutauh',
#    # 'embeddingelmub',
#    # 'embeddingelmuc',
#    # 'embeddingelmud',
#    # 'embeddingelmue',
#    # 'embeddingelmuf',
#    # 'embeddingelmug',
#    # 'embeddingelmuh',
#    # 'embeddingeltaub',
#    # 'embeddingeltauc',
#    # 'embeddingeltaud',
#    # 'embeddingeltaue',
#    # 'embeddingeltauf',
#    # 'embeddingeltaug',
#    # 'embeddingeltauh',
#    # 'embeddingtautaub',
#    # 'embeddingtautauc',
#    # 'embeddingtautaud',
#    # 'embeddingtautaue',
#    # 'embeddingtautauf',
#    # 'embeddingtautaug',
#    # 'embeddingtautauh',
#    # 'embeddingelelb',
#    # 'embeddingelelc',
#    # 'embeddingeleld',
#    # 'embeddingelele',
#    # 'embeddingelelf',
#    # 'embeddingelelg',
#    # 'embeddingelelh',
#    # 'embeddingmumub',
#    # 'embeddingmumuc',
#    # 'embeddingmumud',
#    # 'embeddingmumue',
#    # 'embeddingmumuf',
#    # 'embeddingmumug',
#    # 'embeddingmumuh'
# 	]

channel = ['em','et','mt','tt','zee','zmm','wmnu','tpzee','tpzmm','tpmt','tpem']
with open("%(samplelist)s"%vars(),"r") as inf:
  lines = inf.readlines()

subdirs = ['TSCALE_DOWN','TSCALE_UP','TSCALE0PI_UP','TSCALE0PI_DOWN','TSCALE1PI_UP','TSCALE1PI_DOWN','TSCALE3PRONG_UP','TSCALE3PRONG_DOWN','JES_UP','JES_DOWN', 'BTAG_UP','BTAG_DOWN','BFAKE_UP','BFAKE_DOWN','MET_SCALE_UP','MET_SCALE_DOWN','MET_RES_UP','MET_RES_DOWN', 'EFAKE0PI_UP', 'EFAKE0PI_DOWN', 'EFAKE1PI_UP', 'EFAKE1PI_DOWN','MUFAKE0PI_UP','MUFAKE0PI_DOWN','MUFAKE1PI_UP','MUFAKE1PI_DOWN','METUNCL_UP','METUNCL_DOWN','METCL_UP','METCL_DOWN','MUSCALE_UP','MUSCALE_DOWN','ESCALE_UP','ESCALE_DOWN','JESFULL_DOWN','JESFULL_UP','JESCENT_UP','JESCENT_DOWN','JESHF_UP','JESHF_DOWN','JESRBAL_UP','JESRBAL_DOWN']

nfiles={}

for ind in range(0,len(lines)):
  nfiles[lines[ind].split()[0]]=int(lines[ind].split()[1])
for sa in sample_list:
  command=''
  if batch:
    JOB='jobs/hadd_%s.sh' % sa
    os.system('%(JOBWRAPPER)s "" %(JOB)s' %vars())
  for ch in channel:
    if os.path.isfile('%(outputf)s/%(sa)s_2016_%(ch)s_0.root'%vars()):
      if "%(sa)s_2016"%vars() in nfiles or ignore==True:
        if ignore==True or len(fnmatch.filter(os.listdir('%(outputf)s'%vars()),'%(sa)s_2016_%(ch)s_*'%vars())) == nfiles["%(sa)s_2016"%vars()]:
          if not batch:
            print "Hadding %(sa)s_%(ch)s"%vars()
            os.system('hadd -fk -k %(outputf)s/%(sa)s_%(ch)s_2016.root %(outputf)s/%(sa)s_2016_%(ch)s_* &> ./haddout.txt'% vars())
            os.system("sed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./haddout.txt")
            filetext = open("./haddout.txt").read()
            if 'Warning' in filetext or 'Error' in filetext:
              print "Hadd had a problem:"
              print filetext
            else :
              os.system('rm %(outputf)s/%(sa)s_2016_%(ch)s_*' %vars())
          else:
            haddout='haddout_%s.txt' % sa
            command+="echo \"Hadding %(sa)s_%(ch)s\"\nhadd -fk -k %(outputf)s/%(sa)s_%(ch)s_2016.root %(outputf)s/%(sa)s_2016_%(ch)s_* &> ./%(haddout)s\nsed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./%(haddout)s\nif [ \"$(cat %(haddout)s | grep -e Warning -e Error)\" != \"\" ]; then echo \"Hadd had a problem:\"\ncat %(haddout)s ; else \nrm %(outputf)s/%(sa)s_2016_%(ch)s_*; fi\n" % vars()
        else :
          print "Incorrect number of files for sample %(sa)s_2016_%(ch)s!"%vars()
    for sdir in subdirs:
      if os.path.isfile('%(outputf)s/%(sdir)s/%(sa)s_2016_%(ch)s_0.root'%vars()):
        if "%(sa)s_2016"%vars() in nfiles or ignore==True:
          if ignore ==True or len(fnmatch.filter(os.listdir('%(outputf)s/%(sdir)s'%vars()),'%(sa)s_2016_%(ch)s_*'%vars())) == nfiles["%(sa)s_2016"%vars()]:
            if not batch:
              print "Hadding in subdir %(sdir)s"%vars()
              print "Hadding %(sa)s_%(ch)s in %(sdir)s"%vars()
              os.system('hadd -fk -k %(outputf)s/%(sdir)s/%(sa)s_%(ch)s_2016.root %(outputf)s/%(sdir)s/%(sa)s_2016_%(ch)s_* &> ./haddout.txt'% vars())
              os.system("sed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./haddout.txt")
              filetext = open("./haddout.txt").read()
              if 'Warning' in filetext or 'Error' in filetext:
                print "Hadd had a problem:"
                print filetext
              else :
                os.system('rm %(outputf)s/%(sdir)s/%(sa)s_2016_%(ch)s_*' %vars())
            else:
              haddout='haddout_%s_%s.txt' % (sa,sdir)
              command+="echo \"Hadding %(sa)s_%(ch)s in %(sdir)s\"\necho \"Hadding %(sa)s_%(ch)s\"\nhadd -fk -k %(outputf)s/%(sdir)s/%(sa)s_%(ch)s_2016.root %(outputf)s/%(sdir)s/%(sa)s_2016_%(ch)s_* &> ./%(haddout)s\nsed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./%(haddout)s\nif [ \"$(cat %(haddout)s | grep -e Warning -e Error)\" != \"\" ]; then echo \"Hadd had a problem:\"\ncat %(haddout)s ;\nelse rm %(outputf)s/%(sdir)s/%(sa)s_2016_%(ch)s_*; fi\n" % vars()
          else :
            print "Incorrect number of files for sample %(sa)s_2016_%(ch)s! in %(sdir)s"%vars()

  if batch and command:
    with open(JOB, "a") as file: file.write("\n%s" % command)
    os.system('%(JOBSUBMIT)s %(JOB)s' % vars())

