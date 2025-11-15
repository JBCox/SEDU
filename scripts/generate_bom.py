#!/usr/bin/env python3
"""
Generate BOM (hardware/BOM_Seed.csv) from design_database.yaml

This script creates the Bill of Materials CSV file from the single-source database.
DO NOT edit BOM_Seed.csv directly - edit design_database.yaml and regenerate.
"""

import sys
import csv
from pathlib import Path
import yaml


def load_database():
    """Load design database from YAML."""
    db_path = Path(__file__).parent.parent / "design_database.yaml"
    with open(db_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_bom():
    """Generate BOM CSV from design database."""
    db = load_database()
    components = db.get('components', {})

    bom_path = Path(__file__).parent.parent / "hardware" / "BOM_Seed.csv"

    # Collect all components
    bom_rows = []

    for ref, comp_data in sorted(components.items()):
        # Extract fields
        ref_designator = comp_data.get('ref', ref)
        part_number = comp_data.get('part_number', 'TBD')
        qty = comp_data.get('qty', 1)

        # Build description from multiple fields
        desc_parts = []

        # Value (resistance/capacitance)
        if 'value' in comp_data:
            value_str = comp_data['value']
            # Format value nicely
            if value_str.endswith('m'):  # milliohms
                desc_parts.append(value_str.replace('m', 'mΩ'))
            elif value_str.endswith('k'):  # kilohms
                desc_parts.append(value_str.replace('k', 'kΩ'))
            elif value_str.endswith('R'):  # ohms
                desc_parts.append(value_str)
            elif value_str.endswith('F'):  # farads
                desc_parts.append(value_str)
            else:
                desc_parts.append(value_str)

        # Tolerance
        if 'tolerance' in comp_data:
            desc_parts.append(comp_data['tolerance'])

        # Voltage rating
        if 'voltage_rating' in comp_data:
            vr = comp_data['voltage_rating']
            if isinstance(vr, (int, float)):
                desc_parts.append(f"{vr}V")
            else:
                desc_parts.append(vr)  # Already formatted

        # Dielectric (for caps)
        if 'dielectric' in comp_data:
            desc_parts.append(comp_data['dielectric'])

        # Power rating
        if 'power_rating' in comp_data:
            pr = comp_data['power_rating']
            desc_parts.append(pr)

        # Current rating (for inductors)
        if 'current_rating' in comp_data:
            cr = comp_data['current_rating']
            desc_parts.append(f"{cr} rated")

        # Package
        if 'package' in comp_data:
            desc_parts.append(comp_data['package'])

        # Main description
        if 'description' in comp_data:
            desc_parts.append(comp_data['description'])

        # Criticality warning
        if comp_data.get('criticality') == 'CRITICAL':
            desc_parts.append("(CRITICAL)")

        # Datasheet reference
        if 'datasheet_ref' in comp_data:
            desc_parts.append(f"[{comp_data['datasheet_ref']}]")

        # Build final description
        description = ' '.join(desc_parts)

        # Add notes if present
        if 'notes' in comp_data:
            description += f" | {comp_data['notes']}"

        # Add calculation if present
        if 'calculation' in comp_data:
            description += f" | Calc: {comp_data['calculation']}"

        bom_rows.append({
            'Ref': ref_designator,
            'Part Number': part_number,
            'Qty': qty,
            'Description': description
        })

    # Write CSV
    with open(bom_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Ref', 'Part Number', 'Qty', 'Description']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bom_rows)

    print(f"Generated BOM with {len(bom_rows)} components")
    return 0


if __name__ == "__main__":
    try:
        generate_bom()
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
