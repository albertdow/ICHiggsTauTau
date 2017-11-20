#ifndef ICHiggsTauTau_HiggsTauTau_HTTMLStudies_h
#define ICHiggsTauTau_HiggsTauTau_HTTMLStudies_h

#include "UserCode/ICHiggsTauTau/Analysis/Core/interface/TreeEvent.h"
#include "UserCode/ICHiggsTauTau/Analysis/Core/interface/ModuleBase.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include "UserCode/ICHiggsTauTau/Analysis/Utilities/interface/HistoSet.h"
#include "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/interface/HTTConfig.h"
#include "UserCode/ICHiggsTauTau/interface/Candidate.hh"
#include "UserCode/ICHiggsTauTau/interface/CompositeCandidate.hh"
#include "UserCode/ICHiggsTauTau/interface/Tau.hh"

#include <string>

#include <TH1D.h>
#include <TCanvas.h>

namespace ic {
  
class HTTMLStudies : public ModuleBase {
 private:
  CLASS_MEMBER(HTTMLStudies, fwlite::TFileService*, fs)
  CLASS_MEMBER(HTTMLStudies, std::string, channel_str)
  CLASS_MEMBER(HTTMLStudies, double, min_jet_pt    )
  CLASS_MEMBER(HTTMLStudies, double, max_jet_eta  )
  CLASS_MEMBER(HTTMLStudies, double, min_e_pt     )
  CLASS_MEMBER(HTTMLStudies, double, min_mu_pt    )
  CLASS_MEMBER(HTTMLStudies, double, min_tau1_pt  )
  CLASS_MEMBER(HTTMLStudies, double, min_tau2_pt  )
  CLASS_MEMBER(HTTMLStudies, double, max_e_eta    )
  CLASS_MEMBER(HTTMLStudies, double, max_mu_eta   )
  CLASS_MEMBER(HTTMLStudies, double, max_tau_eta  )
  CLASS_MEMBER(HTTMLStudies, bool, do_theory_uncert)
  
  TTree *outtree_;
  
  unsigned long long event_;
  
  unsigned count_ee_;
  unsigned count_em_;
  unsigned count_et_;
  unsigned count_mm_;
  unsigned count_mt_;
  unsigned count_tt_;

  double jpt_1_;
  double jpt_2_;
  double jeta_1_;
  double jeta_2_;
  float jphi_1_;
  float jphi_2_;
  float jdphi_;
  double mjj_;       // Defined if n_jets >= 2
  double jdeta_;
  double n_jets_;

  double pt_1_;
  double pt_2_;
  double eta_1_;
  double eta_2_;
  double eta_tt_;
  double phi_1_;
  double phi_2_;
  double dphi_;
  double mt_1_;
  double mt_2_;
  
  bool lbyMediumIsolationMVArun2DBoldDMwLT_1;
  bool lbyMediumIsolationMVArun2DBoldDMwLT_2=0;
  bool antiele_1_;
  bool antimu_1_;
  bool antiele_2_;
  bool antimu_2_;

  double pt_tt_;

  double zfeld_;
  double dphi_jjtt_;
  
 public:
  HTTMLStudies(std::string const& name);
  virtual ~HTTMLStudies();

  virtual int PreAnalysis();
  virtual int Execute(TreeEvent *event);
  virtual int PostAnalysis();
  virtual void PrintInfo();

};

}

#endif
