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

CHANNELS= ['et', 'mt', 'em','tt','zmm','zee','mj']
ANALYSIS= ['sm','mssm','Hhh']
METHODS= [8 ,9, 10, 11, 12 , 13, 14, 15, 16, 17, 18, 19, 20]

conf_parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    add_help=False
    )
conf_parser.add_argument("--cfg",
                    help="Specify config file", metavar="FILE")
options, remaining_argv = conf_parser.parse_known_args()

defaults = { "channel":"mt" , "outputfolder":"output", "folder":"/vols/cms/dw515/Offline/output/MSSM/Jan11/" , "signal_folder":"", "embed_folder":"", "paramfile":"scripts/Params_2016_spring16.json", "cat":"inclusive", "year":"2016", "era":"mssmsummer16", "sel":"(1)", "set_alias":[], "analysis":"mssm", "var":"m_vis(7,0,140)", "method":8 , "do_ss":False, "sm_masses":"125", "ggh_masses":"", "bbh_masses":"", "bbh_nlo_masses":"", "nlo_qsh":False, "qcd_os_ss_ratio":-1, "add_sm_background":"", "syst_e_scale":"", "syst_mu_scale":"", "syst_tau_scale":"", "syst_tau_scale_0pi":"", "syst_tau_scale_1pi":"", "syst_tau_scale_3prong":"", "syst_eff_t":"", "syst_tquark":"", "syst_zwt":"", "syst_w_fake_rate":"", "syst_scale_j":"", "syst_scale_j_rbal":"", "syst_scale_j_full":"", "syst_scale_j_cent":"", "syst_scale_j_hf":"", "syst_scale_j_by_source":"","jes_sources":"1:27", "syst_eff_b":"", "syst_fake_b":"" ,"norm_bins":False, "blind":False, "x_blind_min":100, "x_blind_max":4000, "ratio":False, "y_title":"", "x_title":"", "custom_y_range":False, "y_axis_min":0.001, "y_axis_max":100,"custom_x_range":False, "x_axis_min":0.001, "x_axis_max":100, "log_x":False, "log_y":False, "extra_pad":0.0, "signal_scale":1, "draw_signal_mass":"", "draw_signal_tanb":10, "signal_scheme":"run2_mssm", "lumi":"12.9 fb^{-1} (13 TeV)", "no_plot":False, "ratio_range":"0.7,1.3", "datacard":"", "do_custom_uncerts":False, "uncert_title":"Systematic uncertainty", "custom_uncerts_wt_up":"","custom_uncerts_wt_down":"", "add_flat_uncert":0, "add_stat_to_syst":False, "add_wt":"", "custom_uncerts_up_name":"", "custom_uncerts_down_name":"", "do_ff_systs":False, "syst_efake_0pi_scale":"", "syst_efake_1pi_scale":"", "syst_mufake_0pi_scale":"", "syst_mufake_1pi_scale":"", "scheme":"","scheme":"", "syst_zpt_es":"", "syst_zpt_tt":"", "syst_zpt_statpt0":"", "syst_zpt_statpt40":"", "syst_zpt_statpt80":"", "syst_jfake_m":"", "syst_jfake_e":"", "syst_z_mjj":"", "syst_qcd_scale":"","doNLOScales":False, "gen_signal":False, "doPDF":False, "doMSSMReWeighting":False, "do_unrolling":1, "syst_tau_id_dm0":"", "syst_tau_id_dm1":"", "syst_tau_id_dm10":"", "syst_lfake_dm0":"", "syst_lfake_dm1":"","syst_qcd_shape_wsf":"","syst_scale_met_unclustered":"","syst_scale_met_clustered":"", "extra_name":"", "no_default":False, "embedding":False,"syst_embedding_tt":"" , "vbf_background":False, "split_sm_scheme": False, "ggh_scheme": "powheg"}

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
parser.add_argument("--signal_folder", dest="signal_folder", type=str,
    help="If specified will use as input folder for signal samples, else will use same directroy specified by \"folder\" option.")
parser.add_argument("--embed_folder", dest="embed_folder", type=str,
    help="If specified will use as input folder for embed samples, else will use same directroy specified by \"folder\" option.")
parser.add_argument("--paramfile", dest="paramfile", type=str,
    help="Name of parameter file")
parser.add_argument("--cat", dest="cat", type=str,
    help="Category")
parser.add_argument("--datacard", dest="datacard", type=str,
    help="Datacard name")
parser.add_argument("--year", dest="year", type=str,
    help="Year")
parser.add_argument("--era", dest="era", type=str,
    help="Era")
parser.add_argument("--sel", dest="sel", type=str,
    help="Selection")
parser.add_argument("--set_alias", action="append", dest="set_alias", type=str,
    help="Overwrite alias selection using this options. Specify with the form --set_alias=nameofaliastoreset:newselection")
parser.add_argument("--analysis", dest="analysis", type=str,
    help="Analysis.  Supported options: %(CHANNELS)s" % vars())
parser.add_argument("--var", dest="var", type=str,
    help="Variable to plot")
parser.add_argument("--method", dest="method", type=int,
    help="Method.  Supported options: %(METHODS)s" % vars())
parser.add_argument("--do_ss", dest="do_ss", action='store_true',
    help="Do same-sign.")
parser.add_argument("--sm_masses", dest="sm_masses", type=str,
    help="Comma seperated list of SM signal masses.")
parser.add_argument("--ggh_masses", dest="ggh_masses", type=str,
    help="Comma seperated list of SUSY ggH signal masses.")
parser.add_argument("--bbh_nlo_masses", dest="bbh_nlo_masses", type=str,
    help="Comma seperated list of SUSY NLO bbH signal masses.")
parser.add_argument("--nlo_qsh", dest="nlo_qsh", action='store_true',
    help="Do the Up/Down Qsh variations for NLO samples.")
parser.add_argument("--doNLOScales", dest="doNLOScales", action='store_true',
    help="Do the Up/Down QCD scale variations for NLO samples and compute uncertainties.")
parser.add_argument("--doPDF", dest="doPDF", action='store_true',
    help="Do PDF and alphaS variations for NLO samples and compute uncertainties.")
parser.add_argument("--doMSSMReWeighting", dest="doMSSMReWeighting", action='store_true',
    help="Do mA-tanb dependent reweighting of MSSM ggH signal.")
parser.add_argument("--bbh_masses", dest="bbh_masses", type=str,
    help="Comma seperated list of SUSY bbH signal masses.")
parser.add_argument("--qcd_os_ss_ratio", dest="qcd_os_ss_ratio", type=float,
    help="QCD OS/SS ratio")
parser.add_argument("--add_sm_background", dest="add_sm_background", type=str,
    help="Add SM Higgs background for MSSM")
parser.add_argument("--syst_tau_scale", dest="syst_tau_scale", type=str,
    help="If this string is set then the systematic shift due to tau energy scale is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_e_scale", dest="syst_e_scale", type=str,
    help="If this string is set then the systematic shift due to electron energy scale is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_mu_scale", dest="syst_mu_scale", type=str,
    help="If this string is set then the systematic shift due to muon energy scale is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_tau_scale_0pi", dest="syst_tau_scale_0pi", type=str,
    help="If this string is set then the systematic shift due to the 1 prong 0 pi tau energy scale is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_tau_scale_1pi", dest="syst_tau_scale_1pi", type=str,
    help="If this string is set then the systematic shift due to the 1 prong 1 pi tau energy scale is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_tau_scale_3prong", dest="syst_tau_scale_3prong", type=str,
    help="If this string is set then the systematic shift due to 3 prong tau energy scale is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_eff_t", dest="syst_eff_t", type=str, default='',
    help="If this string is set then the systematic shift due to tau ID is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_tquark", dest="syst_tquark", type=str,
    help="If this string is set then the top-quark weight systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_zwt", dest="syst_zwt", type=str,
    help="If this string is set then the z-reweighting systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_w_fake_rate", dest="syst_w_fake_rate", type=str, default='',
    help="If this string is set then the W+jets fake-rate systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_scale_j", dest="syst_scale_j", type=str,
    help="If this string is set then the jet scale systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_scale_j_rbal", dest="syst_scale_j_rbal", type=str,
    help="If this string is set then the RelativeBal jet scale systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_scale_j_full", dest="syst_scale_j_full", type=str,
    help="If this string is set then the regional jet scale systematic is performed with the set string appended to the resulting histogram name. Region = full region (eta<5)")
parser.add_argument("--syst_scale_j_cent", dest="syst_scale_j_cent", type=str,
    help="If this string is set then the regional jet scale systematic is performed with the set string appended to the resulting histogram name. Region = central region (eta<3)")
parser.add_argument("--syst_scale_j_hf", dest="syst_scale_j_hf", type=str,
    help="If this string is set then the regional jet scale systematic is performed with the set string appended to the resulting histogram name. Region = full region (eta>3)")
parser.add_argument("--syst_scale_j_by_source", dest="syst_scale_j_by_source", type=str,
    help="If this string is set then the jet scale systematic is performed split by source with the set string appended to the resulting histogram name. The string should contrain the substring  \'SOUCE\' which will be replaced by the JES source name")
parser.add_argument("--jes_sources", dest="jes_sources", type=str,
    help="JES sources to process specified by integers seperated by commas. Values seperated by x\':\'y will process all integers from x to y. e.g using --jes_sources=1:3,10 will process sources: 1,2,3,10")
parser.add_argument("--syst_eff_b", dest="syst_eff_b", type=str,
    help="If this string is set then the b-tag efficiency systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_fake_b", dest="syst_fake_b", type=str,
    help="If this string is set then the b-tag fake-rate systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--norm_bins", dest="norm_bins", action='store_true',
    help="Normalize bins by bin width.")
parser.add_argument("--blind", dest="blind", action='store_true',
    help="Blind histogram.")
parser.add_argument("--x_blind_min", dest="x_blind_min", type=float,
    help="Minimum x for blinding.")
parser.add_argument("--x_blind_max", dest="x_blind_max", type=float,
    help="Maximum x for blinding.")
parser.add_argument("--ratio", dest="ratio", action='store_true',
    help="Draw ratio.")
parser.add_argument("--y_title", dest="y_title", type=str,
    help="Y-axis title.")
parser.add_argument("--x_title", dest="x_title", type=str,
    help="X-axis title.")
parser.add_argument("--custom_y_range", dest="custom_y_range", action='store_true',
    help="Use custom y-axis range")
parser.add_argument("--y_axis_min", dest="y_axis_min", type=float,
    help="Minimum y-axis value.")
parser.add_argument("--y_axis_max", dest="y_axis_max", type=float,
    help="Maximum y-axis value.")
parser.add_argument("--custom_x_range", dest="custom_x_range", action='store_true',
    help="Use custom x-axis range")
parser.add_argument("--x_axis_min", dest="x_axis_min", type=float,
    help="Minimum x-axis value.")
parser.add_argument("--x_axis_max", dest="x_axis_max", type=float,
    help="Maximum x-axis value.")
parser.add_argument("--log_x", dest="log_x", action='store_true',
    help="Set log scale on x-axis.")
parser.add_argument("--log_y", dest="log_y", action='store_true',
    help="Set log scale on y-axis.")
parser.add_argument("--extra_pad", dest="extra_pad", type=float,
    help="Fraction of extra whitespace at top of plot.")
parser.add_argument("--signal_scale", dest="signal_scale", type=float,
    help="Signal scale.")
parser.add_argument("--draw_signal_mass", dest="draw_signal_mass", type=str,
    help="Signal mass.")
parser.add_argument("--draw_signal_tanb", dest="draw_signal_tanb", type=float,
    help="Signal tanb.")
parser.add_argument("--signal_scheme", dest="signal_scheme", type=str,
    help="Signal scale.")
parser.add_argument("--lumi", dest="lumi", type=str,
    help="Lumi.")
parser.add_argument("--no_plot", dest="no_plot", action='store_true',
    help="If option is set then no pdf or png plots will be created only the output root file will be produced.")
parser.add_argument("--ratio_range", dest="ratio_range", type=str,
    help="y-axis range for ratio plot in format MIN,MAX")
parser.add_argument("--do_custom_uncerts", dest="do_custom_uncerts", action='store_true',
    help="Do custom uncertainty band. Up and down weights for this uncertainty band should be set using \"custom_uncerts_wt_up\" and \"custom_uncerts_wt_down\" options")
parser.add_argument("--custom_uncerts_down_name", dest="custom_uncerts_down_name", type=str,
    help="Name of histogram to use for uncertainty down band")
parser.add_argument("--custom_uncerts_up_name", dest="custom_uncerts_up_name", type=str,
    help="Name of histogram to use for uncertainty up band")
parser.add_argument("--custom_uncerts_wt_up", dest="custom_uncerts_wt_up", type=str,
    help="Up weight for custom uncertainty band")
parser.add_argument("--custom_uncerts_wt_down", dest="custom_uncerts_wt_down", type=str,
    help="Down weight for custom uncertainty band")
parser.add_argument("--uncert_title", dest="uncert_title", type=str,
    help="Custom uncertainty band legend label")
parser.add_argument("--add_stat_to_syst", dest="add_stat_to_syst", action='store_true',
    help="Add custom uncertainty band to statistical uncertainty.")
parser.add_argument("--add_flat_uncert", dest="add_flat_uncert", type=float,
    help="If set to non-zero will add a flat uncertainty band in quadrature to the uncertainty.")
parser.add_argument("--add_wt", dest="add_wt", type=str,
    help="Name of additional weight to be applied to all templates.")
parser.add_argument("--do_ff_systs", dest="do_ff_systs", action='store_true',
    help="Do fake-factor systamatic shifts.")
parser.add_argument("--syst_efake_0pi_scale", dest="syst_efake_0pi_scale", type=str,
    help="If this string is set then the e->tau dm=0 fake-rate systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_efake_1pi_scale", dest="syst_efake_1pi_scale", type=str,
    help="If this string is set then the e->tau dm=1 fake-rate systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_mufake_0pi_scale", dest="syst_mufake_0pi_scale", type=str,
    help="If this string is set then the mu->tau dm=0 fake-rate systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_mufake_1pi_scale", dest="syst_mufake_1pi_scale", type=str,
    help="If this string is set then the mu->tau dm=1 fake-rate systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--scheme", dest="scheme", type=str,
    help="Set plotting scheme")
parser.add_argument("--syst_zpt_es", dest="syst_zpt_es", type=str,
    help="If this string is set then the zpT muon ES systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_zpt_tt", dest="syst_zpt_tt", type=str,
    help="If this string is set then the zpT tt X-section systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_zpt_statpt0", dest="syst_zpt_statpt0", type=str,
    help="If this string is set then the zpT statistical pt0 systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_zpt_statpt40", dest="syst_zpt_statpt40", type=str,
    help="If this string is set then the zpT statistical pt40 systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_zpt_statpt80", dest="syst_zpt_statpt80", type=str,
    help="If this string is set then the zpT statistical pt80 systematic is performed with the set string appended to the resulting histogram name")
parser.add_argument("--syst_jfake_e", dest="syst_jfake_e", type=str,
    help="If set, adds the e->jet fake rate uncertainty with the set string appended to the resulting histogram name")
parser.add_argument("--syst_jfake_m", dest="syst_jfake_m", type=str,
    help="If set, adds the e->jet fake rate uncertainty with the set string appended to the resulting histogram name")
parser.add_argument("--syst_z_mjj", dest="syst_z_mjj", type=str,
    help="If set then add the uncertainty on the Z mjj corrections")
parser.add_argument("--syst_qcd_scale", dest="syst_qcd_scale", type=str,
    help="If set then add the qcd scale uncertainty for ggH")
parser.add_argument("--syst_tau_id_dm0", dest="syst_tau_id_dm0", type=str,
    help="If set, adds the tau dm = 0 id uncertainty with the set string appended to the resulting histogram name")
parser.add_argument("--syst_tau_id_dm1", dest="syst_tau_id_dm1", type=str,
    help="If set, adds the tau dm = 1 id uncertainty with the set string appended to the resulting histogram name")
parser.add_argument("--syst_tau_id_dm10", dest="syst_tau_id_dm10", type=str,
    help="If set, adds the tau dm = 10 id uncertainty with the set string appended to the resulting histogram name")
parser.add_argument("--syst_lfake_dm0", dest="syst_lfake_dm0", type=str,
    help="If set, adds the e/mu->tau dm = 0 fake-rate uncertainty with the set string appended to the resulting histogram name")
parser.add_argument("--syst_lfake_dm1", dest="syst_lfake_dm1", type=str,
    help="If set, adds the e/mu->tau dm = 1 fake-rate uncertainty with the set string appended to the resulting histogram name")
parser.add_argument("--syst_qcd_shape_wsf", dest="syst_qcd_shape_wsf", type=str,
    help="If set, adds QCD shape uncertainty relating to W subtraction from SS data with the set string appended to the resulting histogram name")
parser.add_argument("--syst_scale_met_unclustered", dest="syst_scale_met_unclustered", type=str,
    help="If set, adds the unclustered energy MET uncertainty with the set string appended to the resulting histogram name")
parser.add_argument("--syst_scale_met_clustered", dest="syst_scale_met_clustered", type=str,
    help="If set, adds the clustered energy MET uncertainty with the set string appended to the resulting histogram name")
parser.add_argument("--gen_signal", dest="gen_signal", action='store_true',
    help="If set then use generator-level tree for signal")
parser.add_argument("--do_unrolling", dest="do_unrolling", type=int,
    help="If argument is set to true will unroll 2D histograms into 1D histogram.")
parser.add_argument("--no_default", dest="no_default", action='store_true',
    help="If option is speficied then don't do nominal histograms.")
parser.add_argument("--extra_name", dest="extra_name", type=str,
    help="If set, adds an additional string to the output datacard name")
parser.add_argument("--embedding", dest="embedding", action='store_true',
    help="If option is speficied then use embedded samples for ZTT templates.")
parser.add_argument("--syst_embedding_tt", dest="syst_embedding_tt", type=str,
    help="If set, adds systematic templates for embedding corresponding to TTbar shift of +/-10\% ")
parser.add_argument("--split_sm_scheme", dest="split_sm_scheme", action='store_true',
    help="If set, splits the SM signal scheme into ggH, qqH and VH")
parser.add_argument("--ggh_scheme", dest="ggh_scheme", type=str,
    help="Decide which ggH scheme to plot with in split SM scheme mode (powheg or JHU)")
options = parser.parse_args(remaining_argv)

print ''
print '################### Options ###################'
print 'channel           = ' + options.channel
print 'outputfolder      = ' + options.outputfolder
print 'folder            = ' + options.folder
print 'paramfile         = ' + options.paramfile
print 'cat               = ' + options.cat
print 'datacard          = ' + options.datacard
print 'year              = ' + options.year
print 'era               = ' + options.era
print 'sel               = ' + options.sel
print 'analysis          = ' + options.analysis
print 'var               = ' + options.var
print 'method            ='  ,  options.method
print 'do_ss             ='  ,  options.do_ss
print 'sm_masses         = ' +  options.sm_masses
print 'ggh_masses        = ' +  options.ggh_masses
print 'bbh_masses        = ' +  options.bbh_masses
print 'qcd_os_ss_ratio   ='  ,  options.qcd_os_ss_ratio
print 'add_sm_background ='  ,  options.add_sm_background
print 'syst_tau_scale    ='  ,  options.syst_tau_scale
print 'syst_eff_t        ='  ,  options.syst_eff_t
print 'syst_tquark       ='  ,  options.syst_tquark
print 'syst_zwt          ='  ,  options.syst_zwt
print 'syst_w_fake_rate  ='  ,  options.syst_w_fake_rate
print 'syst_scale_j      ='  ,  options.syst_scale_j
print 'syst_eff_b        ='  ,  options.syst_eff_b
print 'syst_fake_b       ='  ,  options.syst_fake_b
print 'do_ff_systs       ='  ,  options.do_ff_systs
print '###############################################'
print ''

vbf_background = False
#if options.era == 'cpsummer16': vbf_background = True

compare_w_shapes = False
compare_qcd_shapes = False
if options.scheme == "qcd_shape": compare_qcd_shapes = True
if options.scheme == "w_shape": compare_w_shapes = True
w_abs_shift=None # if not None then the QCD shape will be adjusted by shifting the W yield up and down by +/- w_abs_shift
if options.era == "mssmsummer16" or options.era == "smsummer16" or options.era == "cpsummer16" or options.era == 'tauid2016': options.lumi = "35.9 fb^{-1} (13 TeV)"


cats = {}
if options.analysis == 'sm':
    if options.channel == 'mt':
        cats['baseline'] = '(iso_1<0.15 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && !leptonveto)'
        if options.era in ['smsummer16','cpsummer16']: cats['baseline'] = '(iso_1<0.15 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && !leptonveto && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))'
        #if options.era in ['cpsummer16']: cats['baseline'] = '(iso_1<0.15 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))'
        if options.era in ['tauid2016']:
          cats['baseline'] = '(iso_1<0.15 && antiele_2 && antimu_2 && !leptonveto && trg_singlemuon && pt_1>23)'
          cats['baseline_loosemu'] = '(iso_1<0.15 && antiele_2 && antimu_loose_2 && !leptonveto && trg_singlemuon && pt_1>23)'
          cats['pass'] = 'mva_olddm_tight_2>0.5 && pzeta>-25'
          cats['fail'] = 'mva_olddm_tight_2<0.5 && pzeta>-25'
    elif options.channel == 'et':
        cats['baseline'] = '(iso_1<0.1  && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && !leptonveto)'
        if options.era in ['smsummer16','cpsummer16']: cats['baseline'] = '(iso_1<0.1  && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && !leptonveto && pt_2>30 && trg_singleelectron)'
        #if options.era in ['cpsummer16']: cats['baseline'] = '(iso_1<0.1  && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto && pt_2>30 && trg_singleelectron)'
        if options.era in ['tauid2016']:
          cats['baseline'] = '(iso_1<0.1 && antiele_2 && antimu_2 && !leptonveto && trg_singleelectron)'
          cats['baseline_loosemu'] = '(iso_1<0.1 && antiele_2 && antimu_loose_2 && !leptonveto && trg_singleelectron)'
          cats['pass'] = 'mva_olddm_tight_2>0.5 && pzeta>-25'
          cats['fail'] = 'mva_olddm_tight_2<0.5 && pzeta>-25'

elif options.analysis == 'mssm':
    if options.channel == 'mt':
        cats['baseline'] = '(iso_1<0.15 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto)'
    elif options.channel == 'et':
        cats['baseline'] = '(iso_1<0.1  && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto)'
    if options.era == 'mssmsummer16':
        if options.channel == 'mt':
            cats['baseline'] = '(iso_1<0.15 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && !leptonveto)'
            cats['baseline_antiisotau'] = '(iso_1<0.15 && 1 && mva_olddm_tight_2<0.5 && antiele_2 && antimu_2 && !leptonveto && trg_singlemuon)'
            cats['ichep_baseline'] = '(iso_1<0.15 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto && trg_singlemuon)'
        elif options.channel == 'et':
            cats['baseline'] = '(iso_1<0.1  && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && !leptonveto)'
            cats['baseline_antiisotau'] = '(iso_1<0.1 && mva_olddm_tight_2<0.5 && antiele_2 && antimu_2 && !leptonveto && trg_singleelectron)'
            cats['ichep_baseline'] = '(iso_1<0.1 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto && trg_singleelectron)'
        elif options.channel == 'mj':
            cats['baseline'] = '(iso_1<0.15 && !leptonveto)'
if options.channel == 'tt':
    cats['baseline'] = '(mva_olddm_tight_1>0.5 && mva_olddm_tight_2>0.5 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto)'
    if options.era == 'mssmsummer16': cats['baseline'] = '(mva_olddm_medium_1>0.5 && mva_olddm_medium_2>0.5 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto)'
    if options.era in ['smsummer16','cpsummer16','tauid2016']: cats['baseline'] = '(pt_1>50 && mva_olddm_tight_1>0.5 && mva_olddm_tight_2>0.5 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto && trg_doubletau)'
    #if options.era in ['cpsummer16']: cats['baseline'] = '(pt_1>50 && mva_olddm_medium_1>0.5 && mva_olddm_medium_2>0.5 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto && trg_doubletau)'
elif options.channel == 'em':
    cats['baseline'] = '(iso_1<0.15 && iso_2<0.2 && !leptonveto)'
    cats['loose_baseline'] = '(iso_1<0.5 && iso_2>0.2 && iso_2<0.5 && !leptonveto &&trg_muonelectron)'
    if options.era in ['smsummer16','cpsummer16']: cats['baseline'] = '(iso_1<0.15 && iso_2<0.2 && !leptonveto && trg_muonelectron)'
elif options.channel == 'zmm':
    cats['baseline'] = '(iso_1<0.15 && iso_2<0.15)'
    if options.era in ['smsummer16','cpsummer16']: cats['baseline'] = '(iso_1<0.15 && iso_2<0.15 && trg_singlemuon)'
elif options.channel == 'zee':
    cats['baseline'] = '(iso_1<0.1 && iso_2<0.1)'
    if options.era in ['smsummer16','cpsummer16']: cats['baseline'] = '(iso_1<0.1 && iso_2<0.1 && trg_singleelectron)'

cats['inclusive'] = '(1)'
cats['w_os'] = 'os'
cats['w_sdb'] = 'mt_1>70.'
if options.era in ['smsummer16']: cats['w_sdb'] = 'mt_1>80.'
cats['w_sdb_os'] = 'os'
cats['tt_qcd_norm'] = '(mva_olddm_tight_1>0.5 && mva_olddm_medium_2>0.5 &&mva_olddm_tight_2<0.5 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto)&&trg_doubletau'
if options.era == 'mssmsummer16': cats['tt_qcd_norm'] = '(mva_olddm_medium_1>0.5 && mva_olddm_loose_2>0.5 &&mva_olddm_medium_2<0.5 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto)&&trg_doubletau'
if options.era in ['smsummer16','cpsummer16']: cats['tt_qcd_norm'] = '(((mva_olddm_loose_1>0.5 && mva_olddm_tight_1<0.5 && mva_olddm_medium_2>0.5) || (mva_olddm_loose_2>0.5 && mva_olddm_tight_2<0.5 && mva_olddm_medium_1>0.5)) && pt_1>50 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto)&&trg_doubletau'

## CUTS LOOSENED FOR MVA STUDY
# if options.era in ['cpsummer16']: cats['tt_qcd_norm'] = '(((mva_olddm_loose_1>0.5 && mva_olddm_medium_1<0.5 && mva_olddm_loose_2>0.5) || (mva_olddm_loose_2>0.5 && mva_olddm_medium_2<0.5 && mva_olddm_loose_1>0.5)) && pt_1>50 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto)&&trg_doubletau'
cats['qcd_loose_shape'] = '(iso_1>0.2 && iso_1<0.5 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && !leptonveto)'

# CR categories
cats['ztt_control'] = '(m_sv>60&&m_sv<100)'
cats['ztt_control_dijet'] = '(m_sv>60&&m_sv<100 && n_jets>1)'
if options.channel == 'em':
  cats['ztt_control'] = '(m_sv>60&&m_sv<100 && n_bjets==0)'
  cats['ztt_control_dijet'] = '(m_sv>60&&m_sv<100 && n_jets>1 && n_bjets==0)'

# MSSM categories
cats['btag'] = '(n_bjets>=1)'
cats['nobtag'] = '(n_bjets==0)'
# loose/tight iso-MT categories
cats['nobtag_tight'] = cats['nobtag']
cats['nobtag_loosemt'] = cats['nobtag']
cats['btag_tight'] = cats['btag']
cats['btag_loosemt'] = cats['btag']
cats['atleast1bjet'] = '(n_bjets>0)'
cats['btag_wnobtag']='(n_lowpt_jets>=1)' # this is the one that is used for the b-tag method 16!
cats['0jet'] = '(n_jets==0)'
cats['1jet'] = '(n_jets==1)'
cats['ge2jet'] = '(n_jets>=2)'
cats['btag_tight_wnobtag']='(n_lowpt_jets>=1)'
cats['w_shape']=''
cats['qcd_shape']=''
cats['w_shape_comp']=''
cats['qcd_shape_comp']=''

if options.channel == 'et': cats['baseline_loose'] = '(iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto && pt_2>30 && trg_singleelectron)'
if options.channel == 'mt': cats['baseline_loose'] = '(iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto && pt_2>30 && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))'

## MVA categories for SM MVA
if options.channel in ['em','et','mt']:
    ## for KIT cats
    mva_ggh =     '(KIT_0_max_index==0)'
    mva_qqh =     '(KIT_0_max_index==1)'
    mva_ztt =     '(KIT_0_max_index==2)'
    mva_zll =     '(KIT_0_max_index==3)'
    mva_w =       '(KIT_0_max_index==4)'
    mva_qcd =     '(KIT_0_max_index==5)'
    mva_misc =    '(KIT_0_max_index==6)'


    # IC categories

    # mva_JHU_ggh =     '(mva_cat_sm_Apr11_sm_0_JHU==0)'
    # mva_JHU_misc =    '(mva_cat_sm_Apr11_sm_0_JHU==1)'
    # mva_JHU_qcd =     '(mva_cat_sm_Apr11_sm_0_JHU==2)'
    # mva_JHU_qqh =     '(mva_cat_sm_Apr11_sm_0_JHU==3)'
    # mva_JHU_tt =      '(mva_cat_sm_Apr11_sm_0_JHU==4)'
    # mva_JHU_w =       '(mva_cat_sm_Apr11_sm_0_JHU==5)'
    # mva_JHU_zll =     '(mva_cat_sm_Apr11_sm_0_JHU==6)'
    # mva_JHU_ztt =     '(mva_cat_sm_Apr11_sm_0_JHU==7)'

    # mva_powheg_ggh =  '(mva_cat_sm_Apr11_sm_0_powheg==0)'
    # mva_powheg_misc = '(mva_cat_sm_Apr11_sm_0_powheg==1)'
    # mva_powheg_qcd =  '(mva_cat_sm_Apr11_sm_0_powheg==2)'
    # mva_powheg_qqh =  '(mva_cat_sm_Apr11_sm_0_powheg==3)'
    # mva_powheg_tt =   '(mva_cat_sm_Apr11_sm_0_powheg==4)'
    # mva_powheg_w =    '(mva_cat_sm_Apr11_sm_0_powheg==5)'
    # mva_powheg_zll =  '(mva_cat_sm_Apr11_sm_0_powheg==6)'
    # mva_powheg_ztt =  '(mva_cat_sm_Apr11_sm_0_powheg==7)'

#     mva_JHU_ggh =     '(mva_cat_cpsm_Apr06_1_JHU==0)'
#     mva_JHU_misc =    '(mva_cat_cpsm_Apr06_1_JHU==1)'
#     mva_JHU_qcd =     '(mva_cat_cpsm_Apr06_1_JHU==2)'
#     mva_JHU_qqh =     '(mva_cat_cpsm_Apr06_1_JHU==3)'
#     mva_JHU_tt =      '(mva_cat_cpsm_Apr06_1_JHU==4)'
#     mva_JHU_w =       '(mva_cat_cpsm_Apr06_1_JHU==5)'
#     mva_JHU_zll =     '(mva_cat_cpsm_Apr06_1_JHU==6)'
#     mva_JHU_ztt =     '(mva_cat_cpsm_Apr06_1_JHU==7)'

#     mva_powheg_ggh =  '(mva_cat_cpsm_Apr06_1_powheg==0)'
#     mva_powheg_misc = '(mva_cat_cpsm_Apr06_1_powheg==1)'
#     mva_powheg_qcd =  '(mva_cat_cpsm_Apr06_1_powheg==2)'
#     mva_powheg_qqh =  '(mva_cat_cpsm_Apr06_1_powheg==3)'
#     mva_powheg_tt =   '(mva_cat_cpsm_Apr06_1_powheg==4)'
#     mva_powheg_w =    '(mva_cat_cpsm_Apr06_1_powheg==5)'
#     mva_powheg_zll =  '(mva_cat_cpsm_Apr06_1_powheg==6)'
#     mva_powheg_ztt =  '(mva_cat_cpsm_Apr06_1_powheg==7)'

if options.channel == 'tt':
    mva_JHU_ggh =     '(mva_cat_sm_Apr11_sm_0_JHU==0)'
    mva_JHU_misc =    '(mva_cat_sm_Apr11_sm_0_JHU==1)'
    mva_JHU_qcd =     '(mva_cat_sm_Apr11_sm_0_JHU==2)'
    mva_JHU_qqh =     '(mva_cat_sm_Apr11_sm_0_JHU==3)'
    mva_JHU_ztt =     '(mva_cat_sm_Apr11_sm_0_JHU==4)'

    mva_powheg_ggh =  '(mva_cat_sm_Apr11_sm_0_powheg==0)'
    mva_powheg_misc = '(mva_cat_sm_Apr11_sm_0_powheg==1)'
    mva_powheg_qcd =  '(mva_cat_sm_Apr11_sm_0_powheg==2)'
    mva_powheg_qqh =  '(mva_cat_sm_Apr11_sm_0_powheg==3)'
    mva_powheg_ztt =  '(mva_cat_sm_Apr11_sm_0_powheg==4)'

    # mva_JHU_ggh =     '(mva_cat_cpsm_Apr06_1_JHU==0)'
    # mva_JHU_misc =    '(mva_cat_cpsm_Apr06_1_JHU==1)'
    # mva_JHU_qcd =     '(mva_cat_cpsm_Apr06_1_JHU==2)'
    # mva_JHU_qqh =     '(mva_cat_cpsm_Apr06_1_JHU==3)'
    # mva_JHU_ztt =     '(mva_cat_cpsm_Apr06_1_JHU==4)'

    # mva_powheg_ggh =  '(mva_cat_cpsm_Apr06_1_powheg==0)'
    # mva_powheg_misc = '(mva_cat_cpsm_Apr06_1_powheg==1)'
    # mva_powheg_qcd =  '(mva_cat_cpsm_Apr06_1_powheg==2)'
    # mva_powheg_qqh =  '(mva_cat_cpsm_Apr06_1_powheg==3)'
    # mva_powheg_ztt =  '(mva_cat_cpsm_Apr06_1_powheg==4)'

# SM categories
## add the cuts here for the SM ML multiclass
## depending on what class it belongs to add it to the category
cats['0jet'] = '(n_jets==0)'
if options.channel == 'em': cats['0jet'] = '(n_jets==0 && n_bjets==0)'
cats['vbf'] = '(0)'
cats['twojets'] = '(n_jets>=2)'
if options.channel == 'em': cats['vbf'] = '(n_jets==2 && mjj>300 && n_bjets==0)'
if options.channel == 'et': cats['vbf'] = '(n_jets>=2 && mjj>300 && pt_tt>50)'
if options.channel == 'mt': cats['vbf'] = '(n_jets>=2 && mjj>300 && pt_tt>50 && pt_2>40)'
if options.channel == 'tt': cats['vbf'] = '(n_jets>=2 && pt_tt>100 && jdeta>2.5)'
cats['boosted'] = '(!(%s) && !(%s))' % (cats['0jet'], cats['vbf'])
if options.channel == 'em': cats['boosted'] = '(!(%s) && !(%s) && n_bjets==0)' % (cats['0jet'], cats['vbf'])

if options.era in ['smsummer16','cpsummer16']: # change here for mlcpsummer16
  if options.channel in ['em','mt','et']:
      # KIT categories (with qqh modification)
      cats['ggh'] =  mva_ggh
      cats['misc'] = mva_misc
      cats['qcd'] =  mva_qcd
      cats['w'] =    mva_w
      cats['zll'] =  mva_zll
      cats['ztt'] =  mva_ztt

      cats['qqh'] =  '({}) && !(n_jets>=2 && mjj>300)'.format(mva_qqh)
      cats['qqh_dijet'] =  '({}) && (n_jets>=2 && mjj>300)'.format(mva_qqh)

      # IC categories

      # cats['JHU_ggh'] =  mva_JHU_ggh
      # cats['JHU_misc'] = mva_JHU_misc
      # cats['JHU_qcd'] =  mva_JHU_qcd
      # cats['JHU_qqh'] =  mva_JHU_qqh
      # cats['JHU_tt'] =   mva_JHU_tt
      # cats['JHU_w'] =    mva_JHU_w
      # cats['JHU_zll'] =  mva_JHU_zll
      # cats['JHU_ztt'] =  mva_JHU_ztt

      # cats['powheg_ggh'] =  mva_powheg_ggh
      # cats['powheg_misc'] = mva_powheg_misc
      # cats['powheg_qcd'] =  mva_powheg_qcd
      # cats['powheg_qqh'] =  mva_powheg_qqh
      # cats['powheg_tt'] =   mva_powheg_tt
      # cats['powheg_w'] =    mva_powheg_w
      # cats['powheg_zll'] =  mva_powheg_zll
      # cats['powheg_ztt'] =  mva_powheg_ztt
  if options.channel == 'tt':
      cats['JHU_ggh'] =  mva_JHU_ggh
      cats['JHU_misc'] = mva_JHU_misc
      cats['JHU_qcd'] =  mva_JHU_qcd
      cats['JHU_qqh'] =  mva_JHU_qqh
      cats['JHU_ztt'] =  mva_JHU_ztt

      cats['powheg_ggh'] =  mva_powheg_ggh
      cats['powheg_misc'] = mva_powheg_misc
      cats['powheg_qcd'] =  mva_powheg_qcd
      cats['powheg_qqh'] =  mva_powheg_qqh
      cats['powheg_ztt'] =  mva_powheg_ztt

      # cats['0jet'] = '(n_jets==0 && n_bjets==0)'
      # cats['dijet']='n_jets>=2 && mjj>300 && n_bjets==0'
      # cats['dijet_boosted']='%s && pt_tt>150 && n_bjets==0' % cats['dijet']
      # cats['dijet_lowboost']='%s && pt_tt<150 && n_bjets==0' % cats['dijet']
      # cats['boosted'] = '(!(%s) && !(%s) && n_bjets==0)' % (cats['0jet'], cats['dijet'])
  # else:
# if options.era == 'cpsummer16':
#   if options.channel in ['em','mt','et']:
#       cats['0jet'] = '(n_jets==0 && n_bjets==0)'
#       cats['dijet']='n_jets>=2 && mjj>300 && n_bjets==0'
#       cats['dijet_boosted']='%s && pt_tt>200' % cats['dijet']
#       cats['dijet_lowboost']='%s && pt_tt<200' % cats['dijet']
#       cats['boosted'] = '(!(%s) && !(%s) && n_bjets==0)' % (cats['0jet'], cats['dijet'])
#   else:
#     cats['0jet'] = '(n_jets==0)'
#     cats['dijet']='n_jets>=2 && mjj>300'
#     cats['dijet_boosted']='%s && pt_tt>150' % cats['dijet']
#     cats['dijet_lowboost']='%s && pt_tt<200' % cats['dijet']
#     cats['boosted'] = '(!(%s) && !(%s))' % (cats['0jet'], cats['dijet'])





  # aachen groups cuts
  #if options.channel == 'mt':
  #  cats['baseline'] = '(iso_1<0.15 && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && !leptonveto && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))'
  #  cats['baseline_loose'] = '(iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto && (trg_singlemuon*(pt_1>23) || trg_mutaucross*(pt_1<23)))'
  #if options.channel == 'et':
  #  cats['baseline'] = '(iso_1<0.1  && mva_olddm_tight_2>0.5 && antiele_2 && antimu_2 && !leptonveto && pt_2>30 && trg_singleelectron)'
  #  cats['baseline_loose'] = '(iso_1<0.3 && mva_olddm_medium_2>0.5 && antiele_2 && antimu_2 && !leptonveto && trg_singleelectron)'
  #if options.channel == 'tt':
  #  cats['baseline'] = '(mva_olddm_tight_1>0.5 && mva_olddm_tight_2>0.5 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto && trg_doubletau)'
  #  cats['tt_qcd_norm'] = '(((mva_olddm_loose_1>0.5 && mva_olddm_tight_1<0.5 && mva_olddm_medium_2>0.5) || (mva_olddm_loose_2>0.5 && mva_olddm_tight_2<0.5 && mva_olddm_medium_1>0.5)) && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto)&&trg_doubletau'
 #
 # cats['0jet'] = 'n_jets==0'
 # if options.channel == 'mt':
 #   cats['boosted'] = '((n_jets==1)||(n_jets>1&&!(mjj>300&&pt_2>40&&pt_tt>50)))'
 # if options.channel == 'et':
 #   cats['boosted'] = '((n_jets==1)||(n_jets>1&&!(mjj>300&&pt_tt>50)))'
 # if options.channel == 'em':
 #   cats['boosted'] = '((n_jets==1)||(n_jets==2&&!(mjj>300&&pzeta>-10))||(n_jets>2))'
 # if options.channel == 'tt':
 #   cats['boosted'] = '((n_jets==1)||(n_jets>1&&!(jdeta>2.5&&pt_tt>100)))'

 # cats['dijet_boosted'] = '(mjj>500)*(jdeta>2.0)*(n_jets>1)*(pt_tt>150.)*(m_sv>100)'
 # cats['dijet_highM'] = '(mjj>500)*(jdeta>2.0)*(n_jets>1)*(pt_tt<150.)*(m_sv>100)'
 # cats['dijet_lowM'] = '(mjj>500)*(jdeta>2.0)*(n_jets>1)*(pt_tt<150.)*(m_sv<100)'
 # cats['dijet_lowMjj'] = '(mjj>300)*(mjj<500)*(n_jets>1)'
 #
 # if options.channel == 'em':
 #   cats['dijet_boosted']+='&& n_bjets<1'
 #   cats['dijet_highM']+='&& n_bjets<1'
 #   cats['dijet_lowM']+='&& n_bjets<1'
 #   cats['dijet_lowMjj']+='&& n_bjets<1'
 #
  # end of aachen cuts

# 2016 sm analysis uses relaxed shape selections for W + WCD processes in et and mt channel, these are set here
if options.era in ['smsummer16','cpsummer16']:
  if options.channel in ['et','mt']: cats['qcd_shape'] = '('+cats['baseline_loose']+')*('+cats[options.cat]+')'
  if options.cat in ['boosted','vbf','dijet','dijet_lowM','dijet_highM','dijet_lowboost','dijet_boosted', 'dijet_lowMjj', ## add all mva cats as well for now (also in some systematics, see below)
          'mva_JHU_ggh','mva_JHU_misc','mva_JHU_qcd','mva_JHU_qqh','mva_JHU_tt','mva_JHU_w','mva_JHU_zll','mva_JHU_ztt',
          'mva_powheg_ggh','mva_powheg_misc','mva_powheg_qcd','mva_powheg_qqh','mva_powheg_tt','mva_powheg_w','mva_powheg_zll','mva_powheg_ztt']:
      cats['w_shape'] = cats['qcd_shape']


# Overwrite selection depending on whether tight or loose-mt categories is chosen - this can still be overwritten from command line using the --set_alias=sel:(...) option
if options.cat == 'nobtag_tight' or options.cat == 'btag_tight':
    if options.channel == 'mt' or options.channel == 'et': options.sel = '(mt_1<40)'
if options.cat == 'nobtag_loosemt' or options.cat == 'btag_loosemt':
    if options.channel == 'mt' or options.channel == 'et': options.sel = '(mt_1<70 && mt_1>40)'

if options.era == "mssmsummer16":
    if options.channel == "em": cats['baseline']+=" && trg_muonelectron"
    if options.channel == "et" or options.channel == 'zee': cats['baseline']+=" && trg_singleelectron"
    if options.channel in ['mt','zmm','mj']: cats['baseline']+=" && trg_singlemuon"
    if options.channel == "tt": cats['baseline']+=" && trg_doubletau"

# Overwrite any category selections if the --set_alias option is used
for i in options.set_alias:
    cat_to_overwrite = i.split(':')[0]
    cat_to_overwrite=cat_to_overwrite.replace("\"","")
    overwrite_with = i.split(':')[1]
    overwrite_with=overwrite_with.replace("\"","")
    start_index=overwrite_with.find("{")
    end_index=overwrite_with.find("}")
    while start_index >0:
        replace_with=overwrite_with[start_index:end_index+1]
        replace_with=replace_with.replace("{","")
        replace_with=replace_with.replace("}","")
        replace_string = cats[replace_with]
        overwrite_with=overwrite_with[0:start_index] + replace_string  + overwrite_with[end_index+1:]
        start_index=overwrite_with.find("{")
        end_index=overwrite_with.find("}")

    print 'Overwriting alias: \"'+cat_to_overwrite+'\" with selection: \"'+overwrite_with+'\"'
    if cat_to_overwrite == 'sel':
        options.sel = overwrite_with
    else:
        cats[cat_to_overwrite] = overwrite_with

# Additional selections to seperate MC samples by gen flags

z_sels = {}
if options.channel == 'et':
    z_sels['ztt_sel'] = '(gen_match_2==5)'
    z_sels['zl_sel'] = '(gen_match_2<5)'
    z_sels['zj_sel'] = '(gen_match_2==6)'
elif options.channel in ['mt','mj']:
    z_sels['ztt_sel'] = '(gen_match_2==5)'
    z_sels['zl_sel'] = '(gen_match_2<5)'
    z_sels['zj_sel'] = '(gen_match_2==6)'
elif options.channel in ['mj']:
    z_sels['ztt_sel'] = '(0)'
    z_sels['zl_sel'] = '(0)'
    z_sels['zj_sel'] = '(1)'
elif options.channel == 'tt':
    z_sels['ztt_sel'] = '(gen_match_1==5&&gen_match_2==5)'
    z_sels['zl_sel'] = '(gen_match_2<6&&gen_match_1<6&&!(gen_match_1==5&&gen_match_2==5))'
    z_sels['zj_sel'] = '(gen_match_2==6||gen_match_1==6)'
elif options.channel == 'em':
    z_sels['ztt_sel'] = '(gen_match_1>2 && gen_match_2>3)'
    z_sels['zll_sel'] = '(gen_match_1<3 || gen_match_2<4)'
elif options.channel == 'zee' or  options.channel == 'zmm':
    z_sels['ztt_sel'] = '(gen_match_1>2&&gen_match_1<6 && gen_match_2>2&&gen_match_2<6)'
    if options.channel == 'zmm': z_sels['zl_sel'] = '(gen_match_1==2&&gen_match_2==2)'
    else: z_sels['zl_sel'] = '(gen_match_1==1&&gen_match_2==1)'
    z_sels['zj_sel'] = '(!('+z_sels['zl_sel']+') && !('+z_sels['ztt_sel']+'))'

top_sels = {}
vv_sels = {}
top_sels['ttt_sel'] = z_sels['ztt_sel']
top_sels['ttj_sel'] = '!('+z_sels['ztt_sel']+')'
vv_sels['vvt_sel'] = z_sels['ztt_sel']
vv_sels['vvj_sel'] = '!('+z_sels['ztt_sel']+')'

if options.channel == 'zee' or  options.channel == 'zmm':
  top_sels['ttt_sel'] = z_sels['zl_sel']
  top_sels['ttj_sel'] = '!('+z_sels['zl_sel']+')'
  vv_sels['vvt_sel'] = z_sels['zl_sel']
  vv_sels['vvj_sel'] = '!('+z_sels['zl_sel']+')'


top_sels_embed = {}
if options.channel == 'mt': top_sels_embed['ttt_sel'] = '((gen_match_1 == 4) && (gen_match_2 == 5))'
if options.channel == 'et': top_sels_embed['ttt_sel'] = '((gen_match_1 == 3) && (gen_match_2 == 5))'
if options.channel == 'tt': top_sels_embed['ttt_sel'] = '((gen_match_1 == 5) && (gen_match_2 == 5))'
if options.channel == 'em': top_sels_embed['ttt_sel'] = '((gen_match_1 == 3) && (gen_match_2 == 4))'

if options.channel in ['et','mt','mj']:
  vv_sels['vvt_sel'] = '(gen_match_2<6)'
  vv_sels['vvj_sel'] = '(gen_match_2==6)'
  top_sels['ttt_sel'] = '(gen_match_2<6)'
  top_sels['ttj_sel'] = '(gen_match_2==6)'
elif options.channel == 'tt':
  vv_sels['vvt_sel'] = '(gen_match_1<6 && gen_match_2<6)'
  vv_sels['vvj_sel'] = '(!(gen_match_1<6 && gen_match_2<6))'
  top_sels['ttt_sel'] = '(gen_match_1<6 && gen_match_2<6)'
  top_sels['ttj_sel'] = '(!(gen_match_1<6 && gen_match_2<6))'
if options.channel in ['mj']:
  vv_sels['vvt_sel'] = '(0)'
  vv_sels['vvj_sel'] = '(1)'
  top_sels['ttt_sel'] = '(0)'
  top_sels['ttj_sel'] = '(1)'

if options.era in ["smsummer16",'cpsummer16','tauid2016']:
  if options.channel in ['mt','et']:
    z_sels['ztt_sel'] = '(gen_match_2==5)'
    z_sels['zl_sel'] = '(gen_match_2!=6&&gen_match_2!=5)'
    z_sels['zj_sel'] = '(gen_match_2==6)'
    vv_sels['vvt_sel'] = '(gen_match_2==5)'
    vv_sels['vvj_sel'] = '(gen_match_2!=5)'
    top_sels['ttt_sel'] = '(gen_match_2==5)'
    top_sels['ttj_sel'] = '(gen_match_2!=5)'
  elif options.channel == 'tt':
    z_sels['ztt_sel'] = '(gen_match_1==5&&gen_match_2==5)'
    z_sels['zl_sel'] = '(!(gen_match_1==6 || gen_match_2==6) && !(gen_match_1==5&&gen_match_2==5))'
    z_sels['zj_sel'] = '(gen_match_1==6 || gen_match_2==6)'
    vv_sels['vvt_sel'] = '(gen_match_1==5 && gen_match_2==5)'
    vv_sels['vvj_sel'] = '(!(gen_match_1==5 && gen_match_2==5))'
    top_sels['ttt_sel'] = '(gen_match_1==5 && gen_match_2==5)'
    top_sels['ttj_sel'] = '(!(gen_match_1==5 && gen_match_2==5))'

if options.embedding:
    extra_top_sel = '1'
    if options.channel == 'mt': extra_top_sel = '!((gen_match_1 == 4) && (gen_match_2 == 5))'
    if options.channel == 'et': extra_top_sel = '!((gen_match_1 == 3) && (gen_match_2 == 5))'
    if options.channel == 'tt': extra_top_sel = '!((gen_match_1 == 5) && (gen_match_2 == 5))'
    if options.channel == 'em': extra_top_sel = '!((gen_match_1 == 3) && (gen_match_2 == 4))'
    for sel in top_sels: top_sels[sel]+='&&'+extra_top_sel

# Add data sample names
if options.channel == 'mt':
    data_samples = ['SingleMuonB','SingleMuonC','SingleMuonD']
if options.channel == 'em':
    data_samples = ['MuonEGB','MuonEGC','MuonEGD']
if options.channel == 'et':
    data_samples = ['SingleElectronB','SingleElectronC','SingleElectronD']
if options.channel == 'tt':
    data_samples = ['TauB','TauC','TauD']

# Add MC sample names
ztt_samples = ['DYJetsToLL-LO-ext','DY1JetsToLL-LO','DY2JetsToLL-LO','DY3JetsToLL-LO','DY4JetsToLL-LO','DYJetsToLL_M-10-50-LO']
vv_samples = ['T-tW', 'Tbar-tW','Tbar-t','T-t','WWTo1L1Nu2Q','WZJToLLLNu','VVTo2L2Nu','ZZTo2L2Q','ZZTo4L','WZTo2L2Q','WZTo1L3Nu','WZTo1L1Nu2Q']
wgam_samples = ['WGToLNuG','WGstarToLNuEE','WGstarToLNuMuMu']
top_samples = ['TT']
ztt_shape_samples = ['DYJetsToLL-LO-ext','DY1JetsToLL-LO','DY2JetsToLL-LO','DY3JetsToLL-LO','DY4JetsToLL-LO','DYJetsToLL_M-10-50-LO']
wjets_samples = ['WJetsToLNu-LO','W1JetsToLNu-LO','W2JetsToLNu-LO','W3JetsToLNu-LO','W4JetsToLNu-LO']
ewkz_samples = []
gghww_samples = []
qqhww_samples = []

if options.era in ["mssmsummer16","smsummer16",'cpsummer16','tauid2016']:
    # Add data sample names
    if options.channel in ['mt','zmm','mj']:
        data_samples = ['SingleMuonB','SingleMuonC','SingleMuonD','SingleMuonE','SingleMuonF','SingleMuonG','SingleMuonHv2','SingleMuonHv3']
    if options.channel == 'em':
        data_samples = ['MuonEGB','MuonEGC','MuonEGD','MuonEGE','MuonEGF','MuonEGG','MuonEGHv2','MuonEGHv3']
    if options.channel == 'et' or options.channel == 'zee':
        data_samples = ['SingleElectronB','SingleElectronC','SingleElectronD','SingleElectronE','SingleElectronF','SingleElectronG','SingleElectronHv2','SingleElectronHv3']
    if options.channel == 'tt':
        data_samples = ['TauB','TauC','TauD','TauE','TauF','TauG','TauHv2','TauHv3']

    # Add MC sample names
    ztt_samples = ['DYJetsToLL-LO-ext1','DYJetsToLL-LO-ext2','DY1JetsToLL-LO','DY2JetsToLL-LO','DY3JetsToLL-LO','DY4JetsToLL-LO','DYJetsToLL_M-10-50-LO']
    vv_samples = ['T-tW', 'Tbar-tW','Tbar-t','T-t','WWTo1L1Nu2Q','WZJToLLLNu','VVTo2L2Nu','VVTo2L2Nu-ext1','ZZTo2L2Q','ZZTo4L-amcat','WZTo2L2Q','WZTo1L3Nu','WZTo1L1Nu2Q']
    wgam_samples = ['WGToLNuG','WGToLNuG-ext','WGstarToLNuEE','WGstarToLNuMuMu']
    top_samples = ['TT']
    ztt_shape_samples = ['DYJetsToLL-LO-ext2','DY1JetsToLL-LO','DY2JetsToLL-LO','DY3JetsToLL-LO','DY4JetsToLL-LO','DYJetsToLL_M-10-50-LO']
    wjets_samples = ['WJetsToLNu-LO', 'WJetsToLNu-LO-ext','W1JetsToLNu-LO','W2JetsToLNu-LO','W2JetsToLNu-LO-ext','W3JetsToLNu-LO','W3JetsToLNu-LO-ext','W4JetsToLNu-LO','W4JetsToLNu-LO-ext1','W4JetsToLNu-LO-ext2']

    if options.channel == 'mt': embed_samples = ['EmbeddingMuTauB','EmbeddingMuTauC','EmbeddingMuTauD','EmbeddingMuTauE','EmbeddingMuTauF','EmbeddingMuTauG','EmbeddingMuTauH']
    if options.channel == 'et': embed_samples = ['EmbeddingElTauB','EmbeddingElTauC','EmbeddingElTauD','EmbeddingElTauE','EmbeddingElTauF','EmbeddingElTauG','EmbeddingElTauH']
    if options.channel == 'em': embed_samples = ['EmbeddingElMuB','EmbeddingElMuC','EmbeddingElMuD','EmbeddingElMuE','EmbeddingElMuF','EmbeddingElMuG','EmbeddingElMuH']
    if options.channel == 'tt': embed_samples = ['EmbeddingTauTauB','EmbeddingTauTauC','EmbeddingTauTauD','EmbeddingTauTauE','EmbeddingTauTauF','EmbeddingTauTauG','EmbeddingTauTauH']
    if options.channel == 'zmm': embed_samples = ['EmbeddingMuMuB','EmbeddingMuMuC','EmbeddingMuMuD','EmbeddingMuMuE','EmbeddingMuMuF','EmbeddingMuMuG','EmbeddingMuMuH']
    if options.channel == 'zee': embed_samples = ['EmbeddingElElB','EmbeddingElElC','EmbeddingElElD','EmbeddingElElE','EmbeddingElElF','EmbeddingElElG','EmbeddingElElH']


if options.era in ["smsummer16",'cpsummer16','tauid2016']:
    vv_samples = ['T-tW', 'Tbar-tW','Tbar-t','T-t','WWTo1L1Nu2Q','WZJToLLLNu','VVTo2L2Nu','VVTo2L2Nu-ext1','ZZTo2L2Q','ZZTo4L-amcat','WZTo2L2Q','WZTo1L3Nu','WZTo1L1Nu2Q']
    wjets_samples = ['WJetsToLNu-LO', 'WJetsToLNu-LO-ext','W1JetsToLNu-LO','W2JetsToLNu-LO','W2JetsToLNu-LO-ext','W3JetsToLNu-LO','W3JetsToLNu-LO-ext','W4JetsToLNu-LO','W4JetsToLNu-LO-ext1','W4JetsToLNu-LO-ext2', 'EWKWMinus2Jets_WToLNu','EWKWMinus2Jets_WToLNu-ext1','EWKWMinus2Jets_WToLNu-ext2','EWKWPlus2Jets_WToLNu','EWKWPlus2Jets_WToLNu-ext1','EWKWPlus2Jets_WToLNu-ext2']
    ewkz_samples = ['EWKZ2Jets_ZToLL','EWKZ2Jets_ZToLL-ext']#,'EWKZ2Jets_ZToNuNu','EWKZ2Jets_ZToNuNu-ext'] TOOK THESE OUT THEY ARE BASICALLY EMPTY
    gghww_samples = ['GluGluHToWWTo2L2Nu_M-125']
    qqhww_samples = ['VBFHToWWTo2L2Nu_M-125']

sm_samples = { 'ggH' : 'GluGluHToTauTau_M-*', 'qqH' : 'VBFHToTauTau_M-*', 'WplusH' : 'WplusHToTauTau_M-*', 'WminusH' : 'WminusHToTauTau_M-*', 'ZH' : 'ZHToTauTau_M-*', 'TTH' : 'TTHToTauTau_M-*' }
if options.era in ["smsummer16"]: sm_samples = { 'ggH_htt' : 'GluGluToHToTauTau_M-*', 'qqH_htt' : 'VBFHToTauTau_M-*', 'WplusH_htt' : 'WplusHToTauTau_M-*', 'WminusH_htt' : 'WminusHToTauTau_M-*', 'ZH_htt' : 'ZHToTauTau_M-*'}
if options.era in ['cpsummer16']: sm_samples = { 'ggH_htt' : 'GluGluToHToTauTau_M-*', 'qqH_htt' : 'VBFHToTauTau_M-*', 'WplusH_htt' : 'WplusHToTauTau_M-*', 'WminusH_htt' : 'WminusHToTauTau_M-*', 'ZH_htt' : 'ZHToTauTau_M-*', 'ggHsm_htt' : 'GluGluH2JetsToTauTau_M*_CPmixing_sm', 'ggHmm_htt' : 'GluGluH2JetsToTauTau_M*_CPmixing_maxmix', 'ggHps_htt' : 'GluGluH2JetsToTauTau_M*_CPmixing_pseudoscalar', 'qqHsm_htt' : 'VBFHiggs0PM_M-*', 'qqHmm_htt' : 'VBFHiggs0Mf05ph0_M-*', 'qqHps_htt' : 'VBFHiggs0M_M-*'}#, 'ggHMG_htt':'GluGluToHToTauTau_amcNLO_M-*'}


# if options.era in ['cpsummer16']: sm_samples = { 'ggH_htt' : 'GluGluToHToTauTau_M-*', 'qqH_htt' : 'VBFHToTauTau_M-*', 'WplusH_htt' : 'WplusHToTauTau_M-*', 'WminusH_htt' : 'WminusHToTauTau_M-*', 'ZH_htt' : 'ZHToTauTau_M-*', 'ggHsm_htt' : 'GluGluH2JetsToTauTau_M*_CPmixing_sm'}#, 'ggHmm_htt' : 'GluGluH2JetsToTauTau_M*_CPmixing_maxmix', 'ggHps_htt' : 'GluGluH2JetsToTauTau_M*_CPmixing_pseudoscalar', 'qqHsm_htt' : 'VBFHiggs0PM_M-*', 'qqHmm_htt' : 'VBFHiggs0Mf05ph0_M-*', 'qqHps_htt' : 'VBFHiggs0M_M-*'}#, 'ggHMG_htt':'GluGluToHToTauTau_amcNLO_M-*'}
# removing TTH for now because it isn't processed
if options.analysis == 'mssm': sm_samples = { 'ggH' : 'GluGluToHToTauTau_M-*', 'qqH' : 'VBFHToTauTau_M-*', 'WplusH' : 'WplusHToTauTau_M-*', 'WminusH' : 'WminusHToTauTau_M-*', 'ZH' : 'ZHToTauTau_M-*'}
mssm_samples = { 'ggH' : 'SUSYGluGluToHToTauTau_M-*', 'bbH' : 'SUSYGluGluToBBHToTauTau_M-*' }
mssm_nlo_samples = { 'bbH' : 'SUSYGluGluToBBHToTauTau_M-*-NLO' }
mssm_lo_samples = { 'bbH-LO' : 'SUSYGluGluToBBHToTauTau_M-*' }
mssm_nlo_qsh_samples = { 'bbH-QshUp' : 'SUSYGluGluToBBHToTauTau_M-*-NLO-QshUp', 'bbH-QshDown' : 'SUSYGluGluToBBHToTauTau_M-*-NLO-QshDown' }
if options.nlo_qsh: mssm_nlo_samples.update(mssm_nlo_qsh_samples)
Hhh_samples = { 'ggH' : 'GluGluToRadionToHHTo2B2Tau_M-*' }

# set systematics: first index sets folder name contaning systematic samples, second index sets string to be appended to output histograms, third index specifies the weight to be applied , 4th lists samples that should be skipped
systematics = OrderedDict()
if not options.no_default: systematics['default'] = ('','', 'wt', [], False)

if options.syst_e_scale != '':
    systematics['scale_e_up'] = ('ESCALE_UP' , '_'+options.syst_e_scale+'Up', 'wt', ['jetFakes','ZTT','ZJ','ZL','ZLL','VVT','VVJ','VV','TTT','TTJ','TT','QCD','W','signal','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EWKZ'], False)
    systematics['scale_e_down'] = ('ESCALE_DOWN' , '_'+options.syst_e_scale+'Down', 'wt', ['jetFakes','ZTT','ZJ','ZL','ZLL','VVT','VVJ','VV','TTT','TTJ','TT','QCD','W','signal','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EWKZ'], False)
if options.syst_mu_scale != '':
    systematics['scale_mu_up'] = ('MUSCALE_UP' , '_'+options.syst_mu_scale+'Up', 'wt',['jetFakes','ZTT','ZJ','ZL','ZLL','VVT','VVJ','VV','TTT','TTJ','TT','QCD','W','signal','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EWKZ'], False)
    systematics['scale_mu_down'] = ('MUSCALE_DOWN' , '_'+options.syst_mu_scale+'Down', 'wt', ['jetFakes','ZTT','ZJ','ZL','ZLL','VVT','VVJ','VV','TTT','TTJ','TT','QCD','W','signal','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EWKZ'], False)
if options.syst_tau_scale != '':
    systematics['scale_t_up'] = ('TSCALE_UP' , '_'+options.syst_tau_scale+'Up', 'wt', ['jetFakes'], False)
    systematics['scale_t_down'] = ('TSCALE_DOWN' , '_'+options.syst_tau_scale+'Down', 'wt', ['jetFakes'], False)
if options.syst_tau_scale_0pi != '':
    systematics['scale_t_0pi_up'] = ('TSCALE0PI_UP' , '_'+options.syst_tau_scale_0pi+'Up', 'wt', ['QCD','jetFakes'], False)
    systematics['scale_t_0pi_down'] = ('TSCALE0PI_DOWN' , '_'+options.syst_tau_scale_0pi+'Down', 'wt', ['QCD','jetFakes'], False)
if options.syst_tau_scale_1pi != '':
    systematics['scale_t_1pi_up'] = ('TSCALE1PI_UP' , '_'+options.syst_tau_scale_1pi+'Up', 'wt', ['QCD','jetFakes'], False)
    systematics['scale_t_1pi_down'] = ('TSCALE1PI_DOWN' , '_'+options.syst_tau_scale_1pi+'Down', 'wt', ['QCD','jetFakes'], False)
if options.syst_tau_scale_3prong != '':
    systematics['scale_t_3prong_up'] = ('TSCALE3PRONG_UP' , '_'+options.syst_tau_scale_3prong+'Up', 'wt', ['QCD','jetFakes'], False)
    systematics['scale_t_3prong_down'] = ('TSCALE3PRONG_DOWN' , '_'+options.syst_tau_scale_3prong+'Down', 'wt', ['QCD','jetFakes'], False)
if options.syst_efake_0pi_scale != '':
    systematics['scale_efake_0pi_up'] = ('EFAKE0PI_UP' , '_'+options.syst_efake_0pi_scale+'Up', 'wt', ['ZTT','VVT','VVJ','TTT','TTJ','QCD','signal','W','jetFakes','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
    systematics['scale_efake_0pi_down'] = ('EFAKE0PI_DOWN' , '_'+options.syst_efake_0pi_scale+'Down', 'wt', ['ZTT','VVT','VVJ','TTT','TTJ','QCD','signal','W','jetFakes','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
if options.syst_efake_1pi_scale != '':
    systematics['scale_efake_1pi_up'] = ('EFAKE1PI_UP' , '_'+options.syst_efake_1pi_scale+'Up', 'wt', ['ZTT','VVT','VVJ','TTT','TTJ','QCD','signal','W','jetFakes','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
    systematics['scale_efake_1pi_down'] = ('EFAKE1PI_DOWN' , '_'+options.syst_efake_1pi_scale+'Down', 'wt', ['ZTT','VVT','VVJ','TTT','TTJ','QCD','signal','W','jetFakes','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
if options.syst_mufake_0pi_scale != '':
    systematics['scale_mufake_0pi_up'] = ('MUFAKE0PI_UP' , '_'+options.syst_mufake_0pi_scale+'Up', 'wt', ['ZTT','VVT','VVJ','TTT','TTJ','QCD','signal','W','jetFakes','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
    systematics['scale_mufake_0pi_down'] = ('MUFAKE0PI_DOWN' , '_'+options.syst_mufake_0pi_scale+'Down', 'wt', ['ZTT','VVT','VVJ','TTT','TTJ','QCD','signal','W','jetFakes','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
if options.syst_mufake_1pi_scale != '':
    systematics['scale_mufake_1pi_up'] = ('MUFAKE1PI_UP' , '_'+options.syst_mufake_1pi_scale+'Up', 'wt', ['ZTT','VVT','VVJ','TTT','TTJ','QCD','signal','W','jetFakes','ggH_hww125','qqH_hww125','EmbedZTT'], False)
    systematics['scale_mufake_1pi_down'] = ('MUFAKE1PI_DOWN' , '_'+options.syst_mufake_1pi_scale+'Down', 'wt', ['ZTT','VVT','VVJ','TTT','TTJ','QCD','signal','W','jetFakes','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
if options.syst_eff_t != '':
    systematics['syst_eff_t_up'] = ('' , '_'+options.syst_eff_t+'Up', 'wt*wt_tau_id_up', ['ZL','ZJ','VVJ','TTJ','QCD','W'], False)
    systematics['syst_eff_t_down'] = ('' , '_'+options.syst_eff_t+'Down', 'wt*wt_tau_id_down', ['ZL','ZJ','VVJ','TTJ','QCD','W'], False)
if options.syst_tquark != '':
    systematics['syst_tquark_up'] = ('' , '_'+options.syst_tquark+'Up', 'wt*wt_tquark_up', ['ZTT','ZL','ZJ','VVT','VVJ','QCD','W','signal','jetFakes','EWKZ','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
    systematics['syst_tquark_down'] = ('' , '_'+options.syst_tquark+'Down', 'wt*wt_tquark_down', ['ZTT','ZL','ZJ','VVJ','VVT','QCD','W', 'signal','jetFakes','EWKZ','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
if options.syst_zwt != '':
    systematics['syst_zwt_up'] = ('' , '_'+options.syst_zwt+'Up', 'wt*wt_zpt_up', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
    systematics['syst_zwt_down'] = ('' , '_'+options.syst_zwt+'Down', 'wt*wt_zpt_down', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
if options.syst_w_fake_rate != '':
    to_skip = ['ZTT','ZL','ZJ','VVT','VVJ','TTT','TTJ','QCD','signal','jetFakes','EWKZ','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT']
    if options.era in ["smsummer16",'cpsummer16','tauid2016']: to_skip = ['ZTT','ZL','VVT','TTT','QCD','signal','jetFakes','EWKZ','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT']
    systematics['syst_w_fake_rate_up'] = ('' , '_'+options.syst_w_fake_rate+'Up', 'wt*wt_tau_fake_up', to_skip, False)
    systematics['syst_w_fake_rate_down'] = ('' , '_'+options.syst_w_fake_rate+'Down', 'wt*wt_tau_fake_down', to_skip, False)
if options.syst_jfake_m != '':
    systematics['syst_jfake_m_up'] = ('' , '_'+options.syst_jfake_m+'Up', 'wt*idisoweight_up_2', ['ZTT','QCD','signal','TT','EmbedZTT'], False)
    systematics['syst_jfake_m_down'] = ('' , '_'+options.syst_jfake_m+'Down', 'wt*idisoweight_down_2', ['ZTT','QCD','signal','TT','EmbedZTT'], False)
if options.syst_jfake_e != '':
    systematics['syst_jfake_e_up'] = ('' , '_'+options.syst_jfake_e+'Up', 'wt*idisoweight_up_1', ['ZTT','QCD','signal','TT','EmbedZTT'], False)
    systematics['syst_jfake_e_down'] = ('' , '_'+options.syst_jfake_e+'Down', 'wt*idisoweight_down_1', ['ZTT','QCD','signal','TT','EmbedZTT'], False)
if options.syst_scale_j != '':
    systematics['syst_scale_j_up'] = ('JES_UP' , '_'+options.syst_scale_j+'Up', 'wt', ['EmbedZTT'], False)
    systematics['syst_scale_j_down'] = ('JES_DOWN' , '_'+options.syst_scale_j+'Down', 'wt', ['EmbedZTT'], False)
if options.syst_scale_j_rbal != '':
    systematics['syst_scale_j_rbal_up'] = ('JESRBAL_UP' , '_'+options.syst_scale_j_rbal+'Up', 'wt', ['EmbedZTT'], False)
    systematics['syst_scale_j_rbal_down'] = ('JESRBAL_DOWN' , '_'+options.syst_scale_j_rbal+'Down', 'wt', ['EmbedZTT'], False)
if options.syst_scale_j_full != '':
    systematics['syst_scale_j_full_up'] = ('JESFULL_UP' , '_'+options.syst_scale_j_full+'Up', 'wt', ['EmbedZTT'], False)
    systematics['syst_scale_j_full_down'] = ('JESFULL_DOWN' , '_'+options.syst_scale_j_full+'Down', 'wt', ['EmbedZTT'], False)
if options.syst_scale_j_cent != '':
    systematics['syst_scale_j_cent_up'] = ('JESCENT_UP' , '_'+options.syst_scale_j_cent+'Up', 'wt', ['EmbedZTT'], False)
    systematics['syst_scale_j_cent_down'] = ('JESCENT_DOWN' , '_'+options.syst_scale_j_cent+'Down', 'wt', ['EmbedZTT'], False)
if options.syst_scale_j_hf != '':
    systematics['syst_scale_j_hf_up'] = ('JESHF_UP' , '_'+options.syst_scale_j_hf+'Up', 'wt', ['EmbedZTT'], False)
    systematics['syst_scale_j_hf_down'] = ('JESHF_DOWN' , '_'+options.syst_scale_j_hf+'Down', 'wt', ['EmbedZTT'], False)
if options.syst_eff_b != '':
    systematics['syst_b_up'] = ('BTAG_UP' , '_'+options.syst_eff_b+'Up', 'wt', ['EmbedZTT'], False)
    systematics['syst_b_down'] = ('BTAG_DOWN' , '_'+options.syst_eff_b+'Down', 'wt', ['EmbedZTT'], False)
if options.syst_fake_b != '':
    systematics['syst_fake_b_up'] = ('BFAKE_UP' , '_'+options.syst_fake_b+'Up', 'wt', ['EmbedZTT'], False)
    systematics['syst_fake_b_down'] = ('BFAKE_DOWN' , '_'+options.syst_fake_b+'Down', 'wt', ['EmbedZTT'], False)
if options.syst_zpt_es != '':
    systematics['syst_zpt_es_up'] = ('' , '_'+options.syst_zpt_es+'Up', 'wt*wt_zpt_esup', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
    systematics['syst_zpt_es_down'] = ('' , '_'+options.syst_zpt_es+'Down', 'wt*wt_zpt_esdown', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
if options.syst_zpt_tt != '':
    systematics['syst_zpt_tt_up'] = ('' , '_'+options.syst_zpt_tt+'Up', 'wt*wt_zpt_ttup', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
    systematics['syst_zpt_tt_down'] = ('' , '_'+options.syst_zpt_tt+'Down', 'wt*wt_zpt_ttdown', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
if options.syst_zpt_statpt0 != '':
    systematics['syst_zpt_statpt0_up'] = ('' , '_'+options.syst_zpt_statpt0+'Up', 'wt*wt_zpt_stat_m400pt0_up', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
    systematics['syst_zpt_statpt0_down'] = ('' , '_'+options.syst_zpt_statpt0+'Down', 'wt*wt_zpt_stat_m400pt0_down', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
if options.syst_zpt_statpt40 != '':
    systematics['syst_zpt_statpt40_up'] = ('' , '_'+options.syst_zpt_statpt40+'Up', 'wt*wt_zpt_stat_m400pt40_up', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
    systematics['syst_zpt_statpt40_down'] = ('' , '_'+options.syst_zpt_statpt40+'Down', 'wt*wt_zpt_stat_m400pt40_down', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
if options.syst_zpt_statpt80 != '':
    systematics['syst_zpt_statpt80_up'] = ('' , '_'+options.syst_zpt_statpt80+'Up', 'wt*wt_zpt_stat_m400pt80_up', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
    systematics['syst_zpt_statpt80_down'] = ('' , '_'+options.syst_zpt_statpt80+'Down', 'wt*wt_zpt_stat_m400pt80_down', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
if options.syst_z_mjj != '' and options.cat in ['vbf','dijet','dijet_lowM','dijet_highM','dijet_lowboost','dijet_boosted', 'dijet_lowMjj',
    'mva_JHU_ggh','mva_JHU_misc','mva_JHU_qcd','mva_JHU_qqh','mva_JHU_tt','mva_JHU_w','mva_JHU_zll','mva_JHU_ztt',
    'mva_powheg_ggh','mva_powheg_misc','mva_powheg_qcd','mva_powheg_qqh','mva_powheg_tt','mva_powheg_w','mva_powheg_zll','mva_powheg_ztt']:
    systematics['syst_z_mjj_up'] = ('' , '_'+options.syst_z_mjj+'Up', 'wt*wt_z_mjj_up', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','ggH_hww125','qqH_hww125', 'ggH_hww', 'qqH_hww','EmbedZTT'], False)
    systematics['syst_z_mjj_down'] = ('' , '_'+options.syst_z_mjj+'Down', 'wt*wt_z_mjj_down', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','ggH_hww125','qqH_hww125', 'ggH_hww', 'qqH_hww','EmbedZTT'], False)
if options.syst_qcd_scale != '' and options.cat in ['0jet','boosted','vbf','dijet','dijet_lowM','dijet_highM','dijet_lowboost','dijet_boosted', 'dijet_lowMjj',
    'mva_JHU_ggh','mva_JHU_misc','mva_JHU_qcd','mva_JHU_qqh','mva_JHU_tt','mva_JHU_w','mva_JHU_zll','mva_JHU_ztt',
    'mva_powheg_ggh','mva_powheg_misc','mva_powheg_qcd','mva_powheg_qqh','mva_powheg_tt','mva_powheg_w','mva_powheg_zll','mva_powheg_ztt'] and options.channel in ['em','et','mt','tt']:
    weight_up = 'wt*wt_scale_%s_%s' % (options.channel, options.cat)
    weight_down = 'wt*(2-wt_scale_%s_%s)' % (options.channel, options.cat)
    if options.cat in ['dijet','dijet_lowM','dijet_highM','dijet_lowboost','dijet_boosted', 'dijet_lowMjj',
            'mva_JHU_ggh','mva_JHU_misc','mva_JHU_qcd','mva_JHU_qqh','mva_JHU_tt','mva_JHU_w','mva_JHU_zll','mva_JHU_ztt',
            'mva_powheg_ggh','mva_powheg_misc','mva_powheg_qcd','mva_powheg_qqh','mva_powheg_tt','mva_powheg_w','mva_powheg_zll','mva_powheg_ztt']:
      weight_up = 'wt*wt_scale_%s_vbf' % (options.channel)
      weight_down = 'wt*(2-wt_scale_%s_vbf)' % (options.channel)
    systematics['syst_qcd_scale_up'] = ('' , '_'+options.syst_qcd_scale+'Up', weight_up, ['ZTT','ZL','ZJ','ZLL','VVT','VVJ','TTT','TTJ','QCD','W','jetFakes','qqH','WminusH','WplusH','ZH','EWKZ','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
    systematics['syst_qcd_scale_down'] = ('' , '_'+options.syst_qcd_scale+'Down', weight_down, ['ZTT','ZL','ZJ','ZLL','VVT','VVJ','TTT','TTJ','QCD','W','jetFakes','qqH','WminusH','WplusH','ZH','EWKZ','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
if options.syst_tau_id_dm0 != '':
    systematics['syst_tau_id_dm0_up'] = ('' , '_'+options.syst_tau_id_dm0+'Up', 'wt*wt_tau_id_dm0_up', ['ZL','ZJ','VVJ','TTJ','QCD','W'], False)
    systematics['syst_tau_id_dm0_down'] = ('' , '_'+options.syst_tau_id_dm0+'Down', 'wt*wt_tau_id_dm0_down', ['ZL','ZJ','VVJ','TTJ','QCD','W'], False)
if options.syst_tau_id_dm1 != '':
    systematics['syst_tau_id_dm1_up'] = ('' , '_'+options.syst_tau_id_dm1+'Up', 'wt*wt_tau_id_dm1_up', ['ZL','ZJ','VVJ','TTJ','QCD','W'], False)
    systematics['syst_tau_id_dm1_down'] = ('' , '_'+options.syst_tau_id_dm1+'Down', 'wt*wt_tau_id_dm1_down', ['ZL','ZJ','VVJ','TTJ','QCD','W'], False)
if options.syst_tau_id_dm10 != '':
    systematics['syst_tau_id_dm10_up'] = ('' , '_'+options.syst_tau_id_dm10+'Up', 'wt*wt_tau_id_dm10_up', ['ZL','ZJ','VVJ','TTJ','QCD','W'], False)
    systematics['syst_tau_id_dm10_down'] = ('' , '_'+options.syst_tau_id_dm10+'Down', 'wt*wt_tau_id_dm10_down', ['ZL','ZJ','VVJ','TTJ','QCD','W'], False)
if options.syst_lfake_dm0 != '':
    systematics['syst_lfake_dm0_up'] = ('' , '_'+options.syst_lfake_dm0+'Up', 'wt*wt_lfake_dm0_up', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
    systematics['syst_lfake_dm0_down'] = ('' , '_'+options.syst_lfake_dm0+'Down', 'wt*wt_lfake_dm0_down', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
if options.syst_lfake_dm1 != '':
    systematics['syst_lfake_dm1_up'] = ('' , '_'+options.syst_lfake_dm1+'Up', 'wt*wt_lfake_dm1_up', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
    systematics['syst_lfake_dm1_down'] = ('' , '_'+options.syst_lfake_dm1+'Down', 'wt*wt_lfake_dm1_down', ['VVT','VVJ','TTT','TTJ','QCD','W','signal','jetFakes','EmbedZTT'], False)
if options.syst_qcd_shape_wsf != '':
    systematics['syst_qcd_shape_wsf_up'] = ('' , '_'+options.syst_qcd_shape_wsf.replace('cat',options.cat)+'Up', 'wt', ['ZTT','ZL','ZJ','ZLL','VVT','VVJ','TTT','TTJ','jetFakes','signal','W','EWKZ','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
    systematics['syst_qcd_shape_wsf_down'] = ('' , '_'+options.syst_qcd_shape_wsf.replace('cat',options.cat)+'Down', 'wt', ['ZTT','ZL','ZJ','ZLL','VVT','VVJ','TTT','TTJ','jetFakes','signal','W','EWKZ','ggH_hww125','qqH_hww125','ggH_hww','qqH_hww','EmbedZTT'], False)
    if options.cat in ["0jet","boosted"]: w_abs_shift=0.1
    if options.cat in ["vbf",'dijet','dijet_lowM','dijet_highM','dijet_lowboost','dijet_boosted', 'dijet_lowMjj',
            'mva_JHU_ggh','mva_JHU_misc','mva_JHU_qcd','mva_JHU_qqh','mva_JHU_tt','mva_JHU_w','mva_JHU_zll','mva_JHU_ztt',
            'mva_powheg_ggh','mva_powheg_misc','mva_powheg_qcd','mva_powheg_qqh','mva_powheg_tt','mva_powheg_w','mva_powheg_zll','mva_powheg_ztt']:
        w_abs_shift=0.3
if options.syst_scale_met_unclustered != '':
    systematics['syst_scale_met_unclustered_up'] = ('METUNCL_UP' , '_'+options.syst_scale_met_unclustered+'Up', 'wt', ['QCD','jetFakes','EmbedZTT'], False)
    systematics['syst_scale_met_unclustered_down'] = ('METUNCL_DOWN' , '_'+options.syst_scale_met_unclustered+'Down', 'wt', ['QCD','jetFakes','EmbedZTT'], False)
if options.syst_scale_met_clustered != '':
    systematics['syst_scale_met_clustered_up'] = ('METCL_UP' , '_'+options.syst_scale_met_clustered+'Up', 'wt', ['QCD','jetFakes','EmbedZTT'], False)
    systematics['syst_scale_met_clustered_down'] = ('METCL_DOWN' , '_'+options.syst_scale_met_clustered+'Down', 'wt', ['QCD','jetFakes','EmbedZTT'], False)
if options.syst_scale_j_by_source != '':
    jes_sources={"AbsoluteFlavMap":1,"AbsoluteMPFBias":2,"AbsoluteScale":3,"AbsoluteStat":4,"FlavorQCD":5,"Fragmentation":6,"PileUpDataMC":7,"PileUpPtBB":8,"PileUpPtEC1":9,"PileUpPtEC2":10,"PileUpPtHF":11,"PileUpPtRef":12,"RelativeBal":13,"RelativeFSR":14,"RelativeJEREC1":15,"RelativeJEREC2":16,"RelativeJERHF":17,"RelativePtBB":18,"RelativePtEC1":19,"RelativePtEC2":20,"RelativePtHF":21,"RelativeStatEC":22,"RelativeStatFSR":23,"RelativeStatHF":24,"SinglePionECAL":25,"SinglePionHCAL":26,"TimePtEta":27}
    jes_to_process=[]
    for i in options.jes_sources.split(','):
      if ':' in i: jes_to_process+=range(int(i.split(':')[0]),int(i.split(':')[1])+1)
      else: jes_to_process.append(int(i))
    jes_to_process = list(set(jes_to_process))
    for source in jes_sources:
      jes_num = jes_sources[source]
      if jes_num not in jes_to_process: continue
      replace_dict = {'n_jets':'n_jets_%i'%jes_num, 'n_bjets':'n_bjets_%i'%jes_num, 'mjj':'mjj_%i'%jes_num, 'jdeta':'jdeta_%i'%jes_num, 'jdphi':'jdphi_%i'%jes_num, 'jpt_1':'jpt_1_%i'%jes_num, 'jpt_2':'jpt_2_%i'%jes_num}
      syst_name = 'syst_scale_j_by_source_'+source
      hist_name = options.syst_scale_j_by_source.replace('SOURCE', source)
      systematics[syst_name+'_up'] = ('JES_UP' , '_'+hist_name+'Up', 'wt', ['jetFakes','EmbedZTT'], False,replace_dict)
      systematics[syst_name+'_down'] = ('JES_DOWN' , '_'+hist_name+'Down', 'wt', ['jetFakes','EmbedZTT'], False,replace_dict)

if options.method in [17,18] and options.do_ff_systs and options.channel in ['et','mt','tt']:
    processes = ['tt','w','qcd']
    dms = ['dm0', 'dm1']
    njets = ['njet0','njet1']
    for process in processes:
      template_name = 'ff_'+process+'_syst'
      if process is 'qcd' or options.channel == 'tt': template_name = 'ff_'+process+'_'+options.channel+'_syst'
      weight_name = 'wt_ff_'+options.cat+'_'+process+'_syst_'
      systematics[template_name+'_up']   = ('' , '_'+template_name+'Up',   weight_name+'up',   ['ZTT','ZJ','ZL','VVT','VVJ','TTT','TTJ','QCD','W','signal','EmbedZTT'], True)
      systematics[template_name+'_down'] = ('' , '_'+template_name+'Down', weight_name+'down', ['ZTT','ZJ','ZL','VVT','VVJ','TTT','TTJ','QCD','W','signal','EmbedZTT'], True)
      if options.channel == 'tt' and process in ['w','tt']: continue
      for dm in dms:
        for njet in njets:
          template_name = 'ff_'+process+'_'+dm+'_'+njet
          if process != 'tt': template_name+='_'+options.channel
          template_name+='_stat'
          weight_name = 'wt_ff_'+options.cat+'_'+process+'_'+dm+'_'+njet+'_stat_'
          systematics[template_name+'_up']   = ('' , '_'+template_name+'Up',   weight_name+'up',   ['ZTT','ZJ','ZL','VVT','VVJ','TTT','TTJ','QCD','W','signal','EmbedZTT'], True)
          systematics[template_name+'_down'] = ('' , '_'+template_name+'Down', weight_name+'down', ['ZTT','ZJ','ZL','VVT','VVJ','TTT','TTJ','QCD','W','signal','EmbedZTT'], True)
    if options.channel == "tt":
      processes = ['dy', 'w', 'tt']
      for process in processes:
        template_name = 'ff_'+process+'_frac_tt_syst'
        weight_name = 'wt_ff_'+options.cat+'_'+process+'_frac_syst_'
        systematics[template_name+'_up']   = ('' , '_'+template_name+'Up',   weight_name+'up',   ['ZTT','ZJ','ZL','VVT','VVJ','TTT','TTJ','QCD','W','signal','EmbedZTT'], True)
        systematics[template_name+'_down'] = ('' , '_'+template_name+'Down', weight_name+'down', ['ZTT','ZJ','ZL','VVT','VVJ','TTT','TTJ','QCD','W','signal','EmbedZTT'], True)

# sort systematics by tree's input directory name
systematics = OrderedDict(sorted(systematics.items(), key=lambda key: key[1]))

if options.qcd_os_ss_ratio > 0:
    qcd_os_ss_ratio = options.qcd_os_ss_ratio
else:
    if options.analysis == 'sm':
      if options.channel == 'et':
          qcd_os_ss_ratio = 1.0
          if options.cat == '0jet': qcd_os_ss_ratio = 1.0
          elif options.cat == 'boosted': qcd_os_ss_ratio = 1.28
          elif options.cat in ['vbf','dijet','dijet_lowM','dijet_highM','dijet_lowboost','dijet_boosted', 'dijet_lowMjj',
                  'mva_JHU_ggh','mva_JHU_misc','mva_JHU_qcd','mva_JHU_qqh','mva_JHU_tt','mva_JHU_w','mva_JHU_zll','mva_JHU_ztt',
                  'mva_powheg_ggh','mva_powheg_misc','mva_powheg_qcd','mva_powheg_qqh','mva_powheg_tt','mva_powheg_w','mva_powheg_zll','mva_powheg_ztt']:
              qcd_os_ss_ratio = 1.0
      elif options.channel in ['mt','mj']:
          qcd_os_ss_ratio = 1.07
          if options.cat == '0jet': qcd_os_ss_ratio = 1.07
          elif options.cat == 'boosted': qcd_os_ss_ratio = 1.06
          elif options.cat in ['vbf','dijet','dijet_lowM','dijet_highM','dijet_lowboost','dijet_boosted', 'dijet_lowMjj',
                  'mva_JHU_ggh','mva_JHU_misc','mva_JHU_qcd','mva_JHU_qqh','mva_JHU_tt','mva_JHU_w','mva_JHU_zll','mva_JHU_ztt',
                  'mva_powheg_ggh','mva_powheg_misc','mva_powheg_qcd','mva_powheg_qqh','mva_powheg_tt','mva_powheg_w','mva_powheg_zll','mva_powheg_ztt']:
              qcd_os_ss_ratio = 1.0
      elif options.channel == 'zmm' or options.channel == 'zee':
          qcd_os_ss_ratio = 1.07
      else:
          qcd_os_ss_ratio = 1.0
    else:
      if options.channel == 'et':
          qcd_os_ss_ratio = 1.02
          if options.cat == 'inclusive': qcd_os_ss_ratio = 1.13
          elif options.cat in ['nobtag', 'nobtag_tight', 'nobtag_loosemt']: qcd_os_ss_ratio = 1.11
          elif options.cat in ['btag', 'btag_tight', 'btag_loosemt']: qcd_os_ss_ratio = 1.16
      elif options.channel in ['mt','mj']:
          qcd_os_ss_ratio = 1.18
          if options.cat == 'inclusive': qcd_os_ss_ratio = 1.12
          elif options.cat in ['nobtag', 'nobtag_tight', 'nobtag_loosemt']: qcd_os_ss_ratio = 1.14
          elif options.cat in ['btag', 'btag_tight', 'btag_loosemt']: qcd_os_ss_ratio = 1.01
      elif options.channel == 'zmm' or options.channel == 'zee':
          qcd_os_ss_ratio = 1.06
      else:
          qcd_os_ss_ratio = 1.0
#if options.do_ss:
#    qcd_os_ss_ratio = 1.0


# Get array of signal masses to process
ggh_masses=None
bbh_masses=None
sm_masses=None
if options.sm_masses != "": sm_masses = options.sm_masses.split(',')
if options.ggh_masses != "": ggh_masses = options.ggh_masses.split(',')
if options.bbh_masses != "": bbh_masses = options.bbh_masses.split(',')
if options.bbh_nlo_masses != "": bbh_nlo_masses = options.bbh_nlo_masses.split(',')

ROOT.TH1.SetDefaultSumw2(True)

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

def GetZTTNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    if get_os: OSSS = 'os'
    else: OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS, z_sels['ztt_sel'])
    return ana.SummedFactory('ZTT'+add_name, samples, plot, full_selection)
def GetEmbeddedNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    if get_os: OSSS = 'os'
    else: OSSS = '!os'
    if options.channel in ['et','mt']: wt_=wt+'*1.02'
    if options.channel == 'tt': wt_=wt+'*1.02*1.02'
    full_selection = BuildCutString(wt_, sel, cat, OSSS, z_sels['ztt_sel'])
    return ana.SummedFactory('EmbedZTT'+add_name, samples, plot, full_selection)

def GetZLLNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    if get_os: OSSS = 'os'
    else: OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS, z_sels['zll_sel'])
    return ana.SummedFactory('ZLL'+add_name, samples, plot, full_selection)

def GetZLNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    if get_os: OSSS = 'os'
    else: OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS, z_sels['zl_sel'])
    return ana.SummedFactory('ZL'+add_name, samples, plot, full_selection)

def GetZLEmbeddedNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    if get_os: OSSS = 'os'
    else: OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS, z_sels['zl_sel'])
    return ana.SummedFactory('EmbedZL'+add_name, samples, plot, full_selection)

def GetZJNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    if get_os: OSSS = 'os'
    else: OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS, z_sels['zj_sel'])
    return ana.SummedFactory('ZJ'+add_name, samples, plot, full_selection)

def GenerateZLL(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True, doZL=True, doZJ=True):
    if options.channel == 'em':
        zll_node = GetZLLNode(ana, add_name, samples, plot, wt, sel, cat, z_sels, get_os)
        ana.nodes[nodename].AddNode(zll_node)
    else:
        if doZL:
            zl_node = GetZLNode(ana, add_name, samples, plot, wt, sel, cat, z_sels, get_os)
            ana.nodes[nodename].AddNode(zl_node)
        if doZJ:
            zj_node = GetZJNode(ana, add_name, samples, plot, wt, sel, cat, z_sels, get_os)
            ana.nodes[nodename].AddNode(zj_node)

def GenerateZTT(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    ztt_node = GetZTTNode(ana, add_name, samples, plot, wt, sel, cat, z_sels, get_os)
    ana.nodes[nodename].AddNode(ztt_node)

def GenerateEmbedded(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    embed_node = GetEmbeddedNode(ana, add_name, samples, plot, wt, sel, cat, z_sels, get_os)
    ana.nodes[nodename].AddNode(embed_node)
def GenerateZLEmbedded(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    embed_node = GetZLEmbeddedNode(ana, add_name, samples, plot, wt, sel, cat, z_sels, get_os)
    ana.nodes[nodename].AddNode(embed_node)

def GetEWKZNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    if get_os: OSSS = 'os'
    else: OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS, '1')
    return ana.SummedFactory('EWKZ'+add_name, samples, plot, full_selection)

def GenerateEWKZ(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', z_sels={}, get_os=True):
    ewkz_node = GetEWKZNode(ana, add_name, samples, plot, wt, sel, cat, z_sels, get_os)
    ana.nodes[nodename].AddNode(ewkz_node)

def GetggHWWNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', get_os=True):
    if get_os: OSSS = 'os'
    else: OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS, '1')
    return ana.SummedFactory('ggH_hww125'+add_name, samples, plot, full_selection)

def GetqqHWWNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', get_os=True):
    if get_os: OSSS = 'os'
    else: OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS, '1')
    return ana.SummedFactory('qqH_hww125'+add_name, samples, plot, full_selection)

def GenerateHWW(ana, add_name='', ggh_samples=[], qqh_samples=[], plot='', wt='', sel='', cat='', get_os=True, doggH=True, doqqH=True):
  if doggH:
      gghww_node = GetggHWWNode(ana, add_name, ggh_samples, plot, wt, sel, cat, get_os)
      ana.nodes[nodename].AddNode(gghww_node)
  if doqqH:
      qqhww_node = GetqqHWWNode(ana, add_name, qqh_samples, plot, wt, sel, cat, get_os)
      ana.nodes[nodename].AddNode(qqhww_node)

def GetTTTNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', top_sels={}, get_os=True):
  if get_os: OSSS = 'os'
  else: OSSS = '!os'
  full_selection = BuildCutString(wt, sel, cat, OSSS, top_sels['ttt_sel'])
  return ana.SummedFactory('TTT'+add_name, samples, plot, full_selection)

def GetTTJNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', top_sels={}, get_os=True):
  if get_os: OSSS = 'os'
  else: OSSS = '!os'
  full_selection = BuildCutString(wt, sel, cat, OSSS, top_sels['ttj_sel'])
  return ana.SummedFactory('TTJ'+add_name, samples, plot, full_selection)

def GenerateTop(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', top_sels={}, get_os=True, doTTT=True, doTTJ=True):
  if doTTT:
      ttt_node = GetTTTNode(ana, add_name, samples, plot, wt, sel, cat, top_sels, get_os)
      ana.nodes[nodename].AddNode(ttt_node)
  if doTTJ:
      ttj_node = GetTTJNode(ana, add_name, samples, plot, wt, sel, cat, top_sels, get_os)
      ana.nodes[nodename].AddNode(ttj_node)

def GetVVTNode(ana, add_name ='', samples=[], plot='', wt='', sel='', cat='', vv_sels={}, get_os=True):
  if get_os: OSSS = 'os'
  else: OSSS = '!os'
  full_selection = BuildCutString(wt, sel, cat, OSSS, vv_sels['vvt_sel'])
  return ana.SummedFactory('VVT'+add_name, samples, plot, full_selection)

def GetVVJNode(ana, add_name ='', samples=[], plot='', wt='', sel='', cat='', vv_sels={}, get_os=True):
  if get_os: OSSS = 'os'
  else: OSSS = '!os'
  full_selection = BuildCutString(wt, sel, cat, OSSS, vv_sels['vvj_sel'])
  return ana.SummedFactory('VVJ'+add_name, samples, plot, full_selection)

def GenerateVV(ana, add_name ='', samples=[], plot='', wt='', sel='', cat='', vv_sels={}, get_os=True, doVVT=True, doVVJ=True):
  if doVVT:
      vvt_node = GetVVTNode(ana, add_name, samples, plot, wt, sel, cat, vv_sels, get_os)
      ana.nodes[nodename].AddNode(vvt_node)
  if doVVJ:
      vvj_node = GetVVJNode(ana, add_name, samples, plot, wt, sel, cat, vv_sels, get_os)
      ana.nodes[nodename].AddNode(vvj_node)

def GetWGNode(ana, add_name='', samples=[], plot='', wt='', sel='', cat='', get_os=True):
  if get_os:
      OSSS = 'os'
  else:
      OSSS = '!os'
  full_selection = BuildCutString(wt, sel, cat, OSSS)
  wg_node = ana.SummedFactory('WGam'+add_name, samples, plot, full_selection)
  return wg_node

def GetWNode(ana, name='W', samples=[], data=[], plot='',plot_unmodified='', wt='', sel='', cat='', cat_data='', method=8, qcd_factor=qcd_os_ss_ratio, get_os=True):
  if get_os: OSSS = 'os'
  else: OSSS = '!os'
  full_selection = BuildCutString(wt, sel, cat, OSSS, '')
  if cats['w_shape'] != '': shape_cat = cats['w_shape']
  else: shape_cat = cat
  if method == 14:
      shape_cat = '(n_jets<=1 && n_loose_bjets>=1)*('+cats['baseline']+')'
  shape_selection = BuildCutString(wt, sel, shape_cat, OSSS, '')

  if method in [8, 9, 15, 19, 20]:
      w_node = ana.SummedFactory(name, samples, plot, full_selection)
  elif method in [10, 11]:
      control_sel = cats['w_sdb']+' && '+ OSSS
      w_control_full_selection = BuildCutString(wt, control_sel, cat, OSSS)
      w_control_full_selection_data = BuildCutString(wt, control_sel, cat_data, OSSS)
      subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,wt,control_sel,cat,cat_data,method,qcd_os_ss_ratio,True,False)
      if shape_selection == full_selection:
          w_shape = None
      else:
          w_shape = ana.SummedFactory('w_shape', samples, plot, shape_selection)
      w_node = HttWNode(name,
        ana.SummedFactory('data_obs', data, plot_unmodified, w_control_full_selection_data),
        subtract_node,
        ana.SummedFactory('W_cr', samples, plot, w_control_full_selection),
        ana.SummedFactory('W_sr', samples, plot, full_selection),
        w_shape)
  elif method in [12, 13, 14, 16, 23]:
      if method == 16:
          cat_nobtag = '('+cats['btag_wnobtag']+')*('+cats['baseline']+')'
          cat_nobtag_data = '('+cats_unmodified['btag_wnobtag']+')*('+cats_unmodified['baseline']+')'
          full_selection = BuildCutString(wt, sel, cat_nobtag, OSSS)
          ss_selection = BuildCutString(wt, '', cat_nobtag, '!os', '')
          os_selection = BuildCutString(wt, '', cat_nobtag, 'os', '')
          control_sel = cats['w_sdb']
          w_control_full_selection = BuildCutString(wt, control_sel, cat_nobtag, OSSS)
          w_control_full_selection_os = BuildCutString(wt, control_sel, cat_nobtag)
          w_control_full_selection_ss = BuildCutString(wt, control_sel, cat_nobtag, '!os')
          w_control_full_selection_os_data = BuildCutString(wt, control_sel, cat_nobtag_data)
          w_control_full_selection_ss_data = BuildCutString(wt, control_sel, cat_nobtag_data, '!os')
          btag_extrap_sel_num = BuildCutString(wt, sel, cat, OSSS, '')
          btag_extrap_sel_den = BuildCutString(wt, sel, cat_nobtag, OSSS, '')
          btag_extrap_num_node = ana.SummedFactory('btag', samples, plot, btag_extrap_sel_num)
          btag_extrap_den_node = ana.SummedFactory('no_btag', samples, plot, btag_extrap_sel_den)
          subtract_node_os = GetSubtractNode(ana,'_os',plot,plot_unmodified,wt,control_sel,cat_nobtag,cat_nobtag_data,method,qcd_os_ss_ratio,True,False)
          subtract_node_ss = GetSubtractNode(ana,'_ss',plot,plot_unmodified,wt,control_sel,cat_nobtag,cat_nobtag_data,method,qcd_os_ss_ratio,False,False)
      elif method == 23:
          cat_nopt = '('+cats['dijet']+')*('+cats['baseline']+')'
          cat_nopt_data = '('+cats_unmodified['dijet']+')*('+cats_unmodified['baseline']+')'
          full_selection = BuildCutString(wt, sel, cat_nopt, OSSS)
          ss_selection = BuildCutString(wt, '', cat_nopt, '!os', '')
          os_selection = BuildCutString(wt, '', cat_nopt, 'os', '')
          control_sel = cats['w_sdb']
          w_control_full_selection = BuildCutString(wt, control_sel, cat_nopt, OSSS)
          w_control_full_selection_os = BuildCutString(wt, control_sel, cat_nopt)
          w_control_full_selection_ss = BuildCutString(wt, control_sel, cat_nopt, '!os')
          w_control_full_selection_os_data = BuildCutString(wt, control_sel, cat_nopt_data)
          w_control_full_selection_ss_data = BuildCutString(wt, control_sel, cat_nopt_data, '!os')
          btag_extrap_sel_num = BuildCutString(wt, sel, cat, OSSS, '')
          btag_extrap_sel_den = BuildCutString(wt, sel, cat_nopt, OSSS, '')
          btag_extrap_num_node = ana.SummedFactory('btag', samples, plot, btag_extrap_sel_num)
          btag_extrap_den_node = ana.SummedFactory('no_btag', samples, plot, btag_extrap_sel_den)
          subtract_node_os = GetSubtractNode(ana,'_os',plot,plot_unmodified,wt,control_sel,cat_nopt,cat_nopt_data,method,qcd_os_ss_ratio,True,False)
          subtract_node_ss = GetSubtractNode(ana,'_ss',plot,plot_unmodified,wt,control_sel,cat_nopt,cat_nopt_data,method,qcd_os_ss_ratio,False,False)
      else:
          full_selection = BuildCutString(wt, sel, cat, OSSS)
          ss_selection = BuildCutString(wt, '', cat, '!os', '')
          os_selection = BuildCutString(wt, '', cat, 'os', '')
          control_sel = cats['w_sdb']
          w_control_full_selection = BuildCutString(wt, control_sel, cat, OSSS)
          w_control_full_selection_os = BuildCutString(wt, control_sel, cat)
          w_control_full_selection_ss = BuildCutString(wt, control_sel, cat, '!os')
          w_control_full_selection_os_data = BuildCutString(wt, control_sel, cat_data)
          w_control_full_selection_ss_data = BuildCutString(wt, control_sel, cat_data, '!os')
          btag_extrap_num_node = None
          btag_extrap_den_node = None
          subtract_node_os = GetSubtractNode(ana,'_os',plot,plot_unmodified,wt,control_sel,cat,cat_data,method,qcd_os_ss_ratio,True,False)
          subtract_node_ss = GetSubtractNode(ana,'_ss',plot,plot_unmodified,wt,control_sel,cat,cat_data,method,qcd_os_ss_ratio,False,False)

      if shape_selection == full_selection:
          w_shape = None
      else:
          w_shape = ana.SummedFactory('w_shape', samples, plot, shape_selection)
      w_node = HttWOSSSNode(name,
        ana.SummedFactory('data_os', data, plot_unmodified, w_control_full_selection_os_data),
        subtract_node_os,
        ana.SummedFactory('data_ss', data, plot_unmodified, w_control_full_selection_ss_data),
        subtract_node_ss,
        ana.SummedFactory('W_cr', samples, plot, w_control_full_selection),
        ana.SummedFactory('W_sr', samples, plot, full_selection),
        ana.SummedFactory('W_os', samples, plot, os_selection),
        ana.SummedFactory('W_ss', samples, plot, ss_selection),
        w_shape,
        qcd_factor,
        get_os,
        btag_extrap_num_node,
        btag_extrap_den_node)

  elif method in [21,22,24,25]:
    control_sel = cats['w_sdb']+' && '+ OSSS
    w_control_full_selection = BuildCutString(wt, control_sel, cat, OSSS)
    w_control_full_selection_data = BuildCutString(wt, control_sel, cat_data, OSSS)
    data_node=ana.SummedFactory('data_obs', data, plot_unmodified, w_control_full_selection_data)
    subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,wt,control_sel,cat,cat_data,method,qcd_os_ss_ratio,True,False)

    qcd_subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,wt,cats['w_sdb'],cat,cat_data,8,qcd_os_ss_ratio,False,True)
    qcd_control_full_selection = BuildCutString(wt, cats['w_sdb'], cat, '!os')
    qcd_control_full_selection_data = BuildCutString(wt, cats['w_sdb'], cat_data, '!os')
    qcd_node = HttQCDNode('QCD'+add_name,
      ana.SummedFactory('data_ss', data, plot_unmodified, qcd_control_full_selection_data),
      qcd_subtract_node,
      qcd_factor,
      None)

    subtract_node.AddNode(qcd_node)

    if shape_selection == full_selection: w_shape = None
    else: w_shape = ana.SummedFactory('w_shape', samples, plot, shape_selection)

    if method in [22]:
      data_node = None
      wsf_num = GetWNode(ana, name, samples, data, plot,plot_unmodified, wt, sel, cat, cat_data, 21, qcd_factor, True)
      wsf_denum = GetWNode(ana, name, samples, data, plot,plot_unmodified, wt, sel, cat, cat_data, 8, qcd_factor, True)
    if method in [24]:
      data_node = None
      cat_nopt = '('+cats['dijet']+')*('+cats['baseline']+')'
      cat_nopt_data = '('+cats_unmodified['dijet']+')*('+cats_unmodified['baseline']+')'
      wsf_num = GetWNode(ana, name, samples, data, plot,plot_unmodified, wt, sel, cat, cat_data, 8, qcd_factor, True)
      wsf_denum = GetWNode(ana, name, samples, data, plot,plot_unmodified, wt, sel, cat_nopt, cat_nopt_data, 8, qcd_factor, True)
    if method in [25]:
      data_node = None
      wsf_num = GetWNode(ana, name, samples, data, plot,plot_unmodified, wt, sel, cat, cat_data, 24, qcd_factor, True)
      wsf_denum = GetWNode(ana, name, samples, data, plot,plot_unmodified, wt, sel, cat, cat_data, 8, qcd_factor, True)
    else:
      wsf_num = None
      wsf_denum = None

    w_node = HttWNode(name,
      data_node,
      subtract_node,
      ana.SummedFactory('W_cr', samples, plot, w_control_full_selection),
      ana.SummedFactory('W_sr', samples, plot, full_selection),
      w_shape,
      wsf_num,
      wsf_denum)
  return w_node

def GenerateW(ana, add_name='', samples=[], data=[], wg_samples=[], plot='', plot_unmodified='', wt='', sel='', cat='', cat_data='', method=8, qcd_factor=qcd_os_ss_ratio, get_os=True):
  w_node_name = 'W'
  if options.channel == 'em':
      w_total_node = SummedNode('W'+add_name)
      w_total_node.AddNode(GetWGNode(ana, add_name, wg_samples, plot, wt, sel, cat))
      ana.nodes[nodename].AddNode(GetWGNode(ana, add_name, wg_samples, plot, wt, sel, cat))
      w_node_name+='J'
  ana.nodes[nodename].AddNode(GetWNode(ana, w_node_name+add_name, samples, data, plot, plot_unmodified, wt, sel, cat, cat_data, method, qcd_factor, get_os))
  if options.channel == 'em':
      w_total_node.AddNode(GetWNode(ana, w_node_name+add_name, samples, data, plot, plot_unmodified, wt, sel, cat, cat_data, method, qcd_factor, get_os))
      ana.nodes[nodename].AddNode(w_total_node)

def GetSubtractNode(ana,add_name,plot,plot_unmodified,wt,sel,cat,cat_data,method,qcd_os_ss_ratio,OSSS,includeW=False,w_shift=None):
  subtract_node = SummedNode('total_bkg'+add_name)
  if includeW:
      if w_shift is not None: w_wt = '%s*%f' %(wt,w_shift)
      else: w_wt = wt
      w_node = GetWNode(ana, 'W', wjets_samples, data_samples, plot, plot_unmodified, w_wt, sel, cat, cat_data,method, qcd_os_ss_ratio, OSSS)
      subtract_node.AddNode(w_node)
  ttt_node = GetTTTNode(ana, "", top_samples, plot, wt, sel, cat, top_sels, OSSS)
  ttj_node = GetTTJNode(ana, "", top_samples, plot, wt, sel, cat, top_sels, OSSS)
  vvt_node = GetVVTNode(ana, "", vv_samples, plot, wt, sel, cat, vv_sels, OSSS)
  vvj_node = GetVVJNode(ana, "", vv_samples, plot, wt, sel, cat, vv_sels, OSSS)
  subtract_node.AddNode(ttt_node)
  subtract_node.AddNode(ttj_node)
  subtract_node.AddNode(vvt_node)
  subtract_node.AddNode(vvj_node)
  if options.embedding and options.channel != 'zmm':
    embed_node = GetEmbeddedNode(ana, "", embed_samples, plot, wt, sel, cat, z_sels, OSSS)
    subtract_node.AddNode(embed_node)
  else:
    ztt_node = GetZTTNode(ana, "", ztt_samples, plot, wt, sel, cat, z_sels, OSSS)
    subtract_node.AddNode(ztt_node)
  if options.era in ['smsummer16','cpsummer16','tauid2016']:
    ewkz_node = GetEWKZNode(ana, "", ewkz_samples, plot, wt, sel, cat, z_sels, OSSS)
    subtract_node.AddNode(ewkz_node)
  if options.channel not in ["em"]:
      zl_node = GetZLNode(ana, "", ztt_samples, plot, wt, sel, cat, z_sels, OSSS)
      zj_node = GetZJNode(ana, "", ztt_samples, plot, wt, sel, cat, z_sels, OSSS)
      subtract_node.AddNode(zl_node)
      subtract_node.AddNode(zj_node)
  if options.channel in ["em"]:
      zll_node = GetZLLNode(ana, "", ztt_samples, plot, wt, sel, cat, z_sels, OSSS)
      subtract_node.AddNode(zll_node)
  if options.channel == "em":
      wg_node = GetWGNode(ana, "", wgam_samples, plot, wt, sel, cat, OSSS)
      subtract_node.AddNode(wg_node)
  return subtract_node

def GenerateQCD(ana, add_name='', data=[], plot='', plot_unmodified='', wt='', sel='', cat='', cat_data='', method=8, qcd_factor=qcd_os_ss_ratio, get_os=True,w_shift=None):
    shape_node = None
    OSSS = "!os"
    if get_os: OSSS = "os"
    if options.channel != 'tt':

        if method in [9, 11, 13, 14]:
            if method in [9, 11, 13]:
              shape_cat = '('+cats[options.cat]+')*('+cats['qcd_loose_shape']+')'
              shape_cat_data = '('+cats_unmodified[options.cat]+')*('+cats_unmodified['qcd_loose_shape']+')'
            elif method == 14:
                shape_cat = '(n_jets<=1 && n_loose_bjets>=1)*('+cats['baseline']+')'
                shape_cat_data = '(n_jets<=1 && n_loose_bjets>=1)*('+cats_unmodified['baseline']+')'
            shape_selection = BuildCutString(wt, sel, shape_cat_data, '!os')
            subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,wt,sel,shape_cat,shape_cat_data,method,qcd_os_ss_ratio,False,True)
            shape_node = SubtractNode('shape', ana.SummedFactory('data_ss', data, plot_unmodified, shape_selection), subtract_node)

        #if options.channel == 'em': qcd_os_ss_factor = 1
        qcd_os_ss_factor = qcd_factor
        weight = wt
        if method in [15,19]:
            #qcd_os_ss_factor = 1
            if get_os and options.channel == "em":
                weight = wt+'*wt_em_qcd'
            if method == 19:
                shape_selection = BuildCutString(weight, sel, cats_unmodified['em_shape_cat'], '!os')
                subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,weight,sel,cats['em_shape_cat'],cats_unmodified['em_shape_cat'],method,1,False,True)
                shape_node = SubtractNode('shape', ana.SummedFactory('data_ss',data, plot_unmodified, shape_selection), subtract_node)

        if cats['qcd_shape'] != "" or w_shift is not None:
            add_shape = False
            if cats['qcd_shape'] == '': shape_cat = cat
            else:
              shape_cat = cats['qcd_shape']
              add_shape = True
            if cats['qcd_shape'] == '': shape_cat_data = cat_data
            else:
              shape_cat_data = cats_unmodified['qcd_shape']
              add_shape = True
            if add_shape:
              shape_selection = BuildCutString(weight, sel, shape_cat_data, '!os')
              if method == 21: subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,weight,sel,shape_cat,shape_cat_data,22,1,False,True,w_shift)
              else: subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,weight,sel,shape_cat,shape_cat_data,method,1,False,True,w_shift)
              shape_node = SubtractNode('shape', ana.SummedFactory('data_ss',data, plot_unmodified, shape_selection), subtract_node)
            else: shape_node = None

        full_selection = BuildCutString(weight, sel, cat_data, '!os')
        if method == 21:
          subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,weight,sel,cat,cat_data,22,qcd_os_ss_ratio,False,True)
        elif method == 24:
          subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,weight,sel,cat,cat_data,25,qcd_os_ss_ratio,False,True)
        else: subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,weight,sel,cat,cat_data,method,qcd_os_ss_ratio,False,True)
        if get_os: qcd_ratio = qcd_os_ss_factor
        else: qcd_ratio = 1.0
        ana.nodes[nodename].AddNode(HttQCDNode('QCD'+add_name,
          ana.SummedFactory('data_ss', data, plot_unmodified, full_selection),
          subtract_node,
          qcd_ratio,
          shape_node))

    else:
        qcd_sdb_cat = cats[options.cat]+' && '+cats['tt_qcd_norm']
        qcd_sdb_cat_data = cats_unmodified[options.cat]+' && '+cats_unmodified['tt_qcd_norm']

        subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,wt,sel,cat,cat_data,method,qcd_os_ss_ratio,False,True)
        num_selection = BuildCutString(wt, sel, cat_data, '!os')
        num_node = SubtractNode('ratio_num',
                     ana.SummedFactory('data', data, plot_unmodified, num_selection),
                     subtract_node)
        if options.analysis == 'mssmsummer16': tau_id_wt = 'wt_tau2_id_loose'
        else: tau_id_wt = '1'
        subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,wt+'*'+tau_id_wt,sel,qcd_sdb_cat,qcd_sdb_cat_data,method,qcd_os_ss_ratio,False,True)
        den_selection = BuildCutString(wt, sel, qcd_sdb_cat_data, '!os')
        den_node = SubtractNode('ratio_den',
                     ana.SummedFactory('data', data, plot_unmodified, den_selection),
                     subtract_node)
        shape_node = None
        full_selection = BuildCutString(wt, sel, qcd_sdb_cat_data, OSSS)
        subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,wt+'*'+tau_id_wt,sel,qcd_sdb_cat,qcd_sdb_cat_data,method,qcd_os_ss_ratio,get_os,True)

        if options.method == 20:
            num_node = None
            den_node = None
            subtract_node = GetSubtractNode(ana,'',plot,plot_unmodified,wt+'*wt_tt_qcd_nobtag',sel,cat,cat_data,method,qcd_os_ss_ratio,False,True)
            full_selection = BuildCutString(wt+'*wt_tt_qcd_nobtag', sel, qcd_sdb_cat_data, OSSS)

        ana.nodes[nodename].AddNode(HttQCDNode('QCD'+add_name,
          ana.SummedFactory('data', data, plot_unmodified, full_selection),
          subtract_node,
          1,
          shape_node,
          num_node,
          den_node))


def GenerateFakeTaus(ana, add_name='', data=[], plot='',plot_unmodified='', wt='', sel='', cat_name='',get_os=True,ff_syst_weight=None):
    print "Generating fake tau background via fake-factor method. In order for this to work you must first ensure that the fake-factor weights are included in the input tree for the channel and category you wish use. Weights should be named as: wt_ff_channel_category"

    if get_os:
        OSSS = 'os'
    else:
        OSSS = '!os'

    # Select data from anti-isolated region
    if options.channel != "tt":
        if options.channel == 'mt':
            anti_isolated_sel = '(iso_1<0.15 && mva_olddm_tight_2<0.5 && mva_olddm_vloose_2>0.5 && antiele_2 && antimu_2 && !leptonveto)'
            if options.era == "mssmsummer16": anti_isolated_sel +=" && trg_singlemuon"
        elif options.channel == 'et':
            anti_isolated_sel = '(iso_1<0.1  && mva_olddm_tight_2<0.5 && mva_olddm_vloose_2>0.5 && antiele_2 && antimu_2 && !leptonveto)'
            if options.era == "mssmsummer16": anti_isolated_sel +=" && trg_singleelectron"
        ff_cat = cats[cat_name] +" && "+ anti_isolated_sel
        ff_cat_data = cats_unmodified[cat_name] +" && "+ anti_isolated_sel
        if ff_syst_weight is not None: fake_factor_wt_string = ff_syst_weight
        else: fake_factor_wt_string = "wt_ff_"+options.cat
        fake_factor_wt_string+='*wt_tau_id_loose'
        if wt is not "": wt+="*"+fake_factor_wt_string
        else: wt=fake_factor_wt_string

        full_selection = BuildCutString(wt, sel, ff_cat_data, OSSS, '')
        # Calculate FF for anti-isolated data (f1) then subtract contributions from real taus (f2)
        f1 = ana.SummedFactory('data', data, plot_unmodified, full_selection)
        f2 = GetSubtractNode(ana,'',plot,plot_unmodified,wt,sel+'*(gen_match_2<6)',ff_cat,ff_cat_data,8,1.0,True,True)
        ana.nodes[nodename].AddNode(SubtractNode('jetFakes'+add_name, f1, f2))

    if options.channel == 'tt':
        anti_isolated_sel_1 = '(mva_olddm_medium_1<0.5 && mva_olddm_vloose_1>0.5 && mva_olddm_medium_2>0.5 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto)'
        anti_isolated_sel_2 = '(mva_olddm_medium_2<0.5 && mva_olddm_vloose_2>0.5 && mva_olddm_medium_1>0.5 && antiele_1 && antimu_1 && antiele_2 && antimu_2 && !leptonveto)'
        if options.era == "mssmsummer16":
          anti_isolated_sel_1 +=" && trg_doubletau"
          anti_isolated_sel_2 +=" && trg_doubletau"

        ff_cat_1 = cats[cat_name] +" && "+ anti_isolated_sel_1
        ff_cat_2 = cats[cat_name] +" && "+ anti_isolated_sel_2
        ff_cat_1_data = cats_unmodified[cat_name] +" && "+ anti_isolated_sel_1
        ff_cat_2_data = cats_unmodified[cat_name] +" && "+ anti_isolated_sel_2
        if ff_syst_weight is not None:
            fake_factor_wt_string_1 = ff_syst_weight+'_1'
            fake_factor_wt_string_2 = ff_syst_weight+'_2'
        else:
          fake_factor_wt_string_1 = "wt_ff_"+options.cat+"_1"
          fake_factor_wt_string_2 = "wt_ff_"+options.cat+"_2"
        if wt is not "":
            wt_1=wt+"*"+fake_factor_wt_string_1
            wt_2=wt+"*"+fake_factor_wt_string_2
        else:
            wt_1=fake_factor_wt_string_1
            wt_2=fake_factor_wt_string_2

        full_selection_1 = BuildCutString(wt_1, sel, ff_cat_1_data, OSSS, '')
        full_selection_2 = BuildCutString(wt_2, sel, ff_cat_2_data, OSSS, '')

        ff_total_node = SummedNode('jetFakes'+add_name)
        f1_total_node = SummedNode('data')
        f1_total_node.AddNode(ana.SummedFactory('data_1', data, plot_unmodified, full_selection_1))
        f1_total_node.AddNode(ana.SummedFactory('data_2', data, plot_unmodified, full_selection_2))
        f2_total_node = SummedNode('total_bkg')
        f2_total_node.AddNode(GetSubtractNode(ana,'_1',plot,plot_unmodified,wt_1+'*wt_tau1_id_loose',sel+'*(gen_match_1<6)',ff_cat_1,ff_cat_1_data,8,1.0,True,True))
        f2_total_node.AddNode(GetSubtractNode(ana,'_2',plot,plot_unmodified,wt_2+'*wt_tau2_id_loose',sel+'*(gen_match_2<6)',ff_cat_2,ff_cat_2_data,8,1.0,True,True))
        ana.nodes[nodename].AddNode(SubtractNode('jetFakes'+add_name, f1_total_node, f2_total_node))

def GenerateSMSignal(ana, add_name='', plot='', masses=['125'], wt='', sel='', cat='', get_os=True, sm_bkg = '',processes=['ggH','qqH','ZH','WminusH','WplusH']):
    if get_os:
        OSSS = 'os'
    else:
        OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS)
    if masses is not None:
        for mass in masses:
            if sm_bkg != '':
                add_str = '_SM'+sm_bkg
            else:
                add_str = mass
            for key in sm_samples:
                if True not in [proc in key for proc in processes]: continue
                sample_name = sm_samples[key].replace('*',mass)
                ana.nodes[nodename].AddNode(ana.BasicFactory(key+add_str+add_name, sample_name, plot, full_selection))

def GenerateMSSMSignal(ana, add_name='', bbh_add_name='', plot='', ggh_masses = ['1000'], bbh_masses = ['1000'], wt='', sel='', cat='', get_os=True, do_ggH=True, do_bbH=True):
    if get_os:
        OSSS = 'os'
    else:
        OSSS = '!os'
    if options.gen_signal: OSSS='1'
    full_selection = BuildCutString(wt, sel, cat, OSSS)
    for key in mssm_samples:
        masses = None
        if key == 'ggH':
            masses = ggh_masses
        elif key == 'bbH':
            masses = bbh_masses
        if masses is not None:
            for mass in masses:
                if key == 'ggH' and not do_ggH:
                    continue
                if key == 'bbH' and not do_bbH:
                    continue
                sample_name = mssm_samples[key].replace('*',mass)
                add_name_2 = ''
                if bbh_add_name == '-LO' and key is 'bbH':
                    sample_name = mssm_lo_samples['bbH-LO'].replace('*',mass)
                    add_name_2 = bbh_add_name
                ana.nodes[nodename].AddNode(ana.BasicFactory(key+add_name_2+mass+add_name, sample_name, plot, full_selection))

def GenerateReWeightedMSSMSignal(ana, add_name='', plot='', ggh_masses = ['1000'], wt='', sel='', cat='', get_os=True):
  weights = {'ggh_t':'wt_ggh_t', 'ggh_b':'wt_ggh_b', 'ggh_i':'wt_ggh_i', 'ggH_t':'wt_ggH_t', 'ggH_b':'wt_ggH_b', 'ggH_i':'wt_ggH_i', 'ggA_t':'wt_ggA_t', 'ggA_b':'wt_ggA_b', 'ggA_i':'wt_ggA_i' }
  if get_os: OSSS = 'os'
  else: OSSS = '!os'
  if options.gen_signal: OSSS='1'
  for mass in ggh_masses:
    for name in weights:
      weight=wt+"*"+weights[name]
      full_selection = BuildCutString(weight, sel, cat, OSSS)
      sample_name = mssm_samples['ggH'].replace('*',mass)
      add_name_2 = ''
      ana.nodes[nodename].AddNode(ana.BasicFactory(name+mass+add_name, sample_name, plot, full_selection))

def GenerateNLOMSSMSignal(ana, add_name='', plot='', ggh_nlo_masses = ['1000'], bbh_nlo_masses = ['1000'],wt='wt', sel='', cat='', doScales=True, doPDF=False, get_os=True,do_ggH=True, do_bbH=True):
    if get_os:
        OSSS = 'os'
    else:
        OSSS = '!os'
    if options.gen_signal: OSSS='1'
    weights = {'':'1'}
    wt_noscale = wt
    if doScales: weights = {'':'1','muR1muF2':'wt_mur1_muf2','muR1muF0.5':'wt_mur1_muf0p5','muR2muF1':'wt_mur2_muf1','muR2muF2':'wt_mur2_muf2','muR0.5muF1':'wt_mur0p5_muf1','muR0.5muF0.5':'wt_mur0p5_muf0p5'}
    if doPDF:
      for i in range(1,101): weights['PDF_'+str(i)] = 'wt_pdf_'+str(i)
      weights['AlphaS_Up'] = 'wt_alphasup'
      weights['AlphaS_Down'] = 'wt_alphasdown'
    for weight in weights:
      wt = weights[weight]+'*'+wt_noscale
      full_selection = BuildCutString(wt, sel, cat, OSSS)
      for key in mssm_nlo_samples:
          if 'Qsh' in key and weight is not '': continue
          if 'ggH' in key:
              masses = ggh_nlo_masses
          elif 'bbH' in key:
              masses = bbh_nlo_masses
          if masses is not None:
              for mass in masses:
                  if key == 'ggH' and not do_ggH:
                      continue
                  if key == 'bbH' and not do_bbH:
                      continue
                  sample_name = mssm_nlo_samples[key].replace('*',mass)
                  ana.nodes[nodename].AddNode(ana.BasicFactory(key+mass+add_name+weight, sample_name, plot, full_selection))


def GenerateHhhSignal(ana, add_name='', plot='', masses = ['700'], wt='', sel='', cat='', get_os=True):
    if get_os:
        OSSS = 'os'
    else:
        OSSS = '!os'
    full_selection = BuildCutString(wt, sel, cat, OSSS)
    if masses is not None:
        for mass in masses:
            for key in Hhh_samples:
                sample_name = Hhh_samples[key].replace('*',mass)
                ana.nodes[nodename].AddNode(ana.BasicFactory(key+mass+add_name, sample_name, plot, full_selection))

def PrintSummary(nodename='', data_strings=['data_obs'], add_names=''):
    print ''
    print '################### Summary ###################'
    nodes = ana.nodes[nodename].SubNodes()
    bkg_total = ufloat(0.000000001,0.000000001)
    sig_total = ufloat(0.000000001,0.000000001)
    for node in nodes:
        if options.method == 18 and 'jetFakes' == node.name: continue
        if node.shape.rate.n == 0: per_err = 0
        else: per_err = node.shape.rate.s/node.shape.rate.n
        print node.name.ljust(10) , ("%.2f" % node.shape.rate.n).ljust(10), '+/-'.ljust(5), ("%.2f" % node.shape.rate.s).ljust(7), "(%.4f)" % per_err
        if True in [node.name.find(add_name) != -1 and add_name is not '' for add_name in add_names]: continue
        if True in [node.name.find(sig) != -1 for sig in signal_samples.keys()] and node.name.find("_SM"+options.add_sm_background) ==-1:
            sig_total += node.shape.rate
        elif node.name not in data_strings:
            bkg_total += node.shape.rate
    if bkg_total.n == 0: per_err = 0
    else: per_err = bkg_total.s/bkg_total.n
    print 'Total bkg'.ljust(10) , ("%.2f" % bkg_total.n).ljust(10), '+/-'.ljust(5), ("%.2f" % bkg_total.s).ljust(7), "(%.4f)" % per_err
    if sig_total.n == 0: per_err = 0
    else: per_err = sig_total.s/sig_total.n
    print 'Total sig'.ljust(10) , ("%.2f" % sig_total.n).ljust(10), '+/-'.ljust(5), ("%.2f" % sig_total.s).ljust(7), "(%.4f)" % per_err
    print '###############################################'
    print ''


def FixBins(ana,outfile='output.root'):
    #Fix empty histograms
    nodes = ana.nodes[nodename].SubNodes()
    for node in nodes:
        if 'data_obs' in node.name: continue
        hist = outfile.Get(nodename+'/'+node.name)
        outfile.cd(nodename)
        #Fix empty histogram
        if hist.Integral() == 0.0:
            hist.SetBinContent(hist.GetNbinsX()/2, 0.00001)
            hist.SetBinError(hist.GetNbinsX()/2, 0.00001)
            hist.Write()
        outfile.cd()


def NormFFSysts(ana,outfile='output.root'):
    nominal_hist = outfile.Get(nodename+'/jetFakes')
    if isinstance(nominal_hist,ROOT.TH2): nominal_scale = nominal_hist.Integral(-1,-1,-1,-1)
    else: nominal_scale = nominal_hist.Integral(0,nominal_hist.GetNbinsX()+1)
    directory = outfile.Get(nodename)
    outfile.cd(nodename)
    hists_to_add=[]
    for key in directory.GetListOfKeys():
        hist_name = key.GetName()
        hist = directory.Get(hist_name).Clone()
        if not isinstance(hist,ROOT.TDirectory):
           if 'jetFakes' not in hist_name: continue
           if hist_name == 'jetFakes': continue
           if isinstance(hist,ROOT.TH2): norm = nominal_scale/hist.Integral(-1,-1,-1,-1)
           else: norm = nominal_scale/hist.Integral(0,hist.GetNbinsX()+1)
           hist.Scale(norm)
           norm_hist_name = hist_name
           norm_hist_name = norm_hist_name.replace('jetFakes','jetFakes_norm')
           hist.SetName(norm_hist_name)
           hists_to_add.append(hist)
    for hist in hists_to_add: hist.Write()

def NormWFakeSysts(ana,outfile='output.root'):
    nominal_hist = outfile.Get(nodename+'/W')
    if isinstance(nominal_hist,ROOT.TH2): nominal_scale = nominal_hist.Integral(-1,-1,-1,-1)
    else: nominal_scale = nominal_hist.Integral(-1,-1)
    directory = outfile.Get(nodename)
    outfile.cd(nodename)
    hists_to_add=[]
    for key in directory.GetListOfKeys():
        hist_name = key.GetName()
        hist = directory.Get(hist_name)
        if not isinstance(hist,ROOT.TDirectory):
           if 'W' not in hist_name or options.syst_w_fake_rate not in hist_name or 'Wplus' in hist_name or 'Wminus' in hist_name or 'WH' in hist_name: continue
           if isinstance(hist,ROOT.TH2): norm = nominal_scale/hist.Integral(-1,-1,-1,-1)
           else: norm = nominal_scale/hist.Integral(-1,-1)
           hist.Scale(norm)
           hists_to_add.append(hist)
    for hist in hists_to_add: hist.Write("",ROOT.TObject.kOverwrite)

def NormEmbedToMC(ana,outfile='output.root'):
    nominal_hist = outfile.Get(nodename+'/ZTT')
    nominal_hist_embed = outfile.Get(nodename+'/EmbedZTT')
    if isinstance(nominal_hist,ROOT.TH2): scale = nominal_hist.Integral(-1,-1,-1,-1)/nominal_hist_embed.Integral(-1,-1,-1,-1)
    else: scale = nominal_hist.Integral(-1,-1)/nominal_hist_embed.Integral(-1,-1)
    directory = outfile.Get(nodename)
    outfile.cd(nodename)
    hists_to_add=[]
    for key in directory.GetListOfKeys():
        hist_name = key.GetName()
        hist = directory.Get(hist_name)
        if not isinstance(hist,ROOT.TDirectory):
           if 'EmbedZTT' not in hist_name: continue
           hist.Scale(scale)
           hists_to_add.append(hist)
    for hist in hists_to_add: hist.Write("",ROOT.TObject.kOverwrite)


def TTBarEmbeddingSyst(ana,outfile,template_name):
    nominal_hist = outfile.Get(nodename+'/EmbedZTT')
    shift_hist = outfile.Get(nodename+'/TTT_embed_syst')
    shift_hist.Scale(0.1)
    up_hist = nominal_hist.Clone()
    down_hist = nominal_hist.Clone()
    up_hist.Add(shift_hist)
    down_hist.Add(shift_hist,-1)
    up_hist.SetName('EmbedZTT_'+template_name+'Up')
    down_hist.SetName('EmbedZTT_'+template_name+'Down')
    outfile.cd(nodename)
    up_hist.Write()
    down_hist.Write()

def OverwriteNames(input_string,replace_dict={}):
    for i in replace_dict:
      input_string=input_string.replace(i,replace_dict[i])
    return input_string

def PDFUncerts(nodename, infile):
  def RMS(a):
    from numpy import mean, sqrt, square
    rms = sqrt(mean(square(a-mean(a))))
    return rms
  outstring1=''
  outstring2=''

  for mass in bbh_nlo_masses:
    nominal_error=ROOT.Double()
    nominal = outfile.Get(nodename+'/bbH'+mass).IntegralAndError(-1, -1,nominal_error)
    sample_name='SUSYGluGluToBBHToTauTau_M-'+mass+'-NLO'
    evt_nom = ana.info[sample_name]['evt']
    pdf_variations_nosf=[]
    pdf_variations=[]
    pdf_variations_nosf.append(nominal)
    pdf_variations.append(nominal)
    for i in range(1,101):
      wt = 'wt_pdf_'+str(i)
      name = 'PDF_'+str(i)
      val = outfile.Get(nodename+'/bbH'+mass+name).Integral(-1, -1)
      pdf_variations_nosf.append(val)
      evt_var = ana.info[sample_name]['evt_'+wt]
      sf = evt_nom/evt_var
      pdf_variations.append(val*sf)
    pdf_uncert_nosf=RMS(pdf_variations_nosf)/nominal*100
    pdf_uncert=RMS(pdf_variations)/nominal*100
    #print pdf_uncert_nosf, pdf_uncert

    outstring1+=mass+','
    outstring2+=str(pdf_uncert)+','

    nominal_error=ROOT.Double()
    nominal = outfile.Get(nodename+'/bbH'+mass).IntegralAndError(-1, -1,nominal_error)
    alphas_down_error_nosf=ROOT.Double()
    alphas_down_nosf = outfile.Get(nodename+'/bbH'+mass+'AlphaS_Down').IntegralAndError(-1, -1,alphas_down_error_nosf)
    alphas_up_error_nosf=ROOT.Double()
    alphas_up_nosf = outfile.Get(nodename+'/bbH'+mass+'AlphaS_Up').IntegralAndError(-1, -1,alphas_up_error_nosf)
    evt_var = ana.info[sample_name]['evt_wt_alphasdown']
    sf = evt_nom/evt_var
    alphas_down=alphas_down_nosf*sf
    alphas_down_error=alphas_down_error_nosf*sf
    evt_var = ana.info[sample_name]['evt_wt_alphasup']
    sf = evt_nom/evt_var
    alphas_up=alphas_up_nosf*sf
    alphas_up_error=alphas_up_error_nosf*sf

    alphas_uncert = (alphas_up-alphas_down)/2/nominal
    alphas_uncert_error = math.sqrt(alphas_down_error**2+alphas_up_error**2)/(alphas_up-alphas_down)*alphas_uncert
    #(alphas_up_nosf-alphas_down_nosf)/2/nominal
    #print alphas_uncert*100, '\\% $\\pm$', alphas_uncert_error*100,'\\%'
  print outstring1
  print outstring2

def DONLOUncerts(nodename,infile):
    def LargestDiff(nominal,scales_shifted):
        largest_diff=0
        value = nominal
        for i in scales_shifted:
            diff = abs(scales_shifted[i] - nominal)
            if diff > largest_diff:
              largest_diff = diff
              value = scales_shifted[i]
        return value
    if not options.bbh_nlo_masses: return
    outstring='%'+options.channel+' '+options.datacard+'\n'
    if options.nlo_qsh: outstring+='\\begin{table}[H]\n\\centering\n\\resizebox{\\textwidth}{!}{\n\\begin{tabular}{ |c|c|c| }\n\\hline\nSignal Mass (GeV) & Qsh Uncertainty &  Qsh Uncertainty (*)'
    else: outstring+='\\begin{table}[H]\n\\centering\n\\resizebox{\\textwidth}{!}{\n\\begin{tabular}{ |c|c|c| }\n\\hline\nSignal Mass (GeV) & Scale Uncertainty &  Scale Uncertainty (*)'
    outstring += '\\\\\n\\hline\n'
    #outstring2='{'
    #outstring3='{'
    #outstring4='{'
    for mass in bbh_nlo_masses:
      nominal_error=ROOT.Double()
      nominal = outfile.Get(nodename+'/bbH'+mass).IntegralAndError(-1, -1,nominal_error)
      samples = {'bbH*':'', 'bbH*muR0.5muF0.5':'wt_mur0p5_muf0p5', 'bbH*muR1muF0.5':'wt_mur1_muf0p5', 'bbH*muR0.5muF1':'wt_mur0p5_muf1', 'bbH*muR2muF2':'wt_mur2_muf2', 'bbH*muR2muF1':'wt_mur2_muf1', 'bbH*muR1muF2':'wt_mur1_muf2'}
      qsh_down_error=ROOT.Double()
      qsh_up_error=ROOT.Double()
      if options.nlo_qsh:
        qsh_down = outfile.Get(nodename+'/bbH-QshDown'+mass).IntegralAndError(-1, -1,qsh_down_error)
        qsh_up = outfile.Get(nodename+'/bbH-QshUp'+mass).IntegralAndError(-1, -1,qsh_up_error)
        qsh_uncert_1=(max(nominal,qsh_down,qsh_up) - min(nominal,qsh_down,qsh_up))/2
        up_error = nominal_error
        down_error = nominal_error
        if max(nominal,qsh_down,qsh_up) is qsh_up: up_error = qsh_up_error
        if max(nominal,qsh_down,qsh_up) is qsh_down: up_error = qsh_down_error
        if min(nominal,qsh_down,qsh_up) is qsh_up: down_error = qsh_up_error
        if min(nominal,qsh_down,qsh_up) is qsh_down: down_error = qsh_down_error
        qsh_error_1 = math.sqrt(up_error**2 + down_error**2)
        qsh_uncert_2 = (qsh_up - qsh_down)/2
        qsh_error_2 = math.sqrt(qsh_up_error**2 + qsh_down_error**2)
      scale_max = nominal
      scale_min = nominal
      scale_nosf_max = nominal
      scale_nosf_min = nominal
      up_dic = {}
      down_dic = {}
      for samp in samples:
        acceptance_error = ROOT.Double()
        acceptance = outfile.Get(nodename+'/'+samp.replace('*',mass)).IntegralAndError(-1, -1,acceptance_error)
        if samp is 'bbH*': sf = 1.0
        else:
          sample_name='SUSYGluGluToBBHToTauTau_M-'+mass+'-NLO'
          evt_nom = ana.info[sample_name]['evt']
          evt_var = ana.info[sample_name]['evt_'+samples[samp]]
          sf = evt_nom/evt_var
        acceptance_nosf = acceptance
        acceptance*=sf
        #if samples[samp] in ['wt_mur0p5_muf0p5', 'wt_mur1_muf0p5', 'wt_mur0p5_muf1']: down_dic[samples[samp]] = acceptance
        #if samples[samp] in ['wt_mur2_muf2','wt_mur2_muf1','wt_mur1_muf2']: up_dic[samples[samp]] = acceptance
        if samples[samp] in ['wt_mur0p5_muf0p5']:
            down_dic[samples[samp]] = [acceptance,acceptance_error]
        if samples[samp] in ['wt_mur2_muf2']: up_dic[samples[samp]] = [acceptance,acceptance_error]
        if acceptance > scale_max:
            scale_max = acceptance
            up_error = acceptance_error
        if acceptance < scale_min:
            scale_min = acceptance
            down_error = acceptance_error
        if acceptance_nosf > scale_nosf_max: scale_nosf_max = acceptance_nosf
        if acceptance_nosf < scale_nosf_min: scale_nosf_min = acceptance_nosf
      #up_nom = LargestDiff(nominal,up_dic)
      #down_nom = LargestDiff(nominal,down_dic)
      up_nom = up_dic['wt_mur2_muf2'][0]
      down_nom = down_dic['wt_mur0p5_muf0p5'][0]
      uncert = (scale_max-scale_min)/2
      uncert_error = math.sqrt(up_error**2+down_error**2)/(scale_max-scale_min)*uncert
      uncert_nosf = (scale_nosf_max-scale_nosf_min)/2
      uncert_alt_method = (up_nom-down_nom)/2
      uncert_alt_error = math.sqrt(up_dic['wt_mur2_muf2'][1]**2 + down_dic['wt_mur0p5_muf0p5'][1]**2)/(up_nom-down_nom) *uncert_alt_method
      pythia_error=ROOT.Double()
      pythia_yield = outfile.Get(nodename+'/bbH'+mass).IntegralAndError(-1, -1,pythia_error)
      outstring +=mass#+ ' & '+ str(round(pythia_yield,1))+' $\pm$ '+str(round(pythia_error,1))+ ' & '+ str(round(nominal,1))+' $\pm$ '+str(round(nominal_error,1))+ '('+str(round((pythia_yield-nominal)*100/pythia_yield,2))+' \%)' + ' & '+ str(round(uncert_nosf/nominal,2)) + ' & '+ str(round(uncert/nominal,2))+ ' & '+ str(round(uncert_alt_method/nominal,2))
      if options.nlo_qsh:
        outstring+=' & '+ str(round(100*qsh_uncert_1/nominal,1))+' $\pm$ '+str(round(100*qsh_error_1/nominal,1))+' & '+ str(round(100*qsh_uncert_2/nominal,1))+' $\pm$ '+str(round(100*qsh_error_2/nominal,1))+'\\\\\n'
      else:
        outstring+=' & '+ str(round(100*uncert/nominal,1))+'\\% $\\pm$ '+ str(round(100*uncert_error/nominal,1)) +'\\% & '+ str(round(100*uncert_alt_method/nominal,1))+'\\% $\\pm$ '+str(round(100*uncert_alt_error/nominal,1)) +'\\% \\\\\n'
      #outstring2 +=str(round(100*uncert/nominal,1))+','
      #outstring3 +=str(round(100*uncert_error/nominal,1))+','
      #outstring4+=mass+','
    outstring+='\\hline\n\\end{tabular}}\n\\end{table}'
    print outstring
    #print outstring2
    #print outstring3
    #print outstring4

def ScaleUncertBand(nodename='',outfile='output.root',NormScales=True):
    hist_names=['bbH*muR0.5muF0.5','bbH*muR1muF0.5','bbH*muR0.5muF1','bbH*muR2muF1','bbH*muR1muF2','bbH*muR2muF2']
    mass = '100'
    if options.draw_signal_mass: mass = options.draw_signal_mass
    hists=[]
    for hist_name in hist_names:
        sf = 1.0
        if NormScales:
            sample_name='SUSYGluGluToBBHToTauTau_M-'+mass+'-NLO'
            evt_nom = ana.info[sample_name]['evt']
            evt_var = ana.info[sample_name]['evt_'+hist_name.replace('bbH*','wt_').replace('muF','_muf').replace('muR','mur').replace('0.5','0p5')]
            sf = evt_nom/evt_var
        hist_name=hist_name.replace('*',mass)
        hist = outfile.Get(nodename+'/'+hist_name).Clone()
        if NormScales: hist.Scale(sf)
        hists.append(hist)
    nom_hist = outfile.Get(nodename+'/bbH'+mass)
    up_hist = nom_hist.Clone()
    down_hist = nom_hist.Clone()
    up_hist.SetName('ScaleUp')
    down_hist.SetName('ScaleDown')
    for i in range (1,nom_hist.GetNbinsX()+1):
        for hist in hists:
          max_content = up_hist.GetBinContent(i)
          min_content = down_hist.GetBinContent(i)
          content = hist.GetBinContent(i)
          if content > max_content: up_hist.SetBinContent(i,content)
          if content < min_content: down_hist.SetBinContent(i,content)
    outfile.cd(nodename)
    up_hist.Write()
    down_hist.Write()
    outfile.cd()


def DYUncertBand(outfile='output.root',ScaleToData=True):
    bkg_hist = outfile.Get(nodename+'/total_bkg')
    nominal_hist = outfile.Get(nodename+'/ZLL')
    up_hist = outfile.Get(nodename+'/total_bkg').Clone()
    down_hist = outfile.Get(nodename+'/total_bkg').Clone()
    up_hist.SetName('total_bkg_up')
    down_hist.SetName('total_bkg_down')
    shifts=['_ES', '_TT', '_Stat0', '_Stat40', '_Stat80']
    for i in range(1,nominal_hist.GetNbinsX()+1):
      nom_content = nominal_hist.GetBinContent(i)
      bkg_content = bkg_hist.GetBinContent(i)
      uncert=0
      for shift in shifts:
          shift_hist_up = outfile.Get(nodename+'/ZLL'+shift+'Up')
          shift_hist_down = outfile.Get(nodename+'/ZLL'+shift+'Down')
          up = abs(shift_hist_up.GetBinContent(i) - nom_content)
          down = abs(shift_hist_down.GetBinContent(i) - nom_content)
          uncert=math.sqrt(max([up,down])**2+uncert**2)
      up_hist.SetBinContent(i, bkg_content+uncert)
      down_hist.SetBinContent(i, bkg_content-uncert)
    outfile.cd(nodename)
    up_hist.Write()
    down_hist.Write()
    outfile.cd()
    if ScaleToData:
      data_hist=outfile.Get(nodename+'/data_obs')
      data_total=data_hist.Integral(-1,-1)
      bkg_total=bkg_hist.Integral(-1,-1)
      data_hist.Scale(bkg_total/data_total)
      outfile.cd(nodename)
      data_hist.Write()
      outfile.cd()

def GetTotals(ana,add_name="",outfile='outfile.root'):
    # add histograms to get totals for backgrounds split into real/fake taus and make a total backgrounds histogram
    outfile.cd(nodename)
    nodes = ana.nodes[nodename].SubNodes()
    nodenames=[]
    for node in nodes: nodenames.append(node.name)
    for i in ['TT', 'VV', 'Z']:
        j = 'T'
        outname = i+add_name
        first_hist=True
        if options.channel == 'em' and i is 'Z':
            if first_hist and 'ZLL'+add_name in nodenames:
                sum_hist = ana.nodes[nodename].nodes['ZLL'+add_name].shape.hist.Clone()
                first_hist=False
            elif 'ZLL'+add_name in nodenames: sum_hist.Add(ana.nodes[nodename].nodes['ZLL'+add_name].shape.hist.Clone())
            if first_hist and'ZTT'+add_name in nodenames:
                sum_hist = ana.nodes[nodename].nodes['ZTT'+add_name].shape.hist.Clone()
                first_hist=False
            elif 'ZTT'+add_name in nodenames: sum_hist.Add(ana.nodes[nodename].nodes['ZTT'+add_name].shape.hist.Clone())
            if not first_hist:
                sum_hist.SetName(outname)
                sum_hist.Write()
        elif (options.channel == 'zee' or options.channel == 'zmm') and i is 'Z':
            if first_hist and 'ZLL'+add_name in nodenames:
                sum_hist = ana.nodes[nodename].nodes['ZLL'+add_name].shape.hist.Clone()
                first_hist=False
            elif 'ZLL'+add_name in nodenames: sum_hist.Add(ana.nodes[nodename].nodes['ZLL'+add_name].shape.hist.Clone())
            if not first_hist:
                sum_hist.SetName(outname)
                sum_hist.Write()
        else:
            if i is 'Z':
                outname = 'ZLL'+add_name
                j = 'L'
            if i+'J' or i+j in [node.name for node in nodes]:
                if first_hist and i+'J'+add_name in nodenames:
                    sum_hist = ana.nodes[nodename].nodes[i+'J'+add_name].shape.hist.Clone()
                    first_hist=False
                elif i+'J'+add_name in nodenames: sum_hist.Add(ana.nodes[nodename].nodes[i+'J'+add_name].shape.hist.Clone())
                if first_hist and i+j+add_name in nodenames:
                    sum_hist = ana.nodes[nodename].nodes[i+j+add_name].shape.hist.Clone()
                    first_hist=False
                elif i+j+add_name in nodenames: sum_hist.Add(ana.nodes[nodename].nodes[i+j+add_name].shape.hist.Clone())
            if not first_hist:
                sum_hist.SetName(outname)
                sum_hist.Write()
    first_hist=True
    for node in nodes:
        if True not in [node.name.find(sig) != -1 for sig in signal_samples.keys()] and node.name != 'data_obs' and node.name.find("_SM"+options.add_sm_background) ==-1:
            if options.method == 18 and 'jetFakes' == node.name: continue
            if add_name not in node.name: continue
            if first_hist:
                total_bkg = ana.nodes[nodename].nodes[node.name].shape.hist.Clone()
                first_hist=False
            else: total_bkg.Add(ana.nodes[nodename].nodes[node.name].shape.hist.Clone())
    if not first_hist:
        total_bkg.SetName('total_bkg'+add_name)
        total_bkg.Write()
    outfile.cd()


def CompareShapes(compare_w_shapes, compare_qcd_shapes):
    if compare_w_shapes:
      nominal_hist = outfile.Get(nodename+'/W')
      nominal_scale = nominal_hist.Integral(0,nominal_hist.GetNbinsX()+1)
      directory = outfile.Get(nodename)
      outfile.cd(nodename)
      shape_hist = outfile.Get(nodename+'/W_shape')
      shape_scale = shape_hist.Integral(0,shape_hist.GetNbinsX()+1)
      shape_hist.Scale(nominal_scale/shape_scale)
      shape_hist.Write()
    if compare_qcd_shapes:
      nominal_hist = outfile.Get(nodename+'/QCD')
      nominal_scale = nominal_hist.Integral(0,nominal_hist.GetNbinsX()+1)
      directory = outfile.Get(nodename)
      outfile.cd(nodename)
      shape_hist = outfile.Get(nodename+'/QCD_shape')
      shape_scale = shape_hist.Integral(0,shape_hist.GetNbinsX()+1)
      shape_hist.Scale(nominal_scale/shape_scale)
      shape_hist.Write()

def AppendNameToSamples(samples=[],name_to_add=None):
  if name_to_add is None or name_to_add is '': return samples
  elif type(samples) is dict:
    new_samples = {}
    for key in samples: new_samples[key] = samples[key]+name_to_add
    return new_samples
  else:
    new_samples = []
    for sample in samples: new_samples.append(sample+name_to_add)
    return new_samples

def RunPlotting(ana, cat='',cat_data='', sel='', add_name='', wt='wt', do_data=True, samples_to_skip=[], outfile='output.root',ff_syst_weight=None):
    doTTJ = 'TTJ' not in samples_to_skip
    doTTT = 'TTT' not in samples_to_skip
    doVVJ = 'VVJ' not in samples_to_skip
    doVVT = 'VVT' not in samples_to_skip
    doZL  = 'ZL'  not in samples_to_skip
    doZJ  = 'ZJ'  not in samples_to_skip

    # produce template for observed data
    if do_data:
        if options.do_ss:
          OSSS = '!os'
        else:
            OSSS = 'os'
        full_selection = BuildCutString('wt', sel, cat_data, OSSS)
        ana.nodes[nodename].AddNode(ana.SummedFactory('data_obs', data_samples, plot_unmodified, full_selection))

    # produce templates for backgrounds
    if options.method == 17 and options.channel != "em":
        doVVJ=False
        doTTJ=False
        GenerateFakeTaus(ana, add_name, data_samples, plot, plot_unmodified, wt, sel, options.cat,not options.do_ss,ff_syst_weight)

        # use existing methods to calculate background due to non-fake taus
        add_fake_factor_selection = "gen_match_2<6"
        if options.channel == "tt": add_fake_factor_selection = "gen_match_1<6 && gen_match_2<6"
        residual_cat=cat+"&&"+add_fake_factor_selection

        if 'EmbedZTT' not in samples_to_skip and options.embedding:
            GenerateEmbedded(ana, add_name, embed_samples, plot, wt, sel, residual_cat, z_sels, not options.do_ss)
        if 'ZTT' not in samples_to_skip:
            GenerateZTT(ana, add_name, ztt_samples, plot, wt, sel, residual_cat, z_sels, not options.do_ss)
        if 'ZLL' not in samples_to_skip:
            GenerateZLL(ana, add_name, ztt_samples, plot, wt, sel, residual_cat, z_sels, not options.do_ss,doZL,False)
        if 'TT' not in samples_to_skip:
            GenerateTop(ana, add_name, top_samples, plot, wt, sel, residual_cat, top_sels, not options.do_ss, doTTT, doTTJ)
        if 'VV' not in samples_to_skip:
            GenerateVV(ana, add_name, vv_samples, plot, wt, sel, residual_cat, vv_sels, not options.do_ss, doVVT, doVVJ)
        if 'EWKZ' not in samples_to_skip and options.era in ['smsummer16','cpsummer16','tauid2016']:
            GenerateEWKZ(ana, add_name, ewkz_samples, plot, wt, sel, residual_cat, z_sels, not options.do_ss)

    else:
        method = options.method
        if options.method == 18:
            GenerateFakeTaus(ana, add_name, data_samples, plot, plot_unmodified,wt, sel, options.cat,not options.do_ss,ff_syst_weight)
            if options.channel == 'tt': method = 8
            elif options.cat == "btag_loosemt" or options.cat == "btag_tight": method = 16
            elif options.channel == 'et' or options.channel == 'mt': method = 12
        if 'EmbedZTT' not in samples_to_skip and options.embedding and options.channel != 'zmm':
            GenerateEmbedded(ana, add_name, embed_samples, plot, wt, sel, cat, z_sels, not options.do_ss)
        if 'ZTT' not in samples_to_skip:
            GenerateZTT(ana, add_name, ztt_samples, plot, wt, sel, cat, z_sels, not options.do_ss)
        if 'ZLL' not in samples_to_skip:
            GenerateZLL(ana, add_name, ztt_samples, plot, wt, sel, cat, z_sels, not options.do_ss,doZL,doZJ)
            if options.embedding and options.channel =='zmm': GenerateZLEmbedded(ana, add_name, embed_samples, plot, wt, sel, cat, z_sels, not options.do_ss)
        if 'TT' not in samples_to_skip:
            GenerateTop(ana, add_name, top_samples, plot, wt, sel, cat, top_sels, not options.do_ss, doTTT, doTTJ)
        if 'VV' not in samples_to_skip:
            GenerateVV(ana, add_name, vv_samples, plot, wt, sel, cat, vv_sels, not options.do_ss, doVVT, doVVJ)
        if 'W' not in samples_to_skip:
            GenerateW(ana, add_name, wjets_samples, data_samples, wgam_samples, plot, plot_unmodified, wt, sel, cat, cat_data, method, qcd_os_ss_ratio, not options.do_ss)
        if 'QCD' not in samples_to_skip:
            GenerateQCD(ana, add_name, data_samples, plot, plot_unmodified, wt, sel, cat, cat_data, method, qcd_os_ss_ratio, not options.do_ss,wshift)
        if 'EWKZ' not in samples_to_skip and options.era in ['smsummer16','cpsummer16','tauid2016']:
            GenerateEWKZ(ana, add_name, ewkz_samples, plot, wt, sel, cat, z_sels, not options.do_ss)
        if 'ggH_hww' not in samples_to_skip and 'qqH_hww' not in samples_to_skip and options.era in ['smsummer16','cpsummer16'] and options.channel == 'em':
            GenerateHWW(ana, add_name, gghww_samples, qqhww_samples, plot, wt, sel, cat, not options.do_ss, True, True)

        if compare_w_shapes:
          cat_relax=cats['w_shape_comp']
          GenerateW(ana, '_shape', wjets_samples, data_samples, wgam_samples, plot, plot_unmodified, wt, sel, cat_relax, cats_unmodified['w_shape_comp'], 8, qcd_os_ss_ratio, not options.do_ss)
        if compare_qcd_shapes:
          cat_relax=cats['qcd_shape_comp']
          GenerateQCD(ana, '_shape', data_samples, plot, plot_unmodified, wt, sel, cat_relax,cats_unmodified['qcd_shape_comp'], method, qcd_os_ss_ratio, not options.do_ss)

    if 'signal' not in samples_to_skip:
        if options.analysis == 'sm':
            procs=[]
            for proc in sm_samples:
                if True not in [samp in proc for samp in samples_to_skip]: procs.append(proc)
            GenerateSMSignal(ana, add_name, plot, sm_masses, wt, sel, cat, not options.do_ss,processes=procs)
        elif options.analysis == 'mssm' and (options.ggh_masses != "" or options.bbh_masses != ""):
            bbh_add_name = ''
            if options.bbh_nlo_masses: bbh_add_name = '-LO'
            GenerateMSSMSignal(ana, add_name, bbh_add_name, plot, ggh_masses, bbh_masses, wt, sel, cat, not options.do_ss)
            if options.add_sm_background:
                GenerateSMSignal(ana, add_name, plot, ['125'],  wt, sel, cat, not options.do_ss, options.add_sm_background)
        elif options.analysis == 'Hhh':
            GenerateHhhSignal(ana, add_name, plot, ggh_masses, wt, sel, cat, not options.do_ss)
        if options.analysis == 'mssm' and options.bbh_nlo_masses != "":
            GenerateNLOMSSMSignal(ana, add_name, plot, [''], bbh_nlo_masses, wt, sel, cat, options.doNLOScales, options.doPDF, not options.do_ss)
        if options.analysis == 'mssm' and options.doMSSMReWeighting:
          GenerateReWeightedMSSMSignal(ana, add_name, plot, ggh_masses, wt, sel, cat, not options.do_ss)

    if options.syst_embedding_tt and options.embedding and systematic == 'default':
        GenerateTop(ana, '_embed_syst', top_samples, plot, wt, sel, cat, top_sels_embed, not options.do_ss, True, False)

def Get1DBinNumFrom2D(h2d,xbin,ybin):
    Nxbins = h2d.GetNbinsX()
    return (ybin-1)*Nxbins + xbin -1

def Get1DBinNumFrom3D(h3d,xbin,ybin,zbin):
    Nxbins = h3d.GetNbinsX()
    Nybins = h3d.GetNbinsY()
    return (zbin-1)*Nxbins*Nybins + (ybin-1)*Nxbins + xbin -1

def UnrollHist2D(h2d,inc_y_of=True):
    # inc_y_of = True includes the y over-flow bins
    if inc_y_of: n = 1
    else: n = 0
    Nbins = (h2d.GetNbinsY()+n)*(h2d.GetNbinsX())
    h1d = ROOT.TH1D(h2d.GetName(), '', Nbins, 0, Nbins)
    for i in range(1,h2d.GetNbinsX()+1):
      for j in range(1,h2d.GetNbinsY()+1+n):
        glob_bin = Get1DBinNumFrom2D(h2d,i,j)
        content = h2d.GetBinContent(i,j)
        error = h2d.GetBinError(i,j)
        h1d.SetBinContent(glob_bin+1,content)
        h1d.SetBinError(glob_bin+1,error)
        #if 'sjdphi' in plot: h1d.GetXaxis().SetBinLabel(glob_bin+1,'%.1f-%.1f' % (h2d.GetXaxis().GetBinLowEdge(i),h2d.GetXaxis().GetBinLowEdge(i+1)))
        #else:
        #  h1d.GetXaxis().SetBinLabel(glob_bin+1,'%.0f-%.0f' % (h2d.GetXaxis().GetBinLowEdge(i),h2d.GetXaxis().GetBinLowEdge(i+1)))
        #if 'sdphi' in options.var: h1d.GetXaxis().SetBinLabel(glob_bin+1,'%.1f-%.1f' % (h2d.GetXaxis().GetBinLowEdge(i),h2d.GetXaxis().GetBinLowEdge(i+1)))
    #h1d.LabelsOption('v','X')
    return h1d

def UnrollHist3D(h3d,inc_y_of=False,inc_z_of=True):
    if inc_y_of: ny = 1
    else: ny = 0
    if inc_z_of: nz = 1
    else: nz = 0

    Nbins = (h3d.GetNbinsZ()+nz)*(h3d.GetNbinsY()+ny)*(h3d.GetNbinsX())
    h1d = ROOT.TH1D(h3d.GetName(), '', Nbins, 0, Nbins)
    for i in range(1,h3d.GetNbinsX()+1):
      for j in range(1,h3d.GetNbinsY()+1+ny):
        for k in range(1,h3d.GetNbinsZ()+1+nz):
          glob_bin = Get1DBinNumFrom3D(h3d,i,j,k)
          content = h3d.GetBinContent(i,j,k)
          error = h3d.GetBinError(i,j,k)
          h1d.SetBinContent(glob_bin+1,content)
          h1d.SetBinError(glob_bin+1,error)
          #if 'sjdphi' in plot: h1d.GetXaxis().SetBinLabel(glob_bin+1,'%.1f-%.1f' % (h3d.GetXaxis().GetBinLowEdge(i),h3d.GetXaxis().GetBinLowEdge(i+1)))
          #else:
          #  h1d.GetXaxis().SetBinLabel(glob_bin+1,'%.0f-%.0f' % (h3d.GetXaxis().GetBinLowEdge(i),h3d.GetXaxis().GetBinLowEdge(i+1)))
         # if 'sdphi' in options.var: h1d.GetXaxis().SetBinLabel(glob_bin+1,'%.1f-%.1f' % (h3d.GetXaxis().GetBinLowEdge(i),h3d.GetXaxis().GetBinLowEdge(i+1)))
    #h1d.LabelsOption('v','X')
    return h1d

def NormSignals(outfile,add_name):
    # When adding signal samples to the data-card we want to scale all XS to 1pb - correct XS times BR is then applied at combine harvestor level
    if 'signal' not in samples_to_skip:
        outfile.cd(nodename)
        if options.analysis == "sm" or options.add_sm_background:
            if options.analysis == "sm":
                masses = sm_masses
            else:
                masses = [options.add_sm_background]
            for samp in sm_samples:
                if options.analysis == "sm":
                    samp_name = samp
                else:
                    samp_name = samp+"_SM"
                if masses is not None:
                    for mass in masses:
                        xs = ana.info[sm_samples[samp].replace('*',mass)]['xs']
                        sf = 1.0/xs
                        if not outfile.GetDirectory(nodename).GetListOfKeys().Contains(samp_name+mass+add_name): continue
                        sm_hist = outfile.Get(nodename+'/'+samp_name+mass+add_name)
                        sm_hist.Scale(sf)
                        sm_hist.Write("",ROOT.TObject.kOverwrite)
        if options.analysis == "mssm":
            for samp in mssm_samples:
                if samp == 'ggH':
                    masses = ggh_masses
                elif samp == 'bbH' and not options.bbh_nlo_masses:
                    masses = bbh_masses
                elif 'bbH' in samp:
                    masses = bbh_nlo_masses
                if masses is not None:
                    for mass in masses:
                        xs = ana.info[mssm_samples[samp].replace('*',mass)]['xs']
                        sf = 1.0/xs
                        mssm_hist = outfile.Get(nodename+'/'+samp+mass+add_name)
                        mssm_hist.Scale(sf)
                        mssm_hist.Write("",ROOT.TObject.kOverwrite)
                        if options.doMSSMReWeighting:
                          re_weighted_names = ['ggh_t','ggh_b','ggh_i','ggH_t','ggH_b','ggH_i','ggA_t','ggA_b','ggA_i']
                          for name in re_weighted_names:
                            mssm_hist = ana.nodes[nodename].nodes[name+mass+add_name].shape.hist
                            mssm_hist.Scale(sf)
                            mssm_hist.Write("",ROOT.TObject.kOverwrite)
        if options.analysis == "Hhh":
            for samp in Hhh_samples:
                masses = ggh_masses
                if masses is not None:
                    for mass in masses:
                        xs = ana.info[Hhh_samples[samp].replace('*',mass)]['xs']
                        sf = 1.0/xs
                        mssm_hist = outfile.Get(nodename+'/'+samp+mass+add_name)
                        mssm_hist.Scale(sf)
                        mssm_hist.Write("",ROOT.TObject.kOverwrite)
        outfile.cd()


# Create output file
is_2d=False
is_3d=False
var_name = options.var.split('[')[0]
var_name = var_name.split('(')[0]
if var_name.count(',') == 1:
    is_2d = True
    var_name = var_name.split(',')[0]+'_vs_'+var_name.split(',')[1]
if var_name.count(',') == 2:
    is_3d = True
    var_name = var_name.split(',')[0]+'_vs_'+var_name.split(',')[1]+'_vs_'+var_name.split(',')[2]

if options.datacard != "": datacard_name = options.datacard
else: datacard_name = options.cat
if options.extra_name != "": datacard_name+='_'+options.extra_name
output_name = options.outputfolder+'/datacard_'+var_name+'_'+datacard_name+'_'+options.channel+'_'+options.year+'.root'
outfile = ROOT.TFile(output_name, 'RECREATE')

cats['cat'] = '('+cats[options.cat]+')*('+cats['baseline']+')'
if options.channel=="em": cats['em_shape_cat'] = '('+cats[options.cat]+')*('+cats['loose_baseline']+')'
sel = options.sel
plot = options.var
plot_unmodified = plot
if options.datacard != "": nodename = options.channel+'_'+options.datacard
else: nodename = options.channel+'_'+options.cat

add_names = []
cats_unmodified = copy.deepcopy(cats)

max_systs_per_pass = 30 # code uses too much memory if we try and process too many systematics at once so set the maximum number of systematics processed per loop here
while len(systematics) > 0:
  ana = Analysis()
  #if options.syst_scale_j_by_source != '': ana.writeSubnodes(False) # storing subnodes uses too much memory when doing JES uncertainties split by source

  ana.remaps = {}
  if options.channel == 'em':
      ana.remaps['MuonEG'] = 'data_obs'
  elif options.channel in ['mt','mj','zmm']:
      ana.remaps['SingleMuon'] = 'data_obs'
  elif options.channel == 'et' or options.channel == 'zee':
      ana.remaps['SingleElectron'] = 'data_obs'
  elif options.channel == 'tt':
      ana.remaps['Tau'] = 'data_obs'

  ana.nodes.AddNode(ListNode(nodename))
  if options.do_custom_uncerts and options.custom_uncerts_wt_up != "" and options.custom_uncerts_wt_down !="":
      ana_up   = Analysis()
      ana_down = Analysis()
      ana_up = copy.deepcopy(ana)
      ana_down = copy.deepcopy(ana)
  prev_dir=None
  for index, systematic in enumerate(list(systematics.keys())[:max_systs_per_pass]):
      if prev_dir is not None and systematics[systematic][0] is not prev_dir: continue # this ensures that we process the same trees from every call to ana.Run() - i.e trees in sub-directory systematics[systematic][0]
      prev_dir = systematics[systematic][0]
      print "Processing:", systematic
      print ""

      plot = options.var
      cats=copy.deepcopy(cats_unmodified)
      wshift=1.0
      if systematic == 'syst_qcd_shape_wsf_up': wshift+=w_abs_shift
      if systematic == 'syst_qcd_shape_wsf_down': wshift-=w_abs_shift
      if options.syst_scale_j_by_source != '' and 'syst_scale_j_by_source' in systematic:
        # if JES systematic split by source then the category and plotting variable strings need to be modified to use the shifted variables
        replace_dict = systematics[systematic][5]
        for cat in cats: cats[cat] = OverwriteNames(cats[cat], replace_dict)
        plot = OverwriteNames(plot, replace_dict)

      add_folder_name = systematics[systematic][0]
      add_name = systematics[systematic][1]
      isFFSyst = systematics[systematic][4]
      ff_syst_weight = None
      if not isFFSyst: weight = systematics[systematic][2]
      else:
          weight='wt'
          ff_syst_weight = systematics[systematic][2]
      if options.add_wt is not "": weight+="*"+options.add_wt
      if options.channel == "tt" and options.era == 'mssmsummer16': weight+='*wt_tau_id_medium'
      if options.channel == "tt" and options.era in ['smsummer16','cpsummer16']: weight+='*wt_tau_id_tight'
      if options.cat == '0jet': weight+='*wt_lfake_rate'

      samples_to_skip = systematics[systematic][3]
      add_names.append(add_name)
      syst_add_name=add_folder_name


      mc_input_folder_name = options.folder
      if add_folder_name != '': mc_input_folder_name += '/'+add_folder_name

      if options.signal_folder: signal_mc_input_folder_name = options.signal_folder
      else: signal_mc_input_folder_name = options.folder
      if add_folder_name != '': signal_mc_input_folder_name += '/'+add_folder_name

      if options.embed_folder: embed_input_folder_name = options.embed_folder
      else: embed_input_folder_name = options.folder
      if add_folder_name != '' and 'EmbedZTT' not in samples_to_skip: embed_input_folder_name += '/'+add_folder_name

      # Add all data files
      for sample_name in data_samples:
          ana.AddSamples(options.folder+'/'+sample_name+'_'+options.channel+'*.root', 'ntuple', None, sample_name)

      # Add all MC background files
      for sample_name in ztt_samples + vv_samples + wgam_samples + top_samples + ztt_shape_samples + wjets_samples+ewkz_samples+gghww_samples+qqhww_samples:
          ana.AddSamples(mc_input_folder_name+'/'+sample_name+'_'+options.channel+'*.root', 'ntuple', None, sample_name)

      # Add embedded samples if using
      if options.embedding:
        for sample_name in embed_samples:
          ana.AddSamples(embed_input_folder_name+'/'+sample_name+'_'+options.channel+'*.root', 'ntuple', None, sample_name)

      # Add all MC signal files

      if options.analysis == 'sm':
          signal_samples = sm_samples
      elif options.analysis == 'mssm':
          signal_samples = mssm_samples
          if options.bbh_nlo_masses: signal_samples['bbH'] = mssm_nlo_samples['bbH']
          if options.nlo_qsh: signal_samples.update(mssm_nlo_qsh_samples)
          if options.bbh_nlo_masses and options.bbh_masses:  signal_samples.update(mssm_lo_samples)
      elif options.analysis == 'Hhh':
          signal_samples = Hhh_samples

      for samp in signal_samples:
          if options.analysis == "sm":
              masses=sm_masses
          elif samp == 'ggH':
              masses = ggh_masses
          elif (samp == 'bbH' and not options.bbh_nlo_masses) or samp == 'bbH-LO':
              masses = bbh_masses
          elif 'bbH' in samp:
              masses = bbh_nlo_masses
          if masses is not None:
              for mass in masses:
                  sample_name = signal_samples[samp].replace('*',mass)
                  tree_name = 'ntuple'
                  if options.gen_signal: tree_name = 'gen_ntuple'
                  ana.AddSamples(signal_mc_input_folder_name+'/'+sample_name+'_'+options.channel+'*.root', tree_name, None, sample_name)
      if options.add_sm_background and options.analysis == 'mssm':
          for samp in sm_samples:
              sample_name = sm_samples[samp].replace('*',options.add_sm_background)
              ana.AddSamples(mc_input_folder_name+'/'+sample_name+'_'+options.channel+'*.root', 'ntuple', None, sample_name)

      ana.AddInfo(options.paramfile, scaleTo='data_obs')

      # Add data only for default
      if systematic == 'default': do_data = True
      else: do_data = False

      #Run default plot
      if options.scheme == 'signal':
          samples_to_skip.extend(['TTT','TTJ','VVT','VVJ','W','QCD','jetFakes','ZLL','ZTT','ZL'])
          do_data = False
      RunPlotting(ana, cats['cat'], cats_unmodified['cat'], sel, add_name, weight, do_data, samples_to_skip,outfile,ff_syst_weight)
      if options.era == "tauid2016" and options.channel in ['et','mt']:
          RunPlotting(ana, cats['pass']+'&&'+cats['baseline'], cats_unmodified['pass']+'&&'+cats_unmodified['baseline'], sel, "pass"+add_name, weight, False, samples_to_skip,outfile,ff_syst_weight)
          RunPlotting(ana, cats['fail']+'&&'+cats['baseline'], cats_unmodified['fail']+'&&'+cats_unmodified['baseline'], sel, "fail"+add_name, weight, False, samples_to_skip,outfile,ff_syst_weight)

      if options.do_custom_uncerts and options.custom_uncerts_wt_up != "" and options.custom_uncerts_wt_down !="":
          add_names.append("_custom_uncerts_up")
          add_names.append("_custom_uncerts_down")
          RunPlotting(ana_up, cats['cat'], cats_unmodified['cat'], sel, '_custom_uncerts_up', weight+'*'+options.custom_uncerts_wt_up, do_data, ['signal'],outfile,ff_syst_weight)
          RunPlotting(ana_down, cats['cat'], cats_unmodified['cat'], sel, '_custom_uncerts_down', weight+'*'+options.custom_uncerts_wt_down, do_data, ['signal'],outfile,ff_syst_weight)

      del systematics[systematic]
  ana.Run()
  ana.nodes.Output(outfile)
  # fix negative bns,empty histograms etc.
  FixBins(ana,outfile)
  for n in add_names:
    GetTotals(ana,n,outfile)
  PrintSummary(nodename, ['data_obs'], add_names)

if compare_w_shapes or compare_qcd_shapes: CompareShapes(compare_w_shapes, compare_qcd_shapes)

if options.method in [17,18] and options.do_ff_systs: NormFFSysts(ana,outfile)
if (options.era in ["smsummer16"] and options.syst_w_fake_rate and options.method != 8) or options.era in ["tauid2016"]: NormWFakeSysts(ana,outfile)
#NormEmbedToMC(ana,outfile) # this is to check embedding sensitivity after scaling embedding to MC yields

if options.syst_embedding_tt and options.embedding and not options.no_default: TTBarEmbeddingSyst(ana,outfile,options.syst_embedding_tt)

if options.doNLOScales:
    ScaleUncertBand(nodename,outfile)
    DONLOUncerts(nodename,outfile)
if options.doPDF:
    PDFUncerts(nodename,outfile)


# sm 2D unrolling
if is_2d and options.do_unrolling:
  x_lines = []
  y_labels = []
  first_hist = True
  # loop over all TH2Ds and for each one unroll to produce TH1D and add to datacard
  directory = outfile.Get(nodename)
  outfile.cd(nodename)
  hists_to_add = []
  for key in directory.GetListOfKeys():
    hist_name = key.GetName()
    hist = directory.Get(hist_name).Clone()
    if not isinstance(hist,ROOT.TDirectory):
      include_of = True
      h1d = UnrollHist2D(hist,include_of)
      hists_to_add.append(h1d)
      if first_hist:
        first_hist=False
        Nxbins = hist.GetNbinsX()
        for i in range(1,hist.GetNbinsY()+1): x_lines.append(Nxbins*i)
        for j in range(1,hist.GetNbinsY()+1): y_labels.append([hist.GetYaxis().GetBinLowEdge(j),hist.GetYaxis().GetBinLowEdge(j+1)])
        if include_of: y_labels.append([hist.GetYaxis().GetBinLowEdge(hist.GetNbinsY()+1),-1])
  for hist in hists_to_add: hist.Write("",ROOT.TObject.kOverwrite)

# sm 3D unrolling
if is_3d and options.do_unrolling:
  x_lines = []
  y_labels = []
  z_labels = []
  first_hist = True
  # loop over all TH3Ds and for each one unroll to produce TH1D and add to datacard
  directory = outfile.Get(nodename)
  outfile.cd(nodename)
  hists_to_add = []
  for key in directory.GetListOfKeys():
    hist_name = key.GetName()
    hist = directory.Get(hist_name).Clone()
    if not isinstance(hist,ROOT.TDirectory):
      include_y_of = False
      include_z_of = True
      h1d = UnrollHist3D(hist,include_y_of,include_z_of)
      hists_to_add.append(h1d)
      if first_hist:
        first_hist=False
        Nxbins = hist.GetNbinsX()
        for i in range(1,hist.GetNbinsY()+1): x_lines.append(Nxbins*i)
        for j in range(1,hist.GetNbinsY()+1): y_labels.append([hist.GetYaxis().GetBinLowEdge(j),hist.GetYaxis().GetBinLowEdge(j+1)])
        if include_y_of: y_labels.append([hist.GetYaxis().GetBinLowEdge(hist.GetNbinsY()+1),-1])
        for j in range(1,hist.GetNbinsZ()+1): z_labels.append([hist.GetZaxis().GetBinLowEdge(j),hist.GetZaxis().GetBinLowEdge(j+1)])
        if include_z_of: z_labels.append([hist.GetZaxis().GetBinLowEdge(hist.GetNbinsZ()+1),-1])
  for hist in hists_to_add: hist.Write("",ROOT.TObject.kOverwrite)

outfile.Close()


if is_2d and not options.do_unrolling: exit(0) # add options for is_3d as well!
plot_file = ROOT.TFile(output_name, 'READ')

#if options.method in [12,16] or (options.channel != "tt" and options.method == "18"):
#    w_os = plot_file.Get(nodename+"/W.subnodes/W_os")
#    w_ss = plot_file.Get(nodename+"/W.subnodes/W_ss")
#    w_os_error=ROOT.Double(0.)
#    w_ss_error=ROOT.Double(0.)
#    w_os_total = w_os.IntegralAndError(0,w_os.GetNbinsX()+1,w_os_error)
#    w_ss_total = w_ss.IntegralAndError(0,w_ss.GetNbinsX()+1,w_ss_error)
#    w_os_ss = w_os_total/w_ss_total
#    w_os_ss_error = math.sqrt( (w_os_error/w_os_total)**2 + (w_ss_error/w_ss_total)**2 )*w_os_ss
#
#    #print "W OS/SS ratio = ", w_os_ss, "+/-", w_os_ss_error, "("+str(100*w_os_ss_error/w_os_ss)+" %)"

if options.custom_uncerts_wt_up != "" and options.custom_uncerts_wt_down != "":
    custom_uncerts_up_name = "total_bkg_custom_uncerts_up"
    custom_uncerts_down_name = "total_bkg_custom_uncerts_down"
else:
    custom_uncerts_up_name = options.custom_uncerts_up_name
    custom_uncerts_down_name = options.custom_uncerts_down_name

if not options.no_plot:
    if options.datacard != "": plot_name = options.outputfolder+'/'+var_name+'_'+options.datacard+'_'+options.channel+'_'+options.year
    else: plot_name = options.outputfolder+'/'+var_name+'_'+options.cat+'_'+options.channel+'_'+options.year
    if options.do_ss: plot_name += "_ss"
    if options.log_x: plot_name += "_logx"
    if options.log_y: plot_name += "_logy"
    titles = plotting.SetAxisTitles(options.var,options.channel)
    if options.do_unrolling and is_2d: titles2d = plotting.SetAxisTitles2D(options.var,options.channel)
    if options.x_title == "":
      x_title = titles[0]
      if options.do_unrolling and is_2d:
        x_title = titles2d[0][0]
    else: x_title = options.x_title

    if options.y_title == "":
        y_title = titles[1]
        if options.do_unrolling and is_2d:
          if options.norm_bins: y_title = titles2d[0][1]
          else: y_title = titles2d[0][1]
          y_var_titles = titles2d[1]
    else: y_title = options.y_title
    scheme = options.channel
    if compare_w_shapes: scheme = 'w_shape'
    if compare_qcd_shapes: scheme = 'qcd_shape'
    if options.scheme != "": scheme = options.scheme
    FF = options.method==17 or options.method==18
    if options.do_unrolling and is_2d:
        auto_blind=False
        plotting.HTTPlotUnrolled(nodename,
        plot_file,
        options.signal_scale,
        options.draw_signal_mass,
        FF,
        options.norm_bins,
        options.channel,
        options.blind,
        options.x_blind_min,
        options.x_blind_max,
        auto_blind,
        options.ratio,
        options.log_y,
        options.log_x,
        options.ratio_range,
        options.custom_x_range,
        options.x_axis_min,
        options.x_axis_max,
        options.custom_y_range,
        options.y_axis_max,
        options.y_axis_min,
        x_title,
        y_title,
        options.extra_pad,
        options.do_custom_uncerts,
        options.add_stat_to_syst,
        options.add_flat_uncert,
        options.uncert_title,
        options.lumi,
        plot_name,
        custom_uncerts_up_name,
        custom_uncerts_down_name,
        scheme,
        options.cat,
        x_lines,
        [y_labels,y_var_titles],
        options.embedding
        )
    elif scheme != 'signal':
      plotting.HTTPlot(nodename,
        plot_file,
        options.signal_scale,
        options.draw_signal_mass,
        FF,
        options.norm_bins,
        options.channel,
        options.blind,
        options.x_blind_min,
        options.x_blind_max,
        options.ratio,
        options.log_y,
        options.log_x,
        options.ratio_range,
        options.custom_x_range,
        options.x_axis_min,
        options.x_axis_max,
        options.custom_y_range,
        options.y_axis_max,
        options.y_axis_min,
        x_title,
        y_title,
        options.extra_pad,
        options.signal_scheme,
        options.do_custom_uncerts,
        options.add_stat_to_syst,
        options.add_flat_uncert,
        options.uncert_title,
        options.lumi,
        plot_name,
        custom_uncerts_up_name,
        custom_uncerts_down_name,
        scheme,
        options.embedding,
        options.vbf_background,
        options.split_sm_scheme,
        options.ggh_scheme
        )
    else:
      plotting.HTTPlotSignal(nodename,
        plot_file,
        options.signal_scale,
        options.draw_signal_mass,
        options.norm_bins,
        options.channel,
        options.blind,
        options.x_blind_min,
        options.x_blind_max,
        options.ratio,
        options.log_y,
        options.log_x,
        options.ratio_range,
        options.custom_x_range,
        options.x_axis_min,
        options.x_axis_max,
        options.custom_y_range,
        options.y_axis_max,
        options.y_axis_min,
        x_title,
        y_title,
        options.extra_pad,
        options.signal_scheme,
        options.do_custom_uncerts,
        options.add_stat_to_syst,
        options.add_flat_uncert,
        options.uncert_title,
        options.lumi,
        plot_name,
        custom_uncerts_up_name,
        custom_uncerts_down_name
        )

   # plotting.SoverBPlot(nodename,
   #          plot_file,
   #          options.channel,
   #          options.log_y,
   #          options.log_x,
   #          options.custom_x_range,
   #          options.x_axis_max,
   #          options.x_axis_min,
   #          options.custom_y_range,
   #          options.y_axis_max,
   #          options.y_axis_min,
   #          x_title,
   #          options.extra_pad,
   #          plot_name+'_soverb')

   # hists = [plot_file.Get(nodename+"/bbH-LO700"), plot_file.Get(nodename+"/bbH700") ]
   # plotting.CompareHists(hists,
   #          ['Pythia','amc@NLO'],
   #          "bb#phi 700",
   #          options.ratio,
   #          options.log_y,
   #          options.log_x,
   #          options.ratio_range,
   #          options.custom_x_range,
   #          options.x_axis_max,
   #          options.x_axis_min,
   #          options.custom_y_range,
   #          options.y_axis_max,
   #          options.y_axis_min,
   #          x_title,
   #          y_title,
   #          options.extra_pad,
   #          False,
   #          plot_name,
   #          "#mu#tau_{h}")

#norm signal yields on datacards to 1pb AFTER plotting
outfile =  ROOT.TFile(output_name, 'UPDATE')
for add_name in add_names:
    if options.era not in ["smsummer16",'cpsummer16']: NormSignals(outfile,add_name)

# for smsummer16 need to ad WplusH and WminusH templates into one
if options.era in ["smsummer16",'cpsummer16']:
  outfile.cd(nodename)
  directory = outfile.Get(nodename)
  hists_to_add = []
  for key in directory.GetListOfKeys():
    hist_name = key.GetName()
    if 'WminusH' in hist_name:
      hist_to_add_name = hist_name.replace('minus', 'plus')
      hist = directory.Get(hist_name).Clone()
      hist_to_add = directory.Get(hist_to_add_name).Clone()
      hist.Add(hist_to_add)
      hist.SetName(hist_name.replace('minus',''))
      hists_to_add.append(hist)
  for hist in hists_to_add: hist.Write()

outfile.Close()


