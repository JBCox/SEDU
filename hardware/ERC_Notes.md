# ERC Notes (to minimize false warnings)

- Place `PWR_FLAG` on 24V and 3V3 rails so ERC recognizes driven nets. **(5V rail eliminated)**
- LCD MISO is intentionally NC (panel is write-only). Mark it as `No ERC` or omit the net.
- BTN_SENSE is an analog input; ladder connects to 3V3 and GND through resistors — ERC may flag this as a passive path; OK.
- DRV8353 fault pins that are not used should be pulled or marked `No ERC` per datasheet guidance.
- Unused ESP32 pins: leave NC or tie as per Espressif’s recommended strapping; add `No ERC` on unbonded pins if KiCad complains.
