#!/usr/bin/env bash

# download the code package

# # download 3DMCGlauber
# rm -fr 3dMCGlauber_code
# git clone --depth=1 https://github.com/chunshen1987/3dMCGlauber 3dMCGlauber_code
# rm -fr 3dMCGlauber_code/.git

# # download IPGlasma
#rm -fr ipglasma_code
#git clone --depth=1  https://github.com/xyw2016/ipglasma.git -b iebe_xyw_dev ipglasma_code
#commitHash="8e071daafbe45975ca7330bbc3d2f73b2124fdac"
#cd ipglasma_code 
#git checkout $commitHash
#cd ..
#rm -fr ipglasma_code/.git
#
#
# # download KoMPoST
#rm -fr kompost_code
#git clone --depth=1 https://github.com/xyw2016/KoMPoST.git -b xyw_iebe kompost_code
#commitHash="bc0355e5bbff7761054e8f8f3711d3e8ec2c321a"
#cd  kompost_code 
#git checkout $commitHash
#cd ..
#rm -fr kompost_code/.git
#
## download part2s
#rm -fr part2s_code
#git clone --depth=1 https://github.com/xyw2016/pre_equlibrium_smash.git part2s_code
#rm -fr part2s_code/.git

## download MUSIC
rm -fr MUSIC_code
git clone --depth=1  https://github.com/xyw2016/MUSIC.git -b polx MUSIC_code
commitHash="af68a5d3f50beff78e117e87afdaaafc5922415a"
cd  MUSIC_code 
git checkout $commitHash
cd ..
rm -fr MUSIC_code/.git
#
### download iSS particle sampler
rm -fr iSS_code
git clone --depth=1 https://github.com/xyw2016/iSS.git -b xyw_dev iSS_code
commitHash="dd02b971f68514e83c7266191c81212df2c627f9"
cd iSS_code 
git checkout $commitHash
cd ..
rm -fr iSS_code/.git

#
## download iS3D particle sampler
#rm -fr iS3D_code
#git clone --depth=1 https://github.com/LipeiDu/iS3D2.git -b ldu_dev iS3D_code
#rm -fr iS3D_code/.git
#
## download UrQMD afterburner
rm -fr urqmd_code
git clone --depth=1 https://Chunshen1987@bitbucket.org/Chunshen1987/urqmd_afterburner.git urqmd_code
rm -fr urqmd_code/.git


#
## download hadronic afterner
rm -fr hadronic_afterburner_toolkit_code
git clone --depth=1 https://github.com/xyw2016/hadronic_afterburner_toolkit.git -b xyw_dev hadronic_afterburner_toolkit_code
commitHash="bffe82fd9cea473e3a8e34c260ab4eeb0097c2d3"
cd  hadronic_afterburner_toolkit_code
git checkout $commitHash
cd ..
rm -fr hadronic_afterburner_toolkit_code/.git
