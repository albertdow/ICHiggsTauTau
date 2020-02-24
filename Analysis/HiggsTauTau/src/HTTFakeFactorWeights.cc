#include "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/interface/HTTFakeFactorWeights.h"
#include "UserCode/ICHiggsTauTau/interface/PFJet.hh"
#include "UserCode/ICHiggsTauTau/Analysis/Utilities/interface/FnPredicates.h"
#include "UserCode/ICHiggsTauTau/Analysis/Utilities/interface/FnPairs.h"
#include "boost/format.hpp"
#include "TMVA/Reader.h"
#include "TVector3.h"
#include "TFile.h"
#include "TString.h"
#include <boost/algorithm/string/classification.hpp>
#include <boost/algorithm/string/split.hpp> 

namespace ic {

  HTTFakeFactorWeights::HTTFakeFactorWeights(std::string const& name) : ModuleBase(name),
    channel_(channel::et), strategy_(strategy::mssmsummer16), era_(era::data_2012_rereco){ 
    met_label_ = "pfMET";
    jets_label_ = "ak4PFJetsCHS";
    ditau_label_ = "ditau";
    categories_ = "inclusive";
    do_systematics_= false;
    ff_file_= "20170330_tight";
    fracs_file_ = "";
    is_embedded_ = "";
  }

  HTTFakeFactorWeights::~HTTFakeFactorWeights() {
    ;
  }

  int HTTFakeFactorWeights::PreAnalysis() {
    std::cout << "-------------------------------------" << std::endl;
    std::cout << "HTTFakeFactorWeights" << std::endl;
    std::cout << "-------------------------------------" << std::endl;

    std::cout << boost::format(param_fmt()) % "channel"     % Channel2String(channel_);
    std::cout << boost::format(param_fmt()) % "era"         % Era2String(era_);
    std::cout << boost::format(param_fmt()) % "met_label"   % met_label_;
    std::cout << boost::format(param_fmt()) % "jets_label"  % jets_label_;
    std::cout << boost::format(param_fmt()) % "ditau_label" % ditau_label_;
    std::cout << boost::format(param_fmt()) % "ff_file"     % ff_file_;
    std::cout << boost::format(param_fmt()) % "fracs_file"  % fracs_file_;
     

    boost::split(category_names_, categories_, boost::is_any_of(","), boost::token_compress_on);
    std::string baseDir = (std::string)getenv("CMSSW_BASE") + "/src/";
    if(strategy_ == strategy::smsummer16 || strategy_ == strategy::cpsummer16 || strategy_ == strategy::legacy16 || strategy_ == strategy::cpdecays16 || strategy_ == strategy::cpsummer17 || strategy_ == strategy::cpdecays17 || strategy_ == strategy::cpdecays18) category_names_ = {"inclusive"};

    if((strategy_ == strategy::cpdecays18 || strategy_ == strategy::cpdecays16 || strategy_ == strategy::legacy16 || strategy_ == strategy::cpdecays17 ) && channel_==channel::tt) {
      TFile f((baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/"+ff_file_).c_str());
      ff_ws_ = std::shared_ptr<RooWorkspace>((RooWorkspace*)gDirectory->Get("w"));
      f.Close();

      systs_mvadm_ = {"","_qcd_syst_up","_qcd_syst_down","_wjets_syst_up","_wjets_syst_down","_qcd_met_up","_qcd_met_down","_qcd_stat_njet0_mvadm0_sig_lt3_up","_qcd_stat_njet0_mvadm0_sig_lt3_down","_qcd_stat_njet1_mvadm0_sig_lt3_up","_qcd_stat_njet1_mvadm0_sig_lt3_down","_qcd_stat_njet2_mvadm0_sig_lt3_up","_qcd_stat_njet2_mvadm0_sig_lt3_down","_qcd_stat_njet0_mvadm0_sig_gt3_up","_qcd_stat_njet0_mvadm0_sig_gt3_down","_qcd_stat_njet1_mvadm0_sig_gt3_up","_qcd_stat_njet1_mvadm0_sig_gt3_down","_qcd_stat_njet2_mvadm0_sig_gt3_up","_qcd_stat_njet2_mvadm0_sig_gt3_down","_qcd_stat_njet0_mvadm1_up","_qcd_stat_njet0_mvadm1_down","_qcd_stat_njet1_mvadm1_up","_qcd_stat_njet1_mvadm1_down","_qcd_stat_njet2_mvadm1_up","_qcd_stat_njet2_mvadm1_down","_qcd_stat_njet0_mvadm2_up","_qcd_stat_njet0_mvadm2_down","_qcd_stat_njet1_mvadm2_up","_qcd_stat_njet1_mvadm2_down","_qcd_stat_njet2_mvadm2_up","_qcd_stat_njet2_mvadm2_down","_qcd_stat_njet0_mvadm10_up","_qcd_stat_njet0_mvadm10_down","_qcd_stat_njet1_mvadm10_up","_qcd_stat_njet1_mvadm10_down","_qcd_stat_njet2_mvadm10_up","_qcd_stat_njet2_mvadm10_down","_qcd_stat_njet0_mvadm11_up","_qcd_stat_njet0_mvadm11_down","_qcd_stat_njet1_mvadm11_up","_qcd_stat_njet1_mvadm11_down","_qcd_stat_njet2_mvadm11_up","_qcd_stat_njet2_mvadm11_down","_ttbar_syst_up","_ttbar_syst_down"};

      systs_dm_ = {"","_qcd_syst_up","_qcd_syst_down","_wjets_syst_up","_wjets_syst_down","_qcd_met_up","_qcd_met_down","_qcd_stat_njet0_dm0_up","_qcd_stat_njet0_dm0_down","_qcd_stat_njet1_dm0_up","_qcd_stat_njet1_dm0_down","_qcd_stat_njet2_dm0_up","_qcd_stat_njet2_dm0_down","_qcd_stat_njet0_dm1_up","_qcd_stat_njet0_dm1_down","_qcd_stat_njet1_dm1_up","_qcd_stat_njet1_dm1_down","_qcd_stat_njet2_dm1_up","_qcd_stat_njet2_dm1_down","_qcd_stat_njet0_dm10_up","_qcd_stat_njet0_dm10_down","_qcd_stat_njet1_dm10_up","_qcd_stat_njet1_dm10_down","_qcd_stat_njet2_dm10_up","_qcd_stat_njet2_dm10_down","_qcd_stat_njet0_dm11_up","_qcd_stat_njet0_dm11_down","_qcd_stat_njet1_dm11_up","_qcd_stat_njet1_dm11_down","_qcd_stat_njet2_dm11_up","_qcd_stat_njet2_dm11_down","_ttbar_syst_up","_ttbar_syst_down"};
      systs_us_ = {"","_qcd_stat_njets0_up","_qcd_stat_njets0_down","_qcd_stat_njets1_up","_qcd_stat_njets1_down","_qcd_stat_njets2_up","_qcd_stat_njets2_down","_qcd_syst_closure_njets0_up","_qcd_syst_closure_njets0_down","_qcd_syst_closure_njets1_up","_qcd_syst_closure_njets1_down","_qcd_syst_closure_njets2_up","_qcd_syst_closure_njets2_down","_qcd_syst_osss_up","_qcd_syst_osss_down"};

      for(auto s : systs_mvadm_) {
        fns_["ff_tt_medium_mvadmbins"+s] = std::shared_ptr<RooFunctor>(
              ff_ws_->function(("ff_tt_medium_mvadmbins"+s).c_str())->functor(ff_ws_->argSet("pt,mvadm,ipsig,njets,pt_2,os,met_var_qcd")));
      }
      for(auto s : systs_dm_) {
        fns_["ff_tt_medium_dmbins"+s] = std::shared_ptr<RooFunctor>(
              ff_ws_->function(("ff_tt_medium_dmbins"+s).c_str())->functor(ff_ws_->argSet("pt,dm,njets,pt_2,os,met_var_qcd"))); 
      }

      // load us groups fake factors

      std::string us_file_ = "input/fake_factors/fakefactors_us_ws_tt_lite_2016.root";
      if(strategy_==strategy::cpdecays17) us_file_ = "input/fake_factors/fakefactors_us_ws_tt_lite_2017.root";
      if(strategy_==strategy::cpdecays18) us_file_ = "input/fake_factors/fakefactors_us_ws_tt_lite_2018.root";
      TFile f_us((baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/"+us_file_).c_str());

      ff_ws_us_ = std::shared_ptr<RooWorkspace>((RooWorkspace*)gDirectory->Get("w"));
      f_us.Close();

      for(auto s : systs_us_) {
        fns_["ff_tt_medium_us"+s] = std::shared_ptr<RooFunctor>(
              ff_ws_us_->function(("ff_tt_medium"+s).c_str())->functor(ff_ws_us_->argSet("pt,njets,pt_2,os,mvis")));
      }


      return 0;
    }

    if((strategy_ == strategy::cpdecays18 || strategy_ == strategy::cpdecays16 || strategy_ == strategy::legacy16||strategy_==strategy::cpdecays17) && (channel_==channel::mt)) {
      TFile f_fracs((baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/mva_fract_mt_2018.root").c_str());
      ff_fracs_qcd_ = (TH2D*)f_fracs.Get("QCD");
      ff_fracs_wjets_ = (TH2D*)f_fracs.Get("W");
      ff_fracs_qcd_->SetDirectory(0);
      ff_fracs_wjets_->SetDirectory(0);
      f_fracs.Close();


      TFile f((baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/"+ff_file_).c_str());
      ff_ws_ = std::shared_ptr<RooWorkspace>((RooWorkspace*)gDirectory->Get("w"));
      f.Close();

      systs_mvadm_ = {"","_wjets_syst_up","_wjets_syst_down","_wjets_met_up","_wjets_met_down","_wjets_l_pt_up","_wjets_l_pt_down","_wjets_stat_njet0_mvadm0_sig_lt3_up","_wjets_stat_njet0_mvadm0_sig_lt3_down","_wjets_stat_njet1_mvadm0_sig_lt3_up","_wjets_stat_njet1_mvadm0_sig_lt3_down","_wjets_stat_njet2_mvadm0_sig_lt3_up","_wjets_stat_njet2_mvadm0_sig_lt3_down","_wjets_stat_njet0_mvadm0_sig_gt3_up","_wjets_stat_njet0_mvadm0_sig_gt3_down","_wjets_stat_njet1_mvadm0_sig_gt3_up","_wjets_stat_njet1_mvadm0_sig_gt3_down","_wjets_stat_njet2_mvadm0_sig_gt3_up","_wjets_stat_njet2_mvadm0_sig_gt3_down","_wjets_stat_njet0_mvadm1_up","_wjets_stat_njet0_mvadm1_down","_wjets_stat_njet1_mvadm1_up","_wjets_stat_njet1_mvadm1_down","_wjets_stat_njet2_mvadm1_up","_wjets_stat_njet2_mvadm1_down","_wjets_stat_njet0_mvadm2_up","_wjets_stat_njet0_mvadm2_down","_wjets_stat_njet1_mvadm2_up","_wjets_stat_njet1_mvadm2_down","_wjets_stat_njet2_mvadm2_up","_wjets_stat_njet2_mvadm2_down","_wjets_stat_njet0_mvadm10_up","_wjets_stat_njet0_mvadm10_down","_wjets_stat_njet1_mvadm10_up","_wjets_stat_njet1_mvadm10_down","_wjets_stat_njet2_mvadm10_up","_wjets_stat_njet2_mvadm10_down","_wjets_stat_njet0_mvadm11_up","_wjets_stat_njet0_mvadm11_down","_wjets_stat_njet1_mvadm11_up","_wjets_stat_njet1_mvadm11_down","_wjets_stat_njet2_mvadm11_up","_wjets_stat_njet2_mvadm11_down","_qcd_syst_up","_qcd_syst_down","_qcd_met_up","_qcd_met_down","_qcd_l_pt_up","_qcd_l_pt_down","_qcd_stat_njet0_mvadm0_sig_lt3_up","_qcd_stat_njet0_mvadm0_sig_lt3_down","_qcd_stat_njet1_mvadm0_sig_lt3_up","_qcd_stat_njet1_mvadm0_sig_lt3_down","_qcd_stat_njet2_mvadm0_sig_lt3_up","_qcd_stat_njet2_mvadm0_sig_lt3_down","_qcd_stat_njet0_mvadm0_sig_gt3_up","_qcd_stat_njet0_mvadm0_sig_gt3_down","_qcd_stat_njet1_mvadm0_sig_gt3_up","_qcd_stat_njet1_mvadm0_sig_gt3_down","_qcd_stat_njet2_mvadm0_sig_gt3_up","_qcd_stat_njet2_mvadm0_sig_gt3_down","_qcd_stat_njet0_mvadm1_up","_qcd_stat_njet0_mvadm1_down","_qcd_stat_njet1_mvadm1_up","_qcd_stat_njet1_mvadm1_down","_qcd_stat_njet2_mvadm1_up","_qcd_stat_njet2_mvadm1_down","_qcd_stat_njet0_mvadm2_up","_qcd_stat_njet0_mvadm2_down","_qcd_stat_njet1_mvadm2_up","_qcd_stat_njet1_mvadm2_down","_qcd_stat_njet2_mvadm2_up","_qcd_stat_njet2_mvadm2_down","_qcd_stat_njet0_mvadm10_up","_qcd_stat_njet0_mvadm10_down","_qcd_stat_njet1_mvadm10_up","_qcd_stat_njet1_mvadm10_down","_qcd_stat_njet2_mvadm10_up","_qcd_stat_njet2_mvadm10_down","_qcd_stat_njet0_mvadm11_up","_qcd_stat_njet0_mvadm11_down","_qcd_stat_njet1_mvadm11_up","_qcd_stat_njet1_mvadm11_down","_qcd_stat_njet2_mvadm11_up","_qcd_stat_njet2_mvadm11_down","_ttbar_syst_up","_ttbar_syst_down"};


      systs_dm_ = {"","_wjets_syst_up","_wjets_syst_down","_wjets_met_up","_wjets_met_down","_wjets_l_pt_up","_wjets_l_pt_down","_wjets_stat_njet0_dm0_up","_wjets_stat_njet0_dm0_down","_wjets_stat_njet1_dm0_up","_wjets_stat_njet1_dm0_down","_wjets_stat_njet2_dm0_up","_wjets_stat_njet2_dm0_down","_wjets_stat_njet0_dm1_up","_wjets_stat_njet0_dm1_down","_wjets_stat_njet1_dm1_up","_wjets_stat_njet1_dm1_down","_wjets_stat_njet2_dm1_up","_wjets_stat_njet2_dm1_down","_wjets_stat_njet0_dm10_up","_wjets_stat_njet0_dm10_down","_wjets_stat_njet1_dm10_up","_wjets_stat_njet1_dm10_down","_wjets_stat_njet2_dm10_up","_wjets_stat_njet2_dm10_down","_wjets_stat_njet0_dm11_up","_wjets_stat_njet0_dm11_down","_wjets_stat_njet1_dm11_up","_wjets_stat_njet1_dm11_down","_wjets_stat_njet2_dm11_up","_wjets_stat_njet2_dm11_down","_qcd_syst_up","_qcd_syst_down","_qcd_met_up","_qcd_met_down","_qcd_l_pt_up","_qcd_l_pt_down","_qcd_stat_njet0_dm0_up","_qcd_stat_njet0_dm0_down","_qcd_stat_njet1_dm0_up","_qcd_stat_njet1_dm0_down","_qcd_stat_njet2_dm0_up","_qcd_stat_njet2_dm0_down","_qcd_stat_njet0_dm1_up","_qcd_stat_njet0_dm1_down","_qcd_stat_njet1_dm1_up","_qcd_stat_njet1_dm1_down","_qcd_stat_njet2_dm1_up","_qcd_stat_njet2_dm1_down","_qcd_stat_njet0_dm10_up","_qcd_stat_njet0_dm10_down","_qcd_stat_njet1_dm10_up","_qcd_stat_njet1_dm10_down","_qcd_stat_njet2_dm10_up","_qcd_stat_njet2_dm10_down","_qcd_stat_njet0_dm11_up","_qcd_stat_njet0_dm11_down","_qcd_stat_njet1_dm11_up","_qcd_stat_njet1_dm11_down","_qcd_stat_njet2_dm11_up","_qcd_stat_njet2_dm11_down","_ttbar_syst_up","_ttbar_syst_down"};


      for(auto s : systs_mvadm_) {
        fns_["ff_lt_medium_mvadmbins"+s] = std::shared_ptr<RooFunctor>(
              ff_ws_->function(("ff_mt_medium_mvadmbins"+s).c_str())->functor(ff_ws_->argSet("pt,mvadm,ipsig,njets,m_pt,os,met_var_qcd,met_var_w,mt,m_iso,pass_single,mvis,wjets_frac,qcd_frac,ttbar_frac")));
      }
      for(auto s : systs_dm_) {
        fns_["ff_lt_medium_dmbins"+s] = std::shared_ptr<RooFunctor>(
              ff_ws_->function(("ff_mt_medium_dmbins"+s).c_str())->functor(ff_ws_->argSet("pt,dm,njets,m_pt,os,met_var_qcd,met_var_w,mt,m_iso,pass_single,mvis,wjets_frac,qcd_frac,ttbar_frac")));
      }
      fns_["ff_lt_medium_dmbins_qcd"] = std::shared_ptr<RooFunctor>(
            ff_ws_->function("ff_mt_medium_dmbins_qcd")->functor(ff_ws_->argSet("pt,dm,njets,m_pt,os,met_var_qcd,m_iso,pass_single")));
      fns_["ff_lt_medium_dmbins_wjets"] = std::shared_ptr<RooFunctor>(
            ff_ws_->function("ff_mt_medium_dmbins_wjets")->functor(ff_ws_->argSet("pt,dm,njets,m_pt,,met_var_w,mt,pass_single,mvis")));
      fns_["ff_lt_medium_mvadmbins_qcd"] = std::shared_ptr<RooFunctor>(
            ff_ws_->function("ff_mt_medium_mvadmbins_qcd")->functor(ff_ws_->argSet("pt,mvadm,ipsig,njets,m_pt,os,met_var_qcd,m_iso,pass_single")));
      fns_["ff_lt_medium_mvadmbins_wjets"] = std::shared_ptr<RooFunctor>(
            ff_ws_->function("ff_mt_medium_mvadmbins_wjets")->functor(ff_ws_->argSet("pt,mvadm,ipsig,njets,m_pt,met_var_w,mt,pass_single,mvis")));

      // load us groups fake factors
      
      std::string us_file_ = "input/fake_factors/fakefactors_us_ws_mt_lite_2016.root";
      if(strategy_==strategy::cpdecays17) us_file_ = "input/fake_factors/fakefactors_us_ws_mt_lite_2017.root";
      if(strategy_==strategy::cpdecays18) us_file_ = "input/fake_factors/fakefactors_us_ws_mt_lite_2018.root";
      TFile f_us((baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/"+us_file_).c_str());

      ff_ws_us_ = std::shared_ptr<RooWorkspace>((RooWorkspace*)gDirectory->Get("w"));
      f_us.Close();
      systs_us_ = {"","_qcd_syst_osss_up","_qcd_syst_osss_down","_wjets_syst_mt_unc1_up","_wjets_syst_mt_unc1_down","_wjets_syst_mt_unc2_up","_wjets_syst_mt_unc2_down","_qcd_syst_closure_up","_qcd_syst_closure_down","_wjets_syst_closure_up","_wjets_syst_closure_down","_ttbar_syst_closure_up","_ttbar_syst_closure_down","_qcd_stat_njets0_unc1_up","_qcd_stat_njets0_unc1_down","_qcd_stat_njets0_unc2_up","_qcd_stat_njets0_unc2_down","_qcd_stat_njets1_unc1_up","_qcd_stat_njets1_unc1_down","_qcd_stat_njets1_unc2_up","_qcd_stat_njets1_unc2_down","_qcd_stat_njets2_unc1_up","_qcd_stat_njets2_unc1_down","_qcd_stat_njets2_unc2_up","_qcd_stat_njets2_unc2_down","_wjets_stat_njets0_unc1_up","_wjets_stat_njets0_unc1_down","_wjets_stat_njets0_unc2_up","_wjets_stat_njets0_unc2_down","_wjets_stat_njets1_unc1_up","_wjets_stat_njets1_unc1_down","_wjets_stat_njets1_unc2_up","_wjets_stat_njets1_unc2_down","_wjets_stat_njets2_unc1_up","_wjets_stat_njets2_unc1_down","_wjets_stat_njets2_unc2_up","_wjets_stat_njets2_unc2_down","_ttbar_stat_unc1_up","_ttbar_stat_unc1_down","_ttbar_stat_unc2_up","_ttbar_stat_unc2_down"};

      for(auto s : systs_us_) {
        fns_["ff_lt_medium_us"+s] = std::shared_ptr<RooFunctor>(
              ff_ws_us_->function(("ff_mt_medium"+s).c_str())->functor(ff_ws_us_->argSet("pt,njets,os,mt,mvis,pfmt")));
      }


      // load MVA scroes reader for fractions
      reader_ = new TMVA::Reader();
      reader_->AddVariable( "pt_tt", &pt_tt_ );
      reader_->AddVariable( "pt_1", &pt_1_ );
      reader_->AddVariable( "pt_2", &pt_2_ );
      reader_->AddVariable( "met", &met_ );
      reader_->AddVariable( "m_vis", &m_vis_ );
      reader_->AddVariable( "n_jets", &n_jets_ );
      reader_->AddVariable( "mjj", &mjj_ );
      reader_->AddVariable( "mva_dm_2", &mva_dm_2_ );
      reader_->AddVariable( "mt_1", &mt_1_ );
      std::string xml_file=baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/fractions_2018_mt.xml";
      if(strategy_ == strategy::legacy16) xml_file=baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/fractions_2016_mt.xml";
      reader_->BookMVA( "BDT method", xml_file );

      return 0;
    }

 
    if((strategy_ == strategy::cpdecays18 || strategy_ == strategy::cpdecays16 || strategy_ == strategy::legacy16||strategy_==strategy::cpdecays17) && (channel_==channel::et)) {

      TFile f_fracs((baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/mva_fract_et_2018.root").c_str());
      ff_fracs_qcd_ = (TH2D*)f_fracs.Get("QCD");
      ff_fracs_wjets_ = (TH2D*)f_fracs.Get("W");
      ff_fracs_qcd_->SetDirectory(0);
      ff_fracs_wjets_->SetDirectory(0);
      f_fracs.Close();
      TFile f((baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/"+ff_file_).c_str());
      ff_ws_ = std::shared_ptr<RooWorkspace>((RooWorkspace*)gDirectory->Get("w"));
      f.Close();


      systs_mvadm_ = {"","_wjets_syst_up","_wjets_syst_down","_wjets_met_up","_wjets_met_down","_wjets_l_pt_up","_wjets_l_pt_down","_wjets_stat_njet0_mvadm0_sig_lt3_up","_wjets_stat_njet0_mvadm0_sig_lt3_down","_wjets_stat_njet1_mvadm0_sig_lt3_up","_wjets_stat_njet1_mvadm0_sig_lt3_down","_wjets_stat_njet2_mvadm0_sig_lt3_up","_wjets_stat_njet2_mvadm0_sig_lt3_down","_wjets_stat_njet0_mvadm0_sig_gt3_up","_wjets_stat_njet0_mvadm0_sig_gt3_down","_wjets_stat_njet1_mvadm0_sig_gt3_up","_wjets_stat_njet1_mvadm0_sig_gt3_down","_wjets_stat_njet2_mvadm0_sig_gt3_up","_wjets_stat_njet2_mvadm0_sig_gt3_down","_wjets_stat_njet0_mvadm1_up","_wjets_stat_njet0_mvadm1_down","_wjets_stat_njet1_mvadm1_up","_wjets_stat_njet1_mvadm1_down","_wjets_stat_njet2_mvadm1_up","_wjets_stat_njet2_mvadm1_down","_wjets_stat_njet0_mvadm2_up","_wjets_stat_njet0_mvadm2_down","_wjets_stat_njet1_mvadm2_up","_wjets_stat_njet1_mvadm2_down","_wjets_stat_njet2_mvadm2_up","_wjets_stat_njet2_mvadm2_down","_wjets_stat_njet0_mvadm10_up","_wjets_stat_njet0_mvadm10_down","_wjets_stat_njet1_mvadm10_up","_wjets_stat_njet1_mvadm10_down","_wjets_stat_njet2_mvadm10_up","_wjets_stat_njet2_mvadm10_down","_wjets_stat_njet0_mvadm11_up","_wjets_stat_njet0_mvadm11_down","_wjets_stat_njet1_mvadm11_up","_wjets_stat_njet1_mvadm11_down","_wjets_stat_njet2_mvadm11_up","_wjets_stat_njet2_mvadm11_down","_qcd_syst_up","_qcd_syst_down","_qcd_met_up","_qcd_met_down","_qcd_l_pt_up","_qcd_l_pt_down","_qcd_stat_njet0_mvadm0_sig_lt3_up","_qcd_stat_njet0_mvadm0_sig_lt3_down","_qcd_stat_njet1_mvadm0_sig_lt3_up","_qcd_stat_njet1_mvadm0_sig_lt3_down","_qcd_stat_njet2_mvadm0_sig_lt3_up","_qcd_stat_njet2_mvadm0_sig_lt3_down","_qcd_stat_njet0_mvadm0_sig_gt3_up","_qcd_stat_njet0_mvadm0_sig_gt3_down","_qcd_stat_njet1_mvadm0_sig_gt3_up","_qcd_stat_njet1_mvadm0_sig_gt3_down","_qcd_stat_njet2_mvadm0_sig_gt3_up","_qcd_stat_njet2_mvadm0_sig_gt3_down","_qcd_stat_njet0_mvadm1_up","_qcd_stat_njet0_mvadm1_down","_qcd_stat_njet1_mvadm1_up","_qcd_stat_njet1_mvadm1_down","_qcd_stat_njet2_mvadm1_up","_qcd_stat_njet2_mvadm1_down","_qcd_stat_njet0_mvadm2_up","_qcd_stat_njet0_mvadm2_down","_qcd_stat_njet1_mvadm2_up","_qcd_stat_njet1_mvadm2_down","_qcd_stat_njet2_mvadm2_up","_qcd_stat_njet2_mvadm2_down","_qcd_stat_njet0_mvadm10_up","_qcd_stat_njet0_mvadm10_down","_qcd_stat_njet1_mvadm10_up","_qcd_stat_njet1_mvadm10_down","_qcd_stat_njet2_mvadm10_up","_qcd_stat_njet2_mvadm10_down","_qcd_stat_njet0_mvadm11_up","_qcd_stat_njet0_mvadm11_down","_qcd_stat_njet1_mvadm11_up","_qcd_stat_njet1_mvadm11_down","_qcd_stat_njet2_mvadm11_up","_qcd_stat_njet2_mvadm11_down","_ttbar_syst_up","_ttbar_syst_down"};

      systs_dm_ = {"","_wjets_syst_up","_wjets_syst_down","_wjets_met_up","_wjets_met_down","_wjets_l_pt_up","_wjets_l_pt_down","_wjets_stat_njet0_dm0_up","_wjets_stat_njet0_dm0_down","_wjets_stat_njet1_dm0_up","_wjets_stat_njet1_dm0_down","_wjets_stat_njet2_dm0_up","_wjets_stat_njet2_dm0_down","_wjets_stat_njet0_dm1_up","_wjets_stat_njet0_dm1_down","_wjets_stat_njet1_dm1_up","_wjets_stat_njet1_dm1_down","_wjets_stat_njet2_dm1_up","_wjets_stat_njet2_dm1_down","_wjets_stat_njet0_dm10_up","_wjets_stat_njet0_dm10_down","_wjets_stat_njet1_dm10_up","_wjets_stat_njet1_dm10_down","_wjets_stat_njet2_dm10_up","_wjets_stat_njet2_dm10_down","_wjets_stat_njet0_dm11_up","_wjets_stat_njet0_dm11_down","_wjets_stat_njet1_dm11_up","_wjets_stat_njet1_dm11_down","_wjets_stat_njet2_dm11_up","_wjets_stat_njet2_dm11_down","_qcd_syst_up","_qcd_syst_down","_qcd_met_up","_qcd_met_down","_qcd_l_pt_up","_qcd_l_pt_down","_qcd_stat_njet0_dm0_up","_qcd_stat_njet0_dm0_down","_qcd_stat_njet1_dm0_up","_qcd_stat_njet1_dm0_down","_qcd_stat_njet2_dm0_up","_qcd_stat_njet2_dm0_down","_qcd_stat_njet0_dm1_up","_qcd_stat_njet0_dm1_down","_qcd_stat_njet1_dm1_up","_qcd_stat_njet1_dm1_down","_qcd_stat_njet2_dm1_up","_qcd_stat_njet2_dm1_down","_qcd_stat_njet0_dm10_up","_qcd_stat_njet0_dm10_down","_qcd_stat_njet1_dm10_up","_qcd_stat_njet1_dm10_down","_qcd_stat_njet2_dm10_up","_qcd_stat_njet2_dm10_down","_qcd_stat_njet0_dm11_up","_qcd_stat_njet0_dm11_down","_qcd_stat_njet1_dm11_up","_qcd_stat_njet1_dm11_down","_qcd_stat_njet2_dm11_up","_qcd_stat_njet2_dm11_down","_ttbar_syst_up","_ttbar_syst_down"};

      for(auto s : systs_mvadm_) {
        fns_["ff_lt_medium_mvadmbins"+s] = std::shared_ptr<RooFunctor>(
              ff_ws_->function(("ff_et_medium_mvadmbins"+s).c_str())->functor(ff_ws_->argSet("pt,mvadm,ipsig,njets,e_pt,os,met_var_qcd,met_var_w,mt,e_iso,pass_single,mvis,wjets_frac,qcd_frac,ttbar_frac")));
      }
      for(auto s : systs_dm_) {
        fns_["ff_lt_medium_dmbins"+s] = std::shared_ptr<RooFunctor>(
              ff_ws_->function(("ff_et_medium_dmbins"+s).c_str())->functor(ff_ws_->argSet("pt,dm,njets,e_pt,os,met_var_qcd,met_var_w,mt,e_iso,pass_single,mvis,wjets_frac,qcd_frac,ttbar_frac")));
      }
      fns_["ff_lt_medium_dmbins_qcd"] = std::shared_ptr<RooFunctor>(
            ff_ws_->function("ff_et_medium_dmbins_qcd")->functor(ff_ws_->argSet("pt,dm,njets,e_pt,os,met_var_qcd,e_iso,pass_single")));
      fns_["ff_lt_medium_dmbins_wjets"] = std::shared_ptr<RooFunctor>(
            ff_ws_->function("ff_et_medium_dmbins_wjets")->functor(ff_ws_->argSet("pt,dm,njets,e_p,met_var_w,mt,pass_single,mvis")));
      fns_["ff_lt_medium_mvadmbins_qcd"] = std::shared_ptr<RooFunctor>(
            ff_ws_->function("ff_et_medium_mvadmbins_qcd")->functor(ff_ws_->argSet("pt,mvadm,ipsig,njets,e_pt,os,met_var_qcd,e_iso,pass_single")));
      fns_["ff_lt_medium_mvadmbins_wjets"] = std::shared_ptr<RooFunctor>(
            ff_ws_->function("ff_et_medium_mvadmbins_wjets")->functor(ff_ws_->argSet("pt,mvadm,ipsig,njets,e_pt,met_var_w,mt,pass_single,mvis")));

      // load us groups fake factors

      std::string us_file_ = "input/fake_factors/fakefactors_us_ws_et_lite_2016.root";
      if(strategy_==strategy::cpdecays17) us_file_ = "input/fake_factors/fakefactors_us_ws_et_lite_2017.root";
      if(strategy_==strategy::cpdecays18) us_file_ = "input/fake_factors/fakefactors_us_ws_et_lite_2018.root";
      TFile f_us((baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/"+us_file_).c_str());

      ff_ws_us_ = std::shared_ptr<RooWorkspace>((RooWorkspace*)gDirectory->Get("w"));
      f_us.Close();
      systs_us_ = {"","_qcd_syst_osss_up","_qcd_syst_osss_down","_wjets_syst_mt_unc1_up","_wjets_syst_mt_unc1_down","_wjets_syst_mt_unc2_up","_wjets_syst_mt_unc2_down","_qcd_syst_closure_up","_qcd_syst_closure_down","_wjets_syst_closure_up","_wjets_syst_closure_down","_ttbar_syst_closure_up","_ttbar_syst_closure_down","_qcd_stat_njets0_unc1_up","_qcd_stat_njets0_unc1_down","_qcd_stat_njets0_unc2_up","_qcd_stat_njets0_unc2_down","_qcd_stat_njets1_unc1_up","_qcd_stat_njets1_unc1_down","_qcd_stat_njets1_unc2_up","_qcd_stat_njets1_unc2_down","_qcd_stat_njets2_unc1_up","_qcd_stat_njets2_unc1_down","_qcd_stat_njets2_unc2_up","_qcd_stat_njets2_unc2_down","_wjets_stat_njets0_unc1_up","_wjets_stat_njets0_unc1_down","_wjets_stat_njets0_unc2_up","_wjets_stat_njets0_unc2_down","_wjets_stat_njets1_unc1_up","_wjets_stat_njets1_unc1_down","_wjets_stat_njets1_unc2_up","_wjets_stat_njets1_unc2_down","_wjets_stat_njets2_unc1_up","_wjets_stat_njets2_unc1_down","_wjets_stat_njets2_unc2_up","_wjets_stat_njets2_unc2_down","_ttbar_stat_unc1_up","_ttbar_stat_unc1_down","_ttbar_stat_unc2_up","_ttbar_stat_unc2_down"};

      for(auto s : systs_us_) {
        fns_["ff_lt_medium_us"+s] = std::shared_ptr<RooFunctor>(
              ff_ws_us_->function(("ff_et_medium"+s).c_str())->functor(ff_ws_us_->argSet("pt,njets,os,mt,mvis,pfmt")));
      }

      // load MVA scroes reader for fractions
      reader_ = new TMVA::Reader();
      reader_->AddVariable( "pt_tt", &pt_tt_ );
      reader_->AddVariable( "pt_1", &pt_1_ );
      reader_->AddVariable( "pt_2", &pt_2_ );
      reader_->AddVariable( "met", &met_ );
      reader_->AddVariable( "m_vis", &m_vis_ );
      reader_->AddVariable( "n_jets", &n_jets_ );
      reader_->AddVariable( "mjj", &mjj_ );
      reader_->AddVariable( "mva_dm_2", &mva_dm_2_ );
      reader_->AddVariable( "mt_1", &mt_1_ );
      std::string xml_file=baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/fractions_2018_et.xml";
      if(strategy_ == strategy::legacy16) xml_file=baseDir+"UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/fractions_2016_et.xml";
      reader_->BookMVA( "BDT method", xml_file );

      return 0;
    }
    
    std::string channel = Channel2String(channel_);
    for(unsigned i=0; i<category_names_.size(); ++i){
      std::string ff_file_name;
      if(strategy_ == strategy::mssmsummer16) ff_file_name = "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/Jet2TauFakesFiles/"+ff_file_+"/"+channel+"/"+category_names_[i]+"/fakeFactors_"+ff_file_+".root";
      if(strategy_ == strategy::smsummer16 || strategy_ == strategy::cpsummer16){
        ff_file_name = "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/Jet2TauFakesFiles2016/"+ff_file_;
      }
      if(strategy_ == strategy::cpsummer17 || strategy_ == strategy::cpdecays17){
        ff_file_name = "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/Jet2TauFakesFilesNew/"+ff_file_;
      }
      if(strategy_ == strategy::cpdecays18){
        ff_file_name = "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/input/fake_factors/Jet2TauFakesFiles2018New/"+ff_file_;
      }

      ff_file_name = baseDir + ff_file_name;
      
      std::string map_key = category_names_[i];
      std::string map_name = "ff_map_"+channel+"_"+map_key;
      if(strategy_ != strategy::cpdecays18 && strategy_ != strategy::cpdecays16 && strategy_ != strategy::legacy16 && strategy_!=strategy::cpdecays17){
        if(ProductExists(map_name)){
          fake_factors_[map_key] = GetProduct<std::shared_ptr<FakeFactor>>(map_name);
          std::cout << "Getting " << fake_factors_[map_key] << std::endl;
        } else {
          TFile* ff_file = new TFile(ff_file_name.c_str());
          FakeFactor* ff = (FakeFactor*)ff_file->Get("ff_comb");
          fake_factors_[map_key]  = std::shared_ptr<FakeFactor>(ff);
          AddToProducts(map_name, fake_factors_[map_key]);
          std::cout << "Adding " << fake_factors_[map_key] << std::endl;
          ff_file->Close();
          delete ff_file;
        }
      }
    }
    
    if(fracs_file_!="") {
      TFile f(fracs_file_.c_str());
      w_ = std::shared_ptr<RooWorkspace>((RooWorkspace*)gDirectory->Get("w"));
      f.Close();
       
      if(false){      
        fns_["w_et_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("w_et_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_et_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_et_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_et_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_et_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["w_et_ss_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("w_et_ss_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_et_ss_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_et_ss_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_et_ss_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_et_ss_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["w_et_highmt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("w_et_highmt_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_et_highmt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_et_highmt_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_et_highmt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_et_highmt_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["w_mt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("w_mt_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_mt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_mt_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_mt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_mt_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["w_mt_ss_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("w_mt_ss_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_mt_ss_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_mt_ss_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_mt_ss_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_mt_ss_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["w_mt_highmt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("w_mt_highmt_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_mt_highmt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_mt_highmt_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_mt_highmt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_mt_highmt_fracs")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["w_tt_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("w_tt_fracs_1")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_tt_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_tt_fracs_1")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_tt_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_tt_fracs_1")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["dy_tt_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("dy_tt_fracs_1")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["w_tt_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("w_tt_fracs_2")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_tt_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_tt_fracs_2")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_tt_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_tt_fracs_2")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["dy_tt_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("dy_tt_fracs_2")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["w_tt_ss_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("w_tt_ss_fracs_1")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_tt_ss_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_tt_ss_fracs_1")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_tt_ss_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_tt_ss_fracs_1")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["dy_tt_ss_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("dy_tt_ss_fracs_1")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["w_tt_ss_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("w_tt_ss_fracs_2")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["qcd_tt_ss_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_tt_ss_fracs_2")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["ttbar_tt_ss_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_tt_ss_fracs_2")->functor(w_->argSet("pt,njets,nbjets")));
        fns_["dy_tt_ss_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("dy_tt_ss_fracs_2")->functor(w_->argSet("pt,njets,nbjets")));
      } else {
        fns_["w_et_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("w_et_fracs")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["qcd_et_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_et_fracs")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["ttbar_et_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_et_fracs")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));

        fns_["w_mt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("w_mt_fracs")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["qcd_mt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_mt_fracs")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["ttbar_mt_fracs"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_mt_fracs")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));

        fns_["w_tt_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("w_tt_fracs_1")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["qcd_tt_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_tt_fracs_1")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["ttbar_tt_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_tt_fracs_1")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["dy_tt_fracs_1"] = std::shared_ptr<RooFunctor>(
              w_->function("dy_tt_fracs_1")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["w_tt_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("w_tt_fracs_2")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["qcd_tt_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("qcd_tt_fracs_2")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["ttbar_tt_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("ttbar_tt_fracs_2")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
        fns_["dy_tt_fracs_2"] = std::shared_ptr<RooFunctor>(
              w_->function("dy_tt_fracs_2")->functor(w_->argSet("m_sv,pt_tt,njets,mjj,sjdphi")));
      } 
    }

    return 0;
  }

  int HTTFakeFactorWeights::Execute(TreeEvent *event) {
      
    if(channel_ != channel::et && channel_ != channel::mt && channel_ != channel::tt) return 0;

    Met * met = event->GetPtr<Met>(met_label_);
    std::vector<PFJet*> jets = event->GetPtrVec<PFJet>(jets_label_);
    std::vector<PFJet*> bjets = jets;
    ic::erase_if(bjets,!boost::bind(MinPtMaxEta, _1, 20.0, 2.4));
    ic::erase_if(jets,!boost::bind(MinPtMaxEta, _1, 30.0, 4.7));
    
    std::string btag_label       = "pfCombinedInclusiveSecondaryVertexV2BJetTags";
    std::string btag_label_extra = "";
    double btag_wp (1.0);
    auto filterBTagSumTight = [btag_label, btag_label_extra, btag_wp] (PFJet* s1) -> bool {
      return s1->GetBDiscriminator(btag_label) + s1->GetBDiscriminator(btag_label_extra) > btag_wp;
    };
    if(strategy_ == strategy::mssmsummer16 || strategy_ == strategy::smsummer16 || strategy_ == strategy::cpsummer16 || strategy_ == strategy::legacy16 || strategy_ == strategy::cpdecays16) btag_wp = 0.8484;
    // if(strategy_ == strategy::cpsummer17 || strategy_ == strategy::cpdecays17 || strategy_ == strategy::cpdecays18) btag_wp = 0.8838;
    if (era_ == era::data_2017) {
      btag_wp          = 0.4941;
      btag_label       = "pfDeepCSVJetTags:probb";
      btag_label_extra = "pfDeepCSVJetTags:probbb";
    }
    if (era_ == era::data_2018) {
      btag_wp          = 0.4184;
      btag_label       = "pfDeepCSVJetTags:probb";
      btag_label_extra = "pfDeepCSVJetTags:probbb";
    } 
    if (era_ == era::data_2017 || era_ == era::data_2018) {
      if (event->Exists("retag_result")) {
        auto const& retag_result = event->Get<std::map<std::size_t,bool>>("retag_result"); 
        ic::erase_if(bjets, !boost::bind(IsReBTagged, _1, retag_result));
      } else{ 
        ic::erase_if_not(bjets, filterBTagSumTight);
      } 
    } 
    else{
      if (event->Exists("retag_result")) {
        auto const& retag_result = event->Get<std::map<std::size_t,bool>>("retag_result"); 
        ic::erase_if(bjets, !boost::bind(IsReBTagged, _1, retag_result));
      } else{ 
        ic::erase_if(bjets, boost::bind(&PFJet::GetBDiscriminator, _1, btag_label) < btag_wp);
      } 
    }
    
    std::vector<CompositeCandidate *> const& ditau_vec = event->GetPtrVec<CompositeCandidate>(ditau_label_);
    CompositeCandidate const* ditau = ditau_vec.at(0);
    Candidate const* lep1 = ditau->GetCandidate("lepton1");
    Candidate const* lep2 = ditau->GetCandidate("lepton2");
    
    // Get all inputs needed by FF 
    pt_1_ = lep1->pt();  
    pt_2_ = lep2->pt();
    m_vis_ = ditau->M();
    mt_1_ = MT(lep1, met);

    double met_var_qcd = met->pt()*cos(ROOT::Math::VectorUtil::DeltaPhi(met->vector(),lep2->vector()))/pt_2_;

    Met* newmet = new Met();
    ROOT::Math::PtEtaPhiEVector newvec;
    newvec.SetPxPyPzE(lep1->vector().Px(), lep1->vector().Py(),0.,lep1->pt());
    newmet->set_vector(met->vector()+newvec);

    double met_var_w = newmet->pt()*cos(ROOT::Math::VectorUtil::DeltaPhi(newmet->vector(),lep2->vector()))/pt_2_;

    double m_sv_=-9999;
    if (event->Exists("svfitMass")) {
      m_sv_ = event->Get<double>("svfitMass");
    } else {
      //m_sv_ = -9999;
      m_sv_ = m_vis_*1.4; // not intended for use in a propper analysis but quick fix for cases when sv fit mas has not been calculated yet. 1.4 factor is roughly the ratio of m_sv/m_vis for QCD/W jets events
    }
    pt_tt_ = (ditau->vector() + met->vector()).pt();   
    met_ = met->pt();   
 
    double iso_1_ = 0;
    if (channel_ == channel::et) {
      Electron const* elec = dynamic_cast<Electron const*>(lep1);
      EventInfo *eventInfo = event->GetPtr<EventInfo>("eventInfo");
      iso_1_ = PF03EAIsolationVal(elec, eventInfo->jet_rho());
    } else if (channel_ == channel::mt){
      Muon const* muon = dynamic_cast<Muon const*>(lep1);
      iso_1_ = PF04IsolationVal(muon, 0.5, 0);
    }
    
    double tau_decaymode_1_=0;
    double tau_decaymode_2_=0;
    if(channel_ == channel::et || channel_ == channel::mt){
      Tau const* tau = dynamic_cast<Tau const*>(lep2);
      tau_decaymode_2_ = tau->decay_mode();
    } else if (channel_ == channel::tt){
      Tau const* tau1 = dynamic_cast<Tau const*>(lep1);
      Tau const* tau2 = dynamic_cast<Tau const*>(lep2);
      tau_decaymode_1_ = tau1->decay_mode();
      tau_decaymode_2_ = tau2->decay_mode();  
    }
    
    n_jets_ = (double)jets.size();
    mjj_ = 0;
    if(n_jets_>1) mjj_ = (jets[0]->vector()+jets[1]->vector()).M();    

    double sjdphi_ = -9999;
    if(n_jets_>1) sjdphi_ =  std::fabs(ROOT::Math::VectorUtil::DeltaPhi(jets[0]->vector(), jets[1]->vector()));
 
    std::vector<double> inputs;
    std::vector<double> tt_inputs_1;
    std::vector<double> tt_inputs_2;
    if(strategy_ == strategy::mssmsummer16) {
      inputs.resize(6);
      tt_inputs_1.resize(6);
      tt_inputs_2.resize(6);
      if(channel_ == channel::et || channel_ == channel::mt){
        inputs[0] = pt_2_; inputs[1] = tau_decaymode_2_; inputs[2] = n_jets_; inputs[3] = m_vis_; inputs[4] = mt_1_; inputs[5] = iso_1_;    
      } else if (channel_ == channel::tt){
        double mt_tot_ = sqrt(pow(MT(lep1, met),2) + pow(MT(lep2, met),2) + pow(MT(lep1, lep2),2));  
        tt_inputs_1[0] = pt_1_; tt_inputs_1[1] = pt_2_; tt_inputs_1[2] = tau_decaymode_1_; tt_inputs_1[3] = n_jets_; tt_inputs_1[4] = m_vis_; tt_inputs_1[5] = mt_tot_;
        tt_inputs_2[0] = pt_2_; tt_inputs_2[1] = pt_1_; tt_inputs_2[2] = tau_decaymode_2_; tt_inputs_2[3] = n_jets_; tt_inputs_2[4] = m_vis_; tt_inputs_2[5] = mt_tot_;
      }
      // Need to loop over all categories and add a ff weight to the event for each
      for(unsigned i=0; i<category_names_.size(); ++i){
        std::string map_key = category_names_[i];
        
        // Retrieve fake factors and add to event as weights
        if(channel_ == channel::et || channel_ == channel::mt){
          double ff_nom = fake_factors_[map_key]->value(inputs);
          event->Add("wt_ff_"+map_key, ff_nom);
          
          if(do_systematics_){
            std::vector<std::string> systematics = {"ff_qcd_syst_up","ff_qcd_syst_down","ff_qcd_dm0_njet0_stat_up","ff_qcd_dm0_njet0_stat_down","ff_qcd_dm0_njet1_stat_up","ff_qcd_dm0_njet1_stat_down","ff_qcd_dm1_njet0_stat_up","ff_qcd_dm1_njet0_stat_down","ff_qcd_dm1_njet1_stat_up","ff_qcd_dm1_njet1_stat_down","ff_w_syst_up","ff_w_syst_down","ff_w_dm0_njet0_stat_up","ff_w_dm0_njet0_stat_down","ff_w_dm0_njet1_stat_up","ff_w_dm0_njet1_stat_down","ff_w_dm1_njet0_stat_up","ff_w_dm1_njet0_stat_down","ff_w_dm1_njet1_stat_up","ff_w_dm1_njet1_stat_down","ff_tt_syst_up","ff_tt_syst_down","ff_tt_dm0_njet0_stat_up","ff_tt_dm0_njet0_stat_down","ff_tt_dm0_njet1_stat_up","ff_tt_dm0_njet1_stat_down","ff_tt_dm1_njet0_stat_up","ff_tt_dm1_njet0_stat_down" ,"ff_tt_dm1_njet1_stat_up","ff_tt_dm1_njet1_stat_down"};
            for(unsigned j=0; j<systematics.size(); ++j){
              std::string syst = systematics[j];
              double ff_syst = fake_factors_[map_key]->value(inputs,syst);
              std::string syst_name = "wt_"+map_key+"_"+syst;
              event->Add(syst_name, ff_syst);
            } 
          }
        } else if(channel_ == channel::tt){
          double ff_nom_1 = fake_factors_[map_key]->value(tt_inputs_1)*0.5;
          double ff_nom_2 = fake_factors_[map_key]->value(tt_inputs_2)*0.5;
          event->Add("wt_ff_"+map_key, ff_nom_1);
          event->Add("wt_ff_"+map_key+"_2", ff_nom_2);
          
          if(do_systematics_){
            std::vector<std::string> systematics = {"ff_qcd_syst_up","ff_qcd_syst_down","ff_qcd_dm0_njet0_stat_up","ff_qcd_dm0_njet0_stat_down","ff_qcd_dm0_njet1_stat_up","ff_qcd_dm0_njet1_stat_down","ff_qcd_dm1_njet0_stat_up","ff_qcd_dm1_njet0_stat_down","ff_qcd_dm1_njet1_stat_up","ff_qcd_dm1_njet1_stat_down","ff_w_syst_up","ff_w_syst_down","ff_tt_syst_up","ff_tt_syst_down", "ff_w_frac_syst_up", "ff_w_frac_syst_down", "ff_tt_frac_syst_up", "ff_tt_frac_syst_down", "ff_dy_frac_syst_up", "ff_dy_frac_syst_down"};
            
            for(unsigned j=0; j<systematics.size(); ++j){
              std::string syst = systematics[j];
              double ff_syst_1 = fake_factors_[map_key]->value(tt_inputs_1,syst)*0.5;
              double ff_syst_2 = fake_factors_[map_key]->value(tt_inputs_2,syst)*0.5;
              std::string syst_name = "wt_"+map_key+"_"+syst;
              event->Add(syst_name+"_1", ff_syst_1);
              event->Add(syst_name+"_2", ff_syst_2);
            } 
          }
        }
      }
    } else if(strategy_ == strategy::smsummer16 || true) {

      double real_frac=0;
      double real_frac_2=0;
      inputs.resize(9);
      if(true||(strategy_ == strategy::cpsummer17 || strategy_ == strategy::cpdecays17 || strategy_ == strategy::cpdecays18)){
        tt_inputs_1.resize(8);
        tt_inputs_2.resize(8); 
      } else {
        tt_inputs_1.resize(9);
        tt_inputs_2.resize(9);
      }
      if((channel_ == channel::et || channel_ == channel::mt)&&false){
        std::vector<double> args = {m_sv_,pt_tt_,n_jets_,mjj_,sjdphi_};
        double qcd_frac=0.5, w_frac=0.5, tt_frac=0.0;
        if(channel_ == channel::et){
          qcd_frac = fns_["qcd_et_fracs"]->eval(args.data());  
          w_frac = fns_["w_et_fracs"]->eval(args.data());
          tt_frac = fns_["ttbar_et_fracs"]->eval(args.data());
          real_frac = 1-qcd_frac-w_frac-tt_frac;
        }
        if(channel_ == channel::mt){
          std::vector<double> args = {m_sv_,pt_tt_,n_jets_,mjj_,sjdphi_};
          qcd_frac = fns_["qcd_mt_fracs"]->eval(args.data());  
          w_frac = fns_["w_mt_fracs"]->eval(args.data());
          tt_frac = fns_["ttbar_mt_fracs"]->eval(args.data());
          real_frac = 1-qcd_frac-w_frac-tt_frac;
        }
        // for some bins the fractions can be 0 (if all background is accounted for by real taus) in this case take W fraction as 1
        if(qcd_frac+w_frac+tt_frac<=0) {
          qcd_frac = 0.0;
          w_frac = 1.0;
          tt_frac = 0.0;
        }

        // make sure fractions always sum to 1
        double tot_frac = qcd_frac+w_frac+tt_frac;
        qcd_frac /= tot_frac;
        w_frac /= tot_frac;
        tt_frac /= tot_frac;

        inputs[0] = pt_2_; inputs[1] = tau_decaymode_2_; inputs[2] = n_jets_; inputs[3] = m_vis_; inputs[4] = mt_1_; inputs[5] = iso_1_; inputs[6] = qcd_frac; inputs[7] = w_frac; inputs[8] = tt_frac;
      } else if (channel_ == channel::tt){
        std::vector<double> args_1 = {m_sv_,pt_tt_,n_jets_,mjj_,sjdphi_};
        std::vector<double> args_2 = {m_sv_,pt_tt_,n_jets_,mjj_,sjdphi_};
        double qcd_frac_1=1.0, w_frac_1=0.0, tt_frac_1=0.0, dy_frac_1=0.0, qcd_frac_2=1.0, w_frac_2=0.0, tt_frac_2=0.0, dy_frac_2=0.0;

        if(fracs_file_!="") {
          qcd_frac_1 = fns_["qcd_tt_fracs_1"]->eval(args_1.data());  
          w_frac_1 = fns_["w_tt_fracs_1"]->eval(args_1.data());
          tt_frac_1 = fns_["ttbar_tt_fracs_1"]->eval(args_1.data());
          dy_frac_1 = fns_["dy_tt_fracs_1"]->eval(args_1.data());
          qcd_frac_2 = fns_["qcd_tt_fracs_2"]->eval(args_2.data());  
          w_frac_2 = fns_["w_tt_fracs_2"]->eval(args_2.data());
          tt_frac_2 = fns_["ttbar_tt_fracs_2"]->eval(args_2.data());
          dy_frac_2 = fns_["dy_tt_fracs_2"]->eval(args_2.data());
          real_frac = 1-qcd_frac_1-w_frac_1-tt_frac_1-dy_frac_1;
          real_frac_2 = 1-qcd_frac_2-w_frac_2-tt_frac_2-dy_frac_2;
        }
        // for some bins the fractions can be 0 (if all background is accounted for by real taus) in this case take QCD fraction as 1
        if(qcd_frac_1+w_frac_1+tt_frac_1<=0) {
          qcd_frac_1 = 1.0;
          w_frac_1 = 0.0;
          tt_frac_1 = 0.0;
        }
        if(qcd_frac_2+w_frac_2+tt_frac_2<=0) {
          qcd_frac_2 = 1.0;
          w_frac_2 = 0.0;
          tt_frac_2 = 0.0;
        }

        // make sure fractions always sum to 1
        double tot_frac_1 = qcd_frac_1+w_frac_1+tt_frac_1;
        double tot_frac_2 = qcd_frac_2+w_frac_2+tt_frac_2;
        qcd_frac_1 /= tot_frac_1;
        w_frac_1 /= tot_frac_1;
        tt_frac_1 /= tot_frac_1;
        qcd_frac_2 /= tot_frac_2;
        w_frac_2 /= tot_frac_2;
        tt_frac_2 /= tot_frac_2;

        if(true || (strategy_ == strategy::cpsummer17 || strategy_ == strategy::cpdecays17 || strategy_ == strategy::cpdecays18)) {
          tt_inputs_1[0] = pt_1_; tt_inputs_1[1] = pt_2_; tt_inputs_1[2] = tau_decaymode_1_; tt_inputs_1[3] = n_jets_; tt_inputs_1[4] = m_vis_; tt_inputs_1[5] = qcd_frac_1; tt_inputs_1[6] = w_frac_1+dy_frac_1; tt_inputs_1[7] = tt_frac_1; 
          tt_inputs_2[0] = pt_2_; tt_inputs_2[1] = pt_1_; tt_inputs_2[2] = tau_decaymode_2_; tt_inputs_2[3] = n_jets_; tt_inputs_2[4] = m_vis_; tt_inputs_2[5] = qcd_frac_2; tt_inputs_2[6] = w_frac_2+dy_frac_2; tt_inputs_2[7] = tt_frac_2; 
        } else {
          tt_inputs_1[0] = pt_1_; tt_inputs_1[1] = pt_2_; tt_inputs_1[2] = tau_decaymode_1_; tt_inputs_1[3] = n_jets_; tt_inputs_1[4] = m_vis_; tt_inputs_1[5] = qcd_frac_1; tt_inputs_1[6] = w_frac_1; tt_inputs_1[7] = tt_frac_1; tt_inputs_1[8] = dy_frac_1;
          tt_inputs_2[0] = pt_2_; tt_inputs_2[1] = pt_1_; tt_inputs_2[2] = tau_decaymode_2_; tt_inputs_2[3] = n_jets_; tt_inputs_2[4] = m_vis_; tt_inputs_2[5] = qcd_frac_2; tt_inputs_2[6] = w_frac_2; tt_inputs_2[7] = tt_frac_2; tt_inputs_2[8] = dy_frac_2;
        }
      }
      std::string map_key = "inclusive";
      // Retrieve fake factors and add to event as weights
      if(channel_ == channel::et || channel_ == channel::mt){

        if(strategy_ == strategy::cpdecays17 || strategy_ == strategy::cpdecays18 || strategy_ == strategy::legacy16) {
          std::size_t id = 0;
          if(channel_==channel::mt){ 
            Muon const* muon = dynamic_cast<Muon const*>(lep1);
           id = muon->id();
          }
          if(channel_==channel::et){ 
            Electron const* elec = dynamic_cast<Electron const*>(lep1);
           id = elec->id();
          }

          Tau const* tau = dynamic_cast<Tau const*>(lep2);

          std::vector<ic::PFCandidate*> pfcands =  event->GetPtrVec<ic::PFCandidate>("pfCandidates");
          std::vector<ic::Vertex*> & vertex_vec = event->GetPtrVec<ic::Vertex>("vertices");
          std::vector<ic::Vertex*> & refit_vertex_vec = event->GetPtrVec<ic::Vertex>("refittedVerticesBS");
          ic::Vertex* refit_vertex = vertex_vec[0];
          for(unsigned i=0; i<refit_vertex_vec.size();++i) {
            Vertex * v = refit_vertex_vec[i];
            if(v->id() == tau->id()+id) refit_vertex = v;
          }

          double pass_single = 1.;
          if(channel_==channel::mt) {
            bool trg_singlemuon;
            if (!event->Exists("trg_singlemuon")) trg_singlemuon = true;
            else  trg_singlemuon = event->Get<bool>("trg_singlemuon"); 
            if(strategy_==strategy::legacy16) {
              if(!(pt_1_>23&&trg_singlemuon)) pass_single=0.;
            } else {
              if(!(pt_1_>25&&trg_singlemuon)) pass_single=0.;
            }
          }

          if(channel_==channel::et) {
            bool trg_singleelectron;
            if (!event->Exists("trg_singleelectron")) trg_singleelectron = true;
            else  trg_singleelectron = event->Get<bool>("trg_singleelectron");
            if(era_ == era::data_2017) {
              if(!(pt_1_>28&&trg_singleelectron)) pass_single=0.;
            } else if(era_ == era::data_2018) {
              if(!(pt_1_>33&&trg_singleelectron)) pass_single=0.;
            }
          }
          if(era_ == era::data_2016) pass_single=1.;


          double ipsig = IPAndSignificance(tau, refit_vertex, pfcands).second;

          mva_dm_2_=tau->HasTauID("MVADM2017v1") ? tau->GetTauID("MVADM2017v1") : -1.;

          // get mva fractions
          std::vector<float> scores = reader_->EvaluateMulticlass("BDT method");
          double qcd_score = scores[1];
          double w_score = scores[0];
          
          event->Add("w_frac_score",  w_score);
          event->Add("qcd_frac_score",  qcd_score);

          double w_frac = ff_fracs_wjets_->GetBinContent(ff_fracs_wjets_->FindBin(qcd_score,w_score));
          double qcd_frac = ff_fracs_qcd_->GetBinContent(ff_fracs_qcd_->FindBin(qcd_score,w_score));
          double ttbar_frac = 1. - w_frac - qcd_frac;

          bool isOS = PairOppSign(ditau);
          double os = 1.;
          if(!isOS) os=0.;
 
          auto args = std::vector<double>{pt_2_,mva_dm_2_,ipsig,n_jets_,pt_1_,os,met_var_qcd,met_var_w,mt_1_, iso_1_,pass_single,m_vis_,w_frac,qcd_frac,ttbar_frac};
          double ff_nom = fns_["ff_lt_medium_mvadmbins"]->eval(args.data());
          event->Add("wt_ff_1",  ff_nom);

          auto args_qcd = std::vector<double>{pt_2_,mva_dm_2_,ipsig,n_jets_,pt_1_,met_var_qcd,iso_1_,pass_single};
          auto args_w = std::vector<double>{pt_2_,mva_dm_2_,ipsig,n_jets_,pt_1_,met_var_w,mt_1_,pass_single,m_vis_};
          ff_nom = fns_["ff_lt_medium_mvadmbins_qcd"]->eval(args_qcd.data());
          event->Add("wt_ff_qcd_1",  ff_nom);
          ff_nom = fns_["ff_lt_medium_mvadmbins_wjets"]->eval(args_w.data());
          event->Add("wt_ff_wjets_1",  ff_nom);

          auto args_dm = std::vector<double>{pt_2_,tau_decaymode_2_,n_jets_,pt_1_,os,met_var_qcd,met_var_w,mt_1_,iso_1_,pass_single,m_vis_,w_frac,qcd_frac,ttbar_frac};
          ff_nom = fns_["ff_lt_medium_dmbins"]->eval(args_dm.data());
          event->Add("wt_ff_dmbins_1",  ff_nom);

          auto args_dm_qcd = std::vector<double>{pt_2_,tau_decaymode_2_,n_jets_,pt_1_,os,met_var_qcd,iso_1_,pass_single};
          auto args_dm_w = std::vector<double>{pt_2_,tau_decaymode_2_,n_jets_,pt_1_,met_var_w,mt_1_,pass_single,m_vis_};

          ff_nom = fns_["ff_lt_medium_dmbins_qcd"]->eval(args_dm_qcd.data());
          event->Add("wt_ff_dmbins_qcd_1",  ff_nom);
          ff_nom = fns_["ff_lt_medium_dmbins_wjets"]->eval(args_dm_w.data());
          event->Add("wt_ff_dmbins_wjets_1",  ff_nom);

          // us groups FFs
          std::vector<Met*> pfMet_vec = event->GetPtrVec<Met>("pfMetFromSlimmed");
          Met const* pfmet = pfMet_vec.at(0);
          double pfmt_1 = MT(lep1, pfmet);
          auto args_us = std::vector<double>{pt_2_,n_jets_,os,mt_1_,m_vis_,pfmt_1};
          double ff_us_nom = fns_["ff_lt_medium_us"]->eval(args_us.data());
          event->Add("wt_ff_us_1",  ff_us_nom);

          if(do_systematics_) {
            for(auto s : systs_mvadm_){
              if (s == "") continue;
              double ff_syst = fns_["ff_lt_medium_mvadmbins"+s]->eval(args.data());
              std::string syst_name = "wt_ff"+s;
              event->Add(syst_name+"_1", ff_syst);
            }
            for(auto s : systs_dm_){
              if (s == "") continue;
              double ff_syst = fns_["ff_lt_medium_dmbins"+s]->eval(args_dm.data());
              std::string syst_name = "wt_ff_dmbins"+s;
              event->Add(syst_name+"_1", ff_syst);
            }

            // us groups FFs
            for(auto s : systs_us_){
              if (s == "") continue;
              double ff_us_syst = fns_["ff_lt_medium_us"+s]->eval(args_us.data());
              std::string syst_name = "wt_ff_us"+s;
              event->Add(syst_name+"_1",  ff_us_syst);
            } 

          }

          return 0;
        }

        double ff_nom = fake_factors_[map_key]->value(inputs);
        event->Add("wt_ff_1",  ff_nom);
        double ff_real_up = ff_nom*(1.-real_frac*1.1)/(1.-real_frac);
        double ff_real_down = ff_nom*(1.-real_frac*0.9)/(1.-real_frac);
        event->Add("wt_ff_realtau_up_1",  ff_real_up);
        event->Add("wt_ff_realtau_down_1",  ff_real_down);

        if(do_systematics_){
          std::vector<std::string> systematics = {"ff_qcd_syst_up","ff_qcd_syst_down","ff_qcd_dm0_njet0_stat_up","ff_qcd_dm0_njet0_stat_down","ff_qcd_dm0_njet1_stat_up","ff_qcd_dm0_njet1_stat_down","ff_qcd_dm1_njet0_stat_up","ff_qcd_dm1_njet0_stat_down","ff_qcd_dm1_njet1_stat_up","ff_qcd_dm1_njet1_stat_down","ff_w_syst_up","ff_w_syst_down","ff_w_dm0_njet0_stat_up","ff_w_dm0_njet0_stat_down","ff_w_dm0_njet1_stat_up","ff_w_dm0_njet1_stat_down","ff_w_dm1_njet0_stat_up","ff_w_dm1_njet0_stat_down","ff_w_dm1_njet1_stat_up","ff_w_dm1_njet1_stat_down","ff_tt_syst_up","ff_tt_syst_down","ff_tt_dm0_njet0_stat_up","ff_tt_dm0_njet0_stat_down","ff_tt_dm0_njet1_stat_up","ff_tt_dm0_njet1_stat_down","ff_tt_dm1_njet0_stat_up","ff_tt_dm1_njet0_stat_down" ,"ff_tt_dm1_njet1_stat_up","ff_tt_dm1_njet1_stat_down"};
          for(unsigned j=0; j<systematics.size(); ++j){
            std::string syst = systematics[j];
            double ff_syst = fake_factors_[map_key]->value(inputs,syst);
            if(std::isinf(ff_syst) || std::isnan(ff_syst)) ff_syst = ff_nom; 
            std::string syst_name = "wt_"+syst+"_1";
            event->Add(syst_name, ff_syst);

          } 
        }
      } else if(channel_ == channel::tt){

        if(strategy_ == strategy::cpdecays17 || strategy_ == strategy::cpdecays18 || strategy_ == strategy::legacy16) { 
          // FF from workspace for cp in decay analysis

          Tau const* tau1 = dynamic_cast<Tau const*>(lep1);
          Tau const* tau2 = dynamic_cast<Tau const*>(lep2);

          std::vector<ic::PFCandidate*> pfcands =  event->GetPtrVec<ic::PFCandidate>("pfCandidates");
          std::vector<ic::Vertex*> & vertex_vec = event->GetPtrVec<ic::Vertex>("vertices");
          std::vector<ic::Vertex*> & refit_vertex_vec = event->GetPtrVec<ic::Vertex>("refittedVerticesBS");
          ic::Vertex* refit_vertex = vertex_vec[0];
          for(auto v : refit_vertex_vec) {
            if(v->id() == tau1->id()+tau2->id()) refit_vertex = v;
          }

          double ipsig = IPAndSignificance(tau1, refit_vertex, pfcands).second;

          double mva_dm_1=tau1->HasTauID("MVADM2017v1") ? tau1->GetTauID("MVADM2017v1") : -1.;

          bool isOS = PairOppSign(ditau);
          double os = 1.;
          if(!isOS) os=0.;

          auto args = std::vector<double>{pt_1_,mva_dm_1,ipsig,n_jets_,pt_2_,os,met_var_qcd};
          double ff_nom = fns_["ff_tt_medium_mvadmbins"]->eval(args.data()); 
          event->Add("wt_ff_1",  ff_nom);
          double mva_dm_2_=tau2->HasTauID("MVADM2017v1") ? tau2->GetTauID("MVADM2017v1") : -1.;
          double ipsig2 = IPAndSignificance(tau2, refit_vertex, pfcands).second;
          auto args2 = std::vector<double>{pt_2_,mva_dm_2_,ipsig2,n_jets_,pt_1_,0.,met_var_qcd}; // we are using this FF only for W and ttbar contributions so we set this to false as we want to take the same-sign value in this case 
          double ff_nom_2 = fns_["ff_tt_medium_mvadmbins"]->eval(args2.data());
          event->Add("wt_ff_2",  ff_nom_2);
 

          auto args_dm = std::vector<double>{pt_1_,tau_decaymode_1_,n_jets_,pt_2_,os,met_var_qcd};
          ff_nom = fns_["ff_tt_medium_dmbins"]->eval(args_dm.data());
          event->Add("wt_ff_dmbins_1",  ff_nom);
          auto args_dm_2 = std::vector<double>{pt_2_,tau_decaymode_2_,n_jets_,pt_1_,0.,met_var_qcd}; // we are using this FF only for W and ttbar contributions so we set this to false as we want to take the same-sign value in this case 
          ff_nom_2 = fns_["ff_tt_medium_dmbins"]->eval(args_dm_2.data());
          event->Add("wt_ff_dmbins_2",  ff_nom_2);

         auto args_us = std::vector<double>{pt_1_,n_jets_,pt_2_,os,m_vis_};
         auto args_us_2 = std::vector<double>{pt_2_,n_jets_,pt_1_,os,m_vis_};

         ff_nom = fns_["ff_tt_medium_us"]->eval(args_us.data());
         event->Add("wt_ff_us_1",  ff_nom);
         ff_nom_2 = fns_["ff_tt_medium_us"]->eval(args_us_2.data());
         event->Add("wt_ff_us_2",  ff_nom_2);


          if(do_systematics_){

            for(auto s : systs_mvadm_){
              if (s == "") continue;
              double ff_syst = fns_["ff_tt_medium_mvadmbins"+s]->eval(args.data()); 
              std::string syst_name = "wt_ff"+s;
              event->Add(syst_name+"_1", ff_syst);

              double ff_syst_2 = fns_["ff_tt_medium_mvadmbins"+s]->eval(args2.data());
              event->Add(syst_name+"_2", ff_syst_2);
            }
            for(auto s : systs_dm_){
              if (s == "") continue;
              double ff_syst = fns_["ff_tt_medium_dmbins"+s]->eval(args_dm.data());
              std::string syst_name = "wt_ff_dmbins"+s;
              event->Add(syst_name+"_1", ff_syst);

              double ff_syst_2 = fns_["ff_tt_medium_dmbins"+s]->eval(args_dm_2.data());
              event->Add(syst_name+"_2", ff_syst_2);
            }

            for(auto s : systs_us_){
              if (s == "") continue;
              double ff_syst = fns_["ff_tt_medium_us"+s]->eval(args_us.data());
              std::string syst_name = "wt_ff_us"+s;
              event->Add(syst_name+"_1", ff_syst);

              double ff_syst_2 = fns_["ff_tt_medium_us"+s]->eval(args_us_2.data());
              event->Add(syst_name+"_2", ff_syst_2);
            }


          }
          return 0;
        }
        double ff_nom_1 = fake_factors_[map_key]->value(tt_inputs_1)*0.5;
        double ff_nom_2 = fake_factors_[map_key]->value(tt_inputs_2)*0.5;
        event->Add("wt_ff_1",  ff_nom_1);
        event->Add("wt_ff_2",  ff_nom_2);
        double ff_real_up_1 = ff_nom_1*(1.-real_frac*1.1)/(1.-real_frac);
        double ff_real_down_1 = ff_nom_1*(1.-real_frac*0.9)/(1.-real_frac);
        double ff_real_up_2 = ff_nom_2*(1.-real_frac_2*1.1)/(1.-real_frac_2);
        double ff_real_down_2 = ff_nom_2*(1.-real_frac_2*0.9)/(1.-real_frac_2);
        event->Add("wt_ff_realtau_up_1",  ff_real_up_1);
        event->Add("wt_ff_realtau_down_1",  ff_real_down_1);
        event->Add("wt_ff_realtau_up_2",  ff_real_up_2);
        event->Add("wt_ff_realtau_down_2",  ff_real_down_2);
        
        if(do_systematics_){
          std::vector<std::string> systematics = {"ff_qcd_syst_up","ff_qcd_syst_down","ff_qcd_dm0_njet0_stat_up","ff_qcd_dm0_njet0_stat_down","ff_qcd_dm0_njet1_stat_up","ff_qcd_dm0_njet1_stat_down","ff_qcd_dm1_njet0_stat_up","ff_qcd_dm1_njet0_stat_down","ff_qcd_dm1_njet1_stat_up","ff_qcd_dm1_njet1_stat_down","ff_w_syst_up","ff_w_syst_down","ff_tt_syst_up","ff_tt_syst_down","ff_w_frac_syst_up", "ff_w_frac_syst_down", "ff_tt_frac_syst_up", "ff_tt_frac_syst_down"};
         
          if(strategy_ == strategy::cpsummer17 || strategy_ == strategy::cpdecays17 || strategy_ == strategy::cpdecays18) {
            systematics = {"ff_qcd_syst_up","ff_qcd_syst_down","ff_qcd_dm0_njet0_stat_up","ff_qcd_dm0_njet0_stat_down","ff_qcd_dm0_njet1_stat_up","ff_qcd_dm0_njet1_stat_down","ff_qcd_dm1_njet0_stat_up","ff_qcd_dm1_njet0_stat_down","ff_qcd_dm1_njet1_stat_up","ff_qcd_dm1_njet1_stat_down","ff_w_syst_up","ff_w_syst_down","ff_tt_syst_up","ff_tt_syst_down","ff_w_frac_syst_up", "ff_w_frac_syst_down", "ff_tt_frac_syst_up", "ff_tt_frac_syst_down"};
          }
 
          for(unsigned j=0; j<systematics.size(); ++j){
            std::string syst = systematics[j];
            double ff_syst_1 = fake_factors_[map_key]->value(tt_inputs_1,syst)*0.5;
            double ff_syst_2 = fake_factors_[map_key]->value(tt_inputs_2,syst)*0.5;

            if(std::isinf(ff_syst_1) || std::isnan(ff_syst_1)) ff_syst_1 = ff_nom_1;
            if(std::isinf(ff_syst_2) || std::isnan(ff_syst_2)) ff_syst_2 = ff_nom_2;

            std::string syst_name = "wt_"+syst;
            event->Add(syst_name+"_1", ff_syst_1);
            event->Add(syst_name+"_2", ff_syst_2);

            if(syst_name.find("_frac_syst_") != std::string::npos) {
              double w_frac_1 = tt_inputs_1[6], tt_frac_1 = tt_inputs_1[7], qcd_frac_1 = tt_inputs_1[5];
              double w_frac_2 = tt_inputs_2[6], tt_frac_2 = tt_inputs_2[7], qcd_frac_2 = tt_inputs_2[5];
              double w_frac_1_up = w_frac_1, tt_frac_1_up = tt_frac_1, qcd_frac_1_up = qcd_frac_1, w_frac_2_up = w_frac_2, tt_frac_2_up = tt_frac_2, qcd_frac_2_up = qcd_frac_2;
 
              if(syst=="ff_w_frac_syst_up") {
                w_frac_1_up =  (w_frac_1)*1.2;
                qcd_frac_1_up+=w_frac_1-w_frac_1_up;

                w_frac_2_up =  (w_frac_2)*1.2;
                qcd_frac_2_up+=w_frac_2-w_frac_2_up;
              } else if(syst=="ff_w_frac_syst_down") {
                w_frac_1_up =  (w_frac_1)*0.8;
                qcd_frac_1_up+=w_frac_1-w_frac_1_up;

                w_frac_2_up =  (w_frac_2)*0.8;
                qcd_frac_2_up+=w_frac_2-w_frac_2_up;
              } else if(syst=="ff_tt_frac_syst_up") {
                tt_frac_1_up =  (tt_frac_1)*1.2;
                qcd_frac_1_up+=tt_frac_1-tt_frac_1_up;

                tt_frac_2_up =  (tt_frac_2)*1.2;
                qcd_frac_2_up+=tt_frac_2-tt_frac_2_up;

              } else if(syst=="ff_tt_frac_syst_down") {
                tt_frac_1_up =  (tt_frac_1)*0.8;
                qcd_frac_1_up+=tt_frac_1-tt_frac_1_up;

                tt_frac_2_up =  (tt_frac_2)*0.8;
                qcd_frac_2_up+=tt_frac_2-tt_frac_2_up;
              } 
              auto tt_inputs_1_shift = tt_inputs_1;
              auto tt_inputs_2_shift = tt_inputs_2;
              tt_inputs_1_shift[5]=qcd_frac_1_up; tt_inputs_1_shift[6] = w_frac_1_up; tt_inputs_1_shift[7] = tt_frac_1_up;
              tt_inputs_2_shift[5]=qcd_frac_2_up; tt_inputs_2_shift[6] = w_frac_2_up; tt_inputs_2_shift[7] = tt_frac_2_up;
              double ff_shift_1 = fake_factors_[map_key]->value(tt_inputs_1_shift)*0.5;
              double ff_shift_2 = fake_factors_[map_key]->value(tt_inputs_2_shift)*0.5;
              event->Add(syst_name+"_alt_1", ff_shift_1);
              event->Add(syst_name+"_alt_2", ff_shift_2);
            }
          } 
        }
      }
    } 
    
    

    return 0;
  }
  
  int HTTFakeFactorWeights::PostAnalysis() {
    return 0;
  }

  void HTTFakeFactorWeights::PrintInfo() {
    ;
  }
}
