import ROOT
import os
import glob
import json
from UserCode.ICHiggsTauTau.analysis import *
from UserCode.ICHiggsTauTau.uncertainties import ufloat
from optparse import OptionParser
import argparse
import ConfigParser
import UserCode.ICHiggsTauTau.plotting as plotting
from collections import OrderedDict
import copy

CHANNELS= ['tpzmm','tpzee']

conf_parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    add_help=False
    )
conf_parser.add_argument("--cfg",
                    help="Specify config file", metavar="FILE")
options, remaining_argv = conf_parser.parse_known_args()

defaults = { "channel":"tpzmm" , "outputfolder":"tagandprobe", "folder":"/vols/cms/dw515/Offline/output/SM/TagAndProbe/SingleLepton/" , "paramfile":"scripts/Params_2016_smsummer16.json","era":"smsummer16", "embedded":False, "em_iso":False, "aiso1":False, "aiso2":False, "ttbins":False, "taudm":"", "embed_sel":False }

if options.cfg:
    config = ConfigParser.SafeConfigParser()
    config.read([options.cfg])
    defaults.update(dict(config.items("Defaults")))

parser = argparse.ArgumentParser(
    parents=[conf_parser]
    )
parser.set_defaults(**defaults)
parser.add_argument("--channel", dest="channel", type=str,
    help="Tau decay channel to process.  Supported channels: %(CHANNELS)s" % vars())
parser.add_argument("--outputfolder", dest="outputfolder", type=str,
    help="Name of output folder")
parser.add_argument("--folder", dest="folder", type=str,
    help="Name of input folder")
parser.add_argument("--paramfile", dest="paramfile", type=str,
    help="Name of parameter file")
parser.add_argument("--era", dest="era", type=str,
    help="Era")
parser.add_argument("--embedded", dest="embedded", action='store_true',
    help="Produce scale-factors for embedded samples.")
parser.add_argument("--em_iso", dest="em_iso", action='store_true',
    help="Use iso-cuts defined for emu channel.")
parser.add_argument("--aiso1", dest="aiso1", action='store_true',
    help="Compute scale-factors or anti-isolated region 1.")
parser.add_argument("--aiso2", dest="aiso2", action='store_true',
    help="Compute scale-factors or anti-isolated region 2.")
parser.add_argument("--ttbins", dest="ttbins", action='store_true',
    help="Use tt channel trigger bins.")
parser.add_argument("--taudm", dest="taudm", type=str,
    help="If specified then does efficincies for set tau decay mode.")
parser.add_argument("--embed_sel", dest="embed_sel", action='store_true',
    help="Do scale-factors for embedding trgger selection")

options = parser.parse_args(remaining_argv)   

print ''
print '################### Options ###################'
print 'channel           = ' + options.channel
print 'outputfolder      = ' + options.outputfolder
print 'folder            = ' + options.folder
print 'paramfile         = ' + options.paramfile
print 'era               = ' + options.era
print 'embedded          =', options.embedded
print 'em_iso            =', options.em_iso
print 'aiso1             =', options.aiso1
print 'aiso2             =', options.aiso2
print 'ttbins            =', options.ttbins
print 'tau decay mode    =', options.taudm
print '###############################################'
print ''

# Add data sample names
if options.channel == 'tpzmm' or options.channel == 'tpmt': 
    data_samples = ['SingleMuonB','SingleMuonC','SingleMuonD','SingleMuonE','SingleMuonF','SingleMuonG','SingleMuonHv2','SingleMuonHv3']
if  options.channel == 'tpzee' or options.channel == 'tpem': 
    data_samples = ['SingleElectronB','SingleElectronC','SingleElectronD','SingleElectronE','SingleElectronF','SingleElectronG','SingleElectronHv2','SingleElectronHv3']

# Add MC sample names   
ztt_samples = ['DYJetsToLL-LO-ext1','DYJetsToLL-LO-ext2']

embed_samples = []
if options.channel == 'tpmt': embed_samples = ['EmbeddingMuTauB','EmbeddingMuTauC','EmbeddingMuTauD','EmbeddingMuTauE','EmbeddingMuTauF','EmbeddingMuTauG','EmbeddingMuTauH']
if options.channel == 'tpzmm': embed_samples = ['EmbeddingMuMuB','EmbeddingMuMuC','EmbeddingMuMuD','EmbeddingMuMuE','EmbeddingMuMuF','EmbeddingMuMuG','EmbeddingMuMuH']
if options.channel == 'tpzee': embed_samples = ['EmbeddingElElB','EmbeddingElElC','EmbeddingElElD','EmbeddingElElE','EmbeddingElElF','EmbeddingElElG','EmbeddingElElH']
if options.channel == 'tpem': embed_samples = ['EmbeddingElMuB','EmbeddingElMuC','EmbeddingElMuD','EmbeddingElMuE','EmbeddingElMuF','EmbeddingElMuG','EmbeddingElMuH']

ROOT.TH1.SetDefaultSumw2(True)

trg_probe_1 = '(trg_probe_1)'
trg_probe_2 = '(trg_probe_2)'
id_probe_1 = '(id_probe_1)'
id_probe_2 = '(id_probe_2)'
if options.channel == 'tpzmm':
  iso_cut_1='iso_1<0.15'
  iso_cut_2='iso_2<0.15'
  if options.aiso1:
    iso_cut_1='iso_1>=0.15&&iso_1<0.25'  
    iso_cut_2='iso_2>=0.15&&iso_2<0.25'
  if options.aiso2:
    iso_cut_1='iso_1>=0.25&&iso_1<0.5'  
    iso_cut_2='iso_2>=0.25&&iso_2<0.5'  
  if options.em_iso:
    iso_cut_1='iso_1<0.2'    
    iso_cut_2='iso_2<0.2'
    if options.aiso1:
      iso_cut_1='iso_1>=0.2&&iso_1<0.3'  
      iso_cut_2='iso_2>=0.2&&iso_2<0.3'
    if options.aiso2:
      iso_cut_1='iso_1>=0.3&&iso_1<0.5'  
      iso_cut_2='iso_2>=0.3&&iso_2<0.5' 
      
  baseline_tag1 = '(m_vis>80&&m_vis<100&&pt_1>25&&abs(eta_1)<2.1&&iso_1<0.15&&id_tag_1&&trg_tag_1&&os)'
  baseline_tag2 = '(m_vis>80&&m_vis<100&&pt_2>25&&abs(eta_2)<2.1&&iso_2<0.15&&id_tag_2&&trg_tag_2&&os)'
  
  if options.embed_sel:
    baseline_tag1 = '(m_vis>80&&m_vis<100&&pt_1>25&&abs(eta_1)<2.1&&iso_1<0.15&&id_tag_1&&trg_tag_1&&os)'
    baseline_tag2 = '(m_vis>80&&m_vis<100&&pt_2>25&&abs(eta_2)<2.1&&iso_2<0.15&&id_tag_2&&trg_tag_2&&os)'    

  if options.embed_sel:
    iso_cut_1="1"
    iso_cut_2="1"
  iso_probe_1 = '(%s)' % iso_cut_1
  iso_probe_2 = '(%s)' % iso_cut_2
  trg_tag_1 = baseline_tag1+'*(%s&&id_probe_1)' % iso_cut_2
  trg_tag_2 = baseline_tag2+'*(%s&&id_probe_1)' % iso_cut_1
  id_tag_1 = baseline_tag1 
  id_tag_2 = baseline_tag2 
if options.channel == 'tpzee':
  iso_cut_1='iso_1<0.1'
  iso_cut_2='iso_2<0.1'
  if options.aiso1:
    iso_cut_1='iso_1>=0.1&&iso_1<0.25'  
    iso_cut_2='iso_2>=0.1&&iso_2<0.25'
  if options.aiso2:
    iso_cut_1='iso_1>=0.25&&iso_1<0.5'  
    iso_cut_2='iso_2>=0.25&&iso_2<0.5'  
  if options.em_iso:
    iso_cut_1='iso_1<0.15'    
    iso_cut_2='iso_2<0.15'
    if options.aiso1:
      iso_cut_1='iso_1>=0.15&&iso_1<0.3'  
      iso_cut_2='iso_2>=0.15&&iso_2<0.3'
    if options.aiso2:
      iso_cut_1='iso_1>=0.3&&iso_1<0.5'  
      iso_cut_2='iso_2>=0.3&&iso_2<0.5'  
  
  baseline_tag1 = '(m_vis>80&&m_vis<100&&pt_1>25&&abs(eta_1)<2.1&&iso_1<0.1&&id_tag_1&&trg_tag_1&&os)'
  baseline_tag2 = '(m_vis>80&&m_vis<100&&pt_2>25&&abs(eta_2)<2.1&&iso_2<0.1&&id_tag_2&&trg_tag_2&&os)'
  iso_probe_1 = '(%s)' % iso_cut_1
  iso_probe_2 = '(%s)' % iso_cut_2
  trg_tag_1 = baseline_tag1+'*(%s&&id_tag_2)' % iso_cut_2
  trg_tag_2 = baseline_tag2+'*(%s&&id_tag_1)' % iso_cut_1
  id_tag_1 = baseline_tag1 
  id_tag_2 = baseline_tag2
if options.channel == 'tpem': 
  iso_cut_1='iso_1<0.15'    
  iso_cut_2='iso_2<0.15'
  baseline_tag1 = '(m_vis>70&&m_vis<110&&pt_1>25&&abs(eta_1)<2.1&&iso_1<0.1&&id_tag_1&&trg_tag_1&&os&&gen_match_1==3&&gen_match_2==4)'
  baseline_tag2 = '(m_vis>70&&m_vis<110&&pt_2>25&&abs(eta_2)<2.1&&iso_2<0.1&&id_tag_2&&trg_tag_2&&os&&gen_match_1==3&&gen_match_2==4)'
  if options.aiso1:
    iso_cut_1='iso_1>=0.15&&iso_1<0.3'  
    iso_cut_2='iso_2>=0.15&&iso_2<0.3'
  if options.aiso2:
    iso_cut_1='iso_1>=0.3&&iso_1<0.5'  
    iso_cut_2='iso_2>=0.3&&iso_2<0.5'  
  
  baseline_tag1 = '(0)'
  baseline_tag2 = '(gen_match_1==3&&gen_match_2==4)'
  iso_probe_1 = '(%s)' % iso_cut_1
  iso_probe_2 = '(%s)' % iso_cut_2
  trg_tag_1 = baseline_tag1+'*(%s&&id_tag_2)' % iso_cut_2
  trg_tag_2 = baseline_tag2+'*(%s&&id_tag_1)' % iso_cut_1
  id_tag_1 = baseline_tag1 
  id_tag_2 = baseline_tag2  
if options.channel == 'tpmt':
  iso_cut_1='iso_1<0.15'
  iso_cut_2='iso_tight'
  if options.aiso1:  
    iso_cut_2='iso_medium'
  if options.aiso2:
    iso_cut_2='iso_loose'  

  #baseline_tag1 = '(m_vis>40&&m_vis<80&&mt_1<30&&pzeta>-25&&n_bjets==0&&lepton_veto==0&&pt_1>25&&abs(eta_1)<2.1&&iso_1<0.15&&id_tag_1&&trg_tag_1&&id_probe_2&&pass_antilep)'
  if options.taudm: baseline_tag1+="&&dm==%s" % options.taudm

  idiso_probe_2 = '(%s)' % iso_cut_2
  trg_tag_1 = baseline_tag1+'*(%s)' % iso_cut_2 # reqires probe to pass id/iso cut as well!
  
  # add W-jets MC samples. mt channel eta bins 0,1.5,2.1. tt channels no eta bins. antimuon different for mt and tt so add additional bool 

iso_tag_1 = baseline_tag1+'*(id_tag_2)'
if options.channel != 'tpmt': iso_tag_2 = baseline_tag2+'*(id_tag_1)'

# All functions defined here

def BuildCutString(wt='', sel='', cat='', sign='os',bkg_sel=''):
    full_selection = '(1)'
    if wt != '':
        full_selection = '('+wt+')'
    if sel != '':
        full_selection += '*('+sel+')'
    if sign != '':
        full_selection += '*('+sign+')'
    if bkg_sel != '':
        full_selection += '*('+bkg_sel+')'
    if cat != '':
        full_selection += '*('+cat+')'
    return full_selection

def GetZLLNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat=''):
    full_selection = BuildCutString(wt, sel, cat, 'os', '1')
    if options.channel == 'tpmt': full_selection = BuildCutString(wt, sel, cat, 'os-(os==0)', '1')
    return ana.SummedFactory('ZLL'+add_name, samples, plot, full_selection)

def GetDataNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat=''):
    full_selection = BuildCutString(wt, sel, cat, 'os', '1')
    if options.channel == 'tpmt': full_selection = BuildCutString(wt, sel, cat, 'os-(os==0)', '1')
    return ana.SummedFactory('data'+add_name, samples, plot, full_selection)

def GetEmbeddedNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat=''):
    full_selection = BuildCutString(wt, sel, cat, 'os', '1')
    if options.channel == 'tpmt': full_selection = BuildCutString(wt, sel, cat, 'os-(os==0)', '1')
    return ana.SummedFactory('EmbedZLL'+add_name, samples, plot, full_selection)

def GenerateZLL(ana, add_name='', samples=[], plot='', wt='', sel='', cat=''):
    zll_node = GetZLLNode(ana, add_name, samples, plot, wt, sel, cat)
    ana.nodes[nodename].AddNode(zll_node)

def GenerateData(ana, add_name='', samples=[], plot='', wt='', sel='', cat=''):
    data_node = GetDataNode(ana, add_name, samples, plot, wt, sel, cat)
    ana.nodes[nodename].AddNode(data_node)

def GenerateEmbedded(ana, add_name='', samples=[], plot='', wt='', sel='', cat=''):
    embed_node = GetEmbeddedNode(ana, add_name, samples, plot, wt, sel, cat)
    ana.nodes[nodename].AddNode(embed_node)
    
def RunTagAndProbePlotting(ana, wt='wt', outfile=None):
    
    if options.channel == 'tpzmm':
      idiso_eta_bins = '[0,0.9,1.2,2.1,2.4]'
      idiso_pt_bins = '[10,15,20,25,30,40,50,60,80,100,200,1000]'
      trg_eta_bins = '[0,0.9,1.2,2.1,2.4]'
      trg_pt_bins = '[15,18,19,20,21,22,23,24,25,30,40,50,60,80,100,200,1000]'
      if options.em_iso: 
        idiso_eta_bins = '[0,0.9,1.2,2.1,2.4]'  
        idiso_pt_bins = '[10,15,20,25,30,40,50,60,70,100,1000]'
        trg_eta_bins = '[0,0.9,1.2,2.1,2.4]'
        #trg_pt_bins = '[10,12,14,16,18,20,22,24,26,28,31,34,37,40,45,50,60,70,100,1000]'
        trg_pt_bins = '[10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,31,34,37,40,45,50,60,70,100,200,1000]' # low pt leg
        #trg_pt_bins = '[10,20,22,23,24,25,26,27,28,31,34,37,40,45,50,60,70,100,200,1000]' # high pt leg
      if options.embed_sel:
        #trg_eta_bins = '[0,0.1,0.3,0.8,1.0,1.2,1.6,1.8,2.1,2.4]' #mu8
        #trg_eta_bins = '(24,0,2.4)'
        #trg_pt_bins='[20,40]'
        trg_eta_bins = '[0,0.1,0.2,0.3,0.8,0.9,1.2,1.6,1.8,2.1,2.4]' # mu 17
        #trg_pt_bins = '[10,12,14,16,18,20,22,24,26,28,31,34,37,40,45,50,60,70,100,1000]' 'mu8
        trg_pt_bins = '[10,15,17,19,21,23,24,25,26,27,28,31,34,37,40,45,50,60,70,100,1000]' # mu17
        trg_eta_bins='[0,2.4]'
        trg_pt_bins = '[10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,31,34,37,40,45,50,60,70,100,1000]'
    if options.channel == 'tpzee':
      idiso_eta_bins = '[0,1,1.4442,1.56,2.1,2.5]'
      idiso_pt_bins = '[10,20,25,30,40,50,100,200,1000]'
      trg_eta_bins = '[0,1,1.4442,1.56,2.1,2.5]'
      trg_pt_bins = '[10,20,22,24,26,28,30,40,50,100,200,1000]'
      if options.em_iso: 
          idiso_eta_bins = '[0,1.48,2.1,2.5]'
          idiso_pt_bins = '[10,15,20,25,30,40,50,60,70,100,1000]'
          trg_eta_bins = '[0,1.48,2.1,2.5]'
          #trg_pt_bins = '[10,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,31,34,37,40,45,50,60,70,100,200,1000]'    # low pt leg
          trg_pt_bins = '[10,20,22,23,24,25,26,27,28,31,34,37,40,45,50,60,70,100,200,1000]' # high pt leg
    
    if options.channel == 'tpem':
      idiso_eta_bins = '[0,0.9,1.2,2.1,2.4]'  
      idiso_pt_bins = '[10,15,20,25,30,40,50,60,70,100,1000]'
      trg_eta_bins = '[0,0.9,1.2,2.1,2.4]'
      trg_pt_bins = '[10,13,16,17,18,19,20,21,22,23,24,25,26,27,28,31,34,37,40,45,50,60,70,100,200,1000]'
      
    if options.channel == 'tpmt':
      idiso_pt_bins = '[20,25,30,40,50,100,200,1000]'
      idiso_eta_bins = '[0,2.1]'
      trg_pt_bins = '[10,20,22,24,26,28,30,40,50,100,200,1000]'
      trg_eta_bins = '[0,2.1]'
    
    trg_plot_probe_1 = 'abs(eta_1),pt_1'+trg_eta_bins+','+trg_pt_bins
    trg_plot_probe_2 = 'abs(eta_2),pt_2'+trg_eta_bins+','+trg_pt_bins
    idiso_plot_probe_1 = 'abs(eta_1),pt_1'+idiso_eta_bins+','+idiso_pt_bins
    idiso_plot_probe_2 = 'abs(eta_2),pt_2'+idiso_eta_bins+','+idiso_pt_bins

    GenerateZLL(ana, '_trg_tag1_denum', ztt_samples, trg_plot_probe_2, wt, trg_tag_1, '1')
    GenerateZLL(ana, '_trg_tag2_denum', ztt_samples, trg_plot_probe_1, wt, trg_tag_2, '1')
    GenerateZLL(ana, '_trg_tag1_num', ztt_samples, trg_plot_probe_2, wt, trg_tag_1, trg_probe_2)
    GenerateZLL(ana, '_trg_tag2_num', ztt_samples, trg_plot_probe_1, wt, trg_tag_2, trg_probe_1)    
    GenerateData(ana, '_trg_tag1_denum', data_samples, trg_plot_probe_2, wt, trg_tag_1, '1')
    GenerateData(ana, '_trg_tag2_denum', data_samples, trg_plot_probe_1, wt, trg_tag_2, '1')
    GenerateData(ana, '_trg_tag1_num', data_samples, trg_plot_probe_2, wt, trg_tag_1, trg_probe_2)
    GenerateData(ana, '_trg_tag2_num', data_samples, trg_plot_probe_1, wt, trg_tag_2, trg_probe_1)
    
    GenerateZLL(ana, '_id_tag1_denum', ztt_samples, idiso_plot_probe_2, wt, id_tag_1, '1')
    GenerateZLL(ana, '_id_tag2_denum', ztt_samples, idiso_plot_probe_1, wt, id_tag_2, '1')
    GenerateZLL(ana, '_id_tag1_num', ztt_samples, idiso_plot_probe_2, wt, id_tag_1, id_probe_2)
    GenerateZLL(ana, '_id_tag2_num', ztt_samples, idiso_plot_probe_1, wt, id_tag_2, id_probe_1)    
    GenerateData(ana, '_id_tag1_denum', data_samples, idiso_plot_probe_2, wt, id_tag_1, '1')
    GenerateData(ana, '_id_tag2_denum', data_samples, idiso_plot_probe_1, wt, id_tag_2, '1')
    GenerateData(ana, '_id_tag1_num', data_samples, idiso_plot_probe_2, wt, id_tag_1, id_probe_2)
    GenerateData(ana, '_id_tag2_num', data_samples, idiso_plot_probe_1, wt, id_tag_2, id_probe_1)
    
    GenerateZLL(ana, '_iso_tag1_denum', ztt_samples, idiso_plot_probe_2, wt, iso_tag_1, '1')
    GenerateZLL(ana, '_iso_tag2_denum', ztt_samples, idiso_plot_probe_1, wt, iso_tag_2, '1')
    GenerateZLL(ana, '_iso_tag1_num', ztt_samples, idiso_plot_probe_2, wt, iso_tag_1, iso_probe_2)
    GenerateZLL(ana, '_iso_tag2_num', ztt_samples, idiso_plot_probe_1, wt, iso_tag_2, iso_probe_1)   
    GenerateData(ana, '_iso_tag1_denum', data_samples, idiso_plot_probe_2, wt, iso_tag_1, '1')
    GenerateData(ana, '_iso_tag2_denum', data_samples, idiso_plot_probe_1, wt, iso_tag_2, '1')
    GenerateData(ana, '_iso_tag1_num', data_samples, idiso_plot_probe_2, wt, iso_tag_1, iso_probe_2)
    GenerateData(ana, '_iso_tag2_num', data_samples, idiso_plot_probe_1, wt, iso_tag_2, iso_probe_1)
    
    
    if options.embedded:
       
      GenerateEmbedded(ana, '_trg_tag1_denum', embed_samples, trg_plot_probe_2, wt+'*(wt<2)', trg_tag_1, '1')
      GenerateEmbedded(ana, '_trg_tag2_denum', embed_samples, trg_plot_probe_1, wt+'*(wt<2)', trg_tag_2, '1')
      GenerateEmbedded(ana, '_trg_tag1_num', embed_samples, trg_plot_probe_2, wt+'*(wt<2)', trg_tag_1, trg_probe_2)
      GenerateEmbedded(ana, '_trg_tag2_num', embed_samples, trg_plot_probe_1, wt+'*(wt<2)', trg_tag_2, trg_probe_1)
         
      GenerateEmbedded(ana, '_id_tag1_denum', embed_samples, idiso_plot_probe_2, wt+'*(wt<2)', id_tag_1, '1')
      GenerateEmbedded(ana, '_id_tag2_denum', embed_samples, idiso_plot_probe_1, wt+'*(wt<2)', id_tag_2, '1')
      GenerateEmbedded(ana, '_id_tag1_num', embed_samples, idiso_plot_probe_2, wt+'*(wt<2)', id_tag_1, id_probe_2)
      GenerateEmbedded(ana, '_id_tag2_num', embed_samples, idiso_plot_probe_1, wt+'*(wt<2)', id_tag_2, id_probe_1)
       
      GenerateEmbedded(ana, '_iso_tag1_denum', embed_samples, idiso_plot_probe_2, wt+'*(wt<2)', iso_tag_1, '1')
      GenerateEmbedded(ana, '_iso_tag2_denum', embed_samples, idiso_plot_probe_1, wt+'*(wt<2)', iso_tag_2, '1')
      GenerateEmbedded(ana, '_iso_tag1_num', embed_samples, idiso_plot_probe_2, wt+'*(wt<2)', iso_tag_1, iso_probe_2)
      GenerateEmbedded(ana, '_iso_tag2_num', embed_samples, idiso_plot_probe_1, wt+'*(wt<2)', iso_tag_2, iso_probe_1)

    
    ana.Run()
    ana.nodes.Output(outfile)
    
    zll_trg_denum = outfile.Get(nodename+'/ZLL_trg_tag1_denum')
    zll_trg_denum.Add(outfile.Get(nodename+'/ZLL_trg_tag2_denum'))
    zll_trg_num = outfile.Get(nodename+'/ZLL_trg_tag1_num')
    zll_trg_num.Add(outfile.Get(nodename+'/ZLL_trg_tag2_num'))
    
    data_trg_denum = outfile.Get(nodename+'/data_trg_tag1_denum')
    data_trg_denum.Add(outfile.Get(nodename+'/data_trg_tag2_denum'))
    data_trg_num = outfile.Get(nodename+'/data_trg_tag1_num')
    data_trg_num.Add(outfile.Get(nodename+'/data_trg_tag2_num'))
    
    zll_id_denum = outfile.Get(nodename+'/ZLL_id_tag1_denum')
    zll_id_denum.Add(outfile.Get(nodename+'/ZLL_id_tag2_denum'))
    zll_id_num = outfile.Get(nodename+'/ZLL_id_tag1_num')
    zll_id_num.Add(outfile.Get(nodename+'/ZLL_id_tag2_num'))
    
    data_id_denum = outfile.Get(nodename+'/data_id_tag1_denum')
    data_id_denum.Add(outfile.Get(nodename+'/data_id_tag2_denum'))
    data_id_num = outfile.Get(nodename+'/data_id_tag1_num')
    data_id_num.Add(outfile.Get(nodename+'/data_id_tag2_num'))
    
    zll_iso_denum = outfile.Get(nodename+'/ZLL_iso_tag1_denum')
    zll_iso_denum.Add(outfile.Get(nodename+'/ZLL_iso_tag2_denum'))
    zll_iso_num = outfile.Get(nodename+'/ZLL_iso_tag1_num')
    zll_iso_num.Add(outfile.Get(nodename+'/ZLL_iso_tag2_num'))
    
    data_iso_denum = outfile.Get(nodename+'/data_iso_tag1_denum')
    data_iso_denum.Add(outfile.Get(nodename+'/data_iso_tag2_denum'))
    data_iso_num = outfile.Get(nodename+'/data_iso_tag1_num')
    data_iso_num.Add(outfile.Get(nodename+'/data_iso_tag2_num'))

    
    data_trg_num_proj   = data_trg_num.ProjectionX()
    zll_trg_num_proj    = zll_trg_num.ProjectionX()
    data_id_num_proj    = data_id_num.ProjectionX()
    zll_id_num_proj     = zll_id_num.ProjectionX()
    data_iso_num_proj   = data_iso_num.ProjectionX()
    zll_iso_num_proj    = zll_iso_num.ProjectionX()
    
    data_trg_denum_proj   = data_trg_denum.ProjectionX()
    zll_trg_denum_proj    = zll_trg_denum.ProjectionX()
    data_id_denum_proj    = data_id_denum.ProjectionX()
    zll_id_denum_proj     = zll_id_denum.ProjectionX()
    data_iso_denum_proj   = data_iso_denum.ProjectionX()
    zll_iso_denum_proj    = zll_iso_denum.ProjectionX()
    
    data_trg_gr   = ROOT.TGraphAsymmErrors(data_trg_num.GetNbinsX())
    data_iso_gr   = ROOT.TGraphAsymmErrors(data_iso_num.GetNbinsX())
    data_id_gr    = ROOT.TGraphAsymmErrors(data_id_num.GetNbinsX())
    mc_trg_gr   = ROOT.TGraphAsymmErrors(zll_trg_num.GetNbinsX())
    mc_iso_gr   = ROOT.TGraphAsymmErrors(zll_iso_num.GetNbinsX())
    mc_id_gr    = ROOT.TGraphAsymmErrors(zll_id_num.GetNbinsX())
    
    data_trg_gr.Divide(data_trg_num_proj,data_trg_denum_proj,"n")
    mc_trg_gr.Divide(zll_trg_num_proj,zll_trg_denum_proj,"n") 
    data_id_gr.Divide(data_id_num_proj,data_id_denum_proj,"n")
    mc_id_gr.Divide(zll_id_num_proj,zll_id_denum_proj,"n")
    data_iso_gr.Divide(data_iso_num_proj,data_iso_denum_proj,"n")
    mc_iso_gr.Divide(zll_iso_num_proj,zll_iso_denum_proj,"n")
    
    if options.embedded:
      
      embed_trg_denum = outfile.Get(nodename+'/EmbedZLL_trg_tag1_denum')
      embed_trg_denum.Add(outfile.Get(nodename+'/EmbedZLL_trg_tag2_denum'))
      embed_trg_num = outfile.Get(nodename+'/EmbedZLL_trg_tag1_num')
      embed_trg_num.Add(outfile.Get(nodename+'/EmbedZLL_trg_tag2_num'))
      
      embed_id_denum = outfile.Get(nodename+'/EmbedZLL_id_tag1_denum')
      embed_id_denum.Add(outfile.Get(nodename+'/EmbedZLL_id_tag2_denum'))
      embed_id_num = outfile.Get(nodename+'/EmbedZLL_id_tag1_num')
      embed_id_num.Add(outfile.Get(nodename+'/EmbedZLL_id_tag2_num'))
      
      embed_iso_denum = outfile.Get(nodename+'/EmbedZLL_iso_tag1_denum')
      embed_iso_denum.Add(outfile.Get(nodename+'/EmbedZLL_iso_tag2_denum'))
      embed_iso_num = outfile.Get(nodename+'/EmbedZLL_iso_tag1_num')
      embed_iso_num.Add(outfile.Get(nodename+'/EmbedZLL_iso_tag2_num'))
    
      
      embed_trg_num_proj   = embed_trg_num.ProjectionX()
      embed_id_num_proj    = embed_id_num.ProjectionX()
      embed_iso_num_proj   = embed_iso_num.ProjectionX()
      
      embed_trg_denum_proj   = embed_trg_denum.ProjectionX()
      embed_id_denum_proj    = embed_id_denum.ProjectionX()
      embed_iso_denum_proj   = embed_iso_denum.ProjectionX()
      
      embed_trg_gr   = ROOT.TGraphAsymmErrors(embed_trg_num.GetNbinsX())
      embed_iso_gr   = ROOT.TGraphAsymmErrors(embed_iso_num.GetNbinsX())
      embed_id_gr    = ROOT.TGraphAsymmErrors(embed_id_num.GetNbinsX())
      
      embed_trg_gr.Divide(embed_trg_num_proj,embed_trg_denum_proj,"n")
      embed_id_gr.Divide(embed_id_num_proj,embed_id_denum_proj,"n")
      embed_iso_gr.Divide(embed_iso_num_proj,embed_iso_denum_proj,"n")
    
    if options.channel == 'tpzmm': sfs_output_name = options.outputfolder+'/muon_SFs.root'
    if options.channel == 'tpzee' or options.channel == 'tpem': sfs_output_name = options.outputfolder+'/electron_SFs.root'
    sfs_output = ROOT.TFile(sfs_output_name, 'RECREATE')
    sfs_output.cd()
    
    data_trg_gr.Write('data_trg_proj')
    mc_trg_gr.Write('mc_trg_proj')
    #data_id_gr.Write('data_id_proj') 
    mc_id_gr.Write('mc_id_proj') 
    #data_iso_gr.Write('data_iso_proj')
    mc_iso_gr.Write('mc_iso_proj')
    
    trg_graphs = [sfs_output.Get('data_trg_proj'),sfs_output.Get('mc_trg_proj')]
    id_graphs = [data_id_gr,sfs_output.Get('mc_id_proj')]
    iso_graphs = [data_iso_gr,sfs_output.Get('mc_iso_proj')]
    
    if options.embedded:
        
      embed_trg_gr.Write('embed_trg_proj')
      embed_id_gr.Write('embed_id_proj') 
      embed_iso_gr.Write('embed_iso_proj')
      
      trg_graphs.append(sfs_output.Get('embed_trg_proj'))
      id_graphs.append(sfs_output.Get('embed_id_proj'))
      iso_graphs.append(sfs_output.Get('embed_iso_proj'))
    
    if options.channel == 'tpzmm': 
        x_title = 'P_{T}^{#mu} (GeV)'
        plot_name = 'muon_efficiency_'
    if options.channel == 'tpzee' or options.channel == 'tpem':
        x_title = 'P_{T}^{e} (GeV)'
        plot_name = 'electron_efficiency_'

    if options.era=='mssmsummer16': x_max = 1000
    else: x_max = 100
    leg_labels=['data','MC']
    if options.embedded: leg_labels=['data','MC','Embedded']
    plotting.TagAndProbePlot(trg_graphs,leg_labels,"",True,False,options.era=='mssmsummer16',"0.7,1.3",True,x_max,0,False,0,1,x_title, "Efficiency",0,options.outputfolder+'/'+plot_name+'trg',"trigger")
    plotting.TagAndProbePlot(id_graphs,leg_labels,"",True,False,options.era=='mssmsummer16',"0.7,1.3",True,x_max,0,False,0,1,x_title, "Efficiency",0,options.outputfolder+'/'+plot_name+'id',"ID")
    plotting.TagAndProbePlot(iso_graphs,leg_labels,"",True,False,options.era=='mssmsummer16',"0.7,1.3",True,x_max,0,False,0,1,x_title, "Efficiency",0,options.outputfolder+'/'+plot_name+'iso',"isolation")
    
    if options.embedded:
      plotting.TagAndProbePlot([mc_id_gr,embed_id_gr],['MC','Embedded'],"",True,False,options.era=='mssmsummer16',"0.7,1.3",True,x_max,0,False,0,1,x_title, "Efficiency",0,options.outputfolder+'/'+plot_name+'id_nodata',"ID")
      plotting.TagAndProbePlot([mc_iso_gr,embed_iso_gr],['MC','Embedded'],"",True,False,options.era=='mssmsummer16',"0.7,1.3",True,x_max,0,False,0,1,x_title, "Efficiency",0,options.outputfolder+'/'+plot_name+'iso_nodata',"isolation")


    
    data_trg_num.Divide(data_trg_denum)
    zll_trg_num.Divide(zll_trg_denum)
    data_id_num.Divide(data_id_denum)
    zll_id_num.Divide(zll_id_denum)
    data_iso_num.Divide(data_iso_denum)
    zll_iso_num.Divide(zll_iso_denum)
    
    data_trg_num.SetName("trg_data")
    zll_trg_num.SetName("trg_mc")
    data_id_num.SetName("id_data")
    zll_id_num.SetName("id_mc")
    data_iso_num.SetName("iso_data")
    zll_iso_num.SetName("iso_mc")
    
    #hists = [data_trg_num,zll_trg_num,data_id_num,zll_id_num,data_iso_num,zll_iso_num]
    hists = [data_trg_num,zll_trg_num,zll_id_num,zll_iso_num]
    
    if options.embedded:
        embed_trg_num.Divide(embed_trg_denum)
        embed_id_num.Divide(embed_id_denum)
        embed_iso_num.Divide(embed_iso_denum)
        
        embed_trg_num.SetName("trg_embed")
        embed_id_num.SetName("id_embed")
        embed_iso_num.SetName("iso_embed")
        
        hists.append(embed_trg_num)
        hists.append(embed_id_num)
        hists.append(embed_iso_num)
    
    # set overflow pT bins to same value as last bin and write to file
    for hist in hists:
      for i in range(1,hist.GetNbinsY()+1): 
        hist.SetBinContent(hist.GetNbinsX()+1,i,hist.GetBinContent(hist.GetNbinsX(),i))
      hist.Write()
      
def RunTauTagAndProbePlotting(ana, wt='wt', outfile=None):
      
    if options.channel == 'tpmt':
      idiso_pt_bins = '[20,25,30,40,50,100]'
      idiso_eta_bins = '[0,1.5,2.1]'
      trg_eta_bins = '[0,1.5,2.1]'
      trg_pt_bins = '[10,20,22,24,26,28,30,35,40,50,100]'
      if options.ttbins:  
        #trg_pt_bins = '[30,35,40,45,50,60,80,200]'
        #trg_pt_bins = '[30,35,40,45,50,60,80,100,160]'
        trg_pt_bins = '[20,25,30,32,34,36,38,42,44,48,52,58,64,80,120,160]'
        if options.taudm == '0': trg_pt_bins = '[30,35,40,45,50,60,80,100,160]'
        #trg_eta_bins = '[0,2.1]'
        trg_eta_bins = '[0,2.1]'
    
    trg_plot_probe_2 = 'abs(eta_2),pt_2'+trg_eta_bins+','+trg_pt_bins
    idiso_plot_probe_2 = 'abs(eta_2),pt_2'+idiso_eta_bins+','+idiso_pt_bins

    GenerateZLL(ana, '_trg_tag1_denum', ztt_samples, trg_plot_probe_2, wt, trg_tag_1, '1')
    GenerateZLL(ana, '_trg_tag1_num', ztt_samples, trg_plot_probe_2, wt, trg_tag_1, trg_probe_2)   
    GenerateData(ana, '_trg_tag1_denum', data_samples, trg_plot_probe_2, wt, trg_tag_1, '1')
    GenerateData(ana, '_trg_tag1_num', data_samples, trg_plot_probe_2, wt, trg_tag_1, trg_probe_2)
    
    GenerateZLL(ana, '_idiso_tag1_denum', ztt_samples, idiso_plot_probe_2, wt, baseline_tag1, '1')
    GenerateZLL(ana, '_idiso_tag1_num', ztt_samples, idiso_plot_probe_2, wt, baseline_tag1, idiso_probe_2)   
    GenerateData(ana, '_idiso_tag1_denum', data_samples, idiso_plot_probe_2, wt, baseline_tag1, '1')
    GenerateData(ana, '_idiso_tag1_num', data_samples, idiso_plot_probe_2, wt, baseline_tag1, idiso_probe_2)

    if options.embedded:
       
      GenerateEmbedded(ana, '_trg_tag1_denum', embed_samples, trg_plot_probe_2, wt, trg_tag_1, '1')
      GenerateEmbedded(ana, '_trg_tag1_num', embed_samples, trg_plot_probe_2, wt, trg_tag_1, trg_probe_2)
  
      GenerateEmbedded(ana, '_idiso_tag1_denum', embed_samples, idiso_plot_probe_2, wt, baseline_tag1, '1')
      GenerateEmbedded(ana, '_idiso_tag1_num', embed_samples, idiso_plot_probe_2, wt, baseline_tag1, idiso_probe_2)
    
    ana.Run()
    ana.nodes.Output(outfile)
    
    zll_trg_denum = outfile.Get(nodename+'/ZLL_trg_tag1_denum')
    zll_trg_num = outfile.Get(nodename+'/ZLL_trg_tag1_num')
    
    data_trg_denum = outfile.Get(nodename+'/data_trg_tag1_denum')
    data_trg_num = outfile.Get(nodename+'/data_trg_tag1_num')
    
    zll_idiso_denum = outfile.Get(nodename+'/ZLL_idiso_tag1_denum')
    zll_idiso_num = outfile.Get(nodename+'/ZLL_idiso_tag1_num')
    
    data_idiso_denum = outfile.Get(nodename+'/data_idiso_tag1_denum')
    data_idiso_num = outfile.Get(nodename+'/data_idiso_tag1_num')
    
    data_trg_num_proj   = data_trg_num.ProjectionX()
    zll_trg_num_proj    = zll_trg_num.ProjectionX()
    data_idiso_num_proj = data_idiso_num.ProjectionX()
    zll_idiso_num_proj  = zll_idiso_num.ProjectionX()
    
    data_trg_denum_proj   = data_trg_denum.ProjectionX()
    zll_trg_denum_proj    = zll_trg_denum.ProjectionX()
    data_idiso_denum_proj = data_idiso_denum.ProjectionX()
    zll_idiso_denum_proj  = zll_idiso_denum.ProjectionX()
    
    data_trg_gr   = ROOT.TGraphAsymmErrors(data_trg_num.GetNbinsX())
    data_idiso_gr = ROOT.TGraphAsymmErrors(data_idiso_num.GetNbinsX())
    mc_trg_gr   = ROOT.TGraphAsymmErrors(zll_trg_num.GetNbinsX())
    mc_idiso_gr = ROOT.TGraphAsymmErrors(zll_idiso_num.GetNbinsX())
    
    data_trg_gr.Divide(data_trg_num_proj,data_trg_denum_proj,"n")
    mc_trg_gr.Divide(zll_trg_num_proj,zll_trg_denum_proj,"n") 
    data_idiso_gr.Divide(data_idiso_num_proj,data_idiso_denum_proj,"n")
    mc_idiso_gr.Divide(zll_idiso_num_proj,zll_idiso_denum_proj,"n")
    
    if options.ttbins:
      # for efficiencies binned in eta
      mc_trg_num_proj_bin1   = zll_trg_num.ProjectionX("",1,1)
      #mc_trg_num_proj_bin2   = zll_trg_num.ProjectionX("",2,2)
      mc_trg_denum_proj_bin1   = zll_trg_denum.ProjectionX("",1,1)
      #mc_trg_denum_proj_bin2   = zll_trg_denum.ProjectionX("",2,2)
      mc_trg_gr_bin1   = ROOT.TGraphAsymmErrors(zll_trg_num.GetNbinsX())
      #mc_trg_gr_bin2   = ROOT.TGraphAsymmErrors(zll_trg_num.GetNbinsX())
      mc_trg_gr_bin1.Divide(mc_trg_num_proj_bin1,mc_trg_denum_proj_bin1,"n")
      #mc_trg_gr_bin2.Divide(mc_trg_num_proj_bin2,mc_trg_denum_proj_bin2,"n")
    
      data_trg_num_proj_bin1   = data_trg_num.ProjectionX("",1,1)
      #data_trg_num_proj_bin2   = data_trg_num.ProjectionX("",2,2)
      data_trg_denum_proj_bin1   = data_trg_denum.ProjectionX("",1,1)
      #data_trg_denum_proj_bin2   = data_trg_denum.ProjectionX("",2,2)
      data_trg_gr_bin1   = ROOT.TGraphAsymmErrors(data_trg_num.GetNbinsX())
      #data_trg_gr_bin2   = ROOT.TGraphAsymmErrors(data_trg_num.GetNbinsX())
      data_trg_gr_bin1.Divide(data_trg_num_proj_bin1,data_trg_denum_proj_bin1,"n")
      #data_trg_gr_bin2.Divide(data_trg_num_proj_bin2,data_trg_denum_proj_bin2,"n")
    
    if options.embedded:
      
      embed_trg_denum = outfile.Get(nodename+'/EmbedZLL_trg_tag1_denum')
      embed_trg_num = outfile.Get(nodename+'/EmbedZLL_trg_tag1_num')
      
      embed_idiso_denum = outfile.Get(nodename+'/EmbedZLL_idiso_tag1_denum')
      embed_idiso_num = outfile.Get(nodename+'/EmbedZLL_idiso_tag1_num')
      
      embed_trg_num_proj   = embed_trg_num.ProjectionX()
      embed_idiso_num_proj = embed_idiso_num.ProjectionX()
      
      embed_trg_denum_proj   = embed_trg_denum.ProjectionX()
      embed_idiso_denum_proj = embed_idiso_denum.ProjectionX()
      
      embed_trg_gr   = ROOT.TGraphAsymmErrors(embed_trg_num.GetNbinsX())
      embed_idiso_gr = ROOT.TGraphAsymmErrors(embed_idiso_num.GetNbinsX())
      
      embed_trg_gr.Divide(embed_trg_num_proj,embed_trg_denum_proj,"n")
      embed_idiso_gr.Divide(embed_idiso_num_proj,embed_idiso_denum_proj,"n")
      
      if options.ttbins:
        # for efficiencies binned in eta
        embed_trg_num_proj_bin1   = embed_trg_num.ProjectionX("",1,1)
        #embed_trg_num_proj_bin2   = embed_trg_num.ProjectionX("",2,2)
        embed_trg_denum_proj_bin1   = embed_trg_denum.ProjectionX("",1,1)
        #embed_trg_denum_proj_bin2   = embed_trg_denum.ProjectionX("",2,2)
        embed_trg_gr_bin1   = ROOT.TGraphAsymmErrors(embed_trg_num.GetNbinsX())
        #embed_trg_gr_bin2   = ROOT.TGraphAsymmErrors(embed_trg_num.GetNbinsX())
        embed_trg_gr_bin1.Divide(embed_trg_num_proj_bin1,embed_trg_denum_proj_bin1,"n")
        #embed_trg_gr_bin2.Divide(embed_trg_num_proj_bin2,embed_trg_denum_proj_bin2,"n")
    
    if options.channel == 'tpmt': sfs_output_name = options.outputfolder+'/tau_SFs.root'
    sfs_output = ROOT.TFile(sfs_output_name, 'RECREATE')
    sfs_output.cd()
    
    data_trg_gr.Write('data_trg_proj')
    mc_trg_gr.Write('mc_trg_proj')
    data_idiso_gr.Write('data_idiso_proj')
    mc_idiso_gr.Write('mc_idiso_proj')
    
    if options.ttbins:
      data_trg_gr_bin1.Write('data_trg_proj_bin1')    
      #data_trg_gr_bin2.Write('data_trg_proj_bin2')
      mc_trg_gr_bin1.Write('mc_trg_proj_bin1')    
      #mc_trg_gr_bin2.Write('mc_trg_proj_bin2')
    
    trg_graphs = [sfs_output.Get('data_trg_proj'),sfs_output.Get('mc_trg_proj')]
    idiso_graphs = [sfs_output.Get('data_idiso_proj'),sfs_output.Get('mc_idiso_proj')]
    
    if options.embedded:
        
      embed_trg_gr.Write('embed_trg_proj')
      embed_idiso_gr.Write('embed_idiso_proj')
      
      if options.ttbins:
        embed_trg_gr_bin1.Write('embed_trg_proj_bin1')    
        #embed_trg_gr_bin2.Write('embed_trg_proj_bin2')
      
      trg_graphs.append(sfs_output.Get('embed_trg_proj'))
      idiso_graphs.append(sfs_output.Get('embed_idiso_proj'))
    
    if options.channel == 'tpmt': 
        x_title = 'P_{T}^{#tau} (GeV)'
        plot_name = 'tau_efficiency_'

    if options.era=='mssmsummer16': x_max = 1000
    else: x_max = 200
    leg_labels=['data','MC']
    if options.embedded: leg_labels=['data','MC','Embedded']
    plotting.TagAndProbePlot(trg_graphs,leg_labels,"",True,False,options.era=='mssmsummer16',"0.7,1.3",True,x_max,0,False,0,1,x_title, "Efficiency",0,options.outputfolder+'/'+plot_name+'trg',"trigger")
    plotting.TagAndProbePlot(idiso_graphs,leg_labels,"",True,False,options.era=='mssmsummer16',"0.7,1.3",True,x_max,0,False,0,1,x_title, "Efficiency",0,options.outputfolder+'/'+plot_name+'idiso',"ID-isolation")
    if options.ttbins:
      plotting.TagAndProbePlot([data_trg_gr_bin1,embed_trg_gr_bin1],['data','Embedded'],"",True,False,options.era=='mssmsummer16',"2,3",True,x_max,0,False,0,1,x_title, "Efficiency",0,options.outputfolder+'/'+plot_name+'trg_bin1',"trigger")
      #plotting.TagAndProbePlot([data_trg_gr_bin2,embed_trg_gr_bin2],['data','Embedded'],"",True,False,options.era=='mssmsummer16',"1.7,3",True,x_max,0,False,0,1,x_title, "Efficiency",0,options.outputfolder+'/'+plot_name+'trg_bin2',"trigger #eta > 1.5")
    
    data_trg_num.Divide(data_trg_denum)
    zll_trg_num.Divide(zll_trg_denum)
    data_idiso_num.Divide(data_idiso_denum)
    zll_idiso_num.Divide(zll_idiso_denum)
    
    data_trg_num.SetName("trg_data")
    zll_trg_num.SetName("trg_mc")
    data_idiso_num.SetName("idiso_data")
    zll_idiso_num.SetName("idiso_mc")
    
    hists = [data_trg_num,zll_trg_num,data_idiso_num,zll_idiso_num]
    
    if options.embedded:
        embed_trg_num.Divide(embed_trg_denum)
        embed_idiso_num.Divide(embed_idiso_denum)
        
        embed_trg_num.SetName("trg_embed")
        embed_idiso_num.SetName("idiso_embed")
        
        hists.append(embed_trg_num)
        hists.append(embed_idiso_num)
    
    # set overflow pT bins to same value as last bin and write to file
    for hist in hists:
      for i in range(1,hist.GetNbinsY()+1): 
        hist.SetBinContent(hist.GetNbinsX()+1,i,hist.GetBinContent(hist.GetNbinsX(),i))
      hist.Write()
      

# Create output file

output_name = options.outputfolder+'/tagandprobe_'+options.channel+'.root'
outfile = ROOT.TFile(output_name, 'RECREATE')

nodename = options.channel
ana = Analysis()
ana.nodes.AddNode(ListNode(nodename))

ana.remaps = {}
if options.channel =='tpzmm': ana.remaps['SingleMuon'] = 'data_obs'
elif options.channel == 'tpzee' or options.channel == 'tpem': ana.remaps['SingleElectron'] = 'data_obs'
elif options.channel == 'tpmt': ana.remaps['SingleMuon'] = 'data_obs'


# Add all data files
for sample_name in data_samples:
    ana.AddSamples(options.folder+'/'+sample_name+'_'+options.channel+'*.root', 'tagandprobe', None, sample_name)

# Add all MC background files
for sample_name in ztt_samples:
    ana.AddSamples(options.folder+'/'+sample_name+'_'+options.channel+'*.root', 'tagandprobe', None, sample_name)

if options.embedded:
  # Add all embedded files
  for sample_name in embed_samples:
      ana.AddSamples(options.folder+'/'+sample_name+'_'+options.channel+'*.root', 'tagandprobe', None, sample_name)

if options.channel == 'tpmt': RunTauTagAndProbePlotting(ana, 'wt', outfile)
else: RunTagAndProbePlotting(ana, 'wt', outfile)

 
