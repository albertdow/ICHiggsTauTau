#!/usr/bin/env python

#./scripts/makeDatacardsSMCP16.py --cfg=scripts/new_plot_sm_2016_NewPlotting.cfg -c 'mt,tt' scripts/Params_2016_smsummer16.json -s 'cpsummer16_2d'

import sys
from optparse import OptionParser
import os
import string
import shlex
from subprocess import Popen, PIPE

CHANNELS= ['et', 'mt', 'em','tt', 'zmm']

def validate_channel(channel):
  assert channel in CHANNELS, 'Error, channel %(channel)s duplicated or unrecognised' % vars()
  CHANNELS.remove(channel)

def split_callback(option, opt, value, parser):
  setattr(parser.values, option.dest, value.split(','))

def run_command(command):
    print command
    p = Popen(shlex.split(command), stdout = PIPE, stderr = PIPE)
    out, err = p.communicate()
    print out, err
    return out, err

parser = OptionParser()
parser.add_option("-p","--parameterfile", dest="params", type='string',default='',
                  help="Specify the parameter file containing the luminosity and cross section information - can be used to override config file.")
parser.add_option("--cfg", dest="config", type='string',
                  help="The config file that will be passed to HiggsTauTauPlot.py. Parameter file, input folder and signal scheme taken from this cfg file unless overriden by command line options")
parser.add_option("-i","--input", dest="folder", type='string', default='',
                  help="The input folder, containing the output of HTT - can be used to override config file")
parser.add_option("-o","--output", dest="output", type='string', default='',
                  help="The name that will be appended to the datacard inputs.")
parser.add_option("--output_folder", dest="output_folder", type='string', default='./',
                  help="Output folder where plots/datacards will be saved to.")
parser.add_option("-c", "--channels", dest="channels", type='string', action='callback',callback=split_callback,
                  help="A comma separated list of channels to process.  Supported channels: %(CHANNELS)s" % vars())
parser.add_option("--blind", dest="blind", action='store_true', default=False,
                  help="blind data")
parser.add_option("--extra", dest="extra", type='string', default='',
                  help="Extra command line options, applied to every datacard")
parser.add_option("-s", "--scheme", dest="scheme", type='string', default='',
                  help="datacard scheme - can be used to override config file")
parser.add_option("-e", dest="energy", type='string', default='13',
                  help="The C.O.M. energy is written into the datacard name, default is 13")
parser.add_option("--no_shape_systs", dest="no_shape_systs", action='store_true', default=False,
                  help="Do not add shape systematics")
parser.add_option("--total_jes", dest="total_jes", action='store_true', default=False,
                  help="Do total JES uncertainties.")
parser.add_option("--no_split_jes", dest="no_split_jes", action='store_true', default=False,
                  help="If set then the JES uncertainties split by source are not added")
parser.add_option("--regional_jes", dest="regional_jes", action='store_true', default=False,
                  help="Split JES by sources grouped regionally")
parser.add_option("--norm_systs", dest="norm_systs", action='store_true', default=False,
                  help="Add shapes for evaluating normalisation uncerts")
parser.add_option("--year", dest="year", type='string', default='',
                  help="Output names are data-taking year dependent. This value is read from the config file if present")
parser.add_option("--embedding", dest="embedding", action='store_true', default=False,
                  help="Add shapes are embedded samples.")
parser.add_option("--batch", dest="batch", action='store_true', default=False,
                  help="Submit on batch.")

(options, args) = parser.parse_args()
output_folder = options.output_folder
output = options.output
if output:
  output = '-'+output
  print 'Appending "%(output)s" to datacard outputs' % vars()

channels = options.channels

print 'Processing channels:      %(channels)s' % vars()

### Do some validation of the input
helpMsg = "Run 'datacard_inputs.py -h' for help."

if not channels:
  print 'Error, no channels specified. ' + helpMsg
  sys.exit(1)

for channel in channels:
  validate_channel(channel)


CFG=options.config
BLIND = options.blind
BLIND = " "
if options.blind: BLIND = "--blind"
COM = options.energy

#Hacky config file parsing
with open("%(CFG)s"%vars(),"r") as cfgfile:
  lines = cfgfile.readlines()

configmap={}

for ind in range(0,len(lines)):
  if len(lines[ind].split("="))>1:
    configmap[lines[ind].split("=")[0]]=(lines[ind].split("=")[1])
if "signal_scheme" in configmap:
  SCHEME= configmap["signal_scheme"].rstrip('\n')
YEAR=2015
if "year" in configmap:
  YEAR=configmap["year"].rstrip('\n')
FOLDER=configmap["folder"].rstrip('\n')
PARAMS=configmap["paramfile"].rstrip('\n')

#Override config file params
if not options.scheme == "":
  SCHEME=options.scheme
if not options.folder ==  "":
  FOLDER=options.folder
if not options.params == "":
  PARAMS=options.params
if not options.year == "":
  YEAR=options.year


########## Set up schemes and options

#### Always apply these options:

extra_global = ' '


#### Apply these options for specific channels

# update these to latest shape systematics
extra_channel = {
      "et" : ' ',
      "mt" : ' ',
      "tt" : ' ',
      "em" : ' ',
      "zmm" : ' ',
  }
jes_systematics=''
if not options.no_split_jes:
  jes_systematics = ' --syst_scale_j_by_source="CMS_scale_j_SOURCE_13TeV" '
else:
  jes_systematics = ' --syst_scale_j="CMS_scale_j_13TeV" '

common_shape_systematics=' --syst_zwt="CMS_htt_dyShape_13TeV" --syst_tquark="CMS_htt_ttbarShape_13TeV" --syst_qcd_scale="CMS_scale_gg_13TeV" --syst_z_mjj="CMS_htt_zmumuShape_VBF_13TeV" --syst_scale_met_unclustered="CMS_scale_met_unclustered_13TeV" --syst_scale_met_clustered="CMS_scale_met_clustered_13TeV" '

if options.regional_jes:
  common_shape_systematics += ' --syst_scale_j_full="CMS_scale_j_eta0to5_13TeV" --syst_scale_j_cent="CMS_scale_j_eta0to3_13TeV" --syst_scale_j_hf="CMS_scale_j_eta3to5_13TeV" --syst_scale_j_rbal="CMS_scale_j_RelativeBal_13TeV" '
if options.total_jes:
  common_shape_systematics += ' --syst_scale_j="CMS_scale_j_13TeV" '


em_shape_systematics=' --syst_tau_scale="CMS_scale_e_em_13TeV" '
et_shape_systematics=' --syst_efake_0pi_scale="CMS_ZLShape_et_1prong_13TeV" --syst_efake_1pi_scale="CMS_ZLShape_et_1prong1pizero_13TeV" --syst_tau_scale_0pi="CMS_scale_t_1prong_13TeV" --syst_tau_scale_1pi="CMS_scale_t_1prong1pizero_13TeV" --syst_tau_scale_3prong="CMS_scale_t_3prong_13TeV" --syst_w_fake_rate="CMS_htt_jetToTauFake_13TeV" --syst_qcd_shape_wsf="WSFUncert_et_cat_13TeV" --syst_tau_id_dm0="CMS_tauDMReco_1prong_13TeV" --syst_tau_id_dm1="CMS_tauDMReco_1prong1pizero_13TeV" --syst_tau_id_dm10="CMS_tauDMReco_3prong_13TeV" --syst_lfake_dm0="CMS_eFakeTau_1prong_13TeV" --syst_lfake_dm1="CMS_eFakeTau_1prong1pizero_13TeV"  '
mt_shape_systematics=' --syst_mufake_0pi_scale="CMS_ZLShape_mt_1prong_13TeV" --syst_mufake_1pi_scale="CMS_ZLShape_mt_1prong1pizero_13TeV" --syst_tau_scale_0pi="CMS_scale_t_1prong_13TeV" --syst_tau_scale_1pi="CMS_scale_t_1prong1pizero_13TeV" --syst_tau_scale_3prong="CMS_scale_t_3prong_13TeV" --syst_w_fake_rate="CMS_htt_jetToTauFake_13TeV" --syst_qcd_shape_wsf="WSFUncert_mt_cat_13TeV" --syst_tau_id_dm0="CMS_tauDMReco_1prong_13TeV" --syst_tau_id_dm1="CMS_tauDMReco_1prong1pizero_13TeV" --syst_tau_id_dm10="CMS_tauDMReco_3prong_13TeV" --syst_lfake_dm0="CMS_mFakeTau_1prong_13TeV" --syst_lfake_dm1="CMS_mFakeTau_1prong1pizero_13TeV" '
tt_shape_systematics=' --syst_tau_scale_0pi="CMS_scale_t_1prong_13TeV" --syst_tau_scale_1pi="CMS_scale_t_1prong1pizero_13TeV" --syst_tau_scale_3prong="CMS_scale_t_3prong_13TeV" --syst_w_fake_rate="CMS_htt_jetToTauFake_13TeV" '
zmm_shape_systematics=' --folder=/vols/cms/dw515/Offline/output/SM/Apr09/ '


if options.embedding:
  mt_shape_systematics+=' --syst_mu_scale="CMS_scale_m_13TeV" '
  et_shape_systematics+=' --syst_e_scale="CMS_scale_e_13TeV" '
  em_shape_systematics+=' --syst_e_scale="CMS_scale_e_13TeV" --syst_mu_scale="CMS_scale_m_13TeV" '
  common_shape_systematics+=' --syst_embedding_tt="CMS_ttbar_embeded_13TeV" '

extra_channel = {
      "et" : ' '+common_shape_systematics+ ' '+et_shape_systematics,
      "mt" : ' '+common_shape_systematics+ ' '+mt_shape_systematics,
      "tt" : ' '+common_shape_systematics+ ' '+tt_shape_systematics,
      "em" : ' '+common_shape_systematics+ ' '+em_shape_systematics,
      "zmm" : ' '+common_shape_systematics+ ' '+zmm_shape_systematics
  }

if options.no_shape_systs:
  extra_channel = {
      "et" : ' ',
      "mt" : ' ',
      "tt" : ' ',
      "em" : ' ',
      "zmm" : ' '
  }


if SCHEME == 'cpsummer16':

  VAR_0JET_LT = 'tau_decay_mode_2,m_vis[0,1,10],[0,60,65,70,75,80,85,90,95,100,105,110,400]'
  VAR_0JET_EM = 'pt_2,m_vis[15,25,35],[0,50,55,60,65,70,75,80,85,90,95,100,400]'
  VAR_0JET_TT = 'm_sv[0,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300]'

  VAR_BOOSTED = 'pt_tt,m_sv[0,100,150,200,250,300],[0,80,90,100,110,120,130,140,150,160,300]'
  VAR_BOOSTED_TT = 'pt_tt,m_sv[0,100,170,300],[0,40,60,70,80,90,100,110,120,130,150,200,250]'

  VAR_DIJET = 'sjdphi(20,-3.2,3.2)'
  VAR_DIJET_WIDEBINS = 'sjdphi(10,-3.2,3.2)'

  VAR_0JET_LT_WCR = 'mt_1[80,200]'
  VAR_BOOSTED_WCR = 'mt_1[80,200]'

  VAR_0JET_LT_QCDCR = 'm_vis(4,40,200)'
  VAR_BOOSTED_LT_QCDCR = 'm_sv(4,40,200)'

  VAR_0JET_TT_QCDCR = 'm_sv[0,300]'
  VAR_BOOSTED_TT_QCDCR = 'm_sv[0,300]'

  scheme_et = [
    ("21",   "0jet",    "0jet",  VAR_0JET_LT, '--set_alias="sel:mt_1<50" '),
    ("21",   "0jet",    "wjets_0jet_cr",  VAR_0JET_LT_WCR, '--set_alias="sel:mt_1>80" --set_alias="0jet:({0jet}&&n_bjets==0)" '),
    ("21",   "0jet",    "antiiso_0jet_cr",  VAR_0JET_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),
    ("21",   "boosted", "boosted",  VAR_BOOSTED, '--set_alias="sel:mt_1<50" '),
    ("21",   "boosted", "wjets_boosted_cr",  VAR_BOOSTED_WCR, '--set_alias="sel:mt_1>80" --set_alias="boosted:({boosted}&&n_bjets==0)" '),
    ("21",   "boosted",    "antiiso_boosted_cr",  VAR_BOOSTED_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" --set_alias="w_shape:({w_shape}&&iso_1>0.1)" '),
    ("21",   "dijet",     "dijet",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_lowM",     "dijet_lowM",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_highM",     "dijet_highM",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_lowboost",     "dijet_lowboost",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET_WIDEBINS, '--set_alias="sel:mt_1<50" ')


  ]
  scheme_mt = [
    ("21",   "0jet",    "0jet",  VAR_0JET_LT, '--set_alias="sel:mt_1<50" '),
    ("21",   "0jet",    "wjets_0jet_cr",  VAR_0JET_LT_WCR, '--set_alias="sel:(mt_1>80&&mt_1<200)" --set_alias="0jet:({0jet}&&n_bjets==0)" '),
    # ("21",   "0jet",    "antiiso_0jet_cr",  VAR_0JET_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),
    ("21",   "0jet",    "antiiso_0jet_cr",  VAR_0JET_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),
    ("21",   "boosted", "boosted",  VAR_BOOSTED, '--set_alias="sel:mt_1<50" '),
    ("21",   "boosted", "wjets_boosted_cr",  VAR_BOOSTED_WCR, '--set_alias="sel:mt_1>80" --set_alias="boosted:({boosted}&&n_bjets==0)" '),
    # ("21",   "boosted",    "antiiso_boosted_cr",  VAR_BOOSTED_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.15)" --set_alias="w_shape:({w_shape}&&iso_1>0.15)" '),
    ("21",   "boosted",    "antiiso_boosted_cr",  VAR_BOOSTED_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.15)" --set_alias="w_shape:({w_shape}&&iso_1>0.15)" '),
    ("21",   "dijet",     "dijet",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_lowM",     "dijet_lowM",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_highM",     "dijet_highM",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_lowboost",     "dijet_lowboost",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET_WIDEBINS, '--set_alias="sel:mt_1<50" ')

  ]
  scheme_tt = [
    ("8",   "0jet",    "0jet",  VAR_0JET_TT, ''),
    ("8",   "0jet",    "0jet_qcd_cr",  VAR_0JET_TT_QCDCR, ' --do_ss '),
    ("8",   "boosted", "boosted",  VAR_BOOSTED_TT, ''),
    ("8",   "boosted", "boosted_qcd_cr",  VAR_BOOSTED_TT_QCDCR, ' --do_ss '),
    ("8",   "dijet",     "dijet",  VAR_DIJET, ''),
    ("8",   "dijet_lowM",     "dijet_lowM",  VAR_DIJET, ''),
    ("8",   "dijet_highM",     "dijet_highM",  VAR_DIJET, ''),
    ("8",   "dijet_lowboost",     "dijet_lowboost",  VAR_DIJET, ''),
    ("8",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET_WIDEBINS, ''),
    ("8",   "dijet",      "dijet_qcd_cr",  VAR_DIJET, ' --do_ss '),
    ("8",   "dijet_lowM",      "dijet_lowM_qcd_cr",  VAR_DIJET, ' --do_ss '),
    ("8",   "dijet_highM",      "dijet_highM_qcd_cr",  VAR_DIJET, ' --do_ss '),
    ("8",   "dijet_lowboost",     "dijet_lowboost_qcd_cr",  VAR_DIJET, ' --do_ss '),
    ("8",   "dijet_boosted",     "dijet_boosted_qcd_cr",  VAR_DIJET_WIDEBINS, ' --do_ss ')
  ]
  scheme_em = [
    ("15",   "0jet",    "0jet",  VAR_0JET_EM, '--set_alias="sel:mt_1<50" '),
    ("15",   "boosted", "boosted",  VAR_BOOSTED, '--set_alias="sel:mt_1<50" '),
    ("15",   "dijet",     "dijet",  VAR_DIJET, '--set_alias="sel:mt_1<50" ')
  ]
  bkg_schemes = {
    'et' : 'et_default',
    'mt' : 'mt_with_zmm',
    'em' : 'em_default',
    'tt' : 'tt_default',
  }
  ANA = 'sm'

if SCHEME == 'cpsummer16_aachen':

  VAR_0JET_LT = 'tau_decay_mode_2,m_vis[0,1,10],[0,60,65,70,75,80,85,90,95,100,105,110,400]'
  VAR_0JET_EM = 'pt_2,m_vis[15,25,35],[0,50,55,60,65,70,75,80,85,90,95,100,400]'
  VAR_0JET_TT = 'm_sv[0,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300]'

  VAR_BOOSTED = 'pt_tt,m_sv[0,100,150,200,250,300],[0,80,90,100,110,120,130,140,150,160,300]'
  VAR_BOOSTED_TT = 'pt_tt,m_sv[0,100,170,300],[0,40,60,70,80,90,100,110,120,130,150,200,250]'

  VAR_DIJET = 'sjdphi(12,-3.2,3.2)'
  VAR_DIJET_THINBINS = 'sjdphi(20,-3.2,3.2)' # use this with ic cuts

  VAR_0JET_LT_WCR = 'mt_1[80,200]'
  VAR_BOOSTED_WCR = 'mt_1[80,200]'

  VAR_0JET_LT_QCDCR = 'm_vis(4,40,200)'
  VAR_BOOSTED_LT_QCDCR = 'm_sv(4,40,200)'

  VAR_0JET_TT_QCDCR = 'm_sv[0,300]'
  VAR_BOOSTED_TT_QCDCR = 'm_sv[0,300]'

  VAR_DIJET_TT_QCD = 'sjdphi(1,-3.2,3.2)'

  scheme_et = [
    ("21",   "0jet",    "0jet",  VAR_0JET_LT, '--set_alias="sel:mt_1<50" '),
    ("21",   "0jet",    "wjets_0jet_cr",  VAR_0JET_LT_WCR, '--set_alias="sel:mt_1>80" --set_alias="0jet:({0jet}&&n_bjets==0)" '),
    ("21",   "0jet",    "antiiso_0jet_cr",  VAR_0JET_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),
    ("21",   "boosted", "boosted",  VAR_BOOSTED, '--set_alias="sel:mt_1<50" '),
    ("21",   "boosted", "wjets_boosted_cr",  VAR_BOOSTED_WCR, '--set_alias="sel:mt_1>80" --set_alias="boosted:({boosted}&&n_bjets==0)" '),
    ("21",   "boosted",    "antiiso_boosted_cr",  VAR_BOOSTED_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" --set_alias="w_shape:({w_shape}&&iso_1>0.1)" '),
    ("21",   "dijet_lowM",     "dijet_lowM",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_highM",     "dijet_highM",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_lowMjj",     "dijet_lowMjj",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET, '--set_alias="sel:mt_1<50" ')


  ]
  scheme_mt = [
    ("21",   "0jet",    "0jet",  VAR_0JET_LT, '--set_alias="sel:mt_1<50" '),
    ("21",   "0jet",    "wjets_0jet_cr",  VAR_0JET_LT_WCR, '--set_alias="sel:(mt_1>80&&mt_1<200)" --set_alias="0jet:({0jet}&&n_bjets==0)" '),
    # ("21",   "0jet",    "antiiso_0jet_cr",  VAR_0JET_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),
    ("21",   "0jet",    "antiiso_0jet_cr",  VAR_0JET_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),
    ("21",   "boosted", "boosted",  VAR_BOOSTED, '--set_alias="sel:mt_1<50" '),
    ("21",   "boosted", "wjets_boosted_cr",  VAR_BOOSTED_WCR, '--set_alias="sel:mt_1>80" --set_alias="boosted:({boosted}&&n_bjets==0)" '),
    # ("21",   "boosted",    "antiiso_boosted_cr",  VAR_BOOSTED_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.15)" --set_alias="w_shape:({w_shape}&&iso_1>0.15)" '),
    ("21",   "boosted",    "antiiso_boosted_cr",  VAR_BOOSTED_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.15)" --set_alias="w_shape:({w_shape}&&iso_1>0.15)" '),
    ("21",   "dijet_lowM",     "dijet_lowM",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_highM",     "dijet_highM",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_lowMjj",     "dijet_lowMjj",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("21",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET, '--set_alias="sel:mt_1<50" ')

  ]
  scheme_tt = [
    ("8",   "0jet",    "0jet",  VAR_0JET_TT, ''),
    ("8",   "0jet",    "0jet_qcd_cr",  VAR_0JET_TT_QCDCR, ' --do_ss '),
    ("8",   "boosted", "boosted",  VAR_BOOSTED_TT, ''),
    ("8",   "boosted", "boosted_qcd_cr",  VAR_BOOSTED_TT_QCDCR, ' --do_ss '),
    ("8",   "dijet_lowM",     "dijet_lowM",  VAR_DIJET, ''),
    ("8",   "dijet_highM",     "dijet_highM",  VAR_DIJET, ''),
    ("8",   "dijet_lowMjj",     "dijet_lowMjj",  VAR_DIJET, ''),
    ("8",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET, ''),
    ("8",   "dijet_lowM",      "dijet_lowM_qcd_cr",  VAR_DIJET_TT_QCD, ' --do_ss '),
    ("8",   "dijet_highM",      "dijet_highM_qcd_cr",  VAR_DIJET_TT_QCD, ' --do_ss '),
    ("8",   "dijet_lowMjj",     "dijet_lowMjj_qcd_cr",  VAR_DIJET_TT_QCD, ' --do_ss '),
    ("8",   "dijet_boosted",     "dijet_boosted_qcd_cr",  VAR_DIJET_TT_QCD, ' --do_ss ')
  ]
  #scheme_em = [
  #  ("19",   "0jet",    "0jet",  VAR_0JET_EM, ' --set_alias="sel:pzeta>-35" '),
  #  ("19",   "boosted", "boosted",  VAR_BOOSTED, ' --set_alias="sel:pzeta>-35" '),
  #  ("19",   "dijet_lowM",     "dijet_lowM",  VAR_DIJET, ' --set_alias="sel:pzeta>-10" '),
  #  ("19",   "dijet_highM",     "dijet_highM",  VAR_DIJET, ' --set_alias="sel:pzeta>-10" '),
  #  ("19",   "dijet_lowMjj",     "dijet_lowMjj",  VAR_DIJET, ' --set_alias="sel:pzeta>-10" '),
  #  ("19",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET, ' --set_alias="sel:pzeta>-10" ')
  #]
  scheme_em = [
    ("19",   "0jet",    "0jet",  VAR_0JET_EM, ' --set_alias="sel:pzeta>-35" '),
    ("19",   "boosted", "boosted",  VAR_BOOSTED, ' --set_alias="sel:pzeta>-35" '),
    ("19",   "dijet_lowM",     "dijet_lowM",  VAR_DIJET, ' --set_alias="sel:pzeta>-35" '),
    ("19",   "dijet_highM",     "dijet_highM",  VAR_DIJET, ' --set_alias="sel:pzeta>-35" '),
    ("19",   "dijet_lowMjj",     "dijet_lowMjj",  VAR_DIJET, ' --set_alias="sel:pzeta>-35" '),
    ("19",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET, ' --set_alias="sel:pzeta>-35" ')
  ]

  bkg_schemes = {
    'et' : 'et_default',
    'mt' : 'mt_with_zmm',
    'em' : 'em_default',
    'tt' : 'tt_default'
  }
  ANA = 'sm'


if SCHEME == 'cpsummer16_2d':

  #VAR_0JET_LT = 'tau_decay_mode_2,m_vis[0,1,10],[0,60,65,70,75,80,85,90,95,100,105,110,400]'
  #VAR_0JET_EM = 'pt_2,m_vis[15,25,35],[0,50,55,60,65,70,75,80,85,90,95,100,400]'

  VAR_0JET_LT = 'm_sv[0,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,220,240,260,280,300]'
  VAR_0JET_EM = 'm_sv[0,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,220,240,260,280,300]'

  VAR_0JET_TT = 'm_sv[0,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300]'

  VAR_BOOSTED = 'pt_tt,m_sv[0,100,150,200,250,300],[0,80,90,100,110,120,130,140,150,160,300]'
  VAR_BOOSTED_TT = 'pt_tt,m_sv[0,100,170,300],[0,40,60,70,80,90,100,110,120,130,150,200,250]'

  VAR_DIJET = 'm_sv,sjdphi[0,80,100,115,130,150],(10,-3.2,3.2)'
  # VAR_DIJET = 'm_sv,DCP,D0[0,80,100,115,130,150],[-1,0,1],(6,0,1)'
  #VAR_DIJET = 'm_sv,DCP,D0[0,80,100,115,130,150],[-1,-0.4,0.4,1],[0,0.25,0.5,0.75,1]'


  VAR_DIJET_TT_QCD = 'sjdphi(1,-3.2,3.2)'

  VAR_WCR = 'mt_1[70,200]'

  VAR_0JET_LT_QCDCR = 'm_vis(4,40,200)'
  VAR_LT_QCDCR = 'm_sv(4,40,200)'

  VAR_TT_QCDCR = 'm_sv[0,300]'

  scheme_et = [
    ("21",   "0jet",    "0jet",  VAR_0JET_LT, ' --set_alias="sel:mt_1<50" '),
    ("21",   "0jet",    "wjets_0jet_cr",  VAR_WCR, ' --set_alias="sel:mt_1>70" '),
    ("21",   "0jet",    "antiiso_0jet_cr",  VAR_0JET_LT_QCDCR, ' --set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),
    ("21",   "boosted", "boosted",  VAR_BOOSTED, '--set_alias="sel:mt_1<50" '),
    ("21",   "boosted", "wjets_boosted_cr",  VAR_WCR, '--set_alias="sel:mt_1>70" '),
    ("21",   "boosted",    "antiiso_boosted_cr",  VAR_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" --set_alias="w_shape:({w_shape}&&iso_1>0.1)" '),
    ("24",   "dijet_lowboost",     "dijet_lowboost",  VAR_DIJET, ' --set_alias="sel:mt_1<50"  '),
    ("24",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("24",   "dijet",    "wjets_dijet_cr",  VAR_WCR, '--set_alias="sel:(mt_1>70)"  '),
    ("24",   "dijet",    "antiiso_dijet_cr",  VAR_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" ')

  ]
  scheme_mt = [
    ("21",   "inclusive",    "met_cr",  'met[0,10,20,30,40,50,60,70,80,90,100,120,140,160,180,200]', ' --set_alias="sel:mt_1<50" --set_alias="inclusive:(m_vis>50&&m_vis<80)" '),
    ("21",   "0jet",    "0jet",  VAR_0JET_LT, '--set_alias="sel:mt_1<50" '),
    ("21",   "0jet",    "wjets_0jet_cr",  VAR_WCR, '--set_alias="sel:(mt_1>70)" '),
    ("21",   "0jet",    "antiiso_0jet_cr",  VAR_0JET_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.15)" '),
    ("21",   "boosted", "boosted",  VAR_BOOSTED, '--set_alias="sel:mt_1<50" '),
    ("21",   "boosted", "wjets_boosted_cr",  VAR_WCR, '--set_alias="sel:mt_1>70" '),
    ("21",   "boosted",    "antiiso_boosted_cr",  VAR_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.15)" --set_alias="w_shape:({w_shape}&&iso_1>0.15)" '),
    ("24",   "dijet_lowboost",     "dijet_lowboost",  VAR_DIJET, ' --set_alias="sel:mt_1<50"  '),
    ("24",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET, '--set_alias="sel:mt_1<50" '),
    ("24",   "dijet",    "wjets_dijet_cr",  VAR_WCR, '--set_alias="sel:(mt_1>70)"  '),
    ("24",   "dijet",    "antiiso_dijet_cr",  VAR_LT_QCDCR, '--set_alias="sel:mt_1<50" --set_alias="baseline:(iso_1>0.15 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.15)" ')


  ]
  scheme_tt = [
    ("8",   "0jet",    "0jet",  VAR_0JET_TT, ''),
    ("8",   "0jet",    "0jet_qcd_cr",  VAR_TT_QCDCR, ' --do_ss '),
    ("8",   "boosted", "boosted",  VAR_BOOSTED_TT, ''),
    ("8",   "boosted", "boosted_qcd_cr",  VAR_TT_QCDCR, ' --do_ss '),
    ("8",   "dijet_lowboost",     "dijet_lowboost",  VAR_DIJET, ' '),
    ("8",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET, ' '),
    ("8",   "dijet_lowboost",      "dijet_lowboost_qcd_cr",  VAR_TT_QCDCR, ' --do_ss '),
    ("8",   "dijet_boosted",     "dijet_boosted_qcd_cr",  VAR_TT_QCDCR, ' --do_ss ')
  ]
  scheme_em = [
    ("19",   "0jet",    "0jet",  VAR_0JET_EM, ' --set_alias="sel:pzeta>-35" '),
    ("19",   "boosted", "boosted",  VAR_BOOSTED, ' --set_alias="sel:pzeta>-35" '),
    ("19",   "dijet_lowboost",     "dijet_lowboost",  VAR_DIJET, ' --set_alias="sel:pzeta>-10" '),
    ("19",   "dijet_boosted",     "dijet_boosted",  VAR_DIJET, ' --set_alias="sel:pzeta>-10" '),
    ("19",   "inclusive",    "ttbar",  'm_sv[0,300]', ' --set_alias="sel:pzeta<-50" --set_alias="inclusive:(n_jets>0)"'),
  ]
  scheme_zmm = [
    ("8",   "inclusive",    "met_cr",  'met[0,10,20,30,40,50,60,70,80,90,100,120,140,160,180,200]', '  --set_alias="inclusive:(m_vis>70&&m_vis<120)" ')
  ]
  bkg_schemes = {
    'et' : 'et_default',
    'mt' : 'mt_with_zmm',
    'em' : 'em_default',
    'tt' : 'tt_default',
    'zmm' : 'zmm_default'
  }
  ANA = 'sm'

if SCHEME == 'mlcpsummer16_2d':
    # define signal regions for each training

    VAR_MT_LOWMJJ_GGH =     'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'
    VAR_MT_LOWMJJ_QQH =     'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'
    VAR_MT_LOWMJJ_MISC =    'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,1.0]'
    VAR_MT_LOWMJJ_QCD =     'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'
    VAR_MT_LOWMJJ_TT =      'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'
    VAR_MT_LOWMJJ_W =       'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,1.0]'
    VAR_MT_LOWMJJ_ZLL =     'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'
    VAR_MT_LOWMJJ_ZTT =     'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'

    VAR_ET_LOWMJJ_GGH =     'IC_less2jets_max_score[0.0,0.4,0.5,0.6,0.7,1.0]'
    VAR_ET_LOWMJJ_QQH =     'IC_less2jets_max_score[0.0,0.2,0.3,0.4,0.5,0.6,0.7,1.0]'
    VAR_ET_LOWMJJ_MISC =    'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,1.0]'
    VAR_ET_LOWMJJ_QCD =     'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'
    VAR_ET_LOWMJJ_TT =      'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'
    VAR_ET_LOWMJJ_W =       'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,1.0]'
    VAR_ET_LOWMJJ_ZLL =     'IC_less2jets_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'
    VAR_ET_LOWMJJ_ZTT =     'IC_less2jets_max_score[0.0,0.2,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'

    VAR_TT_LOWMJJ_GGH =     'IC_less2jets_max_score[0.0,0.4,0.5,0.6,1.0]'
    VAR_TT_LOWMJJ_QQH =     'IC_less2jets_max_score[0.0,0.4,0.5,0.6,0.7,1.0]'
    VAR_TT_LOWMJJ_MISC =    'IC_less2jets_max_score[0.0,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'
    VAR_TT_LOWMJJ_QCD =     'IC_less2jets_max_score[0.0,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'
    VAR_TT_LOWMJJ_ZTT =     'IC_less2jets_max_score[0.0,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'


    # VAR_MT_HIGHMJJ_GGH =     'IC_max_score,sjdphi[0.0,0.4,0.5,0.6,0.7],(10,-3.2,3.2)'
    # VAR_MT_HIGHMJJ_QQH =     'IC_max_score,sjdphi[0.0,0.4,0.5,0.6,0.65],(10,-3.2,3.2)'
    # VAR_MT_HIGHMJJ_MISC =    'IC_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'
    # VAR_MT_HIGHMJJ_QCD =     'IC_max_score[0.0,0.3,0.5,0.7,1.0]'
    # VAR_MT_HIGHMJJ_TT =      'IC_max_score[0.0,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'
    # VAR_MT_HIGHMJJ_W =       'IC_max_score[0.0,0.3,0.4,0.5,1.0]'
    # VAR_MT_HIGHMJJ_ZLL =     'IC_max_score[0.0,1.0]'
    # VAR_MT_HIGHMJJ_ZTT =     'IC_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'

    # VAR_MT_HIGHMJJ_GGH =     'IC_highMjj_9May_jetvars_fullfakes_noscaling_fix_max_score,sjdphi[0.0,0.4,0.5,0.6,0.7],(12,-3.2,3.2)'
    # VAR_MT_HIGHMJJ_QQH =     'IC_highMjj_9May_jetvars_fullfakes_noscaling_fix_max_score,sjdphi[0.0,0.4,0.5,0.6,0.7],(10,-3.2,3.2)'
    # VAR_MT_HIGHMJJ_MISC =    'IC_highMjj_9May_jetvars_fullfakes_noscaling_fix_max_score[0.0,0.3,0.4,0.5,0.6,1.0]'
    # VAR_MT_HIGHMJJ_TT =      'IC_highMjj_9May_jetvars_fullfakes_noscaling_fix_max_score[0.0,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'
    # VAR_MT_HIGHMJJ_FAKE =    'IC_highMjj_9May_jetvars_fullfakes_noscaling_fix_max_score[0.0,0.3,0.4,0.5,0.6,1.0]'
    # VAR_MT_HIGHMJJ_ZTT =     'IC_highMjj_9May_jetvars_fullfakes_noscaling_fix_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'

    VAR_MT_HIGHMJJ_GGH =     'IC_highMjj_10May_mjj_jdeta_dijetpt_max_score,sjdphi[0.0,0.3,0.4,0.5,0.6,0.7,0.8],(10,-3.2,3.2)'
    VAR_MT_HIGHMJJ_QQH =     'IC_highMjj_10May_mjj_jdeta_dijetpt_max_score,sjdphi[0.0,0.3,0.4,0.5,0.6,0.7,0.8],(10,-3.2,3.2)'
    VAR_MT_HIGHMJJ_MISC =    'IC_highMjj_10May_mjj_jdeta_dijetpt_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'
    VAR_MT_HIGHMJJ_TT =      'IC_highMjj_10May_mjj_jdeta_dijetpt_max_score[0.0,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'
    VAR_MT_HIGHMJJ_FAKE =    'IC_highMjj_10May_mjj_jdeta_dijetpt_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'
    VAR_MT_HIGHMJJ_ZTT =     'IC_highMjj_10May_mjj_jdeta_dijetpt_max_score[0.0,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'

    # VAR_ET_HIGHMJJ_GGH =     'IC_max_score,sjdphi[0.0,0.4,0.5,0.6],(10,-3.2,3.2)'
    # VAR_ET_HIGHMJJ_QQH =     'IC_max_score,sjdphi[0.0,0.4,0.5,0.6],(10,-3.2,3.2)'
    # VAR_ET_HIGHMJJ_MISC =    'IC_max_score[0.0,0.3,0.5,0.7,1.0]'
    # VAR_ET_HIGHMJJ_QCD =     'IC_max_score[0.0,1.0]'
    # VAR_ET_HIGHMJJ_TT =      'IC_max_score[0.0,0.4,0.5,0.6,0.7,0.8,1.0]'
    # VAR_ET_HIGHMJJ_W =       'IC_max_score[0.0,0.5,1.0]'
    # VAR_ET_HIGHMJJ_ZLL =     'IC_max_score[0.0,1.0]'
    # VAR_ET_HIGHMJJ_ZTT =     'IC_max_score[0.0,0.4,0.5,0.6,0.7,0.8,1.0]'

    VAR_ET_HIGHMJJ_GGH =     'IC_highMjj_10May_fulljetvars_fullfakes_max_score,sjdphi[0.0,0.3,0.4,0.5,0.6],(10,-3.2,3.2)'
    VAR_ET_HIGHMJJ_QQH =     'IC_highMjj_10May_fulljetvars_fullfakes_max_score,sjdphi[0.0,0.3,0.4,0.5,0.6],(10,-3.2,3.2)'
    VAR_ET_HIGHMJJ_MISC =    'IC_highMjj_10May_fulljetvars_fullfakes_max_score[0.0,0.3,0.4,0.5,0.6,1.0]'
    VAR_ET_HIGHMJJ_TT =      'IC_highMjj_10May_fulljetvars_fullfakes_max_score[0.0,0.3,0.4,0.5,0.6,0.7,0.8,1.0]'
    VAR_ET_HIGHMJJ_FAKE =    'IC_highMjj_10May_fulljetvars_fullfakes_max_score[0.0,0.3,0.4,0.5,0.6,1.0]'
    VAR_ET_HIGHMJJ_ZTT =     'IC_highMjj_10May_fulljetvars_fullfakes_max_score[0.0,0.3,0.4,0.5,0.6,0.7,1.0]'

    VAR_TT_HIGHMJJ_GGH =     'IC_highMjj_9May_jetpts_max_score,sjdphi[0.0,0.4,0.5,0.6,0.7],(10,-3.2,3.2)'
    VAR_TT_HIGHMJJ_QQH =     'IC_highMjj_9May_jetpts_max_score,sjdphi[0.0,0.4,0.5,0.6,0.7],(10,-3.2,3.2)'
    VAR_TT_HIGHMJJ_MISC =    'IC_highMjj_9May_jetpts_max_score[0.0,0.5,0.6,0.7,0.8,0.9,1.0]'
    VAR_TT_HIGHMJJ_QCD =     'IC_highMjj_9May_jetpts_max_score[0.0,0.4,0.5,0.6,0.7,0.8,0.9,1.0]'
    VAR_TT_HIGHMJJ_ZTT =     'IC_highMjj_9May_jetpts_max_score[0.0,0.4,0.5,0.6,0.7,0.8,1.0]'

    # VAR_JHU_GGH =     'mva_score_Apr06_1_JHU,sjdphi[0.0,0.2,0.4,0.6,0.8],(12,-3.2,3.2)'
    # VAR_JHU_MISC =    'mva_score_Apr06_1_JHU,sjdphi[0.0,0.2,0.4,0.6,0.8],(12,-3.2,3.2)'
    # VAR_JHU_QCD =     'mva_score_Apr06_1_JHU,sjdphi[0.0,0.2,0.4,0.6,0.8],(12,-3.2,3.2)'
    # VAR_JHU_QQH =     'mva_score_Apr06_1_JHU,sjdphi[0.0,0.2,0.4,0.6,0.8],(12,-3.2,3.2)'
    # VAR_JHU_TT =      'mva_score_Apr06_1_JHU,sjdphi[0.0,0.2,0.4,0.6,0.8],(12,-3.2,3.2)'
    # VAR_JHU_W =       'mva_score_Apr06_1_JHU,sjdphi[0.0,0.2,0.4,0.6,0.8],(12,-3.2,3.2)'
    # VAR_JHU_ZLL =     'mva_score_Apr06_1_JHU,sjdphi[0.0,0.2,0.4,0.6,0.8],(12,-3.2,3.2)'
    # VAR_JHU_ZTT =     'mva_score_Apr06_1_JHU,sjdphi[0.0,0.2,0.4,0.6,0.8],(12,-3.2,3.2)'

    # VAR_POWHEG_GGH =  'mva_score_Apr06_1_powheg[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]'
    # VAR_POWHEG_MISC = 'mva_score_Apr06_1_powheg[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]'
    # VAR_POWHEG_QCD =  'mva_score_Apr06_1_powheg[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]'
    # VAR_POWHEG_QQH =  'mva_score_Apr06_1_powheg[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]'
    # VAR_POWHEG_TT =   'mva_score_Apr06_1_powheg[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]'
    # VAR_POWHEG_W =    'mva_score_Apr06_1_powheg[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]'
    # VAR_POWHEG_ZLL =  'mva_score_Apr06_1_powheg[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]'
    # VAR_POWHEG_ZTT =  'mva_score_Apr06_1_powheg[0.0, 0.2, 0.4, 0.6, 0.8, 1.0]'

    # define control regions
    # QCD CR for both trainings for et,mt,tt
    # W CR for both trainings for et,mt

    VAR_LT_QCDCR =     'm_vis(4,40,200)'
    VAR_LT_WCR =       'mt_1[80,200]'

    # VAR_JHU_TT_QCDCR =     'sjdphi(1,-3.2,3.2)'
    # VAR_JHU_LT_QCDCR =     'm_vis(4,40,200)'

    # VAR_POWHEG_TT_QCDCR =  'sjdphi(1,-3.2,3.2)'
    # VAR_POWHEG_LT_QCDCR =  'm_vis(4,40,200)'

    # VAR_JHU_LT_WCR =       'mt_1[80,200]'

    # VAR_POWHEG_LT_WCR =    'mt_1[80,200]'

    scheme_et = [
        ("21",   "fake_highMjj",   "fake_highMjj", VAR_ET_HIGHMJJ_FAKE, ' --set_alias="sel:mt_1<50" '),

        ("21",   "qqh_lowMjj",    "qqh_lowMjj",  VAR_ET_LOWMJJ_QQH,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "ggh_lowMjj",    "ggh_lowMjj",  VAR_ET_LOWMJJ_GGH,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "misc_lowMjj",   "misc_lowMjj", VAR_ET_LOWMJJ_MISC, ' --set_alias="sel:mt_1<50" '),
        ("21",   "qcd_lowMjj",    "qcd_lowMjj",  VAR_ET_LOWMJJ_QCD,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "tt_lowMjj",     "tt_lowMjj",   VAR_ET_LOWMJJ_TT,   ' --set_alias="sel:mt_1<50" '),
        ("21",   "w_lowMjj",      "w_lowMjj",    VAR_ET_LOWMJJ_W,    ' --set_alias="sel:mt_1<50" '),
        ("21",   "zll_lowMjj",    "zll_lowMjj",  VAR_ET_LOWMJJ_ZLL,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "ztt_lowMjj",    "ztt_lowMjj",  VAR_ET_LOWMJJ_ZTT,   ' --set_alias="sel:mt_1<50" '),

        ("21",   "qqh_highMjj",    "qqh_highMjj",  VAR_ET_HIGHMJJ_QQH,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "ggh_highMjj",    "ggh_highMjj",  VAR_ET_HIGHMJJ_GGH,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "misc_highMjj",   "misc_highMjj", VAR_ET_HIGHMJJ_MISC, ' --set_alias="sel:mt_1<50" '),
        # ("21",   "qcd_highMjj",    "qcd_highMjj",  VAR_ET_HIGHMJJ_QCD,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "tt_highMjj",     "tt_highMjj",   VAR_ET_HIGHMJJ_TT,   ' --set_alias="sel:mt_1<50" '),
        # ("21",   "w_highMjj",      "w_highMjj",    VAR_ET_HIGHMJJ_W,    ' --set_alias="sel:mt_1<50" '),
        # ("21",   "zll_highMjj",    "zll_highMjj",  VAR_ET_HIGHMJJ_ZLL,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "ztt_highMjj",    "ztt_highMjj",  VAR_ET_HIGHMJJ_ZTT,   ' --set_alias="sel:mt_1<50" '),

        # ("21",   "qqh",    "qqh",  VAR_QQH,  ' --set_alias="sel:mt_1<50" '),
        # ("21",   "ggh",    "ggh",  VAR_ET_GGH,  ' --set_alias="sel:mt_1<50" '),
        # ("21",   "misc",   "misc", VAR_MISC, ' --set_alias="sel:mt_1<50" '),
        # ("21",   "qcd",    "qcd",  VAR_ET_QCD,  ' --set_alias="sel:mt_1<50" '),
        # ("21",   "tt",     "tt",   VAR_ET_TT,   ' --set_alias="sel:mt_1<50" '),
        # ("21",   "w",      "w",    VAR_W,    ' --set_alias="sel:mt_1<50" '),
        # ("21",   "zll",    "zll",  VAR_ET_ZLL,  ' --set_alias="sel:mt_1<50" '),
        # ("21",   "ztt",    "ztt",  VAR_ET_ZTT,  ' --set_alias="sel:mt_1<50" '),



        # ("21",   "JHU_ggh",    "JHU_ggh",  VAR_JHU_GGH, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_misc",    "JHU_misc",  VAR_JHU_MISC, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_qcd",    "JHU_qcd",  VAR_JHU_QCD, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_qqh",    "JHU_qqh",  VAR_JHU_QQH, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_tt",    "JHU_tt",  VAR_JHU_TT, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_w",    "JHU_w",  VAR_JHU_W, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_zll",    "JHU_zll",  VAR_JHU_ZLL, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_ztt",    "JHU_ztt",  VAR_JHU_ZTT, ' --set_alias="sel:mt_1<80" '),

        # ("21",   "powheg_ggh",    "powheg_ggh",  VAR_POWHEG_GGH, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_misc",    "powheg_misc",  VAR_POWHEG_MISC, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_qcd",    "powheg_qcd",  VAR_POWHEG_QCD, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_qqh",    "powheg_qqh",  VAR_POWHEG_QQH, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_tt",    "powheg_tt",  VAR_POWHEG_TT, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_w",    "powheg_w",  VAR_POWHEG_W, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_zll",    "powheg_zll",  VAR_POWHEG_ZLL, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_ztt",    "powheg_ztt",  VAR_POWHEG_ZTT, ' --set_alias="sel:mt_1<80" '),

        # CRs - using the same cuts as in the other schemes

        # ("21",   "JHU_qcd",    "JHU_qcd_cr",  VAR_JHU_LT_QCDCR, ' --set_alias="sel:mt_1<80" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),
        # ("21",   "powheg_qcd",    "powheg_qcd_cr",  VAR_POWHEG_LT_QCDCR, ' --set_alias="sel:mt_1<80" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),

        # ("21",   "JHU_w",    "JHU_w_cr",  VAR_JHU_LT_WCR, ' --set_alias="sel:mt_1>80" --set_alias="0jet:({0jet}&&n_bjets==0)" '),
        # ("21",   "powheg_w",    "powheg_w_cr",  VAR_POWHEG_LT_WCR, ' --set_alias="sel:mt_1>80" --set_alias="0jet:({0jet}&&n_bjets==0)" '),

    ]

    scheme_mt = [
        ("21",   "fake_highMjj",   "fake_highMjj", VAR_MT_HIGHMJJ_FAKE, ' --set_alias="sel:mt_1<50" '),

        ("21",   "qqh_lowMjj",    "qqh_lowMjj",  VAR_MT_LOWMJJ_QQH,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "ggh_lowMjj",    "ggh_lowMjj",  VAR_MT_LOWMJJ_GGH,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "misc_lowMjj",   "misc_lowMjj", VAR_MT_LOWMJJ_MISC, ' --set_alias="sel:mt_1<50" '),
        ("21",   "qcd_lowMjj",    "qcd_lowMjj",  VAR_MT_LOWMJJ_QCD,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "tt_lowMjj",     "tt_lowMjj",   VAR_MT_LOWMJJ_TT,   ' --set_alias="sel:mt_1<50" '),
        ("21",   "w_lowMjj",      "w_lowMjj",    VAR_MT_LOWMJJ_W,    ' --set_alias="sel:mt_1<50" '),
        ("21",   "zll_lowMjj",    "zll_lowMjj",  VAR_MT_LOWMJJ_ZLL,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "ztt_lowMjj",    "ztt_lowMjj",  VAR_MT_LOWMJJ_ZTT,   ' --set_alias="sel:mt_1<50" '),

        ("21",   "qqh_highMjj",    "qqh_highMjj",  VAR_MT_HIGHMJJ_QQH,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "ggh_highMjj",    "ggh_highMjj",  VAR_MT_HIGHMJJ_GGH,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "misc_highMjj",   "misc_highMjj", VAR_MT_HIGHMJJ_MISC, ' --set_alias="sel:mt_1<50" '),
        # ("21",   "qcd_highMjj",    "qcd_highMjj",  VAR_MT_HIGHMJJ_QCD,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "tt_highMjj",     "tt_highMjj",   VAR_MT_HIGHMJJ_TT,   ' --set_alias="sel:mt_1<50" '),
        # ("21",   "w_highMjj",      "w_highMjj",    VAR_MT_HIGHMJJ_W,    ' --set_alias="sel:mt_1<50" '),
        # ("21",   "zll_highMjj",    "zll_highMjj",  VAR_MT_HIGHMJJ_ZLL,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "ztt_highMjj",    "ztt_highMjj",  VAR_MT_HIGHMJJ_ZTT,   ' --set_alias="sel:mt_1<50" '),

        # CRs - using the same cuts as in the other schemes

        # ("8",   "qcd",    "qcd_cr",  VAR_LT_QCDCR, ' --set_alias="sel:mt_1<80" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),

        # ("21",   "w",    "w_cr",  VAR_LT_WCR, ' --set_alias="sel:mt_1>80" --set_alias="0jet:({0jet}&&n_bjets==0)" '),

        # ("21",   "JHU_ggh",    "JHU_ggh",  VAR_JHU_GGH, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_misc",    "JHU_misc",  VAR_JHU_MISC, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_qcd",    "JHU_qcd",  VAR_JHU_QCD, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_qqh",    "JHU_qqh",  VAR_JHU_QQH, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_tt",    "JHU_tt",  VAR_JHU_TT, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_w",    "JHU_w",  VAR_JHU_W, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_zll",    "JHU_zll",  VAR_JHU_ZLL, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "JHU_ztt",    "JHU_ztt",  VAR_JHU_ZTT, ' --set_alias="sel:mt_1<80" '),

        # ("21",   "powheg_ggh",    "powheg_ggh",  VAR_POWHEG_GGH, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_misc",    "powheg_misc",  VAR_POWHEG_MISC, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_qcd",    "powheg_qcd",  VAR_POWHEG_QCD, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_qqh",    "powheg_qqh",  VAR_POWHEG_QQH, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_tt",    "powheg_tt",  VAR_POWHEG_TT, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_w",    "powheg_w",  VAR_POWHEG_W, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_zll",    "powheg_zll",  VAR_POWHEG_ZLL, ' --set_alias="sel:mt_1<80" '),
        # ("21",   "powheg_ztt",    "powheg_ztt",  VAR_POWHEG_ZTT, ' --set_alias="sel:mt_1<80" '),

        # # CRs - using the same cuts as in the other schemes

        # ("21",   "JHU_qcd",    "JHU_qcd_cr",  VAR_JHU_LT_QCDCR, ' --set_alias="sel:mt_1<80" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),
        # ("21",   "powheg_qcd",    "powheg_qcd_cr",  VAR_POWHEG_LT_QCDCR, ' --set_alias="sel:mt_1<80" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),

        # ("21",   "JHU_w",    "JHU_w_cr",  VAR_JHU_LT_WCR, ' --set_alias="sel:mt_1>80" --set_alias="0jet:({0jet}&&n_bjets==0)" '),
        # ("21",   "powheg_w",    "powheg_w_cr",  VAR_POWHEG_LT_WCR, ' --set_alias="sel:mt_1>80" --set_alias="0jet:({0jet}&&n_bjets==0)" '),
    ]

    scheme_tt = [
        ("8",   "ggh_lowMjj",    "ggh_lowMjj",  VAR_TT_LOWMJJ_GGH,  '  '),
        ("8",   "misc_lowMjj",   "misc_lowMjj", VAR_TT_LOWMJJ_MISC, '  '),
        ("8",   "qcd_lowMjj",    "qcd_lowMjj",  VAR_TT_LOWMJJ_QCD,  '  '),
        ("8",   "qqh_lowMjj",    "qqh_lowMjj",  VAR_TT_LOWMJJ_QQH,  '  '),
        ("8",   "ztt_lowMjj",    "ztt_lowMjj",  VAR_TT_LOWMJJ_ZTT,  '  '),

        ("8",   "ggh_highMjj",    "ggh_highMjj",  VAR_TT_HIGHMJJ_GGH,  '  '),
        ("8",   "misc_highMjj",   "misc_highMjj", VAR_TT_HIGHMJJ_MISC, '  '),
        ("8",   "qcd_highMjj",    "qcd_highMjj",  VAR_TT_HIGHMJJ_QCD,  '  '),
        ("8",   "qqh_highMjj",    "qqh_highMjj",  VAR_TT_HIGHMJJ_QQH,  '  '),
        ("8",   "ztt_highMjj",    "ztt_highMjj",  VAR_TT_HIGHMJJ_ZTT,  '  '),


        # ("8",   "JHU_ggh",    "JHU_ggh",  VAR_JHU_GGH, '  '),
        # ("8",   "JHU_misc",    "JHU_misc",  VAR_JHU_MISC, '  '),
        # ("8",   "JHU_qcd",    "JHU_qcd",  VAR_JHU_QCD, ' --do_ss '),
        # ("8",   "JHU_qqh",    "JHU_qqh",  VAR_JHU_QQH, '  '),
        # # ("8",   "JHU_tt",    "JHU_tt",  VAR_JHU_TT, '  '),
        # # ("8",   "JHU_w",    "JHU_w",  VAR_JHU_W, '  '),
        # # ("8",   "JHU_zll",    "JHU_zll",  VAR_JHU_ZLL, '  '),
        # ("8",   "JHU_ztt",    "JHU_ztt",  VAR_JHU_ZTT, '  '),

        # ("8",   "powheg_ggh",    "powheg_ggh",  VAR_POWHEG_GGH, '  '),
        # ("8",   "powheg_misc",    "powheg_misc",  VAR_POWHEG_MISC, '  '),
        # ("8",   "powheg_qcd",    "powheg_qcd",  VAR_POWHEG_QCD, ' --do_ss  '),
        # ("8",   "powheg_qqh",    "powheg_qqh",  VAR_POWHEG_QQH, '  '),
        # # ("8",   "powheg_tt",    "powheg_tt",  VAR_POWHEG_TT, '  '),
        # # ("8",   "powheg_w",    "powheg_w",  VAR_POWHEG_W, '  '),
        # # ("8",   "powheg_zll",    "powheg_zll",  VAR_POWHEG_ZLL, '  '),
        # ("8",   "powheg_ztt",    "powheg_ztt",  VAR_POWHEG_ZTT, '  '),

        # CRs - using the same cuts as in the other schemes

        # ("8",   "JHU_qcd",    "JHU_qcd_cr",  VAR_JHU_TT_QCDCR, ' --do_ss '),
        # ("8",   "powheg_qcd",    "powheg_qcd_cr",  VAR_POWHEG_TT_QCDCR, ' --do_ss '),
    ]
    scheme_em = [ #just named these to work for now
        # ("19",   "ggh",    "ggh",   VAR_ET_HIGHMJJ_GGH, '  '),
        # ("19",   "misc",    "misc", VAR_ET_HIGHMJJ_MISC, '  '),
        # ("19",   "qcd",    "qcd",   VAR_ET_HIGHMJJ_QCD, '  '),
        # ("19",   "qqh",    "qqh",   VAR_ET_HIGHMJJ_QQH, '  '),
        # ("19",   "tt",    "tt",     VAR_ET_HIGHMJJ_TT, '  '),
        # ("19",   "w",    "w",       VAR_ET_HIGHMJJ_W, '  '),
        # ("19",   "zll",    "zll",   VAR_ET_HIGHMJJ_ZLL, '  '),
        # ("19",   "ztt",    "ztt",   VAR_ET_HIGHMJJ_ZTT, '  '),

        # ("19",   "JHU_ggh",    "JHU_ggh",  VAR_JHU_GGH, '  '),
        # ("19",   "JHU_misc",    "JHU_misc",  VAR_JHU_MISC, '  '),
        # ("19",   "JHU_qcd",    "JHU_qcd",  VAR_JHU_QCD, '  '),
        # ("19",   "JHU_qqh",    "JHU_qqh",  VAR_JHU_QQH, '  '),
        # ("19",   "JHU_tt",    "JHU_tt",  VAR_JHU_TT, '  '),
        # ("19",   "JHU_w",    "JHU_w",  VAR_JHU_W, '  '),
        # ("19",   "JHU_zll",    "JHU_zll",  VAR_JHU_ZLL, '  '),
        # ("19",   "JHU_ztt",    "JHU_ztt",  VAR_JHU_ZTT, '  '),

        # ("19",   "powheg_ggh",    "powheg_ggh",  VAR_POWHEG_GGH, '  '),
        # ("19",   "powheg_misc",    "powheg_misc",  VAR_POWHEG_MISC, '  '),
        # ("19",   "powheg_qcd",    "powheg_qcd",  VAR_POWHEG_QCD, '  '),
        # ("19",   "powheg_qqh",    "powheg_qqh",  VAR_POWHEG_QQH, '  '),
        # ("19",   "powheg_tt",    "powheg_tt",  VAR_POWHEG_TT, '  '),
        # ("19",   "powheg_w",    "powheg_w",  VAR_POWHEG_W, '  '),
        # ("19",   "powheg_zll",    "powheg_zll",  VAR_POWHEG_ZLL, '  '),
        # ("19",   "powheg_ztt",    "powheg_ztt",  VAR_POWHEG_ZTT, '  '),
    ]
    bkg_schemes = {
      'et' : 'et_default',
      'mt' : 'mt_with_zmm',
      'em' : 'em_default',
      'tt' : 'tt_default'
    }
    ANA = 'sm'


# KIT scheme
if SCHEME == 'mlcpsummer16_2d_KIT':
    # define signal regions for each training
    # TT category not available

    VAR_GGH =     'KIT_0_max_score[0.0,0.2,0.4,0.6,0.8,1.0]'
    VAR_QQH =     'KIT_0_max_score[0.0,0.2,0.4,0.6,0.8,1.0]'
    VAR_ZTT =     'KIT_0_max_score[0.0,0.2,0.4,0.6,0.8,1.0]'
    VAR_ZLL =     'KIT_0_max_score[0.0,0.2,0.4,0.6,0.8,1.0]'
    VAR_QCD =     'KIT_0_max_score[0.0,0.2,0.4,0.6,0.8,1.0]'
    VAR_W =       'KIT_0_max_score[0.0,0.2,0.4,0.6,0.8,1.0]'
    VAR_MISC =    'KIT_0_max_score[0.0,0.2,0.4,0.6,0.8,1.0]'

    VAR_QQH_DIJET = 'KIT_0_max_score,sjdphi[0.0,0.25,0.5,0.75],(10,-3.2,3.2)'

    # define control regions
    # QCD CR for both trainings for et,mt,tt
    # W CR for both trainings for et,mt

    VAR_TT_QCDCR =     'sjdphi(1,-3.2,3.2)'
    VAR_LT_QCDCR =     'm_vis(4,40,200)'

    VAR_LT_WCR =       'mt_1[80,200]'

    scheme_et = [
        ("21",   "ggh",    "ggh",  VAR_GGH, ' --set_alias="sel:mt_1<80" '),
        ("21",   "misc",    "misc",  VAR_MISC, ' --set_alias="sel:mt_1<80" '),
        ("21",   "qcd",    "qcd",  VAR_QCD, ' --set_alias="sel:mt_1<80" '),
        ("21",   "qqh",    "qqh",  VAR_QQH, ' --set_alias="sel:mt_1<80" '),
        ("21",   "w",    "w",  VAR_W, ' --set_alias="sel:mt_1<80" '),
        ("21",   "zll",    "zll",  VAR_ZLL, ' --set_alias="sel:mt_1<80" '),
        ("21",   "ztt",    "ztt",  VAR_ZTT, ' --set_alias="sel:mt_1<80" '),
        # CRs - using the same cuts as in the other schemes

        ("21",   "qcd",    "qcd_cr",  VAR_LT_QCDCR, ' --set_alias="sel:mt_1<80" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),

        ("21",   "w",    "w_cr",  VAR_LT_WCR, ' --set_alias="sel:mt_1>80" --set_alias="0jet:({0jet}&&n_bjets==0)" '),

    ]

    scheme_mt = [
        ## only writing this for now since not using other channels
        ("21",   "qqh",       "qqh",       VAR_QQH,       ' --set_alias="sel:mt_1<50" '),
        ("21",   "qqh_dijet", "qqh_dijet", VAR_QQH_DIJET, ' --set_alias="sel:mt_1<50" '),

        ("8",   "ggh",    "ggh",   VAR_GGH,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "misc",   "misc",  VAR_MISC, ' --set_alias="sel:mt_1<50" '),
        ("21",   "qcd",    "qcd",   VAR_QCD,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "w",      "w",     VAR_W,    ' --set_alias="sel:mt_1<50" '),
        ("21",   "zll",    "zll",   VAR_ZLL,  ' --set_alias="sel:mt_1<50" '),
        ("21",   "ztt",    "ztt",   VAR_ZTT,  ' --set_alias="sel:mt_1<50" '),


        # CRs - using the same cuts as in the other schemes

        ("21",   "qcd",    "qcd_cr",  VAR_LT_QCDCR, ' --set_alias="sel:mt_1<80" --set_alias="baseline:(iso_1>0.1 && iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && leptonveto==0 && pt_2>30 && trg_singleelectron)" --set_alias="qcd_shape:({qcd_shape}&&iso_1>0.1)" '),

        ("21",   "w",    "w_cr",  VAR_LT_WCR, ' --set_alias="sel:mt_1>80" --set_alias="0jet:({0jet}&&n_bjets==0)" '),
    ]

    scheme_tt = [
        ("8",   "ggh",    "ggh",  VAR_GGH, '  '),
        ("8",   "misc",    "misc",  VAR_MISC, '  '),
        ("8",   "qcd",    "qcd",  VAR_QCD, ' --do_ss '),
        ("8",   "qqh",    "qqh",  VAR_QQH, '  '),
        ("8",   "ztt",    "ztt",  VAR_ZTT, '  '),


        # CRs - using the same cuts as in the other schemes

        ("8",   "qcd",    "qcd_cr",  VAR_TT_QCDCR, ' --do_ss '),
    ]
    scheme_em = [
        ("19",   "ggh",    "ggh",  VAR_GGH, '  '),
        ("19",   "misc",    "misc",  VAR_MISC, '  '),
        ("19",   "qcd",    "qcd",  VAR_QCD, '  '),
        ("19",   "qqh",    "qqh",  VAR_QQH, '  '),
        ("19",   "w",    "w",  VAR_W, '  '),
        ("19",   "zll",    "zll",  VAR_ZLL, '  '),
        ("19",   "ztt",    "ztt",  VAR_ZTT, '  '),
    ]
    bkg_schemes = {
      'et' : 'et_default',
      'mt' : 'mt_with_zmm',
      'em' : 'em_default',
      'tt' : 'tt_default'
    }
    ANA = 'sm'


cat_schemes = {
  'et' : scheme_et,
  'mt' : scheme_mt,
  'em' : scheme_em,
  'tt' : scheme_tt,
  # 'zmm': scheme_zmm
}

qsub_command = "qsub -e ./err -o /dev/null -cwd -V -q hep.q -v CFG='{}',ch='{}',cat_num='{}',cat_str='{}',YEAR='{}',output_folder='{}',dc='{}',PARAMS='{}',FOLDER='{}',BLIND='{}',var=\'{}\',extra=\'{}\'"

dc_app='-2D'
for ch in channels:
  scheme = cat_schemes[ch]
  bkg_scheme = bkg_schemes[ch]
  for x in scheme:
    cat_num = x[0]
    cat_str = x[1]
    dc      = x[2]
    var     = x[3]
    opts    = x[4]
    extra = options.extra + ' ' + extra_global + ' ' + extra_channel[ch] + ' ' + opts
    if options.embedding: extra+=' --embedding'
    extra_jes = options.extra + ' ' + extra_global + ' ' + jes_systematics + ' ' + opts + ' --no_default '

    if not options.batch:
        os.system('python $CMSSW_BASE/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/scripts/HiggsTauTauPlot.py --cfg=%(CFG)s --channel=%(ch)s'
            ' --method=%(cat_num)s --cat=%(cat_str)s --year=%(YEAR)s --outputfolder=%(output_folder)s/ --datacard=%(dc)s'
            ' --paramfile=%(PARAMS)s --folder=%(FOLDER)s %(BLIND)s'
            ' --var="%(var)s" %(extra)s --no_plot' % vars())

    else:
        print(qsub_command
                .format(CFG,ch,cat_num,cat_str,YEAR,output_folder,dc,PARAMS,FOLDER,BLIND,var,extra)
                + ' ./scripts/batch_datacards.sh'
                '\n')
        exit()

    if jes_systematics and not options.no_shape_systs and not options.batch:
      # have to do this to avoid using too much memory...
        os.system('python $CMSSW_BASE/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/scripts/HiggsTauTauPlot.py --cfg=%(CFG)s --channel=%(ch)s'
            ' --method=%(cat_num)s --cat=%(cat_str)s --year=%(YEAR)s --outputfolder=%(output_folder)s/ --datacard=%(dc)s --extra_name=jes1'
            ' --paramfile=%(PARAMS)s --folder=%(FOLDER)s %(BLIND)s'
            ' --var="%(var)s" %(extra_jes)s --no_plot --jes_sources=1:9' % vars())
        os.system('python $CMSSW_BASE/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/scripts/HiggsTauTauPlot.py --cfg=%(CFG)s --channel=%(ch)s'
            ' --method=%(cat_num)s --cat=%(cat_str)s --year=%(YEAR)s --outputfolder=%(output_folder)s/ --datacard=%(dc)s --extra_name=jes2'
            ' --paramfile=%(PARAMS)s --folder=%(FOLDER)s %(BLIND)s'
            ' --var="%(var)s" %(extra_jes)s --no_plot --jes_sources=10:18' % vars())
        os.system('python $CMSSW_BASE/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/scripts/HiggsTauTauPlot.py --cfg=%(CFG)s --channel=%(ch)s'
            ' --method=%(cat_num)s --cat=%(cat_str)s --year=%(YEAR)s --outputfolder=%(output_folder)s/ --datacard=%(dc)s --extra_name=jes3'
            ' --paramfile=%(PARAMS)s --folder=%(FOLDER)s %(BLIND)s'
            ' --var="%(var)s" %(extra_jes)s --no_plot --jes_sources=19:27' % vars())

    # elif jes_systematics and not options.no_shape_systs and options.batch:
    #     run_command(qsub_command
    #             .format(CFG,ch,cat_num,cat_str,YEAR,output_folder,dc,PARAMS,FOLDER,BLIND,var,extra_jes)
    #             + ',extra_name=jes1,jes_sources=1:9 ./scripts/batch_datacards_jes.sh'
    #             )
    #     exit()
    #     run_command(qsub_command
    #             .format(CFG,ch,cat_num,cat_str,YEAR,output_folder,dc,PARAMS,FOLDER,BLIND,var,extra_jes)
    #             + ',extra_name=jes2,jes_sources=10:18 ./scripts/batch_datacards_jes.sh'
    #             )
    #     run_command(qsub_command
    #             .format(CFG,ch,cat_num,cat_str,YEAR,output_folder,dc,PARAMS,FOLDER,BLIND,var,extra_jes)
    #             + ',extra_name=jes3,jes_sources=19:27 ./scripts/batch_datacards_jes.sh'
    #             )

    if not options.batch:
        os.system('hadd -f %(output_folder)s/htt_%(ch)s.inputs-%(ANA)s-%(COM)sTeV%(dc_app)s%(output)s.root %(output_folder)s/datacard_*_%(ch)s_%(YEAR)s.root' % vars())
        os.system('rm %(output_folder)s/datacard_*_%(ch)s_%(YEAR)s.root' % vars())

