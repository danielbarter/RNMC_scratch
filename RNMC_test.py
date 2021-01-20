import sys
sys.path.append('./mrnet/src')


import mrnet.network
import mrnet.core.mol_entry
import mrnet.core.reactions
import mrnet.core.rates
sys.modules['pymatgen.reaction_network'] = mrnet.network
sys.modules['pymatgen.entries.mol_entry'] = mrnet.core.mol_entry
sys.modules['pymatgen.reaction_network.reaction'] =  mrnet.core.reactions
sys.modules['pymatgen.reaction_network.reaction_rates'] = mrnet.core.rates


import pickle
# currently, these will only load using commit 222ad71 of mrnet
ledc_no_hop_file = "./-2.15V_ledc_lemc_network_pickle_wo_hop_1123"
with open(ledc_no_hop_file, 'rb') as f:
    ledc_no_hop_reaction_network = pickle.load(f)

from RNMC import *

ledc_rns = ReactionNetworkSerialization(ledc_no_hop_reaction_network)

ledc_initial_state = np.zeros(ledc_rns.number_of_species)
Li_plus_index = ledc_rns.find_index_from_mol_graph('./Li.xyz', 1)
EC_index = ledc_rns.find_index_from_mol_graph('./mrnet/test_files/reaction_network_files/EC.xyz',0)
LEDC_index = ledc_rns.find_index_from_mol_graph('./mrnet/test_files/reaction_network_files/LEDC.xyz',0)
ledc_initial_state[Li_plus_index] = 30
ledc_initial_state[EC_index] = 30

serialize_reaction_network(ledc_rns, ledc_initial_state, "./ronalds_network")
