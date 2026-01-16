#!/usr/bin/env python3
"""
Map complete upward hierarchy paths for ESCO skills.

For each skill in skills.csv, this script:
1. Maps all upward paths through parent relationships
2. Creates separate rows for skills with multiple parents
3. Adds columns for each hierarchy level (IDs and labels)
4. Concatenates the full path into a single string

Output: skills_with_hierarchy_paths.csv
"""

import csv
import pandas as pd
from collections import defaultdict

def load_hierarchy(hierarchy_file):
    """Load parent-child relationships from skill_hierarchy.csv."""
    child_to_parents = defaultdict(list)

    with open(hierarchy_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            child_id = row['CHILDID']
            parent_id = row['PARENTID']
            child_to_parents[child_id].append(parent_id)

    return child_to_parents

def load_labels(skills_file, skillgroups_file):
    """Load preferred labels for both skills and skillgroups."""
    labels = {}

    # Load skill labels
    print("Loading skill labels...")
    with open(skills_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels[row['ID']] = row['PREFERREDLABEL']

    # Load skillgroup labels
    print("Loading skillgroup labels...")
    with open(skillgroups_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels[row['ID']] = row['PREFERREDLABEL']

    return labels

def get_all_paths(skill_id, child_to_parents, current_path=None, visited=None):
    """
    Recursively get all upward paths from a skill to root nodes.

    Returns a list of paths, where each path is a list of IDs.
    """
    if current_path is None:
        current_path = [skill_id]
    if visited is None:
        visited = set()

    # Prevent cycles
    if skill_id in visited:
        return [current_path]

    # If no parents, this is a complete path
    if skill_id not in child_to_parents or not child_to_parents[skill_id]:
        return [current_path]

    # Mark as visited for this path
    visited.add(skill_id)

    # Get all paths through all parents
    all_paths = []
    for parent_id in child_to_parents[skill_id]:
        parent_paths = get_all_paths(
            parent_id,
            child_to_parents,
            current_path + [parent_id],
            visited.copy()
        )
        all_paths.extend(parent_paths)

    return all_paths

def map_skill_hierarchies(skills_file, hierarchy_file, skillgroups_file, output_file):
    """Main function to map all skill hierarchy paths."""

    print("Loading hierarchy relationships...")
    child_to_parents = load_hierarchy(hierarchy_file)

    print("Loading labels...")
    labels = load_labels(skills_file, skillgroups_file)

    print("Loading skills data...")
    skills_df = pd.read_csv(skills_file)

    print(f"\nProcessing {len(skills_df)} skills...")

    # Store all output rows
    output_rows = []
    max_path_length = 0

    for idx, skill_row in skills_df.iterrows():
        skill_id = skill_row['ID']

        # Get all upward paths for this skill
        paths = get_all_paths(skill_id, child_to_parents)

        # Track maximum path length for column creation
        for path in paths:
            max_path_length = max(max_path_length, len(path))

        # Create a row for each unique path
        for path in paths:
            row = skill_row.to_dict()

            # Add hierarchy level columns (starting from level 1, which is one level up)
            # path[0] is the skill itself, path[1] is one level up, etc.
            for level in range(1, len(path)):
                parent_id = path[level]
                level_name = f"{level}_level{'s' if level > 1 else ''}_up"

                # Add parent ID column
                row[f"{level_name}"] = parent_id

                # Add parent label column
                row[f"{level_name}_preferredlabel"] = labels.get(parent_id, "")

            # Create concatenated path string (from skill to root)
            # Using labels, separated by ";"
            path_labels = [labels.get(node_id, node_id) for node_id in path]
            row['hierarchy_path'] = " ; ".join(path_labels)

            output_rows.append(row)

        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1} skills...")

    print(f"\nCreating output with {len(output_rows)} total rows (including multiple paths)...")
    print(f"Maximum path length: {max_path_length} levels")

    # Convert to DataFrame
    output_df = pd.DataFrame(output_rows)

    # Reorder columns: original skill columns first, then hierarchy columns, then path
    original_cols = list(skills_df.columns)

    # Get hierarchy columns and sort them numerically
    hierarchy_cols = [col for col in output_df.columns if '_level' in col]

    # Sort hierarchy columns by level number (1, 2, 3... not 1, 10, 2)
    def get_level_num(col):
        # Extract the number from column names like "1_level_up" or "10_levels_up"
        import re
        match = re.match(r'(\d+)_level', col)
        return int(match.group(1)) if match else 999

    # Separate ID and label columns, sort each by level number
    id_cols = sorted([col for col in hierarchy_cols if 'preferredlabel' not in col], key=get_level_num)
    label_cols = sorted([col for col in hierarchy_cols if 'preferredlabel' in col], key=get_level_num)

    # Interleave ID and label columns: 1_level_up, 1_level_up_preferredlabel, 2_levels_up, etc.
    ordered_hierarchy_cols = []
    for id_col, label_col in zip(id_cols, label_cols):
        ordered_hierarchy_cols.extend([id_col, label_col])

    # Final column order
    final_cols = original_cols + ordered_hierarchy_cols + ['hierarchy_path']
    output_df = output_df[final_cols]

    # Save to CSV
    print(f"Writing output to {output_file}...")
    output_df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"\nDone!")
    print(f"  Input skills: {len(skills_df)}")
    print(f"  Output rows: {len(output_df)} (skills with multiple parents have multiple rows)")
    print(f"  Skills with multiple parents: {len(output_df) - len(skills_df)}")

    # Show some statistics
    paths_per_skill = output_df.groupby('ID').size()
    print(f"\nPath statistics:")
    print(f"  Skills with 1 path: {sum(paths_per_skill == 1)}")
    print(f"  Skills with 2+ paths: {sum(paths_per_skill > 1)}")
    print(f"  Max paths for a single skill: {paths_per_skill.max()}")

if __name__ == '__main__':
    import os

    # Determine file paths relative to repository structure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))  # Go up to automation-skill-gaps/

    # Input files from raw data
    data_dir = os.path.join(repo_root, 'data', 'esco', 'ESCO_Tabiya_v2.0.1-rc.1')
    skills_file = os.path.join(data_dir, 'skills.csv')
    hierarchy_file = os.path.join(data_dir, 'skill_hierarchy.csv')
    skillgroups_file = os.path.join(data_dir, 'skill_groups.csv')

    # Output file to processed directory
    output_dir = os.path.join(repo_root, 'data', 'esco', 'processed')
    output_file = os.path.join(output_dir, 'skills_with_hierarchy_paths.csv')

    map_skill_hierarchies(skills_file, hierarchy_file, skillgroups_file, output_file)
