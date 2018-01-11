cd /vols/build/cms/akd116/MLStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau
export SCRAM_ARCH=slc6_amd64_gcc481
eval `scramv1 runtime -sh`
source /vols/build/cms/akd116/MLStudies/CMSSW_8_0_25/src/UserCode/ICHiggsTauTau/Analysis/HiggsTauTau/scripts/setup_libs.sh
ulimit -c 0
inputNumber=$(printf "%03d\n" $((SGE_TASK_ID-1)))
TODAY=2018Jan10

./bin/HTT --cfg=scripts/configsm2016.json --json='{"job":{"filelist":"./filelists/inputFiles/Apr05_MC_80X_GluGluToHToTauTau_M-125_'"${inputNumber}"'"}, "sequence":{"output_folder":"/vols/cms/akd116/MLStudies/tmp","output_name":"'"${TODAY}"'_Apr05_MC_80X_GluGluToHToTauTau_'"${inputNumber}"'"}}' > jobs/${TODAY}_Apr05_MC_80X_GluGluToHToTauTau_${inputNumber}.log
