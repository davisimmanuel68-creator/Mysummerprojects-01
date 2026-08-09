from pymol import cmd
 
OUTPUT_DIR = "docking_run"
 
# Load the receptor
cmd.load(f"{OUTPUT_DIR}/receptor_raw.pdb", "receptor")
 
# Load the original crystal-bound ibuprofen
cmd.load(f"{OUTPUT_DIR}/original_ligand.pdb", "crystal_ibuprofen")
 
# Load your docked poses (all 10 -- each becomes a separate "state")
cmd.load(f"{OUTPUT_DIR}/docking_out.pdbqt", "docked_poses")
 
# Show only the top-ranked pose (state 1) for clarity
cmd.set("state", 1)
 
# Styling
cmd.hide("everything")
cmd.show("cartoon", "receptor")
cmd.color("gray80", "receptor")
 
cmd.show("sticks", "crystal_ibuprofen")
cmd.color("green", "crystal_ibuprofen")
 
cmd.show("sticks", "docked_poses")
cmd.color("magenta", "docked_poses")
 
# Zoom into the binding pocket (around the crystal ligand)
cmd.zoom("crystal_ibuprofen", 8)
 
# Label for clarity
cmd.set("label_size", 14)
 
print("Green = original crystal ibuprofen pose")
print("Magenta = your top-ranked docked pose")
print("If your docking worked well, the magenta and green sticks should")
print("overlap closely in the same pocket.")
 
# Save a rendered image
cmd.ray(1200, 900)
cmd.png(f"{OUTPUT_DIR}/pose_comparison.png", dpi=150)
print(f"Saved image -> {OUTPUT_DIR}/pose_comparison.png")
 