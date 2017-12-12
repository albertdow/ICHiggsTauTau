TH1D* DrawVBFHist(TString filename){

    TFile* f = TFile::Open(filename);
    TTree* ntuple = (TTree*) f->Get("ntuple");
    
    TH1D* h = new TH1D("h","h", 15, 0, 150);
    h->SetStats(0);
    gStyle->SetHistLineWidth(0);

    TCut offline = "mjj>500 & jdeta>3.5 & jpt_1>30 & jpt_2>30 & pt_tt>100 & mva_olddm_medium_1>0.5 & mva_olddm_medium_2>0.5 & antiele_1 & antiele_2 & antimu_1 & antimu_2";
    TCut VBF = "trg_VBF";

    ntuple->Draw("m_vis >> h",  VBF && offline);

    return h;
}

void CombineVBFHistsWithRatio(){

    gStyle->SetHistLineWidth(0);

    TCanvas* c1 = new TCanvas("c1", "c1", 1300, 1300);;
    c1->SetLogy();


    // do the S/B plot

    TH1D* h1 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/2017Dec07_MC_92X_VBFHToTauTau_tt_0.root"));
    Double_t norm_VBF = (0.2371)/2933672.;
    h1->Scale(norm_VBF);
    /* h1->GetXaxis()->SetTitle("m_{visible} (GeV)"); */
    /* h1->GetYaxis()->SetTitle("Events"); */
    h1->SetTitle("");
    h1->SetFillColor(kBlue+1);


    TH1D* h2 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY1Jets/2017Dec07_MC_92X_DY1JetsToLL_tt_0.root"));
    Double_t norm_DY1 = (1012.0/4963.0)*5765.4/66005667.;
    h2->Scale(norm_DY1);
    /* h2->GetXaxis()->SetTitle("m_{visible} (GeV)"); */
    /* h2->GetYaxis()->SetTitle("Events"); */
    h2->SetTitle("");


    TH1D* h3 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY2Jets/2017Dec07_MC_92X_DY2JetsToLL_tt_0.root"));
    Double_t norm_DY2 = (334.7/4963.0)*5765.4/45414763.;
    h3->Scale(norm_DY2);
    /* h3->GetXaxis()->SetTitle("m_{visible} (GeV)"); */
    /* h3->GetYaxis()->SetTitle("Events"); */
    h3->SetTitle("");

    h3->Add(h2);

    TH1D* h4 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY3Jets/2017Dec07_MC_92X_DY3JetsToLL_tt_0.root"));
    Double_t norm_DY3 = (102.3/4963.0)*5765.4/5218008.;
    h4->Scale(norm_DY3);
    /* h4->GetXaxis()->SetTitle("m_{visible} (GeV)"); */
    /* h4->GetYaxis()->SetTitle("Events"); */
    h4->SetTitle("");

    h4->Add(h3);

    TH1D* h5 = DrawVBFHist(TString("/vols/cms/akd116/triggerStudies/2017Dec07_MC_92X/DY4Jets/2017Dec07_MC_92X_DY4JetsToLL_tt_0.root"));
    Double_t norm_DY4 = (54.52/4963.0)*5765.4/17338269.;
    h5->Scale(norm_DY4);
    /* h5->GetXaxis()->SetTitle("m_{visible} (GeV)"); */
    /* h5->GetYaxis()->SetTitle("Events"); */
    h5->SetTitle("");
    h5->SetFillColor(kOrange+1);

    h5->Add(h4);


    TPad* pad1 = new TPad("pad1","pad1",0,0.3,1,1.0);
    pad1->SetBottomMargin(0);
    pad1->SetLogy();
    pad1->Draw();
    pad1->cd();


    THStack* hs = new THStack;

    Double_t norm_lumi = 30000;
    h1->Scale(norm_lumi);
    h5->Scale(norm_lumi);

    hs->Add(h1);
    hs->Add(h5);
    hs->Draw();
    hs->GetXaxis()->SetTitle("");

    hs->GetYaxis()->SetTitle("Events");
    hs->GetYaxis()->SetTitleOffset(1.05);
    hs->GetYaxis()->SetTitleSize(30);
    hs->GetYaxis()->SetTitleFont(43);

    // legend for the top pad
    TLegend* leg = new TLegend(0.7,0.7,0.85,0.85);
    leg->SetBorderSize(0);
    leg->AddEntry(h1,"qqH #rightarrow #tau_{h} #tau_{h}");
    leg->AddEntry(h5,"Z #rightarrow #tau_{h} #tau_{h}");
    leg->Draw();

    // do the ratio plot

    // do sqrt (B)
    //
    TH1D* h_sqrt = new TH1D("h_sqrt","h_sqrt",15,0,150);
    Int_t nbinsx = h5->GetXaxis()->GetNbins();
    for (int i = 0; i <= nbinsx+1; i++) {
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
    h_ratio->SetMarkerSize(2);
    h_ratio->SetStats(0);
    h_ratio->SetMinimum(0);
    h_ratio->SetMaximum(1.6);
    h_ratio->Draw("phist");

    h_ratio->GetYaxis()->SetTitle("S/#sqrt{B} ");
    h_ratio->GetYaxis()->SetNdivisions(505);
    h_ratio->GetYaxis()->SetTitleSize(30);
    h_ratio->GetYaxis()->SetTitleFont(43);
    h_ratio->GetYaxis()->SetTitleOffset(1.35);
    h_ratio->GetYaxis()->SetLabelFont(43); // Absolute font size in pixel (precision 3)
    h_ratio->GetYaxis()->SetLabelSize(25);
    
    h_ratio->GetXaxis()->SetTitle("m_{visible} (GeV)");
    h_ratio->GetXaxis()->SetTitleSize(30);
    h_ratio->GetXaxis()->SetTitleFont(43);
    h_ratio->GetXaxis()->SetTitleOffset(4.);
    h_ratio->GetXaxis()->SetLabelFont(43); // Absolute font size in pixel (precision 3)
    h_ratio->GetXaxis()->SetLabelSize(25);


    c1->cd();
    TLatex* txt = new TLatex();
    txt->SetTextFont(42);
    txt->SetTextSize(0.035);
    txt->SetTextAlign(11);
    txt->DrawLatexNDC(c1->GetLeftMargin(),1.035-c1->GetTopMargin(),"#bf{CMS} #it{Simulation Preliminary}");
    TLatex* txt2 = new TLatex();
    txt2->SetTextFont(42);
    txt2->SetTextSize(0.025);
    txt2->SetTextAlign(11);
    txt2->DrawLatexNDC(0.85-c1->GetLeftMargin(),1.035-c1->GetTopMargin(),"30fb^{-1} (13 TeV)");

    c1->SaveAs("TEST_trgVBF.pdf");
}
