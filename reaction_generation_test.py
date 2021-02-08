import sys
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from RNMC import *

if len(sys.argv) != 2:
    print("usage: python serialize.py json")
    exit()

molecule_list_json = sys.argv[1]
molecule_entries = loadfn(molecule_list_json)
generator = ReactionGenerator(molecule_entries)

for reaction in generator:
    print("yewwwwwwww")
