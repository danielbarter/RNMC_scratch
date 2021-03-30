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

molecule_entries = loadfn(sys.argv[1])

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

reaction_generator = ReactionGenerator(molecule_entries, 20, single_elem_interm_ignore=[])
rnsd = SerializedReactionNetwork(reaction_generator)
rnsd.serialize("./runs/network_0", initial_state_data_0)
rnsd.serialize("./runs/network_1", initial_state_data_1)
rnsd.serialize("./runs/network_2", initial_state_data_2)
rnsd.serialize("./runs/network_3", initial_state_data_3)
serialize_simulation_parameters("./runs/params", number_of_threads=7, step_cutoff=2000, number_of_simulations = 10000)
