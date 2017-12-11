TH1D* DrawDiTauHist(TString filename){

    TFile* f = TFile::Open(filename);
    TTree* HLT_trigger_ntuple = (TTree*) f->Get("HLT_trigger_ntuple");
    
    TH1D* h = new TH1D("h","h", 15, 0, 150);

    TCut offline = "mjj>500 & jdeta>2.5 & jpt_1>30 & jpt_2>30 & pt_tt>100 & mva_olddm_medium_1>0.5 & mva_olddm_medium_2>0.5 & antiele_1 & antiele_2 & antimu_1 & antimu_2";
    TCut diTau = "trg_doubletau";

    HLT_trigger_ntuple->Draw("m_vis >> h",  diTau && offline);

    return h;
}
void CombineDiTauHists(){

    TCanvas* c1 = new TCanvas;
    c1->SetLogy();

    TH1D* h1 = DrawDiTauHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/2017Dec07_MC_92X_VBFHToTauTau_tt_0.root"));
    Double_t norm_VBF = 0.2371/2933672.;
    h1->Scale(norm_VBF);
    h1->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h1->GetYaxis()->SetTitle("Events");
    h1->SetTitle("");
    h1->SetFillColor(kRed);


    TH1D* h2 = DrawDiTauHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY1Jets/2017Dec07_MC_92X_DY1JetsToLL_tt_0.root"));
    Double_t norm_DY1 = (1012.0/4963.0)*5765.4/66005667.;
    h2->Scale(norm_DY1);
    h2->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h2->GetYaxis()->SetTitle("Events");
    h2->SetTitle("");
    h2->SetFillColor(kBlue);


    TH1D* h3 = DrawDiTauHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY2Jets/2017Dec07_MC_92X_DY2JetsToLL_tt_0.root"));
    Double_t norm_DY2 = (334.7/4963.0)*5765.4/45414763.;
    h3->Scale(norm_DY2);
    h3->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h3->GetYaxis()->SetTitle("Events");
    h3->SetTitle("");
    h3->SetFillColor(kBlack);

    h3->Add(h2);
/*     /1* hs->Add(h3); *1/ */

    TH1D* h4 = DrawDiTauHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY3Jets/2017Dec07_MC_92X_DY3JetsToLL_tt_0.root"));
    Double_t norm_DY3 = (102.3/4963.0)*5765.4/5218008.;
    h4->Scale(norm_DY3);
    h4->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h4->GetYaxis()->SetTitle("Events");
    h4->SetTitle("");
    h4->SetFillColor(kGreen);

    h4->Add(h3);
/*     /1* hs->Add(h4); *1/ */

    TH1D* h5 = DrawDiTauHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY4Jets/2017Dec07_MC_92X_DY4JetsToLL_tt_0.root"));
    Double_t norm_DY4 = (54.52/4963.0)*5765.4/17338269.;
    h5->Scale(norm_DY4);
    h5->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h5->GetYaxis()->SetTitle("Events");
    h5->SetTitle("");
    h5->SetFillColor(kYellow);

    h5->Add(h4);
    
    cout<<"entries in DY: "<<h5->Integral(-1,-1)<<endl;
    cout<<"entries in vbf: "<<h1->Integral(-1,-1)<<endl;
    THStack* hs = new THStack;
    hs->Add(h1);
    hs->Add(h5);
    hs->Draw();

    TLatex* txt = new TLatex();
    txt->SetTextFont(42);
    txt->SetTextAlign(11);
    txt->DrawLatexNDC(c1->GetLeftMargin(),1.01-c1->GetTopMargin(),"#bf{CMS} #it{Simulation Preliminary}");

    c1->SaveAs("combined_trgDiTau.pdf");
}
