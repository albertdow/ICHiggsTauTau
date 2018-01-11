#!/bin/sh
cd /vols/build/cms/akd116/MLStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau
source /vols/grid/cms/setup.sh
source /vols/grid/cms/setup.sh
source /vols/grid/cms/setup.sh
source /vols/grid/cms/setup.sh
source /vols/grid/cms/setup.sh
export SCRAM_ARCH=slc6_amd64_gcc530
eval `scramv1 runtime -sh`
source /vols/build/cms/akd116/MLStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/scripts/setup_libs.sh
ulimit -c 0
#file_list=("Apr05_MC_80X_VBFHToTauTau_M-125" "Apr05_MC_80X_GluGluToHToTauTau_M-125" "Apr05_MC_80X_DYJetsToLL_M-10to50" "Apr05_MC_80X_TT" "Apr05_MC_80X_WJetsToLNu")
file_list=("Apr05_MC_80X_DYJetsToLL")
#file_list=("Apr05_MC_80X_TT")
#file_list=("Apr05_MC_80X_WJetsToLNu")

TODAY=`date +%Y%b%d`

for i in "${file_list[@]}" 
do
    echo running "$i"
    ./bin/HTT --cfg=scripts/config2016.json --json='{"job":{"filelist":"./filelists/'"${i}"'.dat"}, "sequence":{"output_name":"'"${TODAY}_${i}"'"}}' &> ${TODAY}_IC_MC_92X_${i}.log 
done
