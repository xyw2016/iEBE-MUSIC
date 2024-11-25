#!/usr/bin/env bash

# download the code package

# # download 3DMCGlauber
# rm -fr 3dMCGlauber_code
# git clone --depth=1 https://github.com/chunshen1987/3dMCGlauber 3dMCGlauber_code
# rm -fr 3dMCGlauber_code/.git

# # download IPGlasma
#rm -fr ipglasma_code
git clone --depth=1  https://github.com/xyw2016/ipglasma.git -b iebe_xyw_dev ipglasma_code
commitHash="8e071daafbe45975ca7330bbc3d2f73b2124fdac"
cd ipglasma_code 
git checkout $commitHash
rm -fr ipglasma_code/.git
cd ..


 # download KoMPoST
rm -fr kompost_code
git clone --depth=1 https://github.com/xyw2016/KoMPoST.git -b xyw_iebe kompost_code
commitHash="bc0355e5bbff7761054e8f8f3711d3e8ec2c321a"
cd  kompost_code 
git checkout $commitHash
rm -fr kompost_code/.git
cd ..

## download MUSIC
rm -fr MUSIC_code
git clone --depth=1  https://github.com/xyw2016/MUSIC.git -b xyw_dev2 MUSIC_code
commitHash="1394eddc9c3265de64ec22c8a28801d18fccb987"
cd  MUSIC_code 
git checkout $commitHash
rm -fr MUSIC_code/.git
cd ..

## download iSS particle sampler
rm -fr iSS_code
git clone --depth=1 https://github.com/chunshen1987/iSS -b v1.1 iSS_code
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
git clone --depth=1 https://github.com/xyw2016/hadronic_afterburner_toolkit.git -b ldu_dev hadronic_afterburner_toolkit_code
commitHash="9137411d27fb8b79f1c8b00de9115bfe3f193057"
cd  hadronic_afterburner_toolkit_code
git checkout $commitHash
rm -fr hadronic_afterburner_toolkit_code/.git
cd ..
