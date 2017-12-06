void TwoD_TurnOnJpt2(){

    //filename = TString("/vols/cms/akd116/triggerStudies/2017Dec04_21Nov17_Data_VBF_Taus_Cert_294927-306460_TauD-F_tt_0.root");
    filename = TString("/vols/cms/akd116/triggerStudies/TEST_NEWOFFLINE_20Nov17_IC_18Nov17_MC_VBF2and3_Taus20_Tau40_92X_v2_VBFHToTauTau_tt_0.root");
    TFile* f = TFile::Open(filename);
    TTree* HLT_trigger_ntuple = (TTree*) f->Get("HLT_trigger_ntuple");
    
    auto h = new TH2D("h","h", 50, 0, 300, 50, 0, 300);

    // define selection
    TCut offline = "hlt_jpt_2>0 & offline_jpt_2>0 & xclean_mjj>1000 & xclean_jpt_1>160 & mva_olddm_medium_1>0.5 & mva_olddm_medium_2>0.5";

    TCanvas* c1 = new TCanvas();
    HLT_trigger_ntuple->Draw("hlt_jpt_2:offline_jpt_2 >> h", offline);
    gStyle->SetOptStat(0);
    gStyle->SetPalette(55);
    gStyle->SetNumberContours(255);
    h->Draw("colz");

    TLine * line = new TLine();
    line->SetLineStyle(7);
    line->DrawLine(0,0,300,300);

    h->GetXaxis()->SetTitle("Offline Subleading Jet pT (GeV)");
    h->GetYaxis()->SetTitle("HLT Subleading Jet pT (GeV)");
    h->SetTitle("");

    TLatex* txt = new TLatex();
    txt->SetTextFont(42);
    txt->SetTextAlign(11);
    //txt->DrawLatexNDC(c1->GetLeftMargin(),1.01-c1->GetTopMargin(),"#bf{CMS} #it{Preliminary}");
    txt->DrawLatexNDC(c1->GetLeftMargin(),1.01-c1->GetTopMargin(),"#bf{CMS} #it{Simulation Preliminary}");

    //c1->SaveAs("2Djpt2.pdf");
    c1->SaveAs("2Djpt2MC.pdf");
}
