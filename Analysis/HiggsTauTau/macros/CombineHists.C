TH2D* DrawDiTauHist(TString filename){

    TFile* f = TFile::Open(filename);
    TTree* HLT_trigger_ntuple = (TTree*) f->Get("HLT_trigger_ntuple");
    
    auto h = new TH2D("h","h", 5, 100, 500, 5, 100, 500);

    TCut offline = "jdeta>2.5 & jpt_1>30 & jpt_2>30 & pt_tt>100 & mva_olddm_medium_1>0.5 & mva_olddm_medium_2>0.5";
    TCut diTau = "trg_doubletau";

    HLT_trigger_ntuple->Draw("m_vis >> h",  diTau && offline);

    return h;
}

TH2D* DrawVBFHist(TString filename){

    TFile* f = TFile::Open(filename);
    TTree* HLT_trigger_ntuple = (TTree*) f->Get("HLT_trigger_ntuple");
    
    auto h = new TH2D("h","h", 100, 0, 2500, 100, 0, 2500);

    TCut offline = "jdeta>2.5 & jpt_1>30 & jpt_2>30 & pt_tt>100 & mva_olddm_medium_1>0.5 & mva_olddm_medium_2>0.5";
    TCut VBF = "trg_VBF";

    HLT_trigger_ntuple->Draw("m_vis >> h",  VBF && offline);

    return h;
}

void CombineHists(){

    THStack* hs = new THStack("hs","");

    TCanvas* c1 = new TCanvas();
    c1->SetLogy();

    TH2D* h1 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/2017Dec07_MC_92X_VBFHToTauTau_tt_0.root"));
    Double_t norm_VBF = 0.2371/2933672.;
    h1->Scale(norm_VBF);
    h1->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h1->GetYaxis()->SetTitle("Events");
    h1->SetTitle("");
    h1->SetFillColor(kRed);

    /* hs->Add(h1); */

    TH2D* h2 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY1Jets/2017Dec07_MC_92X_DY1JetsToLL_tt_0.root"));
    Double_t norm_DY1 = (1012.0/4963.0)*5765.4/66005667.;
    h2->Scale(norm_DY1);
    h2->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h2->GetYaxis()->SetTitle("Events");
    h2->SetAxisRange(0.,2500.,"X");
    h2->SetTitle("");
    h2->SetFillColor(kBlue);

    hs->Add(h2);

    TH2D* h3 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY2Jets/2017Dec07_MC_92X_DY2JetsToLL_tt_0.root"));
    Double_t norm_DY2 = (334.7/4963.0)*5765.4/45414763.;
    h3->Scale(norm_DY2);
    h3->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h3->GetYaxis()->SetTitle("Events");
    h3->SetTitle("");
    h3->SetFillColor(kBlack);

    hs->Add(h3);

    TH2D* h4 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY3Jets/2017Dec07_MC_92X_DY3JetsToLL_tt_0.root"));
    Double_t norm_DY3 = (102.3/4963.0)*5765.4/5218008.;
    h4->Scale(norm_DY3);
    h4->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h4->GetYaxis()->SetTitle("Events");
    h4->SetTitle("");
    h4->SetFillColor(kGreen);

    hs->Add(h4);

    TH2D* h5 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY4Jets/2017Dec07_MC_92X_DY4JetsToLL_tt_0.root"));
    Double_t norm_DY4 = (54.52/4963.0)*5765.4/17338269.;
    h5->Scale(norm_DY4);
    h5->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h5->GetYaxis()->SetTitle("Events");
    h5->SetTitle("");
    h5->SetFillColor(kGreen);

    hs->Add(h5);

    hs->Draw();

    /* TH2D* sum = new TH2D("sum","sum", 5, 100, 2500, 5, 100, 2500); */


    /* TList *histos = hs->GetHists(); */
    /* TIter next(histos); */
    /* TH2D* hist; */
    /* while ((hist =(TH2D*)next())) { */
    /*     cout << "Adding " << hist->GetName() << endl; */
    /*     sum->Add(hist); */
    /* } */

    /* sum->Draw(); */

    
    /* hs_final->Add(h1); */
    /* hs_final->Add(sum); */
    /* hs_final->Draw("nostack"); */

    TLatex* txt = new TLatex();
    txt->SetTextFont(42);
    txt->SetTextAlign(11);
    txt->DrawLatexNDC(c1->GetLeftMargin(),1.01-c1->GetTopMargin(),"#bf{CMS} #it{Simulation Preliminary}");

    c1->SaveAs("combined_trgVBF.pdf");
}
