TEfficiency* DrawEffs(TString filename)
{
    TFile* f = TFile::Open(filename);
    TTree* HLT_trigger_ntuple = (TTree*) f->Get("HLT_trigger_ntuple");
    // book the historams
    //TH1::SetDefaultSumw2(true);
    double xbins[18]={0,100,200,300,400,500,600,700,800,900,1000,1200,1400,1600,1800,2000};
    TH1D* h_num = new TH1D("h_num", "Numerator Count;Jet variable;Numerator Count"    , 15, xbins);
    TH1D* h_den = new TH1D("h_den", "Denominator Count;Jet variable;Denominator Count", 15, xbins);
    TEfficiency* pEff = 0;

    // define selection
    TCut offline = "mjj>400 & xclean_jpt_1>145 & xclean_jpt_2>55";

    TCut VBF = "trg_VBF";
    TCut DiTau = "trg_doubletau"; 

    // fill the histograms with TTree::Draw
    HLT_trigger_ntuple->Draw("mjj>>h_num", VBF && DiTau && offline);
    HLT_trigger_ntuple->Draw("mjj>>h_den", DiTau && offline);

    if(TEfficiency::CheckConsistency(*h_num,*h_den)){
        pEff = new TEfficiency(*h_num,*h_den);
        //pEff->Draw("same");
        //gPad->Update();
        pEff->SetTitle(";m_{jj} (GeV);Efficiency");
    }

    return pEff;
}

auto effErf = [](double* x, double* p) {
      return (TMath::Erf((x[0] - p[0]) / p[1]) + 1) / 2. * p[2];
   };

void effDataMCmjj(){
    TCanvas* c1 = new TCanvas();
    //TEfficiency * eff1 = DrawEffs(TString("/vols/build/cms/akd116/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/output/TauTriggerStudy_17Oct17_VBFHToTauTau_tt_0.root"));
    //TEfficiency * eff1 = DrawEffs(TString("/vols/build/cms/akd116/triggerStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/output/VBF_HToTauTau_M-125_tt_0.root"));
    //TEfficiency * eff1 = DrawEffs(TString("/vols/build/cms/akd116/triggerStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/output/21Nov17_MC_VBF_92X_VBFTaus20_Taus35_VBFHToTauTau_M-125_tt_0.root"));
    //TEfficiency * eff1 = DrawEffs(TString("/vols/build/cms/akd116/triggerStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/output/ModifiedVBF2and3_92X_VBF_HToTauTau_M-125_tt_0.root"));
    //TEfficiency * eff1 = DrawEffs(TString("/vols/build/cms/akd116/triggerStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/output/TEST_VBF2and3_92X_VBF_HToTauTau_M-125_tt_0.root"));
    TEfficiency * eff1 = DrawEffs(TString("/vols/build/cms/akd116/triggerStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/output/TEST_VBF2and3_withThreeObjs_92X_VBF_HToTauTau_M-125_tt_0.root"));

    TEfficiency * eff2 = DrawEffs(TString("/vols/build/cms/akd116/triggerStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/output/21Nov17_Data_VBF_Taus_Cert_294927-306460_TauD-F.root"));

    eff1->SetLineColor(kBlue);
    eff2->SetLineColor(kRed);
    eff1->Draw();
    eff2->Draw("same");

    TF1* myErf1 = new TF1("myErf1", effErf,500., 2000., 3);
    myErf1->SetParameter(0, 700.);
    myErf1->SetParameter(1, 30.);
    myErf1->SetParameter(2, 1.);

    eff1->Fit(myErf1);
    myErf1->SetLineColor(kBlue);
    myErf1->Draw("same");
    
    TF1* myErf2 = new TF1("myErf2", effErf, 500., 2000., 3);
    myErf2->SetParameter(0, 700.);
    myErf2->SetParameter(1, 50.);
    myErf2->SetParameter(2, 1.);

    eff2->Fit(myErf2);
    myErf2->SetLineColor(kRed);
    myErf2->Draw("same");

    TLegend* leg = new TLegend(0.7,0.2,0.85,0.3);
    leg->SetBorderSize(0);
    leg->AddEntry(myErf1,"MC");
    leg->AddEntry(myErf2,"Data");
    leg->Draw();

    TLatex* txt = new TLatex();
    txt->SetTextFont(42);
    txt->SetTextAlign(11);
    txt->DrawLatexNDC(c1->GetLeftMargin(),1.01-c1->GetTopMargin(),"#bf{CMS} #it{Preliminary}");
    
    std::cout<<myErf1->GetParameter(2)<<std::endl; 
    std::cout<<myErf2->GetParameter(2)<<std::endl; 
    c1->SaveAs("effDataMCmjj_xclean_VBF2.pdf");
}
