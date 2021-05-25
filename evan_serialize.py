import sys
import pickle
sys.path.append('./mrnet/src')
from pymatgen.core.structure import Molecule
from pymatgen.analysis.graphs import MoleculeGraph
from pymatgen.analysis.local_env import OpenBabelNN, metal_edge_extender
from mrnet.stochastic.serialize import SerializeNetwork, serialize_initial_state, serialize_simulation_parameters
from mrnet.network.reaction_generation import EntriesBox, ReactionIterator
from mrnet.network.reaction_network import ReactionNetwork

path_to_box = sys.argv[1]
destination_path = sys.argv[2]

with open(path_to_box, "rb") as pick:
    box = pickle.load(pick)
    rxn_iter = ReactionIterator(
        box,
        electron_free_energy=-1.8,
        single_elem_interm_ignore=["C1", "O1", "P1", "F1"])

sn = SerializeNetwork(destination_path,
       rxn_iter,
       constant_barrier=0.0)
