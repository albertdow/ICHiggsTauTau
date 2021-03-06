#include <vector>
#include <string>
#include <iostream>
#include "TFile.h"
#include "TTree.h"
#include "TGraph.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TLine.h"
#include "TLegend.h"
#include "TString.h"
#include "TLatex.h"

#include "Core/interface/Plotting.h"
#include "Core/interface/Plotting_Style.h"

TGraph ExtractGraph(TTree *t, double & bestFit) {
  TGraph g(t->GetEntries());
  float r = 0;
  float deltaNLL = 0;
  t->SetBranchAddress("r", &r);
  t->SetBranchAddress("deltaNLL", &deltaNLL);
  for (unsigned i = 0; i < t->GetEntries(); ++i) {
    t->GetEntry(i);
    if (deltaNLL == 0) bestFit = r;
    g.SetPoint(i, r, 2.0*deltaNLL);
  }
  g.Sort();
  return g;
}

std::vector<double> GetCrossings(TGraph const& g, double cross) {
  std::vector<double> result;
  unsigned n = g.GetN();
  double x1 = 0;
  double y1 = 0;
  double x2 = 0;
  double y2 = 0;
  for (unsigned i = 0; i < (n-1); ++i) {
    g.GetPoint(i, x1, y1);
    g.GetPoint(i+1, x2, y2);
    if ( (y2-cross)*(y1-cross) < 0.0 ) {
      double m = (y2-y1)/(x2-x1);
      double c = (y1 - m * x1);
      double xc = (cross - c) / m;
      result.push_back(xc);
      std::cout << "Crossing at " << xc << std::endl;
    }
  }
  return result;
}

struct Scan {
  std::string file;
  std::string label;
  int color;
  TGraph *gr;
};

int main() {
  ModTDRStyle();

  std::vector<Scan> scans;
  //scans.push_back({"higgsCombinefullScan.MultiDimFit.mH125.root", "with syst.", 1, nullptr});
  //scans.push_back({"higgsCombinefastScan.MultiDimFit.mH125.root", "no syst.", 32, nullptr});
  //scans.push_back({"higgsCombinenoBBBScan.MultiDimFit.mH125.root", "no bbb syst.", 38, nullptr});
  
  //  scans.push_back({"thesis/higgsCombineFullScan.MultiDimFit.mH125.root", "Stat+Syst+Theory", 1, nullptr});
  //scans.push_back({"thesis/higgsCombineStatAndExp.MultiDimFit.mH125.root", "Stat+Syst", kAzure-9, nullptr});
  //scans.push_back({"thesis/higgsCombineStatOnly.MultiDimFit.mH125.root", "Stat Only", kBlue+1, nullptr});
  //scans.push_back({"thesis/higgsCombineStatAndTh.MultiDimFit.mH125.root", "Stat+Theory", 39, nullptr});
  scans.push_back({"/vols/cms04/pjd12/invcmssws/CMSSW_6_1_1/src/HiggsAnalysis/CombinedLimit/likelihoodscan/higgsCombinecomb.MultiDimFit.mH125.root", "Parked Comb", kRed, nullptr});
  scans.push_back({"/vols/cms04/pjd12/invcmssws/CMSSW_6_1_1/src/HiggsAnalysis/CombinedLimit/likelihoodscan/higgsCombinepromptcomb.MultiDimFit.mH125.root", "Prompt Comb", kRed+3, nullptr});
  //  scans.push_back({"/vols/cms04/pjd12/invcmssws/CMSSW_6_1_1/src/HiggsAnalysis/CombinedLimit/likelihoodscan/higgsCombinevbf.MultiDimFit.mH125.root", "ParkedVBF", kBlue, nullptr});
  //  scans.push_back({"/vols/cms04/pjd12/invcmssws/CMSSW_6_1_1/src/HiggsAnalysis/CombinedLimit/likelihoodscan/higgsCombinepromptvbf.MultiDimFit.mH125.root", "Prompt VBF", kBlue+3, nullptr});
  //  scans.push_back({"/vols/cms04/pjd12/invcmssws/CMSSW_6_1_1/src/HiggsAnalysis/CombinedLimit/likelihoodscan/higgsCombinezh.MultiDimFit.mH125.root", "ZH", kGreen+3, nullptr});
  
  //scans.push_back({"thesis/higgsCombineStatAndTh.MultiDimFit.mH125.root", "Stat+Theory", 39, nullptr});
  TCanvas c1("canvas","canvas");

  std::vector<TLine *> lines;

  TLegend *leg = new TLegend(0.65,0.75,0.9,0.9,"","brNDC");
  //TLegend *leg = new TLegend(0.37,0.65,0.73,0.9,"","brNDC");

  unsigned counter = 0;
  for (auto & sc : scans) {
    TFile f1(sc.file.c_str());
    TTree *t1 = dynamic_cast<TTree*>(f1.Get("limit"));
    double best1 = 0.0;
    sc.gr = new TGraph(ExtractGraph(t1, best1));
    auto x1 = GetCrossings(*(sc.gr), 1.0);
    auto x2 = GetCrossings(*(sc.gr), 4.0);
    TString res;

    if (x1.size() == 2) {
      double err = (x1[1]-x1[0])/2.0;
      std::cout << "Best fit is: " << best1 << " +/- " << err << std::endl;
      lines.push_back(new TLine(x1[0],0,x1[0],1.0));
      lines.back()->SetLineColor(sc.color);
      lines.back()->SetLineWidth(2);
      lines.push_back(new TLine(x1[1],0,x1[1],1.0));
      lines.back()->SetLineColor(sc.color);
      lines.back()->SetLineWidth(2);
      res = TString::Format("%.2f#pm%.2f",best1,err);
    }
    else{
      lines.push_back(new TLine(x1[0],0,x1[0],1.0));
      lines.back()->SetLineColor(sc.color);
      lines.back()->SetLineWidth(2);
    }

    if (x2.size() == 2) {
      double err = (x2[1]-x2[0])/2.0;
      std::cout << "Best fit is: " << best1 << " +/- " << err << std::endl;
      lines.push_back(new TLine(x2[0],0,x2[0],4.0));
      lines.back()->SetLineColor(sc.color);
      lines.back()->SetLineWidth(2);
      lines.push_back(new TLine(x2[1],0,x2[1],4.0));
      lines.back()->SetLineColor(sc.color);
      lines.back()->SetLineWidth(2);
      res = TString::Format("%.2f#pm%.2f",best1,err);
    }
    else{
      lines.push_back(new TLine(x2[0],0,x2[0],4.0));
      lines.back()->SetLineColor(sc.color);
      lines.back()->SetLineWidth(2);
    }
    sc.gr->SetLineColor(sc.color);
    sc.gr->SetLineWidth(3);
    sc.gr->Draw(counter ? "LSAME" : "AL");
    TString leg_text = sc.label;//"#splitline{"+sc.label+"}{"+res+"}";
    leg->AddEntry(sc.gr, leg_text, "L");
    counter++;
  }
  // c1.cd();
  // // g1.Print();
  // g1.SetLineColor(1);
  // g1.SetLineWidth(2);
  // // g1.SetMarkerColor(7);
  // g1.Draw("AC");
  scans[0].gr->SetMaximum(9);
  scans[0].gr->SetMinimum(0.);
  scans[0].gr->GetXaxis()->SetRangeUser(0., 1.0);
  scans[0].gr->GetXaxis()->SetTitle("BR_{inv}");

  //scans[0].gr->SetMaximum(1.9);
  //scans[0].gr->GetXaxis()->SetRangeUser(0., 1.4);
  //scans[0].gr->GetXaxis()->SetTitle("Signal Strength, #mu");
  scans[0].gr->GetYaxis()->SetTitle("-2 #Delta ln L");
  scans[0].gr->GetXaxis()->SetTitleFont(62);
  scans[0].gr->GetYaxis()->SetTitleFont(62);
  leg->SetBorderSize(1);
  leg->SetTextFont(42);
  leg->SetTextSize(0.03);
  leg->SetLineColor(0);
  leg->SetLineStyle(1);
  leg->SetLineWidth(1);
  leg->SetFillColor(0);
  leg->SetFillStyle(1001);
  leg->Draw();
  lines.push_back(new TLine(0.,1,1.0,1));
  lines.back()->SetLineColor(2);
  lines.push_back(new TLine(0.,4,1.0,4));
  lines.back()->SetLineColor(2);
  for (auto l : lines) l->Draw();
  TLatex lat = TLatex();
  lat.SetNDC();
  lat.SetTextSize(0.04);                                                                                                                                    
  lat.SetTextFont(42);
  
  TLatex lat2 = TLatex();
  lat2.SetNDC();
  lat2.SetTextSize(0.03);
  lat2.SetTextFont(42);
  
  lat.DrawLatex(0.2,0.85,"CMS Unpublished");
  lat.DrawLatex(0.2,0.78,"Combination of VBF and");
  lat.DrawLatex(0.2,0.73,"ZH, H #rightarrow invisible");

 
  lat2.DrawLatex(0.2,0.665,"#sqrt{s} = 8 TeV (VBF + ZH)");
  lat2.DrawLatex(0.2,0.62,"L = 18.9-19.7 fb^{-1}");
  
  lat2.DrawLatex(0.2,0.555,"#sqrt{s} = 7 TeV (Z(ll)H only)");
  lat2.DrawLatex(0.2,0.515,"L = 4.9 fb^{-1}");

  c1.Update();
  c1.SaveAs("scan.pdf");
  return 0;
}
