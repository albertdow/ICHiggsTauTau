#!/usr/bin/env python

import sys
import os
from optparse import OptionParser
import math
import fnmatch
import glob

parser = OptionParser()

parser.add_option("--folder", dest = "folder",
                  help="Specify folder that contains the output to be hadded")
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
batch = options.batch

JOBWRAPPER      = './scripts/generate_job.sh'
JOBSUBMIT       = './scripts/submit_ic_batch_job.sh "hep.q -l h_rt=0:180:0"'

sample_list = [
    'DY1JetsToLL-LO',
    'DY1JetsToLL-LO-ext',
    'DY2JetsToLL-LO',
    'DY2JetsToLL-LO-ext',
    'DY3JetsToLL-LO',
    'DY3JetsToLL-LO-ext',
    'DY4JetsToLL-LO',
    'DYJetsToLL',
    'DYJetsToLL-LO',
    'DYJetsToLL-LO-ext1',
    'DYJetsToLL-ext',
    'DYJetsToLL_M-10-50-LO',
    'DYJetsToLL_M-10-50-LO-ext1',
    'EWKWMinus2Jets',
    'EWKWPlus2Jets',
    'EWKZ2Jets',
    'EmbeddingElElB',
    'EmbeddingElElC',
    'EmbeddingElElD',
    'EmbeddingElElE',
    'EmbeddingElElF',
    'EmbeddingElMuB',
    'EmbeddingElMuC',
    'EmbeddingElMuD',
    'EmbeddingElMuE',
    'EmbeddingElMuF',
    'EmbeddingElTauB',
    'EmbeddingElTauC',
    'EmbeddingElTauD',
    'EmbeddingElTauE',
    'EmbeddingElTauF',
    'EmbeddingMuMuB',
    'EmbeddingMuMuC',
    'EmbeddingMuMuD',
    'EmbeddingMuMuE',
    'EmbeddingMuMuF',
    'EmbeddingMuTauB',
    'EmbeddingMuTauC',
    'EmbeddingMuTauD',
    'EmbeddingMuTauE',
    'EmbeddingMuTauF',
    'EmbeddingTauTauB',
    'EmbeddingTauTauC',
    'EmbeddingTauTauD',
    'EmbeddingTauTauE',
    'EmbeddingTauTauF',
    'GluGluHToTauTau_M-125',
    'GluGluHToTauTau_M-125-ext',
    'GluGluToHToTauTauPlusTwoJets_M125_amcatnloFXFX',
    'GluGluToHToTauTau_M125_amcatnloFXFX',
    'GluGluToMaxmixHToTauTauPlusTwoJets_M125_amcatnloFXFX',
    'GluGluToMaxmixHToTauTau_M125_amcatnloFXFX',
    'GluGluToPseudoscalarHToTauTauPlusTwoJets_M125_amcatnloFXFX',
    'GluGluToPseudoscalarHToTauTau_M125_amcatnloFXFX',
    'MuonEGB',
    'MuonEGC',
    'MuonEGD',
    'MuonEGE',
    'MuonEGF',
    'SingleElectronB',
    'SingleElectronC',
    'SingleElectronD',
    'SingleElectronE',
    'SingleElectronF',
    'SingleMuonB',
    'SingleMuonC',
    'SingleMuonD',
    'SingleMuonE',
    'SingleMuonF',
    'T-t',
    'T-tW',
    'TTTo2L2Nu',
    'TTToHadronic',
    'TTToSemiLeptonic',
    'TauB',
    'TauC',
    'TauD',
    'TauE',
    'TauF',
    'Tbar-t',
    'Tbar-tW',
    'VBFHToTauTau_M-125',
    'W1JetsToLNu-LO',
    'W2JetsToLNu-LO',
    'W3JetsToLNu-LO',
    'W4JetsToLNu-LO',
    'WGToLNuG',
    'WJetsToLNu-LO',
    'WJetsToLNu-LO-ext',
    'WWTo1L1Nu2Q',
    'WWTo2L2Nu',
    'WWToLNuQQ',
    'WWToLNuQQ-ext',
    'WZTo1L1Nu2Q',
    'WZTo1L3Nu',
    'WZTo2L2Q',
    'WZTo3LNu',
    'WminusHToTauTau_M-125',
    'WplusHToTauTau_M-125',
    'ZHToTauTau_M-125',
    'ZZTo2L2Nu',
    'ZZTo2L2Q',
    'ZZTo2Q2Nu',
    'ZZTo4L',
    'ZZTo4L-ext',
    'ttHToTauTau_M-125',
    'VBFHiggs0MToTauTau',
    'VBFHiggs0Mf05ph0ToTauTau',
    'VBFHiggs0PMToTauTau',
    'WHiggs0MToTauTau',
    'WHiggs0Mf05ph0ToTauTau',
    'WHiggs0PMToTauTau',
    'ZHiggs0MToTauTau',
    'ZHiggs0Mf05ph0ToTauTau',
    'ZHiggs0PMToTauTau',
    'GluGluToHToTauTau_M-125-nospinner',
    'VBFHToTauTau_M-125-nospinner',
    'GluGluToHToTauTau_M125_nospinner-2017',
    'VBFHToTauTau_M125_nospinner-2017',
    'GluGluToHToTauTau_M-125-nospinner-filter',
    'VBFHToTauTau_M-125-nospinner-filter',
    'VBFHToTauTauUncorrelatedDecay_Filtered',
    'WminusHToTauTauUncorrelatedDecay_Filtered',
    'WplusHToTauTauUncorrelatedDecay_Filtered',
    'ZHToTauTauUncorrelatedDecay_Filtered',
	]

channel = ['em','et','mt','tt']

subdirs=['']
subdirs+=list_paths(outputf)

new_subdirs=[]
for d in subdirs:
  infi=os.listdir('%(outputf)s/%(d)s' % vars())
  if infi: new_subdirs.append((d,infi))
subdirs=new_subdirs

print subdirs

failed = []

for sa in sample_list:
  remove=True
  to_remove=[]
  hadd_dirs=[]
  sa = 'svfit_'+sa
  command=''
  if batch:
    JOB='jobs/hadd_%s.sh' % sa
    os.system('%(JOBWRAPPER)s "" %(JOB)s' %vars())
  for ch in channel:
    for jsdir in subdirs:
      sdir = jsdir[0]
      infiles=jsdir[1]
      if os.path.isfile('%(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_0_0_input.root'%vars()):
        if not batch:  
          print "Hadding in subdir %(sdir)s"%vars()
          print "Hadding %(sa)s_%(ch)s in %(sdir)s"%vars()
          os.system('hadd -f %(outputf)s/%(sdir)s/%(sa)s_%(ch)s_2018_input.root %(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_*input.root &> ./haddout.txt'% vars()) 
          os.system("sed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./haddout.txt")
          filetext = open("./haddout.txt").read()
          if 'Warning' in filetext or 'Error' in filetext:
            print "Hadd had a problem:"
            print filetext
            remove=False 
            failed.append(sa) 
          else :
            to_remove.append('rm %(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_*input.root' %vars())
        else:
          haddout='haddout_%s_%s_%s.txt' % (sa,ch,sdir) 
          command+="echo \"Hadding %(sa)s_%(ch)s in %(sdir)s\"\necho \"Hadding %(sa)s_%(ch)s\"\nhadd -f %(outputf)s/%(sdir)s/%(sa)s_%(ch)s_2018_input.root %(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_*input.root &> ./%(haddout)s\nsed -i '/Warning in <TInterpreter::ReadRootmapFile>/d' ./%(haddout)s\nif [ \"$(cat %(haddout)s | grep -e Warning -e Error)\"  == \"\" ]; then rm %(outputf)s/%(sdir)s/%(sa)s_2018_%(ch)s_*input.root; fi\n" % vars()    

  if batch and command:
    with open(JOB, "a") as file: 
      file.write("\n%s" % command)
      file.write('\necho End of job &> jobs/hadd_svfit_%(sa)s.log' % vars())
    os.system('%(JOBSUBMIT)s %(JOB)s' % vars())



