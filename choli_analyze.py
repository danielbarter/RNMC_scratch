import sys
import os
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.serialize import *
from mrnet.stochastic.analyze import *
from mrnet.core.mol_entry import *

if len(sys.argv) != 3:
    print("usage: python analyze.py json_file network_folder")
    quit()

choli = loadfn(sys.argv[1])
network_folder = sys.argv[2]
molecule_entries = [MoleculeEntry.from_dataset_entry(e) for e in choli if e["formula_alphabetical"] != "Li1" or e["charge"] == 1]

Li_plus_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/Li.xyz',
    1)
EC_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/EC.xyz',
    0)
LEDC_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/LEDC.xyz',
    0)
EMC_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/EMC.xyz',
    0)


entries_box = EntriesBox(molecule_entries)
sa = SimulationAnalyzer(network_folder, entries_box)
sa.generate_sink_report()
