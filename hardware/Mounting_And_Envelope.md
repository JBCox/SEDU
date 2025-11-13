# Mounting & Envelope

## Current Plan (Rev C.4b)
- **Optimized layout**: **80 × 50 mm board outline** (17% area reduction from 80×60mm baseline, fits credit card footprint 85.6×54mm)
- **Optimization basis**: Leverages 5V rail elimination (~12-15mm space savings) + thermal/routing analysis
- **Philosophy**: Balanced size reduction with adequate thermal margin (470mm²/W copper area)

## Board Outline
- **Finalized dimensions**: **80 × 50 mm**
- Thermal analysis confirms adequate heat dissipation for 8.5W typical power (12W peak)
- Adequate routing channels for 4mm battery traces + 3mm phase traces
- Component placement zones fit with 3-5mm margin per edge
- **Critical requirement**: Mandatory 8× thermal vias (Ø0.3mm) under high-power ICs (DRV8873, LMR33630, DRV8353RS)

## Mounting Holes
- Mounting holes are NOT constrained by enclosure - tool is designed around board
- 4 × M3 (3.2 mm finished) at positions: **(4, 4), (76, 4), (4, 46), (76, 46) mm** from board corner
- Positions optimized for 80×50mm board based on component placement, thermal zones, and mechanical stress
- Keep-out around holes: ≥1.5 mm annulus with no copper; tent vias near holes
- Avoid placing holes under hot components or in critical signal paths

## Stack-Up
- 4-layer recommended: L1 signals/short pours; L2 solid GND; L3 3V3 plane and sense stitching **(5V removed)**; L4 signals/returns.

## Keep-Outs & Constraints
- ESP32 antenna keep-out per datasheet: ≥15 mm forward, ≥5 mm perimeter; no copper/dense routing under antenna
- Place J_LCD/J_UI away from inverter phase nodes; route BTN_SENSE with return in same cable
- BTN_SENSE ≥10 mm from switching nodes (buck SW islands, motor phases)
