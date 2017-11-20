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
    // jet variables
    outtree_->Branch("jpt_1",             &jpt_1_);
    outtree_->Branch("jpt_2",             &jpt_2_);
    outtree_->Branch("jeta_1",             &jeta_1_);
    outtree_->Branch("jeta_2",             &jeta_2_);
    outtree_->Branch("jphi_1",             &jphi_1_);
    outtree_->Branch("jphi_2",             &jphi_2_);
    outtree_->Branch("mjj",               &mjj_);
    outtree_->Branch("jdeta",             &jdeta_);
    outtree_->Branch("jdphi",             &jdphi_);
    outtree_->Branch("njets",             &n_jets_);

    // lepton variables
    outtree_->Branch("pt_1",             &pt_1_);
    outtree_->Branch("pt_2",             &pt_2_);
    outtree_->Branch("eta_1",             &eta_1_);
    outtree_->Branch("eta_2",             &eta_2_);
    outtree_->Branch("eta_tt",             &eta_tt_);
    outtree_->Branch("phi_1",             &phi_1_);
    outtree_->Branch("phi_2",             &phi_2_);
    outtree_->Branch("dphi",             &dphi_);
    outtree_->Branch("mt_1",             &mt_1_);
    outtree_->Branch("mt_2",             &mt_2_);

    outtree_->Branch("mva_olddm_medium_1",&lbyMediumIsolationMVArun2DBoldDMwLT_1);
    outtree_->Branch("mva_olddm_medium_2",&lbyMediumIsolationMVArun2DBoldDMwLT_2);
    outtree_->Branch("antiele_1",         &antiele_1_);
    outtree_->Branch("antimu_1",          &antimu_1_);
    outtree_->Branch("antiele_2",         &antiele_2_);
    outtree_->Branch("antimu_2",          &antimu_2_);

    outtree_->Branch("pt_tt",             &pt_tt_);

    outtree_->Branch("dphi_jjtt",        &dphi_jjtt_);
    outtree_->Branch("zfeld",        &zfeld_);
    }

    return 0;
  }


  int HTTMLStudies::Execute(TreeEvent *event) {

    // offline variables from other tree ("ntuple")
    // jet variables
    if(event->Exists("jpt_1")) jpt_1_ = event->Get<double>("jpt_1");
    if(event->Exists("jpt_2")) jpt_2_ = event->Get<double>("jpt_2");
    if(event->Exists("jeta_1")) jeta_1_ = event->Get<double>("jeta_1");
    if(event->Exists("jeta_2")) jeta_2_ = event->Get<double>("jeta_2");
    if(event->Exists("jphi_1")) jphi_1_ = event->Get<float>("jphi_1");
    if(event->Exists("jphi_2")) jphi_2_ = event->Get<float>("jphi_2");
    if(event->Exists("mjj")) mjj_ = event->Get<double>("mjj");
    if(event->Exists("jdeta")) jdeta_ = event->Get<double>("jdeta");
    if(event->Exists("jdphi")) jdphi_ = event->Get<float>("jdphi");
    if(event->Exists("njets")) n_jets_ = event->Get<unsigned>("njets");

    // lepton variables
    if(event->Exists("pt_1")) pt_1_ = event->Get<double>("pt_1");
    if(event->Exists("pt_2")) pt_2_ = event->Get<double>("pt_2");
    if(event->Exists("eta_1")) jeta_1_ = event->Get<double>("eta_1");
    if(event->Exists("eta_2")) jeta_2_ = event->Get<double>("eta_2");
    if(event->Exists("eta_tt")) eta_tt_ = event->Get<double>("eta_tt");
    if(event->Exists("phi_1")) jphi_1_ = event->Get<double>("phi_1");
    if(event->Exists("phi_2")) jphi_2_ = event->Get<double>("phi_2");
    if(event->Exists("dphi_")) dphi_ = event->Get<double>("dphi_");
    if(event->Exists("mt_1")) mt_1_ = event->Get<double>("mt_1");
    if(event->Exists("mt_2")) mt_2_ = event->Get<double>("mt_2");

    if(event->Exists("mva_olddm_medium_1")) lbyMediumIsolationMVArun2DBoldDMwLT_1 = event->Get<bool>("mva_olddm_medium_1");
    if(event->Exists("mva_olddm_medium_2")) lbyMediumIsolationMVArun2DBoldDMwLT_2 = event->Get<bool>("mva_olddm_medium_2");
    if(event->Exists("antiele_1")) antiele_1_ = event->Get<bool>("antiele_1");
    if(event->Exists("antimu_1")) antimu_1_ = event->Get<bool>("antimu_1");
    if(event->Exists("antiele_2")) antiele_2_ = event->Get<bool>("antiele_2");
    if(event->Exists("antimu_2")) antimu_2_ = event->Get<bool>("antimu_2");

    if(event->Exists("pt_tt")) pt_tt_ = event->Get<double>("pt_tt");


    
    // adding Zeppenfeld variable
    zfeld_ = -9999;
    zfeld_ = eta_tt_ + (jeta_1_ + jeta_2_)/2;

    // adding delta phi between jj and tt pairs
    dphi_jjtt_ = -9999;
    dphi_jjtt_ = std::fabs(jdphi_-dphi_);


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
