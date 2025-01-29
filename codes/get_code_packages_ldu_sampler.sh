#!/usr/bin/env bash

# download the code package

# # download 3DMCGlauber
# rm -fr 3dMCGlauber_code
# git clone --depth=1 https://github.com/chunshen1987/3dMCGlauber 3dMCGlauber_code
# rm -fr 3dMCGlauber_code/.git

# # download IPGlasma
# rm -fr ipglasma_code
# git clone --depth=1 https://github.com/chunshen1987/ipglasma ipglasma_code
# rm -fr ipglasma_code/.git

# # download KoMPoST
# rm -fr kompost_code
# git clone --depth=1 https://github.com/j-f-paquet/kompost kompost_code
# rm -fr kompost_code/.git

# download part2s
rm -fr part2s_code
git clone --depth=1 https://github.com/xyw2016/pre_equlibrium_smash.git part2s_code
rm -fr part2s_code/.git

# download MUSIC
rm -fr MUSIC_code
git clone --depth=1 https://github.com/LipeiDu/MUSIC.git -b du_viscous MUSIC_code
rm -fr MUSIC_code/.git

# download iSS particle sampler
rm -fr iSS_code
git clone --depth=1 https://github.com/LipeiDu/iSS.git iSS_code
rm -fr iSS_code/.git

# download iS3D particle sampler
rm -fr iS3D_code
git clone --depth=1 https://github.com/xyw2016/iS3D2.githttps://github.com/xyw2016/iS3D2.git -b dev_xyw iS3D_code
rm -fr iS3D_code/.git

# download UrQMD afterburner
rm -fr urqmd_code
git clone --depth=1 https://Chunshen1987@bitbucket.org/Chunshen1987/urqmd_afterburner.git urqmd_code
rm -fr urqmd_code/.git

# download hadronic afterner
rm -fr hadronic_afterburner_toolkit_code
git clone --depth=1 https://github.com/LipeiDu/hadronic_afterburner_toolkit -b ldu_dev hadronic_afterburner_toolkit_code
rm -fr hadronic_afterburner_toolkit_code/.git

