# import ROOT in batch mode
import sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
import ROOT
ROOT.gROOT.SetBatch(True)
sys.argv = oldargv

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.FWLiteEnabler.enable()

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events
from PhysicsTools.HeppyCore.utils.deltar import deltaR,bestMatch

triggerBits, triggerBitLabel = Handle("edm::TriggerResults"), ("TriggerResults","","HLTX")
triggerObjects, triggerObjectLabel  = Handle("std::vector<pat::TriggerObjectStandAlone>"), ("selectedPatTriggerCustom","","HLTX")
triggerPrescales, triggerPrescaleLabel  = Handle("pat::PackedTriggerPrescales"), ("patTrigger","","PAT")

finalObjsHandle,finalObjsLabel = Handle("trigger::TriggerFilterObjectWithRefs"),("hltMatchedVBFTwoPFJets2CrossCleanedFromDoubleLooseChargedIsoPFTau20","","HLTX")
ROOT.gROOT.ProcessLine("std::vector<reco::PFJetRef> jets;")
TriggerJet = +85

tauObjsHandle, tauObjsLabel = Handle("trigger::TriggerFilterObjectWithRefs"),("hltDoublePFTau20TrackPt1LooseChargedIsolationReg","","HLTX")
ROOT.gROOT.ProcessLine("std::vector<reco::PFTauRef> taus;")
TriggerTau = +84

jetsOffHandle, jetsOffLabel = Handle("std::vector<pat::Jet>"), ("slimmedJets","","PAT")
tausOffHandle, tausOffLabel = Handle("std::vector<pat::Tau>"), ("slimmedTaus","","PAT")

l1tmatched2mjjjetsHandle,l1tmatched2mjjjetsLabel = Handle('std::vector<reco::PFJet>'),('hltVBFL1TLooseIDPFJetsMatching','TwoJets','HLTX')

AK4jetsHandle  = Handle ('std::vector<reco::PFJet>')
AK4jetsLabel = ("hltAK4PFJetsLooseIDCorrected","","HLTX")

L1ObjsHandle, L1ObjsLabel = Handle("trigger::TriggerFilterObjectWithRefs"),("hltL1VBFDiJetOR","","HLTX")
ROOT.gROOT.ProcessLine("std::vector<reco::PFJetRef> l1jets;")
TriggerJet = +85

#events = Events(sys.argv[1])
events = Events ('outputFULL.root')


for iev,event in enumerate(events):
    event.getByLabel(triggerBitLabel, triggerBits)
    event.getByLabel(triggerObjectLabel, triggerObjects)
    event.getByLabel(triggerPrescaleLabel, triggerPrescales)

    try:
        event.getByLabel(l1tmatched2mjjjetsLabel,l1tmatched2mjjjetsHandle)
        l1tmatched2mjjjets = l1tmatched2mjjjetsHandle.product()

        event.getByLabel(finalObjsLabel,finalObjsHandle)
        finalObjs = finalObjsHandle.product()
        finalObjs.getObjects(TriggerJet, ROOT.jets)

        print "\nnumber of HLT jets in final 2jet filter: ",len(ROOT.jets)

        print ""


        for jetindex, jet in enumerate(ROOT.jets):
            print "jet ", jetindex
            print "pt: ", jet.pt(), "eta: ", jet.eta(), "phi: ", jet.phi()

        event.getByLabel(tauObjsLabel,tauObjsHandle)
        tauObjs = tauObjsHandle.product()
        tauObjs.getObjects(TriggerTau, ROOT.taus)
        print "number of HLT taus in final filter: ",len(ROOT.taus)

        for tauindex, tau in enumerate(ROOT.taus):
            print "tau ", tauindex
            print "pt: ", tau.pt(), "eta: ", tau.eta(), "phi: ", tau.phi()

        print ""


        ## mjj calc from HLT Ak4 loose jets
        event.getByLabel(AK4jetsLabel,AK4jetsHandle)
        ak4jets = AK4jetsHandle.product()
        ak4jets = filter(lambda x: x.pt()>40., ak4jets)
        for jetindex,jet in enumerate(ak4jets):
            print "ak4 jet: ", jetindex, "pt: ", jet.pt(), "eta: ", jet.eta(), "phi: ", jet.phi()
        for i in range(len(ak4jets)-1):
            for j in range(i+1,len(ak4jets)):
                mjj = (ak4jets[i].p4()+ak4jets[j].p4()).M()
                print "index i: ", i, "index j: ", j
                print "\tmjj: ", mjj

        print ""



        # check order of overlap removal
        # i.e. if looping of taus and then
        # jets is better compared to current
        # implementation

        for tauindex, tau in enumerate(ROOT.taus):
            isMatched = False
            for jetindex,jet in enumerate(ak4jets):
                if deltaR(tau.p4(),jet.p4()) < 0.3:
                    isMatched = True
                    print 'HLT tau ', tauindex, ' matched to HLT ak4 jet ', jetindex , ': HLT tau pt', tau.pt(), 'HLT jet pt', jet.pt()


        print ""

        for jetindex,jet in enumerate(l1tmatched2mjjjets):
            print "L1T matched max mjj 2 jet: ", jetindex, "pt: ", jet.pt(), "eta: ", jet.eta(), "phi: ", jet.phi()

        print ""


    except RuntimeError:
        continue

    print "\nEvent %d: run %6d, lumi %4d, event %12d" % (iev,event.eventAuxiliary().run(), event.eventAuxiliary().luminosityBlock(),event.eventAuxiliary().event())

    print "\n === TRIGGER OBJECTS ==="
    for j,to in enumerate(triggerObjects.product()):
        to.unpackFilterLabels(event.object(), triggerBits.product());
        print "Trigger object pt %6.2f eta %+5.3f phi %+5.3f  " % (to.pt(),to.eta(),to.phi())
        print "         collection: ", to.collection()
        print "         type ids: ", ", ".join([str(f) for f in to.filterIds()])
        print "         filters: ", ", ".join([str(f) for f in to.filterLabels()])
        pathslast = set(to.pathNames(True))
        print "         paths:   ", ", ".join([("%s*" if f in pathslast else "%s")%f for f in to.pathNames()])

