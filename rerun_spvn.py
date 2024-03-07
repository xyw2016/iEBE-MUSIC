#!/usr/bin/env python3

import sys
import os
from os import path, mkdir,chdir,makedirs
import shutil
import subprocess
import argparse
from math import ceil
from glob import glob
import h5py
import numpy as np
def create_a_working_folder(workfolder_path):
    try:
        mkdir(workfolder_path)
    except FileExistsError:
        print("The folder {} exists, do you want to delete it?".format(
            workfolder_path))
        user_answer = input()
        if 'y' in user_answer:
            shutil.rmtree(workfolder_path)
            mkdir(workfolder_path)
        else:
            print("bye~\n")
            exit(0)

def main(spvn_path,results_path):

    cwd=path.abspath("./")

    create_a_working_folder(results_path)
    subprocess.call("cp -r {0:s} {1:s}".format(path.join(cwd,"codes/hadronic_afterburner_toolkit_code"),results_path),shell=True)
    
    
    run_folder = path.join(results_path,"hadronic_afterburner_toolkit_code")
    chdir(run_folder)
    
    urqmd_events = glob(path.join(spvn_path,"*.gz"))
    total_evt = len(urqmd_events)
    nnn =0
    for iurqmd_path in urqmd_events:
        event_id = iurqmd_path.split("/")[-1].split(".")[0].split("_")[-1]
        print(nnn/total_evt)
        nnn=nnn+1
        #print(event_id,iurqmd_path)
        final_results_folder = path.join(results_path,"spvn_results_{0:s}".format(event_id))
        
        if path.exists(final_results_folder):
            shutil.rmtree(final_results_folder)
        
        spvn_folder = path.abspath("./results")
    
        if path.exists(spvn_folder):
            shutil.rmtree(spvn_folder)
        makedirs(spvn_folder)

        subprocess.call("ln -s {0:s} {1:s}".format(iurqmd_path,path.join(spvn_folder,"particle_list.dat")),shell=True)
        
        subprocess.call("./hadronic_afterburner_tools.e analyze_HBT=0", shell=True)
        subprocess.call("rm {}/particle_list.dat".format(spvn_folder), shell=True)
        shutil.move(spvn_folder,final_results_folder)

        chdir(final_results_folder)
        
        results_name = "spvn_results_{0:s}".format(event_id)
        hf = h5py.File("{0}.h5".format(results_name), "w")
        gtemp = hf.create_group("{0}".format(results_name))
        
        file_list = glob(path.abspath("./*.dat"))
        for file_path in file_list:
            print (file_path)
            file_name = file_path.split("/")[-1]
            dtemp = np.loadtxt(file_path)
            h5data = gtemp.create_dataset("{0}".format(file_name),
                                          data=dtemp,
                                          compression="gzip",
                                          compression_opts=9)
            # save header
            ftemp = open(file_path, "r")
            header_text = str(ftemp.readline())
            ftemp.close()
            if header_text.startswith("#"):
                h5data.attrs.create("header", np.string_(header_text))
        hf.close()
        
        shutil.move("{}.h5".format(results_name), results_path)
        chdir(run_folder)
        shutil.rmtree(final_results_folder, ignore_errors=True)

    

    chdir(cwd)
    
def make_spvn_h5(results_path):
    
    spvn_file_list = glob(path.join(results_path,"spvn_results_*"))
    for ispvn_path in spvn_file_list:
        print (ispvn_path)




if __name__ == "__main__":
    
    spvn_path=path.abspath(sys.argv[1])
    results_path=path.abspath(sys.argv[2])
    if len(sys.argv) != 3:
        print ("Useage: python *.py spvn_path results_path")
    main(spvn_path,results_path)
    #make_spvn_h5(results_path)
