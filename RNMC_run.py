import sys
import time
import pickle
sys.path.append('./mrnet/src')
from mrnet.network.reaction_network import ReactionNetwork


import mrnet.network
import mrnet.core.mol_entry
import mrnet.core.reactions
import mrnet.core.rates
sys.modules['pymatgen.reaction_network'] = mrnet.network
sys.modules['pymatgen.entries.mol_entry'] = mrnet.core.mol_entry
sys.modules['pymatgen.reaction_network.reaction'] =  mrnet.core.reactions
sys.modules['pymatgen.reaction_network.reaction_rates'] = mrnet.core.rates


with open('./network_from_paper','rb') as f:
    network_from_paper = pickle.load(f)

from RNMC import *

rns = ReactionNetworkSerialization(network_from_paper)

initial_state = np.zeros(rns.number_of_species)
Li_plus_index = rns.find_index_from_mol_graph('./Li.xyz', 1)
EC_index = rns.find_index_from_mol_graph(
    './mrnet/test_files/reaction_network_files/EC.xyz',0)
LEDC_index = rns.find_index_from_mol_graph(
    './mrnet/test_files/reaction_network_files/LEDC.xyz',0)
initial_state[Li_plus_index] = 30
initial_state[EC_index] = 30


plasma_process = start_plasma_server(10)
t = time.process_time()
mcb = MonteCarloBundler(4,rns,initial_state,5,range(1000))
print("time taken:", time.process_time() - t)
mcb.pp_pathways(LEDC_index)
plasma_process.terminate()
