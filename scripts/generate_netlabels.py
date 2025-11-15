#!/usr/bin/env python3
"""
Generate Net Labels (hardware/Net_Labels.csv) from design_database.yaml

This script creates the net label CSV file from the single-source database.
DO NOT edit Net_Labels.csv directly - edit design_database.yaml and regenerate.
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


def generate_netlabels():
    """Generate Net Labels CSV from design database."""
    db = load_database()
    gpio_pins = db.get('gpio_pins', {})
    power_rails = db.get('power_rails', {})

    netlabels_path = Path(__file__).parent.parent / "hardware" / "Net_Labels.csv"

    # Collect net labels
    net_rows = []

    # Add power rails
    for rail_name, rail_data in sorted(power_rails.items()):
        net_rows.append({
            'Net': rail_name,
            'Type': 'Power',
            'Description': rail_data.get('description', '')
        })

    # Add GPIO nets
    for gpio_num, pin_data in sorted(gpio_pins.items(), key=lambda x: int(x[0].replace('GPIO', ''))):
        function = pin_data['function']
        description = pin_data.get('description', '')
        direction = pin_data.get('direction', 'unknown')

        # Map direction to type
        if direction == 'input':
            net_type = 'Input'
        elif direction == 'output':
            net_type = 'Output'
        elif direction == 'bidir':
            net_type = 'Bidirectional'
        else:
            net_type = 'Signal'

        net_rows.append({
            'Net': function,
            'Type': net_type,
            'Description': f"{description} ({gpio_num})"
        })

    # Add common nets
    common_nets = [
        {'Net': 'GND', 'Type': 'Power', 'Description': 'Ground'},
        {'Net': 'MOTOR_PH_U', 'Type': 'Power', 'Description': 'Motor phase U power'},
        {'Net': 'MOTOR_PH_V', 'Type': 'Power', 'Description': 'Motor phase V power'},
        {'Net': 'MOTOR_PH_W', 'Type': 'Power', 'Description': 'Motor phase W power'},
    ]
    net_rows.extend(common_nets)

    # Write CSV
    with open(netlabels_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Net', 'Type', 'Description']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(net_rows)

    print(f"Generated Net Labels with {len(net_rows)} nets")
    return 0


if __name__ == "__main__":
    try:
        generate_netlabels()
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
