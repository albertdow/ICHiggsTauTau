#!/bin/sh

file_list=("Apr05_MC_80X_VBFHToTauTau_M-125.dat" "Apr05_MC_80X_GluGluToHToTauTau_M-125.dat" "Apr05_MC_80X_DYJetsToLL_M-10to50.dat" "Apr05_MC_80X_TT.dat" "Apr05_MC_80X_WJetsToLNu.dat")

TODAY=`date +%Y%b%d`

for i in "${file_list[@]}" 
do
    echo running "$i"
    ./bin/HTT --cfg=scripts/config2016.json --json='{"job":{"filelist":"./filelists/'"${i}"'"}, "sequence":{"output_name":"'"${TODAY}_${i}"'"}}' &> ${TODAY}_IC_MC_92X_${i}.log &

done

