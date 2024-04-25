#!/usr/bin/env python3
"""
    This script contains all the user modified parameters in
    the iEBE-MUSIC package.
"""

# control parameters
control_dict = {
    'initial_state_type': "IPGlasma",
    'walltime': "6:00:00",  # walltime to run
    'use_iS3D': False,               # flag to use iS3D as sampler
    'save_ipglasma_results': True,   # flag to save ipglasma results
    'save_kompost_results': False,   # flag to save kompost results
    'save_hydro_surfaces': True,   # flag to save hydro surfaces
    'save_UrQMD_files': True,      # flag to save UrQMD files
}


# IPGlasma
ipglasma_dict = {
    'type': "self",
    # all parameters below are for (type == self)
    'size': 700,            # number of grid points of IP-Glasma computation
    'L': 28.,               # grid size in the transverse plane
    'bmin': 7.2353,
    'bmax': 10.247,
    'Projectile': "Pb",
    'Target': "Pb",
    'roots': 2760.,
    'SigmaNN': 64.,
    'setWSDeformParams': 1,
    'R_WS': 6.62,
    'a_WS': 0.546,
    'beta2': 0.0,
    'beta3': 0.0,
    'beta4': 0.0,
    'gamma': 0.82,
    'd_min':0.9,
    'maxtime':0.4,
    'LOutput': 34,
    'sizeOutput': 512,
    'useConstituentQuarkProton': 3,   # 0: round proton; 3: fluctuating proton
}


# KoMPoST
kompost_dict = {
    'KoMPoSTInputs': {
        'tIn': 0.1,
        'tOut': 0.8,
    },
    'KoMPoSTParameters': {
        'EtaOverS': 0.12,                   # specific shear viscosity
    },
    'EventInput': {
        'normFactor': 0.235,    # Tmunu is normalized by this factor after being read in
        'afm': 0.0664062,       # lattice spacing in fm
        'Ns': 512,              # number of grid points on a square lattice
        'xSTART': 0,            # The first grid point to include in the x direction
        'xEND': 511,            # The last grid point to include in the x direction
        'ySTART': 0,            # The first grid point to include in the y direction
        'yEND': 511,            # The last grid point to include in the y direction
    },
}


# MUSIC
music_dict = {
    'Initial_profile': 9,   # type of initial condition 
                            # 9: IPGlasma (full Tmunu),
                            #   -- 91: e and u^\mu,
                            #   -- 92: e only,
                            #   -- 93: e, u^\mu, and pi^\munu
    's_factor': 0.235,        # normalization factor read in initial data file
    'Initial_time_tau_0': 0.4,  # starting time of the hydrodynamic evolution (fm/c)
    'Delta_Tau': 0.005,         # time step to use in the evolution [fm/c]
    'boost_invariant':  1,      # whether the simulation is boost-invariant
    'EOS_to_use': 9,            # type of the equation of state
                                # 9: hotQCD EOS with UrQMD
    # transport coefficients
    'quest_revert_strength': 1.0,          # the strength of the viscous regulation
    'Viscosity_Flag_Yes_1_No_0': 1,        # turn on viscosity in the evolution
    'Include_Shear_Visc_Yes_1_No_0': 1,    # include shear viscous effect
    'Shear_to_S_ratio': 0.12,              # value of \eta/s
    'T_dependent_Shear_to_S_ratio': 0,     # flag to use temperature dep. \eta/s(T)
    'Include_Bulk_Visc_Yes_1_No_0': 1,     # include bulk viscous effect
    'T_dependent_zeta_over_s': 8,          # parameterization of \zeta/s(T)
    'Include_second_order_terms': 1,       # include second order non-linear coupling terms
    'Include_vorticity_terms': 0,          # include vorticity coupling terms

    'output_evolution_data': 2,     # flag to output evolution history to file
    'output_evolution_T_cut': 0.13,
    'outputBinaryEvolution': 1,     # output evolution file in binary format
    'output_evolution_every_N_eta': 1,  # output evolution file every Neta steps
    'output_evolution_every_N_x':  1,   # output evolution file every Nx steps
    'output_evolution_every_N_y': 1,    # output evolution file every Ny steps
    'output_evolution_every_N_timesteps':40,  # output evolution every Ntime steps
    
    # parameters for freeze out and Cooper-Frye
    'N_freeze_out': 1,
    'eps_freeze_max': 0.18,
    'eps_freeze_min': 0.18,
}


# iSS
iss_dict = {
    'hydro_mode': 2,    # mode for reading in freeze out information 
    'MC_sampling': 2, # 0/1/2/3: whether to perform Monte-Carlo sampling
    'store_samples_in_memory': 1,    # flag to store particle samples in memory
    'include_deltaf_shear': 1,      # include delta f contribution from shear
    'include_deltaf_bulk': 1,       # include delta f contribution from bulk
    'sample_upto_desired_particle_number': 1,  # 1: flag to run sampling until desired
                                               # particle numbers is reached
    'number_of_particles_needed': 5000,      # number of hadrons to sample
    'local_charge_conservation': 0,  # flag to impose local charge conservation
    'global_momentum_conservation': 0,  # flag to impose GMC
}

# iS3D
is3d_dict = {
    'operation': 1,                   # determines what iS3D calculates
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

    'hrg_eos': 1,                     # determines what PDG file to read in (chosen particles must be subset of selected PDG!)
                                      #   1 = urqmd v3.3+     (goes up to n-2250)
                                      #   2 = smash           (goes up to Υ(3S))
                                      #   3 = smash box       (smash box: no decay info now, so can't do resdecays)   (what is this?)

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
    'include_shear_deltaf': 0,        # switch to include shear viscous corrections (or residual shear for vah)
    'include_baryondiff_deltaf': 1,   # switch to include baryon diffusion corrections

    'oversample': 1,                  # run sampler iteratively until mininum number of hadrons
                                      # or max number of events sampled

    'fast': 0,                        # switch to run sampler in fast mode
                                      # compute thermal density for (T_avg, muB_avg) rather than (T, muB) for each cell
                                      # assumes (T,muB) throughout surface are very close to (T_avg, muB_avg)
                                      # turn off if you have corona cells

    'min_num_hadrons': 1.0e+7,        # across all samples >= min_num_hadrons
    'max_num_samples': 1.0e+3,        # oversampling will finish after this number of samples

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

# urqmd afterburner
urqmd_dict = {
    'run_collisionless': 0,         # flag to run afterburner without collisions
}


# hadronic afterburner toolkit
hadronic_afterburner_toolkit_dict = {
    'event_buffer_size': 100000,       # the number of events read in at once
    'compute_correlation': 0,       # flag to compute correlation function
    'flag_charge_dependence': 0,    # flag to compute charge dependence correlation
    'compute_corr_rap_dep': 0,      # flag to compute the rapidity dependent multi-particle correlation
    'resonance_weak_feed_down_flag': 0,  # include weak feed down contribution
}
