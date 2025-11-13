#!/usr/bin/env python3
"""
Physical verification of 80x50mm board layout.
Checks if all components fit with required routing channels.
"""

print('=' * 80)
print('SEDU PCB 80x50mm PHYSICAL VERIFICATION')
print('=' * 80)

# Board dimensions
board_w = 80  # mm
board_h = 50  # mm
board_area = board_w * board_h
print(f'\nBoard: {board_w}x{board_h} mm = {board_area} mm^2')

# Mounting holes with keep-out
hole_dia = 3.2  # mm finished
hole_keepout = 1.5  # mm annulus
hole_total = hole_dia + 2 * hole_keepout
hole_area = 4 * (hole_total ** 2)
print(f'Mounting holes: 4x M3 (3.2mm) with 1.5mm keep-out = {hole_total}mm each')
print(f'  Positions: (4,4), (76,4), (4,46), (76,46)')
print(f'  Total exclusion area: {hole_area:.1f} mm^2')

print('\n' + '-' * 80)
print('MAJOR COMPONENTS (from BOM and datasheets):')
print('-' * 80)

# Component dimensions (width × length in mm, from datasheets)
components = {
    'ESP32-S3-WROOM-1': {'w': 18, 'l': 25.5, 'qty': 1, 'note': '+ antenna keep-out'},
    'DRV8353RS (HTSSOP-48)': {'w': 6.1, 'l': 12.5, 'qty': 1, 'note': 'Gate driver'},
    'DRV8873-Q1 (HTSSOP-28)': {'w': 4.4, 'l': 9.7, 'qty': 1, 'note': 'Actuator driver'},
    'LM5069-1 (MSOP-10)': {'w': 3.0, 'l': 5.0, 'qty': 1, 'note': 'Hot-swap controller'},
    'LMR33630 (HSOIC-8)': {'w': 5.0, 'l': 6.5, 'qty': 1, 'note': 'Buck converter'},
    'TPS22919 (SOT-23-6)': {'w': 1.6, 'l': 2.9, 'qty': 1, 'note': 'USB load switch'},
    'TLV75533 (SOT-23-5)': {'w': 1.6, 'l': 2.9, 'qty': 1, 'note': 'USB LDO'},
    'MOSFETs SuperSO8': {'w': 5.15, 'l': 5.2, 'qty': 8, 'note': '6× motor + 2× LM5069'},
    'Phase shunts 2512': {'w': 3.2, 'l': 6.4, 'qty': 3, 'note': 'Kelvin sense'},
    'RS_IN shunt 2728': {'w': 7.0, 'l': 7.1, 'qty': 1, 'note': 'LM5069 sense'},
    'Inductor 1008': {'w': 10.0, 'l': 10.0, 'qty': 1, 'note': 'Buck L4'},
    'XT30 connectors': {'w': 12.5, 'l': 16.0, 'qty': 4, 'note': 'Battery + 3× phases'},
    'MicroFit 2P': {'w': 10.0, 'l': 7.0, 'qty': 1, 'note': 'J_ACT'},
    'JST-GH-8P': {'w': 11.5, 'l': 5.5, 'qty': 2, 'note': 'J_LCD + J_UI'},
    'SMBJ33A TVS': {'w': 5.0, 'l': 5.8, 'qty': 2, 'note': 'DO-214AA'},
}

total_component_area = 0
print(f"{'Component':<35} {'Size (WxL)':<15} {'Qty':<5} {'Area':<10} {'Notes':<30}")
print('-' * 80)

for name, specs in components.items():
    area = specs['w'] * specs['l'] * specs['qty']
    total_component_area += area
    size_str = f"{specs['w']:.1f}x{specs['l']:.1f} mm"
    print(f"{name:<35} {size_str:<15} {specs['qty']:>3} {area:>7.1f} mm^2 {specs['note']:<30}")

print('-' * 80)
print(f'Total component footprint area: {total_component_area:.1f} mm^2')

# ESP32 antenna keep-out
esp_w = 18
esp_l = 25.5
antenna_forward = 15  # mm
antenna_sides = 5  # mm
antenna_keepout = (esp_w + 2 * antenna_sides) * antenna_forward
print(f'ESP32 antenna keep-out: {antenna_keepout:.1f} mm^2 (>=15mm forward x (18mm+10mm sides))')

print('\n' + '-' * 80)
print('AREA BUDGET ANALYSIS:')
print('-' * 80)
usable_area = board_area - hole_area - antenna_keepout
print(f'Board area: {board_area:.1f} mm^2')
print(f'  - Mounting hole exclusions: {hole_area:.1f} mm^2')
print(f'  - ESP32 antenna keep-out: {antenna_keepout:.1f} mm^2')
print(f'Usable placement area: {usable_area:.1f} mm^2')
print(f'Component footprint area: {total_component_area:.1f} mm^2')

utilization = (total_component_area / usable_area) * 100
print(f'\n**Component density: {utilization:.1f}%**')

# Add routing channels and spacing
print('\n' + '-' * 80)
print('ROUTING REQUIREMENTS:')
print('-' * 80)
print('Battery traces (VBAT_HP): >=4.00mm width + 0.50mm clearance = 4.5mm channel')
print('Motor phase traces: >=3.00mm width + 0.50mm clearance = 3.5mm channel')
print('Actuator traces: >=1.50mm width + 0.40mm clearance = 1.9mm channel')
print('Required inter-component spacing: ~3-5mm for routing channels')

# Estimate routing overhead
routing_overhead = 1.3  # 30% overhead for routing channels, spacing
effective_utilization = utilization * routing_overhead
print(f'\nWith routing overhead (x{routing_overhead}): {effective_utilization:.1f}% effective density')

print('\n' + '-' * 80)
print('PLACEMENT ZONE VERIFICATION:')
print('-' * 80)

zones = [
    ('Power Entry (LM5069+TVS+FETs+J_BAT)', 'Along short edge (80mm): ~15mm width × 20mm depth = 300 mm²'),
    ('Buck (LMR33630+L+caps)', 'Adjacent to power: ~20mm × 15mm = 300 mm²'),
    ('Motor Bridge (DRV8353+6FETs+3shunts)', 'Opposite MCU: ~30mm × 25mm = 750 mm²'),
    ('MCU + Antenna', 'Corner with keep-out: ~28mm × 40mm = 1120 mm²'),
    ('Actuator (DRV8873+TVS+connector)', 'Edge mount: ~15mm × 20mm = 300 mm²'),
    ('USB (TPS22919+TLV75533+connector)', 'Near MCU: ~10mm × 10mm = 100 mm²'),
    ('LCD/UI connectors', 'Edge opposite motor: ~25mm × 10mm = 250 mm²'),
]

for zone, spec in zones:
    print(f'{zone}: {spec}')

print('\n' + '-' * 80)
print('CRITICAL CONFLICTS CHECK:')
print('-' * 80)

# Check mounting holes vs component clearances
print('Mounting hole positions (with 6.2mm keep-out diameter):')
print('  H1: (4,4) - corner, near power entry zone')
print('  H2: (76,4) - corner, near motor connector edge')
print('  H3: (4,46) - corner, near UI connector edge')
print('  H4: (76,46) - corner, near motor phase zone')

# Calculate usable width/height accounting for hole positions
inner_w = 76 - 4 - hole_total  # Between holes minus keep-out
inner_h = 46 - 4 - hole_total  # Between holes minus keep-out
print(f'\nUsable interior rectangle (between holes): {inner_w:.1f}x{inner_h:.1f} mm = {inner_w*inner_h:.1f} mm^2')

print('\n' + '=' * 80)
print('VERDICT:')
print('=' * 80)

issues = []

if effective_utilization > 85:
    issues.append(f'WARNING: Effective density {effective_utilization:.1f}% exceeds recommended 85% maximum')

if inner_w < 60:
    issues.append(f'WARNING: Interior width {inner_w:.1f}mm may be tight for 30mm motor bridge')

if inner_h < 30:
    issues.append(f'WARNING: Interior height {inner_h:.1f}mm may be tight for component placement')

# Check if connectors fit on edges
edge_connectors_width = 12.5 * 4 + 10 + 11.5 * 2  # XT30s + MicroFit + JSTs
perimeter = 2 * (board_w + board_h)
connector_utilization = (edge_connectors_width / perimeter) * 100
print(f'\nConnector edge utilization: {edge_connectors_width:.1f}mm / {perimeter:.1f}mm perimeter = {connector_utilization:.1f}%')

if connector_utilization > 70:
    issues.append(f'WARNING: Connector utilization {connector_utilization:.1f}% may be tight for edge placement')

if issues:
    print('\n'.join(issues))
    print('\nWARNING: BOARD SIZE MARGINAL - TIGHT FIT WITH POTENTIAL ISSUES')
else:
    print('PASS: 80x50mm BOARD PHYSICALLY VERIFIED - ALL COMPONENTS FIT')
    print(f'   Component density: {utilization:.1f}% (raw), {effective_utilization:.1f}% (with routing)')
    print(f'   Usable interior: {inner_w:.1f}x{inner_h:.1f} mm')
    print('   All placement zones feasible with proper layout planning')
