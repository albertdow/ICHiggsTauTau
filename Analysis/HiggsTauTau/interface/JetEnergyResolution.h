#ifndef ICHiggsTauTau_HiggsTauTau_JetEnergyResolution_h
#define ICHiggsTauTau_HiggsTauTau_JetEnergyResolution_h

#include "UserCode/ICHiggsTauTau/Analysis/Core/interface/TreeEvent.h"
#include "UserCode/ICHiggsTauTau/Analysis/Core/interface/ModuleBase.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/interface/HTTConfig.h"
#include <string>
#include "boost/bind.hpp"
#include "boost/format.hpp"
#include "Math/Vector4D.h"
#include "Math/Vector4Dfwd.h"

namespace ic {

template <class T>
class JetEnergyResolution : public ModuleBase {
 private:
  CLASS_MEMBER(JetEnergyResolution, unsigned, jer_shift_mode)
  CLASS_MEMBER(JetEnergyResolution, std::string, input_label)
  CLASS_MEMBER(JetEnergyResolution, bool, EENoiseFix)

 public:
  JetEnergyResolution(std::string const& name);
  virtual ~JetEnergyResolution();

  virtual int PreAnalysis();
  virtual int Execute(TreeEvent *event);
  virtual int PostAnalysis();
  virtual void PrintInfo();
};

template <class T>
JetEnergyResolution<T>::JetEnergyResolution(std::string const& name) : ModuleBase(name) {
  input_label_ = "pfJetsPFlow";
  EENoiseFix_ = false;
}

template <class T>
JetEnergyResolution<T>::~JetEnergyResolution() {
}

template <class T>
int JetEnergyResolution<T>::PreAnalysis() {
  std::cout << "----------------------------------------" << std::endl;
  std::cout << "PreAnalysis Info for JetEnergyResolution" << std::endl;
  std::cout << "----------------------------------------" << std::endl;
  std::cout << boost::format(param_fmt()) % "input_label"         % input_label_;
  std::cout << boost::format(param_fmt()) % "jer_shift_mode"      % jer_shift_mode_;
  std::cout << boost::format(param_fmt()) % "EENoiseFix"          % EENoiseFix_;

  return 0;
}

template <class T>
int JetEnergyResolution<T>::Execute(TreeEvent *event) {
  std::vector<T *> & vec = event->GetPtrVec<T>(input_label_);
  ROOT::Math::PxPyPzEVector before(0.,0.,0.,0.);
  ROOT::Math::PxPyPzEVector after(0.,0.,0.,0.);  
  double shift = 1.;
  for (unsigned i = 0; i < vec.size(); ++i) {
    double pt = vec[i]->pt() * (vec[i]->uncorrected_energy()/vec[i]->energy());
    bool skipJet = (EENoiseFix_ && pt<50 && fabs(vec[i]->eta())>2.65 && fabs(vec[i]->eta())<3.139);  
    if(!skipJet) before += vec[i]->vector();
    shift = vec[i]->jer_shift(); //nominal
    if (jer_shift_mode_ == 1) shift *= vec[i]->jerdown_shift(); //down
    else if (jer_shift_mode_ == 2) shift *= vec[i]->jerup_shift(); //up
    shift = shift == 0 ? 1. : shift;
    vec[i]->set_vector(vec[i]->vector() * shift);
    if(!skipJet) after += vec[i]->vector();
  }
  event->Add("jer_shift", after-before);
  std::sort(vec.begin(), vec.end(), bind(&T::pt, _1) > bind(&T::pt, _2));
  
  return 0;
}

template <class T>
int JetEnergyResolution<T>::PostAnalysis() {
  return 0;
}

template <class T>
void JetEnergyResolution<T>::PrintInfo() {
  ;
}

}

#endif