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
std::string jet_leg1_filter;
std::string jet_leg2_filter;
std::string trig_jet_obj_label; 

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

    // OTHERS
    outtree_->Branch("L1_jpt_1"       ,  &L1_jpt_1_);
    outtree_->Branch("L1_jpt_2"       ,  &L1_jpt_2_);
    outtree_->Branch("L1_jeta_1"       ,  &L1_jeta_1_);
    outtree_->Branch("L1_jeta_2"       ,  &L1_jeta_2_);
    outtree_->Branch("L1_mjj"       ,  &L1_mjj_);
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

    outtree_->Branch("trg_doubletau", &trg_doubletau);

    // offline variables from other tree
    outtree_->Branch("jpt_1",             &jpt_1_);
    outtree_->Branch("jpt_2",             &jpt_2_);
    outtree_->Branch("mjj",               &mjj_);
    outtree_->Branch("jdeta",             &jdeta_);
    outtree_->Branch("mva_olddm_medium_1",&lbyMediumIsolationMVArun2DBoldDMwLT_1);
    outtree_->Branch("mva_olddm_medium_2",&lbyMediumIsolationMVArun2DBoldDMwLT_2);
    outtree_->Branch("antiele_1",         &antiele_1_);
    outtree_->Branch("antimu_1",          &antimu_1_);
    outtree_->Branch("antiele_2",         &antiele_2_);
    outtree_->Branch("antimu_2",          &antimu_2_);
    outtree_->Branch("pt_tt",             &pt_tt_);
    }


    h1 = new TH1D("h1","(Offline Jets.Pt()-HLT PFJets.Pt())/Offline Jets.Pt()",50,-1.5,1.5);
    c1 = new TCanvas("c1","c1",800,1000);
   
    h2 = new TH1D("h2","(offline Taus.Pt()-HLT PFTaus.Pt())/offline Taus.Pt()",50,-1.5,1.5);
    c2 = new TCanvas("c2","c2",800,1000);
    
    return 0;
  }


  int HTTVBFTriggerAnalysis::Execute(TreeEvent *event) {
    
   std::vector<TriggerObject *> const& VBFobjs = event->GetPtrVec<TriggerObject>("triggerObjectsVBFDoubleLooseChargedIsoPFTau20");	
   std::vector<TriggerObject *>  L1jets;
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
   
   tau_lo_pt_=-9999;
   tau_pt_2_ = -9999;
   cleanTau_lo_pt_ = -9999;
   cleanTau_pt_2_ = -9999;
   hlt_mjj_=-9999;
   L1_jpt_1_=-9999;
   L1_jpt_2_=-9999;
   L1_jeta_1_=-9999;
   L1_jeta_2_=-9999;
   L1_mjj_=-9999;

   matched_vbf_jpt_1_=-9999;
   matched_vbf_jpt_2_=-9999;
//   matched_vbf_jpt_3_=-9999;
//   matched_vbf_jpt_4_=-9999;

   matched_vbf_jeta_1_=-9999;
   matched_vbf_jeta_2_=-9999;
//   matched_vbf_jeta_3_=-9999;
//   matched_vbf_jeta_4_=-9999;
   HLTDoubleMediumIsoPFTau35_=-9999;


   PFTausize_=-9999;
   HLTjetssize_=-9999;

    // Get the objects at HLT from the appropriate filters
    for (unsigned i = 0; i < VBFobjs.size(); ++i){ 
  	  if (IsFilterMatchedWithName(VBFobjs[i], "hltL1VBFDiJetOR")) L1jets.push_back(VBFobjs[i]);	
	  if (IsFilterMatchedWithName(VBFobjs[i], "hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20")) HLTjets.push_back(VBFobjs[i]);	
	  if (IsFilterMatchedWithName(VBFobjs[i], "hltDoublePFTau20TrackPt1LooseChargedIsolationReg")) PFTau.push_back(VBFobjs[i]);	
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


std::sort(HLTjets.begin(), HLTjets.end(), PtComparatorTriggerObj());
std::sort(L1jets.begin(), L1jets.end(), PtComparatorTriggerObj());
std::sort(PFTau.begin(), PFTau.end(), PtComparatorTriggerObj());

//L1jets and PFjets match test

//unsigned int Match =0;
//for (unsigned i = 0; i < HLTjets.size()-1; ++i)
//  for (unsigned j = i+1; j < HLTjets.size(); ++j)
//  {
//    std::pair<TriggerObject *, TriggerObject *> L1PF (HLTjets[i],L1jets[j]);
//    bool a = DRLessThan(L1PF,0.5);
//    if (a) 
//    {
//	  Match+=1;
//   	  //h1->Fill(HLTjets[i]->vector().Pt());
//	  break;
//    } 
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

//for (unsigned i = 0; i < L1jets.size(); ++i) L1Jets_=L1jets[i]->vector().Pt();

if (L1jets.size()>0)
{
    L1_jpt_1_=L1jets[0]->vector().Pt();
    L1_jeta_1_=L1jets[0]->vector().Eta();
}
 
if (L1jets.size()>1)
{
    L1_jpt_2_=L1jets[1]->vector().Pt();
    L1_jeta_2_=L1jets[1]->vector().Eta();

}
  hlt_mjj_ = mjj;


for (unsigned i = 0; i < L1jets.size()-1; ++i)
for (unsigned j = i+1; j < L1jets.size(); ++j)
{

  if ((L1jets.size()>1)) 
  {
    L1_mjj_ = (L1jets[i]->vector()+L1jets[j]->vector()).M();
  }  
}


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


    std::vector<PFJet *> jets = event->GetPtrVec<PFJet>("ak4PFJetsCHS");


  trg_VBF = hlt_jpt_1_>115&&hlt_jpt_2_>40&&hlt_mjj_>650&&tau_pt_2_>20;
  event->Add("trg_VBF",trg_VBF);

  
  if(event->Exists("trg_doubletau")) trg_doubletau = event->Get<bool>("trg_doubletau");


//  if (cleanTau.size()>0) {
//    cleanTau_lo_pt_ = cleanTau[0]->vector().Pt();
//  }
//  if (cleanTau.size()>1) {
//    cleanTau_pt_2_ = cleanTau[1]->vector().Pt();
//  }
  

    // For testing HLT online/offline jets matching
//    std::vector<TriggerObject *> const& vbf_objs = event->GetPtrVec<TriggerObject>("triggerVBF");
//    std::vector<PFJet *> jets = event->GetPtrVec<PFJet>("ak4PFJetsCHS");

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


  // define trg_VBF
//  trig_jet_obj_label = "triggerObjectsVBFDoubleLooseChargedIsoPFTau20";
//  jet_leg1_filter = "hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20";
//  jet_leg2_filter = "hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20";
//
//  bool passed_VBF = false;
//  for(unsigned i = 0; i < jets.size(); ++i){
//    bool jet_leg1_match = IsFilterMatchedWithIndex(jets[i], VBFobjs, jet_leg1_filter, 0.5).first;
//    bool jet_leg2_match = IsFilterMatchedWithIndex(jets[i], VBFobjs, jet_leg2_filter, 0.5).first;
//       
//    if (jet_leg1_match && jet_leg2_match){
//      passed_VBF = true;  
//    } 
//  }
//  event->Add("trg_VBF", passed_VBF);

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


  // offline variables from other tree ("ntuple")
    if(event->Exists("jpt_1")) jpt_1_ = event->Get<double>("jpt_1");
    if(event->Exists("jpt_2")) jpt_2_ = event->Get<double>("jpt_2");
    if(event->Exists("mjj")) mjj_ = event->Get<double>("mjj");
    if(event->Exists("jdeta")) jdeta_ = event->Get<double>("jdeta");

    if(event->Exists("mva_olddm_medium_1")) lbyMediumIsolationMVArun2DBoldDMwLT_1 = event->Get<bool>("mva_olddm_medium_1");
    if(event->Exists("mva_olddm_medium_2")) lbyMediumIsolationMVArun2DBoldDMwLT_2 = event->Get<bool>("mva_olddm_medium_2");
    if(event->Exists("antiele_1")) antiele_1_ = event->Get<bool>("antiele_1");
    if(event->Exists("antimu_1")) antimu_1_ = event->Get<bool>("antimu_1");
    if(event->Exists("antiele_2")) antiele_2_ = event->Get<bool>("antiele_2");
    if(event->Exists("antimu_2")) antimu_2_ = event->Get<bool>("antimu_2");

    if(event->Exists("pt_tt")) pt_tt_ = event->Get<double>("pt_tt");

  if(fs_) outtree_->Fill();
    

    return 0;
	}
 
  int HTTVBFTriggerAnalysis::PostAnalysis() {
 
std::cout<<"L1jets size 0 = "<<1.0*L1size0/L1size1<<std::endl;
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
