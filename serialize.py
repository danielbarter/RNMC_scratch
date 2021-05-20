import sys
import os
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.serialize import *
from mrnet.stochastic.analyze import *



if len(sys.argv) != 4:
    print("usage: python serialize.py json_file network params")
    quit()

molecule_entries = loadfn(sys.argv[1])
network_folder = sys.argv[2]
params_folder = sys.argv[3]


li_plus_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/Li.xyz',
    1)

ec_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/EC.xyz',
    0)

ledc_mol_entry  = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/LEDC.xyz',
    0)

initial_state_data_0 = [
(li_plus_mol_entry, 30),
(ec_mol_entry,30)
]

initial_state_data_1 = [
(li_plus_mol_entry, 300),
(ec_mol_entry,30)
]

initial_state_data_2 = [
(li_plus_mol_entry, 30),
(ec_mol_entry,300)
]

initial_state_data_3 = [
(li_plus_mol_entry, 300),
(ec_mol_entry,300)
]

entries_box = EntriesBox(molecule_entries)
reaction_generator = ReactionIterator(entries_box)
SerializeNetwork(network_folder,reaction_generator, shard_size=2000000)
serialize_initial_state(network_folder, entries_box, initial_state_data_0)
serialize_simulation_parameters(params_folder, number_of_threads=20, step_cutoff=200, number_of_simulations = 100000)
