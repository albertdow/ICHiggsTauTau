{
    // book the historams
    //TH1::SetDefaultSumw2(true);
    double xbins[13]={0,20,40,50,60,70,80,90,100,120,140,160,200};
    TH1D* h_num = new TH1D("h_num", "Numerator Count;Jet variable;Numerator Count"    , 12, xbins);
    TH1D* h_den = new TH1D("h_den", "Denominator Count;Jet variable;Denominator Count", 12, xbins);
    TEfficiency* pEff = 0;

    // define selection
    TCut offline = "mjj>800 & jpt_1>180";

    TCut VBF = "trg_VBF";
    TCut DiTau = "trg_doubletau"; 

    // fill the histograms with TTree::Draw
    HLT_trigger_ntuple->Draw("jpt_2>>h_num", VBF && DiTau && offline);
    HLT_trigger_ntuple->Draw("jpt_2>>h_den", DiTau && offline);

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
