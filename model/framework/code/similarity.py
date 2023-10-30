import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT)

import collections
import urllib
import json
import time
import pandas as pd
from smallworld_api import SmallWorld
import warnings
from rdkit import Chem
from rdkit import DataStructs
from rdkit.Chem import AllChem

warnings.filterwarnings("ignore")

MAX_N_MOLECULES = 1000


def calculate_similarity(ref_mol, mol_list):
    # Calculate fingerprints for the reference molecule and molecule list
    ref_fp = AllChem.GetMorganFingerprint(ref_mol, 2)
    mol_fps = [AllChem.GetMorganFingerprint(mol, 2) for mol in mol_list]

    # Calculate similarity between reference and each molecule in the list
    similarities = [
        DataStructs.TanimotoSimilarity(ref_fp, mol_fp) for mol_fp in mol_fps
    ]

    return similarities


def sort_molecules_by_similarity(ref_mol, mol_list, top_n=MAX_N_MOLECULES):
    similarities = calculate_similarity(ref_mol, mol_list)
    # Pair each molecule with its similarity to the reference molecule
    paired = list(zip(mol_list, similarities))
    # Sort by similarity (descending)
    sorted_mols = sorted(paired, key=lambda x: x[1], reverse=True)

    # Return only the molecules (without the similarity values), limited to top_n
    return [mol for mol, sim in sorted_mols][:top_n]


def get_available_maps():
    url = "https://sw.docking.org/search/maps"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data


def get_maps():
    data = get_available_maps()
    labels = ["REAL", "WuXi", "MCule", "Zinc"]
    found_maps = collections.defaultdict(list)
    for k, v in data.items():
        for l in labels:
            l_ = l.lower()
            k_ = k.lower()
            if l_ in k_:
                found_maps[l] += [k]
    found_maps_ = {}
    for k, v in found_maps.items():
        if len(v) == 1:
            v_ = v[0]
            if data[v_]["enabled"] and data[v_]["status"] == "Available":
                found_maps_[k] = v_
        else:
            v_sel = None
            w_sel = None
            for v_ in v:
                if not data[v_]["enabled"] or data[v_]["status"] != "Available":
                    continue
                w_ = data[v_]["numEntries"]
                if v_sel is None:
                    v_sel = v_
                    w_sel = w_
                else:
                    if w_ > w_sel:
                        v_sel = v_
                        w_sel = w_
            if v_sel is not None:
                found_maps_[k] = v_sel
    result = []
    for l in labels:
        if l in found_maps_:
            result += [(l, found_maps_[l])]
    return result


class SmallWorldSampler(object):
    def __init__(self, dist=10, length=100):
        self.maps = get_maps()
        self.sw = SmallWorld()
        self.dist = dist
        self.length = length

    def _sample(self, smiles, time_budget_sec=360):
        t0 = time.time()
        sampled_smiles = []
        for m in self.maps:
            try:
                db_name = m[1]
                results: pd.DataFrame = self.sw.search(
                    smiles, dist=self.dist, db=db_name, length=self.length
                )
            except:
                print(smiles, m, "did not work...")
                results = None
            if results is not None:
                sampled_smiles += list(results["smiles"])
            t1 = time.time()
            if (t1 - t0) > time_budget_sec:
                break
            t0 = time.time()
        can_smiles = []
        for smi in sampled_smiles:
            can_smiles += [Chem.MolToSmiles(Chem.MolFromSmiles(smi), True)]
        sampled_smiles = list(set(can_smiles))
        return sampled_smiles

    def sample(self, smiles, time_budget_sec=360):
        sampled_smiles = self._sample(smiles, time_budget_sec=time_budget_sec)
        if len(sampled_smiles) == 0:
            return []
        mol_list = [Chem.MolFromSmiles(smi) for smi in sampled_smiles]
        ref_mol = Chem.MolFromSmiles(smiles)
        sorted_molecules = sort_molecules_by_similarity(ref_mol, mol_list)
        sorted_smiles = [Chem.MolToSmiles(mol) for mol in sorted_molecules]
        return sorted_smiles
