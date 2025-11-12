# Mounting & Envelope

## Current Plan (Rev C.4b)
- **Initial layout**: 80 × 60 mm board outline
- **Optimization**: After placement and routing are complete, evaluate actual component extents and shrink board to fit + margin
- **Philosophy**: Design for function first, optimize size second

## Board Outline
- Start with 80 × 60 mm for component placement and routing
- After layout is functionally complete, measure actual bounding box of components + critical routing
- Shrink outline to actual size + 3-5mm margin per edge (if space allows)
- Final size will be determined by thermal, EMI, and routing requirements (likely 65-75mm × 50-58mm)

## Mounting Holes
- Mounting holes are NOT constrained by enclosure - tool is designed around board
- 4 × M3 (3.2 mm finished), positions TBD after board size is optimized
- Place holes based on actual component placement, thermal zones, and mechanical stress points
- Keep-out around holes: ≥1.5 mm annulus with no copper; tent vias near holes
- Avoid placing holes under hot components or in critical signal paths

## Stack-Up
- 4-layer recommended: L1 signals/short pours; L2 solid GND; L3 5V/3V3 planes and sense stitching; L4 signals/returns.

## Keep-Outs & Constraints
- ESP32 antenna keep-out per datasheet: ≥15 mm forward, ≥5 mm perimeter; no copper/dense routing under antenna
- Place J_LCD/J_UI away from inverter phase nodes; route BTN_SENSE with return in same cable
- BTN_SENSE ≥10 mm from switching nodes (buck SW islands, motor phases)
