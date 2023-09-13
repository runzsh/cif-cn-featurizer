import gemmi
import re
from util.string_parser import remove_string_braket
import numpy as np


def get_atom_type(label):
    # Splitting the label into separate parts if it contains parentheses
    parts = re.split(r'[()]', label)
    for part in parts:
        # Attempt to extract the atom type
        match = re.search(r'([A-Z][a-z]*)', part)
        if match:
            return match.group(1)
    return None


def extract_formula_and_atoms(block):
    """
    Extract the chemical formula and unique atoms from a CIF block.
    """
    formula = None
    formula_string = None

    if block.find_pair('_chemical_formula_structural'):
        formula = block.find_pair('_chemical_formula_structural')
    elif block.find_pair('_chemical_formula_sum'):
        formula = block.find_pair('_chemical_formula_sum')
    
    if formula:
        formula_string = formula[1]
        formula_string = formula_string.replace("'", "") # Remove quotes
        formula_string = re.sub('[~ ]', '', formula_string) # Remove dashes and spaces

    if not formula_string:
        return None, 0, None

    pattern = re.compile(r"([A-Z][a-z]*)(\d*)") # Extract atom symbols and their counts
    matches = pattern.findall(formula_string)
    unique_atoms_tuple = [(atom, int(count) if count else 1) for atom, count in matches]
    num_of_unique_atoms = len({atom for atom, _ in unique_atoms_tuple})

    return unique_atoms_tuple, num_of_unique_atoms, formula_string


def get_loop_tags():
    """
    Returns a list of predefined loop tags commonly used for atomic site description.
    """
    loop_tags = ["_atom_site_label", "_atom_site_type_symbol",
            "_atom_site_symmetry_multiplicity", "_atom_site_Wyckoff_symbol",
            "_atom_site_fract_x", "_atom_site_fract_y","_atom_site_fract_z", "_atom_site_occupancy"]
    
    return loop_tags


def get_unit_cell_lengths_angles(block):
    """
    Returns the unit cell lengths and angles from a given block.
    """
    keys_lengths = ['_cell_length_a', '_cell_length_b', '_cell_length_c']
    keys_angles = ['_cell_angle_alpha', '_cell_angle_beta', '_cell_angle_gamma']

    lengths = [remove_string_braket(block.find_value(key)) for key in keys_lengths]
    angles = [remove_string_braket(block.find_value(key)) for key in keys_angles]

    return tuple(lengths + angles)


def exceeds_atom_count_limit(all_points, max_atoms_count):
    """
    Checks if the number of unique atomic positions after applying symmetry operations 
    exceeds the specified atom count limit.
    """

    return len(all_points) > max_atoms_count


def get_CIF_block(filename):
    """
    Returns a CIF block from its CIF filename.
    """
    doc = gemmi.cif.read_file(filename)
    block = doc.sole_block()

    return block


def get_loop_values(block, loop_tags):
    """
    Retrieves loop values from a block for the specified tags.
    """
    loop_values = [block.find_loop(tag) for tag in loop_tags]

    # Check for zero or missing coordinates
    if len(loop_values[4]) == 0 or len(loop_values[5]) == 0 or len(loop_values[6]) == 0:  # missing coordinates
        raise RuntimeError("Missing atomic coordinates")

    return loop_values


def print_loop_values(loop_values, i):
    """
    Prints the loop values for a specific index with a descriptive format.
    """
    descriptions = [
        "Atom Site Label:",
        "Atom Site Type Symbol:",
        "Atom Site Symmetry Multiplicity:",
        "Atom Site Wyckoff Symbol:",
        "Atom Site Fract X:",
        "Atom Site Fract Y:",
        "Atom Site Fract Z:",
        "Atom Site Occupancy:"
    ]
    
    for idx, desc in enumerate(descriptions):
        value = loop_values[idx][i]
        if "Fract" in desc:
            value = float(value)
        elif "Symmetry Multiplicity" in desc:
            value = int(value)
        print(f"{desc} {value}")
    print()