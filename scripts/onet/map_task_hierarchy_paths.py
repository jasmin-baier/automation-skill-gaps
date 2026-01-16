"""
Map O*NET Task Hierarchy Paths

This script creates a mapping from O*NET tasks to their complete hierarchy paths:
Tasks → DWAs (Detailed Work Activities) → IWAs (Intermediate Work Activities) → GWAs (Generalized Work Activities)

For each task, it follows all possible upward paths through the hierarchy,
creating one row per unique path when a task maps to multiple higher-level activities.

Input files (from data/onet/raw/):
    - Task Statements.xlsx: Base table with all tasks
    - Tasks to DWAs.xlsx: Mapping from tasks to DWAs
    - DWA Reference.xlsx: Mapping from DWAs to IWAs to Work Activities (GWAs)

Output:
    - data/onet/processed/task_hierarchy_paths.csv: All tasks with their complete hierarchy paths
"""

import pandas as pd
from pathlib import Path


def load_onet_data(data_dir: Path):
    """Load all required O*NET Excel files."""
    print("Loading O*NET data files...")

    # Load Task Statements (base table)
    task_statements = pd.read_excel(
        data_dir / 'Task Statements.xlsx',
        sheet_name='Task Statements'
    )
    print(f"  Loaded {len(task_statements):,} task statements")

    # Load Tasks to DWAs mapping
    tasks_to_dwas = pd.read_excel(
        data_dir / 'Tasks to DWAs.xlsx',
        sheet_name='Tasks to DWAs'
    )
    print(f"  Loaded {len(tasks_to_dwas):,} task-to-DWA mappings")

    # Load DWA Reference (contains DWA → IWA → GWA hierarchy)
    dwa_reference = pd.read_excel(
        data_dir / 'DWA Reference.xlsx',
        sheet_name='DWA Reference'
    )
    print(f"  Loaded {len(dwa_reference):,} DWA reference entries")

    return task_statements, tasks_to_dwas, dwa_reference


def create_hierarchy_paths(task_statements, tasks_to_dwas, dwa_reference):
    """
    Create complete hierarchy paths for all tasks.

    For each task, follow all mappings upward through DWAs, IWAs, and Work Activities.
    When multiple paths exist, create one row per unique path.
    """
    print("\nBuilding hierarchy paths...")

    # Step 1: Join tasks to DWAs
    # A task can map to multiple DWAs, creating multiple rows
    task_with_dwa = task_statements.merge(
        tasks_to_dwas[['O*NET-SOC Code', 'Task ID', 'DWA ID', 'DWA Title']],
        on=['O*NET-SOC Code', 'Task ID'],
        how='left'
    )

    print(f"  After joining with DWAs: {len(task_with_dwa):,} rows")
    print(f"  Tasks with DWA mappings: {task_with_dwa['DWA ID'].notna().sum():,}")
    print(f"  Tasks without DWA mappings: {task_with_dwa['DWA ID'].isna().sum():,}")

    # Step 2: Join DWAs to the complete hierarchy (IWAs and Work Activities)
    # A DWA can map to multiple IWAs/GWAs, potentially creating more rows
    hierarchy_paths = task_with_dwa.merge(
        dwa_reference[['DWA ID', 'IWA ID', 'IWA Title', 'Element ID', 'Element Name']],
        on='DWA ID',
        how='left'
    )

    # Rename columns for clarity
    hierarchy_paths = hierarchy_paths.rename(columns={
        'Element ID': 'WA_Element_ID',
        'Element Name': 'WA_Element_Name'
    })

    print(f"  After joining with hierarchy: {len(hierarchy_paths):,} rows")

    # Step 3: Create concatenated path string
    # Format: WA_Element_Name ; IWA_Title ; DWA_Title ; Task
    def create_path_string(row):
        """Create a semicolon-separated path string."""
        components = []
        if pd.notna(row['WA_Element_Name']):
            components.append(str(row['WA_Element_Name']))
        if pd.notna(row['IWA Title']):
            components.append(str(row['IWA Title']))
        if pd.notna(row['DWA Title']):
            components.append(str(row['DWA Title']))
        if pd.notna(row['Task']):
            components.append(str(row['Task']))

        return ' ; '.join(components) if components else None

    hierarchy_paths['Hierarchy_Path'] = hierarchy_paths.apply(create_path_string, axis=1)

    # Reorder columns for better readability
    # Start with task-level columns, then add hierarchy columns
    task_columns = ['O*NET-SOC Code', 'Title', 'Task ID', 'Task', 'Task Type',
                    'Incumbents Responding', 'Date', 'Domain Source']
    hierarchy_columns = ['DWA ID', 'DWA Title', 'IWA ID', 'IWA Title',
                        'WA_Element_ID', 'WA_Element_Name', 'Hierarchy_Path']

    # Only include columns that exist
    available_task_columns = [col for col in task_columns if col in hierarchy_paths.columns]
    column_order = available_task_columns + hierarchy_columns

    hierarchy_paths = hierarchy_paths[column_order]

    return hierarchy_paths


def analyze_paths(hierarchy_paths):
    """Print summary statistics about the hierarchy paths."""
    print("\n" + "="*60)
    print("HIERARCHY PATH ANALYSIS")
    print("="*60)

    total_rows = len(hierarchy_paths)
    unique_tasks = hierarchy_paths[['O*NET-SOC Code', 'Task ID']].drop_duplicates().shape[0]

    print(f"\nTotal rows (unique paths): {total_rows:,}")
    print(f"Unique tasks: {unique_tasks:,}")
    print(f"Average paths per task: {total_rows/unique_tasks:.2f}")

    # Count tasks by number of paths
    paths_per_task = hierarchy_paths.groupby(['O*NET-SOC Code', 'Task ID']).size()
    print(f"\nDistribution of paths per task:")
    print(f"  1 path: {(paths_per_task == 1).sum():,} tasks")
    print(f"  2-5 paths: {((paths_per_task >= 2) & (paths_per_task <= 5)).sum():,} tasks")
    print(f"  6-10 paths: {((paths_per_task >= 6) & (paths_per_task <= 10)).sum():,} tasks")
    print(f"  >10 paths: {(paths_per_task > 10).sum():,} tasks")
    print(f"  Max paths for a single task: {paths_per_task.max()}")

    # Count by hierarchy level completeness
    complete_paths = hierarchy_paths['WA_Element_ID'].notna().sum()
    has_dwa = hierarchy_paths['DWA ID'].notna().sum()
    has_iwa = hierarchy_paths['IWA ID'].notna().sum()

    print(f"\nHierarchy completeness:")
    print(f"  Rows with complete path to GWA: {complete_paths:,} ({complete_paths/total_rows*100:.1f}%)")
    print(f"  Rows with DWA mapping: {has_dwa:,} ({has_dwa/total_rows*100:.1f}%)")
    print(f"  Rows with IWA mapping: {has_iwa:,} ({has_iwa/total_rows*100:.1f}%)")

    # Show unique counts at each level
    print(f"\nUnique counts at each level:")
    print(f"  Unique Work Activities (GWAs): {hierarchy_paths['WA_Element_ID'].nunique()}")
    print(f"  Unique IWAs: {hierarchy_paths['IWA ID'].nunique()}")
    print(f"  Unique DWAs: {hierarchy_paths['DWA ID'].nunique()}")
    print(f"  Unique Tasks: {unique_tasks:,}")


def main():
    """Main execution function."""
    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'data' / 'onet' / 'raw'
    output_dir = project_root / 'data' / 'onet' / 'processed'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print("O*NET TASK HIERARCHY PATH MAPPER")
    print("="*60)

    # Load data
    task_statements, tasks_to_dwas, dwa_reference = load_onet_data(data_dir)

    # Create hierarchy paths
    hierarchy_paths = create_hierarchy_paths(task_statements, tasks_to_dwas, dwa_reference)

    # Analyze and print statistics
    analyze_paths(hierarchy_paths)

    # Save output
    output_file = output_dir / 'task_hierarchy_paths.csv'
    hierarchy_paths.to_csv(output_file, index=False)
    print(f"\n{'='*60}")
    print(f"Output saved to: {output_file}")
    print(f"Total rows: {len(hierarchy_paths):,}")
    print("="*60)


if __name__ == '__main__':
    main()
