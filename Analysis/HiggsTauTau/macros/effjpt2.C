//{
//    // book the historams
//    //TH1::SetDefaultSumw2(true);
//    double xbins[11]={0,20,30,40,60,80,100,120,140,160,200};
//    TH1D* h_num = new TH1D("h_num", "Numerator Count;Jet variable;Numerator Count"    , 10, xbins);
//    TH1D* h_den = new TH1D("h_den", "Denominator Count;Jet variable;Denominator Count", 10, xbins);
//    TEfficiency* pEff = 0;
//
//    // define selection
//    TCut offline = "mjj>700 & jpt_1>150";
//
//    TCut VBF = "trg_VBF";
//    TCut DiTau = "trg_doubletau"; 
//
//    // fill the histograms with TTree::Draw
//    HLT_trigger_ntuple->Draw("jpt_2>>h_num", VBF && DiTau && offline);
//    HLT_trigger_ntuple->Draw("jpt_2>>h_den", DiTau && offline);
//
//    if(TEfficiency::CheckConsistency(*h_num,*h_den)){
//        pEff = new TEfficiency(*h_num,*h_den);
//        pEff->Draw("AP");
//        gPad->Update();
//        pEff->SetTitle("my efficiency;Subleading Jet pT (GeV);#epsilon");
//    }
//        TCanvas c2("c2", "c2", 600, 600);
//        h_num->Draw("hist");        
//
//        TCanvas c3("c3", "c3", 600, 600);
//        h_den->Draw("hist");
//}



TEfficiency* DrawEffs(TString filename)
{
    TFile* f = TFile::Open(filename);
    TTree* HLT_trigger_ntuple = (TTree*) f->Get("HLT_trigger_ntuple");
    // book the historams
    //TH1::SetDefaultSumw2(true);
    double xbins[11]={0,20,30,40,60,80,100,120,140,160,200};
    TH1D* h_num = new TH1D("h_num", "Numerator Count;Jet variable;Numerator Count"    , 10, xbins);
    TH1D* h_den = new TH1D("h_den", "Denominator Count;Jet variable;Denominator Count", 10, xbins);
    TEfficiency* pEff = 0;

    // define selection
    TCut offline = "mjj>800 & jpt_1>150 & mva_olddm_medium_1>0.5 & mva_olddm_medium_2>0.5";

    TCut VBF = "trg_VBF";
    TCut DiTau = "trg_doubletau"; 
    //TCut L1 = "VBFL1Passed";

    // fill the histograms with TTree::Draw
    HLT_trigger_ntuple->Draw("jpt_2>>h_num", VBF && DiTau && offline);
    HLT_trigger_ntuple->Draw("jpt_2>>h_den", DiTau && offline);

    if(TEfficiency::CheckConsistency(*h_num,*h_den)){
        pEff = new TEfficiency(*h_num,*h_den);
        //pEff->Draw("same");
        //gPad->Update();
        pEff->SetTitle(";Subleading Jet pT (GeV);Efficiency");
    }
    //TCanvas c2("c2", "c2", 600, 600);
    //h_num->Draw("hist");        

    //TCanvas c3("c3", "c3", 600, 600);
    //h_den->Draw("hist");

    return pEff;
}

auto effErf = [](double* x, double* p) {
      return (TMath::Erf((x[0] - p[0]) / p[1]) + 1) / 2. * p[2];
   };

void effjpt2(){
    TCanvas* c1 = new TCanvas();
    TEfficiency * eff1 = DrawEffs(TString("/vols/build/cms/akd116/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/output/TauTriggerStudy_TauD-E_302026-304508_tt_0.root"));
    TEfficiency * eff2 = DrawEffs(TString("/vols/build/cms/akd116/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/output/TauTriggerStudy_17Oct17_VBFHToTauTau_tt_0.root"));
    eff1->SetLineColor(kBlue);
    eff2->SetLineColor(kRed);
    eff2->Draw();
    eff1->Draw("same");

    TF1* myErf1 = new TF1("myErf1", effErf, 20., 200., 3);
    myErf1->SetParameter(0, 40.);
    myErf1->SetParameter(1, 5.);
    myErf1->SetParameter(2, 1.);

    eff1->Fit(myErf1);
    myErf1->SetLineColor(kBlue);
    myErf1->Draw("same");
    
    TF1* myErf2 = new TF1("myErf2", effErf, 20., 200., 3);
    myErf2->SetParameter(0, 40.);
    myErf2->SetParameter(1, 5.);
    myErf2->SetParameter(2, 1.);

    eff2->Fit(myErf2);
    myErf2->SetLineColor(kRed);
    myErf2->Draw("same");

    TLegend* leg = new TLegend(0.7,0.2,0.85,0.3);
    leg->SetBorderSize(0);
    leg->AddEntry(myErf1,"Data");
    leg->AddEntry(myErf2,"MC");
    leg->Draw();

    c1->SaveAs("effsjpt2.pdf");
}
