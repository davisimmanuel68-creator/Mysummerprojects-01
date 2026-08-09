import os
import requests
from rdkit import Chem
from rdkit.Chem import AllChem
from Bio.PDB import PDBParser, PDBIO, Select
import numpy as np
 
# ------------------------------------------------------------------
# CONFIG - edit these
# ------------------------------------------------------------------
PDB_ID = "1EQG"          # <-- VERIFY this on rcsb.org yourself
LIGAND_CODE = "IBP"      # PDB ligand code for ibuprofen
OUTPUT_DIR = "docking_run"
BOX_SIZE = 20.0           # Angstrom, size of the search box around the pocket
 
os.makedirs(OUTPUT_DIR, exist_ok=True)
 
 
# ------------------------------------------------------------------
# STEP 1: Download the PDB structure
# ------------------------------------------------------------------
def download_pdb(pdb_id, out_dir):
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    r = requests.get(url)
    r.raise_for_status()
    path = os.path.join(out_dir, f"{pdb_id}.pdb")
    with open(path, "w") as f:
        f.write(r.text)
    print(f"Downloaded {pdb_id} -> {path}")
    return path
 
 
# ------------------------------------------------------------------
# STEP 2: Split into (a) protein-only receptor and (b) the original
# bound ibuprofen, so we can dock our own copy back in and compare.
# ------------------------------------------------------------------
class ProteinOnly(Select):
    """Keeps only standard amino acid residues (drops waters, ligands, ions)."""
    def accept_residue(self, residue):
        return residue.id[0] == " "  # blank hetflag = standard residue
 
 
class LigandOnly(Select):
    def __init__(self, ligand_code):
        self.ligand_code = ligand_code
 
    def accept_residue(self, residue):
        return residue.resname == self.ligand_code
 
 
def split_structure(pdb_path, pdb_id, ligand_code, out_dir):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure(pdb_id, pdb_path)
 
    io = PDBIO()
    io.set_structure(structure)
 
    receptor_path = os.path.join(out_dir, "receptor_raw.pdb")
    io.save(receptor_path, ProteinOnly())
 
    io.set_structure(structure)
    ligand_path = os.path.join(out_dir, "original_ligand.pdb")
    io.save(ligand_path, LigandOnly(ligand_code))
 
    print(f"Receptor saved -> {receptor_path}")
    print(f"Original bound ligand saved -> {ligand_path}")
    return receptor_path, ligand_path
 
 
# ------------------------------------------------------------------
# STEP 3: Find the docking box center from the original ligand's
# coordinates (i.e. dock into the same pocket it was crystallized in)
# ------------------------------------------------------------------
def get_ligand_centroid(ligand_pdb_path):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("ligand", ligand_pdb_path)
    coords = [atom.coord for atom in structure.get_atoms()]
    coords = np.array(coords)
    centroid = coords.mean(axis=0)
    print(f"Docking box center (from original ligand): {centroid}")
    return centroid
 
 
# ------------------------------------------------------------------
# STEP 4: Build a fresh ibuprofen 3D structure from SMILES with RDKit
# (independent of the crystal structure -- this is the molecule we
# will actually dock)
# ------------------------------------------------------------------
def build_ibuprofen(out_dir):
    smiles = "CC(C)Cc1ccc(cc1)C(C)C(=O)O"  # ibuprofen
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol)
 
    sdf_path = os.path.join(out_dir, "ibuprofen.sdf")
    writer = Chem.SDWriter(sdf_path)
    writer.write(mol)
    writer.close()
    print(f"Built ibuprofen 3D structure -> {sdf_path}")
    return sdf_path
 
 
# ------------------------------------------------------------------
# STEP 5: Convert receptor + ligand to PDBQT (Vina's input format)
# Uses Meeko for the ligand and a simple call for the receptor.
# ------------------------------------------------------------------
def prepare_ligand_pdbqt(sdf_path, out_dir):
    from meeko import MoleculePreparation, PDBQTWriterLegacy
 
    mol = Chem.SDMolSupplier(sdf_path, removeHs=False)[0]
    preparator = MoleculePreparation()
    mol_setups = preparator.prepare(mol)
 
    pdbqt_path = os.path.join(out_dir, "ligand.pdbqt")
    pdbqt_string = PDBQTWriterLegacy.write_string(mol_setups[0])[0]
    with open(pdbqt_path, "w") as f:
        f.write(pdbqt_string)
    print(f"Ligand PDBQT ready -> {pdbqt_path}")
    return pdbqt_path
 
 
def prepare_receptor_pdbqt(receptor_pdb_path, out_dir):
    """
    Receptor prep uses meeko's mk_prepare_receptor executable, which pip
    installs into the same environment's Scripts folder. Rather than rely
    on that folder being on PATH (which is finicky across terminal
    sessions on Windows), we locate it directly relative to sys.executable.
    """
    import subprocess
    import sys
 
    scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
    exe_path = os.path.join(scripts_dir, "mk_prepare_receptor.exe")
 
    if not os.path.exists(exe_path):
        # Fall back to PATH lookup in case of a non-Windows / different layout
        exe_path = "mk_prepare_receptor.exe"
 
    pdbqt_path = os.path.join(out_dir, "receptor.pdbqt")
    cmd = [
        exe_path,
        "--read_pdb", receptor_pdb_path,
        "-o", pdbqt_path.replace(".pdbqt", ""),
        "-p"  # write pdbqt
    ]
    subprocess.run(cmd, check=True)
    print(f"Receptor PDBQT ready -> {pdbqt_path}")
    return pdbqt_path
 
 
# ------------------------------------------------------------------
# STEP 6: Run AutoDock Vina
# ------------------------------------------------------------------
# NOTE: this calls the standalone vina.exe binary via subprocess instead
# of the "vina" pip package. The pip package needs to compile C++ code
# against Boost, which is a pain to set up (especially on Windows).
# The precompiled executable avoids that entirely.
#
# Download it from: https://github.com/ccsb-scripps/AutoDock-Vina/releases
# Rename it to vina.exe and either put it on your PATH, or set
# VINA_EXECUTABLE below to its full path.
# ------------------------------------------------------------------
VINA_EXECUTABLE = r"D:\gamess\tool\vina_1.2.7_win.exe"  # or full path, e.g. r"C:\tools\vina.exe"
 
 
def run_vina(receptor_pdbqt, ligand_pdbqt, center, out_dir, box_size=BOX_SIZE):
    import subprocess
 
    out_path = os.path.join(out_dir, "docking_out.pdbqt")
    log_path = os.path.join(out_dir, "docking_log.txt")
 
    cmd = [
        VINA_EXECUTABLE,
        "--receptor", receptor_pdbqt,
        "--ligand", ligand_pdbqt,
        "--center_x", str(center[0]),
        "--center_y", str(center[1]),
        "--center_z", str(center[2]),
        "--size_x", str(box_size),
        "--size_y", str(box_size),
        "--size_z", str(box_size),
        "--exhaustiveness", "8",
        "--num_modes", "10",
        "--out", out_path,
    ]
 
    print("Running Vina:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
 
    with open(log_path, "w") as f:
        f.write(result.stdout)
        f.write(result.stderr)
 
    if result.returncode != 0:
        print("Vina failed. Full output written to:", log_path)
        print(result.stderr)
        raise RuntimeError("Vina docking failed -- check docking_log.txt")
 
    print(f"Docking complete -> {out_path}")
    print("Binding affinities (top poses):")
    for line in result.stdout.splitlines():
        # Vina prints a results table; lines starting with a pose number
        if line.strip() and line.strip()[0].isdigit():
            print("  " + line.strip())
 
    return out_path
 
 
# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    pdb_path = download_pdb(PDB_ID, OUTPUT_DIR)
    receptor_pdb, original_ligand_pdb = split_structure(
        pdb_path, PDB_ID, LIGAND_CODE, OUTPUT_DIR
    )
    center = get_ligand_centroid(original_ligand_pdb)
    ligand_sdf = build_ibuprofen(OUTPUT_DIR)
 
    ligand_pdbqt = prepare_ligand_pdbqt(ligand_sdf, OUTPUT_DIR)
    receptor_pdbqt = prepare_receptor_pdbqt(receptor_pdb, OUTPUT_DIR)
 
    run_vina(receptor_pdbqt, ligand_pdbqt, center, OUTPUT_DIR)
 
    print("\nNext step: open receptor_raw.pdb, original_ligand.pdb, and "
          "docking_out.pdbqt together in PyMOL to visually compare your "
          "docked pose against the original crystal pose, and compute RMSD.")
 
 
if __name__ == "__main__":
    main()
