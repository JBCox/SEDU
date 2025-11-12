#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supplemental Power & Thermal Analysis for SEDU Single-PCB
Agent 1: Power & Thermal Analysis Expert
"""

import sys
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('='*70)
print('SUPPLEMENTAL POWER & THERMAL ANALYSIS')
print('='*70)
print()

# 1. LMR33630 Thermal Analysis (24V->3.3V single-stage)
print('1. LMR33630 BUCK CONVERTER THERMAL ANALYSIS (24V->3.3V)')
print('-'*70)
Vin = 24.0
Vout = 3.3
Iout = 3.0  # Peak capability
Iout_typ = 0.7  # Typical load
eta = 0.88  # Efficiency at full load
Rth_ja = 40  # °C/W (HSOIC-8 with thermal vias)
Tamb = 85  # Worst case

# Switching losses
Fsw = 400e3  # 400kHz
Qg = 10e-9  # Gate charge (internal FET)
P_sw = Qg * Vin * Fsw * 1e3  # mW

# Conduction losses
Rds_on = 0.120  # 120mΩ typical for internal FET
D = Vout / Vin  # Duty cycle
Irms_hs = Iout * (D**0.5)  # HS FET RMS current
Irms_ls = Iout * ((1-D)**0.5)  # LS FET RMS current
P_cond = (Irms_hs**2 + Irms_ls**2) * Rds_on

# Total loss
P_loss_total = (Vout * Iout) * (1/eta - 1)
Tj = Tamb + P_loss_total * Rth_ja

print(f'   Input voltage:      {Vin:.1f} V')
print(f'   Output:             {Vout:.1f} V @ {Iout:.1f} A (peak)')
print(f'   Typical load:       {Iout_typ:.1f} A ({Iout_typ/Iout*100:.0f}% utilization)')
print(f'   Efficiency:         {eta*100:.0f}%')
print(f'   Duty cycle:         {D*100:.1f}%')
print(f'   Power loss:         {P_loss_total:.2f} W')
print(f'   Rth(j-a):           {Rth_ja:.0f} °C/W')
print(f'   Ambient temp:       {Tamb:.0f} °C')
print(f'   Junction temp:      {Tj:.1f} °C')
print(f'   Tj max:             150 °C')
print(f'   Margin:             {(150-Tj)/150*100:.1f}%')
print(f'   Status:             {"OK" if Tj < 150 else "FAIL"}')
print()
print(f'   NOTE: 8× thermal vias (Ø0.3mm) under PowerPAD MANDATORY')
print(f'   NOTE: Typical load ({Iout_typ}A): P_loss = {(Vout*Iout_typ)*(1/eta-1):.2f}W, Tj = {Tamb + (Vout*Iout_typ)*(1/eta-1)*Rth_ja:.1f}°C')
print()

# 2. Phase MOSFET Detailed Thermal
print('2. PHASE MOSFET THERMAL ANALYSIS (BSC016N06NS)')
print('-'*70)
Rds_on_25C = 1.6e-3  # 1.6mΩ @ 25°C
Rds_on_125C = 2.5e-3  # 2.5mΩ @ 125°C
I_phase_avg = 12.0  # RMS current
I_phase_peak = 20.0
Rth_ja = 150  # °C/W (SuperSO8, minimal airflow)
D_motor = 0.5  # 50% duty (sinusoidal avg)

# Conduction loss
P_cond_avg = I_phase_avg**2 * Rds_on_125C * D_motor
P_cond_peak = I_phase_peak**2 * Rds_on_125C * D_motor

# Switching loss (20kHz PWM)
Fsw_motor = 20e3
Coss = 1500e-12  # Output capacitance
Vds = 24
P_sw_est = 0.5 * Coss * Vds**2 * Fsw_motor

P_total_avg = P_cond_avg + P_sw_est
P_total_peak = P_cond_peak + P_sw_est * 2  # Assume 2× sw loss at peak

Tj_avg = Tamb + P_total_avg * Rth_ja
Tj_peak = Tamb + P_total_peak * Rth_ja

print(f'   Rds(on) @ 125°C:    {Rds_on_125C*1e3:.1f} mΩ')
print(f'   Phase current (avg):{I_phase_avg:.0f} A RMS')
print(f'   Phase current (pk): {I_phase_peak:.0f} A RMS')
print(f'   PWM frequency:      {Fsw_motor/1e3:.0f} kHz')
print()
print(f'   At 12A average:')
print(f'     Conduction loss:  {P_cond_avg:.3f} W')
print(f'     Switching loss:   {P_sw_est:.3f} W')
print(f'     Total loss:       {P_total_avg:.3f} W')
print(f'     Junction temp:    {Tj_avg:.1f} °C')
print(f'     Margin:           {(175-Tj_avg)/175*100:.1f}%')
print()
print(f'   At 20A peak (brief <1s):')
print(f'     Conduction loss:  {P_cond_peak:.3f} W')
print(f'     Switching loss:   {P_sw_est*2:.3f} W (est)')
print(f'     Total loss:       {P_total_peak:.3f} W')
print(f'     Junction temp:    {Tj_peak:.1f} °C')
print(f'     Status:           {"OK (<1s)" if Tj_peak < 175 else "CRITICAL"}')
print()

# 3. Total Board Power Dissipation
print('3. TOTAL BOARD POWER DISSIPATION ANALYSIS')
print('-'*70)

# Operating modes
print('   Operating Mode Analysis:')
print('   -' * 68)
print('   Mode              | Motor | Actuator | Logic | Total | Status')
print('   -' * 68)

# Idle
P_logic_idle = 0.5  # W
print(f'   Idle              | 0.0 W |  0.0 W   | {P_logic_idle:.1f} W | {P_logic_idle:.1f} W  | Continuous')

# Motor only (average)
P_motor_avg = 6 * P_total_avg  # 6 FETs
P_logic = 0.3  # Buck + ESP32
P_total_motor_avg = P_motor_avg + P_logic
print(f'   Motor (avg 12A)   | {P_motor_avg:.1f} W |  0.0 W   | {P_logic:.1f} W | {P_total_motor_avg:.1f} W | <5s bursts')

# Motor peak
P_motor_peak = 6 * P_total_peak
P_total_motor_peak = P_motor_peak + P_logic
print(f'   Motor (peak 20A)  | {P_motor_peak:.1f} W |  0.0 W   | {P_logic:.1f} W | {P_total_motor_peak:.1f} W | <1s brief')

# Actuator only
P_actuator = 4.4  # From DRV8873 thermal calc
P_total_actuator = P_actuator + P_logic
print(f'   Actuator (3.3A)   | 0.0 W |  {P_actuator:.1f} W   | {P_logic:.1f} W | {P_total_actuator:.1f} W | <10s (TIMEOUT)')

print('   -' * 68)
print()
print(f'   Board area:         75mm × 55mm = 4125 mm²')
print(f'   Typical dissipation:{P_total_motor_avg:.1f} W')
print(f'   Power density:      {P_total_motor_avg/4.125:.2f} W/cm²')
print(f'   Required thermal:   {P_total_motor_avg/(85-25):.2f} W/°C (60°C rise)')
print()

# 4. Connector Voltage Drop Analysis
print('4. CONNECTOR & WIRE VOLTAGE DROP ANALYSIS')
print('-'*70)

# Battery connector
print('   Battery Path (J_BAT + 14 AWG wire, 0.5m):')
R_wire_14awg = 8.28e-3  # Ω/m @ 80°C
L_cable = 0.5  # meters
R_total_bat = 2 * R_wire_14awg * L_cable  # Round trip
I_peak = 20.0
V_drop_bat = I_peak * R_total_bat
P_loss_bat = I_peak**2 * R_total_bat

print(f'     Wire resistance:  {R_total_bat*1e3:.2f} mΩ (round-trip)')
print(f'     At 20A peak:      {V_drop_bat*1e3:.1f} mV drop')
print(f'     Power loss:       {P_loss_bat:.2f} W')
print(f'     Efficiency loss:  {V_drop_bat/24*100:.2f}%')
print()

# Motor phase wires
print('   Motor Phase Path (J_MOT + 14 AWG wire, 0.3m):')
L_phase = 0.3
R_total_phase = 2 * R_wire_14awg * L_phase
V_drop_phase = I_peak * R_total_phase
P_loss_phase = I_peak**2 * R_total_phase

print(f'     Wire resistance:  {R_total_phase*1e3:.2f} mΩ (round-trip)')
print(f'     At 20A peak:      {V_drop_phase*1e3:.1f} mV drop')
print(f'     Power loss:       {P_loss_phase:.2f} W (per phase)')
print(f'     Total 3 phases:   {3*P_loss_phase:.2f} W')
print()

# 5. Board Area Thermal Capacity
print('5. BOARD THERMAL CAPACITY VERIFICATION')
print('-'*70)

board_w = 75  # mm
board_h = 55  # mm
board_area_mm2 = board_w * board_h
board_area_cm2 = board_area_mm2 / 100

# Thermal conductivity targets
copper_area_frac = 0.40  # 40% copper coverage (typical for 4-layer)
thermal_cond = 470  # mm²/W (target from docs)

print(f'   Board dimensions:   {board_w}mm × {board_h}mm')
print(f'   Total area:         {board_area_mm2:.0f} mm² ({board_area_cm2:.2f} cm²)')
print(f'   Copper coverage:    {copper_area_frac*100:.0f}% (est)')
print(f'   Effective Cu area:  {board_area_mm2*copper_area_frac:.0f} mm²')
print()
print(f'   Target thermal:     {thermal_cond:.0f} mm²/W')
print(f'   Available thermal:  {board_area_mm2*copper_area_frac:.0f} mm²')
print(f'   Max dissipation:    {board_area_mm2*copper_area_frac/thermal_cond:.2f} W (60°C rise)')
print()
print(f'   Actual peak:        {P_total_motor_peak:.1f} W (brief)')
print(f'   Actual average:     {P_total_motor_avg:.1f} W (typical)')
print(f'   Thermal margin:     {(board_area_mm2*copper_area_frac/thermal_cond - P_total_motor_avg)/(board_area_mm2*copper_area_frac/thermal_cond)*100:.1f}%')
print(f'   Status:             {"ADEQUATE" if P_total_motor_avg < board_area_mm2*copper_area_frac/thermal_cond else "INSUFFICIENT"}')
print()

print('='*70)
print('END OF SUPPLEMENTAL ANALYSIS')
print('='*70)
