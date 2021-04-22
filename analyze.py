import sys
import os
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.serialize import *
from mrnet.stochastic.analyze import *

from multiprocessing import Pool

if len(sys.argv) != 3:
    print("usage: python analyze.py json_file network_folder")
    quit()

molecule_entries = loadfn(sys.argv[1])
network_folder = sys.argv[2]


# 3797
ledc_mol_entry  = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/LEDC.xyz',
    0)


sa = SimulationAnalyzer(network_folder, molecule_entries)
sa.generate_simulation_history_report(3727)
sa.generate_reaction_tally_report()
sa.generate_pathway_report(ledc_mol_entry, 10)
sa.generate_consumption_report(ledc_mol_entry)
