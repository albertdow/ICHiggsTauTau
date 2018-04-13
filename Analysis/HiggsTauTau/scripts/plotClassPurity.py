#!/usr/bin/env python
import ROOT as R
import numpy as np
import pandas as pd
import UserCode.ICHiggsTauTau.plotting as plot
import os
import argparse

# Boilerplate
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(R.kTRUE)
R.TH1.AddDirectory(0)
plot.ModTDRStyle()


parser = argparse.ArgumentParser()

parser.add_argument(
    '--cat', default='ztt', help='Input class')
parser.add_argument(
    '--channel', default='mt', help='Input channel')
parser.add_argument(
    '--training', default='powheg', help='Input training')
parser.add_argument(
    '--output', '-o', default='purity', help="""Name of the output
    plot without file extension""")
parser.add_argument('--title', default='Muon ID Efficiency')
parser.add_argument('--y-range', default='0,1')
parser.add_argument('--ratio-y-range', default='0.92,1.08')
parser.add_argument('--x-title', default='mva_score')
parser.add_argument('--ratio-to', default=None, type=int)
parser.add_argument('--plot-dir', '-p', default='./')
parser.add_argument('--label_pos', default=1)
args = parser.parse_args()

if args.plot_dir != '':
    os.system('mkdir -p {}'.format(args.plot_dir))

latex = R.TLatex()
latex.SetNDC()

hnames = []
hists = dict()
process = ['total_bkg','ggH_htt125','ggHsm_htt125','qqH_htt125','ZTT','ZLL','QCD','TT','W']
for index, proc in enumerate(process):
    hists[proc] = R.TH1D('{}'.format(proc),'{}'.format(proc),10,0,1)

file = R.TFile('output/datacard_mva_score_cpsm_Apr06_1_{0}_{0}_{1}_{2}_2016.root'
        .format(args.training, args.cat, args.channel))
directory = file.GetDirectory('{}_{}_{}'.format(args.channel, args.training, args.cat))
for key in directory.GetListOfKeys():
    h = key.ReadObj()
    if h.ClassName() == 'TH1D':
        hnames.append(h.GetName())
        if h.GetName() in process:
            hists[h.GetName()] = h.Clone()


canv = R.TCanvas()

stack = R.THStack()

if args.ratio_to is not None:
    pads = plot.TwoPadSplit(0.30, 0.01, 0.01)
else:
    pads = plot.OnePad()

# if args.label_pos == 1:
#     text = R.TPaveText(0.55, 0.37, 0.9, 0.50, 'NDC')
#     legend = R.TLegend(0.18, 0.37, 0.5, 0.50, '', 'NDC')
# else:
#     text = R.TPaveText(0.55, 0.67, 0.9, 0.80, 'NDC')
#     legend = R.TLegend(0.18, 0.67, 0.5, 0.80, '', 'NDC')

for proc in process:
    if proc != 'total_bkg':
        hists[proc].Divide(hists['total_bkg'])

# signals
hists['ggH_htt125'].SetFillColor(R.TColor.GetColor(20,200,20))
hists['ggHsm_htt125'].SetFillColor(R.TColor.GetColor(20,200,20))

hists['qqH_htt125'].SetFillColor(R.TColor.GetColor(51,51,255))

# backgrounds
hists['ZTT'].SetFillColor(R.TColor.GetColor(248,206,104))

hists['ZLL'].SetFillColor(R.TColor.GetColor(100,192,232))

hists['QCD'].SetFillColor(R.TColor.GetColor(250,202,255))

hists['W'].SetFillColor(R.TColor.GetColor(222,90,106))

hists['TT'].SetFillColor(R.TColor.GetColor(155,152,204))


if args.training == 'powheg':
    stack.Add(hists['ggH_htt125'])
else:
    stack.Add(hists['ggHsm_htt125'])

stack.Add(hists['qqH_htt125'])
if args.cat == 'ztt':
    stack.Add(hists['ZTT'])
if args.cat == 'zll':
    stack.Add(hists['ZLL'])
if args.cat == 'qcd':
    stack.Add(hists['QCD'])
if args.cat == 'tt':
    stack.Add(hists['TT'])
if args.cat == 'w':
    stack.Add(hists['W'])
stack.Draw('hist')
R.gPad.SetLogy()

axis = plot.GetAxisHist(pads[0])
axis.GetYaxis().SetTitle('Events / Total Bkg')
axis.GetXaxis().SetTitle(args.x_title)
axis.GetYaxis().SetRange(0,1)
pads[0].SetGrid(1, 1)
latex.SetTextSize(0.04)

# text.AddText(args.title)
# text.AddText(bin_label)
# text.SetTextAlign(13)
# text.SetBorderSize(0)
# text.Draw()
# legend.Draw()

plot.DrawCMSLogo(pads[0], 'CMS', 'Preliminary', 0, 0.16, 0.035, 1.2, cmsTextSize=0.9)
plot.DrawTitle(pads[0], '35.9 fb^{-1} (13 TeV)', 3)

outname = '{}_{}_{}_{}'.format(args.output, args.channel, args.training, args.cat)

canv.Print('{}/{}.png'.format(args.plot_dir, outname))
canv.Print('{}/{}.pdf'.format(args.plot_dir, outname))
