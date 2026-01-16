# Automation Skill Gaps

Repository for the Zambia-based project on automation and skill gaps. Tools and scripts for processing and analyzing ESCO and O*NET skills data, with a focus on mapping hierarchical relationships and identifying automation-related skill gaps.

## Repository Structure

```
automation-skill-gaps/
├── scripts/              # Python processing scripts
│   ├── esco/            # ESCO-specific scripts
│   └── onet/            # O*NET-specific scripts
│
├── notebooks/           # Jupyter notebooks for analysis
│   ├── esco/            # ESCO analysis notebooks
│   └── onet/            # O*NET analysis notebooks
│
├── data/                # Data files
│   ├── esco/
│   │   ├── ESCO_Tabiya_v2.0.1-rc.1/  # Raw ESCO taxonomy data
│   │   └── processed/                 # Generated/processed ESCO files
│   └── onet/
│       ├── raw/                       # Raw O*NET data files
│       └── processed/                 # Generated/processed O*NET files
│
└── docs/                # Documentation
    ├── esco/            # ESCO-specific documentation
    └── onet/            # O*NET-specific documentation
```

## ESCO Tools

### Scripts

#### `scripts/esco/map_skill_hierarchy_paths.py`
Maps complete upward hierarchy paths for each ESCO skill, creating separate rows for skills with multiple parents.

**Usage:**
```bash
python scripts/esco/map_skill_hierarchy_paths.py
```

**Output:** `data/esco/processed/skills_with_hierarchy_paths.csv`

**Features:**
- Traces all unique paths from skill to root nodes
- Adds columns for each hierarchy level (IDs and labels)
- Concatenates full path into single string (semicolon-separated)
- Handles skills with up to 31 different parent paths
- Creates separate rows for each unique path (24,015 total rows from 13,896 skills)

### Data Files

**Raw ESCO Data** (`data/esco/ESCO_Tabiya_v2.0.1-rc.1/`):
- `skills.csv` - ESCO skills dataset (13,896 skills)
- `skill_groups.csv` - Skill group classifications
- `skill_hierarchy.csv` - Parent-child relationships (20,649 relationships)
- `skill_to_skill_relations.csv` - Skill-to-skill relationships
- `occupations.csv` - ESCO occupations
- `occupation_groups.csv` - Occupation group classifications
- `occupation_hierarchy.csv` - Occupation hierarchies
- `occupation_to_skill_relations.csv` - Occupation-skill mappings
- `model_info.csv` - ESCO model metadata

**Processed ESCO Data** (`data/esco/processed/`):
- `skills_with_hierarchy_paths.csv` - Skills with complete upward paths (24,015 rows including all path variations)

## O*NET Tools

### Scripts

#### `scripts/onet/map_task_hierarchy_paths.py`
Maps complete upward hierarchy paths for each O*NET task through the work activity hierarchy: Tasks → DWAs (Detailed Work Activities) → IWAs (Intermediate Work Activities) → GWAs (Generalized Work Activities).

**Usage:**
```bash
python scripts/onet/map_task_hierarchy_paths.py
```

**Output:** `data/onet/processed/task_hierarchy_paths.csv`

**Features:**
- Traces all unique paths from tasks through DWAs, IWAs, to Work Activities
- Starts from Task Statements to preserve task metadata (Task Type, Incumbents Responding)
- Creates separate rows for tasks with multiple DWA mappings (handles 1-5 paths per task)
- Concatenates full path into single string (semicolon-separated)
- Provides detailed statistics on hierarchy coverage and completeness

### Notebooks

- `notebooks/onet/onet_data_prep.ipynb` - O*NET data preparation and analysis

### Data Files

**Raw O*NET Data** (`data/onet/raw/`):
- `Task Statements.xlsx` - Base table with all tasks (18,797 tasks)
- `Tasks to DWAs.xlsx` - Task-to-DWA mappings (23,851 mappings)
- `DWA Reference.xlsx` - Complete hierarchy (DWAs → IWAs → Work Activities)
- `IWA Reference.xlsx` - IWA definitions
- `Work Activities.xlsx` - Work Activity ratings by occupation

**Processed O*NET Data** (`data/onet/processed/`):
- `task_hierarchy_paths.csv` - Tasks with complete upward paths (23,851 rows including all path variations)
- `joined_tasks_dwa_iwa_elements.csv` - (Legacy) join output from notebook analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/automation-skill-gaps.git
cd automation-skill-gaps

# Install dependencies
pip install -r requirements.txt
```

## Requirements

See `requirements.txt` for full dependencies. Key requirements:
- Python 3.8+
- pandas
- jupyter (for notebooks)

## Quick Start

### ESCO Hierarchy Analysis

1. **Map complete hierarchy paths:**
   ```bash
   python scripts/esco/map_skill_hierarchy_paths.py
   ```

2. **View results:**
   - Check `data/esco/processed/skills_with_hierarchy_paths.csv` for output
   - Open Jupyter notebooks in `notebooks/esco/` for analysis

### O*NET Hierarchy Analysis

1. **Map complete hierarchy paths:**
   ```bash
   python scripts/onet/map_task_hierarchy_paths.py
   ```

2. **View results:**
   - Check `data/onet/processed/task_hierarchy_paths.csv` for output
   - Open `notebooks/onet/onet_data_prep.ipynb` for additional analysis

## Hierarchy Statistics

### ESCO Hierarchy

- **Total unique skills:** 13,896
- **Total paths (with duplicates for multiple parents):** 24,015
- **Skills with multiple parent paths:** 4,955 (35.7%)
- **Maximum paths for a single skill:** 31
- **Hierarchy depth:** 4-11 levels

### O*NET Hierarchy

- **Total unique tasks:** 18,797
- **Total paths (with multiple DWA mappings):** 23,851
- **Average paths per task:** 1.27
- **Tasks with multiple paths:** 4,366 (23.2%)
- **Maximum paths for a single task:** 5
- **Hierarchy levels:**
  - **37 unique Work Activities (GWAs)** - Generalized work activities
  - **332 unique IWAs** - Intermediate work activities
  - **2,083 unique DWAs** - Detailed work activities
  - **18,797 unique Tasks** - Bottom level

## Contributing

When adding new scripts or data:
1. Place scripts in appropriate `scripts/` subdirectory
2. Place raw data in `data/*/raw/` directories
3. Output processed data to `data/*/processed/` directories
4. Add documentation to `docs/` subdirectories
5. Add analysis notebooks to `notebooks/` subdirectories

## License

See [LICENSE](LICENSE) file for details.

## Data Sources

- **ESCO:** European Skills, Competences, Qualifications and Occupations taxonomy (v2.0.1-rc.1)
- **O*NET:** Occupational Information Network database
