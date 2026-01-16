#!/usr/bin/env python3
"""
Quick CSV viewer for skills_with_levels.csv

Shows key columns in a readable table format.
"""

import pandas as pd
import sys

def view_skills(filename='skills_with_levels.csv', num_rows=20, level_filter=None):
    """View skills in a readable format."""

    # Read CSV
    df = pd.read_csv(filename)

    # Filter by level if specified
    if level_filter is not None:
        df = df[df['LEVEL'] == level_filter]
        print(f"Showing skills at LEVEL {level_filter}")
    else:
        print(f"Showing first {num_rows} rows")

    # Select key columns to display
    display_cols = ['ID', 'PREFERREDLABEL', 'SKILLTYPE', 'LEVEL']

    # Configure display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 60)

    # Display
    print("\n" + "="*100)
    print(df[display_cols].head(num_rows).to_string(index=False))
    print("="*100)

    # Statistics
    print(f"\nTotal skills: {len(df):,}")
    print(f"\nLevel distribution:")
    level_counts = df['LEVEL'].value_counts().sort_index()
    for level, count in level_counts.items():
        print(f"  Level {level}: {count:,} skills")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='View skills CSV file')
    parser.add_argument('-n', '--num', type=int, default=20,
                        help='Number of rows to display (default: 20)')
    parser.add_argument('-l', '--level', type=int,
                        help='Filter by specific level')
    parser.add_argument('-f', '--file', default='skills_with_levels.csv',
                        help='CSV file to view (default: skills_with_levels.csv)')

    args = parser.parse_args()

    view_skills(args.file, args.num, args.level)
