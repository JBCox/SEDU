# Bring-Up Checklist (Rev C.4b)

Use this as a step-by-step, novice-friendly guide to verify the board.

## Equipment
- Bench supply set to 24.0 V, 5–10 A current limit
- DMM with current and voltage measurement
- USB-C cable

## Steps
1. Visual: Inspect polarity, orientation, and that LM5069 sense resistor is 3.0 mΩ (4‑terminal).
2. USB-only: Connect USB-C (no battery). Board should enumerate; LCD may show "USB DEV MODE"; no motor/actuator activity.
3. Battery-only (no USB): Set supply to 24 V, current limit 5 A. Power on. Confirm 24 V → 5 V buck (~5.0 V) and 3.3 V rail (~3.3 V).
4. Inrush check (LM5069): Increase current limit to 10 A. Power-cycle and observe peak current. Goal: ≤ ~0.5 × ILIM (≈6 A). If higher, increase C_dv/dt; if too slow, decrease.
5. Buttons: Observe serial output.
   - Press START: expect ladder "START" and Start line asserted.
   - Release to IDLE: expect ladder "IDLE".
   - Press STOP (NC opens): expect ladder "STOP" (not FAULT) and immediate disable.
   - Measure BTN_SENSE with DMM: ~0.85–0.95 V (START), ~1.7–1.8 V (IDLE), ~3.3 V (STOP).
6. Halls: Manually rotate motor shaft; verify Hall edges count and nonzero RPM in logs.
7. Actuator current: Put DMM in series with actuator supply. Briefly enable motion (tap START) and read steady current after ~0.5 s. Record "I_act,cont". If ≈3.0 A, keep R_IPROPI = 1.0 kΩ; otherwise, set `R_IPROPI ≤ (3.3 V · 1100) / I_act,cont` and update BOM.
8. Interlock validation (hybrid fix):
   - Motor-only: spin motor; verify battery current remains below ILIM and RPM logs are stable.
   - Actuator-only: extend actuator; verify IPROPI < 3.3 A and logs report current.
   - Overlap test A: with motor spinning (>500 RPM), command actuator; actuator must be blocked; observe "[INTERLOCK]" log.
   - Overlap test B: with actuator active (IPROPI > 0.5 A), command motor (if applicable); motor must remain idle (log intent if not yet implemented).
9. Finalize: Once I_act,cont is known, lock ILIM policy (110–120% of continuous) and update `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md` and `Component_Report.md` with the chosen R_IPROPI and any C_dv/dt tweaks.

Record results in a dated note under `docs/` and summarize in the changelog.
