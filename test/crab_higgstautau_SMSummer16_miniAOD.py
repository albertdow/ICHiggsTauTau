from WMCore.Configuration import Configuration
from multiprocessing import Process
config = Configuration()
config.section_('General')
config.General.transferOutputs = True
config.General.workArea='Nov20_MC_80X'
config.section_('JobType')
config.JobType.psetName = 'higgstautau_cfg_80X_Nov17.py'
config.JobType.pluginName = 'Analysis'
config.JobType.outputFiles = ['EventTree.root']
#config.JobType.inputFiles = ['Spring16_25nsV3_MC.db']
CfgParams = ['release=80XMINIAOD','isData=0','doHT=0', 'globalTag=80X_mcRun2_asymptotic_2016_TrancheIV_v8','isReHLT=1']
config.section_('Data')
#config.Data.inputDataset = 'DUMMY'
config.Data.unitsPerJob = 100000
#config.Data.unitsPerJob = 1
config.Data.splitting = 'EventAwareLumiBased'
config.Data.publication = False
#config.Data.ignoreLocality= True
config.Data.outLFNDirBase='/store/user/dwinterb/Nov20_MC_80X/'
config.section_('User')
config.section_('Site')
#config.Site.whitelist = ['T2_UK_London_IC', 'T2_CH_CERN', 'T2_FR_GRIF_LLR', 'T2_UK_SGrid_Bristol', 'T3_US_FNALLPC', 'T2_DE_DESY', 'T2_IT_Bari', 'T2_BE_IIHE', 'T2_IT_Rome','T2_FR_IPHC','T2_UK_London_Brunel']
#config.Site.blacklist  = ['T2_US_*']
config.Site.storageSite = 'T2_UK_London_IC'
config.JobType.allowUndistributedCMSSW = True

if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand
    from httplib import HTTPException

    # We want to put all the CRAB project directories from the tasks we submit here into one common directory.
    # That's why we need to set this parameter (here or above in the configuration file, it does not matter, we will not overwrite it).

    def submit(config):
        try:
            crabCommand('submit', config = config)
        except HTTPException, hte:
            print hte.headers

    #############################################################################################
    ## From now on that's what users should modify: this is the a-la-CRAB2 configuration part. ##
    #############################################################################################

    tasks=list()

    #commented out samples aren't available yet
    tasks.append(('VVTo2L2Nu','/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('VVTo2L2Nu-ext1','/VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM'))
    tasks.append(('ZZTo2L2Q','/ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('WWTo1L1Nu2Q','/WWTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('WWToLNuQQ','/WWToLNuQQ_13TeV-powheg/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('WWToLNuQQ-ext', '/WWToLNuQQ_13TeV-powheg/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM'))
    tasks.append(('WZTo2L2Q','/WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('WZTo1L3Nu','/WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('WZTo1L1Nu2Q','/WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v3/MINIAODSIM'))
    tasks.append(('WZJToLLLNu', '/WZJToLLLNu_TuneCUETP8M1_13TeV-amcnlo-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('ZZTo4L','/ZZTo4L_13TeV_powheg_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM')) 
    tasks.append(('QCDMuEnrichedPt15', '/QCD_Pt-20toInf_MuEnrichedPt15_TuneCUETP8M1_13TeV_pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('Tbar-tW','/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM'))
    tasks.append(('T-tW','/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM'))
    tasks.append(('Tbar-t','/ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('T-t', '/ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('TT','/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('WJetsToLNu','/WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'))
    tasks.append(('EWKWMinus2Jets_WToLNu', '/EWKWMinus2Jets_WToLNu_M-50_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'     ))
    tasks.append(('EWKWMinus2Jets_WToLNu-ext1', '/EWKWMinus2Jets_WToLNu_M-50_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM'))
    tasks.append(('EWKWMinus2Jets_WToLNu-ext2', '/EWKWMinus2Jets_WToLNu_M-50_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/MINIAODSIM'))
    tasks.append(('EWKWPlus2Jets_WToLNu', '/EWKWPlus2Jets_WToLNu_M-50_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'      ))
    tasks.append(('EWKWPlus2Jets_WToLNu-ext1', '/EWKWPlus2Jets_WToLNu_M-50_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM' ))
    tasks.append(('EWKWPlus2Jets_WToLNu-ext2', '/EWKWPlus2Jets_WToLNu_M-50_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/MINIAODSIM' ))
    tasks.append(('EWKZ2Jets_ZToLL', '/EWKZ2Jets_ZToLL_M-50_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'           ))
    tasks.append(('EWKZ2Jets_ZToLL-ext', '/EWKZ2Jets_ZToLL_M-50_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM'      ))
    tasks.append(('EWKZ2Jets_ZToNuNu', '/EWKZ2Jets_ZToNuNu_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/MINIAODSIM'              )) 
    tasks.append(('EWKZ2Jets_ZToNuNu-ext', '/EWKZ2Jets_ZToNuNu_13TeV-madgraph-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM'         ))    
    tasks.append(('ZZTo4L-amcat', '/ZZTo4L_13TeV-amcatnloFXFX-pythia8/RunIISummer16MiniAODv2-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/MINIAODSIM'))

    for task in tasks:
        print task[0]
        config.General.requestName = task[0]
        config.Data.inputDataset = task[1]
        #submit(config)
            
        if "GluGluToHToTauTau_M-125" in task[0] or "VBFHToTauTau_M-125" in task[0]:
            config.JobType.pyCfgParams = CfgParams + ['LHEWeights=True']
        else: config.JobType.pyCfgParams = CfgParams + ['LHEWeights=False']
            
        p = Process(target=submit, args=(config,))
        p.start()
        p.join()



