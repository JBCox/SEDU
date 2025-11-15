#!/usr/bin/env python3
"""
SEDU Power System Verification Calculations (Database-Driven)

UPDATED: Now reads all power calculation values from design_database.yaml

Verifies all power calculations, component ratings, and margins
Exit codes: 0 = all calculations verified, 1 = calculation mismatch
"""

import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "design_database.yaml"


def load_database():
    """Load design database from YAML."""
    if not DATABASE.exists():
        print(f"[power_calcs] ERROR: Database not found: {DATABASE}")
        sys.exit(1)

    try:
        with open(DATABASE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[power_calcs] ERROR: Failed to parse database: {e}")
        sys.exit(1)


def get_locked_value(db, component_ref):
    """Get locked value from verification_rules section."""
    locked_values = db.get('verification_rules', {}).get('locked_values', [])

    for entry in locked_values:
        if entry.get('component') == component_ref:
            value_str = entry.get('value', '')
            # Parse value string (e.g., "3.0m" -> 0.003, "140k" -> 140000)
            if value_str.endswith('m'):  # milliohms
                return float(value_str[:-1]) / 1000
            elif value_str.endswith('k'):  # kilohms
                return float(value_str[:-1]) * 1000
            elif value_str.endswith('nF'):  # nanofarads
                return float(value_str[:-2]) * 1e-9
            elif value_str.endswith('uH'):  # microhenrys
                return float(value_str[:-2]) * 1e-6
            else:
                return float(value_str)
    return None


def get_component_value(db, ref):
    """Get component value from components section."""
    components = db.get('components', {})
    if ref in components:
        value_str = components[ref].get('value', '')
        # Parse value (same logic as locked values)
        if value_str.endswith('m'):
            return float(value_str[:-1]) / 1000
        elif value_str.endswith('k'):
            return float(value_str[:-1]) * 1000
        elif value_str.endswith('R'):
            return float(value_str[:-1])
        else:
            try:
                return float(value_str)
            except ValueError:
                return None
    return None


def main():
    # Load database
    db = load_database()

    # Extract firmware constants
    fw_const = db.get('firmware_constants', {})

    # Extract locked values
    RS_IN = get_locked_value(db, 'RS_IN')
    R_VBAT_TOP = get_locked_value(db, 'R_VBAT_TOP')
    R_VBAT_BOT = get_locked_value(db, 'R_VBAT_BOT')
    R_ILIM = get_locked_value(db, 'R_ILIM')
    R_IPROPI = get_locked_value(db, 'R_IPROPI')
    RS_U = get_locked_value(db, 'RS_U')  # All phase shunts should be same value

    # Extract firmware constants
    VBAT_MIN = fw_const.get('VBAT_MIN', 18.0)
    VBAT_MAX = fw_const.get('VBAT_MAX', 25.2)
    CSA_GAIN = fw_const.get('CSA_GAIN', 20.0)
    PHASE_SHUNT_R = fw_const.get('PHASE_SHUNT_R', 0.002)

    # Extract IC data
    ics = db.get('ics', {})
    u4_data = ics.get('U4', {})
    V_out_buck = u4_data.get('output_voltage', 3.3)

    # Get MOSFET voltage rating from components
    components = db.get('components', {})
    q1_data = components.get('Q1', {})
    V_mosfet_rating = q1_data.get('voltage_rating', 60)

    print('='*70)
    print('SEDU POWER SYSTEM VERIFICATION (Database-Driven)')
    print('='*70)
    print()

    # Validation check
    all_ok = True

    # 1. LM5069 ILIM Calculation
    print('1. LM5069 CURRENT LIMIT VERIFICATION')
    print('-'*70)

    if RS_IN is None:
        print('[ERROR] RS_IN not found in database locked_values')
        return 1

    Rsense = RS_IN
    V_ILIM = 55e-3   # 55 mV typical threshold (from LM5069 datasheet)
    I_LIM = V_ILIM / Rsense

    print(f'   Rsense (database): {Rsense*1000:.1f} mOhm')
    print(f'   V_ILIM threshold:  {V_ILIM*1000:.1f} mV')
    print(f'   ILIM calculated:   {I_LIM:.2f} A')
    print(f'   Expected ILIM:     18.3 A')
    match_ilim = abs(I_LIM - 18.3) < 0.1
    print(f'   [{"OK" if match_ilim else "FAIL"}] MATCH: {match_ilim}')
    all_ok = all_ok and match_ilim
    print()

    # Circuit Breaker
    V_CB = 105e-3  # 105 mV circuit breaker threshold
    I_CB = V_CB / Rsense
    print(f'   Circuit Breaker:')
    print(f'   V_CB threshold:   {V_CB*1000:.1f} mV')
    print(f'   I_CB calculated:  {I_CB:.1f} A')
    print(f'   Expected I_CB:    35 A')
    match_cb = abs(I_CB - 35) < 1
    print(f'   [{"OK" if match_cb else "FAIL"}] MATCH: {match_cb}')
    all_ok = all_ok and match_cb
    print()

    # Power dissipation in sense resistor
    I_peak = 18.3
    P_sense_peak = I_peak**2 * Rsense
    P_sense_CB = I_CB**2 * Rsense
    print(f'   Power dissipation in Rsense:')
    print(f'   At ILIM ({I_LIM:.1f}A): {P_sense_peak:.2f} W')
    print(f'   At CB ({I_CB:.1f}A):    {P_sense_CB:.2f} W (brief)')
    print(f'   Rsense rating:    >=3 W')
    adequate_sense = P_sense_peak < 3.0
    print(f'   [{"OK" if adequate_sense else "FAIL"}] ADEQUATE: {adequate_sense}')
    all_ok = all_ok and adequate_sense
    print()

    # 2. Battery Voltage Divider
    print('2. BATTERY VOLTAGE DIVIDER VERIFICATION')
    print('-'*70)

    if R_VBAT_TOP is None or R_VBAT_BOT is None:
        print('[ERROR] Battery divider values not found in database')
        return 1

    R_high = R_VBAT_TOP
    R_low = R_VBAT_BOT
    V_bat_max = VBAT_MAX
    V_bat_min = VBAT_MIN

    V_adc_max = V_bat_max * R_low / (R_high + R_low)
    V_adc_min = V_bat_min * R_low / (R_high + R_low)
    V_adc_fullscale = 3.5  # ADC_11db full scale (conservative)

    print(f'   Divider (database): {R_high/1000:.1f}kOhm / {R_low/1000:.1f}kOhm')
    print(f'   At V_bat_max ({V_bat_max}V): {V_adc_max:.3f} V')
    print(f'   At V_bat_min ({V_bat_min}V): {V_adc_min:.3f} V')
    print(f'   ADC full scale (11dB):        {V_adc_fullscale} V')
    print(f'   Margin at max:                {((V_adc_fullscale - V_adc_max)/V_adc_fullscale)*100:.1f}%')
    adequate_divider = V_adc_max < V_adc_fullscale * 0.9
    print(f'   [{"OK" if adequate_divider else "FAIL"}] ADEQUATE MARGIN: {adequate_divider}')
    all_ok = all_ok and adequate_divider
    print()

    # 3. DRV8873 ILIM Calculation
    print('3. DRV8873 ACTUATOR CURRENT LIMIT')
    print('-'*70)

    if R_ILIM is None:
        print('[ERROR] R_ILIM not found in database locked_values')
        return 1

    K_ILIM = 5200    # V from datasheet
    I_lim_act = K_ILIM / R_ILIM

    print(f'   R_ILIM (database): {R_ILIM/1000:.2f} kOhm')
    print(f'   I_ILIM = 5200/R:   {I_lim_act:.2f} A')
    print(f'   Expected:          3.29 A')
    match_act_ilim = abs(I_lim_act - 3.29) < 0.01
    print(f'   [{"OK" if match_act_ilim else "FAIL"}] MATCH: {match_act_ilim}')
    all_ok = all_ok and match_act_ilim
    print()

    # 4. DRV8873 IPROPI Calculation
    print('4. DRV8873 IPROPI CURRENT MIRROR')
    print('-'*70)

    if R_IPROPI is None:
        print('[ERROR] R_IPROPI not found in database locked_values')
        return 1

    K_IPROPI = 1100    # A/A gain from datasheet
    I_act_max = 3.3    # Max actuator current

    # V_IPROPI = (I_act / K_IPROPI) * R_IPROPI
    V_IPROPI_at_3A = (3.0 * R_IPROPI) / K_IPROPI
    V_IPROPI_at_33A = (3.3 * R_IPROPI) / K_IPROPI
    V_ADC_max = 3.5

    print(f'   R_IPROPI (database): {R_IPROPI/1000:.2f} kOhm')
    print(f'   At 3.0A:             {V_IPROPI_at_3A:.3f} V')
    print(f'   At 3.3A:             {V_IPROPI_at_33A:.3f} V')
    print(f'   ADC max (11dB):      {V_ADC_max} V')
    print(f'   Margin at 3.3A:      {((V_ADC_max - V_IPROPI_at_33A)/V_ADC_max)*100:.1f}%')
    within_range_ipropi = V_IPROPI_at_33A < V_ADC_max
    print(f'   [{"OK" if within_range_ipropi else "FAIL"}] WITHIN RANGE: {within_range_ipropi}')
    all_ok = all_ok and within_range_ipropi
    print()

    # 5. Motor CSA Calculation
    print('5. MOTOR CURRENT SENSE AMPLIFIER (DRV8353RS)')
    print('-'*70)

    R_shunt = PHASE_SHUNT_R
    CSA_gain_val = CSA_GAIN
    I_phase_max = 25  # Peak phase current

    V_shunt_max = I_phase_max * R_shunt
    V_CSA_out = V_shunt_max * CSA_gain_val

    print(f'   Shunt resistance (database): {R_shunt*1000:.1f} mOhm')
    print(f'   CSA gain (database):         {CSA_gain_val:.0f} V/V')
    print(f'   At I_phase_max ({I_phase_max}A):')
    print(f'   V_shunt:                     {V_shunt_max*1000:.1f} mV')
    print(f'   V_CSA_out:                   {V_CSA_out:.2f} V')
    print(f'   ADC range:                   0 - {V_ADC_max} V')
    within_range_csa = V_CSA_out < V_ADC_max
    print(f'   [{"OK" if within_range_csa else "FAIL"}] WITHIN RANGE: {within_range_csa}')
    all_ok = all_ok and within_range_csa
    print()

    # Power in shunt at peak
    P_shunt_peak = I_phase_max**2 * R_shunt
    print(f'   Power in shunt at {I_phase_max}A: {P_shunt_peak:.2f} W')
    print(f'   Shunt rating:     >=5 W pulse')
    adequate_shunt = P_shunt_peak < 5.0
    print(f'   [{"OK" if adequate_shunt else "FAIL"}] ADEQUATE: {adequate_shunt}')
    all_ok = all_ok and adequate_shunt
    print()

    # 6. Buck Converter Power Dissipation
    print('6. BUCK CONVERTER POWER CALCULATIONS')
    print('-'*70)

    # LMR33630 (24V->3.3V) - Single-stage conversion
    V_in_buck = 24.0
    I_out_buck = 3.0  # Max output current (all logic)
    eta_buck = 0.88   # 88% efficiency (lower due to large voltage step)

    P_out_buck = V_out_buck * I_out_buck
    P_in_buck = P_out_buck / eta_buck
    P_loss_buck = P_in_buck - P_out_buck

    print(f'   LMR33630 (24V->{V_out_buck}V @ 400kHz) - Single-stage:')
    print(f'   Input:            {V_in_buck}V')
    print(f'   Output (database):{V_out_buck}V @ {I_out_buck}A')
    print(f'   Efficiency:       {eta_buck*100:.0f}%')
    print(f'   P_out:            {P_out_buck:.2f} W')
    print(f'   P_in:             {P_in_buck:.2f} W')
    print(f'   P_loss:           {P_loss_buck:.2f} W')
    print(f'   Previous (two-stage): 1.08 W loss')
    print(f'   Trade-off: +0.27W loss for simpler design (1 IC vs 2)')
    print()

    print(f'   NOTE: 5V rail eliminated. TPS62133 removed from design.')
    print(f'   Single-stage simpler (1 IC vs 2), fewer components, better reliability.')
    print()

    # 7. Worst Case Power Budget
    print('7. WORST CASE POWER BUDGET ANALYSIS')
    print('-'*70)

    # Motor
    I_motor_peak_phase = 20.0  # Peak phase current (datasheet)
    duty_cycle = 0.90          # High duty at spin-up
    eta_motor = 0.90           # Motor + driver efficiency
    I_motor_battery = (I_motor_peak_phase * duty_cycle) / eta_motor

    # Actuator
    I_actuator = 3.3  # ILIM setting

    # Buck converter (reflected to 24V)
    P_logic = P_out_buck  # Total logic power (single buck now)
    I_buck_reflected = P_logic / V_in_buck

    # Total
    I_total_worst = I_motor_battery + I_actuator + I_buck_reflected

    print(f'   Motor (peak spin-up):')
    print(f'   - Phase current:        {I_motor_peak_phase} A')
    print(f'   - Duty cycle:           {duty_cycle*100:.0f}%')
    print(f'   - Efficiency:           {eta_motor*100:.0f}%')
    print(f'   - Battery current:      {I_motor_battery:.1f} A')
    print()
    print(f'   Actuator:               {I_actuator} A')
    print(f'   Buck converter:         {I_buck_reflected:.1f} A')
    print()
    print(f'   TOTAL WORST CASE:       {I_total_worst:.1f} A')
    print(f'   LM5069 ILIM (database): {I_LIM:.1f} A')
    print(f'   Margin:                 {((I_LIM - I_total_worst)/I_LIM)*100:.1f}%')
    print()

    if I_total_worst > I_LIM:
        print(f'   [WARNING] Worst case exceeds ILIM!')
        print(f'   -> REQUIRES firmware interlock to prevent simultaneous high-power operation')
    else:
        print(f'   [OK] ADEQUATE: Within ILIM with {((I_LIM - I_total_worst)/I_LIM)*100:.1f}% margin')
    print()

    # 8. Component Voltage Ratings
    print('8. COMPONENT VOLTAGE RATINGS')
    print('-'*70)
    V_system_max = VBAT_MAX
    V_system_nominal = 24.0

    print(f'   System voltage (database):')
    print(f'   - Nominal:        {V_system_nominal}V')
    print(f'   - Maximum (6S):   {V_system_max}V')
    print()

    # MOSFETs
    margin_mosfet = ((V_mosfet_rating - V_system_max) / V_system_max) * 100
    print(f'   MOSFETs (database):')
    print(f'   - Rating:         {V_mosfet_rating}V')
    print(f'   - Margin:         {margin_mosfet:.0f}%')
    adequate_mosfet = margin_mosfet > 100
    print(f'   [{"OK" if adequate_mosfet else "FAIL"}] ADEQUATE: {adequate_mosfet}')
    all_ok = all_ok and adequate_mosfet
    print()

    # TVS
    V_tvs_standoff = 33
    V_tvs_clamp = 53.3  # Typical clamping at 1A
    print(f'   TVS (SMBJ33A):')
    print(f'   - Standoff:       {V_tvs_standoff}V')
    print(f'   - Clamp (typ):    {V_tvs_clamp}V')
    adequate_tvs = V_tvs_standoff > V_system_max
    print(f'   [{"OK" if adequate_tvs else "FAIL"}] ADEQUATE: {adequate_tvs}')
    all_ok = all_ok and adequate_tvs
    print()

    print('='*70)
    if all_ok:
        print('[PASS] ALL POWER CALCULATIONS VERIFIED')
    else:
        print('[FAIL] POWER CALCULATION ERRORS DETECTED')
    print('='*70)

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
