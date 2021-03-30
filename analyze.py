import sys
import os
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.serialize import *
from mrnet.stochastic.analyze import *

if len(sys.argv) != 2:
    print("usage: python serialize.py json_file")
    quit()

molecule_entries = loadfn(sys.argv[2])

ledc_mol_entry  = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/LEDC.xyz',
    0)

a0 = load_analysis("./runs/network_0")
a1 = load_analysis("./runs/network_1")
a2 = load_analysis("./runs/network_2")
a3 = load_analysis("./runs/network_3")

a0.generate_pathway_report(ledc_mol_entry, 100)
a1.generate_pathway_report(ledc_mol_entry, 100)
a2.generate_pathway_report(ledc_mol_entry, 100)
a3.generate_pathway_report(ledc_mol_entry, 100)
