#! /usr/bin/env python
"""
     This script performs event averaging for particle 
     spectra and anisotropic flow coefficients calculated 
     from event-by-event simulations

     v_n is analyzed up to n = 6

     Format for particle_XXX_vndata.dat file:
     n_order  real_part  real_part_err  imag_part  imag_part_err

     Format for particle_XXX_vndata_diff.dat file:
     pT(GeV)  pT_err(GeV)  dN/(2pi dy pT dpT)(GeV^-2)  dN/(2pi dy pT dpT)_err(GeV^-2)
     vn_real  vn_real_err  vn_imag  vn_imag_err

     All the errors are only statistic errors
"""

from sys import argv, exit
from os import path, mkdir
from glob import glob
from numpy import *
import h5py
import shutil

# define colors
purple = "\033[95m"
green = "\033[92m"
blue = "\033[94m"
yellow = "\033[93m"
red = "\033[91m"
normal = "\033[0m"

Reg_centrality_cut_list = [0., 5., 10., 20., 30., 40., 50.,
                           60., 70., 80., 90., 100.]
PHOBOS_cen_list = [0., 6., 15., 25., 35., 45., 55.]  # PHOBOS AuAu 200
SPS_cen_list    = [5., 12.5, 23.5, 33.5, 43.5]       # SPS PbPb
PHENIX_cen_list = [20., 40., 60., 88.]               # PHENIX dAu
STAR_cen_list   = [0., 10., 40., 80]                 # STAR v1
ALICE_pp_list   = [0., 100., 0., 1., 5.,
                   0., 5., 10., 15, 20., 30., 40., 50., 70., 100.]
centralityCutList = Reg_centrality_cut_list

CentralityFlag = 1   # 0: use pre-generated centrality label in the database
                     # 1: sort dNch/deta and cut centrality
                     # 2: assume uneven number of events in pre-generated
                     #    centrality, remove the bias and cut on dNch/deta
RapidityTrigger = 0  # 0: mid-rapidity [-0.5, 0.5]
                     # 1: PHENIX BBC trigger [-3.9, -3.1]
                     # 2: ALICE V0A trigger [-5.1, -2.8]
                     # 3: ATLAS forward trigger [-4.9, -3.1]
FastFlag = False     # True: only analyze a subset of charged hadron obs.
                     # False: full analysis

RapTrigLabel = "CL1"
if RapidityTrigger == 1:
    RapTrigLabel = "BBC"
elif RapidityTrigger == 2:
    RapTrigLabel = "V0A"
elif RapidityTrigger == 3:
    RapTrigLabel = "ATLASForward"

try:
    data_path = path.abspath(argv[1])
    data_name = data_path.split("/")[-1]
    resultsFolderName = data_name.split(".h5")[0]
    avg_folder_header = path.join(
        path.abspath(argv[2]), "{}_{}".format(resultsFolderName, RapTrigLabel))
    print("output folder: %s" % avg_folder_header)
    if path.isdir(avg_folder_header):
        print("folder %s already exists!" % avg_folder_header)
        var = input("do you want to delete it? [y/N]")
        if 'y' in var.lower():
            shutil.rmtree(avg_folder_header)
            mkdir(avg_folder_header)
        else:
            print("Continue analysis in {} ...".format(avg_folder_header))
    else:
        mkdir(avg_folder_header)
except IndexError:
    print("Usage: {} working_folder results_folder".format(argv[0]))
    exit(1)

#particle_list = ['9999', '211', '321', '2212', '-211', '-321', '-2212', 
#                 '3122', '-3122', '3312', '-3312', '3334', '-3334',
#                 '333']
#particle_name_list = ['charged_hadron', 'pion_p', 'kaon_p', 'proton',
#                      'pion_m', 'kaon_m', 'anti_proton',
#                      'Lambda', 'anti_Lambda', 'Xi_m', 'anti_Xi_p',
#                      'Omega', 'anti_Omega', 'phi']


particle_list = ['9999', '211', '321', '2212', '-211', '-321', '-2212'] 
particle_name_list = ['charged_hadron', 'pion_p', 'kaon_p', 'proton',
                      'pion_m', 'kaon_m', 'anti_proton']

# p cuts for directed flow
p_min_list = [0.01, 0.2, 0.2, 0.4, 0.2, 0.2, 0.4, 0.2, 0.2, 0.15]
p_max_list = [10, 1.6, 1.6, 2, 1.6, 1.6, 2, 5, 5, 10]

nonlinear_reponse_correlator_name_list = [
                'v4_L', 'v4(Psi2)', 'rho_422', 'chi_422',
                'v5_L', 'v5(Psi23)', 'rho_523', 'chi_523',
                'v6_L', 'v6(Psi2)', 'v6(Psi3)',
                'rho_6222', 'rho_633', 'chi_6222', 'chi_633']
symmetric_cumulant_name_list = ['SC_32', 'SC_42']

n_order = 7
if FastFlag:
    particle_list = particle_list[0:1]
    n_order = 5


def calcualte_inte_vn(pT_low, pT_high, data):
    """
        this function calculates the pT-integrated vn in a 
        given pT range (pT_low, pT_high) for every event in the data
    """
    npT = 50
    pT_inte_array = linspace(pT_low, pT_high, npT)
    dpT = pT_inte_array[1] - pT_inte_array[0]
    dN_event = data[:, 2]
    pT_event = data[:, 0]
    dN_interp = exp(interp(pT_inte_array, pT_event, log(dN_event+1e-30)))
    N_event = data[:, -1]
    N_interp = exp(interp(pT_inte_array, pT_event, log(N_event+1e-30)))
    N = sum(N_interp)*dpT/0.1
    temp_vn_array = [N,]
    for iorder in range(1, n_order):
        vn_real_event = data[:, 4*iorder]
        vn_imag_event = data[:, 4*iorder+2]
        vn_real_interp = interp(pT_inte_array, pT_event, vn_real_event)
        vn_imag_interp = interp(pT_inte_array, pT_event, vn_imag_event)
        vn_real_inte = (
            sum(vn_real_interp*dN_interp*pT_inte_array)
            /sum(dN_interp*pT_inte_array))
        vn_imag_inte = (
            sum(vn_imag_interp*dN_interp*pT_inte_array)
            /sum(dN_interp*pT_inte_array))
        vn_inte = vn_real_inte + 1j*vn_imag_inte
        temp_vn_array.append(vn_inte)
    return(temp_vn_array)


def calculate_chi_422(vn_array):
    """chi_422 = Re(v4*conj(v2)**2.)/|v2|^4"""
    dN = real(vn_array[:, 0])
    Q2 = dN*vn_array[:, 2]
    Q4 = dN*vn_array[:, 4]
    nev = len(dN)

    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q2_4 = ((abs(Q2)**4.) - 2.*real(Q4*conj(Q2)*conj(Q2))
             - 4.*(dN - 2.)*(abs(Q2)**2.) + abs(Q4)**2.
             + 2*dN*(dN - 3.))

    N3_weight = dN*(dN - 1.)*(dN - 2.)
    chi_422_num = Q4*conj(Q2)*conj(Q2) - 2.*Q2*conj(Q2) - Q4*conj(Q4) + 2.*dN

    chi_422_JK = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        chi_422_JK[iev] = (
            real(mean(chi_422_num[array_idx]))/mean(N3_weight[array_idx])
            /(real(mean(Q2_4[array_idx]))/mean(N4_weight[array_idx])))

    chi_422_mean = mean(chi_422_JK)
    chi_422_err = sqrt((nev - 1.)/nev*sum((chi_422_JK - chi_422_mean)**2.))
    return(chi_422_mean, chi_422_err)


def calculate_chi_523(vn_array):
    """chi_523 = Re(v5*conj(v2*v3))/|v2|^2/|v3|^2"""
    dN = real(vn_array[:, 0])
    Q1 = dN*vn_array[:, 1]
    Q2 = dN*vn_array[:, 2]
    Q3 = dN*vn_array[:, 3]
    Q5 = dN*vn_array[:, 5]
    nev = len(dN)

    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q_32 = ((abs(Q2)**2.)*(abs(Q3)**2.) - 2.*real(Q5*conj(Q2)*conj(Q3))
        - 2.*real(Q3*conj(Q1)*conj(Q2)) + abs(Q5)**2. + abs(Q1)**2.
        - (dN - 4.)*(abs(Q2)**2. + abs(Q3)**2.) + dN*(dN - 6.)
    )

    N3_weight = dN*(dN - 1.)*(dN - 2.)
    chi_523_num = (Q5*conj(Q2)*conj(Q3) - Q3*conj(Q3) - Q2*conj(Q2)
                   - Q5*conj(Q5) + 2.*dN)

    chi_523_JK = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        chi_523_JK[iev] = (
            real(mean(chi_523_num[array_idx]))/mean(N3_weight[array_idx])
            /(real(mean(Q_32[array_idx]))/mean(N4_weight[array_idx])))

    chi_523_mean = mean(chi_523_JK)
    chi_523_err = sqrt((nev - 1.)/nev*sum((chi_523_JK - chi_523_mean)**2.))
    return(chi_523_mean, chi_523_err)


def calculate_chi_6222(vn_array):
    """chi_6222 = Re(v6*conj(v2)**3.)/|v2|^6"""
    dN = real(vn_array[:, 0])
    Q2 = dN*vn_array[:, 2]
    Q4 = dN*vn_array[:, 4]
    Q6 = dN*vn_array[:, 6]
    nev = len(dN)

    N6_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)*(dN - 4.)*(dN - 5.)
    Q2_6 = (abs(Q2)**6. + 9*(abs(Q4)**2.)*(abs(Q2)**2.)
            - 6.*real(Q4*Q2*conj(Q2)*conj(Q2)*conj(Q2))
            + 4.*real(Q6*conj(Q2)*conj(Q2)*conj(Q2))
            - 12.*real(Q6*conj(Q4)*conj(Q2))
            + 18.*(dN - 4.)*real(Q4*conj(Q2)*conj(Q2))
            + 4.*(abs(Q6)**2.)
            - 9.*(dN - 4.)*((abs(Q2)**4.) + (abs(Q4)**2.))
            + 18.*(dN - 5.)*(dN - 2.)*(abs(Q2)**2.)
            - 6.*dN*(dN - 4.)*(dN - 5.))

    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    chi_6222_num = (Q6*conj(Q2)*conj(Q2)*conj(Q2) - 3.*Q6*conj(Q4)*conj(Q2)
                    - 3.*Q4*conj(Q2)*conj(Q2) + 2.*Q6*conj(Q6) + 6.*Q2*conj(Q2)
                    + 3.*Q4*conj(Q4) - 6.*dN)

    chi_6222_JK = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        chi_6222_JK[iev] = (
            real(mean(chi_6222_num[array_idx]))/mean(N4_weight[array_idx])
            /(real(mean(Q2_6[array_idx]))/mean(N6_weight[array_idx])))

    chi_6222_mean = mean(chi_6222_JK)
    chi_6222_err = sqrt((nev - 1.)/nev*sum((chi_6222_JK - chi_6222_mean)**2.))
    return(chi_6222_mean, chi_6222_err)


def calculate_chi_633(vn_array):
    """chi_633 = Re(v6*conj(v3)**2.)/|v3|^4"""
    dN = real(vn_array[:, 0])
    Q3 = dN*vn_array[:, 3]
    Q6 = dN*vn_array[:, 6]
    nev = len(dN)

    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q3_4 = ((abs(Q3)**4.) - 2.*real(Q6*conj(Q3)*conj(Q3))
             - 4.*(dN - 2.)*(abs(Q3)**2.) + abs(Q6)**2.
             + 2*dN*(dN - 3.))

    N3_weight = dN*(dN - 1.)*(dN - 2.)
    chi_633_num = Q6*conj(Q3)*conj(Q3) - 2.*Q3*conj(Q3) - Q6*conj(Q6) + 2.*dN

    chi_633_JK = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        chi_633_JK[iev] = (
            real(mean(chi_633_num[array_idx]))/mean(N3_weight[array_idx])
            /(real(mean(Q3_4[array_idx]))/mean(N4_weight[array_idx])))

    chi_633_mean = mean(chi_633_JK)
    chi_633_err = sqrt((nev - 1.)/nev*sum((chi_633_JK - chi_633_mean)**2.))
    return(chi_633_mean, chi_633_err)


def calculate_v4_Psi2(chi_422, chi_422_err, vn_array):
    """v4(Psi2) = chi_422*sqrt(<abs(V2)**4>)"""
    dN = real(vn_array[:, 0])
    Q2 = dN*vn_array[:, 2]
    Q4 = dN*vn_array[:, 4]
    nev = len(dN)

    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q2_4 = ((abs(Q2)**4.) - 2.*real(Q4*conj(Q2)*conj(Q2))
             - 4.*(dN - 2.)*(abs(Q2)**2.) + abs(Q4)**2.
             + 2*dN*(dN - 3.))

    v2_factor = sqrt(mean(Q2_4)/mean(N4_weight))
    v2_factor_err = std(Q2_4)/mean(N4_weight)/(2.*v2_factor)/sqrt(nev)

    v4_Psi2 = chi_422*v2_factor
    v4_Psi2_err = sqrt((chi_422_err*v2_factor)**2.
                       + (chi_422*v2_factor_err)**2.)
    return(v4_Psi2, v4_Psi2_err)


def calculate_v5_Psi23(chi_523, chi_523_err, vn_array):
    """v5(Psi23) = chi_523*sqrt(<abs(V2)**2*abs(V3)**2>)"""
    dN = real(vn_array[:, 0])
    Q1 = dN*vn_array[:, 1]
    Q2 = dN*vn_array[:, 2]
    Q3 = dN*vn_array[:, 3]
    Q5 = dN*vn_array[:, 5]
    nev = len(dN)

    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q_32 = ((abs(Q2)**2.)*(abs(Q3)**2.) - 2.*real(Q5*conj(Q2)*conj(Q3))
        - 2.*real(Q3*conj(Q1)*conj(Q2)) + abs(Q5)**2. + abs(Q1)**2.
        - (dN - 4.)*(abs(Q2)**2. + abs(Q3)**2.) + dN*(dN - 6.)
    )

    v23_factor = sqrt(mean(Q_32)/mean(N4_weight))
    v23_factor_err = std(Q_32)/mean(N4_weight)/(2.*v23_factor)/sqrt(nev)

    v5_Psi23 = chi_523*v23_factor
    v5_Psi23_err = sqrt((chi_523_err*v23_factor)**2.
                        + (chi_523*v23_factor_err)**2.)
    return(v5_Psi23, v5_Psi23_err)


def calculate_v6_Psi2(chi_6222, chi_6222_err, vn_array):
    """v6(Psi2) = chi_6222*sqrt(<abs(V2)**6>)"""
    dN = real(vn_array[:, 0])
    Q2 = dN*vn_array[:, 2]
    Q4 = dN*vn_array[:, 4]
    Q6 = dN*vn_array[:, 6]
    nev = len(dN)

    N6_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)*(dN - 4.)*(dN - 5.)
    Q2_6 = (abs(Q2)**6. + 9*(abs(Q4)**2.)*(abs(Q2)**2.)
            - 6.*real(Q4*Q2*conj(Q2)*conj(Q2)*conj(Q2))
            + 4.*real(Q6*conj(Q2)*conj(Q2)*conj(Q2))
            - 12.*real(Q6*conj(Q4)*conj(Q2))
            + 18.*(dN - 4.)*real(Q4*conj(Q2)*conj(Q2))
            + 4.*(abs(Q6)**2.)
            - 9.*(dN - 4.)*((abs(Q2)**4.) + (abs(Q4)**2.))
            + 18.*(dN - 5.)*(dN - 2.)*(abs(Q2)**2.)
            - 6.*dN*(dN - 4.)*(dN - 5.))

    v2_factor = sqrt(mean(Q2_6)/mean(N6_weight))
    v2_factor_err = std(Q2_6)/mean(N6_weight)/(2.*v2_factor)/sqrt(nev)

    v6_Psi2 = chi_6222*v2_factor
    v6_Psi2_err = sqrt((chi_6222_err*v2_factor)**2.
                        + (chi_6222*v2_factor_err)**2.)
    return(v6_Psi2, v6_Psi2_err)


def calculate_v6_Psi3(chi_633, chi_633_err, vn_array):
    """v6(Psi3) = chi_633*sqrt(<abs(V3)**4>)"""
    dN = real(vn_array[:, 0])
    Q3 = dN*vn_array[:, 3]
    Q6 = dN*vn_array[:, 6]
    nev = len(dN)

    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q3_4 = ((abs(Q3)**4.) - 2.*real(Q6*conj(Q3)*conj(Q3))
             - 4.*(dN - 2.)*(abs(Q3)**2.) + abs(Q6)**2.
             + 2*dN*(dN - 3.))

    v3_factor = sqrt(mean(Q3_4)/mean(N4_weight))
    v3_factor_err = std(Q3_4)/mean(N4_weight)/(2.*v3_factor)/sqrt(nev)

    v6_Psi3 = chi_633*v3_factor
    v6_Psi3_err = sqrt((chi_633_err*v3_factor)**2.
                        + (chi_633*v3_factor_err)**2.)
    return(v6_Psi3, v6_Psi3_err)


def calculate_rho_422(v4_Psi2, v4_Psi2_err, vn_array):
    """rho_422 = v4(Psi2)/v4(Psi4)"""
    dN = real(vn_array[:, 0])
    Q4 = dN*vn_array[:, 4]
    nev = len(dN)

    N2_weight = dN*(dN - 1.)
    Q4_2 = abs(Q4)**2. - dN

    v4_Psi4 = sqrt(mean(Q4_2)/mean(N2_weight))
    v4_Psi4_err = std(Q4_2)/mean(N2_weight)/(2.*v4_Psi4)/sqrt(nev)

    rho_422 = v4_Psi2/v4_Psi4
    rho_422_err = sqrt((v4_Psi2_err/v4_Psi4)**2.
                       + (v4_Psi2*v4_Psi4_err/v4_Psi4**2.)**2.)
    return(rho_422, rho_422_err)


def calculate_rho_523(v5_Psi23, v5_Psi23_err, vn_array):
    """rho_523 = v5(Psi23)/v5(Psi5)"""
    dN = real(vn_array[:, 0])
    Q5 = dN*vn_array[:, 5]
    nev = len(dN)

    N2_weight = dN*(dN - 1.)
    Q5_2 = abs(Q5)**2. - dN

    v5_Psi5 = sqrt(mean(Q5_2)/mean(N2_weight))
    v5_Psi5_err = std(Q5_2)/mean(N2_weight)/(2.*v5_Psi5)/sqrt(nev)

    rho_523 = v5_Psi23/v5_Psi5
    rho_523_err = sqrt((v5_Psi23_err/v5_Psi5)**2.
                       + (v5_Psi23*v5_Psi5_err/v5_Psi5**2.)**2.)
    return(rho_523, rho_523_err)


def calculate_rho_6222(v6_Psi2, v6_Psi2_err, vn_array):
    """rho_6222 = v6(Psi2)/v6(Psi6)"""
    dN = real(vn_array[:, 0])
    Q6 = dN*vn_array[:, 6]
    nev = len(dN)

    N2_weight = dN*(dN - 1.)
    Q6_2 = abs(Q6)**2. - dN

    v6_Psi6 = nan_to_num(sqrt(mean(Q6_2)/mean(N2_weight)))
    v6_Psi6_err = nan_to_num(std(Q6_2)/mean(N2_weight)/(2.*v6_Psi6)/sqrt(nev))

    rho_6222 = v6_Psi2/v6_Psi6
    rho_6222_err = sqrt((v6_Psi2_err/v6_Psi6)**2.
                        + (v6_Psi2*v6_Psi6_err/v6_Psi6**2.)**2.)
    return(rho_6222, rho_6222_err)


def calculate_rho_633(v6_Psi3, v6_Psi3_err, vn_array):
    """rho_633 = v6(Psi3)/v6(Psi6)"""
    dN = real(vn_array[:, 0])
    Q6 = dN*vn_array[:, 6]
    nev = len(dN)

    N2_weight = dN*(dN - 1.)
    Q6_2 = abs(Q6)**2. - dN

    v6_Psi6 = nan_to_num(sqrt(mean(Q6_2)/mean(N2_weight)))
    v6_Psi6_err = nan_to_num(std(Q6_2)/mean(N2_weight)/(2.*v6_Psi6)/sqrt(nev))

    rho_633 = v6_Psi3/v6_Psi6
    rho_633_err = sqrt((v6_Psi3_err/v6_Psi6)**2.
                        + (v6_Psi3*v6_Psi6_err/v6_Psi6**2.)**2.)
    return(rho_633, rho_633_err)


def calculate_v4_L(v4_Psi2, v4_Psi2_err, vn_array):
    """v4_L = sqrt(v4(Psi4)^2 - v4(Psi2)^2)"""
    dN = real(vn_array[:, 0])
    Q4 = dN*vn_array[:, 4]
    nev = len(dN)

    N2_weight = dN*(dN - 1.)
    Q4_2 = abs(Q4)**2. - dN

    v4_Psi4_sq = mean(Q4_2)/mean(N2_weight)
    v4_Psi4_sq_err = std(Q4_2)/mean(N2_weight)/sqrt(nev)

    v4_L = sqrt(v4_Psi4_sq - v4_Psi2**2.)
    v4_L_err = (sqrt(v4_Psi4_sq_err**2. + (2.*v4_Psi2*v4_Psi2_err)**2.)
                /(2.*v4_L))
    return(v4_L, v4_L_err)


def calculate_v5_L(v5_Psi23, v5_Psi23_err, vn_array):
    """v5_L = sqrt(v5(Psi5)^2 - v5(Psi23)^2)"""
    dN = real(vn_array[:, 0])
    Q5 = dN*vn_array[:, 5]
    nev = len(dN)

    N2_weight = dN*(dN - 1.)
    Q5_2 = abs(Q5)**2. - dN

    v5_Psi5_sq = mean(Q5_2)/mean(N2_weight)
    v5_Psi5_sq_err = std(Q5_2)/mean(N2_weight)/sqrt(nev)

    v5_L = sqrt(v5_Psi5_sq - v5_Psi23**2.)
    v5_L_err = (sqrt(v5_Psi5_sq_err**2. + (2.*v5_Psi23*v5_Psi23_err)**2.)
                /(2.*v5_L))
    return(v5_L, v5_L_err)


def calculate_v6_L(chi_6222, chi_6222_err, chi_633, chi_633_err, vn_array):
    """
        v6_L = sqrt(v6(Psi6)^2 - chi_6222^2 v2^6
                    - chi_633^2 v3^4 - 2 Re(chi_6222*chi_633*v2^3 v3^{2*}))
    """
    dN = real(vn_array[:, 0])
    v2_array = vn_array[:, 2]
    v3_array = vn_array[:, 3]
    v6_array = vn_array[:, 6]
    nev = len(dN)

    v6_Psi6_sq = mean(abs(v6_array)**2.)
    v6_Psi6_sq_err = std(abs(v6_array)**2.)/sqrt(nev)
    v2_6 = mean(abs(v2_array)**6.)
    v2_6_err = std(abs(v2_array)**6.)/sqrt(nev)
    v3_4 = mean(abs(v3_array)**4.)
    v3_4_err = std(abs(v3_array)**4.)/sqrt(nev)
    v23 = real(mean(v2_array**3.*conj(v3_array)**2.))
    v23_err = real(std(v2_array**3.*conj(v3_array)**2.))/sqrt(nev)
    v6_L = (v6_Psi6_sq - chi_6222**2.*v2_6 - chi_633**2.*v3_4
            - 2.*chi_6222*chi_633*v23)
    v6_L_err = sqrt(
            v6_Psi6_sq_err**2.
            + (2.*chi_6222*chi_6222_err*v2_6)**2. + (chi_6222**2.*v2_6_err)**2.
            + (2.*chi_633*chi_633_err*v3_4)**2. + (chi_633**2.*v3_4_err)**2.
            + (2.*chi_6222_err*chi_633*v23)**2.
            + (2.*chi_6222*chi_633_err*v23)**2.
            + (2.*chi_6222*chi_633*v23_err)**2.)
    return(v6_L, v6_L_err)


def calculate_nonlinear_reponse(vn_array, outputFileName):
    """
        this function computes all the nonlinear response coefficients
        proposed in the paper arXiv: 1502.02502 up to v6
    """
    chi_422, chi_422_err = calculate_chi_422(vn_array)
    v4_Psi2, v4_Psi2_err = calculate_v4_Psi2(chi_422, chi_422_err, vn_array)
    rho_422, rho_422_err = calculate_rho_422(v4_Psi2, v4_Psi2_err, vn_array)
    v4_L, v4_L_err = calculate_v4_L(v4_Psi2, v4_Psi2_err, vn_array)

    chi_523, chi_523_err = calculate_chi_523(vn_array)
    v5_Psi23, v5_Psi23_err = calculate_v5_Psi23(chi_523, chi_523_err, vn_array)
    rho_523, rho_523_err = calculate_rho_523(v5_Psi23, v5_Psi23_err, vn_array)
    v5_L, v5_L_err = calculate_v5_L(v5_Psi23, v5_Psi23_err, vn_array)

    chi_6222, chi_6222_err = calculate_chi_6222(vn_array)
    v6_Psi2, v6_Psi2_err = calculate_v6_Psi2(chi_6222, chi_6222_err, vn_array)
    rho_6222, rho_6222_err = calculate_rho_6222(v6_Psi2, v6_Psi2_err, vn_array)

    chi_633, chi_633_err = calculate_chi_633(vn_array)
    v6_Psi3, v6_Psi3_err = calculate_v6_Psi3(chi_633, chi_633_err, vn_array)
    rho_633, rho_633_err = calculate_rho_633(v6_Psi3, v6_Psi3_err, vn_array)
    v6_L, v6_L_err = calculate_v6_L(chi_6222, chi_6222_err,
                                    chi_633, chi_633_err, vn_array)

    results = [v4_L, v4_L_err, v4_Psi2, v4_Psi2_err, rho_422, rho_422_err,
               chi_422, chi_422_err,
               v5_L, v5_L_err, v5_Psi23, v5_Psi23_err, rho_523, rho_523_err,
               chi_523, chi_523_err,
               v6_L, v6_L_err, v6_Psi2, v6_Psi2_err, v6_Psi3, v6_Psi3_err,
               rho_6222, rho_6222_err, rho_633, rho_633_err,
               chi_6222, chi_6222_err, chi_633, chi_633_err]
    f = open(outputFileName, 'w')
    f.write("# type  value  stat. err\n")
    for i in range(len(nonlinear_reponse_correlator_name_list)):
        f.write("%s  %.10e  %.10e\n"
                % (nonlinear_reponse_correlator_name_list[i],
                   results[2*i], results[2*i+1]))
    f.close()
    return


def calcualte_vn_2(vn_data_array):
    """
        this function computes vn{2} and its stat. err.
        self correlation is substracted
    """
    vn_data_array = array(vn_data_array)
    nev = len(vn_data_array[:, 0])
    dN = real(vn_data_array[:, 0])
    dN = dN.reshape(len(dN), 1)
    Qn_array = dN*vn_data_array[:, 1:]
    corr = 1./(dN*(dN - 1.))*(Qn_array*conj(Qn_array) - dN)
    vn_2 = sqrt(real(mean(corr, 0))) + 1e-30
    vn_2_err = std(real(corr), 0)/sqrt(nev)/2./vn_2
    return(nan_to_num(vn_2), nan_to_num(vn_2_err))


def calcualte_vn_2_with_gap(vn_data_array_sub1, vn_data_array_sub2):
    """
        this function computes vn{2} and its stat. err.
        using two subevents with a eta gap
    """
    vn_data_array_sub1 = array(vn_data_array_sub1)
    vn_data_array_sub2 = array(vn_data_array_sub2)
    nev = len(vn_data_array_sub1[:, 0])
    dN1 = real(vn_data_array_sub1[:, 0])
    dN1 = dN1.reshape(len(dN1), 1)
    dN2 = real(vn_data_array_sub2[:, 0])
    dN2 = dN1.reshape(len(dN2), 1)
    Qn_array1 = dN1*vn_data_array_sub1[:, 1:]
    Qn_array2 = dN2*vn_data_array_sub2[:, 1:]

    corr = (Qn_array1*conj(Qn_array2))/(dN1*dN2)
    vn_2 = sqrt(real(mean(corr, 0))) + 1e-30
    vn_2_err = std(real(corr), 0)/sqrt(nev)/2./vn_2
    return(nan_to_num(vn_2), nan_to_num(vn_2_err))


def get_vn_diff_2PC_from_single_event(data):
    """This function computes the 2PC vn for a single event"""
    dN_event = data[:, -1]
    temp_vn_real_array = []
    temp_vn_imag_array = []
    temp_vn_denorm_array = []
    for iorder in range(1, n_order):
        vn_real_event = data[:, 4*iorder]
        vn_imag_event = data[:, 4*iorder+2]
        vn_pt = vn_real_event + 1j*vn_imag_event
        numerator_real = real(dN_event*vn_pt)
        numerator_imag = imag(dN_event*vn_pt)
        denorm = dN_event
        temp_vn_real_array.append(numerator_real)
        temp_vn_imag_array.append(numerator_imag)
    temp_vn_denorm_array.append(denorm)
    return(temp_vn_real_array, temp_vn_imag_array, temp_vn_denorm_array)


def calculate_diff_vn_single_event(pT_ref_low, pT_ref_high, data, data_ref):
    """
        This function computes pT differential vn{4} for a single event
        It returns [Qn_pT_arr, Qn_ref_arr]
    """
    npT = 50
    pT_inte_array = linspace(pT_ref_low, pT_ref_high, npT)
    dpT = pT_inte_array[1] - pT_inte_array[0]
    dN_event = data[:, -1]
    dN_ref_event = data_ref[:, -1]
    pT_ref_event = data_ref[:, 0]
    dN_ref_interp = exp(interp(pT_inte_array, pT_ref_event,
                               log(dN_ref_event + 1e-30)))
    dN_ref = sum(dN_ref_interp)*dpT/0.1
    temp_Qn_pT_array = [dN_event,]
    temp_Qn_ref_array = [dN_ref]
    for iorder in range(1, n_order):
        vn_real_event = data[:, 4*iorder]
        vn_imag_event = data[:, 4*iorder+2]
        vn_ref_real_event = data_ref[:, 4*iorder]
        vn_ref_imag_event = data_ref[:, 4*iorder+2]
        vn_ref_real_interp = interp(pT_inte_array, pT_ref_event,
                                    vn_ref_real_event)
        vn_ref_imag_interp = interp(pT_inte_array, pT_ref_event,
                                    vn_ref_imag_event)
        vn_ref_real_inte = (
            sum(vn_ref_real_interp*dN_ref_interp)/sum(dN_ref_interp))
        vn_ref_imag_inte = (
            sum(vn_ref_imag_interp*dN_ref_interp)/sum(dN_ref_interp))
        Qn_ref = dN_ref*(vn_ref_real_inte + 1j*vn_ref_imag_inte)
        Qn_pt = dN_event*(vn_real_event + 1j*vn_imag_event)
        temp_Qn_pT_array.append(Qn_pt)
        temp_Qn_ref_array.append(Qn_ref)
    return(temp_Qn_pT_array, temp_Qn_ref_array)


def calculate_vn_diff_SP(QnpT_diff, Qnref):
    """
        this funciton calculates the scalar-product vn
        assumption: no overlap between particles of interest
                    and reference flow Qn vectors
        inputs: QnpT_diff[nev, norder, npT], Qnref[nev, norder]
        return: [vn{SP}(pT), vn{SP}(pT)_err]
    """
    QnpT_diff = array(QnpT_diff)
    Qnref = array(Qnref)
    nev, norder, npT = QnpT_diff.shape

    vn_diff_SP = []
    Nref = real(Qnref[:, 0])
    N2refPairs = Nref*(Nref - 1.)
    NpTPOI = real(QnpT_diff[:, 0, :])
    N2POIPairs = NpTPOI*Nref.reshape(nev, 1)
    for iorder in range(1, norder):
        # compute Cn^ref{2}
        QnRef_tmp = Qnref[:, iorder]
        n2ref = abs(QnRef_tmp)**2. - Nref

        # compute vn{SP}(pT)
        QnpT_tmp = QnpT_diff[:, iorder, :]
        n2pT = real(QnpT_tmp*conj(QnRef_tmp.reshape(nev, 1)))

        # calcualte observables with Jackknife resampling method
        vnSPpT_arr = zeros([nev, npT])
        for iev in range(nev):
            array_idx = [True]*nev
            array_idx[iev] = False
            array_idx = array(array_idx)

            Cn2ref_arr = mean(n2ref[array_idx])/mean(N2refPairs[array_idx])
            vnSPpT_arr[iev, :] = (mean(n2pT[array_idx], 0)
                    /mean(N2POIPairs[array_idx], 0)/sqrt(Cn2ref_arr))
        vnSPpT_mean = mean(vnSPpT_arr, 0)
        vnSPpT_err  = sqrt((nev - 1.)/nev
                           *sum((vnSPpT_arr - vnSPpT_mean)**2., 0))
        vn_diff_SP.append(vnSPpT_mean)
        vn_diff_SP.append(vnSPpT_err)
    return vn_diff_SP


def calculate_vn_diff_2PC(vn_diff_real, vn_diff_imag, vn_diff_denorm):
    """this funciton calculates the rms vn[2](pT)"""
    vn_diff_real = array(vn_diff_real)
    vn_diff_imag = array(vn_diff_imag)
    vn_diff_denorm = array(vn_diff_denorm)
    nev = len(vn_diff_denorm[:, 0])
    vn_diff_2PC = sqrt(
        mean((vn_diff_real**2. + vn_diff_imag**2. - vn_diff_denorm)
             /(vn_diff_denorm**2. - vn_diff_denorm + 1e-15), 0))
    vn_diff_2PC_err = (
        std((vn_diff_real**2. + vn_diff_imag**2. - vn_diff_denorm)
            /(vn_diff_denorm**2. - vn_diff_denorm + 1e-15), 0)
        /sqrt(nev)/(2.*vn_diff_2PC + 1e-15))
    return(nan_to_num(vn_diff_2PC), nan_to_num(vn_diff_2PC_err))


def calculate_vn4_diff(QnpT_diff, Qnref):
    """
        this funciton calculates the 4-particle vn(pT)
        assumption: no overlap between particles of interest
                    and reference flow Qn vectors
        inputs: QnpT_diff[nev, norder, npT], Qnref[nev, norder]
        return: [v1{4}pT, v1{4}pT_err, v2{4}pT, v2{4}pT_err,
                 v3{4}pT, v3{4}pT_err]
    """
    QnpT_diff = array(QnpT_diff)
    Qnref = array(Qnref)
    nev, norder, npT = QnpT_diff.shape

    vn4pT_arr = []
    for iorder in range(1, 4):
        # compute Cn^ref{4}
        Nref = real(Qnref[:, 0])
        QnRef_tmp = Qnref[:, iorder]
        Q2nRef_tmp = Qnref[:, 2*iorder]
        N4refPairs = Nref*(Nref - 1.)*(Nref - 2.)*(Nref - 3.)
        n4ref = (abs(QnRef_tmp)**4.
                 - 2.*real(Q2nRef_tmp*conj(QnRef_tmp)*conj(QnRef_tmp))
                 - 4.*(Nref - 2)*abs(QnRef_tmp)**2. + abs(Q2nRef_tmp)**2.
                 + 2.*Nref*(Nref - 3))
        N2refPairs = Nref*(Nref - 1.)
        n2ref = abs(QnRef_tmp)**2. - Nref

        # compute dn{4}(pT)
        NpTPOI = real(QnpT_diff[:, 0, :])
        QnpT_tmp = QnpT_diff[:, iorder, :]
        Nref = Nref.reshape(len(Nref), 1)
        QnRef_tmp = QnRef_tmp.reshape(len(QnRef_tmp), 1)
        Q2nRef_tmp = Q2nRef_tmp.reshape(len(Q2nRef_tmp), 1)
        N4POIPairs = NpTPOI*(Nref - 1.)*(Nref - 2.)*(Nref - 3.) + 1e-30
        n4pT = real(QnpT_tmp*QnRef_tmp*conj(QnRef_tmp)*conj(QnRef_tmp)
                    - 2.*(Nref - 1)*QnpT_tmp*conj(QnRef_tmp)
                    - QnpT_tmp*QnRef_tmp*conj(Q2nRef_tmp))
        N2POIPairs = NpTPOI*Nref + 1e-30
        n2pT = real(QnpT_tmp*conj(QnRef_tmp))

        # calcualte observables with Jackknife resampling method
        Cn2ref_arr = zeros(nev)
        Cn4ref_arr = zeros(nev)
        dn4pT_arr = zeros(npT)
        vn4pT4_arr = zeros([nev, npT])
        for iev in range(nev):
            array_idx = [True]*nev
            array_idx[iev] = False
            array_idx = array(array_idx)

            Cn2ref_arr[iev] = (
                    mean(n2ref[array_idx])/mean(N2refPairs[array_idx]))
            Cn4ref_arr[iev] = (
                mean(n4ref[array_idx])/mean(N4refPairs[array_idx])
                - 2.*(Cn2ref_arr[iev])**2.)

            dn4pT_arr = (
                mean(n4pT[array_idx, :], 0)/mean(N4POIPairs[array_idx, :], 0)
                - 2.*mean(n2pT[array_idx, :], 0)
                    /mean(N2POIPairs[array_idx, :], 0)
                    *Cn2ref_arr[iev]
            )

            vn4pT4_arr[iev, :] = (-dn4pT_arr)**4./((-Cn4ref_arr[iev])**3.)

        vn4pT4_mean = mean(vn4pT4_arr, axis=0)
        vn4pT4_err  = sqrt((nev - 1.)/nev
                            *sum((vn4pT4_arr - vn4pT4_mean)**2., axis=0))

        vn4pT     = zeros(npT)
        vn4pT_err = zeros(npT)
        idx = vn4pT4_mean > 0
        vn4pT[idx] = vn4pT4_mean[idx]**(0.25)
        vn4pT_err[idx] = vn4pT4_err[idx]/(4.*vn4pT4_mean[idx]**(0.75))
        vn4pT_arr.append(vn4pT)
        vn4pT_arr.append(vn4pT_err)
    return(vn4pT_arr)



def calculate_vn_distribution(vn_array, outputFileName):
    """This function computes the vn distribution"""
    nbin = 20
    vn_array = array(vn_array)
    vn_dim = len(vn_array[0, :])
    output = []
    for vn_order in range(vn_dim):
        vn_mag_array = abs(vn_array[:, vn_order])
        vn_min = min(vn_mag_array)
        vn_max = max(vn_mag_array)*1.0001
        bin_boundaries = linspace(vn_min, vn_max, nbin+1)
        bin_width = bin_boundaries[1] - bin_boundaries[0]
        bin_center = zeros([nbin])
        bin_value = zeros([nbin])
        for vn_elem in vn_mag_array:
            vn_idx = int(floor((vn_elem - vn_min)/bin_width))
            if (vn_idx == 20):
                print(vn_elem, vn_min, bin_width)
            bin_value[vn_idx] += 1.
            bin_center[vn_idx] += vn_elem
        bin_center = bin_center/(bin_value + 1e-15)
        bin_value = bin_value/len(vn_array)
        bin_value_err = sqrt(bin_value/len(vn_array))
        bin_value = bin_value/bin_width
        bin_value_err = bin_value_err/bin_width
        for i in range(nbin):
            if abs(bin_center[i]) < 1e-15:
                bin_center[i] = (bin_boundaries[i] + bin_boundaries[i+1])/2.
        output.append(bin_center)
        output.append(bin_value)
        output.append(bin_value_err)
    output = array(output).transpose()

    f = open(outputFileName, 'w')
    f.write("#vn  dP(vn)/dvn  dP(vn)/dvn_err\n")
    for ipT in range(len(output[:, 0])):
        for iorder in range(1, n_order):
            f.write("%.10e  %.10e  %.10e  "
                    % (output[ipT, 3*(iorder-1)], 
                       output[ipT, 3*(iorder-1)+1],
                       output[ipT, 3*(iorder-1)+2]))
        f.write("\n")
    f.close()
    return


def calcualte_event_plane_correlations_3sub(vn_array, vn_array_sub1,
                                            vn_array_sub2, outputFileName):
    """
        this function compute the three-particle correlations with Qn
        vectors from three different sub-events
    """
    vn_array = array(vn_array)
    vn_array_sub1 = array(vn_array_sub1)
    vn_array_sub2 = array(vn_array_sub2)
    nev = len(vn_array[:, 0])

    dN = real(vn_array[:, 0].reshape(nev, 1))
    dN_sub1 = real(vn_array_sub1[:, 0].reshape(nev, 1))
    dN_sub2 = real(vn_array_sub2[:, 0].reshape(nev, 1))
    Qn_array = dN*vn_array
    Qn_array_sub1 = dN_sub1*vn_array_sub1
    Qn_array_sub2 = dN_sub2*vn_array_sub2

    corr_224_JK = zeros(nev)
    corr_336_JK = zeros(nev)
    corr_235_JK = zeros(nev)
    corr_246_JK = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        v2_2 = (mean(real(Qn_array_sub1[array_idx, 2]
                          *conj(Qn_array_sub2[array_idx, 2])))
                /mean(dN_sub1[array_idx]*dN_sub2[array_idx]))
        v3_2 = (mean(real(Qn_array_sub1[array_idx, 3]
                          *conj(Qn_array_sub2[array_idx, 3])))
                /mean(dN_sub1[array_idx]*dN_sub2[array_idx]))
        v4_2 = (mean(real(Qn_array_sub1[array_idx, 4]
                          *conj(Qn_array_sub2[array_idx, 4])))
                /mean(dN_sub1[array_idx]*dN_sub2[array_idx]))
        v5_2 = (mean(real(Qn_array_sub1[array_idx, 5]
                          *conj(Qn_array_sub2[array_idx, 5])))
                /mean(dN_sub1[array_idx]*dN_sub2[array_idx]))
        v6_2 = (mean(real(Qn_array_sub1[array_idx, 6]
                          *conj(Qn_array_sub2[array_idx, 6])))
                /mean(dN_sub1[array_idx]*dN_sub2[array_idx]))

        # cos(4(Psi_2 - Psi_4))
        corr_224_num = (
            mean(real(  Qn_array[array_idx, 2]*Qn_array_sub1[array_idx, 2]
                        *conj(Qn_array_sub2[array_idx, 4])
                      + Qn_array[array_idx, 2]*Qn_array_sub2[array_idx, 2]
                        *conj(Qn_array_sub1[array_idx, 4])
                      + Qn_array_sub2[array_idx, 2]*Qn_array_sub1[array_idx, 2]
                        *conj(Qn_array[array_idx, 4])))
            /mean(3.*dN[array_idx]*dN_sub1[array_idx]*dN_sub2[array_idx])
        )
        corr_224_JK[iev] = corr_224_num/sqrt(v2_2*v2_2*v4_2)

        # cos(6(Psi_3 - Psi_6))
        corr_336_num = (
            mean(real(  Qn_array[array_idx, 3]*Qn_array_sub1[array_idx, 3]
                        *conj(Qn_array_sub2[array_idx, 6])
                      + Qn_array[array_idx, 3]*Qn_array_sub2[array_idx, 3]
                        *conj(Qn_array_sub1[array_idx, 6])
                      + Qn_array_sub2[array_idx, 3]*Qn_array_sub1[array_idx, 3]
                        *conj(Qn_array[array_idx, 6])))
            /mean(3.*dN[array_idx]*dN_sub1[array_idx]*dN_sub2[array_idx])
        )
        corr_336_JK[iev] = corr_336_num/sqrt((v3_2**2.)*v6_2)

        # cos(2Psi_2 + 3Psi_3 - 5Psi_5)
        corr_235_num = (
            mean(real(  Qn_array[array_idx, 2]*Qn_array_sub1[array_idx, 3]
                        *conj(Qn_array_sub2[array_idx, 5])
                      + Qn_array[array_idx, 3]*Qn_array_sub2[array_idx, 2]
                        *conj(Qn_array_sub1[array_idx, 5])
                      + Qn_array_sub1[array_idx, 2]*Qn_array_sub2[array_idx, 3]
                        *conj(Qn_array[array_idx, 5])
                      + Qn_array[array_idx, 2]*Qn_array_sub2[array_idx, 3]
                        *conj(Qn_array_sub1[array_idx, 5])
                      + Qn_array[array_idx, 3]*Qn_array_sub1[array_idx, 2]
                        *conj(Qn_array_sub2[array_idx, 5])
                      + Qn_array_sub1[array_idx, 3]*Qn_array_sub2[array_idx, 2]
                        *conj(Qn_array[array_idx, 5])
            ))
            /mean(6.*dN[array_idx]*dN_sub1[array_idx]*dN_sub2[array_idx])
        )
        corr_235_JK[iev] = corr_235_num/sqrt(v2_2*v3_2*v5_2)

        # cos(2Psi_2 + 4Psi_4 - 6Psi_6)
        corr_246_num = (
            mean(real(  Qn_array[array_idx, 2]*Qn_array_sub1[array_idx, 4]
                        *conj(Qn_array_sub2[array_idx, 6])
                      + Qn_array[array_idx, 4]*Qn_array_sub2[array_idx, 2]
                        *conj(Qn_array_sub1[array_idx, 6])
                      + Qn_array_sub1[array_idx, 2]*Qn_array_sub2[array_idx, 4]
                        *conj(Qn_array[array_idx, 6])
                      + Qn_array[array_idx, 2]*Qn_array_sub2[array_idx, 4]
                        *conj(Qn_array_sub1[array_idx, 6])
                      + Qn_array[array_idx, 4]*Qn_array_sub1[array_idx, 2]
                        *conj(Qn_array_sub2[array_idx, 6])
                      + Qn_array_sub1[array_idx, 4]*Qn_array_sub2[array_idx, 2]
                        *conj(Qn_array[array_idx, 6])
            ))
            /mean(6.*dN[array_idx]*dN_sub1[array_idx]*dN_sub2[array_idx])
        )
        corr_246_JK[iev] = corr_246_num/sqrt(v2_2*v4_2*v6_2)

    corr_224 = mean(corr_224_JK)
    corr_224_err = sqrt((nev - 1.)/nev*sum((corr_224_JK - corr_224)**2.))
    corr_336 = mean(corr_336_JK)
    corr_336_err = sqrt((nev - 1.)/nev*sum((corr_336_JK - corr_336)**2.))
    corr_235 = mean(corr_235_JK)
    corr_235_err = sqrt((nev - 1.)/nev*sum((corr_235_JK - corr_235)**2.))
    corr_246 = mean(corr_246_JK)
    corr_246_err = sqrt((nev - 1.)/nev*sum((corr_246_JK - corr_246)**2.))

    # output results to a file
    f = open(outputFileName, 'w')
    f.write("#correlator  value  value_err\n")
    f.write("224  %.5e  %.5e\n" % (corr_224, corr_224_err))
    f.write("336  %.5e  %.5e\n" % (corr_336, corr_336_err))
    f.write("235  %.5e  %.5e\n" % (corr_235, corr_235_err))
    f.write("246  %.5e  %.5e\n" % (corr_246, corr_246_err))
    f.close()
    return


def calcualte_event_plane_correlations(vn_array, outputFileName):
    """
        this function compute the scalar-product event plane correlations
        vn_array is a matrix [event_idx, vn_order]
    """
    vn_array = array(vn_array)
    nev = len(vn_array[:, 0])
    v2_array = vn_array[:, 2]
    v3_array = vn_array[:, 3]
    v4_array = vn_array[:, 4]
    v5_array = vn_array[:, 5]
    v6_array = vn_array[:, 6]

    corr_224_JK = zeros(nev)
    corr_22233_JK = zeros(nev)
    corr_2226_JK = zeros(nev)
    corr_336_JK = zeros(nev)
    corr_235_JK = zeros(nev)
    corr_246_JK = zeros(nev)
    corr_234_JK = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        v2_2 = mean(abs(v2_array[array_idx])**2.)
        v3_2 = mean(abs(v3_array[array_idx])**2.)
        v4_2 = mean(abs(v4_array[array_idx])**2.)
        v5_2 = mean(abs(v5_array[array_idx])**2.)
        v6_2 = mean(abs(v6_array[array_idx])**2.)

        # cos(4(Psi_2 - Psi_4))
        corr_224_num = mean(real((v2_array[array_idx]**2.)
                                 *conj(v4_array[array_idx])))
        corr_224_JK[iev] = corr_224_num/sqrt(v2_2*v2_2*v4_2)

        # cos(6(Psi_2 - Psi_3))
        corr_22233_num = mean(real((v2_array[array_idx]**3.)
                                   *conj(v3_array[array_idx])**2.))
        corr_22233_JK[iev] = corr_22233_num/sqrt(v2_2**3.*v3_2**2.)

        # cos(6(Psi_2 - Psi_6))
        corr_2226_num = mean(real(v2_array[array_idx]**3.
                                  *conj(v6_array[array_idx])))
        corr_2226_JK[iev] = corr_2226_num/sqrt((v2_2**3.)*v6_2)

        # cos(6(Psi_3 - Psi_6))
        corr_336_num = mean(real((v3_array[array_idx]**2.)
                                 *conj(v6_array[array_idx])))
        corr_336_JK[iev] = corr_336_num/sqrt((v3_2**2.)*v6_2)

        # cos(2Psi_2 + 3Psi_3 - 5Psi_5)
        corr_235_num = mean(real(v2_array[array_idx]*v3_array[array_idx]
                                 *conj(v5_array[array_idx])))
        corr_235_JK[iev] = corr_235_num/sqrt(v2_2*v3_2*v5_2)

        # cos(2Psi_2 + 4Psi_4 - 6Psi_6)
        corr_246_num = mean(real(v2_array[array_idx]*v4_array[array_idx]
                                 *conj(v6_array[array_idx])))
        corr_246_JK[iev] = corr_246_num/sqrt(v2_2*v4_2*v6_2)

        # cos(2Psi_2 - 6Psi_3 + 4Psi_4)
        corr_234_num = mean(real(v2_array[array_idx]
                                 *(conj(v3_array[array_idx])**2.)
                                 *v4_array[array_idx]))
        corr_234_JK[iev] = corr_234_num/sqrt(v2_2*(v3_2**2.)*v4_2)

    corr_224 = mean(corr_224_JK)
    corr_224_err = sqrt((nev - 1.)/nev*sum((corr_224_JK - corr_224)**2.))
    corr_22233 = mean(corr_22233_JK)
    corr_22233_err = sqrt((nev - 1.)/nev*sum((corr_22233_JK - corr_22233)**2.))
    corr_2226 = mean(corr_2226_JK)
    corr_2226_err = sqrt((nev - 1.)/nev*sum((corr_2226_JK - corr_2226)**2.))
    corr_336 = mean(corr_336_JK)
    corr_336_err = sqrt((nev - 1.)/nev*sum((corr_336_JK - corr_336)**2.))
    corr_235 = mean(corr_235_JK)
    corr_235_err = sqrt((nev - 1.)/nev*sum((corr_235_JK - corr_235)**2.))
    corr_246 = mean(corr_246_JK)
    corr_246_err = sqrt((nev - 1.)/nev*sum((corr_246_JK - corr_246)**2.))
    corr_234 = mean(corr_234_JK)
    corr_234_err = sqrt((nev - 1.)/nev*sum((corr_234_JK - corr_234)**2.))

    f = open(outputFileName, 'w')
    f.write("#correlator  value  value_err\n")
    f.write("4(24)  %.5e  %.5e\n" % (corr_224, corr_224_err))
    f.write("6(23)  %.5e  %.5e\n" % (corr_22233, corr_22233_err))
    f.write("6(26)  %.5e  %.5e\n" % (corr_2226, corr_2226_err))
    f.write("6(36)  %.5e  %.5e\n" % (corr_336, corr_336_err))
    f.write("(235)  %.5e  %.5e\n" % (corr_235, corr_235_err))
    f.write("(246)  %.5e  %.5e\n" % (corr_246, corr_246_err))
    f.write("(234)  %.5e  %.5e\n" % (corr_234, corr_234_err))
    f.close()
    return


def calculate_vn_arrays_for_rn_ratios(data):
    """
        this function compute the complex pT-integrated Vn vector
        in different pT ranges for a single event
        it returns a 2d matrix vn_arrays[pT_idx, n_order_idx]
    """
    pT_boundaries = [0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0]
    npT = 50
    vn_arrays = []
    for ipT in range(len(pT_boundaries)-1):
        pT_low = pT_boundaries[ipT]
        pT_high = pT_boundaries[ipT + 1]
        pT_mid = (pT_low + pT_high)/2.
        vn_array = calcualte_inte_vn(pT_low, pT_high, data)
        vn_array.insert(0, pT_mid)
        vn_arrays.append(vn_array)
    return(vn_arrays)


def calculate_rn_ratios(vn_event_arrays):
    """
        this function compute rn ratio in different pT bins
        according to the CMS measurements
        it reads in a 3d data cube
              vn_event_arrays[event_idx, pT_idx, n_order_idx]
        it returns rn_arrays[iorder, pT_idx, 3]
    """
    vn_event_arrays = array(vn_event_arrays)
    rn_arrays = []
    for iorder in range(3, 6):
        # compute r2, r3, r4
        rn_array = []
        for itrig in range(3, len(vn_event_arrays[0, :, 0])):
            pT_trig = real(vn_event_arrays[0, itrig, 0])
            dN_trig = real(vn_event_arrays[:, itrig, 1])
            Qn_trig_array = dN_trig*vn_event_arrays[:, itrig, iorder]
            nev = len(Qn_trig_array)

            denorm2_dN = dN_trig*(dN_trig - 1.)
            denorm2_array = abs(Qn_trig_array)**2. - dN_trig

            for iasso in range(0, itrig+1):
                pT_asso = real(vn_event_arrays[0, iasso, 0])
                dN_asso = real(vn_event_arrays[:, iasso, 1])
                Qn_asso_array = dN_asso*vn_event_arrays[:, iasso, iorder]

                num_dN = dN_trig*dN_asso
                num_array = real(Qn_asso_array*conj(Qn_trig_array))
                if iasso == itrig:
                    num_dN -= dN_asso
                    num_array = (real(Qn_asso_array*conj(Qn_trig_array))
                                 - dN_asso)

                denorm1_dN = dN_asso*(dN_asso - 1.)
                denorm1_array = abs(Qn_asso_array)**2. - dN_asso

                rn_jackknife = zeros(nev)
                for iev in range(nev):
                    array_idx = [True]*nev
                    array_idx[iev] = False
                    array_idx = array(array_idx)

                    num = mean(num_array[array_idx])/mean(num_dN[array_idx])
                    denorm1 = (mean(denorm1_array[array_idx])
                               /mean(denorm1_dN[array_idx]))
                    denorm2 = (mean(denorm2_array[array_idx])
                               /mean(denorm2_dN[array_idx]))

                    if denorm1 > 0. and denorm2 > 0.:
                        rn_jackknife[iev] = num/sqrt(denorm1*denorm2)

                rn_mean = mean(rn_jackknife)
                rn_err = sqrt((nev - 1.)/nev*sum((rn_jackknife - rn_mean)**2.))
                rn_array.append([pT_trig - pT_asso, rn_mean, rn_err])
        rn_arrays.append(rn_array)
    rn_arrays = array(rn_arrays)
    return(rn_arrays)


def calculate_symmetric_cumulant(vn_data_array, outputFileName):
    """
        this funciton computes the symmetric cumulant
            SC(m,n) = <v_m*conj(v_m)*v_n*conj(v_n)>
                      - <v_m*conj(v_m)>*<v_n*conj(v_n)>
        we use Jackknife resampling method to estimate the statistical error
    """
    vn_data_array = array(vn_data_array)
    nev = len(vn_data_array[:, 0])
    dN = real(vn_data_array[:, 0])
    Q1 = dN*vn_data_array[:, 1]
    Q2 = dN*vn_data_array[:, 2]
    Q3 = dN*vn_data_array[:, 3]
    Q4 = dN*vn_data_array[:, 4]
    Q5 = dN*vn_data_array[:, 5]
    Q6 = dN*vn_data_array[:, 6]

    # two-particle correlation
    N2_weight = dN*(dN - 1.)
    Q2_2 = abs(Q2)**2. - dN
    Q3_2 = abs(Q3)**2. - dN
    Q4_2 = abs(Q4)**2. - dN

    # four-particle correlation
    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q_32 = ((abs(Q2)**2.)*(abs(Q3)**2.) - 2.*real(Q5*conj(Q2)*conj(Q3))
        - 2.*real(Q3*conj(Q1)*conj(Q2)) + abs(Q5)**2. + abs(Q1)**2.
        - (dN - 4.)*(abs(Q2)**2. + abs(Q3)**2.) + dN*(dN - 6.)
    )
    Q_42 = ((abs(Q2)**2.)*(abs(Q4)**2.) - 2.*real(Q6*conj(Q2)*conj(Q4))
        - 2.*real(Q4*conj(Q2)*conj(Q2)) + abs(Q6)**2. + abs(Q2)**2.
        - (dN - 4.)*(abs(Q2)**2. + abs(Q4)**2.) + dN*(dN - 6.)
    )

    # calcualte observables with Jackknife resampling method
    SC32_array = zeros(nev)
    SC42_array = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        # SC(3,2)
        SC32_array[iev] = (mean(Q_32[array_idx])/mean(N4_weight[array_idx])
                           - (mean(Q3_2[array_idx])*mean(Q2_2[array_idx]))
                             /(mean(N2_weight[array_idx])**2.))

        # SC(4,2)
        SC42_array[iev] = (mean(Q_42[array_idx])/mean(N4_weight[array_idx])
                           - (mean(Q4_2[array_idx])*mean(Q2_2[array_idx]))
                             /(mean(N2_weight[array_idx])**2.))

    SC32_mean = mean(SC32_array)
    SC32_err = sqrt((nev - 1.)/nev*sum((SC32_array - SC32_mean)**2.))

    SC42_mean = mean(SC42_array)
    SC42_err = sqrt((nev - 1.)/nev*sum((SC42_array - SC42_mean)**2.))

    results = [SC32_mean, SC32_err, SC42_mean, SC42_err]
    f = open(outputFileName, 'w')
    f.write("# type  value  stat. err\n")
    for i in range(len(symmetric_cumulant_name_list)):
        f.write("%s  %.10e  %.10e\n"
                % (symmetric_cumulant_name_list[i],
                   results[2*i], results[2*i+1]))
    f.close()
    return


def calculate_vn4(vn_data_array, outputFileName):
    """
        this funciton computes the 4 particle cumulant vn{4}
            vn{4} = (2 <v_n*conj(v_n)>**2 - <(v_n*conj(v_n))**2.>)**(1/4)
    """
    vn_data_array = array(vn_data_array)
    nev = len(vn_data_array[:, 0])
    dN = real(vn_data_array[:, 0])
    Q1 = dN*vn_data_array[:, 1]
    Q2 = dN*vn_data_array[:, 2]
    Q3 = dN*vn_data_array[:, 3]
    Q4 = dN*vn_data_array[:, 4]
    Q5 = dN*vn_data_array[:, 5]
    Q6 = dN*vn_data_array[:, 6]

    # two-particle correlation
    N2_weight = dN*(dN - 1.)
    Q1_2 = abs(Q1)**2. - dN
    Q2_2 = abs(Q2)**2. - dN
    Q3_2 = abs(Q3)**2. - dN

    # four-particle correlation
    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q1_4 = ((abs(Q1)**4.) - 2.*real(Q2*conj(Q1)*conj(Q1))
             - 4.*(dN - 2.)*(abs(Q1)**2.) + abs(Q2)**2.
             + 2*dN*(dN - 3.))
    Q2_4 = ((abs(Q2)**4.) - 2.*real(Q4*conj(Q2)*conj(Q2))
             - 4.*(dN - 2.)*(abs(Q2)**2.) + abs(Q4)**2.
             + 2*dN*(dN - 3.))
    Q3_4 = ((abs(Q3)**4.) - 2.*real(Q6*conj(Q3)*conj(Q3))
             - 4.*(dN - 2.)*(abs(Q3)**2.) + abs(Q6)**2.
             + 2*dN*(dN - 3.))

    # calcualte observables with Jackknife resampling method
    C1_4_array = zeros(nev)
    C2_4_array = zeros(nev)
    C3_4_array = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        # C_1{4}
        C1_4_array[iev] = (mean(Q1_4[array_idx])/mean(N4_weight[array_idx])
                           - 2.*((mean(Q1_2[array_idx])
                                 /mean(N2_weight[array_idx]))**2.))
        # C_2{4}
        C2_4_array[iev] = (mean(Q2_4[array_idx])/mean(N4_weight[array_idx])
                           - 2.*((mean(Q2_2[array_idx])
                                 /mean(N2_weight[array_idx]))**2.))
        # C_3{4}
        C3_4_array[iev] = (mean(Q3_4[array_idx])/mean(N4_weight[array_idx])
                           - 2.*((mean(Q3_2[array_idx])
                                 /mean(N2_weight[array_idx]))**2.))
    C1_4_mean = mean(C1_4_array)
    C1_4_err  = sqrt((nev - 1.)/nev*sum((C1_4_array - C1_4_mean)**2.))
    C2_4_mean = mean(C2_4_array)
    C2_4_err  = sqrt((nev - 1.)/nev*sum((C2_4_array - C2_4_mean)**2.))
    C3_4_mean = mean(C3_4_array)
    C3_4_err  = sqrt((nev - 1.)/nev*sum((C3_4_array - C3_4_mean)**2.))

    v1_4 = 0.0
    v1_4_err = 0.0
    if C1_4_mean < 0:
        v1_4 = (-C1_4_mean)**0.25
        v1_4_err = 0.25*((-C1_4_mean)**(-0.75))*C1_4_err

    v2_4 = 0.0
    v2_4_err = 0.0
    if C2_4_mean < 0:
        v2_4 = (-C2_4_mean)**0.25
        v2_4_err = 0.25*((-C2_4_mean)**(-0.75))*C2_4_err

    v3_4 = 0.0
    v3_4_err = 0.0
    if C3_4_mean < 0:
        v3_4 = (-C3_4_mean)**0.25
        v3_4_err = 0.25*((-C3_4_mean)**(-0.75))*C3_4_err

    results = [v1_4, v1_4_err, C1_4_mean, C1_4_err,
               v2_4, v2_4_err, C2_4_mean, C2_4_err,
               v3_4, v3_4_err, C3_4_mean, C3_4_err,]
    f = open(outputFileName, 'w')
    f.write("# n  vn{4}  vn{4}_err  Cn{4}  Cn{4}_err\n")
    for i in range(1, 4):
        f.write("%d  %.10e  %.10e  %.10e  %.10e\n"
                % (i, results[4*i-4], results[4*i-3],
                   results[4*i-2], results[4*i-1]))
    f.close()
    return


def calculate_vn4_over_vn2(vn_data_array, outputFileName):
    """
        this funciton computes the ratio of
        the 4-particle cumulant vn{4} over the 2-particle cumulant vn{2}
        and Fn = sqrt((vn{2}^2 - vn{4}^2)/(vn{2}^2 + vn{4}^2))

            vn{4} = (2 <v_n*conj(v_n)>**2 - <(v_n*conj(v_n))**2.>)**(1/4)
            vn{2} = (<v_n*conj(v_n)>)**(1/2)

        we will use Jackknife resampling method to estimate
        the statistical error
    """
    vn_data_array = array(vn_data_array)
    nev = len(vn_data_array[:, 0])
    dN = real(vn_data_array[:, 0])
    Q1 = dN*vn_data_array[:, 1]
    Q2 = dN*vn_data_array[:, 2]
    Q3 = dN*vn_data_array[:, 3]
    Q4 = dN*vn_data_array[:, 4]
    Q5 = dN*vn_data_array[:, 5]
    Q6 = dN*vn_data_array[:, 6]

    # two-particle correlation
    N2_weight = dN*(dN - 1.)
    Q1_2 = abs(Q1)**2. - dN
    Q2_2 = abs(Q2)**2. - dN
    Q3_2 = abs(Q3)**2. - dN

    # four-particle correlation
    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q1_4 = ((abs(Q1)**4.) - 2.*real(Q2*conj(Q1)*conj(Q1))
             - 4.*(dN - 2.)*(abs(Q1)**2.) + abs(Q2)**2.
             + 2*dN*(dN - 3.))
    Q2_4 = ((abs(Q2)**4.) - 2.*real(Q4*conj(Q2)*conj(Q2))
             - 4.*(dN - 2.)*(abs(Q2)**2.) + abs(Q4)**2.
             + 2*dN*(dN - 3.))
    Q3_4 = ((abs(Q3)**4.) - 2.*real(Q6*conj(Q3)*conj(Q3))
             - 4.*(dN - 2.)*(abs(Q3)**2.) + abs(Q6)**2.
             + 2*dN*(dN - 3.))

    # calcualte observables with Jackknife resampling method
    r1_array = zeros(nev)
    r2_array = zeros(nev)
    r3_array = zeros(nev)
    F1_array = zeros(nev)
    F2_array = zeros(nev)
    F3_array = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        # C_n{4}
        C_1_4 = (mean(Q1_4[array_idx])/mean(N4_weight[array_idx])
                 - 2.*((mean(Q1_2[array_idx])/mean(N2_weight[array_idx]))**2.))
        C_1_2 = mean(Q1_2[array_idx])/mean(N2_weight[array_idx])
        if C_1_4 < 0. and C_1_2 > 0.:
            v1_4 = (-C_1_4)**0.25
            v1_2 = sqrt(C_1_2)
            r1_array[iev] = v1_4/(v1_2 + 1e-15)
            F1_array[iev] = sqrt((v1_2**2. - v1_4**2.)
                                 /(v1_2**2. + v1_4**2. + 1e-15))

        C_2_4 = (mean(Q2_4[array_idx])/mean(N4_weight[array_idx])
                 - 2.*((mean(Q2_2[array_idx])/mean(N2_weight[array_idx]))**2.))
        C_2_2 = mean(Q2_2[array_idx])/mean(N2_weight[array_idx])
        if C_2_4 < 0. and C_2_2 > 0.:
            v2_4 = (-C_2_4)**0.25
            v2_2 = sqrt(C_2_2)
            r2_array[iev] = v2_4/v2_2
            F2_array[iev] = sqrt((v2_2**2. - v2_4**2.)
                                 /(v2_2**2. + v2_4**2. + 1e-15))

        C_3_4 = (mean(Q3_4[array_idx])/mean(N4_weight[array_idx])
                 - 2.*((mean(Q3_2[array_idx])/mean(N2_weight[array_idx]))**2.))
        C_3_2 = mean(Q3_2[array_idx])/mean(N2_weight[array_idx])
        if C_3_4 < 0. and C_3_2 > 0.:
            v3_4 = (-C_3_4)**0.25
            v3_2 = sqrt(C_3_2)
            r3_array[iev] = v3_4/v3_2
            F3_array[iev] = sqrt((v3_2**2. - v3_4**2.)
                                 /(v3_2**2. + v3_4**2. + 1e-15))

    r1_mean = mean(r1_array)
    r1_err = sqrt((nev - 1.)/nev*sum((r1_array - r1_mean)**2.))
    r2_mean = mean(r2_array)
    r2_err = sqrt((nev - 1.)/nev*sum((r2_array - r2_mean)**2.))
    r3_mean = mean(r3_array)
    r3_err = sqrt((nev - 1.)/nev*sum((r3_array - r3_mean)**2.))

    F1_mean = mean(F1_array)
    F1_err = sqrt((nev - 1.)/nev*sum((F1_array - F1_mean)**2.))
    F2_mean = mean(F2_array)
    F2_err = sqrt((nev - 1.)/nev*sum((F2_array - F2_mean)**2.))
    F3_mean = mean(F3_array)
    F3_err = sqrt((nev - 1.)/nev*sum((F3_array - F3_mean)**2.))

    results = [r1_mean, r1_err, F1_mean, F1_err,
               r2_mean, r2_err, F2_mean, F2_err,
               r3_mean, r3_err, F3_mean, F3_err]
    f = open(outputFileName, 'w')
    f.write("# n  vn{4}/vn{2}  (vn{4}/vn{2})_err  Fn  Fn_err\n")
    f.write("# Fn = sqrt((vn{2}^2 - vn{4}^2)/(vn{2}^2 + vn{4}^2))\n")
    for i in range(1, 4):
        f.write("%d  %.10e  %.10e  %.10e  %.10e\n"
                % (i, results[4*i - 4], results[4*i - 3],
                   results[4*i - 2], results[4*i-1]))
    f.close()
    return


def calculate_vn6_over_vn4(vn_data_array, outputFileName):
    """
        this funciton computes the ratio of
        the 6-particle cumulant vn{6} over the 4-particle cumulant vn{4}
            cn{6} = <<6>> - 9<<2>><<4>> + 12<<2>>^3
            vn{6} = (cn{6}/4)**(1/6)
            vn{4} = (2 <v_n*conj(v_n)>**2 - <(v_n*conj(v_n))**2.>)**(1/4)
        and compute skewness estimator gamma_1
            gamma_1 = -6\sqrt{2}*vn{4}^2*(vn{4} - vn{6})
                                         /(vn{2}^2 - vn{4}^2)^(3/2)
        we will use Jackknife resampling method to estimate
        the statistical error
    """
    vn_data_array = array(vn_data_array)
    nev = len(vn_data_array[:, 0])
    dN = real(vn_data_array[:, 0])
    Q1 = dN*vn_data_array[:, 1]
    Q2 = dN*vn_data_array[:, 2]
    Q3 = dN*vn_data_array[:, 3]
    Q4 = dN*vn_data_array[:, 4]
    Q5 = dN*vn_data_array[:, 5]
    Q6 = dN*vn_data_array[:, 6]

    # two-particle correlation
    N2_weight = dN*(dN - 1.)
    Q2_2 = abs(Q2)**2. - dN

    # four-particle correlation
    N4_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)
    Q2_4 = ((abs(Q2)**4.) - 2.*real(Q4*conj(Q2)*conj(Q2))
             - 4.*(dN - 2.)*(abs(Q2)**2.) + abs(Q4)**2.
             + 2*dN*(dN - 3.))

    # six-particle correlation
    N6_weight = dN*(dN - 1.)*(dN - 2.)*(dN - 3.)*(dN - 4.)*(dN - 5.)
    Q2_6 = (abs(Q2)**6. + 9*(abs(Q4)**2.)*(abs(Q2)**2.)
            - 6.*real(Q4*Q2*conj(Q2)*conj(Q2)*conj(Q2))
            + 4.*real(Q6*conj(Q2)*conj(Q2)*conj(Q2))
            - 12.*real(Q6*conj(Q4)*conj(Q2))
            + 18.*(dN - 4.)*real(Q4*conj(Q2)*conj(Q2))
            + 4.*(abs(Q6)**2.)
            - 9.*(dN - 4.)*((abs(Q2)**4.) + (abs(Q4)**2.))
            + 18.*(dN - 5.)*(dN - 2.)*(abs(Q2)**2.)
            - 6.*dN*(dN - 4.)*(dN - 5.))

    # calcualte observables with Jackknife resampling method
    r2_array = zeros(nev)
    gamma1_array = zeros(nev)
    for iev in range(nev):
        array_idx = [True]*nev
        array_idx[iev] = False
        array_idx = array(array_idx)

        # C_n{4}
        C_2_2 = mean(Q2_2[array_idx])/mean(N2_weight[array_idx])
        C_2_4 = (mean(Q2_4[array_idx])/mean(N4_weight[array_idx])
                 - 2.*(C_2_2**2.))
        C_2_6 = (mean(Q2_6[array_idx])/mean(N6_weight[array_idx])
                 - 9.*C_2_2*mean(Q2_4[array_idx])/mean(N4_weight[array_idx])
                 + 12.*(C_2_2**3.))
        if C_2_6 > 0. and C_2_4 < 0. and C_2_2 > 0.:
            v2_2 = sqrt(C_2_2)
            v2_6 = (C_2_6/4.)**(1./6.)
            v2_4 = (-C_2_4)**(1./4.)
            r2_array[iev] = v2_6/v2_4
            gamma1_array[iev] = (-6.*sqrt(2)*(v2_4**2.)*(v2_4 - v2_6)
                                 /(v2_2**2. - v2_4**2.)**(1.5))

    r2_mean = mean(r2_array)
    r2_err = sqrt((nev - 1.)/nev*sum((r2_array - r2_mean)**2.))
    gamma1_mean = mean(gamma1_array)
    gamma1_err = sqrt((nev - 1.)/nev*sum((gamma1_array - gamma1_mean)**2.))

    f = open(outputFileName, 'w')
    f.write(
        "# n  vn{6}/vn{4}  (vn{6}/vn{4})_err  gamma_1  gamma_1_err\n")
    f.write("%d  %.10e  %.10e  %.10e  %.10e\n"
            % (2, r2_mean, r2_err, gamma1_mean, gamma1_err))
    f.close()
    return


def calculate_vn_eta(eta_array, dN_array, vn_array, eta_min, eta_max):
    """
        This function computes vn(eta).
        eta_min and eta_max specify the rapidity range of reference flow vector
    """
    nev, neta   = dN_array.shape
    dN_array    = dN_array.reshape((nev, 1, neta))
    idx         = (eta_array > eta_min) & (eta_array < eta_max)
    vn_ref      = (sum(dN_array[:, :, idx]*vn_array[:, :, idx], axis=2)
                   /(sum(dN_array[:, :, idx], axis=2) + 1e-15))
    vnshape     = vn_ref.shape
    nvn         = vnshape[1]
    vn_ref      = vn_ref.reshape((vnshape[0], vnshape[1], 1))
    vn_SP_ev    = real(vn_array*conj(vn_ref))
    vn_SP_array = zeros([nev, nvn, neta])
    for iev in range(nev):
        array_idx      = [True]*nev
        array_idx[iev] = False
        array_idx      = array(array_idx)
        vn_den         = mean((absolute(vn_ref[array_idx, :, :]))**2., axis=0)
        vn_SP          = (mean(vn_SP_ev[array_idx, :, :], axis=0)
                          /(sqrt(vn_den) + 1e-16))
        vn_SP_array[iev, :, :] = vn_SP
    vn_SP_mean = mean(vn_SP_array, axis=0)
    vn_SP_err  = sqrt((nev - 1.)/nev*sum((vn_SP_array - vn_SP_mean)**2., axis=0))
    return([vn_SP_mean, vn_SP_err])


def calculate_rn_eta(eta_array, dN_array, vn_array, outputFileName):
    """
        This function computes the longitudinal factorization breaking ratios
        for all n passed from vn_array
            eta, rn(eta)
    """
    nev, neta = dN_array.shape
    dN_array  = dN_array.reshape((nev, 1, neta))
    Qn_array  = vn_array
    Qnshape   = Qn_array.shape
    nQn       = Qnshape[1]

    # calculate the reference flow vector for every event
    eta_b_min    = 2.5
    eta_b_max    = 4.0
    eta_ref1_tmp = linspace(eta_b_min, eta_b_max, 16)
    eta_ref2_tmp = linspace(-eta_b_max, -eta_b_min, 16)
    Qn_ref1      = [] 
    Qn_ref2      = [] 
    for iev in range(nev):
        dN1_interp = interp(eta_ref1_tmp, eta_array, dN_array[iev, 0, :])
        dN2_interp = interp(eta_ref2_tmp, eta_array, dN_array[iev, 0, :])
        Qn_ref1_vec = []
        Qn_ref2_vec = []
        for iorder in range(nQn):
            Qn1_interp = interp(eta_ref1_tmp, eta_array,
                                Qn_array[iev, iorder, :])
            Qn2_interp = interp(eta_ref2_tmp, eta_array,
                                Qn_array[iev, iorder, :])
            Qn_ref1_vec.append(sum(dN1_interp*Qn1_interp)
                               /(sum(dN1_interp) + 1e-15))
            Qn_ref2_vec.append(sum(dN2_interp*Qn2_interp)
                               /(sum(dN2_interp) + 1e-15))
        Qn_ref1.append(Qn_ref1_vec)
        Qn_ref2.append(Qn_ref2_vec)
    Qn_ref1 = array(Qn_ref1).reshape((nev, nQn, 1))
    Qn_ref2 = array(Qn_ref2).reshape((nev, nQn, 1))

    rn_num    = real(Qn_array[:, :, ::-1]*conj(Qn_ref1))
    rn_den    = real(Qn_array*conj(Qn_ref1))
    rnn_num   = real((Qn_ref2*conj(Qn_array))
                     *(Qn_array[:, :, ::-1]*conj(Qn_ref1)))
    rnn_den   = real((Qn_ref2*conj(Qn_array[:, :, ::-1]))
                     *(Qn_array*conj(Qn_ref1)))

    # compute the error using jack-knife
    rn_array  = zeros([nev, nQn, neta])
    rnn_array = zeros([nev, nQn, neta])
    for iev in range(nev):
        array_idx      = [True]*nev
        array_idx[iev] = False
        array_idx      = array(array_idx)
        rn_ev          = (mean(rn_num[array_idx], axis=0)
                          /(mean(rn_den[array_idx], axis=0) + 1e-15))
        rnn_ev         = (mean(rnn_num[array_idx], axis=0)
                          /(mean(rnn_den[array_idx], axis=0) + 1e-15))
        rn_array[iev, :, :]  = rn_ev
        rnn_array[iev, :, :] = rnn_ev
    rn_mean  = mean(rn_array, axis=0)
    rn_err   = sqrt((nev - 1.)/nev*sum((rn_array - rn_mean)**2., axis=0))
    rnn_mean = mean(rnn_array, axis=0)
    rnn_err  = sqrt((nev - 1.)/nev*sum((rnn_array - rnn_mean)**2., axis=0))

    f = open(outputFileName, 'w')
    f.write("#eta  rn(eta)  rn_err(eta)  rnn(eta)  rnn_err(eta)\n")
    for ieta in range(len(eta_array)-1):
        f.write("%.10e  " % eta_array[ieta])
        for iorder in range(0, n_order-1):
            f.write("%.10e  %.10e  %.10e  %.10e  "
                    % (rn_mean[iorder, ieta], rn_err[iorder, ieta],
                       rnn_mean[iorder, ieta], rnn_err[iorder, ieta]))
        f.write("\n")
    f.close()
    return


def calculate_meanpT_fluc(dN_array, pT_array, pT_min=0.0, pT_max=3.0):
    """
        This function computes the mean pT fluctuations
            returns sigma_pT/<pT>, sigma_pT/<pT>_err
        here sigma_pT is the standard deviation of the event-by-event mean pT
        This function accepts pT_cut through [pT_min, pT_max]
        dN_array is dN/(2\pi dy pT dpT)
    """
    npT_interp = 50
    pT_inte_array = linspace(pT_min, pT_max, npT_interp)

    nev, npT = dN_array.shape
    mean_pT_array = zeros(nev)
    for iev in range(nev):
        dN_interp = exp(interp(pT_inte_array, pT_array[iev, :],
                               log(dN_array[iev, :] + 1e-30)))
        mean_pT_array[iev] = (sum(pT_inte_array**2.*dN_interp)
                              /sum(pT_inte_array*dN_interp))

    # compute the error using jack-knife
    rn_array  = zeros(nev)
    for iev in range(nev):
        array_idx      = [True]*nev
        array_idx[iev] = False
        array_idx      = array(array_idx)
        rn_ev          = (std(mean_pT_array[array_idx])
                          /(mean(mean_pT_array[array_idx]) + 1e-15))
        rn_array[iev]  = rn_ev
    rn_mean  = mean(rn_array, axis=0)
    rn_err   = sqrt((nev - 1.)/nev*sum((rn_array - rn_mean)**2.))
    return([rn_mean, rn_err])


hf = h5py.File(data_path, "r")
event_list = list(hf.keys())
print("total number of events: {}".format(len(event_list)))
if CentralityFlag == 2:
    event_list_1 = []
    nev_min = 1e10
    nev_centrality = []
    for icen in range(len(Reg_centrality_cut_list) - 1):
        cen_bin_width = ((  Reg_centrality_cut_list[icen+1]
                          - Reg_centrality_cut_list[icen])/100.)
        cen_label = ("C{0:d}-{1:d}_".format(
            int(Reg_centrality_cut_list[icen]),
            int(Reg_centrality_cut_list[icen+1]))
        )
        selected_events_list = []
        for ifolder, event_name in enumerate(event_list):
            if cen_label in event_name:
                selected_events_list.append(event_name)
        nev_i = len(selected_events_list)
        nev_centrality.append(nev_i)
        if nev_i/cen_bin_width < nev_min:
            nev_min = int(nev_i/cen_bin_width)
    print("Removing the centrality bias, using nev = {}".format(nev_min))
    for icen in range(len(Reg_centrality_cut_list) - 1):
        cen_bin_width = ((  Reg_centrality_cut_list[icen+1]
                          - Reg_centrality_cut_list[icen])/100.)
        cen_label = ("C{0:d}-{1:d}_".format(
            int(Reg_centrality_cut_list[icen]),
            int(Reg_centrality_cut_list[icen+1]))
        )
        iev = 0
        for ifolder, event_name in enumerate(event_list):
            if (cen_label in event_name
                and iev < int(nev_min*cen_bin_width)):
                event_list_1.append(event_name)
                iev += 1
    event_list = event_list_1

dNdyDict = {}
dNdyList = []
if CentralityFlag > 0:
    for ifolder, event_name in enumerate(event_list):
        #file_name = "particle_9999_vndata_eta_-0.5_0.5.dat"
        
        file_name = "particle_9999_vndata_eta_-0.5_0.5_pT_0.05_4.05.dat"
        if RapidityTrigger == 1:      # PHENIX BBC Trigger
            file_name = "particle_9999_vndata_eta_-3.9_-3.1.dat"
        elif RapidityTrigger == 2:    # ALICE V0A Trigger
            file_name = "particle_9999_vndata_eta_-5.1_-2.8.dat"
        elif RapidityTrigger == 3:    # ATLAS forward Trigger
            file_name = "particle_9999_vndata_eta_-4.9_-3.1.dat"
        try:
            event_group = hf.get(event_name)
            temp_data   = event_group.get(file_name)
            temp_data   = nan_to_num(temp_data)
            #print (temp_data)
            dNdyDict[event_name] = temp_data[0, 1]
            print(ifolder,event_name,temp_data[0,1])
        except:
            continue
    dNdyList = -sort(-array(list(dNdyDict.values())))
print("Number of good events: {}".format(len(dNdyList)))


for icen in range(len(centralityCutList) - 1):
    if centralityCutList[icen+1] < centralityCutList[icen]: continue
    avg_folder = path.join(
        avg_folder_header, "{0:02.0f}-{1:02.0f}".format(
            centralityCutList[icen], centralityCutList[icen+1])
    )

    if path.isdir(avg_folder):
        print("{} already exists, skipped ...".format(avg_folder))
        continue
    else:
        mkdir(avg_folder)

    selected_events_list = []
    if CentralityFlag == 0:
        cen_label = ("C{0:d}-{1:d}_".format(
            int(centralityCutList[icen]),
            int(centralityCutList[icen+1]))
        )
        for ifolder, event_name in enumerate(event_list):
            if cen_label in event_name:
                selected_events_list.append(event_name)
    elif CentralityFlag > 0:
        dN_dy_cut_high = dNdyList[
            int(len(dNdyList)*centralityCutList[icen]/100.)
        ]
        dN_dy_cut_low  = dNdyList[
            min(len(dNdyList)-1,
                int(len(dNdyList)*centralityCutList[icen+1]/100.))
        ]
        for event_name in dNdyDict.keys():
            if (dNdyDict[event_name] > dN_dy_cut_low
                and dNdyDict[event_name] <= dN_dy_cut_high):
                selected_events_list.append(event_name)

    nev = len(selected_events_list)
    print("analysis {}%-{}% nev = {}...".format(
            centralityCutList[icen], centralityCutList[icen+1], nev))
    if nev == 0:
        print("Skip ...")
        continue

    for ipart, particle_id in enumerate(particle_list):
        print("processing %s ..." % particle_name_list[ipart])

        # first particle yield dN/dy
        if particle_id == '9999':
            file_name = 'particle_%s_vndata_eta_-0.5_0.5_pT_0.05_4.05.dat' % particle_id
        else:
            file_name = 'particle_%s_vndata_y_-0.5_0.5_pT_0.05_4.05.dat' % particle_id

        dN_dy = zeros(len(selected_events_list))
        for ifolder, event_name in enumerate(selected_events_list):
            print(ifolder, event_name)
            event_group = hf.get(event_name)
            temp_data = event_group.get(file_name)
            temp_data = nan_to_num(temp_data)
            dN_dy[ifolder] = temp_data[0, 1]
        dN_dy_avg = mean(dN_dy)
        dN_dy_avg_err = std(dN_dy)/sqrt(nev)

        # then <pT>, vn, dN/(2pi dy pT dpT), vn{SP}(pT)
        if particle_id == '9999':
            file_name = 'particle_%s_vndata_diff_eta_-0.5_0.5_pT_0.05_4.05.dat' % particle_id
        else:
            file_name = 'particle_%s_vndata_diff_y_-0.5_0.5_pT_0.05_4.05.dat' % particle_id
        #file_name_ref1 = 'particle_9999_vndata_diff_eta_0.5_2.5.dat'
        #file_name_ref2 = 'particle_9999_vndata_diff_eta_-2.5_-0.5.dat'
        #file_name_ALICE = 'particle_9999_vndata_diff_eta_-0.8_0.8.dat'
        #file_name_ATLAS = 'particle_9999_vndata_diff_eta_-2.5_2.5.dat'
        
        file_name_ref1 = 'particle_9999_vndata_diff_eta_-0.5_0.5_pT_0.05_4.05.dat'
        file_name_ref2 = 'particle_9999_vndata_diff_eta_-0.5_0.5_pT_0.05_4.05.dat'
        file_name_ALICE = 'particle_9999_vndata_diff_eta_-0.5_0.5_pT_0.05_4.05.dat'
        file_name_ATLAS = 'particle_9999_vndata_diff_eta_-0.5_0.5_pT_0.05_4.05.dat'

        pT_array = []
        dN_array = []
        pT_array_ALICE = []
        dN_array_ALICE = []
        pT_array_ATLAS = []
        dN_array_ATLAS = []
        vn_phenix_array = []
        vn_phenix_array_sub1 = []; vn_phenix_array_sub2 = []
        vn_star_array = []
        vn_star_array_sub1 = []; vn_star_array_sub2 = []
        vn_alice_array = []
        vn_alice_array_sub1 = []; vn_alice_array_sub2 = []
        vn_cms_array = []
        vn_cms_array_sub1 = []; vn_cms_array_sub2 = []
        vn_cms_arrays_for_rn = []
        vn_atlas_array = []
        vn_atlas_array_sub1 = []; vn_atlas_array_sub2 = []
        QnpT_diff_phenix = []; Qnref_phenix = []
        QnpT_diff_star = []; Qnref_star = []
        QnpT_diff_alice = []; Qnref_alice = []
        QnpT_diff_cms = []; Qnref_cms = []
        QnpT_diff_atlas = []; Qnref_atlas = []
        vn_diff_2PC_real = []; vn_diff_2PC_imag = []; vn_diff_2PC_denorm = []
        for ifolder, event_name in enumerate(selected_events_list):
            event_group = hf.get(event_name)
            temp_data = event_group.get(file_name)
            temp_data = nan_to_num(temp_data)
            temp_data_ref1 = event_group.get(file_name_ref1)
            temp_data_ref1 = nan_to_num(temp_data_ref1)
            temp_data_ref2 = event_group.get(file_name_ref2)
            temp_data_ref2 = nan_to_num(temp_data_ref2)

            dN_event = temp_data[:, 2]  # dN/(2pi dy pT dpT)
            pT_event = temp_data[:, 0]

            # record particle spectra
            pT_array.append(pT_event)
            dN_array.append(dN_event)
            if particle_id == "9999":
                try:
                    
                    temp_data1 = event_group.get(file_name_ATLAS)
                    temp_data1 = nan_to_num(temp_data1)
                    pT_array_ATLAS.append(temp_data1[:, 0])
                    dN_array_ATLAS.append(temp_data1[:, 2])
                    temp_data1 = event_group.get(file_name_ALICE)
                    temp_data1 = nan_to_num(temp_data1)
                    pT_array_ALICE.append(temp_data1[:, 0])
                    dN_array_ALICE.append(temp_data1[:, 2])
                except:
                    continue

            # pT-integrated vn
            # vn with PHENIX pT cut
            temp_vn_array = calcualte_inte_vn(0.2, 2.0, temp_data)
            vn_phenix_array.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.2, 2.0, temp_data_ref1)
            vn_phenix_array_sub1.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.2, 2.0, temp_data_ref2)
            vn_phenix_array_sub2.append(temp_vn_array)

            # vn with STAR pT cut
            temp_vn_array = calcualte_inte_vn(0.15, 2.0, temp_data)
            vn_star_array.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.15, 2.0, temp_data_ref1)
            vn_star_array_sub1.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.15, 2.0, temp_data_ref2)
            vn_star_array_sub2.append(temp_vn_array)

            # vn with ALICE pT cut
            temp_vn_array = calcualte_inte_vn(0.2, 3.0, temp_data)
            vn_alice_array.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.2, 3.0, temp_data_ref1)
            vn_alice_array_sub1.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.2, 3.0, temp_data_ref2)
            vn_alice_array_sub2.append(temp_vn_array)

            # vn with CMS pT cut
            temp_vn_array = calcualte_inte_vn(0.3, 3.0, temp_data)
            vn_cms_array.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.3, 3.0, temp_data_ref1)
            vn_cms_array_sub1.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.3, 3.0, temp_data_ref2)
            vn_cms_array_sub2.append(temp_vn_array)
            if particle_id == "9999" and not FastFlag:
                temp_vn_arrays = (
                        calculate_vn_arrays_for_rn_ratios(temp_data))
                vn_cms_arrays_for_rn.append(temp_vn_arrays)

            # vn with ATLAS pT cut
            temp_vn_array = calcualte_inte_vn(0.5, 3.0, temp_data)
            vn_atlas_array.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.5, 3.0, temp_data_ref1)
            vn_atlas_array_sub1.append(temp_vn_array)
            temp_vn_array = calcualte_inte_vn(0.5, 3.0, temp_data_ref2)
            vn_atlas_array_sub2.append(temp_vn_array)

            # pT-differential vn using scalar-product method
            # vn{SP}(pT) with PHENIX pT cut
            temp_arr = calculate_diff_vn_single_event(0.2, 2.0, temp_data,
                                                      temp_data_ref1)
            QnpT_diff_phenix.append(temp_arr[0])
            Qnref_phenix.append(temp_arr[1])

            # vn{SP}(pT) with STAR pT cut
            temp_arr = calculate_diff_vn_single_event(0.15, 2.0, temp_data,
                                                      temp_data_ref1)
            QnpT_diff_star.append(temp_arr[0])
            Qnref_star.append(temp_arr[1])

            # vn{4}(pT) with ALICE pT cut
            temp_arr = calculate_diff_vn_single_event(0.20, 3.0, temp_data,
                                                      temp_data_ref1)
            QnpT_diff_alice.append(temp_arr[0])
            Qnref_alice.append(temp_arr[1])

            # vn{SP}(pT) with CMS pT cut
            temp_arr = calculate_diff_vn_single_event(0.30, 3.0, temp_data,
                                                     temp_data_ref1)
            QnpT_diff_cms.append(temp_arr[0])
            Qnref_cms.append(temp_arr[1])

            # vn{SP}(pT) with ATLAS pT cut
            temp_arr = calculate_diff_vn_single_event(0.50, 3.0, temp_data,
                                                     temp_data_ref1)
            QnpT_diff_atlas.append(temp_arr[0])
            Qnref_atlas.append(temp_arr[1])

            # pT-differential vn using 2PC method
            # vn[2](pT)
            temp_vn_diff_real, temp_vn_diff_imag, temp_dn_diff = (
                                get_vn_diff_2PC_from_single_event(temp_data))
            vn_diff_2PC_real.append(temp_vn_diff_real)
            vn_diff_2PC_imag.append(temp_vn_diff_imag)
            vn_diff_2PC_denorm.append(temp_dn_diff)

        # now we perform event average
        dN_array = array(dN_array)
        pT_array = array(pT_array)

        n_pT = len(pT_array[0, :])
        pT_spectra = zeros([n_pT])
        for ipT in range(len(pT_array[0, :])):
            dN_temp = sum(dN_array[:, ipT]*pT_array[:, ipT])
            if(dN_temp > 0):
                pT_spectra[ipT] = (
                        sum(pT_array[:, ipT]**2.*dN_array[:, ipT])/dN_temp)
            else:
                pT_spectra[ipT] = mean(pT_array[:, ipT])
        # dN/(2pi dy pT dpT)
        dN_spectra = mean(pT_array*dN_array, 0)/pT_spectra
        dN_spectra_err = std(pT_array*dN_array, 0)/pT_spectra/sqrt(nev)

        # compute mean pT event-by-event
        sigma_pT, sigma_pT_err = calculate_meanpT_fluc(dN_array, pT_array,
                                                       0.15, 2.0)

        if particle_id == "9999":
            # calculate dNch (pT > 0.4 |eta| < 2.5) for ATLAS
            dN_array_ATLAS = array(dN_array_ATLAS)
            pT_array_ATLAS = array(pT_array_ATLAS)
            n_pT = len(pT_array_ATLAS[0, :])
            pT_spectra_ATLAS = zeros([n_pT])
            for ipT in range(len(pT_array_ATLAS[0, :])):
                dN_temp = sum(dN_array_ATLAS[:, ipT]*pT_array_ATLAS[:, ipT])
                if (dN_temp > 0):
                    pT_spectra_ATLAS[ipT] = (
                        sum(pT_array_ATLAS[:, ipT]**2.*dN_array_ATLAS[:, ipT])
                        /dN_temp)
                else:
                    pT_spectra_ATLAS[ipT] = mean(pT_array_ATLAS[:, ipT])
            # dN/(2pi pT dpT) (ATLAS)
            dN_spectra_ATLAS = (mean(pT_array_ATLAS*dN_array_ATLAS, 0)
                                /(pT_spectra_ATLAS + 1e-30))
            dN_spectra_ATLAS_err = (std(pT_array_ATLAS*dN_array_ATLAS, 0)
                                    /(pT_spectra_ATLAS + 1e-30)/sqrt(nev))
            pT_interp1 = linspace(0.4, 3.0, 30)
            dpT1 = pT_interp1[1] - pT_interp1[0]
            dN_interp1 = exp(interp(pT_interp1, pT_spectra_ATLAS,
                                    log(dN_spectra_ATLAS + 1e-30)))
            dN_interp1_err = interp(pT_interp1, pT_spectra_ATLAS,
                                    dN_spectra_ATLAS_err)
            dNch_ATLAS = sum(pT_interp1*dN_interp1)*dpT1*2*pi*5.
            print("dNch(pT > 0.4 GeV, |eta| < 2.5) = {0:.4f}".format(
                                                                dNch_ATLAS))

            # calculate dNch (pT > 0.2 |eta| < 0.8) for ALICE
            dN_array_ALICE = array(dN_array_ALICE)
            pT_array_ALICE = array(pT_array_ALICE)

            n_pT = len(pT_array_ALICE[0, :])
            pT_spectra_ALICE = zeros([n_pT])
            for ipT in range(len(pT_array_ALICE[0, :])):
                dN_temp = sum(dN_array_ALICE[:, ipT]*pT_array_ALICE[:, ipT])
                if (dN_temp > 0):
                    pT_spectra_ALICE[ipT] = (
                        sum(pT_array_ALICE[:, ipT]**2.*dN_array_ALICE[:, ipT])
                        /dN_temp)
                else:
                    pT_spectra_ALICE[ipT] = mean(pT_array_ALICE[:, ipT])
            # dN/(2pi pT dpT)
            dN_spectra_ALICE = (mean(pT_array_ALICE*dN_array_ALICE, 0)
                                /(pT_spectra_ALICE + 1e-30))
            dN_spectra_ALICE_err = (std(pT_array_ALICE*dN_array_ALICE, 0)
                                    /(pT_spectra_ALICE + 1e-30)/sqrt(nev))
            pT_interp1 = linspace(0.2, 3.0, 30)
            dpT1 = pT_interp1[1] - pT_interp1[0]
            dN_interp1 = exp(interp(pT_interp1, pT_spectra_ALICE,
                                    log(dN_spectra_ALICE + 1e-30)))
            dN_interp1_err = interp(pT_interp1, pT_spectra_ALICE,
                                    dN_spectra_ALICE_err)
            dNch_ALICE = sum(pT_interp1*dN_interp1)*dpT1*2*pi*1.6
            print("dNch(pT > 0.2 GeV, |eta| < 0.8) = {0:.4f}".format(
                                                                dNch_ALICE))

            # calculate dNch (pT > 0.15 |eta| < 0.8) for ALICE
            pT_interp1 = linspace(0.15, 3.0, 30)
            dpT1 = pT_interp1[1] - pT_interp1[0]
            dN_interp1 = exp(interp(pT_interp1, pT_spectra_ALICE,
                                    log(dN_spectra_ALICE + 1e-30)))
            dN_interp1_err = interp(pT_interp1, pT_spectra_ALICE,
                                    dN_spectra_ALICE_err)
            dNch_ALICE2 = sum(pT_interp1*dN_interp1)*dpT1*2*pi*1.6
            print("dNch(pT > 0.15 GeV, |eta| < 0.8) = {0:.4f}".format(
                                                                dNch_ALICE2))


        # calculate mean pT from event-averaged particle spectrum
        pT_interp = linspace(0.05, 2.95, 30)
        dN_interp = exp(interp(pT_interp, pT_spectra, log(dN_spectra + 1e-30)))
        dN_interp_err = interp(pT_interp, pT_spectra, dN_spectra_err)
        mean_pT = sum(pT_interp**2.*dN_interp)/sum(pT_interp*dN_interp)
        mean_pT_upper = (sum(pT_interp**2.*(dN_interp+dN_interp_err))
                         /sum(pT_interp*(dN_interp+dN_interp_err)))
        mean_pT_lower = (sum(pT_interp**2.*(dN_interp-dN_interp_err))
                         /sum(pT_interp*(dN_interp-dN_interp_err)))
        mean_pT_err = max(abs(mean_pT_upper - mean_pT), 
                          abs(mean_pT - mean_pT_lower))
        pT_interp = linspace(0.15, 2.95, 30)
        dN_interp = exp(interp(pT_interp, pT_spectra, log(dN_spectra + 1e-30)))
        dN_interp_err = interp(pT_interp, pT_spectra, dN_spectra_err)
        mean_pT_1 = sum(pT_interp**2.*dN_interp)/sum(pT_interp*dN_interp)
        mean_pT_1_upper = (sum(pT_interp**2.*(dN_interp+dN_interp_err))
                         /sum(pT_interp*(dN_interp+dN_interp_err)))
        mean_pT_1_lower = (sum(pT_interp**2.*(dN_interp-dN_interp_err))
                         /sum(pT_interp*(dN_interp-dN_interp_err)))
        mean_pT_1_err = max(abs(mean_pT_1_upper - mean_pT_1), 
                          abs(mean_pT_1 - mean_pT_1_lower))
        
        pT_interp = linspace(0.1, 3.0, 30)
        dN_interp = exp(interp(pT_interp, pT_spectra, log(dN_spectra + 1e-30)))
        dN_interp_err = interp(pT_interp, pT_spectra, dN_spectra_err)
        mean_pT_2 = sum(pT_interp**2.*dN_interp)/sum(pT_interp*dN_interp)
        mean_pT_2_upper = (sum(pT_interp**2.*(dN_interp+dN_interp_err))
                         /sum(pT_interp*(dN_interp+dN_interp_err)))
        mean_pT_2_lower = (sum(pT_interp**2.*(dN_interp-dN_interp_err))
                         /sum(pT_interp*(dN_interp-dN_interp_err)))
        mean_pT_2_err = max(abs(mean_pT_1_upper - mean_pT_1), 
                          abs(mean_pT_1 - mean_pT_1_lower))
        
        pT_interp = linspace(0.2, 3.0, 30)
        dN_interp = exp(interp(pT_interp, pT_spectra, log(dN_spectra + 1e-30)))
        dN_interp_err = interp(pT_interp, pT_spectra, dN_spectra_err)
        mean_pT_3 = sum(pT_interp**2.*dN_interp)/sum(pT_interp*dN_interp)
        mean_pT_3_upper = (sum(pT_interp**2.*(dN_interp+dN_interp_err))
                         /sum(pT_interp*(dN_interp+dN_interp_err)))
        mean_pT_3_lower = (sum(pT_interp**2.*(dN_interp-dN_interp_err))
                         /sum(pT_interp*(dN_interp-dN_interp_err)))
        mean_pT_3_err = max(abs(mean_pT_1_upper - mean_pT_1), 
                          abs(mean_pT_1 - mean_pT_1_lower))
        
        pT_interp = linspace(0.3, 4.6, 30)
        dN_interp = exp(interp(pT_interp, pT_spectra, log(dN_spectra + 1e-30)))
        dN_interp_err = interp(pT_interp, pT_spectra, dN_spectra_err)
        mean_pT_4 = sum(pT_interp**2.*dN_interp)/sum(pT_interp*dN_interp)
        mean_pT_4_upper = (sum(pT_interp**2.*(dN_interp+dN_interp_err))
                         /sum(pT_interp*(dN_interp+dN_interp_err)))
        mean_pT_4_lower = (sum(pT_interp**2.*(dN_interp-dN_interp_err))
                        /sum(pT_interp*(dN_interp-dN_interp_err)))
        mean_pT_4_err = max(abs(mean_pT_1_upper - mean_pT_1), 
                          abs(mean_pT_1 - mean_pT_1_lower))

        # calcualte vn{2}
        vn_phenix_2, vn_phenix_2_err = calcualte_vn_2(vn_phenix_array)
        vn_star_2, vn_star_2_err = calcualte_vn_2(vn_star_array)
        vn_alice_2, vn_alice_2_err = calcualte_vn_2(vn_alice_array)
        vn_cms_2, vn_cms_2_err = calcualte_vn_2(vn_cms_array)
        vn_atlas_2, vn_atlas_2_err = calcualte_vn_2(vn_atlas_array)

        # calcualte vn{2} with |\Delta \eta| > 1
        vn_phenix_2_gap, vn_phenix_2_gap_err = calcualte_vn_2_with_gap(
                                vn_phenix_array_sub1, vn_phenix_array_sub2)
        vn_star_2_gap, vn_star_2_gap_err = calcualte_vn_2_with_gap(
                                vn_star_array_sub1, vn_star_array_sub2)
        vn_alice_2_gap, vn_alice_2_gap_err = calcualte_vn_2_with_gap(
                                vn_alice_array_sub1, vn_alice_array_sub2)
        vn_cms_2_gap, vn_cms_2_gap_err = calcualte_vn_2_with_gap(
                                vn_cms_array_sub1, vn_cms_array_sub2)
        vn_atlas_2_gap, vn_atlas_2_gap_err = calcualte_vn_2_with_gap(
                                vn_atlas_array_sub1, vn_atlas_array_sub2)

        if particle_id == '9999' and not FastFlag:
            vn_alice_array2 = array(vn_alice_array)
            vn_cms_array2 = array(vn_cms_array)
            vn_atlas_array2 = array(vn_atlas_array)
            # calculate non-linear response coefficents with ALICE pT cut
            output_filename = path.join(
                    avg_folder, "non_linear_response_coefficients_ALICE.dat")
            calculate_nonlinear_reponse(vn_alice_array2, output_filename)
            # calculate non-linear response coefficents with CMS pT cut
            output_filename = path.join(
                    avg_folder, "non_linear_response_coefficients_CMS.dat")
            calculate_nonlinear_reponse(vn_cms_array2, output_filename)
            # calculate non-linear response coefficents with ATLAS pT cut
            output_filename = path.join(
                    avg_folder, "non_linear_response_coefficients_ATLAS.dat")
            calculate_nonlinear_reponse(vn_atlas_array2, output_filename)

            # calculate symmetric cumulant coefficents with ALICE pT cut
            output_filename = path.join(
                    avg_folder, "symmetric_cumulant_ALICE.dat")
            calculate_symmetric_cumulant(vn_alice_array, output_filename)

            # calculate vn{4}
            output_filename = path.join(
                    avg_folder, "charged_hadron_vn4_PHENIX.dat")
            calculate_vn4(vn_phenix_array, output_filename)
            output_filename = path.join(
                    avg_folder, "charged_hadron_vn4_STAR.dat")
            calculate_vn4(vn_star_array, output_filename)
            output_filename = path.join(
                    avg_folder, "charged_hadron_vn4_ALICE.dat")
            calculate_vn4(vn_alice_array, output_filename)
            output_filename = path.join(
                    avg_folder, "charged_hadron_vn4_CMS.dat")
            calculate_vn4(vn_cms_array, output_filename)
            output_filename = path.join(
                    avg_folder, "charged_hadron_vn4_ATLAS.dat")
            calculate_vn4(vn_atlas_array, output_filename)

            # calculate vn{4}/vn{2} and vn{6}/vn{4}
            output_filename = path.join(
                avg_folder, "charged_hadron_vn4_over_vn2_PHENIX.dat")
            calculate_vn4_over_vn2(vn_phenix_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn4_over_vn2_STAR.dat")
            calculate_vn4_over_vn2(vn_star_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn4_over_vn2_ALICE.dat")
            calculate_vn4_over_vn2(vn_alice_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn4_over_vn2_CMS.dat")
            calculate_vn4_over_vn2(vn_cms_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn4_over_vn2_ATLAS.dat")
            calculate_vn4_over_vn2(vn_atlas_array, output_filename)

            output_filename = path.join(
                avg_folder, "charged_hadron_vn6_over_vn4_PHENIX.dat")
            calculate_vn6_over_vn4(vn_phenix_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn6_over_vn4_STAR.dat")
            calculate_vn6_over_vn4(vn_star_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn6_over_vn4_ALICE.dat")
            calculate_vn6_over_vn4(vn_alice_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn6_over_vn4_CMS.dat")
            calculate_vn6_over_vn4(vn_cms_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn6_over_vn4_ATLAS.dat")
            calculate_vn6_over_vn4(vn_atlas_array, output_filename)

            # calculate vn distribution for charged hadrons
            output_filename = path.join(
                avg_folder, "charged_hadron_vn_distribution_PHENIX.dat")
            calculate_vn_distribution(vn_phenix_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn_distribution_STAR.dat")
            calculate_vn_distribution(vn_star_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn_distribution_ALICE.dat")
            calculate_vn_distribution(vn_alice_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn_distribution_CMS.dat")
            calculate_vn_distribution(vn_cms_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_vn_distribution_ATLAS.dat")
            calculate_vn_distribution(vn_atlas_array, output_filename)

            # calculate rn ratios
            rn_cms = calculate_rn_ratios(vn_cms_arrays_for_rn)

            # calculate flow event-plane correlation
            output_filename = path.join(
                avg_folder, "charged_hadron_event_plane_correlation_ALICE.dat")
            calcualte_event_plane_correlations(vn_alice_array, output_filename)
            output_filename = path.join(
                avg_folder, "charged_hadron_event_plane_correlation_ATLAS.dat")
            calcualte_event_plane_correlations(vn_atlas_array, output_filename)

            # calculate three-particle correlations
            output_filename = path.join(avg_folder,
                "{}_three_particle_correlation_ALICE.dat".format(
                    particle_name_list[ipart]))
            calcualte_event_plane_correlations_3sub(
                    vn_alice_array, vn_alice_array_sub1, vn_alice_array_sub2,
                    output_filename)
            output_filename = path.join(avg_folder,
                "{}_three_particle_correlation_ATLAS.dat".format(
                    particle_name_list[ipart]))
            calcualte_event_plane_correlations_3sub(
                    vn_atlas_array, vn_atlas_array_sub1, vn_atlas_array_sub2,
                    output_filename)
            output_filename = path.join(avg_folder,
                "{}_three_particle_correlation_CMS.dat".format(
                    particle_name_list[ipart]))
            calcualte_event_plane_correlations_3sub(
                    vn_cms_array, vn_cms_array_sub1, vn_cms_array_sub2,
                    output_filename)
            output_filename = path.join(avg_folder,
                "{}_three_particle_correlation_PHENIX.dat".format(
                    particle_name_list[ipart]))
            calcualte_event_plane_correlations_3sub(
                    vn_phenix_array, vn_phenix_array_sub1,
                    vn_phenix_array_sub2, output_filename)
            output_filename = path.join(avg_folder,
                "{}_three_particle_correlation_STAR.dat".format(
                    particle_name_list[ipart]))
            calcualte_event_plane_correlations_3sub(
                    vn_star_array, vn_star_array_sub1, vn_star_array_sub2,
                    output_filename)

        # calcualte vn{SP}(pT)
        vn_diff_SP_phenix = calculate_vn_diff_SP(QnpT_diff_phenix,
                                                 Qnref_phenix)
        vn_diff_SP_star = calculate_vn_diff_SP(QnpT_diff_star, Qnref_star)
        vn_diff_SP_alice = calculate_vn_diff_SP(QnpT_diff_alice, Qnref_alice)
        vn_diff_SP_cms = calculate_vn_diff_SP(QnpT_diff_cms, Qnref_cms)
        vn_diff_SP_atlas = calculate_vn_diff_SP(QnpT_diff_atlas, Qnref_atlas)

        if not FastFlag:
            vn4_diff_phenix = calculate_vn4_diff(QnpT_diff_phenix,
                                                 Qnref_phenix)
            vn4_diff_star = calculate_vn4_diff(QnpT_diff_star, Qnref_star)
            vn4_diff_alice = calculate_vn4_diff(QnpT_diff_alice, Qnref_alice)
            vn4_diff_cms = calculate_vn4_diff(QnpT_diff_cms, Qnref_cms)
            vn4_diff_atlas = calculate_vn4_diff(QnpT_diff_atlas, Qnref_atlas)

            # calcualte vn[2](pT)
            vn_diff_2PC, vn_diff_2PC_err = calculate_vn_diff_2PC(
                    vn_diff_2PC_real, vn_diff_2PC_imag, vn_diff_2PC_denorm)
        
        # then particle rapidity distribution
        part_idx = particle_list.index(particle_id)
        p_min = p_min_list[part_idx]
        p_max = p_max_list[part_idx]

        if particle_id == '9999':
            file_name = 'particle_%s_dNdeta_pT_%s_%s.dat' % (particle_id, p_min, p_max)
        else:
            file_name = 'particle_%s_dNdy_pT_%s_%s.dat' % (particle_id, p_min, p_max)

        eta_array = []
        dN_array = []
        vn_array = []
        for ifolder, event_name in enumerate(selected_events_list):
            event_group = hf.get(event_name)
            temp_data = event_group.get(file_name)
            temp_data = nan_to_num(temp_data)

            eta_array.append(temp_data[:, 0])
            dN_array.append(temp_data[:, 1])
            temp_vn_array = []
            for iorder in range(1, n_order):
                vn_real = temp_data[:, 6*iorder-3]
                vn_imag = temp_data[:, 6*iorder-1]
                vn = vn_real + 1j*vn_imag
                temp_vn_array.append(vn)
            vn_array.append(temp_vn_array)

        eta_array = array(eta_array)
        dN_array = array(dN_array)
        vn_array = array(vn_array)

        eta_point = mean(eta_array, 0)
        dNdeta = mean(dN_array, 0)
        dNdeta_err = std(dN_array, 0)/sqrt(nev)
        if RapidityTrigger == 0:
            vn_SP_eta, vn_SP_eta_err = calculate_vn_eta(
                                eta_point, dN_array, vn_array, -3.0, 3.0)
        elif RapidityTrigger == 1:
            vn_SP_eta, vn_SP_eta_err = calculate_vn_eta(
                                eta_point, dN_array, vn_array, -3.9, -3.1)
        elif RapidityTrigger == 2:
            vn_SP_eta, vn_SP_eta_err = calculate_vn_eta(
                                eta_point, dN_array, vn_array, -5.1, -2.8)
        elif RapidityTrigger == 3:
            vn_SP_eta, vn_SP_eta_err = calculate_vn_eta(
                                eta_point, dN_array, vn_array, -4.9, -3.1)
        vn_SP_eta_mid, vn_SP_eta_mid_err = calculate_vn_eta(
                                eta_point, dN_array, vn_array, -0.8, 0.8)

        output_filename = path.join(avg_folder, "{}_rn_eta.dat".format(
                                                    particle_name_list[ipart]))
        calculate_rn_eta(eta_point, dN_array, vn_array, output_filename)

        ######################################################################
        # finally, output all the results
        ######################################################################

        output_filename = ("%s_integrated_observables.dat"
                           % particle_name_list[ipart])
        f = open(path.join(avg_folder, output_filename), 'w')
        f.write("dN/dy= %.5e +/- %.5e\n" % (dN_dy_avg, dN_dy_avg_err))
        if particle_id == "9999":
            f.write("dN/dy(pT>0.2,|eta|<0.8)= %.5e \n" % (dNch_ALICE))
            f.write("dN/dy(pT>0.15,|eta|<0.8)= %.5e \n" % (dNch_ALICE2))
            f.write("dN/dy(pT>0.4,|eta|<2.5)= %.5e \n" % (dNch_ATLAS))
        f.write("<pT>= %.5e +/- %.5e\n" % (mean_pT, mean_pT_err))
        f.write("<pT(>0.15)>= %.5e +/- %.5e\n" % (mean_pT_1, mean_pT_1_err))
        f.write("sigma_pT/<pT>= %.5e +/- %.5e\n"% (sigma_pT, sigma_pT_err))
        for iorder in range(1, n_order):
            f.write("v_%d{2}(phenix)= %.5e +/- %.5e\n"
                    % (iorder, vn_phenix_2[iorder-1],
                       vn_phenix_2_err[iorder-1]))
            f.write("v_%d{2}(STAR)= %.5e +/- %.5e\n"
                    % (iorder, vn_star_2[iorder-1], vn_star_2_err[iorder-1]))
            f.write("v_%d{2}(ALICE)= %.5e +/- %.5e\n"
                    % (iorder, vn_alice_2[iorder-1], vn_alice_2_err[iorder-1]))
            f.write("v_%d{2}(CMS)= %.5e +/- %.5e\n"
                    % (iorder, vn_cms_2[iorder-1], vn_cms_2_err[iorder-1]))
            f.write("v_%d{2}(ATLAS)= %.5e +/- %.5e\n"
                    % (iorder, vn_atlas_2[iorder-1], vn_atlas_2_err[iorder-1]))
        f.close()

        output_filename = ("%s_integrated_observables_with_rapidity_gap.dat"
                           % particle_name_list[ipart])
        f = open(path.join(avg_folder, output_filename), 'w')
        f.write("dN/dy= %.5e +/- %.5e\n" % (dN_dy_avg, dN_dy_avg_err))
        if particle_id == "9999":
            f.write("dN/dy(pT>0.2,|eta|<0.8)= %.5e \n" % (dNch_ALICE))
            f.write("dN/dy(pT>0.15,|eta|<0.8)= %.5e \n" % (dNch_ALICE2))
            f.write("dN/dy(pT>0.4,|eta|<2.5)= %.5e \n" % (dNch_ATLAS))
        f.write("<pT>= %.5e +/- %.5e\n" % (mean_pT, mean_pT_err))
        f.write("<pT(>0.15)>= %.5e +/- %.5e\n" % (mean_pT_1, mean_pT_1_err))
        f.write("<pT(>0.1)>= %.10e +/- %.10e\n" % (mean_pT_2, mean_pT_2_err))
        f.write("<pT(>0.2)>= %.10e +/- %.10e\n" % (mean_pT_3, mean_pT_3_err))
        f.write("<pT(>0.3)>= %.10e +/- %.10e\n" % (mean_pT_4, mean_pT_4_err))
        f.write("sigma_pT/<pT>= %.5e +/- %.5e\n"% (sigma_pT, sigma_pT_err))
        for iorder in range(1, n_order):
            f.write("v_%d{2}(phenix)= %.5e +/- %.5e\n"
                    % (iorder, vn_phenix_2_gap[iorder-1],
                       vn_phenix_2_gap_err[iorder-1]))
            f.write("v_%d{2}(STAR)= %.5e +/- %.5e\n"
                    % (iorder, vn_star_2_gap[iorder-1],
                       vn_star_2_gap_err[iorder-1]))
            f.write("v_%d{2}(ALICE)= %.5e +/- %.5e\n"
                    % (iorder, vn_alice_2_gap[iorder-1],
                       vn_alice_2_gap_err[iorder-1]))
            f.write("v_%d{2}(CMS)= %.5e +/- %.5e\n"
                    % (iorder, vn_cms_2_gap[iorder-1],
                       vn_cms_2_gap_err[iorder-1]))
            f.write("v_%d{2}(ATLAS)= %.5e +/- %.5e\n"
                    % (iorder, vn_atlas_2_gap[iorder-1],
                       vn_atlas_2_gap_err[iorder-1]))
        f.close()

        output_filename = ("%s_differential_observables_PHENIX.dat"
                           % particle_name_list[ipart])
        f = open(path.join(avg_folder, output_filename), 'w')
        f.write("#pT  dN/(2pi dy pT dpT)  dN/(2pi dy pT dpT)_err  "
                "vn{SP}  vn{SP}_err\n")
        for ipT in range(len(pT_spectra)):
            f.write("%.10e  %.10e  %.10e  "
                    % (pT_spectra[ipT], dN_spectra[ipT], dN_spectra_err[ipT]))
            for iorder in range(1, n_order):
                f.write("%.10e  %.10e  " % (vn_diff_SP_phenix[2*iorder-2][ipT],
                                            vn_diff_SP_phenix[2*iorder-1][ipT]))
            f.write("\n")
        f.close()

        output_filename = ("%s_differential_observables_STAR.dat"
                           % particle_name_list[ipart])
        f = open(path.join(avg_folder, output_filename), 'w')
        f.write("#pT  dN/(2pi dy pT dpT)  dN/(2pi dy pT dpT)_err  "
                "vn{SP}  vn{SP}_err\n")
        for ipT in range(len(pT_spectra)):
            f.write("%.10e  %.10e  %.10e  "
                    % (pT_spectra[ipT], dN_spectra[ipT], dN_spectra_err[ipT]))
            for iorder in range(1, n_order):
                f.write("%.10e  %.10e  " % (vn_diff_SP_star[2*iorder-2][ipT],
                                            vn_diff_SP_star[2*iorder-1][ipT]))
            f.write("\n")
        f.close()

        output_filename = ("%s_differential_observables_ALICE.dat"
                           % particle_name_list[ipart])
        f = open(path.join(avg_folder, output_filename), 'w')
        f.write("#pT  dN/(2pi dy pT dpT)  dN/(2pi dy pT dpT)_err  "
                "vn{SP}  vn{SP}_err\n")
        for ipT in range(len(pT_spectra)):
            f.write("%.10e  %.10e  %.10e  "
                    % (pT_spectra[ipT], dN_spectra[ipT], dN_spectra_err[ipT]))
            for iorder in range(1, n_order):
                f.write("%.10e  %.10e  " % (vn_diff_SP_alice[2*iorder-2][ipT],
                                            vn_diff_SP_alice[2*iorder-1][ipT]))
            f.write("\n")
        f.close()

        output_filename = ("%s_differential_observables_CMS.dat"
                           % particle_name_list[ipart])
        f = open(path.join(avg_folder, output_filename), 'w')
        f.write("#pT  dN/(2pi dy pT dpT)  dN/(2pi dy pT dpT)_err  "
                "vn{SP}  vn{SP}_err\n")
        for ipT in range(len(pT_spectra)):
            f.write("%.10e  %.10e  %.10e  "
                    % (pT_spectra[ipT], dN_spectra[ipT], dN_spectra_err[ipT]))
            for iorder in range(1, n_order):
                f.write("%.10e  %.10e  " % (vn_diff_SP_cms[2*iorder-2][ipT],
                                            vn_diff_SP_cms[2*iorder-1][ipT]))
            f.write("\n")
        f.close()

        output_filename = ("%s_differential_observables_ATLAS.dat"
                           % particle_name_list[ipart])
        f = open(path.join(avg_folder, output_filename), 'w')
        f.write("#pT  dN/(2pi dy pT dpT)  dN/(2pi dy pT dpT)_err  "
                "vn{SP}  vn{SP}_err\n")
        for ipT in range(len(pT_spectra)):
            f.write("%.10e  %.10e  %.10e  "
                    % (pT_spectra[ipT], dN_spectra[ipT], dN_spectra_err[ipT]))
            for iorder in range(1, n_order):
                f.write("%.10e  %.10e  " % (vn_diff_SP_atlas[2*iorder-2][ipT],
                                            vn_diff_SP_atlas[2*iorder-1][ipT]))
            f.write("\n")
        f.close()

        if not FastFlag:
            output_filename = ("%s_differential_observables_2PC.dat"
                               % particle_name_list[ipart])
            f = open(path.join(avg_folder, output_filename), 'w')
            f.write("#pT  dN/(2pi dy pT dpT)  dN/(2pi dy pT dpT)_err  "
                    "vn[2]  vn[2]_err\n")
            for ipT in range(len(pT_spectra)):
                f.write("%.10e  %.10e  %.10e  "
                        % (pT_spectra[ipT], dN_spectra[ipT], dN_spectra_err[ipT]))
                for iorder in range(1, n_order):
                    f.write("%.10e  %.10e  " % (vn_diff_2PC[iorder-1, ipT],
                                                vn_diff_2PC_err[iorder-1, ipT]))
                f.write("\n")
            f.close()

            # output vn{4}(pT)
            output_filename = (
                    "%s_differential_observables_4particle_PHENIX.dat"
                               % particle_name_list[ipart])
            f = open(path.join(avg_folder, output_filename), 'w')
            f.write("#pT  vn{4}  vn{4}_err\n")
            for ipT in range(len(pT_spectra)):
                f.write("%.10e  " % (pT_spectra[ipT]))
                for iorder in range(1, 4):
                    f.write("%.10e  %.10e  " % (
                        vn4_diff_phenix[2*iorder-2][ipT],
                        vn4_diff_phenix[2*iorder-1][ipT]))
                f.write("\n")
            f.close()

            output_filename = (
                    "%s_differential_observables_4particle_STAR.dat"
                               % particle_name_list[ipart])
            f = open(path.join(avg_folder, output_filename), 'w')
            f.write("#pT  vn{4}  vn{4}_err\n")
            for ipT in range(len(pT_spectra)):
                f.write("%.10e  " % (pT_spectra[ipT]))
                for iorder in range(1, 4):
                    f.write("%.10e  %.10e  " % (
                        vn4_diff_star[2*iorder-2][ipT],
                        vn4_diff_star[2*iorder-1][ipT]))
                f.write("\n")
            f.close()

            output_filename = (
                    "%s_differential_observables_4particle_ALICE.dat"
                               % particle_name_list[ipart])
            f = open(path.join(avg_folder, output_filename), 'w')
            f.write("#pT  vn{4}  vn{4}_err\n")
            for ipT in range(len(pT_spectra)):
                f.write("%.10e  " % (pT_spectra[ipT]))
                for iorder in range(1, 4):
                    f.write("%.10e  %.10e  " % (
                        vn4_diff_alice[2*iorder-2][ipT],
                        vn4_diff_alice[2*iorder-1][ipT]))
                f.write("\n")
            f.close()

            output_filename = ("%s_differential_observables_4particle_CMS.dat"
                               % particle_name_list[ipart])
            f = open(path.join(avg_folder, output_filename), 'w')
            f.write("#pT  vn{4}  vn{4}_err\n")
            for ipT in range(len(pT_spectra)):
                f.write("%.10e  " % (pT_spectra[ipT]))
                for iorder in range(1, 4):
                    f.write("%.10e  %.10e  " % (vn4_diff_cms[2*iorder-2][ipT],
                                                vn4_diff_cms[2*iorder-1][ipT]))
                f.write("\n")
            f.close()

            output_filename = (
                    "%s_differential_observables_4particle_ATLAS.dat"
                               % particle_name_list[ipart])
            f = open(path.join(avg_folder, output_filename), 'w')
            f.write("#pT  vn{4}  vn{4}_err\n")
            for ipT in range(len(pT_spectra)):
                f.write("%.10e  " % (pT_spectra[ipT]))
                for iorder in range(1, 4):
                    f.write("%.10e  %.10e  " % (
                        vn4_diff_atlas[2*iorder-2][ipT],
                        vn4_diff_atlas[2*iorder-1][ipT]))
                f.write("\n")
            f.close()

        output_filename = "{}_rapidity_distribution.dat".format(
                                                    particle_name_list[ipart])
        f = open(path.join(avg_folder, output_filename), 'w')
        if(particle_id == '9999'):
            f.write("#eta  dN/deta  dN/deta_err  vn{2}(eta)  vn{2}(eta)_err"
                    + "  Re{vn}(eta) Re{vn}(eta)_err\n")
        else:
            f.write("#y  dN/dy  dN/dy_err  vn{2}(y)  vn{2}(y)_err  "
                    + "Re{vn}(y)  Re{vn}(y)_err\n")
        for ieta in range(len(eta_point)):
            f.write("%.10e  %.10e  %.10e  "
                    % (eta_point[ieta], dNdeta[ieta], dNdeta_err[ieta]))
            for iorder in range(1, n_order):
                f.write("%.10e  %.10e  %.10e  %.10e  "
                        % (vn_SP_eta[iorder-1, ieta],
                           vn_SP_eta_err[iorder-1, ieta],
                           vn_SP_eta_mid[iorder-1, ieta],
                           vn_SP_eta_mid_err[iorder-1, ieta]))
            f.write("\n")
        f.close()

        if particle_id == '9999' and not FastFlag:
            # output rn ratios
            pT_trig = ['1.0', '1.5', '2.0', '2.5', '3.0']
            ipTtrig = 0
            output_filename = ("%s_rn_ratios_CMS_pTtrig_%s_%s.dat"
                               % (particle_name_list[ipart],
                                  pT_trig[ipTtrig], pT_trig[ipTtrig+1]))
            f = open(path.join(avg_folder, output_filename), 'w')
            f.write("#pT_mid  rn  rn_err (n = 2, 3, 4)\n")
            for ipT in range(len(rn_cms[0, :, 0])):
                for iorder in range(len(rn_cms[:, 0, 0])):
                    f.write("%.5e  %.5e  %.5e  "
                            % (rn_cms[iorder, ipT, 0],
                               rn_cms[iorder, ipT, 1],
                               rn_cms[iorder, ipT, 2]))
                f.write("\n")
                if rn_cms[0, ipT, 0] == 0.0:
                    f.close()
                    ipTtrig += 1
                    if ipTtrig < (len(pT_trig) - 1):
                        output_filename = ("%s_rn_ratios_CMS_pTtrig_%s_%s.dat"
                                           % (particle_name_list[ipart],
                                              pT_trig[ipTtrig],
                                              pT_trig[ipTtrig+1]))
                        f = open(path.join(avg_folder, output_filename), 'w')
                        f.write("#pT_mid  rn  rn_err (n = 2, 3, 4)\n")

print("Analysis is done.")

