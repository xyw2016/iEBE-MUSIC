#!/usr/bin/env python3
"""
    This script contains all the user modified parameters in
    the iEBE-MUSIC package.
"""


# control parameters
control_dict = {
    'initial_state_type': "SMASH_initial",
    'walltime': "8:30:00",          # walltime to run
    'use_iS3D': True,               # flag to use iS3D as sampler
    'use_SMASH_afterburner': True,    # flag to use SMASH as afterburner
    'save_ipglasma_results': False,   # flag to save IPGlasma results
    'save_kompost_results': False,    # flag to save kompost results
    'save_smashini_results': True,   # flag to save smash initial results
    'save_hydro_surfaces': True,     # flag to save hydro surfaces
    'save_UrQMD_files': False,        # flag to save UrQMD files
}


# SMASH initial condition
smashini_dict =  {
    'database_name_pattern': 'self',  # "SMASH_database/SMASH_7.7",
    'use_averaged_smash': False,       # average over smash events to construct initial condition
    'default': 'INFO',
    'Modus': 'Collider',
    'Time_Step_Mode': 'Fixed',
    'Delta_Time': 0.1,
    'End_Time': 2000.0,
    'Proper_Time': 3.2,
    'Randomseed': -1,
    'Nevents': 50,
    'Output_Interval': 10.0,
    'Format': 'Oscar2013',
    'E_Kin': 1.23,
    'Fermi_Motion': 'frozen',
    'b_min': 0.0228994, 
    'b_max': 3.37646,
    'ecm': 7.7,
}

part2s_dict = {
    'PATHIN':   'input/SMASH_ini.binary',
    'PATHOUT':  './',

    'NX':   101,
    'NY':   101,
    'NETA': 101,

    'DX':   0.3,
    'DY':   0.3,
    'DETA': 0.3,


    'SIGR':  0.6,
    'SIGETA': 0.6,

    'TAU00': 0.0,
    'TAU0' : 3.2,
    'NTAU' : 10,
    'EOS_ID' : 12,

    'read_binary': 1,

}

# MUSIC
music_dict = {
    'Initial_profile': 21,      # type of initial condition (11 or 111)
                                # 3dMCGlauber smooth initial condition based on
                                # the nuclear thickness funciton TA and TB
    'Initial_TA_Distribution_Filename': 'initial/initial_TA.dat',
    'Initial_TB_Distribution_Filename': 'initial/initial_TB.dat',
    'Initial_rhob_TA_Distribution_Filename': 'initial/initial_TA.dat',
    'Initial_rhob_TB_Distribution_Filename': 'initial/initial_TB.dat',

    # parameters for the eta profiles in entropy density and net baryon density
    'ecm': 7.7,                    # collision energy
    'Eta_plateau_size': 1.5,        # [-Eta_plateau_size/2, Eta_plateau_size/2] for entropy density
    'Eta_fall_off': 0.17,            # Gaussian width fall off for entropy density

    'initial_eta_profile': 1, # Hirano + Gaussian fall-off
    'initialize_with_entropy': 1, # initialize entropy
    's_factor': 2.44,
    'e_Norm': 1.0,

    'rhob_Norm': 1.22,
    'eta_rhob_0': 1.28,              # peak position of the net baryon density
    'eta_rhob_width_1': 0.07,        # Gaussian width for |eta| > |eta_0|
    'eta_rhob_width_2': 0.75,        # Gaussian width for |eta| < |eta_0|
    
    'Initial_time_tau_0': 3.6,      # starting time of the hydrodynamic evolution (fm/c)
                                    # max(tau_overlap, tau_0)
    'Delta_Tau': 0.010,             # time step to use in the evolution [fm/c]
    'boost_invariant':  0,          # whether the simulation is boost-invariant
    'Eta_grid_size': 10.0,          # spatial rapidity range 
                                    # [-Eta_grid_size/2, Eta_grid_size/2 - delta_eta]
    'Grid_size_in_eta': 64,         # number of the grid points in spatial rapidity direction
    'X_grid_size_in_fm': 26.0,      # spatial range along x direction in the transverse plane
                                    # [-X_grid_size_in_fm/2, X_grid_size_in_fm/2]
    'Y_grid_size_in_fm': 26.0,      # spatial range along x direction in the transverse plane
                                    # [-X_grid_size_in_fm/2, X_grid_size_in_fm/2]
    'Grid_size_in_x': 261,          # number of the grid points in x direction
    'Grid_size_in_y': 261,          # number of the grid points in y direction
    'EOS_to_use': 14,               # type of the equation of state
                                    # 14: neos_BQS lattice EoS at finite mu_B
                                    # 17: BEST lattice EoS at finite mu_B
    # transport coefficients
    'Viscosity_Flag_Yes_1_No_0': 1,        # turn on viscosity in the evolution
    'Include_Shear_Visc_Yes_1_No_0': 1,    # include shear viscous effect
    'Shear_to_S_ratio': 0.1,               # value of \eta/s
    'T_dependent_Shear_to_S_ratio': 0,     # flag to use temperature dep. \eta/s(T)
    'Include_Bulk_Visc_Yes_1_No_0': 0,     # include bulk viscous effect
    'Include_second_order_terms': 1,       # include second order non-linear coupling terms
    'Include_vorticity_terms': 0,          # include vorticity coupling terms
    'Include_Rhob_Yes_1_No_0': 1,
    'turn_on_baryon_diffusion': 1,
    'kappa_coefficient': 0.3,

    # parameters for freeze out and Cooper-Frye
    'Do_FreezeOut_lowtemp': 1,              # flag to include cold corona
    'use_eps_for_freeze_out': 1,
    'N_freeze_out': 1,
    'eps_freeze_max': 0.35,
    'eps_freeze_min': 0.35,

    # switches to output evolution information
    'output_hydro_debug_info': 0,   # flag to output debug information
    'output_evolution_data': 0,     # flag to output evolution history to file
    'output_movie_flag': 0,
    'output_evolution_T_cut': 0.145,
    'outputBinaryEvolution': 1,     # output evolution file in binary format
    'output_evolution_every_N_eta': 1,  # output evolution file every Neta steps
    'output_evolution_every_N_x':  4,   # output evolution file every Nx steps
    'output_evolution_every_N_y': 4,    # output evolution file every Ny steps
    'output_evolution_every_N_timesteps':5,  # output evolution every Ntime steps
    'output_initial_density_profiles': 0,
}


# iSS
iss_dict = {
    'hydro_mode': 2,                # mode for reading in freeze out information
                                    # 2: read in 3D hydro surface
    'include_deltaf_shear': 1,      # include delta f contribution from shear
    'include_deltaf_bulk': 0,       # include delta f contribution from bulk
    'include_deltaf_diffusion': 1,  # include delta f contribution from diffusion
    'sample_upto_desired_particle_number': 1,  # 1: flag to run sampling until desired
                                               # particle numbers is reached
    'number_of_particles_needed': 100000,      # number of hadrons to sample
    'local_charge_conservation': 0,     # flag to impose local charge conservation
    'global_momentum_conservation': 0,  # flag to impose GMC
    'MC_sampling': 4,
    'calculate_vn': 0,
}

# iS3D
is3d_dict = {
    'operation': 2,                   # determines what iS3D calculates
                                      #   0 = mean spacetime distribution dN/dX
                                      #   1 = smooth momentum spectra dN/pTdpTdphidy
                                      #   2 = sampled particle list (test_sampler = 0) or discrete spacetime/momentum distrbutions (test_sampler = 1)

    'mode': 8,                        # file format of surface.dat to read in (your surface needs to match the correct format!)
                                      #   1 = CPU VH or CPU VAH           (3+1d vh or vah)
                                      #   5 = CPU VH w/ thermal vorticity (3+1d vh)
                                      #   6 = MUSIC (public version)      (3+1d vh)
                                      #   7 = HIC-EventGen                (2+1d vh)
                                      #   8 = MUSIC with baryon           (3+1d vh)

    'surface_in_binary': 1,           # freeze-out surface in binary format for mode = 8

    'only_use_partial_surface': 0,    # for example only interested in cells near mid-rapidity
    'partial_surface_etas_min': -0.05,
    'partial_surface_etas_max': 0.05,
    'partial_surface_tau_min': 0.0,
    'partial_surface_tau_max': 2.05,

    'hrg_eos': 2,                     # determines what PDG file to read in (chosen particles must be subset of selected PDG!)
                                      #   1 = urqmd v3.3+     (goes up to n-2250)
                                      #   2 = smash           (goes up to Υ(3S))
                                      #   3 = smash box       (smash box: no decay info now, so can't do resdecays)   (what is this?)

    'afterburner_type': 2,            #   1 = urqmd
                                      #   2 = smash                               
    'dimension': 3,                   # dimensionality of the freezeout surface
                                      #   2 = boost-invariant 2+1d
                                      #   3 = non boost-invariant 3+1d

    'df_mode': 2,                     # df correction method
                                      #   1 = Grad 14-moment approximation            (vh)
                                      #   2 = RTA Chapman-Enskog expansion            (vh)
                                      #   3 = PTM modified equilibrium distribution   (vh)
                                      #   4 = PTB modified equilibrium distribution   (vh)
                                      #   5 = Grad 14-moment approximation            (vah)
                                      #   6 = RTA Chapman-Enskog expansion            (vah)
                                      #   7 = PTM modified anisotropic distribution   (vah)

    'include_baryon': 1,              # switch to include baryon chemical potential
    'include_bulk_deltaf': 0,         # switch to include bulk viscous corrections
    'include_shear_deltaf': 1,        # switch to include shear viscous corrections (or residual shear for vah)
    'include_baryondiff_deltaf': 1,   # switch to include baryon diffusion corrections

    'oversample': 1,                  # run sampler iteratively until mininum number of hadrons
                                      # or max number of events sampled

    'fast': 0,                        # switch to run sampler in fast mode
                                      # compute thermal density for (T_avg, muB_avg) rather than (T, muB) for each cell
                                      # assumes (T,muB) throughout surface are very close to (T_avg, muB_avg)
                                      # turn off if you have corona cells

    'min_num_hadrons': 1.0e+7,        # across all samples >= min_num_hadrons
    'max_num_samples': 1.0e+3,        # oversampling will finish after this number of samples
    'fix_oversample_num_flag': 1,     # switch to specify the number of samples (SMASH needs to know Nevents)
    'oversample_num':   1000,       # oversampling will finish after this number of samples (Nevents for SMASH afterburner)

    'sampler_seed': -1,                # sets seed of particle sampler. If sampler_seed < 0, seed is set using clocktime

    'test_sampler': 0,                # perform sampler test only (i.e. write sampled pT spectra and vn to file only)
                                      # set to zero for actual runs

    'pT_min': 0.0,                    # pT min in GeV (for sampler tests)
    'pT_max': 3.0,                    # pT max in GeV
    'pT_bins': 100,                   # number of pT bins

    'y_bins': 100,                    # number of rapidity bins

    'eta_cut': 7.0,                   # spacetime rapidity cut: |eta| <= eta_cut (should be 2 units > y_cut)
    'eta_bins': 140,                  # number of eta bins

    'do_resonance_decays': 0,         # switch for resonance decays after thermal spectra calculation (not finished)
    'lightest_particle': 111,         # PDG MC ID of lightest particle for resonance decay feed-down

}

urqmd_dict = {
    'run_collisionless': 0,         # flag to run afterburner without collisions
}

smash_dict =  {
    'default': 'INFO',
    'Modus': 'List',
    'Time_Step_Mode': 'None',
    'Delta_Time': 0.1,
    'End_Time': 5000.0,                 
    'Randomseed': -1,
    'Nevents': 1,                     # overwritten by 'oversample_num' in iS3D
    'Output_Interval': 10.0,
    'Format': 'Oscar2013',
    'File_Directory': "./",
    'File_Prefix': "particle_list_osc",
    'Shift_Id': 0,
    'Extended': 'True',
}


# hadronic afterburner toolkit
hadronic_afterburner_toolkit_dict = {
    'event_buffer_size': 100000,        # the number of events read in at once
    'compute_correlation': 0,           # flag to compute correlation function
    'flag_charge_dependence': 0,        # flag to compute charge dependence correlation
    'compute_corr_rap_dep': 0,      # flag to compute the rapidity dependent multi-particle correlation
    'resonance_weak_feed_down_flag': 1,     # include weak feed down contribution
}
