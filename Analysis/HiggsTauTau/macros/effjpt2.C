{
    // book the historams
    //TH1::SetDefaultSumw2(true);
    double xbins[10]={0,20,40,60,80,100,120,140,160,200};
    TH1D* h_num = new TH1D("h_num", "Numerator Count;Jet variable;Numerator Count"    , 9, xbins);
    TH1D* h_den = new TH1D("h_den", "Denominator Count;Jet variable;Denominator Count", 9, xbins);
    TEfficiency* pEff = 0;

    // define selection
    TCut offline = "mjj>2000 & jpt_1>200";

    TCut VBF = "trg_VBF";
    TCut DiTau = "trg_doubletau"; 

    // fill the histograms with TTree::Draw
    HLT_trigger_ntuple->Draw("jpt_2>>h_num", VBF && DiTau && offline);
    HLT_trigger_ntuple->Draw("jpt_2>>h_den", DiTau && offline);

    if(TEfficiency::CheckConsistency(*h_num,*h_den)){
        pEff = new TEfficiency(*h_num,*h_den);
        pEff->Draw("AP");
        gPad->Update();
        pEff->SetTitle("my efficiency;Subleading Jet pT (GeV);#epsilon");
    }
        TCanvas c2("c2", "c2", 600, 600);
        h_num->Draw("hist");        

        TCanvas c3("c3", "c3", 600, 600);
        h_den->Draw("hist");
}
