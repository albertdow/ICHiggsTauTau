{
    // book the historams
    //TH1::SetDefaultSumw2(true);
    TH1D* h_num = new TH1D("h_num", "Numerator Count;Jet variable;Numerator Count"    , 200, 0, 2000);
    TH1D* h_den = new TH1D("h_den", "Denominator Count;Jet variable;Denominator Count", 200, 0, 2000);
    TEfficiency* pEff = 0;

    // define selection
    //TCut offline = "mjj>500&&jdeta>3.5 && pt_tt>100  &&mva_olddm_medium_2>0.5 && antiele_2 && antimu_2";
    //TCut HLT = "trgTau2&&trg_VBF";
    //TCut offline = "mjj>500&&jdeta>3.5 && pt_1>140 && pt_2>60 && pt_tt>100 & mva_olddm_medium_1>0.5 && antiele_1 && antimu_1&&mva_olddm_medium_2>0.5 && antiele_2 && antimu_2";
    TCut offline = "";
    //TCut HLT = "trg_VBF";

    TCut VBF = "trg_VBF";
    TCut DiTau = "trg_doubletau"; 
    //TCut offline = "offlineJets_1>130 & offlineJets_2>50 & offlineJets_mjj>700";

    // fill the histograms with TTree::Draw
    ntuple->Draw("mjj>>h_den", DiTau && offline);
    ntuple->Draw("mjj>>h_num", VBF && DiTau && offline);
    //HLT_trigger_ntuple->Draw("offlineJets_mjj>>h_num", VBF && DiTau && offline);
    //HLT_trigger_ntuple->Draw("offlineJets_mjj>>h_den", DiTau && offline);

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
