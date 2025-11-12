# Connectors — J_LCD and J_UI (Daughterboard Interface)

## J_LCD (8-pos, JST-GH 1.25 mm suggested)
Pin‑1 indicator: Mark a triangle/dot on silkscreen at Pin 1. Diagram below assumes top‑view, connector key facing up.
| Pin | Net        | Notes                              |
|----:|------------|------------------------------------|
| 1   | 3V3        | 3.3 V logic/backlight              |
| 2   | GND        | Return                              |
| 3   | SPI_SCK    | 22–33 Ω in series at MCU           |
| 4   | SPI_MOSI   | 22–33 Ω in series at MCU           |
| 5   | SPI_CS_LCD |                                    |
| 6   | LCD_DC     | Panel D/C                           |
| 7   | LCD_RST    | Panel reset                         |
| 8   | LEDK_PWM   | Backlight sink (10–20 mA)          |

MISO is NC at the panel (write-only).

## J_UI (8-pos, JST-GH 1.25 mm suggested)
Pin‑1 indicator: Mark a triangle/dot on silkscreen at Pin 1. Keep orientation consistent with J_LCD.
| Pin | Net          | Notes                                          |
|----:|--------------|------------------------------------------------|
| 1   | 3V3          | UI logic supply                                |
| 2   | GND          | Return; twist with BTN_SENSE in cable          |
| 3   | BTN_SENSE    | Ladder analog to ADC1_CH3 (GPIO4)              |
| 4   | START_DIG    | Digital Start input                            |
| 5   | STOP_NC_DIG  | Digital Stop (NC chain continuity)             |
| 6   | BUZZER       | Optional piezo                                 |
| 7   | LED1         | UI LED1                                        |
| 8   | LED2         | UI LED2                                        |

Cable ≤200 mm; shield or twist pairs; series 100–220 Ω at J_UI on BTN_SENSE; 100 nF to GND at MCU ADC pin. Add 100 Ω series on START_DIG/STOP_NC_DIG near J_UI.
