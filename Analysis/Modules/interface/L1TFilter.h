#ifndef ICHiggsTauTau_Module_L1TFilter_h
#define ICHiggsTauTau_Module_L1TFilter_h

#include "UserCode/ICHiggsTauTau/Analysis/Core/interface/TreeEvent.h"
#include "UserCode/ICHiggsTauTau/Analysis/Core/interface/ModuleBase.h"
#include "UserCode/ICHiggsTauTau/interface/GenParticle.hh"
#include <string>
#include <cmath>

#include "TH1D.h"
#include "TH2D.h"
#include "TFile.h"
#include "TLorentzVector.h"
#include "TDirectory.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"

// ICHiggsTauTau Objects 
#include "UserCode/ICHiggsTauTau/interface/L1TObject.hh"
#include "UserCode/ICHiggsTauTau/interface/L1TEGamma.hh"
#include "UserCode/ICHiggsTauTau/interface/L1TMuon.hh"
#include "UserCode/ICHiggsTauTau/interface/L1TTau.hh"
#include "UserCode/ICHiggsTauTau/interface/L1TJet.hh"
#include "UserCode/ICHiggsTauTau/interface/L1TSum.hh"
#include "UserCode/ICHiggsTauTau/interface/GenJet.hh"
#include "UserCode/ICHiggsTauTau/interface/Met.hh"
#include "UserCode/ICHiggsTauTau/interface/Candidate.hh"
#include "UserCode/ICHiggsTauTau/interface/EventInfo.hh"

#include "Modules/interface/L1Cuts.h"

namespace ic {
    
class L1TFilter : public ModuleBase {
   public:
      L1TFilter(std::string const& name, std::string channel, fwlite::TFileService *fs, L1Cuts l1Cuts, std::string L1MuTag, std::string subDirName, unsigned isZeroBias);
      virtual ~L1TFilter(); 
      
      virtual int PreAnalysis();
      virtual int Execute(TreeEvent *event);
      virtual int PostAnalysis();
      virtual void PrintInfo();

   private:
      std::string channel_;
      std::string l1jets_label_;
      std::string l1electrons_label_;
      std::string l1muons_label_;
      std::string l1taus_label_;
      std::string l1met_label_;
    
      unsigned n_l1jets_;
      unsigned n_l1electrons_;
      unsigned n_l1muons_;
      unsigned n_l1taus_;
      unsigned n_l1leadtaus_;
      
      double Jet1PtCut;
      double Jet2PtCut;
      double DeltaEtaCut;
      double MjjCut;
      double EGPtCut;
      double Tau1PtCut;
      double Tau2PtCut;
      double MuPtCut;
      double AvePtCut;
      double VecPtCut;
      
      bool IsoTauFilter;
      bool IsoEGFilter;
      bool IsoMuFilter;
      bool JetFilter;
      bool DeltaRJetFilter;
      unsigned isZB;
      
      TH1D *h_L1Filter_Efficiency;
      TH1D *h_SignalEfficiency;
      TH1D *h_METRates;
      
      TH1D *h_SingleIsoTauPt          ;
      TH1D *h_SingleTauPt             ;
      TH1D *h_DoubleIsoTauPt          ;
      TH1D *h_DoubleTauPt             ;
      TH1D *h_SingleEGPt              ;
      TH1D *h_SingleIsoEGPt           ;
      TH1D *h_SingleMuPt              ;
      TH1D *h_SingleIsoMuPt           ;
      TH1D *h_SingleJetPt             ;
      TH1D *h_DoubleJetPt             ;
      TH1D *h_DoubleJetMjj            ;
      TH1D *h_DoubleJetDeltaEta       ;
      TH1D *h_DoubleJetAvePt          ;
      TH1D *h_DoubleJetVecPt          ;
      
      TH2D *h_DoubleIsoTauPt2D        ;
      TH2D *h_DoubleTauPt2D           ;
      
      TH1D *h_l1jj_VecPt;
      TH1D *h_l1jj_Diff;
      TH1D *h_l1jj_DiffOverSum;
      TH1D *h_tauEta_After;
      TH1D *h_tauEta_Before;
      
      TH1D *h_tau1Eta; 
      TH1D *h_tau2Eta; 
      TH1D *h_electron1Eta; 
      TH1D *h_electron2Eta;
      TH1D *h_muon1Eta; 
      TH1D *h_muon2Eta;
      TH1D *h_jet1Eta; 
      TH1D *h_jet2Eta; 
      TH1D *h_tau1Pt;
      TH1D *h_tau2Pt;
      TH1D *h_electron1Pt;
      TH1D *h_electron2Pt;
      TH1D *h_muon1Pt;
      TH1D *h_muon2Pt;
      TH1D *h_jet1Pt;
      TH1D *h_jet2Pt;
      TH1D *h_jetsMjj;  
      TH1D *h_jetsDeltaEta; 
      TH1D *h_jetsAvePt; 
      TH1D *h_jetsVecPt;
      
      TH1D *h_Tau1Multiplicity;
      TH1D *h_Tau2Multiplicity;
      TH1D *h_EGMultiplicity;
      TH1D *h_MuonMultiplicity;
      TH1D *h_JetMultiplicity;
      TH1D *h_LargestMjj;
      TH1D *h_LargestMjj_LeadPt;
      TH1D *h_LargestMjj_SubLeadPt;
      TH1D *h_LargestMjj_AvePt;
      TH1D *h_LargestMjj_VecPt;
      TH1D *h_LargestMjj_DeltaEta;

};
}

#endif