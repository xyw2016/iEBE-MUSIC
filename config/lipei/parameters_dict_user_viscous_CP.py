#!/usr/bin/env python3
"""
    This script contains all the user modified parameters in
    the iEBE-MUSIC package.
"""


# control parameters
control_dict = {
    'initial_state_type': "3DMCGlauber_consttau",
    'walltime': "6:00:00",         # walltime to run
    'save_hydro_surfaces': True,    # flag to save hydro surfaces
    'save_UrQMD_files': False,       # flag to save UrQMD files
}


# 3DMCGlauber model
mcglauber_dict = {
    'database_name': "3DMCGlauber_database/MCGlbAuAu19.6",  # path for initial conditions
}


# MUSIC
music_dict = {
    'Initial_profile': 11,      # type of initial condition (11 or 111)
                                # 3dMCGlauber smooth initial condition based on
                                # the nuclear thickness funciton TA and TB
    'Initial_TA_Distribution_Filename': 'initial/initial_TA.dat',
    'Initial_TB_Distribution_Filename': 'initial/initial_TB.dat',
    'Initial_rhob_TA_Distribution_Filename': 'initial/initial_TA.dat',
    'Initial_rhob_TB_Distribution_Filename': 'initial/initial_TB.dat',

    # parameters for the eta profiles in entropy density and net baryon density
    'ecm': 19.6,                    # collision energy
    'Eta_plateau_size': 3.0,        # [-Eta_plateau_size/2, Eta_plateau_size/2] for entropy density
    'Eta_fall_off': 0.3,            # Gaussian width fall off for entropy density
    'eta_rhob_0': 1.40,              # peak position of the net baryon density
    'eta_rhob_width_1': 0.1,        # Gaussian width for |eta| > |eta_0|
    'eta_rhob_width_2': 0.75,        # Gaussian width for |eta| < |eta_0|
    
    'yL_frac': 0.5,
    'initial_eta_profile': 1, # Hirano + Gaussian fall-off
    'initialize_with_entropy': 1, # initialize entropy
    's_factor': 7.0,

    'Initial_time_tau_0': 1.5,      # starting time of the hydrodynamic evolution (fm/c)
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
    'EOS_to_use': 12,               # type of the equation of state
                                    # 14: neos_BQS lattice EoS at finite mu_B
                                    # 17: BEST lattice EoS at finite mu_B
    # transport coefficients
    'Viscosity_Flag_Yes_1_No_0': 1,        # turn on viscosity in the evolution
    'Include_Shear_Visc_Yes_1_No_0': 1,    # include shear viscous effect
    'Shear_to_S_ratio': 0.06,              # value of \eta/s
    'T_dependent_Shear_to_S_ratio': 1,     # flag to use temperature dep. \eta/s(T)
    'Include_Bulk_Visc_Yes_1_No_0': 1,     # include bulk viscous effect
    'T_dependent_Bulk_to_S_ratio': 1,      # 1. default, 2. duke, 3. sims
    'Include_second_order_terms': 1,       # include second order non-linear coupling terms
    'Include_vorticity_terms': 0,          # include vorticity coupling terms
    'Include_Rhob_Yes_1_No_0': 1,
    'turn_on_baryon_diffusion': 1,
    'kappa_coefficient': 0.4,

    # parameters for freeze out and Cooper-Frye
    'use_eps_for_freeze_out': 1,
    'N_freeze_out': 1,
    'eps_freeze_max': 0.4,
    'eps_freeze_min': 0.4,

    # switches to output evolution information
    'output_hydro_debug_info': 0,   # flag to output debug information
    'output_evolution_data': 2,     # flag to output evolution history to file
    'output_movie_flag': 0,
    'output_evolution_T_cut': 0.145,
    'outputBinaryEvolution': 1,     # output evolution file in binary format
    'output_evolution_every_N_eta': 2,  # output evolution file every Neta steps
    'output_evolution_every_N_x':  5,   # output evolution file every Nx steps
    'output_evolution_every_N_y': 5,    # output evolution file every Ny steps
    'output_evolution_every_N_timesteps':50,  # output evolution every Ntime steps
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
}


# hadronic afterburner toolkit
hadronic_afterburner_toolkit_dict = {
    'event_buffer_size': 100000,        # the number of events read in at once
    'compute_correlation': 0,           # flag to compute correlation function
    'flag_charge_dependence': 0,        # flag to compute charge dependence correlation
    'compute_corr_rap_dep': 0,      # flag to compute the rapidity dependent multi-particle correlation
    'resonance_weak_feed_down_flag': 0,     # include weak feed down contribution
}
