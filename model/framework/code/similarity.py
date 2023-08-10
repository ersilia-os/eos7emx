from rdkit import Chem
from rdkit.Chem.Descriptors import MolWt


from smallworld_api import SmallWorld

sw = SmallWorld()


def zinc_similarity(smiles_list):
    results = []
    for smiles in smiles_list:
        df = sw.search(smiles, dist=5, db=sw.ZINC_dataset)
        results.append(df["smiles"].tolist())
    return results
