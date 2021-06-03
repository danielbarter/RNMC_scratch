import sys
import os
sys.path.append('./mrnet/src')
from monty.serialization import loadfn, dumpfn
from mrnet.core.mol_entry import *



choli = loadfn("./choli.json")
ronald = loadfn("./mol_lists/ronalds_MoleculeEntry.json")


def find_choli(ronald_mol):
    for choli_mol in choli:
        if ronald_mol.mol_graph.isomorphic_to(choli_mol['molecule_graph']) and ronald_mol.charge == choli_mol['charge']:
            return choli_mol


ronald_choli = [find_choli(ronald_mol) for ronald_mol in ronald]

