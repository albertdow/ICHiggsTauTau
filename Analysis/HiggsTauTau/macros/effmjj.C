{
    // book the historams
    //TH1::SetDefaultSumw2(true);
    double xbins[12]={0,400,500,600,700,800,900,1000,1200,1400,1800,2200};
    TH1D* h_num = new TH1D("h_num", "Numerator Count;Jet variable;Numerator Count"    , 11, xbins);
    TH1D* h_den = new TH1D("h_den", "Denominator Count;Jet variable;Denominator Count", 11, xbins);
    TEfficiency* pEff = 0;

    // define selection
    TCut offline = "jpt_1>200 & jpt_2>100";

    TCut VBF = "trg_VBF";
    TCut DiTau = "trg_doubletau"; 

    // fill the histograms with TTree::Draw
    HLT_trigger_ntuple->Draw("mjj>>h_num", VBF && DiTau && offline);
    HLT_trigger_ntuple->Draw("mjj>>h_den", DiTau && offline);

    if(TEfficiency::CheckConsistency(*h_num,*h_den)){
        pEff = new TEfficiency(*h_num,*h_den);
        pEff->Draw("AP");
        gPad->Update();
        pEff->SetTitle("my efficiency;Jet variable;#epsilon");
    }
        TCanvas c2("c2", "c2", 600, 600);
        h_num->Draw("hist");        

        TCanvas c3("c3", "c3", 600, 600);
        h_den->Draw("hist");
}
