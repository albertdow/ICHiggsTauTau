#include "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/interface/HTTMLStudies.h"
#include "UserCode/ICHiggsTauTau/Analysis/Utilities/interface/FnPredicates.h"
#include "Utilities/interface/FnRootTools.h"


struct PtComparator{
    bool operator() (ic::Candidate a, ic::Candidate b) {
    return (a.vector().Pt() > b.vector().Pt());
  }
};

 
namespace ic {

  HTTMLStudies::HTTMLStudies(std::string const& name) : ModuleBase(name) {
    fs_ = NULL;
  }

  HTTMLStudies::~HTTMLStudies() {
    ;
  }

  int HTTMLStudies::PreAnalysis() {
     
  if(fs_){  
    outtree_ = fs_->make<TTree>("MLntuple","MLntuple");
    outtree_->Branch("event"       , &event_       );
    
    // offline variables from other tree
    outtree_->Branch("jpt_1",             &jpt_1_);
    outtree_->Branch("jpt_2",             &jpt_2_);
    outtree_->Branch("mjj",               &mjj_);
    outtree_->Branch("jdeta",             &jdeta_);
    outtree_->Branch("njets",             &njets_);

    outtree_->Branch("mva_olddm_medium_1",&lbyMediumIsolationMVArun2DBoldDMwLT_1);
    outtree_->Branch("mva_olddm_medium_2",&lbyMediumIsolationMVArun2DBoldDMwLT_2);
    outtree_->Branch("antiele_1",         &antiele_1_);
    outtree_->Branch("antimu_1",          &antimu_1_);
    outtree_->Branch("antiele_2",         &antiele_2_);
    outtree_->Branch("antimu_2",          &antimu_2_);

    outtree_->Branch("pt_tt",             &pt_tt_);

    }

    return 0;
  }


  int HTTMLStudies::Execute(TreeEvent *event) {

  // offline variables from other tree ("ntuple")
    if(event->Exists("jpt_1")) jpt_1_ = event->Get<double>("jpt_1");
    if(event->Exists("jpt_2")) jpt_2_ = event->Get<double>("jpt_2");
    if(event->Exists("mjj")) mjj_ = event->Get<double>("mjj");
    if(event->Exists("jdeta")) jdeta_ = event->Get<double>("jdeta");
    if(event->Exists("njets")) njets_ = event->Get<double>("njets");

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
 
  int HTTMLStudies::PostAnalysis() {
 
   return 0;
  }

  void HTTMLStudies::PrintInfo() {
    ;
  }

}
