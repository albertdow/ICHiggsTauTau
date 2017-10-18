#ifndef ICHiggsTauTau_HiggsTauTau_HTTVBFTriggerAnalysis_h
#define ICHiggsTauTau_HiggsTauTau_HTTVBFTriggerAnalysis_h

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
  
class HTTVBFTriggerAnalysis : public ModuleBase {
 private:
  CLASS_MEMBER(HTTVBFTriggerAnalysis, fwlite::TFileService*, fs)
  CLASS_MEMBER(HTTVBFTriggerAnalysis, std::string, channel_str)
  CLASS_MEMBER(HTTVBFTriggerAnalysis, double, min_jet_pt    )
  CLASS_MEMBER(HTTVBFTriggerAnalysis, double, max_jet_eta  )
  CLASS_MEMBER(HTTVBFTriggerAnalysis, double, min_e_pt     )
  CLASS_MEMBER(HTTVBFTriggerAnalysis, double, min_mu_pt    )
  CLASS_MEMBER(HTTVBFTriggerAnalysis, double, min_tau1_pt  )
  CLASS_MEMBER(HTTVBFTriggerAnalysis, double, min_tau2_pt  )
  CLASS_MEMBER(HTTVBFTriggerAnalysis, double, max_e_eta    )
  CLASS_MEMBER(HTTVBFTriggerAnalysis, double, max_mu_eta   )
  CLASS_MEMBER(HTTVBFTriggerAnalysis, double, max_tau_eta  )
  CLASS_MEMBER(HTTVBFTriggerAnalysis, bool, do_theory_uncert)
  
  TTree *outtree_;
  
  unsigned long long event_;
  std::vector<double> scale_variation_wts_;
  std::vector<double> NNPDF_wts_;
  std::vector<double> alpha_s_wts_;
  std::vector<double> CT10_wts_;
  std::vector<double> CT10_alpha_s_wts_;
  std::vector<double> MMHT_wts_;
  
  unsigned count_ee_;
  unsigned count_em_;
  unsigned count_et_;
  unsigned count_mm_;
  unsigned count_mt_;
  unsigned count_tt_;

  double offline_jet_1;
  double offline_jet_2;
  double offline_jet_eta_1;
  double offline_jet_eta_2;
  double offline_jet_deta;
  double offline_mjj;
  double PFJets_;
  double matchedPFJets_;
  
  double offline_tau_1;
  double offline_tau_2;
  double offline_tau_m;

  bool passed_;
  double L1_jpt_1_;
  double L1_jpt_2_;
  double L1_jeta_1_;
  double L1_jeta_2_;
  double L1_mjj_;
  double tau_lo_pt_;
  double tau_pt_2_;
  double cleanTau_lo_pt_;
  double cleanTau_pt_2_;
  double matched_vbf_jpt_1_;
  double matched_vbf_jpt_2_;
//  double matched_vbf_jpt_3_;
//  double matched_vbf_jpt_4_;
  double matched_vbf_jeta_1_;
  double matched_vbf_jeta_2_;
//  double matched_vbf_jeta_3_;
//  double matched_vbf_jeta_4_;

//  double HLTVBFPassThrough_;
  double HLTDoubleMediumIsoPFTau35_;
  double HLTDoubleMediumIsoPFTau35_2_;
  double HLTDoubleMediumIsoPFTau35_tau_;

  bool ttHLTPath1_;
  bool VBFttHLTPath1_;
  bool VBFttHLTPath2_;
  bool VBFttHLTPath3_;

  bool trg_VBF;
  bool trg_doubletau;

  int PFTausize_; 
  int HLTjetssize_;

  double pt_1_;
  double pt_2_;
  double eta_1_;
  double eta_2_;
  double phi_1_;
  double phi_2_;
  double met_;
  double mt_1_;
  double mt_2_;
  double pzeta_;
  double n_bjets_;
  unsigned n_jets_nofilter_;
  unsigned n_jets_;
  unsigned n_jetsingap_;
  double hlt_jpt_1_;
  double hlt_jpt_2_;
  double hlt_jpt_3_;
  double hlt_jpt_4_;
  double hlt_jeta_1_;
  double hlt_jeta_2_;
  double hlt_jeta_3_;
  double hlt_jeta_4_;
  double hlt_mjj_;

  double jpt_1_;
  double jpt_2_;
  double mjj_;       // Defined if n_jets >= 2
  double jdeta_;
  bool lbyMediumIsolationMVArun2DBoldDMwLT_1;
  bool lbyMediumIsolationMVArun2DBoldDMwLT_2=0;
  bool antiele_1_;
  bool antimu_1_;
  bool antiele_2_;
  bool antimu_2_;
  double pt_tt_;

  
 public:
  HTTVBFTriggerAnalysis(std::string const& name);
  virtual ~HTTVBFTriggerAnalysis();

  virtual int PreAnalysis();
  virtual int Execute(TreeEvent *event);
  virtual int PostAnalysis();
  virtual void PrintInfo();
  
  TH1D *h1;
  TCanvas *c1;
  TH1D *h2;
  TCanvas *c2;

};

}

#endif
