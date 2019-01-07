#include "UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/interface/HTTGenAnalysis.h"
#include "UserCode/ICHiggsTauTau/Analysis/Utilities/interface/FnPredicates.h"

std::vector<ic::GenParticle> FamilyTree (std::vector<ic::GenParticle> &v, ic::GenParticle p, std::vector<ic::GenParticle*> gen_particles, unsigned &outputID){ 
  if(p.daughters().size() == 0){
    unsigned ID = std::fabs(p.pdgid());
    if(ID == 11) outputID = 11;
    else if(ID == 13) outputID = 13;
    if(!(ID==12 || ID==14 || ID==16)){
      v.push_back(p);
    }
  }
  else{
    for(size_t i = 0; i < p.daughters().size(); ++i ){
      ic::GenParticle d = *gen_particles[p.daughters().at(i)];
      FamilyTree(v,d, gen_particles, outputID);
    }
  }
  return v;
}

struct swap_labels{
  bool operator() (std::string a,std::string b) {
    if(a=="t" && b!="t") return false;
    else if(a=="m" &&  (b!="m" && b!="t")) return false;
    else return true;
  }
};

struct PtComparator{
  bool operator() (ic::Candidate a, ic::Candidate b) {
    return (a.vector().Pt() > b.vector().Pt());
  }
};

struct PtComparatorGenPart{
  bool operator() (ic::GenParticle *a, ic::GenParticle *b) {
    return (a->vector().Pt() > b->vector().Pt());
  }
};

  
namespace ic {

  HTTGenAnalysis::HTTGenAnalysis(std::string const& name) : ModuleBase(name) {
    fs_ = NULL;
    bbtag_eff_ = nullptr;
  }

  HTTGenAnalysis::~HTTGenAnalysis() {
    ;
  }

  int HTTGenAnalysis::PreAnalysis() {
    TFile f("input/mssm_higgspt/higgs_pt_v2_mssm_mode.root");
    mssm_w_ = std::shared_ptr<RooWorkspace>((RooWorkspace*)gDirectory->Get("w"));
    f.Close();
    std::string mass_str = mssm_mass_;
    if(mssm_w_->function(("h_"+mass_str+"_t_ratio").c_str())){
      fns_["h_t_ratio"] = std::shared_ptr<RooFunctor>(mssm_w_->function(("h_"+mass_str+"_t_ratio").c_str())->functor(mssm_w_->argSet("h_pt")));        
      fns_["h_b_ratio"] = std::shared_ptr<RooFunctor>(mssm_w_->function(("h_"+mass_str+"_b_ratio").c_str())->functor(mssm_w_->argSet("h_pt")));
      fns_["h_i_ratio"] = std::shared_ptr<RooFunctor>(mssm_w_->function(("h_"+mass_str+"_i_ratio").c_str())->functor(mssm_w_->argSet("h_pt")));
      fns_["H_t_ratio"] = std::shared_ptr<RooFunctor>(mssm_w_->function(("H_"+mass_str+"_t_ratio").c_str())->functor(mssm_w_->argSet("h_pt")));
      fns_["H_b_ratio"] = std::shared_ptr<RooFunctor>(mssm_w_->function(("H_"+mass_str+"_b_ratio").c_str())->functor(mssm_w_->argSet("h_pt")));
      fns_["H_i_ratio"] = std::shared_ptr<RooFunctor>(mssm_w_->function(("H_"+mass_str+"_i_ratio").c_str())->functor(mssm_w_->argSet("h_pt")));
      fns_["A_t_ratio"] = std::shared_ptr<RooFunctor>(mssm_w_->function(("A_"+mass_str+"_t_ratio").c_str())->functor(mssm_w_->argSet("h_pt")));
      fns_["A_b_ratio"] = std::shared_ptr<RooFunctor>(mssm_w_->function(("A_"+mass_str+"_b_ratio").c_str())->functor(mssm_w_->argSet("h_pt")));
      fns_["A_i_ratio"] = std::shared_ptr<RooFunctor>(mssm_w_->function(("A_"+mass_str+"_i_ratio").c_str())->functor(mssm_w_->argSet("h_pt"))); 
    }
      
    rand = new TRandom3(0);
    if(fs_){  
      outtree_ = fs_->make<TTree>("gen_ntuple","gen_ntuple");
      outtree_->Branch("event"       , &event_       );
      outtree_->Branch("wt"       , &wt_       );
      outtree_->Branch("wt_stitch"       , &wt_stitch_       );
      outtree_->Branch("wt_topmass"       , &wt_topmass_       );
      outtree_->Branch("wt_topmass_2"     , &wt_topmass_2_  );
      outtree_->Branch("wt_ps_down", &wt_ps_down_);
      outtree_->Branch("wt_ps_up", &wt_ps_up_);
      outtree_->Branch("wt_ue_down", &wt_ue_down_);
      outtree_->Branch("wt_ue_up", &wt_ue_up_);
      outtree_->Branch("npNLO", &npNLO_);
      outtree_->Branch("cand_1"       , &cand_1_       );
      outtree_->Branch("cand_2"       , &cand_2_       );
      outtree_->Branch("match_1"       , &match_1_       );
      outtree_->Branch("match_2"       , &match_2_       );
      if(do_theory_uncert_){
        outtree_->Branch("wt_mur1_muf1",    &scale1_);
        outtree_->Branch("wt_mur1_muf2",    &scale2_);
        outtree_->Branch("wt_mur1_muf0p5",  &scale3_);
        outtree_->Branch("wt_mur2_muf1",    &scale4_);
        outtree_->Branch("wt_mur2_muf2",    &scale5_);
        outtree_->Branch("wt_mur2_muf0p5",  &scale6_);
        outtree_->Branch("wt_mur0p5_muf1",  &scale7_);
        outtree_->Branch("wt_mur0p5_muf2",  &scale8_);
        outtree_->Branch("wt_mur0p5_muf0p5",&scale9_);
       // outtree_->Branch("wt_pdf_1",&wt_pdf_1_);
       // outtree_->Branch("wt_pdf_2",&wt_pdf_2_);
       // outtree_->Branch("wt_pdf_3",&wt_pdf_3_);
       // outtree_->Branch("wt_pdf_4",&wt_pdf_4_);
       // outtree_->Branch("wt_pdf_5",&wt_pdf_5_);
       // outtree_->Branch("wt_pdf_6",&wt_pdf_6_);
       // outtree_->Branch("wt_pdf_7",&wt_pdf_7_);
       // outtree_->Branch("wt_pdf_8",&wt_pdf_8_);
       // outtree_->Branch("wt_pdf_9",&wt_pdf_9_);
       // outtree_->Branch("wt_pdf_10",&wt_pdf_10_);
       // outtree_->Branch("wt_pdf_11",&wt_pdf_11_);
       // outtree_->Branch("wt_pdf_12",&wt_pdf_12_);
       // outtree_->Branch("wt_pdf_13",&wt_pdf_13_);
       // outtree_->Branch("wt_pdf_14",&wt_pdf_14_);
       // outtree_->Branch("wt_pdf_15",&wt_pdf_15_);
       // outtree_->Branch("wt_pdf_16",&wt_pdf_16_);
       // outtree_->Branch("wt_pdf_17",&wt_pdf_17_);
       // outtree_->Branch("wt_pdf_18",&wt_pdf_18_);
       // outtree_->Branch("wt_pdf_19",&wt_pdf_19_);
       // outtree_->Branch("wt_pdf_20",&wt_pdf_20_);
       // outtree_->Branch("wt_pdf_21",&wt_pdf_21_);
       // outtree_->Branch("wt_pdf_22",&wt_pdf_22_);
       // outtree_->Branch("wt_pdf_23",&wt_pdf_23_);
       // outtree_->Branch("wt_pdf_24",&wt_pdf_24_);
       // outtree_->Branch("wt_pdf_25",&wt_pdf_25_);
       // outtree_->Branch("wt_pdf_26",&wt_pdf_26_);
       // outtree_->Branch("wt_pdf_27",&wt_pdf_27_);
       // outtree_->Branch("wt_pdf_28",&wt_pdf_28_);
       // outtree_->Branch("wt_pdf_29",&wt_pdf_29_);
       // outtree_->Branch("wt_pdf_30",&wt_pdf_30_);
       // outtree_->Branch("wt_pdf_31",&wt_pdf_31_);
       // outtree_->Branch("wt_pdf_32",&wt_pdf_32_);
       // outtree_->Branch("wt_pdf_33",&wt_pdf_33_);
       // outtree_->Branch("wt_pdf_34",&wt_pdf_34_);
       // outtree_->Branch("wt_pdf_35",&wt_pdf_35_);
       // outtree_->Branch("wt_pdf_36",&wt_pdf_36_);
       // outtree_->Branch("wt_pdf_37",&wt_pdf_37_);
       // outtree_->Branch("wt_pdf_38",&wt_pdf_38_);
       // outtree_->Branch("wt_pdf_39",&wt_pdf_39_);
       // outtree_->Branch("wt_pdf_40",&wt_pdf_40_);
       // outtree_->Branch("wt_pdf_41",&wt_pdf_41_);
       // outtree_->Branch("wt_pdf_42",&wt_pdf_42_);
       // outtree_->Branch("wt_pdf_43",&wt_pdf_43_);
       // outtree_->Branch("wt_pdf_44",&wt_pdf_44_);
       // outtree_->Branch("wt_pdf_45",&wt_pdf_45_);
       // outtree_->Branch("wt_pdf_46",&wt_pdf_46_);
       // outtree_->Branch("wt_pdf_47",&wt_pdf_47_);
       // outtree_->Branch("wt_pdf_48",&wt_pdf_48_);
       // outtree_->Branch("wt_pdf_49",&wt_pdf_49_);
       // outtree_->Branch("wt_pdf_50",&wt_pdf_50_);
       // outtree_->Branch("wt_pdf_51",&wt_pdf_51_);
       // outtree_->Branch("wt_pdf_52",&wt_pdf_52_);
       // outtree_->Branch("wt_pdf_53",&wt_pdf_53_);
       // outtree_->Branch("wt_pdf_54",&wt_pdf_54_);
       // outtree_->Branch("wt_pdf_55",&wt_pdf_55_);
       // outtree_->Branch("wt_pdf_56",&wt_pdf_56_);
       // outtree_->Branch("wt_pdf_57",&wt_pdf_57_);
       // outtree_->Branch("wt_pdf_58",&wt_pdf_58_);
       // outtree_->Branch("wt_pdf_59",&wt_pdf_59_);
       // outtree_->Branch("wt_pdf_60",&wt_pdf_60_);
       // outtree_->Branch("wt_pdf_61",&wt_pdf_61_);
       // outtree_->Branch("wt_pdf_62",&wt_pdf_62_);
       // outtree_->Branch("wt_pdf_63",&wt_pdf_63_);
       // outtree_->Branch("wt_pdf_64",&wt_pdf_64_);
       // outtree_->Branch("wt_pdf_65",&wt_pdf_65_);
       // outtree_->Branch("wt_pdf_66",&wt_pdf_66_);
       // outtree_->Branch("wt_pdf_67",&wt_pdf_67_);
       // outtree_->Branch("wt_pdf_68",&wt_pdf_68_);
       // outtree_->Branch("wt_pdf_69",&wt_pdf_69_);
       // outtree_->Branch("wt_pdf_70",&wt_pdf_70_);
       // outtree_->Branch("wt_pdf_71",&wt_pdf_71_);
       // outtree_->Branch("wt_pdf_72",&wt_pdf_72_);
       // outtree_->Branch("wt_pdf_73",&wt_pdf_73_);
       // outtree_->Branch("wt_pdf_74",&wt_pdf_74_);
       // outtree_->Branch("wt_pdf_75",&wt_pdf_75_);
       // outtree_->Branch("wt_pdf_76",&wt_pdf_76_);
       // outtree_->Branch("wt_pdf_77",&wt_pdf_77_);
       // outtree_->Branch("wt_pdf_78",&wt_pdf_78_);
       // outtree_->Branch("wt_pdf_79",&wt_pdf_79_);
       // outtree_->Branch("wt_pdf_80",&wt_pdf_80_);
       // outtree_->Branch("wt_pdf_81",&wt_pdf_81_);
       // outtree_->Branch("wt_pdf_82",&wt_pdf_82_);
       // outtree_->Branch("wt_pdf_83",&wt_pdf_83_);
       // outtree_->Branch("wt_pdf_84",&wt_pdf_84_);
       // outtree_->Branch("wt_pdf_85",&wt_pdf_85_);
       // outtree_->Branch("wt_pdf_86",&wt_pdf_86_);
       // outtree_->Branch("wt_pdf_87",&wt_pdf_87_);
       // outtree_->Branch("wt_pdf_88",&wt_pdf_88_);
       // outtree_->Branch("wt_pdf_89",&wt_pdf_89_);
       // outtree_->Branch("wt_pdf_90",&wt_pdf_90_);
       // outtree_->Branch("wt_pdf_91",&wt_pdf_91_);
       // outtree_->Branch("wt_pdf_92",&wt_pdf_92_);
       // outtree_->Branch("wt_pdf_93",&wt_pdf_93_);
       // outtree_->Branch("wt_pdf_94",&wt_pdf_94_);
       // outtree_->Branch("wt_pdf_95",&wt_pdf_95_);
       // outtree_->Branch("wt_pdf_96",&wt_pdf_96_);
       // outtree_->Branch("wt_pdf_97",&wt_pdf_97_);
       // outtree_->Branch("wt_pdf_98",&wt_pdf_98_);
       // outtree_->Branch("wt_pdf_99",&wt_pdf_99_);
       // outtree_->Branch("wt_pdf_100",&wt_pdf_100_);
       // 
       // outtree_->Branch("wt_alphasdown",&wt_alphasdown_);
       // outtree_->Branch("wt_alphasup",&wt_alphasup_);
      }
      outtree_->Branch("passed"       ,&passed_       );
      outtree_->Branch("pt_1"        , &pt_1_        );
      outtree_->Branch("pt_2"        , &pt_2_        );
      outtree_->Branch("eta_1"       , &eta_1_       );
      outtree_->Branch("eta_2"       , &eta_2_       );
      outtree_->Branch("phi_1"       , &phi_1_       );
      outtree_->Branch("phi_2"       , &phi_2_       );
      outtree_->Branch("met"         , &met_         );
      outtree_->Branch("m_vis"       , &m_vis_       );
      outtree_->Branch("pt_tt"       , &pt_tt_       );
      outtree_->Branch("mass"       , &mass_       );
      outtree_->Branch("wtzpt"       , &wtzpt_       );
      outtree_->Branch("mt_1"        , &mt_1_        );
      outtree_->Branch("mt_2"        , &mt_2_        );
      outtree_->Branch("pzeta"       , &pzeta_       );
      outtree_->Branch("n_bjets"     , &n_bjets_     );
      outtree_->Branch("n_bjets_noscale"     , &n_bjets_noscale_);
      outtree_->Branch("n_jets"      , &n_jets_      );
      outtree_->Branch("n_jets_nofilter"      , &n_jets_nofilter_);
      outtree_->Branch("n_jetsingap" , &n_jetsingap_ );
      outtree_->Branch("jpt_1"       , &jpt_1_       );
      outtree_->Branch("jpt_2"       , &jpt_2_       );
      outtree_->Branch("jpt_3"       , &jpt_3_       );
      outtree_->Branch("jeta_1"      , &jeta_1_      );
      outtree_->Branch("jeta_2"      , &jeta_2_      );
      outtree_->Branch("jphi_1"      , &jphi_1_      );
      outtree_->Branch("jphi_2"      , &jphi_2_      );
      outtree_->Branch("mjj"         , &mjj_         );
      outtree_->Branch("jdeta"       , &jdeta_       );
      outtree_->Branch("higgsDecay"  , &decayType    );
      outtree_->Branch("genpt_1"     , &genpt_1_        );
      outtree_->Branch("genpt_2"     , &genpt_2_        );
      outtree_->Branch("geneta_2"    , &geneta_2_       );
      outtree_->Branch("geneta_1"    , &geneta_1_       );
      outtree_->Branch("HiggsPt"     , &HiggsPt_     );
      outtree_->Branch("partons"     , &partons_);
      outtree_->Branch("partons_lhe"     , &partons_lhe_);
      outtree_->Branch("parton_pt"     , &parton_pt_);
      outtree_->Branch("parton_pt_2"     , &parton_pt_2_);
      outtree_->Branch("parton_pt_3"     , &parton_pt_3_);
      outtree_->Branch("parton_mjj",    &parton_mjj_);
      outtree_->Branch("parton_HpT", &parton_HpT_);
      outtree_->Branch("D0"     , &D0_);
      outtree_->Branch("D0star"     , &D0star_);
      outtree_->Branch("DCP"     , &DCP_);
      outtree_->Branch("sjdphi"     , &sjdphi_);
      outtree_->Branch("spjdphi"     , &spjdphi_);
      outtree_->Branch("ysep"     , &ysep_);
      outtree_->Branch("n_pjets"     , &n_pjets_);
      outtree_->Branch("n_pu",      &n_pu_);

      outtree_->Branch("aco_angle_1", &aco_angle_1_);
      outtree_->Branch("aco_angle_2", &aco_angle_2_);
      outtree_->Branch("aco_angle_3", &aco_angle_3_);
      outtree_->Branch("aco_angle_4", &aco_angle_4_);
      outtree_->Branch("cp_sign_1",     &cp_sign_1_);
      outtree_->Branch("cp_sign_2",     &cp_sign_2_);
      outtree_->Branch("cp_sign_3",     &cp_sign_3_);
      outtree_->Branch("cp_sign_4",     &cp_sign_4_);
      outtree_->Branch("cp_channel",    &cp_channel_);
      
      outtree_->Branch("wt_ggh_t", &wt_ggh_t_);
      outtree_->Branch("wt_ggh_b", &wt_ggh_b_);
      outtree_->Branch("wt_ggh_i", &wt_ggh_i_);
      outtree_->Branch("wt_ggH_t", &wt_ggH_t_);
      outtree_->Branch("wt_ggH_b", &wt_ggH_b_);
      outtree_->Branch("wt_ggH_i", &wt_ggH_i_);
      outtree_->Branch("wt_ggA_t", &wt_ggA_t_);
      outtree_->Branch("wt_ggA_b", &wt_ggA_b_);
      outtree_->Branch("wt_ggA_i", &wt_ggA_i_);
      outtree_->Branch("wt_ggA_i", &wt_ggA_i_);
      outtree_->Branch("pT_A", &pT_A_);
      
    }
    count_ee_ = 0;
    count_em_ = 0;
    count_et_ = 0;
    count_mm_ = 0;
    count_mt_ = 0;
    count_tt_ = 0;

    GetFromTFile<TH2D>("input/zpt_weights/dy_weights_2017.root","/","zptmass_histo").Copy(z_pt_weights_sm_);
    topmass_wts_ = GetFromTFile<TH1F>("input/ggh_weights/top_mass_weights.root","/","pt_weight");

    /* topmass_wts_toponly_ = GetFromTFile<TH1F>("input/ggh_weights/quarkmass_uncerts_hnnlo.root","/","nom"); */
   
    /* ps_0jet_up_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ps_0jet_up"); */
    /* ps_0jet_down_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ps_0jet_down"); */
    /* ps_1jet_up_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ps_1jet_up"); */
    /* ps_1jet_down_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ps_1jet_down"); */
    /* ps_2jet_up_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ps_2jet_up"); */
    /* ps_2jet_down_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ps_2jet_down"); */
    /* ps_3jet_up_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ps_3jet_up"); */
    /* ps_3jet_down_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ps_3jet_down"); */   
    /* ue_up_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ue_up"); */
    /* ue_down_ = GetFromTFile<TH1D>("input/ggh_weights/MG_ps_uncerts.root","/","ue_down"); */ 
    return 0;
  }

  int HTTGenAnalysis::Execute(TreeEvent *event) {
    
    EventInfo const* eventInfo = event->GetPtr<EventInfo>("eventInfo");
    event_ = (unsigned long long) eventInfo->event();
    wt_ = 1;
    
    wt_ = eventInfo->total_weight();

    if(do_theory_uncert_){
      // note some of these labels may be generator dependent so need to make sure you check before using them
      if(eventInfo->weight_defined("1001")) scale1_ = eventInfo->weight("1001"); else scale1_=1.0;
      if(eventInfo->weight_defined("1002")) scale2_ = eventInfo->weight("1002"); else scale2_=1.0;
      if(eventInfo->weight_defined("1003")) scale3_ = eventInfo->weight("1003"); else scale3_=1.0;
      if(eventInfo->weight_defined("1004")) scale4_ = eventInfo->weight("1004"); else scale4_=1.0;
      if(eventInfo->weight_defined("1005")) scale5_ = eventInfo->weight("1005"); else scale5_=1.0;
      if(eventInfo->weight_defined("1006")) scale6_ = eventInfo->weight("1006"); else scale6_=1.0;
      if(eventInfo->weight_defined("1007")) scale7_ = eventInfo->weight("1007"); else scale7_=1.0;
      if(eventInfo->weight_defined("1008")) scale8_ = eventInfo->weight("1008"); else scale8_=1.0;
      if(eventInfo->weight_defined("1009")) scale9_ = eventInfo->weight("1009"); else scale9_=1.0; 

      // For MG5 samples:
      //  <weight MUF="1.0" MUR="2.0" PDF="292200" id="1002"> MUR=2.0  </weight>
      //  <weight MUF="1.0" MUR="0.5" PDF="292200" id="1003"> MUR=0.5  </weight>
      //  <weight MUF="2.0" MUR="1.0" PDF="292200" id="1004"> MUF=2.0  </weight>
      //  <weight MUF="2.0" MUR="2.0" PDF="292200" id="1005"> MUR=2.0 MUF=2.0  </weight>
      //  <weight MUF="2.0" MUR="0.5" PDF="292200" id="1006"> MUR=0.5 MUF=2.0  </weight>
      //  <weight MUF="0.5" MUR="1.0" PDF="292200" id="1007"> MUF=0.5  </weight>
      //  <weight MUF="0.5" MUR="2.0" PDF="292200" id="1008"> MUR=2.0 MUF=0.5  </weight>
      //  <weight MUF="0.5" MUR="0.5" PDF="292200" id="1009"> MUR=0.5 MUF=0.5  </weight>
      //

      // for NNLOPS:
      //  <weight id="1001"> muR=1 muF=1 </weight>
      //  <weight id="1002"> muR=1 muF=2 </weight>
      //  <weight id="1003"> muR=1 muF=0.5 </weight>
      //  <weight id="1004"> muR=2 muF=1 </weight>
      //  <weight id="1005"> muR=2 muF=2 </weight>
      //  <weight id="1006"> muR=2 muF=0.5 </weight>
      //  <weight id="1007"> muR=0.5 muF=1 </weight>
      //  <weight id="1008"> muR=0.5 muF=2 </weight>
      //  <weight id="1009"> muR=0.5 muF=0.5 </weight>

      //std::cout << eventInfo->weight_defined("1001")    << std::endl;
 
      //<weight id="1001"> dyn=  -1 muR=0.10000E+01 muF=0.10000E+01 </weight>
      //<weight id="1002"> dyn=  -1 muR=0.20000E+01 muF=0.10000E+01 </weight>
      //<weight id="1003"> dyn=  -1 muR=0.50000E+00 muF=0.10000E+01 </weight>
      //<weight id="1004"> dyn=  -1 muR=0.10000E+01 muF=0.20000E+01 </weight>
      //<weight id="1005"> dyn=  -1 muR=0.20000E+01 muF=0.20000E+01 </weight>
      //<weight id="1006"> dyn=  -1 muR=0.50000E+00 muF=0.20000E+01 </weight>
      //<weight id="1007"> dyn=  -1 muR=0.10000E+01 muF=0.50000E+00 </weight>
      //<weight id="1008"> dyn=  -1 muR=0.20000E+01 muF=0.50000E+00 </weight>
      //<weight id="1009"> dyn=  -1 muR=0.50000E+00 muF=0.50000E+00 </weight>

 
      //if(eventInfo->weight_defined("1")) scale1_ = eventInfo->weight("1"); else scale1_=1.0;
      //if(eventInfo->weight_defined("2")) scale2_ = eventInfo->weight("2"); else scale2_=1.0;
      //if(eventInfo->weight_defined("3")) scale3_ = eventInfo->weight("3"); else scale3_=1.0;
      //if(eventInfo->weight_defined("4")) scale4_ = eventInfo->weight("4"); else scale4_=1.0;
      //if(eventInfo->weight_defined("5")) scale5_ = eventInfo->weight("5"); else scale5_=1.0;
      //if(eventInfo->weight_defined("6")) scale6_ = eventInfo->weight("6"); else scale6_=1.0;
      //if(eventInfo->weight_defined("7")) scale7_ = eventInfo->weight("7"); else scale7_=1.0;
      //if(eventInfo->weight_defined("8")) scale8_ = eventInfo->weight("8"); else scale8_=1.0;
      //if(eventInfo->weight_defined("9")) scale9_ = eventInfo->weight("9"); else scale9_=1.0;
      //pdf variation weights
      //if(eventInfo->weight_defined("2001")) wt_pdf_1_ = eventInfo->weight("2001"); else wt_pdf_1_=1.0;
      //if(eventInfo->weight_defined("2002")) wt_pdf_2_ = eventInfo->weight("2002"); else wt_pdf_2_=1.0;
      //if(eventInfo->weight_defined("2003")) wt_pdf_3_ = eventInfo->weight("2003"); else wt_pdf_3_=1.0;
      //if(eventInfo->weight_defined("2004")) wt_pdf_4_ = eventInfo->weight("2004"); else wt_pdf_4_=1.0;
      //if(eventInfo->weight_defined("2005")) wt_pdf_5_ = eventInfo->weight("2005"); else wt_pdf_5_=1.0;
      //if(eventInfo->weight_defined("2006")) wt_pdf_6_ = eventInfo->weight("2006"); else wt_pdf_6_=1.0;
      //if(eventInfo->weight_defined("2007")) wt_pdf_7_ = eventInfo->weight("2007"); else wt_pdf_7_=1.0;
      //if(eventInfo->weight_defined("2008")) wt_pdf_8_ = eventInfo->weight("2008"); else wt_pdf_8_=1.0;
      //if(eventInfo->weight_defined("2009")) wt_pdf_9_ = eventInfo->weight("2009"); else wt_pdf_9_=1.0;
      //if(eventInfo->weight_defined("2010")) wt_pdf_10_ = eventInfo->weight("2010"); else wt_pdf_10_=1.0;
      //if(eventInfo->weight_defined("2011")) wt_pdf_11_ = eventInfo->weight("2011"); else wt_pdf_11_=1.0;
      //if(eventInfo->weight_defined("2012")) wt_pdf_12_ = eventInfo->weight("2012"); else wt_pdf_12_=1.0;
      //if(eventInfo->weight_defined("2013")) wt_pdf_13_ = eventInfo->weight("2013"); else wt_pdf_13_=1.0;
      //if(eventInfo->weight_defined("2014")) wt_pdf_14_ = eventInfo->weight("2014"); else wt_pdf_14_=1.0;
      //if(eventInfo->weight_defined("2015")) wt_pdf_15_ = eventInfo->weight("2015"); else wt_pdf_15_=1.0;
      //if(eventInfo->weight_defined("2016")) wt_pdf_16_ = eventInfo->weight("2016"); else wt_pdf_16_=1.0;
      //if(eventInfo->weight_defined("2017")) wt_pdf_17_ = eventInfo->weight("2017"); else wt_pdf_17_=1.0;
      //if(eventInfo->weight_defined("2018")) wt_pdf_18_ = eventInfo->weight("2018"); else wt_pdf_18_=1.0;
      //if(eventInfo->weight_defined("2019")) wt_pdf_19_ = eventInfo->weight("2019"); else wt_pdf_19_=1.0;
      //if(eventInfo->weight_defined("2020")) wt_pdf_20_ = eventInfo->weight("2020"); else wt_pdf_20_=1.0;
      //if(eventInfo->weight_defined("2021")) wt_pdf_21_ = eventInfo->weight("2021"); else wt_pdf_21_=1.0;
      //if(eventInfo->weight_defined("2022")) wt_pdf_22_ = eventInfo->weight("2022"); else wt_pdf_22_=1.0;
      //if(eventInfo->weight_defined("2023")) wt_pdf_23_ = eventInfo->weight("2023"); else wt_pdf_23_=1.0;
      //if(eventInfo->weight_defined("2024")) wt_pdf_24_ = eventInfo->weight("2024"); else wt_pdf_24_=1.0;
      //if(eventInfo->weight_defined("2025")) wt_pdf_25_ = eventInfo->weight("2025"); else wt_pdf_25_=1.0;
      //if(eventInfo->weight_defined("2026")) wt_pdf_26_ = eventInfo->weight("2026"); else wt_pdf_26_=1.0;
      //if(eventInfo->weight_defined("2027")) wt_pdf_27_ = eventInfo->weight("2027"); else wt_pdf_27_=1.0;
      //if(eventInfo->weight_defined("2028")) wt_pdf_28_ = eventInfo->weight("2028"); else wt_pdf_28_=1.0;
      //if(eventInfo->weight_defined("2029")) wt_pdf_29_ = eventInfo->weight("2029"); else wt_pdf_29_=1.0;
      //if(eventInfo->weight_defined("2030")) wt_pdf_30_ = eventInfo->weight("2030"); else wt_pdf_30_=1.0;
      //if(eventInfo->weight_defined("2031")) wt_pdf_31_ = eventInfo->weight("2031"); else wt_pdf_31_=1.0;
      //if(eventInfo->weight_defined("2032")) wt_pdf_32_ = eventInfo->weight("2032"); else wt_pdf_32_=1.0;
      //if(eventInfo->weight_defined("2033")) wt_pdf_33_ = eventInfo->weight("2033"); else wt_pdf_33_=1.0;
      //if(eventInfo->weight_defined("2034")) wt_pdf_34_ = eventInfo->weight("2034"); else wt_pdf_34_=1.0;
      //if(eventInfo->weight_defined("2035")) wt_pdf_35_ = eventInfo->weight("2035"); else wt_pdf_35_=1.0;
      //if(eventInfo->weight_defined("2036")) wt_pdf_36_ = eventInfo->weight("2036"); else wt_pdf_36_=1.0;
      //if(eventInfo->weight_defined("2037")) wt_pdf_37_ = eventInfo->weight("2037"); else wt_pdf_37_=1.0;
      //if(eventInfo->weight_defined("2038")) wt_pdf_38_ = eventInfo->weight("2038"); else wt_pdf_38_=1.0;
      //if(eventInfo->weight_defined("2039")) wt_pdf_39_ = eventInfo->weight("2039"); else wt_pdf_39_=1.0;
      //if(eventInfo->weight_defined("2040")) wt_pdf_40_ = eventInfo->weight("2040"); else wt_pdf_40_=1.0;
      //if(eventInfo->weight_defined("2041")) wt_pdf_41_ = eventInfo->weight("2041"); else wt_pdf_41_=1.0;
      //if(eventInfo->weight_defined("2042")) wt_pdf_42_ = eventInfo->weight("2042"); else wt_pdf_42_=1.0;
      //if(eventInfo->weight_defined("2043")) wt_pdf_43_ = eventInfo->weight("2043"); else wt_pdf_43_=1.0;
      //if(eventInfo->weight_defined("2044")) wt_pdf_44_ = eventInfo->weight("2044"); else wt_pdf_44_=1.0;
      //if(eventInfo->weight_defined("2045")) wt_pdf_45_ = eventInfo->weight("2045"); else wt_pdf_45_=1.0;
      //if(eventInfo->weight_defined("2046")) wt_pdf_46_ = eventInfo->weight("2046"); else wt_pdf_46_=1.0;
      //if(eventInfo->weight_defined("2047")) wt_pdf_47_ = eventInfo->weight("2047"); else wt_pdf_47_=1.0;
      //if(eventInfo->weight_defined("2048")) wt_pdf_48_ = eventInfo->weight("2048"); else wt_pdf_48_=1.0;
      //if(eventInfo->weight_defined("2049")) wt_pdf_49_ = eventInfo->weight("2049"); else wt_pdf_49_=1.0;
      //if(eventInfo->weight_defined("2050")) wt_pdf_50_ = eventInfo->weight("2050"); else wt_pdf_50_=1.0;
      //if(eventInfo->weight_defined("2051")) wt_pdf_51_ = eventInfo->weight("2051"); else wt_pdf_51_=1.0;
      //if(eventInfo->weight_defined("2052")) wt_pdf_52_ = eventInfo->weight("2052"); else wt_pdf_52_=1.0;
      //if(eventInfo->weight_defined("2053")) wt_pdf_53_ = eventInfo->weight("2053"); else wt_pdf_53_=1.0;
      //if(eventInfo->weight_defined("2054")) wt_pdf_54_ = eventInfo->weight("2054"); else wt_pdf_54_=1.0;
      //if(eventInfo->weight_defined("2055")) wt_pdf_55_ = eventInfo->weight("2055"); else wt_pdf_55_=1.0;
      //if(eventInfo->weight_defined("2056")) wt_pdf_56_ = eventInfo->weight("2056"); else wt_pdf_56_=1.0;
      //if(eventInfo->weight_defined("2057")) wt_pdf_57_ = eventInfo->weight("2057"); else wt_pdf_57_=1.0;
      //if(eventInfo->weight_defined("2058")) wt_pdf_58_ = eventInfo->weight("2058"); else wt_pdf_58_=1.0;
      //if(eventInfo->weight_defined("2059")) wt_pdf_59_ = eventInfo->weight("2059"); else wt_pdf_59_=1.0;
      //if(eventInfo->weight_defined("2060")) wt_pdf_60_ = eventInfo->weight("2060"); else wt_pdf_60_=1.0;
      //if(eventInfo->weight_defined("2061")) wt_pdf_61_ = eventInfo->weight("2061"); else wt_pdf_61_=1.0;
      //if(eventInfo->weight_defined("2062")) wt_pdf_62_ = eventInfo->weight("2062"); else wt_pdf_62_=1.0;
      //if(eventInfo->weight_defined("2063")) wt_pdf_63_ = eventInfo->weight("2063"); else wt_pdf_63_=1.0;
      //if(eventInfo->weight_defined("2064")) wt_pdf_64_ = eventInfo->weight("2064"); else wt_pdf_64_=1.0;
      //if(eventInfo->weight_defined("2065")) wt_pdf_65_ = eventInfo->weight("2065"); else wt_pdf_65_=1.0;
      //if(eventInfo->weight_defined("2066")) wt_pdf_66_ = eventInfo->weight("2066"); else wt_pdf_66_=1.0;
      //if(eventInfo->weight_defined("2067")) wt_pdf_67_ = eventInfo->weight("2067"); else wt_pdf_67_=1.0;
      //if(eventInfo->weight_defined("2068")) wt_pdf_68_ = eventInfo->weight("2068"); else wt_pdf_68_=1.0;
      //if(eventInfo->weight_defined("2069")) wt_pdf_69_ = eventInfo->weight("2069"); else wt_pdf_69_=1.0;
      //if(eventInfo->weight_defined("2070")) wt_pdf_70_ = eventInfo->weight("2070"); else wt_pdf_70_=1.0;
      //if(eventInfo->weight_defined("2071")) wt_pdf_71_ = eventInfo->weight("2071"); else wt_pdf_71_=1.0;
      //if(eventInfo->weight_defined("2072")) wt_pdf_72_ = eventInfo->weight("2072"); else wt_pdf_72_=1.0;
      //if(eventInfo->weight_defined("2073")) wt_pdf_73_ = eventInfo->weight("2073"); else wt_pdf_73_=1.0;
      //if(eventInfo->weight_defined("2074")) wt_pdf_74_ = eventInfo->weight("2074"); else wt_pdf_74_=1.0;
      //if(eventInfo->weight_defined("2075")) wt_pdf_75_ = eventInfo->weight("2075"); else wt_pdf_75_=1.0;
      //if(eventInfo->weight_defined("2076")) wt_pdf_76_ = eventInfo->weight("2076"); else wt_pdf_76_=1.0;
      //if(eventInfo->weight_defined("2077")) wt_pdf_77_ = eventInfo->weight("2077"); else wt_pdf_77_=1.0;
      //if(eventInfo->weight_defined("2078")) wt_pdf_78_ = eventInfo->weight("2078"); else wt_pdf_78_=1.0;
      //if(eventInfo->weight_defined("2079")) wt_pdf_79_ = eventInfo->weight("2079"); else wt_pdf_79_=1.0;
      //if(eventInfo->weight_defined("2080")) wt_pdf_80_ = eventInfo->weight("2080"); else wt_pdf_80_=1.0;
      //if(eventInfo->weight_defined("2081")) wt_pdf_81_ = eventInfo->weight("2081"); else wt_pdf_81_=1.0;
      //if(eventInfo->weight_defined("2082")) wt_pdf_82_ = eventInfo->weight("2082"); else wt_pdf_82_=1.0;
      //if(eventInfo->weight_defined("2083")) wt_pdf_83_ = eventInfo->weight("2083"); else wt_pdf_83_=1.0;
      //if(eventInfo->weight_defined("2084")) wt_pdf_84_ = eventInfo->weight("2084"); else wt_pdf_84_=1.0;
      //if(eventInfo->weight_defined("2085")) wt_pdf_85_ = eventInfo->weight("2085"); else wt_pdf_85_=1.0;
      //if(eventInfo->weight_defined("2086")) wt_pdf_86_ = eventInfo->weight("2086"); else wt_pdf_86_=1.0;
      //if(eventInfo->weight_defined("2087")) wt_pdf_87_ = eventInfo->weight("2087"); else wt_pdf_87_=1.0;
      //if(eventInfo->weight_defined("2088")) wt_pdf_88_ = eventInfo->weight("2088"); else wt_pdf_88_=1.0;
      //if(eventInfo->weight_defined("2089")) wt_pdf_89_ = eventInfo->weight("2089"); else wt_pdf_89_=1.0;
      //if(eventInfo->weight_defined("2090")) wt_pdf_90_ = eventInfo->weight("2090"); else wt_pdf_90_=1.0;
      //if(eventInfo->weight_defined("2091")) wt_pdf_91_ = eventInfo->weight("2091"); else wt_pdf_91_=1.0;
      //if(eventInfo->weight_defined("2092")) wt_pdf_92_ = eventInfo->weight("2092"); else wt_pdf_92_=1.0;
      //if(eventInfo->weight_defined("2093")) wt_pdf_93_ = eventInfo->weight("2093"); else wt_pdf_93_=1.0;
      //if(eventInfo->weight_defined("2094")) wt_pdf_94_ = eventInfo->weight("2094"); else wt_pdf_94_=1.0;
      //if(eventInfo->weight_defined("2095")) wt_pdf_95_ = eventInfo->weight("2095"); else wt_pdf_95_=1.0;
      //if(eventInfo->weight_defined("2096")) wt_pdf_96_ = eventInfo->weight("2096"); else wt_pdf_96_=1.0;
      //if(eventInfo->weight_defined("2097")) wt_pdf_97_ = eventInfo->weight("2097"); else wt_pdf_97_=1.0;
      //if(eventInfo->weight_defined("2098")) wt_pdf_98_ = eventInfo->weight("2098"); else wt_pdf_98_=1.0;
      //if(eventInfo->weight_defined("2099")) wt_pdf_99_ = eventInfo->weight("2099"); else wt_pdf_99_=1.0;
      //if(eventInfo->weight_defined("2100")) wt_pdf_100_ = eventInfo->weight("2100"); else wt_pdf_100_=1.0;
      //
      ////alpha_s variation weights
      //if(eventInfo->weight_defined("2101")) wt_alphasdown_ = eventInfo->weight("2101"); else wt_alphasdown_=1.0; 
      //if(eventInfo->weight_defined("2102")) wt_alphasup_ = eventInfo->weight("2102"); else wt_alphasup_=1.0;
    }
    
    if (event->Exists("D0")) D0_ = event->Get<float>("D0");
    else D0_ = -9999;
    if (event->Exists("DCP")) DCP_ = event->Get<float>("DCP");
    else DCP_ = -9999; 
    if(D0_!=-9999&&DCP_!=-9999) D0star_ = D0_*DCP_/fabs(DCP_);
    else D0star_ = -9999;
    
    std::vector<ic::GenParticle*> gen_particles = event->GetPtrVec<ic::GenParticle>("genParticles");
    std::vector<ic::GenJet*> gen_jets = event->GetPtrVec<ic::GenJet>("genJets");

    std::vector<ic::GenParticle> higgs_products;
    std::vector<ic::GenParticle> gen_taus;
    ic::Candidate met; 
    std::vector<ic::GenParticle> prompt_leptons;
    std::vector<std::string> decay_types;

    double pT=0;
    HiggsPt_=-9999;
    partons_lhe_=0;
    partons_=0;
    parton_mjj_=-9999;
    parton_HpT_=-9999;
    double higgs_eta = 0;
    std::vector<double> parton_pt_vec = {};
    bool lhe_exists = event->ExistsInTree("lheParticles");
    if(lhe_exists){
      std::vector<GenParticle*> const& lhe_parts = event->GetPtrVec<GenParticle>("lheParticles");
      parton_pt_=-9999;
      std::vector<GenParticle*> outparts;
      for(unsigned i = 0; i< lhe_parts.size(); ++i){
           if(lhe_parts[i]->status() != 1) continue;
           unsigned id = abs(lhe_parts[i]->pdgid());
           if(id==25) parton_HpT_ = lhe_parts[i]->pt();
           if ((id >= 1 && id <=6) || id == 21){ 
             outparts.push_back(lhe_parts[i]);
             partons_++;
             parton_pt_vec.push_back(lhe_parts[i]->pt());
             if(lhe_parts[i]->pt()>=10) partons_lhe_++; 
        }
      }
      std::sort(outparts.begin(),outparts.end(),PtComparatorGenPart());
      if(outparts.size()>1) parton_mjj_ = (outparts[0]->vector()+outparts[1]->vector()).M();
      else parton_mjj_ = -9999;
      if(outparts.size()>2){
        double parton_mjj_2 = (outparts[0]->vector()+outparts[2]->vector()).M(); 
        double parton_mjj_3 = (outparts[1]->vector()+outparts[2]->vector()).M();  
        if(parton_mjj_ < std::max(parton_mjj_2, parton_mjj_3)) parton_mjj_ = std::max(parton_mjj_2, parton_mjj_3);
   
      }
    }
    std::sort(parton_pt_vec.begin(),parton_pt_vec.end());
    std::reverse(parton_pt_vec.begin(),parton_pt_vec.end());
    if (parton_pt_vec.size()>0) parton_pt_ = parton_pt_vec[0];
    else parton_pt_ = -9999;
    if (parton_pt_vec.size()>1) parton_pt_2_ = parton_pt_vec[1];
    else parton_pt_2_ = -9999;
    if (parton_pt_vec.size()>2) parton_pt_3_ = parton_pt_vec[2];
    else parton_pt_3_ = -9999;

    npNLO_ = eventInfo->npNLO();
    if(npNLO_<0) npNLO_ = 2; 
    double n_inc_ = 3089015.;
    double n2_    = 14254055;
    double f2_   = 0.279662;
    if(npNLO_>=2) wt_stitch_ = (n_inc_*f2_) / ( (n_inc_*f2_) + n2_ );
    else wt_stitch_=1.;
    
    for(unsigned i=0; i<gen_particles.size(); ++i){
      if((gen_particles[i]->statusFlags()[FromHardProcessBeforeFSR] || gen_particles[i]->statusFlags()[IsLastCopy]) && gen_particles[i]->pdgid() == 25) {
          HiggsPt_ = gen_particles[i]->pt();
           higgs_eta = gen_particles[i]->eta();
           wt_topmass_ = topmass_wts_toponly_.GetBinContent(topmass_wts_toponly_.FindBin(HiggsPt_))*1.006;
           wt_topmass_2_ = topmass_wts_.GetBinContent(topmass_wts_.FindBin(HiggsPt_))*0.985; //*sm = 0.985022, mix= 0.985167 ps=0.985076 -> all = 0.985 to 3dp so use thsi number
      }

      
      ic::GenParticle part = *gen_particles[i];
      ic::GenParticle higgs_product;
      
      unsigned genID = std::fabs(part.pdgid());
      bool status_flag_t = part.statusFlags().at(0);
      bool status_flag_tlc = part.statusFlags().at(13);
      bool status_hard_process = part.statusFlags().at(7);
      
      if (!lhe_exists && status_hard_process &&(genID == 1 || genID == 2 || genID == 3 || genID == 4 || genID == 5 || genID == 6 || genID == 21) && gen_particles[part.mothers().at(0)]->pdgid() != 2212 ) partons_++;
 
      if(genID==36 && gen_particles[i]->statusFlags()[IsLastCopy]){
        pT = gen_particles[i]->vector().Pt();
        pT_A_ = pT;
      }
      if(genID==25 && gen_particles[i]->statusFlags()[IsLastCopy]){
        pT = gen_particles[i]->vector().Pt();
        pT_A_ = pT;
      }

      std::vector<ic::Electron*> reco_electrons = {};//event->GetPtrVec<ic::Electron>("electrons");
      std::vector<ic::Muon*> reco_muons = {};//event->GetPtrVec<ic::Muon>("muons");     

      // add neutrinos 4-vectors to get gen met
      if(genID == 12 || genID == 14 || genID == 16){
        met.set_vector(met.vector() + part.vector());
        continue;
      }
      if(channel_str_=="zmm") {
        if(!(genID == 13 && gen_particles[i]->statusFlags()[IsPrompt] && gen_particles[i]->statusFlags()[IsLastCopy])) continue;
        higgs_products.push_back(*(gen_particles[i]));
        decay_types.push_back("m");
        std::vector<ic::GenParticle *> match_muons = {gen_particles[i]};
        if(fabs(gen_particles[i]->eta())<2.4 && gen_particles[i]->pt()>20.) {
          if(decay_types.size()==1){
            cand_1_ = true;
            match_1_ = (MatchByDR(match_muons,reco_muons,0.5,true,true).size()>0);
          } else if (decay_types.size()==2) {
            cand_2_ = true;
            match_2_ = (MatchByDR(match_muons,reco_muons,0.5,true,true).size()>0);
          }
        }
      }
      if(channel_str_=="zee") {
        if(!(genID == 11 && gen_particles[i]->statusFlags()[IsPrompt] && gen_particles[i]->statusFlags()[IsLastCopy])) continue;
        higgs_products.push_back(*(gen_particles[i]));
        decay_types.push_back("e");
        std::vector<ic::GenParticle *> match_elecs = {gen_particles[i]};
        if(fabs(gen_particles[i]->eta())<2.5 && gen_particles[i]->pt()>20.) {
          if(decay_types.size()==1){
            cand_1_ = true;
            match_1_ = (MatchByDR(match_elecs,reco_electrons,0.5,true,true).size()>0);
          } else if (decay_types.size()==2) {
            cand_2_ = true;
            match_2_ = (MatchByDR(match_elecs,reco_electrons,0.5,true,true).size()>0); 
          }
        }
      }
      if(!(genID == 15 && status_flag_t && status_flag_tlc)) continue;
      gen_taus.push_back(part);
      std::vector<ic::GenParticle> family;
      unsigned outputID = 15;
      FamilyTree(family, part, gen_particles, outputID);
      if(family.size()==1 && (outputID ==11 || outputID ==13)){
        higgs_products.push_back(family[0]);
        if (outputID == 11) {decay_types.push_back("e");}  
        else if (outputID == 13) {decay_types.push_back("m");}
      } else {
        decay_types.push_back("t");  
        ic::GenParticle had_tau;
        int charge = 0;
        int pdgid = 15;
        for(unsigned j=0; j<family.size(); ++j){
          had_tau.set_vector(had_tau.vector() + family[j].vector());
          charge += family[j].charge();
        }
        pdgid = 15*charge;
        had_tau.set_charge(charge);
        had_tau.set_pdgid(pdgid);
        higgs_products.push_back(had_tau);
      }
    }

    std::sort(higgs_products.begin(),higgs_products.end(),PtComparator());
    std::sort(gen_taus.begin(),gen_taus.end(),PtComparator());
    
    if(gen_taus.size()>=2){
      genpt_1_ = gen_taus[0].vector().Pt();
      genpt_2_ = gen_taus[1].vector().Pt();
      geneta_1_ = gen_taus[0].vector().Rapidity();
      geneta_2_ = gen_taus[1].vector().Rapidity();
    } else {
      genpt_1_ =  -9999;
      genpt_2_ =  -9999;
      geneta_1_ = -9999;
      geneta_2_ = -9999; 
    }
    
    std::vector<ic::GenParticle> electrons;
    std::vector<ic::GenParticle> muons;
    std::vector<ic::GenParticle> taus;
    
    double min_tau_pt[2];
    min_tau_pt[0]     = min_tau1_pt_;
    min_tau_pt[1]     = min_tau2_pt_;
    
    for(unsigned i=0; i<higgs_products.size(); ++i){
      unsigned ID = std::fabs(higgs_products[i].pdgid());
      double eta = std::fabs(higgs_products[i].vector().Rapidity());
      double pt = higgs_products[i].vector().Pt();
      if(ID == 11){
        if(pt > min_e_pt_ && eta < max_e_eta_) electrons.push_back(higgs_products[i]);  
      } else if(ID == 13){
        if(pt > min_mu_pt_ && eta < max_mu_eta_) muons.push_back(higgs_products[i]);  
      } else if(ID == 15){
        if(pt > min_tau_pt[i] && eta < max_tau_eta_) taus.push_back(higgs_products[i]);
      }
    }

    //size of decay_types vector should always be 2 but added this if statement just to be sure
    decayType = "";
    std::sort(decay_types.begin(),decay_types.end(),swap_labels());
    for(unsigned i=0; i< decay_types.size(); ++i){
      decayType += decay_types[i];
    }
    
    if(decayType == "ee") count_ee_++;
    if(decayType == "em") count_em_++;
    if(decayType == "et") count_et_++;
    if(decayType == "mm") count_mm_++;
    if(decayType == "mt") count_mt_++;
    if(decayType == "tt") count_tt_++;

    pt_1_ = -9999.;
    pt_2_ = -9999.;
    ic::Candidate lep1;
    ic::Candidate lep2;
    passed_ = false;
    
    if(channel_str_ == "ee"){
      if(electrons.size() == 2){
        lep1 = electrons[0];
        lep2 = electrons[1];
        passed_ = true;
      }
    } else if(channel_str_ == "mm"){
      if(muons.size() == 2){
        lep1 = muons[0];
        lep2 = muons[1];
        passed_ = true;
      }
    } else if(channel_str_ == "zmm"){
      if(muons.size() == 2){
        lep1 = muons[0];
        lep2 = muons[1];
        passed_ = true;
      }
    } else if(channel_str_ == "em"){
      if(electrons.size() == 1 && muons.size() == 1){
        lep1 = electrons[0];
        lep2 = muons[0];
        passed_ = true;
      }
    } else if(channel_str_ == "et"){
      if(electrons.size() == 1 && taus.size() == 1){
        lep1 = electrons[0];
        lep2 = taus[0];
        passed_ = true;
      }
    } else if(channel_str_ == "mt"){
      if(muons.size() == 1 && taus.size() == 1){
        lep1 = muons[0];
        lep2 = taus[0];
        passed_ = true;
      }
    } else if(channel_str_ == "tt"){
      if(taus.size() == 2){
        lep1 = taus[0];
        lep2 = taus[1];
        passed_ = true;
      }
    }

    std::vector<GenJet> gen_tau_jets = BuildTauJets(gen_particles, false,true);
    std::vector<GenJet *> gen_tau_jets_ptr;
    for (auto & x : gen_tau_jets) gen_tau_jets_ptr.push_back(&x);
    ic::erase_if(gen_tau_jets_ptr, !boost::bind(MinPtMaxEta, _1, 15.0, 999.));
    std::sort(gen_tau_jets_ptr.begin(), gen_tau_jets_ptr.end(), bind(&Candidate::pt, _1) > bind(&Candidate::pt, _2));
    cp_sign_1_ = 999;
    cp_sign_2_ = 999;
    cp_sign_3_ = 999;
    cp_sign_4_ = 999;
    aco_angle_1_ = 9999.;
    aco_angle_2_ = 9999.;
    aco_angle_3_ = 9999.;
    aco_angle_4_ = 9999.;
    cp_channel_=-1;

    std::vector<ic::Vertex*> primary_vtxs = event->GetPtrVec<ic::Vertex>("genVertices"); 
    
    std::pair<bool,GenParticle*> pi_1 = std::make_pair(false, new GenParticle());
    std::pair<bool,std::vector<GenParticle*>> rho_1 = std::make_pair(false, std::vector<GenParticle*>()); 
    std::pair<bool,std::vector<GenParticle*>> a1_1 = std::make_pair(false, std::vector<GenParticle*>());
    std::pair<bool,GenParticle*> pi_2 = std::make_pair(false, new GenParticle());
    std::pair<bool,std::vector<GenParticle*>> rho_2 = std::make_pair(false, std::vector<GenParticle*>()); 
    std::pair<bool,std::vector<GenParticle*>> a1_2 = std::make_pair(false, std::vector<GenParticle*>());
    
    if(gen_tau_jets_ptr.size()>=1){
      pi_1 = GetTauPiDaughter(gen_particles, gen_tau_jets_ptr[0]->constituents()); 
      rho_1 = GetTauRhoDaughter(gen_particles, gen_tau_jets_ptr[0]->constituents());  
      a1_1 = GetTauA1Daughter(gen_particles, gen_tau_jets_ptr[0]->constituents());  
    } 
    if(gen_tau_jets_ptr.size()>=2){
      pi_2 = GetTauPiDaughter(gen_particles, gen_tau_jets_ptr[1]->constituents()); 
      rho_2 = GetTauRhoDaughter(gen_particles, gen_tau_jets_ptr[1]->constituents());  
      a1_2 = GetTauA1Daughter(gen_particles, gen_tau_jets_ptr[1]->constituents()); 
    }
    /* std::vector<ic::GenParticle> leptons;
    for (unsigned i=0; i<electrons.size(); ++i) leptons.push_back(electrons[i]);
    for (unsigned i=0; i<muons.size(); ++i) leptons.push_back(muons[i]);
    TLorentzVector lvec1;
    TLorentzVector lvec2;
    TLorentzVector lvec3;
    TLorentzVector lvec4;
    if(leptons.size()>=2){
      cp_channel_=1;
      lvec1 = TLorentzVector(GetGenImpactParam(*(primary_vtxs[0]),leptons[0].vtx(), leptons[0].vector()),0);    
      lvec2 = TLorentzVector(GetGenImpactParam(*(primary_vtxs[0]),leptons[1].vtx(), leptons[1].vector()),0);
      lvec3 = ConvertToLorentz(leptons[0].vector());
      lvec4 = ConvertToLorentz(leptons[1].vector());
    } else if(leptons.size()==1){
      lvec1 = TLorentzVector(GetGenImpactParam(*(primary_vtxs[0]),leptons[0].vtx(), leptons[0].vector()),0);
      lvec3 = ConvertToLorentz(leptons[0].vector());
      if(pi_1.first) {
        cp_channel_=1; 
        lvec2 = TLorentzVector(GetGenImpactParam(*(primary_vtxs[0]),pi_1.second->vtx(), pi_1.second->vector()),0); 
        lvec4 = ConvertToLorentz(pi_1.second->vector());
      }
      if(pi_2.first) {
        cp_channel_=1; 
        lvec2 = TLorentzVector(GetGenImpactParam(*(primary_vtxs[0]),pi_2.second->vtx(), pi_2.second->vector()),0); 
        lvec4 = ConvertToLorentz(pi_2.second->vector());
      }
      if(rho_1.first) {
        cp_channel_=2; 
        lvec2 = ConvertToLorentz(rho_1.second[1]->vector()); 
        lvec4 = ConvertToLorentz(rho_1.second[0]->vector()); 
        cp_sign_1_ = YRho(rho_1.second,TVector3());
      }
      if(rho_2.first) {
        cp_channel_=2; 
        lvec2 = ConvertToLorentz(rho_2.second[1]->vector()); 
        lvec4 = ConvertToLorentz(rho_2.second[0]->vector()); 
        cp_sign_1_ = YRho(rho_2.second,TVector3());
      }
    } else{
      if(pi_1.first&&pi_2.first){
        cp_channel_=1;
        lvec1 = TLorentzVector(GetGenImpactParam(*(primary_vtxs[0]),pi_1.second->vtx(), pi_1.second->vector()),0);
        lvec2 = TLorentzVector(GetGenImpactParam(*(primary_vtxs[0]),pi_2.second->vtx(), pi_2.second->vector()),0);
        lvec3 = ConvertToLorentz(pi_1.second->vector());
        lvec4 = ConvertToLorentz(pi_2.second->vector());
      } else if (pi_1.first&&rho_2.first){
        cp_channel_=2;
        lvec1 = TLorentzVector(GetGenImpactParam(*(primary_vtxs[0]),pi_1.second->vtx(), pi_1.second->vector()),0);
        lvec2 = ConvertToLorentz(rho_2.second[1]->vector());
        lvec3 = ConvertToLorentz(pi_1.second->vector());
        lvec4 = ConvertToLorentz(rho_2.second[0]->vector());
        cp_sign_1_ = YRho(rho_2.second,TVector3());
      } else if(pi_2.first&&rho_1.first){
        cp_channel_=2;
        lvec1 = TLorentzVector(GetGenImpactParam(*(primary_vtxs[0]),pi_2.second->vtx(), pi_2.second->vector()),0);
        lvec2 = ConvertToLorentz(rho_1.second[1]->vector());
        lvec3 = ConvertToLorentz(pi_2.second->vector());
        lvec4 = ConvertToLorentz(rho_1.second[0]->vector());
        cp_sign_1_ = YRho(rho_1.second,TVector3());
      } else if (rho_1.first&&rho_2.first){
        cp_channel_=3;  
        lvec1 = ConvertToLorentz(rho_1.second[1]->vector());   
        lvec2 = ConvertToLorentz(rho_2.second[1]->vector());
        lvec3 = ConvertToLorentz(rho_1.second[0]->vector());   
        lvec4 = ConvertToLorentz(rho_2.second[0]->vector());
        cp_sign_1_ = YRho(rho_1.second,TVector3())*YRho(rho_2.second,TVector3());
      }
    }
    
    if(cp_channel_!=-1){
      aco_angle_1_ = IPAcoAngle(lvec1, lvec2, lvec3, lvec4,false);    
      aco_angle_2_ = IPAcoAngle(lvec1, lvec2, lvec3, lvec4,true);
    } */
    
    /* if(gen_tau_jets_ptr.size()>=2){
      if(rho_1.first && rho_2.first) { 
        std::vector<std::pair<double,int>> angles = AcoplanarityAngles(rho_1.second,rho_2.second,true);
        aco_angle_2_ = angles[0].first;
        cp_sign_2_ = angles[0].second;
      }
      if(rho_1.first && a1_2.first) {
        cp_channel_ = 3;
        std::vector<std::pair<double,int>> angles = AcoplanarityAngles(rho_1.second,a1_2.second,true);
        aco_angle_1_ = angles[0].first;
        cp_sign_1_ = angles[0].second;
        aco_angle_2_ = angles[1].first;
        cp_sign_2_ = angles[1].second;
        aco_angle_3_ = angles[2].first;
        cp_sign_3_ = angles[2].second;
        aco_angle_4_ = angles[3].first;
        cp_sign_4_ = angles[3].second;
      }
      if(a1_1.first && rho_2.first) {
        cp_channel_ = 3;
        std::vector<std::pair<double,int>> angles = AcoplanarityAngles(rho_2.second,a1_1.second,true);
        aco_angle_1_ = angles[0].first;
        cp_sign_1_ = angles[0].second;
        aco_angle_2_ = angles[1].first;
        cp_sign_2_ = angles[1].second;
        aco_angle_3_ = angles[2].first;
        cp_sign_3_ = angles[2].second;
        aco_angle_4_ = angles[3].first;
        cp_sign_4_ = angles[3].second;
      }

    } */

    if(passed_){
      pt_1_  = lep1.vector().Pt();
      pt_2_  = lep2.vector().Pt();
      eta_1_ = lep1.vector().Rapidity();
      eta_2_ = lep2.vector().Rapidity();
      phi_1_ = lep1.vector().Phi();
      phi_2_ = lep2.vector().Phi();
      met_   = met.vector().Pt();
      pt_tt_ = (met.vector()+lep1.vector()+lep2.vector()).Pt();
      mass_ = (met.vector()+lep1.vector()+lep2.vector()).M();
      wtzpt_ = z_pt_weights_sm_.GetBinContent(z_pt_weights_sm_.FindBin(mass_,pt_tt_));
      m_vis_ = (lep1.vector()+lep2.vector()).M();
      if(!(channel_str_ == "zmm")){
        mt_1_ = MT(&lep1, &met);
        mt_2_ = MT(&lep2, &met);
      }

      ic::CompositeCandidate *ditau = new ic::CompositeCandidate();
      ditau->AddCandidate("lep1",&lep1);
      ditau->AddCandidate("lep2",&lep2);
      pzeta_ = PZeta(ditau, &met , 0.85);
    } else {
      pt_1_  = -9999;
      pt_2_  = -9999;
      eta_1_ = -9999;
      eta_2_ = -9999;
      phi_1_ = -9999;
      phi_2_ = -9999;
      met_   = -9999;
      pt_tt_ = -9999;
      mass_= -9999;
      m_vis_ = -9999;
      mt_1_ = -9999;
      mt_2_ = -9999;
      pzeta_ = -9999;
    }
    
    std::vector<ic::GenJet> filtered_jets;
    std::vector<ic::GenJet> bjets;
    
    std::vector<GenParticle *> sel_bquarks;
    for (unsigned i=0; i < gen_particles.size(); ++i){
      std::vector<bool> status_flags = gen_particles[i]->statusFlags();
      unsigned id = abs(gen_particles[i]->pdgid());  
      if(id == 5 && status_flags[FromHardProcess] && status_flags[IsLastCopy] && gen_particles[i]->vector().Pt()>0){
        sel_bquarks.push_back(gen_particles[i]);
      }
    }
     
    for(unsigned i=0; i<gen_jets.size(); ++i){
      ic::GenJet jet = *gen_jets[i];
      double jetPt = jet.vector().Pt();
      double jetEta = std::fabs(jet.vector().Rapidity());
      if(jetPt > min_jet_pt_ && jetEta < max_jet_eta_) filtered_jets.push_back(jet); 
      if(jetPt > 20 && jetEta < 2.4){
          bool MatchedToB = false;
          for(unsigned j=0; j<sel_bquarks.size(); ++j) if(DRLessThan(std::make_pair(&jet, sel_bquarks[j]),0.5)) MatchedToB = true;
          if(MatchedToB) bjets.push_back(jet); 
      }
    }
    
    for(unsigned i=0; i<bjets.size(); ++i){
      ic::GenJet jet = bjets[i];
      bool MatchedToPrompt = false;
      for(unsigned j=0; j<higgs_products.size(); ++j){
        if(DRLessThan(std::make_pair(&jet, &higgs_products[j]),0.5)) MatchedToPrompt = true;
      }
      //remove jets that are matched to Higgs decay products
      if(MatchedToPrompt) bjets.erase (bjets.begin()+i);
    }
    
    n_bjets_noscale_ = bjets.size();
    
    for(unsigned i=0;  i<bjets.size(); ++i){
      ic::GenJet jet = bjets[i];
      double pt = bjets[i].vector().Pt();
      double eta = fabs(bjets[i].vector().Rapidity());
      double eff=0;
      if(pt > bbtag_eff_->GetXaxis()->GetBinLowEdge(bbtag_eff_->GetNbinsX()+1)){
        eff = bbtag_eff_->GetBinContent(bbtag_eff_->GetNbinsX(),bbtag_eff_->GetYaxis()->FindBin(eta));
      } else{
        eff = bbtag_eff_->GetBinContent(bbtag_eff_->GetXaxis()->FindBin(pt),bbtag_eff_->GetYaxis()->FindBin(eta));
      }
      rand->SetSeed((int)((bjets[i].eta()+5)*100000));
      double randVal = rand->Uniform();
      if (randVal > eff) bjets.erase (bjets.begin()+i);
    }
    n_bjets_ = bjets.size();
    n_jets_nofilter_ = filtered_jets.size();
    
    for(unsigned i=0; i<filtered_jets.size(); ++i){
      ic::GenJet jet = filtered_jets[i];
      bool MatchedToPrompt = false;
      for(unsigned j=0; j<higgs_products.size(); ++j){
        if(DRLessThan(std::make_pair(&jet, &higgs_products[j]),0.5)) MatchedToPrompt = true;
      }
      //remove jets that are matched to Higgs decay products
      if(MatchedToPrompt) filtered_jets.erase (filtered_jets.begin()+i);
    }
    n_jets_ = filtered_jets.size();
    jpt_1_       = -9999;
    jeta_1_      = -9999;
    jphi_1_      = -9999;
    jpt_2_       = -9999;
    jpt_3_       = -9999;
    jeta_2_      = -9999;
    jphi_2_      = -9999;
    mjj_         = -9999;
    jdeta_       = -9999;
    n_jetsingap_ = 9999;
    if(n_jets_ > 0){
      jpt_1_  = filtered_jets[0].vector().Pt();
      jeta_1_ = filtered_jets[0].vector().Rapidity();
      jphi_1_ = filtered_jets[0].vector().Phi();
    }
    if(n_jets_ > 1){
      jpt_2_  = filtered_jets[1].vector().Pt();
      jeta_2_ = filtered_jets[1].vector().Rapidity();
      jphi_2_ = filtered_jets[1].vector().Phi();
      mjj_   = (filtered_jets[0].vector()+filtered_jets[1].vector()).M();
      jdeta_  = std::fabs(filtered_jets[0].vector().Rapidity() - filtered_jets[1].vector().Rapidity());
      double max_jeta = std::max(jeta_1_,jeta_2_);
      double min_jeta = std::min(jeta_1_,jeta_2_);
      n_jetsingap_ = 0;
      for(unsigned i=2; i<n_jets_; ++i){
         double jeta_3 = filtered_jets[i].vector().Rapidity();
         if(jeta_3 > min_jeta && jeta_3 < max_jeta) n_jetsingap_++;    
      }
    }
    if(n_jets_ > 2){
      jpt_3_  = filtered_jets[2].vector().Pt();      
    }

    n_pjets_=0;    
    if(filtered_jets.size()>=2){
      if(filtered_jets[0].eta() > filtered_jets[1].eta()){
        sjdphi_ =  ROOT::Math::VectorUtil::DeltaPhi(filtered_jets[0].vector(), filtered_jets[1].vector());
      }
      else{
        sjdphi_ =  ROOT::Math::VectorUtil::DeltaPhi(filtered_jets[1].vector(), filtered_jets[0].vector());
      }
      // sort jets higher and lower than higgs eta_1
      std::vector<GenJet> jets_high;
      std::vector<GenJet> jets_low;
      for (unsigned i=0; i<filtered_jets.size(); ++i){
        if (filtered_jets[i].eta() > higgs_eta) jets_high.push_back(filtered_jets[i]);
        else jets_low.push_back(filtered_jets[i]);
      }
      if(jets_low.size()>0) n_pjets_++;
      if(jets_high.size()>0) n_pjets_++;
      Candidate pseudo_jet_a;
      Candidate pseudo_jet_b;
      for (auto j : jets_low) pseudo_jet_a.set_vector(pseudo_jet_a.vector()+j.vector());
      for (auto j : jets_high) pseudo_jet_b.set_vector(pseudo_jet_b.vector()+j.vector());
      spjdphi_ =  ROOT::Math::VectorUtil::DeltaPhi(pseudo_jet_a.vector(),pseudo_jet_b.vector());
      for (unsigned i=0; i<filtered_jets.size(); ++i){
        double dEta = std::fabs(higgs_eta - filtered_jets[i].eta());
        if(i==0 || dEta<ysep_) ysep_ = dEta;
      }
    } else {
      sjdphi_ = -9999;
      spjdphi_ = -9999;
    }

    /* wt_ps_down_ = 1.0; */
    /* wt_ps_up_ = 1.0; */
    /* if(n_jets_==0){ */
    /*   wt_ps_up_ =  ps_0jet_up_  .GetBinContent(ps_0jet_up_  .FindBin(HiggsPt_)); */  
    /*   wt_ps_down_ =  ps_0jet_down_.GetBinContent(ps_0jet_down_.FindBin(HiggsPt_)); */   
    /* } */
    /* if(n_jets_==1){ */ 
    /*   wt_ps_up_ =  ps_1jet_up_ .GetBinContent(ps_1jet_up_  .FindBin(HiggsPt_)); */  
    /*   wt_ps_down_ =  ps_1jet_down_.GetBinContent(ps_1jet_down_.FindBin(HiggsPt_)); */   
    /* } */
    /* if(n_jets_==2){ */
    /*   wt_ps_up_ =  ps_2jet_up_  .GetBinContent(ps_2jet_up_  .FindBin(HiggsPt_)); */  
    /*   wt_ps_down_ =  ps_2jet_down_.GetBinContent(ps_2jet_down_.FindBin(HiggsPt_)); */     
    /* } */
    /* if(n_jets_>2){ */
    /*   wt_ps_up_ =  ps_3jet_up_  .GetBinContent(ps_3jet_up_  .FindBin(HiggsPt_)); */
    /*   wt_ps_down_ =  ps_3jet_down_.GetBinContent(ps_3jet_down_.FindBin(HiggsPt_)); */
    /* } */
    /* wt_ue_up_ = ue_up_  .GetBinContent(ue_up_  .FindBin(n_jets_)); */
    /* wt_ue_down_ = ue_down_  .GetBinContent(ue_down_  .FindBin(n_jets_)); */


    std::vector<PileupInfo *> puInfo;
    float true_int = -1;
    
    if(event->ExistsInTree("pileupInfo")){
      puInfo = event->GetPtrVec<PileupInfo>("pileupInfo");
        for (unsigned i = 0; i < puInfo.size(); ++i) {
          if (puInfo[i]->bunch_crossing() == 0)
            true_int = puInfo[i]->true_num_interactions();
        }
    
      n_pu_ = true_int;
    }
    
    auto args = std::vector<double>{pT};
    if(fns_["h_t_ratio"]){
      wt_ggh_t_ = fns_["h_t_ratio"]->eval(args.data());        
      wt_ggh_b_ = fns_["h_b_ratio"]->eval(args.data());
      wt_ggh_i_ = fns_["h_i_ratio"]->eval(args.data());
      wt_ggH_t_ = fns_["H_t_ratio"]->eval(args.data());
      wt_ggH_b_ = fns_["H_b_ratio"]->eval(args.data());
      wt_ggH_i_ = fns_["H_i_ratio"]->eval(args.data());
      wt_ggA_t_ = fns_["A_t_ratio"]->eval(args.data());
      wt_ggA_b_ = fns_["A_b_ratio"]->eval(args.data());
      wt_ggA_i_ = fns_["A_i_ratio"]->eval(args.data());
    }

    if(fs_) outtree_->Fill();
    
    return 0;
  }
  int HTTGenAnalysis::PostAnalysis() {
    std::cout << "ee count = " << count_ee_ << std::endl;
    std::cout << "em count = " << count_em_ << std::endl;
    std::cout << "et count = " << count_et_ << std::endl;
    std::cout << "mm count = " << count_mm_ << std::endl;
    std::cout << "mt count = " << count_mt_ << std::endl;
    std::cout << "tt count = " << count_tt_ << std::endl;
    return 0;
  }

  void HTTGenAnalysis::PrintInfo() {
    ;
  }

}
