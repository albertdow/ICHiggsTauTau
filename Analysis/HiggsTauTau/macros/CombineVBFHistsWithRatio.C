TH1D* DrawVBFHist(TString filename){

    TFile* f = TFile::Open(filename);
    TTree* HLT_trigger_ntuple = (TTree*) f->Get("HLT_trigger_ntuple");
    
    TH1D* h = new TH1D("h","h", 15, 0, 150);

    TCut offline = "mjj>500 & jdeta>3.5 & jpt_1>30 & jpt_2>30 & pt_tt>100 & mva_olddm_medium_1>0.5 & mva_olddm_medium_2>0.5 & antiele_1 & antiele_2 & antimu_1 & antimu_2";
    TCut VBF = "trg_VBF";

    HLT_trigger_ntuple->Draw("m_vis >> h",  VBF && offline);

    return h;
}

void CombineVBFHistsWithRatio(){

    TCanvas* c1 = new TCanvas;
    c1->SetLogy();


    // do the S/B plot

    TH1D* h1 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/2017Dec07_MC_92X_VBFHToTauTau_tt_0.root"));
    Double_t norm_VBF = (0.2371)/2933672.;
    h1->Scale(norm_VBF);
    h1->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h1->GetYaxis()->SetTitle("Events");
    h1->SetTitle("");
    h1->SetFillColor(kRed);


    TH1D* h2 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY1Jets/2017Dec07_MC_92X_DY1JetsToLL_tt_0.root"));
    Double_t norm_DY1 = (1012.0/4963.0)*5765.4/66005667.;
    h2->Scale(norm_DY1);
    h2->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h2->GetYaxis()->SetTitle("Events");
    h2->SetTitle("");
    h2->SetFillColor(kBlue);


    TH1D* h3 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY2Jets/2017Dec07_MC_92X_DY2JetsToLL_tt_0.root"));
    Double_t norm_DY2 = (334.7/4963.0)*5765.4/45414763.;
    h3->Scale(norm_DY2);
    h3->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h3->GetYaxis()->SetTitle("Events");
    h3->SetTitle("");
    h3->SetFillColor(kBlack);

    h3->Add(h2);

    TH1D* h4 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY3Jets/2017Dec07_MC_92X_DY3JetsToLL_tt_0.root"));
    Double_t norm_DY3 = (102.3/4963.0)*5765.4/5218008.;
    h4->Scale(norm_DY3);
    h4->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h4->GetYaxis()->SetTitle("Events");
    h4->SetTitle("");
    h4->SetFillColor(kGreen);

    h4->Add(h3);

    TH1D* h5 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY4Jets/2017Dec07_MC_92X_DY4JetsToLL_tt_0.root"));
    Double_t norm_DY4 = (54.52/4963.0)*5765.4/17338269.;
    h5->Scale(norm_DY4);
    h5->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h5->GetYaxis()->SetTitle("Events");
    h5->SetTitle("");
    h5->SetFillColor(kYellow);

    h5->Add(h4);


    TPad* pad1 = new TPad("pad1","pad1",0,0.3,1,1.0);
    pad1->SetBottomMargin(0);
    pad1->SetLogy();
    pad1->Draw();
    pad1->cd();

    THStack* hs = new THStack;
    hs->Add(h1);
    hs->Add(h5);
    hs->Draw();
    hs->GetXaxis()->SetTitle("m_{visible} (GeV)");
    hs->GetYaxis()->SetTitle("Events");

    // do the ratio plot
    Double_t norm_lumi = 30000;
    h1->Scale(norm_lumi);
    h5->Scale(norm_lumi);

    // do sqrt (B)
    //
    TH1D* h_sqrt = new TH1D("h_sqrt","h_sqrt",15,0,150);
    Int_t nbinsx = h5->GetXaxis()->GetNbins();
    for (int i = 0; i <= nbinsx; i++) {
        Double_t root = sqrt(h5->GetBinContent(i));
        h_sqrt->SetBinContent(i,root);
        cout<<"bin: "<< i << "\n Content: " << h5->GetBinContent(i) << "\n sqrt of content: " << h_sqrt << endl;
    }

    c1->cd();
    TPad* pad2 = new TPad("pad2","pad2",0,0.05,1,0.3);
    pad2->SetTopMargin(0);
    pad2->SetBottomMargin(0.2);
    pad2->SetGridx();
    pad2->Draw();
    pad2->cd();
    
    TH1D* h_ratio = (TH1D*) h1->Clone("h_ratio");
    h_ratio->Divide(h_sqrt);
    h_ratio->SetMarkerStyle(21);
    h_ratio->Draw("phist");

    c1->cd();
    TLatex* txt = new TLatex();
    txt->SetTextFont(42);
    txt->SetTextAlign(11);
    txt->DrawLatexNDC(c1->GetLeftMargin(),1.01-c1->GetTopMargin(),"#bf{CMS} #it{Simulation Preliminary}");

    c1->SaveAs("TEST_trgVBF.pdf");
}
