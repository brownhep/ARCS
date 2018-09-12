setenv VO_CMS_SW_DIR /cvmfs/cms.cern.ch/
source $VO_CMS_SW_DIR/cmsset_default.csh
setenv SCRAM_ARCH slc6_amd64_gcc491

cd /cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/CMSSW_7_4_14/src/
cmsenv
cd -
