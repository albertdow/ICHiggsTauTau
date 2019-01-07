#include "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/interface/HTTSmearScale.h"
#include "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/interface/HTTConfig.h"
#include "UserCode/ICHiggsTauTau/interface/Electron.hh"
#include "boost/format.hpp"

namespace ic {

  HTTSmearScale::HTTSmearScale(std::string const& name) : ModuleBase(name), channel_(channel::et), strategy_(strategy::paper2013) {
  }

  HTTSmearScale::~HTTSmearScale() {
    ;
  }

  int HTTSmearScale::PreAnalysis() {
    std::cout << "-------------------------------------" << std::endl;
    std::cout << "HTTSmearScale" << std::endl;
    std::cout << "-------------------------------------" << std::endl;    
    std::cout << boost::format(param_fmt()) % "input_label"         % input_label_;
    return 0;
  }

  int HTTSmearScale::Execute(TreeEvent *event) {
    if(channel_ == channel::et || channel_ == channel::em || channel_ == channel::zee) {
      std::vector<Electron *> &electrons = event->GetPtrVec<Electron>(input_label_);
      std::map<std::size_t, double> elec_ss;
      for (unsigned i = 0; i < electrons.size() ;++i){
        float preCorr = 1.0;
        float postCorr = 1.0;

        // energy() should be equivalent to ecalTrkEnergyPreCorr()
        preCorr = electrons[i]->energy(); 
        postCorr = electrons[i]->ecalTrkEnergyPostCorr();

        float shift = postCorr/preCorr;

        // shifting pT and E shifts the full four-vector
        // as required by EGammaPOG
        electrons[i]->set_pt(electrons[i]->pt() * shift);
        electrons[i]->set_energy(electrons[i]->energy() * shift);
        elec_ss[electrons[i]->id()] = shift;
      }
      event->Add("elec_ss", elec_ss);
      return 0;
    } else return 0;
  }




  int HTTSmearScale::PostAnalysis() {
    return 0;
  }

  void HTTSmearScale::PrintInfo() {
    ;
  }

}
