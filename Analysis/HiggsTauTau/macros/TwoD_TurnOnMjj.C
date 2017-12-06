void TwoD_TurnOnMjj() {
   
    // choose whether to run on Data or MC

    //filename = TString("/vols/cms/akd116/triggerStudies/2017Dec04_21Nov17_Data_VBF_Taus_Cert_294927-306460_TauD-F_tt_0.root");
    filename = TString("/vols/cms/akd116/triggerStudies/TEST_NEWOFFLINE_20Nov17_IC_18Nov17_MC_VBF2and3_Taus20_Tau40_92X_v2_VBFHToTauTau_tt_0.root");
    
    TFile* f = TFile::Open(filename);
    TTree* HLT_trigger_ntuple = (TTree*) f->Get("HLT_trigger_ntuple");
    
    auto h = new TH2D("h","h", 70, 0, 4000, 70, 0, 4000);

    // define selection
    TCut offline = "hlt_mjj>0 & offline_mjj>0 & xclean_jpt_1>145 & xclean_jpt_2>55 & mva_olddm_medium_1>0.5 & mva_olddm_medium_2>0.5";

    TCanvas* c1 = new TCanvas();
    HLT_trigger_ntuple->Draw("hlt_mjj:offline_mjj >> h", offline);
    gStyle->SetOptStat(0);
    gStyle->SetPalette(55);
    gStyle->SetNumberContours(255);
    h->Draw("colz");

    TLine * line = new TLine();
    line->SetLineStyle(7);
    line->DrawLine(0,0,4000,4000);

    h->GetXaxis()->SetTitle("Offline m_{jj} (GeV)");
    h->GetYaxis()->SetTitle("HLT m_{jj} (GeV)");
    h->GetYaxis()->SetTitleOffset(1.4);
    h->SetTitle("");

    TLatex* txt = new TLatex();
    txt->SetTextFont(42);
    txt->SetTextAlign(11);

    //txt->DrawLatexNDC(c1->GetLeftMargin(),1.01-c1->GetTopMargin(),"#bf{CMS} #it{Preliminary}");
    txt->DrawLatexNDC(c1->GetLeftMargin(),1.01-c1->GetTopMargin(),"#bf{CMS} #it{Simulation Preliminary}");

    //c1->SaveAs("2DmjjData.pdf");
    c1->SaveAs("2DmjjMC.pdf");
}
