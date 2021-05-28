import sys
import os
sys.path.append('./RNMC/mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.serialize import *
from mrnet.stochastic.analyze import *
from mrnet.core.mol_entry import *

if len(sys.argv) != 4:
    print("usage: python serialize.py json_file network params")
    quit()

choli = loadfn(sys.argv[1])
network_folder = sys.argv[2]
params_folder = sys.argv[3]
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

initial_state_data = [
    (Li_plus_mol_entry, 500),
    (EC_mol_entry, 500),
    (EMC_mol_entry, 500)
]

entries_box = EntriesBox(molecule_entries)
reaction_generator = ReactionIterator(
    entries_box,
    electron_free_energy=-1.4,
    single_elem_interm_ignore=["C1", "P1", "F1"],
    filter_concerted_metal_coordination=True
)
SerializeNetwork(network_folder,reaction_generator, shard_size=2000000)
serialize_initial_state(network_folder, entries_box, initial_state_data)
serialize_simulation_parameters(params_folder, number_of_threads=20, step_cutoff=5000, number_of_simulations = 10000)
