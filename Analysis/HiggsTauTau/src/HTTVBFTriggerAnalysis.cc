#include "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/interface/HTTVBFTriggerAnalysis.h"
#include "UserCode/ICHiggsTauTau/Analysis/Utilities/interface/FnPredicates.h"
#include "Utilities/interface/FnRootTools.h"


double L1pass;
double L1fail;
double L1failSecond;
double L1size0;
double L1size1;
double Calosize0;
double HLTsize0;
double CaloL1tot;
double CaloL1matched;
bool CaloL1;

double PFTausize0;
double matchedVBF0;



struct PtComparator{
    bool operator() (ic::Candidate a, ic::Candidate b) {
    return (a.vector().Pt() > b.vector().Pt());
  }
};
 


struct PtComparatorTriggerObj{
    bool operator() (ic::TriggerObject *a, ic::TriggerObject *b) {
    return (a->vector().Pt() > b->vector().Pt());
  }
};


 bool IsFilterMatchedWithName(ic::TriggerObject *objs, std::string const& filter){
      std::size_t hash = CityHash64(filter);
      
      std::vector<std::size_t> const& labels = objs->filters();
      if (std::find(labels.begin(),labels.end(), hash) == labels.end())  return false;
      return true;
  }



 
namespace ic {

  HTTVBFTriggerAnalysis::HTTVBFTriggerAnalysis(std::string const& name) : ModuleBase(name) {
    fs_ = NULL;
  }

  HTTVBFTriggerAnalysis::~HTTVBFTriggerAnalysis() {
    ;
  }

  int HTTVBFTriggerAnalysis::PreAnalysis() {
     
   L1pass = 0;
   L1fail = 0;
   L1failSecond = 0;
   L1size0 = 0;
   L1size1 = 0;
   HLTsize0 = 0;
   Calosize0 = 0; 
   CaloL1matched = 0;
   CaloL1tot = 0; 
   CaloL1 = true;

   PFTausize0 = 0;
   matchedVBF0 = 0;

   if(fs_){  
      outtree_ = fs_->make<TTree>("HLT_trigger_ntuple","HLT_trigger_ntuple");
    outtree_->Branch("event"       , &event_       );
    
    // TWO JETS 
    outtree_->Branch("hlt_jpt_1"       , &hlt_jpt_1_       );
    outtree_->Branch("hlt_jpt_2"       , &hlt_jpt_2_       );
    outtree_->Branch("hlt_jpt_3"       , &hlt_jpt_3_       );
    outtree_->Branch("hlt_jpt_4"       , &hlt_jpt_4_       );
    outtree_->Branch("calo_jpt_1"       , &calo_jpt_1_       );
    outtree_->Branch("calo_jpt_2"       , &calo_jpt_2_       );

    outtree_->Branch("HLTjetssize"      , &HLTjetssize_     );

    outtree_->Branch("hlt_jeta_1"       , &hlt_jeta_1_       );
    outtree_->Branch("hlt_jeta_2"       , &hlt_jeta_2_       );
    outtree_->Branch("hlt_jeta_3"       , &hlt_jeta_3_       );
    outtree_->Branch("hlt_jeta_4"       , &hlt_jeta_4_       );

    outtree_->Branch("matchedPFJets" , &matchedPFJets_ );
    //outtree_->Branch("matched_vbf_jpt_1" , &matched_vbf_jpt_1_ );
    //outtree_->Branch("matched_vbf_jpt_2" , &matched_vbf_jpt_2_ );
    //  outtree_->Branch("matched_vbf_jpt_3" , &matched_vbf_jpt_3_ );
    //  outtree_->Branch("matched_vbf_jpt_4" , &matched_vbf_jpt_4_ );

    //outtree_->Branch("matched_vbf_jeta_1" , &matched_vbf_jeta_1_ );
    //outtree_->Branch("matched_vbf_jeta_2" , &matched_vbf_jeta_2_ );
    //  outtree_->Branch("matched_vbf_jeta_3" , &matched_vbf_jeta_3_ );
    //  outtree_->Branch("matched_vbf_jeta_4" , &matched_vbf_jeta_4_ );

    outtree_->Branch("PFTausize"        , &PFTausize_      );
    outtree_->Branch("tau_lo_pt"        , &tau_lo_pt_      );
    outtree_->Branch("tau_pt_2"        , &tau_pt_2_      );
    //outtree_->Branch("cleanTau_lo_pt"        , &cleanTau_lo_pt_      );
    //outtree_->Branch("cleanTau_pt_2"        , &cleanTau_pt_2_      );
    outtree_->Branch("hlt_mjj"       , &hlt_mjj_       );


    // THREE JETS
    outtree_->Branch("hlt_three_jpt_1"       , &hlt_three_jpt_1_       );
    outtree_->Branch("hlt_three_jpt_2"       , &hlt_three_jpt_2_       );
    outtree_->Branch("hlt_three_jpt_3"       , &hlt_three_jpt_3_       );
    outtree_->Branch("hlt_three_jpt_4"       , &hlt_three_jpt_4_       );
//    outtree_->Branch("calo_jpt_1"       , &calo_jpt_1_       );
  //  outtree_->Branch("calo_jpt_2"       , &calo_jpt_2_       );

    outtree_->Branch("hlt_three_jeta_1"       , &hlt_three_jeta_1_       );
    outtree_->Branch("hlt_three_jeta_2"       , &hlt_three_jeta_2_       );
    outtree_->Branch("hlt_three_jeta_3"       , &hlt_three_jeta_3_       );
    outtree_->Branch("hlt_three_jeta_4"       , &hlt_three_jeta_4_       );

    outtree_->Branch("hlt_three_mjj"       , &hlt_three_mjj_       );

    // OTHERS
    outtree_->Branch("L1_jpt_1"       ,  &L1_jpt_1_);
    //outtree_->Branch("HLTVBFPassThrough" ,  &HLTVBFPassThrough_);
    outtree_->Branch("HLTDoubleMediumIsoPFTau35" ,  &HLTDoubleMediumIsoPFTau35_);
    outtree_->Branch("HLTDoubleMediumIsoPFTau35_2" ,  &HLTDoubleMediumIsoPFTau35_2_);
    outtree_->Branch("HLTDoubleMediumIsoPFTau35_tau", &HLTDoubleMediumIsoPFTau35_tau_);

//    outtree_->Branch("trg_doubletau"       ,  &trg_doubletau);
    outtree_->Branch("trg_VBF"       ,  &trg_VBF);
    outtree_->Branch("offlineJets_1"    , &offline_jet_1);
    outtree_->Branch("offlineJets_2"    , &offline_jet_2);
    outtree_->Branch("offlineJets_eta_1", &offline_jet_eta_1);
    outtree_->Branch("offlineJets_eta_2", &offline_jet_eta_2);
    outtree_->Branch("offlineJets_deta", &offline_jet_deta);
    outtree_->Branch("offlineJets_mjj", &offline_mjj);
    outtree_->Branch("offlineTaus_1", &offline_tau_1);
    outtree_->Branch("offlineTaus_2", &offline_tau_2);
    outtree_->Branch("offlineTaus_m", &offline_tau_m);
    outtree_->Branch("PFJets", &PFJets_);
    outtree_->Branch("matchedPFJets", &matchedPFJets_);

    outtree_->Branch("HLT_DoubleMediumIsoPFTau35_Trk1_eta2p1_Reg_v",           &ttHLTPath1_);
    outtree_->Branch("HLT_VBF_DoubleLooseChargedIsoPFTau20_Trk1_eta2p1_Reg_v",           &VBFttHLTPath1_);
    outtree_->Branch("HLT_VBF_DoubleMediumChargedIsoPFTau20_Trk1_eta2p1_Reg_v",           &VBFttHLTPath2_);
    outtree_->Branch("HLT_VBF_DoubleTightChargedIsoPFTau20_Trk1_eta2p1_Reg_v",           &VBFttHLTPath3_);
    }


    h1 = new TH1D("h1","(Offline Jets.Pt()-HLT PFJets.Pt())/Offline Jets.Pt()",50,-1.5,1.5);
    c1 = new TCanvas("c1","c1",800,1000);
   
    h2 = new TH1D("h2","(offline Taus.Pt()-HLT PFTaus.Pt())/offline Taus.Pt()",50,-1.5,1.5);
    c2 = new TCanvas("c2","c2",800,1000);
    
    return 0;
  }


  int HTTVBFTriggerAnalysis::Execute(TreeEvent *event) {
    
   //std::vector<PFJet *> jetsobjs = event->GetPtrVec<PFJet>("ak4PFJetsCHS");
   //std::vector<Tau *> tausobjs = event->GetPtrVec<Tau>("taus");
   std::vector<TriggerObject *> const& VBFobjs = event->GetPtrVec<TriggerObject>("triggerObjectsVBFDoubleLooseChargedIsoPFTau20");	
   //std::vector<TriggerObject *> const& VBFobjs = event->GetPtrVec<TriggerObject>("triggerVBFLoose");	
   std::vector<TriggerObject *>  L1jets;
   std::vector<TriggerObject *>  Calojets;
   std::vector<TriggerObject *>  HLTjets;
   std::vector<TriggerObject *> PFTau;
   std::vector<TriggerObject *> matched_vbf_objs;
   std::vector<TriggerObject *> cleanTau;
   std::vector<TriggerObject *> DiTaus;
   std::vector<TriggerObject *> ThreeHLTjets;
   std::vector<TriggerObject *> ThreePFTau;

   hlt_jpt_1_=-9999;
   hlt_jpt_2_=-9999;
   hlt_jpt_3_=-9999;
   hlt_jpt_4_=-9999;
   hlt_jeta_1_=-9999;
   hlt_jeta_2_=-9999;
   hlt_jeta_3_=-9999;
   hlt_jeta_4_=-9999;
   calo_jpt_1_=-9999;
   calo_jpt_2_=-9999;
   
   tau_lo_pt_=-9999;
   tau_pt_2_ = -9999;
   cleanTau_lo_pt_ = -9999;
   cleanTau_pt_2_ = -9999;
   hlt_mjj_=-9999;
   L1_jpt_1_=-9999;

   matched_vbf_jpt_1_=-9999;
   matched_vbf_jpt_2_=-9999;
//   matched_vbf_jpt_3_=-9999;
//   matched_vbf_jpt_4_=-9999;

   matched_vbf_jeta_1_=-9999;
   matched_vbf_jeta_2_=-9999;
//   matched_vbf_jeta_3_=-9999;
//   matched_vbf_jeta_4_=-9999;
   HLTDoubleMediumIsoPFTau35_=-9999;


   hlt_three_jpt_1_=-9999;
   hlt_three_jpt_2_=-9999;
   hlt_three_jpt_3_=-9999;
   hlt_three_jpt_4_=-9999;
   hlt_three_jeta_1_=-9999;
   hlt_three_jeta_2_=-9999;
   hlt_three_jeta_3_=-9999;
   hlt_three_jeta_4_=-9999;
   hlt_three_mjj_=-9999;
   tau_lo_threej_pt_ =-9999;
   tau_pt_threej_2_ =-9999;

   PFTausize_=-9999;
   HLTjetssize_=-9999;

    for (unsigned i = 0; i < VBFobjs.size(); ++i)
	{ 
   bool a = IsFilterMatchedWithName(VBFobjs[i], "hltL1VBFDiJetOR");
   bool b = IsFilterMatchedWithName(VBFobjs[i], "'hltL1TCaloJetsMatching','TwoJets'");
   //bool b = IsFilterMatchedWithName(VBFobjs[i], "hltDoubleJet20");
   //bool c = IsFilterMatchedWithName(VBFobjs[i], "hltPFDoubleJetLooseIDOpen");
   //bool c = IsFilterMatchedWithName(VBFobjs[i], "hltMatchedVBFThreePFJetsOpenCrossCleanedFromLooseIsoPFTau20");
   bool c = IsFilterMatchedWithName(VBFobjs[i], "hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20");
   //bool d = IsFilterMatchedWithName(VBFobjs[i], "hltSinglePFTau20TrackPt1TightChargedIsolationAndTightOOSCPhotonsReg");
   bool d = IsFilterMatchedWithName(VBFobjs[i], "hltDoublePFTau20TrackPt1LooseChargedIsolationReg");
   
	if (a) 	L1jets.push_back(VBFobjs[i]);	
	if (b)	Calojets.push_back(VBFobjs[i]);
	if (c)  HLTjets.push_back(VBFobjs[i]);
    if (d)  PFTau.push_back(VBFobjs[i]);
}


//    HLTjetssize_ = HLTjets.size();
//    h1->Fill(HLTjetssize_);   

//    if (HLTjetssize_==1) {
//        std::cout<<"----------- "<<std::endl;
//        std::cout<<"filter matched "<<CityHash64("hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20")<<std::endl;
//        for (unsigned j=0; j<VBFobjs.size();j++) {
//          std::vector<std::size_t> const& labels = VBFobjs[j]->filters();
//          std::cout<<j<<" th object "<<std::endl;
//            for (unsigned i=0; i<labels.size();i++) std::cout<<"label name "<<labels[i]<<std::endl;
//        }
//    }

// for ThreeJets path
    //for (unsigned i = 0; i < VBFThreeobjs.size(); ++i)
	//{ 
    //bool three = IsFilterMatchedWithName(VBFThreeobjs[i], "hltMatchedVBFThreePFJetsOpenCrossCleanedFromLooseIsoPFTau20");
    //bool three_tau = IsFilterMatchedWithName(VBFThreeobjs[i], "hltSinglePFTau20TrackPt1LooseChargedIsolationReg");
    //if (three) ThreeHLTjets.push_back(VBFThreeobjs[i]);
    //if (three_tau) ThreePFTau.push_back(VBFThreeobjs[i]);
    //}

//std::cout<<"A"<<std::endl;
std::sort(HLTjets.begin(), HLTjets.end(), PtComparatorTriggerObj());
std::sort(Calojets.begin(), Calojets.end(), PtComparatorTriggerObj());
std::sort(L1jets.begin(), L1jets.end(), PtComparatorTriggerObj());
std::sort(PFTau.begin(), PFTau.end(), PtComparatorTriggerObj());
//std::sort(ThreeHLTjets.begin(), ThreeHLTjets.end(), PtComparatorTriggerObj());
// Add mjj






//L1jets and PFjets match test

//unsigned int Match =0;
//for (unsigned i = 0; i < HLTjets.size(); ++i)
//{
//  for (unsigned j = 0; j < 1; ++j)
//  {
//    std::pair<TriggerObject *, TriggerObject *> L1PF (HLTjets[i],L1jets[j]);
//    bool a = DRLessThan(L1PF,0.5);
//    if (a) 
//    {
//	  Match+=1;
//   	  h1->Fill(HLTjets[i]->vector().Pt());
//	  break;
//    } 
//  }
//}

//if (Match!=HLTjets.size()){
//  std::cout<<"Matching problem: Matched :"<<Match<<" / "<<HLTjets.size()<<std::endl;
//}


if (L1jets.size()!=0)
	{if (L1jets[0]->vector().Pt()<80) L1fail++;
	if (L1jets.size()>1) 
		if (L1jets[1]->vector().Pt()<30) L1failSecond++;

	}
L1pass++;

if (L1jets.size()==0) L1size0++;
if (Calojets.size()==0) Calosize0++;
if (HLTjets.size()==0) HLTsize0++;
if (PFTau.size()==0) PFTausize0++;
//if (matched_vbf_objs.size()==0) matchedVBF0++;
//if (vbf_objs.size()==0) matchedVBF0++;

L1size1++;


//Insert mjj for HLT and Calo jets 

double mjj = -9999;

for (unsigned i = 0; i < HLTjets.size(); ++i)
for (unsigned j = 0; j < HLTjets.size(); ++j)
{

    if ((HLTjets.size()>1)||(i!=j)) 
    {
        if ((HLTjets[i]->vector()+HLTjets[j]->vector()).M()>mjj)
        {
		    mjj = (HLTjets[i]->vector()+HLTjets[j]->vector()).M();
        }

    }

}


//if ((HLTjets[0]->vector()+HLTjets[1]->vector()).M()>mjj)
//{
//  threeMjj = (HLTjets[0]->vector()+HLTjets[1]->vector()).M();
//}


/*for (unsigned i = 0; i < Calojets.size(); ++i)
{

if ()
CaloL1tot++;

}*/
//if (HLTjets.size()>1)
//std::cout<<HLTjets[0]->vector().Pt()<<" " <<HLTjets[1]->vector().Pt()<<std::endl;
if (HLTjets.size()>0)
	{
    hlt_jpt_1_ = HLTjets[0]->vector().Pt();
    hlt_jeta_1_ = HLTjets[0]->vector().Eta();

	}
if (HLTjets.size()>1)
	{
    hlt_jpt_2_ = HLTjets[1]->vector().Pt();
    hlt_jeta_2_ = HLTjets[1]->vector().Eta();
	}
if (HLTjets.size()>2)
	{
    hlt_jpt_3_ = HLTjets[2]->vector().Pt();
    hlt_jeta_3_ = HLTjets[2]->vector().Eta();	
	}
if (HLTjets.size()>3)
	{
    hlt_jpt_4_ = HLTjets[3]->vector().Pt(); 
    hlt_jeta_4_ = HLTjets[3]->vector().Eta();	
	}
//std::cout<<Calojets.size()<<std::endl;
if (Calojets.size()>0)
        {
    calo_jpt_1_ = Calojets[0]->vector().Pt();
    //calo_jeta_1_ = Calojets[0]->vector().Eta();

        }
if (Calojets.size()>1)
        {
    calo_jpt_2_ = Calojets[1]->vector().Pt();
    //calo_jeta_2_ = Calojets[1]->vector().Eta();
        }

if (L1jets.size()>0)
{
    L1_jpt_1_=L1jets[0]->vector().Pt();
}
 
  hlt_mjj_ = mjj;




  //if (hlt_jpt_1_ > 0 && hlt_jpt_2_ > 0 && hlt_jpt_2_ < 115) std::cout<<"jet < 115 GeV"<<std::endl;

  // THREE JETS

if (ThreeHLTjets.size()>0)
	{
    hlt_three_jpt_1_ = ThreeHLTjets[0]->vector().Pt();
    hlt_three_jeta_1_ = ThreeHLTjets[0]->vector().Eta();

	}
if (ThreeHLTjets.size()>1)
	{
    hlt_three_jpt_2_ = ThreeHLTjets[1]->vector().Pt();
    hlt_three_jeta_2_ = ThreeHLTjets[1]->vector().Eta();
	}
if (ThreeHLTjets.size()>2)
	{
    hlt_three_jpt_3_ = ThreeHLTjets[2]->vector().Pt();
    hlt_three_jeta_3_ = ThreeHLTjets[2]->vector().Eta();	
	}
if (ThreeHLTjets.size()>3)
	{
    hlt_three_jpt_4_ = ThreeHLTjets[3]->vector().Pt(); 
    hlt_three_jeta_4_ = ThreeHLTjets[3]->vector().Eta();	
	}

double threeMjj = -9999;

if (ThreeHLTjets.size()>2){    
  if ((ThreeHLTjets[0]->vector()+ThreeHLTjets[1]->vector()).M()>threeMjj)
  {
    threeMjj = (ThreeHLTjets[0]->vector()+ThreeHLTjets[1]->vector()).M();
  }
}

    hlt_three_mjj_ = threeMjj;
    // For testing HLT online jets/tau matching
//    std::vector<TriggerObject *> const& vbf_objs = event->GetPtrVec<TriggerObject>("triggerVBF");
//
//    for (unsigned i = 0; i < PFTau.size(); ++i)
//    {
//      int index = IsFilterMatchedWithIndex(PFTau[i], vbf_objs, "hltDiPFJetOpenMJJOpen", 0.5).second;
//      if (IsFilterMatchedWithIndex(PFTau[i], vbf_objs, "hltDiPFJetOpenMJJOpen", 0.5).first == false)
//      {
//      	cleanTau.push_back(vbf_objs[index]);
//      }
//      else 
//          break;
//
//    }
 
  ///////
  

    PFTausize_ = PFTau.size();

  if (PFTau.size()>0) {
    tau_lo_pt_ = PFTau[0]->vector().Pt();
  }
  if (PFTau.size()>1) {
    tau_pt_2_ = PFTau[1]->vector().Pt();
  }


  event->Add("trgTau2",tau_pt_2_);



  trg_VBF = hlt_jpt_1_>115&&hlt_jpt_2_>40&&hlt_mjj_>650&&tau_pt_2_>20;
  event->Add("trg_VBF",trg_VBF);

  


//  trg_VBF_three = hlt_three_jpt_1_>40&&hlt_three_jpt_2_>40&&hlt_three_mjj_>650&&tau_pt_2_>20;
//  event->Add("trg_VBF_three",trg_VBF_three);


  //if (PFTau.size()>0) {
  //  tau_lo_threej_pt_ = ThreePFTau[0]->vector().Pt();
  //}
  //if (PFTau.size()>1) {
  //  tau_pt_threej_2_ = ThreePFTau[1]->vector().Pt();
  //}
//  if (cleanTau.size()>0) {
//    cleanTau_lo_pt_ = cleanTau[0]->vector().Pt();
//  }
//  if (cleanTau.size()>1) {
//    cleanTau_pt_2_ = cleanTau[1]->vector().Pt();
//  }
  

    // For testing HLT online/offline jets matching
//    std::vector<TriggerObject *> const& vbf_objs = event->GetPtrVec<TriggerObject>("triggerVBF");
    std::vector<PFJet *> jets = event->GetPtrVec<PFJet>("ak4PFJetsCHS");

    for (unsigned i = 0; i < jets.size(); ++i)
    {
      int index = IsFilterMatchedWithIndex(jets[i], VBFobjs, "hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20", 0.5).second;
      if (IsFilterMatchedWithIndex(jets[i], VBFobjs, "hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20", 0.5).first == true)
      {
      	matched_vbf_objs.push_back(VBFobjs[index]);
        h1->Fill((jets[i]->vector().Pt()-VBFobjs[index]->vector().Pt())/jets[i]->vector().Pt());
      }
      else 
          break;
    }
//
//        if (matched_vbf_objs.size()>0){
//            matched_vbf_jpt_1_ = matched_vbf_objs[0]->vector().Pt();
//            matched_vbf_jeta_1_ = matched_vbf_objs[0]->vector().Eta();
//        }
//        if (matched_vbf_objs.size()>1){
//            matched_vbf_jpt_2_ = matched_vbf_objs[1]->vector().Pt();
//            matched_vbf_jeta_2_ = matched_vbf_objs[1]->vector().Eta();
//        }
        //if (matched_vbf_objs.size()>2){
        //    matched_vbf_jpt_3_ = matched_vbf_objs[2]->vector().Pt();
        //    matched_vbf_jeta_3_ = matched_vbf_objs[0]->vector().Eta();
        //}
        //if (matched_vbf_objs.size()>3){
        //    matched_vbf_jpt_4_ = matched_vbf_objs[3]->vector().Pt();
        //    matched_vbf_jeta_4_ = matched_vbf_objs[0]->vector().Eta();
        //}

  

//  std::vector<TriggerObject *> const& pass_through_objs = event->GetPtrVec<TriggerObject>("triggerObjectsDiJetVBFPassThrough");
//  HLTVBFPassThrough_ = pass_through_objs[0]->vector().Pt(); 

 std::vector<TriggerObject *> const& double_tau_objs = event->GetPtrVec<TriggerObject>("triggerObjectsDoubleMediumChargedIsoPFTau35");
 if (double_tau_objs.size()>0) HLTDoubleMediumIsoPFTau35_ = double_tau_objs[0]->vector().Pt(); 
 if (double_tau_objs.size()>1) HLTDoubleMediumIsoPFTau35_2_ = double_tau_objs[1]->vector().Pt(); 
  
   for (unsigned i = 0; i < double_tau_objs.size(); ++i)
   { 
 bool e = IsFilterMatchedWithName(double_tau_objs[i], "hltDoublePFTau35TrackPt1MediumChargedIsolationDz02Reg");
  
 if (e) 	DiTaus.push_back(double_tau_objs[i]);	
   }
 std::sort(DiTaus.begin(), DiTaus.end(), PtComparatorTriggerObj());

// if (DiTaus.size()>0&&DiTaus.size()<2) std::cout<<"Size equal to 1"<<std::endl;
// if (DiTaus.size()>1&&DiTaus[1]->vector().Pt()<35) std::cout<<"Pt of 2nd tau"<<DiTaus[1]->vector().Pt()<<std::endl;
  
//  trg_doubletau=DiTaus.size()>1;
//  event->Add("trg_doubletau",DiTaus.size()>1);
  //if (double_tau_objs.size()>0) HLTDoubleMediumIsoPFTau35_tau_ = tausobjs[0]->vector().Pt();
  //
  //
  //
    // For testing HLT online/offline jets matching
//    std::vector<TriggerObject *> const& vbf_objs = event->GetPtrVec<TriggerObject>("triggerVBF");
//    std::vector<PFJet *> jets = event->GetPtrVec<PFJet>("ak4PFJetsCHS");
    
    for (unsigned i = 0; i < jets.size(); ++i){
      PFJets_ = jets[i]->vector().Pt();
    }
    for (unsigned i = 0; i < matched_vbf_objs.size(); ++i){
      matchedPFJets_ = matched_vbf_objs[i]->vector().Pt();
    }

  event->Add("PFJets",PFJets_);
  event->Add("matchedPFJets",matchedPFJets_);

  if (jets.size()>0) {
    offline_jet_1 = jets[0]->vector().Pt();
    offline_jet_eta_1 = jets[0]->vector().Eta();
  }
  if (jets.size()>1) {
    offline_jet_2 = jets[1]->vector().Pt();
    offline_jet_eta_2 = jets[1]->vector().Eta();
    offline_jet_deta = fabs(jets[0]->vector().Eta()-jets[1]->vector().Eta());
    offline_mjj = (jets[0]->vector()+jets[1]->vector()).M();
  }
  

    event->Add("offlineJets_1", offline_jet_1);
    event->Add("offlineJets_2", offline_jet_2);
    event->Add("offlineJets_eta_1", offline_jet_eta_1);
    event->Add("offlineJets_eta_2", offline_jet_eta_2);
    event->Add("offlineJets_deta", offline_jet_deta);
    event->Add("offlineJets_mjj", offline_mjj);

//    std::vector<TriggerObject *> matching_vbf_objs;
//
//    for (unsigned i = 0; i < jets.size(); ++i)
//    {
//      if (jets[i]->vector().Pt()>35){
//      int index = IsFilterMatchedWithIndex(jets[i], vbf_objs, "hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20", 0.5).second;
//      if (IsFilterMatchedWithIndex(jets[i], vbf_objs, "hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20", 0.5).first == true)
//      {
//      	matching_vbf_objs.push_back(vbf_objs[index]);
//      	h1->Fill((jets[i]->vector().Pt()-vbf_objs[index]->vector().Pt())/jets[i]->vector().Pt());
//      }
//      else 
//          break;
//      //std::cout << jets[i]->vector().Pt() << ' ';
//      //std::cout << vbf_objs[index]->vector().Pt() << std::endl;
//      }
//    }
//    
//
//    // For testing tau online/offline matching
//    //std::vector<TriggerObject *> const& vbf_objs = event->GetPtrVec<TriggerObject>("triggerVBF");
    std::vector<Tau *> taus = event->GetPtrVec<Tau>("taus");
    std::vector<TriggerObject *> matched_tau_objs;

    for (unsigned i = 0; i < taus.size(); ++i)
    {
      if (taus[i]->vector().Pt()>20) {
      int index = IsFilterMatchedWithIndex(taus[i], VBFobjs, "hltDoublePFTau20TrackPt1LooseChargedIsolationReg", 0.5).second;
      if (IsFilterMatchedWithIndex(taus[i], VBFobjs, "hltDoublePFTau20TrackPt1LooseChargedIsolationReg", 0.5).first == true)
      {
      	matched_tau_objs.push_back(VBFobjs[index]);
      	h2->Fill((taus[i]->vector().Pt()-VBFobjs[index]->vector().Pt())/taus[i]->vector().Pt());
      }
      else 
          break;
      //std::cout << taus[i]->vector().Pt() << ' ';
      //std::cout << vbf_objs[index]->vector().Pt() << std::endl;

      }
    }
//

  if (taus.size()>0) {
    offline_tau_1 = taus[0]->vector().Pt();
  }
  if (taus.size()>1) {
    offline_tau_2 = taus[1]->vector().Pt();
    offline_tau_m = (taus[0]->vector()+taus[1]->vector()).M();
  }    

  event->Add("offlineTaus_1",offline_tau_1);
  event->Add("offlineTaus_2",offline_tau_2);
  event->Add("offlineTaus_m", &offline_tau_m);

//  ttHLTPath1_  = event->Get<bool>("HLT_DoubleMediumChargedIsoPFTau35_Trk1_eta2p1_Reg_v");
//  VBFttHLTPath1_  = event->Get<bool>("HLT_VBF_DoubleLooseChargedIsoPFTau20_Trk1_eta2p1_Reg_v");
//  VBFttHLTPath2_  = event->Get<bool>("HLT_VBF_DoubleMediumChargedIsoPFTau20_Trk1_eta2p1_Reg_v");
//  VBFttHLTPath3_  = event->Get<bool>("HLT_VBF_DoubleTightChargedIsoPFTau20_Trk1_eta2p1_Reg_v");


  if(fs_) outtree_->Fill();
    

    return 0;
	}
 
  int HTTVBFTriggerAnalysis::PostAnalysis() {
 
std::cout<<"L1jets size 0 = "<<1.0*L1size0/L1size1<<std::endl;
std::cout<<"HLT "<<1.0*(HLTsize0)/L1size1 << " CALO size 0 = "<<1.0*(Calosize0)/L1size1<<std::endl;
std::cout<<"L1jets size !=0 but L1jets[0]->vector().Pt()<80: "<<(L1fail/L1pass)<<std::endl;
std::cout<<"L1jets size !=0 but L1jets[1]->vector().Pt()<30: "<<(L1failSecond/L1pass)<<std::endl;
std::cout<<L1fail<<" "<<L1pass<<std::endl;

//    std::cout<<h1->GetEntries()<<std::endl;
//    h1->Draw();
//    c1->Update();
//    c1->Print("jetsRes.pdf");
//    h2->Draw();
//    c2->Update();
//    c2->Print("tausRes.pdf");
   return 0;
  }

  void HTTVBFTriggerAnalysis::PrintInfo() {
    ;
  }

}
