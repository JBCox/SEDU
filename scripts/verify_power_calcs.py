#!/usr/bin/env python3
"""
SEDU Power System Verification Calculations - Agent 1
Verifies all power calculations, component ratings, and margins
"""

print('='*70)
print('SEDU POWER SYSTEM VERIFICATION - AGENT 1')
print('='*70)
print()

# 1. LM5069 ILIM Calculation
print('1. LM5069 CURRENT LIMIT VERIFICATION')
print('-'*70)
Rsense = 3.0e-3  # 3.0 mΩ
V_ILIM = 55e-3   # 55 mV typical threshold
I_LIM = V_ILIM / Rsense
print(f'   Rsense:           {Rsense*1000:.1f} mOhm')
print(f'   V_ILIM threshold: {V_ILIM*1000:.1f} mV')
print(f'   ILIM calculated:  {I_LIM:.2f} A')
print(f'   Expected ILIM:    18.3 A')
print(f'   [OK] MATCH: {abs(I_LIM - 18.3) < 0.1}')
print()

# Circuit Breaker
V_CB = 105e-3  # 105 mV circuit breaker threshold
I_CB = V_CB / Rsense
print(f'   Circuit Breaker:')
print(f'   V_CB threshold:   {V_CB*1000:.1f} mV')
print(f'   I_CB calculated:  {I_CB:.1f} A')
print(f'   Expected I_CB:    35 A')
print(f'   ✓ MATCH: {abs(I_CB - 35) < 1}')
print()

# Power dissipation in sense resistor
I_peak = 18.3
P_sense_peak = I_peak**2 * Rsense
P_sense_CB = I_CB**2 * Rsense
print(f'   Power dissipation in Rsense:')
print(f'   At ILIM ({I_LIM:.1f}A): {P_sense_peak:.2f} W')
print(f'   At CB ({I_CB:.1f}A):    {P_sense_CB:.2f} W (brief)')
print(f'   Rsense rating:    ≥3 W')
print(f'   ✓ ADEQUATE: {P_sense_peak < 3.0}')
print()

# 2. Battery Voltage Divider
print('2. BATTERY VOLTAGE DIVIDER VERIFICATION')
print('-'*70)
R_high = 140e3   # 140 kΩ
R_low = 10.0e3   # 10.0 kΩ
V_bat_max = 25.2  # 6S max voltage
V_bat_min = 18.0  # 6S min voltage

V_adc_max = V_bat_max * R_low / (R_high + R_low)
V_adc_min = V_bat_min * R_low / (R_high + R_low)
V_adc_fullscale = 3.5  # ADC_11db full scale (conservative)

print(f'   Divider: {R_high/1000:.1f}kΩ / {R_low/1000:.1f}kΩ (1%)')
print(f'   At V_bat_max ({V_bat_max}V): {V_adc_max:.3f} V')
print(f'   At V_bat_min ({V_bat_min}V): {V_adc_min:.3f} V')
print(f'   ADC full scale (11dB):       {V_adc_fullscale} V')
print(f'   Margin at max:               {((V_adc_fullscale - V_adc_max)/V_adc_fullscale)*100:.1f}%')
print(f'   ✓ ADEQUATE MARGIN: {V_adc_max < V_adc_fullscale * 0.9}')
print()

# 3. DRV8873 ILIM Calculation
print('3. DRV8873 ACTUATOR CURRENT LIMIT')
print('-'*70)
R_ILIM = 1.58e3  # 1.58 kΩ
K_ILIM = 5200    # V from datasheet
I_lim_act = K_ILIM / R_ILIM
print(f'   R_ILIM:           {R_ILIM/1000:.2f} kΩ')
print(f'   I_ILIM = 5200/R:  {I_lim_act:.2f} A')
print(f'   Expected:         3.29 A')
print(f'   ✓ MATCH: {abs(I_lim_act - 3.29) < 0.01}')
print()

# 4. DRV8873 IPROPI Calculation
print('4. DRV8873 IPROPI CURRENT MIRROR')
print('-'*70)
R_IPROPI = 1.00e3  # 1.00 kΩ
K_IPROPI = 1100    # A/A gain from datasheet
I_act_max = 3.3    # Max actuator current

# V_IPROPI = (I_act / K_IPROPI) * R_IPROPI
V_IPROPI_at_3A = (3.0 * R_IPROPI) / K_IPROPI
V_IPROPI_at_33A = (3.3 * R_IPROPI) / K_IPROPI
V_ADC_max = 3.5

print(f'   R_IPROPI:         {R_IPROPI/1000:.2f} kΩ')
print(f'   At 3.0A:          {V_IPROPI_at_3A:.3f} V')
print(f'   At 3.3A:          {V_IPROPI_at_33A:.3f} V')
print(f'   ADC max (11dB):   {V_ADC_max} V')
print(f'   Margin at 3.3A:   {((V_ADC_max - V_IPROPI_at_33A)/V_ADC_max)*100:.1f}%')
print(f'   ✓ WITHIN RANGE: {V_IPROPI_at_33A < V_ADC_max}')
print()

# 5. Motor CSA Calculation
print('5. MOTOR CURRENT SENSE AMPLIFIER (DRV8353RS)')
print('-'*70)
R_shunt = 2.0e-3  # 2 mΩ
CSA_gain = 20     # 20 V/V
I_phase_max = 25  # Peak phase current

V_shunt_max = I_phase_max * R_shunt
V_CSA_out = V_shunt_max * CSA_gain

print(f'   Shunt resistance: {R_shunt*1000:.1f} mOhm')
print(f'   CSA gain:         {CSA_gain} V/V')
print(f'   At I_phase_max ({I_phase_max}A):')
print(f'   V_shunt:          {V_shunt_max*1000:.1f} mV')
print(f'   V_CSA_out:        {V_CSA_out:.2f} V')
print(f'   ADC range:        0 - {V_ADC_max} V')
print(f'   ✓ WITHIN RANGE: {V_CSA_out < V_ADC_max}')
print()

# Power in shunt at peak
P_shunt_peak = I_phase_max**2 * R_shunt
print(f'   Power in shunt at {I_phase_max}A: {P_shunt_peak:.2f} W')
print(f'   Shunt rating:     ≥5 W pulse')
print(f'   ✓ ADEQUATE: {P_shunt_peak < 5.0}')
print()

# 6. Buck Converter Power Dissipation
print('6. BUCK CONVERTER POWER CALCULATIONS')
print('-'*70)

# LMR33630 (24V→5V)
V_in_buck1 = 24.0
V_out_buck1 = 5.0
I_out_buck1 = 2.0  # Max output current
eta_buck1 = 0.92   # 92% efficiency

P_out_buck1 = V_out_buck1 * I_out_buck1
P_in_buck1 = P_out_buck1 / eta_buck1
P_loss_buck1 = P_in_buck1 - P_out_buck1

print(f'   LMR33630 (24V→5V @ 400kHz):')
print(f'   Input:            {V_in_buck1}V')
print(f'   Output:           {V_out_buck1}V @ {I_out_buck1}A')
print(f'   Efficiency:       {eta_buck1*100:.0f}%')
print(f'   P_out:            {P_out_buck1:.2f} W')
print(f'   P_in:             {P_in_buck1:.2f} W')
print(f'   P_loss:           {P_loss_buck1:.2f} W')
print(f'   Spec target:      0.87 W')
print(f'   ✓ CLOSE: {abs(P_loss_buck1 - 0.87) < 0.2}')
print()

# TPS62133 (5V→3.3V)
V_in_buck2 = 5.0
V_out_buck2 = 3.3
I_out_buck2 = 1.0  # Typical load
eta_buck2 = 0.94   # 94% efficiency

P_out_buck2 = V_out_buck2 * I_out_buck2
P_in_buck2 = P_out_buck2 / eta_buck2
P_loss_buck2 = P_in_buck2 - P_out_buck2

print(f'   TPS62133 (5V→3.3V):')
print(f'   Input:            {V_in_buck2}V')
print(f'   Output:           {V_out_buck2}V @ {I_out_buck2}A')
print(f'   Efficiency:       {eta_buck2*100:.0f}%')
print(f'   P_out:            {P_out_buck2:.2f} W')
print(f'   P_in:             {P_in_buck2:.2f} W')
print(f'   P_loss:           {P_loss_buck2:.2f} W')
print(f'   ✓ LOW DISSIPATION: {P_loss_buck2 < 0.5}')
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

# Buck converters (reflected to 24V)
P_logic = P_out_buck1  # Total logic power
I_buck_reflected = P_logic / V_in_buck1

# Total
I_total_worst = I_motor_battery + I_actuator + I_buck_reflected

print(f'   Motor (peak spin-up):')
print(f'   - Phase current:        {I_motor_peak_phase} A')
print(f'   - Duty cycle:           {duty_cycle*100:.0f}%')
print(f'   - Efficiency:           {eta_motor*100:.0f}%')
print(f'   - Battery current:      {I_motor_battery:.1f} A')
print()
print(f'   Actuator:               {I_actuator} A')
print(f'   Buck converters:        {I_buck_reflected:.1f} A')
print()
print(f'   TOTAL WORST CASE:       {I_total_worst:.1f} A')
print(f'   LM5069 ILIM:            {I_LIM:.1f} A')
print(f'   Margin:                 {((I_LIM - I_total_worst)/I_LIM)*100:.1f}%')
print()

if I_total_worst > I_LIM:
    print(f'   [WARNING] Worst case exceeds ILIM!')
    print(f'   -> REQUIRES firmware interlock to prevent simultaneous high-power operation')
else:
    print(f'   ✓ ADEQUATE: Within ILIM with {((I_LIM - I_total_worst)/I_LIM)*100:.1f}% margin')
print()

# 8. Component Voltage Ratings
print('8. COMPONENT VOLTAGE RATINGS')
print('-'*70)
V_system_max = 25.2  # 6S fully charged
V_system_nominal = 24.0

print(f'   System voltage:')
print(f'   - Nominal:        {V_system_nominal}V')
print(f'   - Maximum (6S):   {V_system_max}V')
print()

# MOSFETs
V_mosfet_rating = 60
margin_mosfet = ((V_mosfet_rating - V_system_max) / V_system_max) * 100
print(f'   MOSFETs:')
print(f'   - Rating:         {V_mosfet_rating}V')
print(f'   - Margin:         {margin_mosfet:.0f}%')
print(f'   ✓ ADEQUATE: {margin_mosfet > 100}')
print()

# TVS
V_tvs_standoff = 33
V_tvs_clamp = 53.3  # Typical clamping at 1A
print(f'   TVS (SMBJ33A):')
print(f'   - Standoff:       {V_tvs_standoff}V')
print(f'   - Clamp (typ):    {V_tvs_clamp}V')
print(f'   ✓ ADEQUATE: {V_tvs_standoff > V_system_max}')
print()

print('='*70)
print('VERIFICATION COMPLETE')
print('='*70)
