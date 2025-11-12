#!/usr/bin/env python3
"""Ensure required net labels exist for firmware pins and connectors.

Parses hardware/Net_Labels.csv and verifies a required set of net names
is present (SPI, USB, LCD, UI, ADC, PWM, etc.).

Exit codes: 0 OK, 1 missing nets.
"""
from __future__ import annotations

import csv
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
NETS = ROOT / "hardware" / "Net_Labels.csv"

REQUIRED_NETS = {
    # Power
    "VBAT", "VBAT_PROT", "5V", "3V3", "GND",
    # USB
    "USB_D-", "USB_D+",
    # SPI
    "SPI_SCK", "SPI_MOSI", "SPI_MISO", "SPI_CS_DRV", "SPI_CS_LCD",
    # LCD
    "LCD_DC", "LCD_RST", "LEDK_PWM",
    # UI
    "BTN_SENSE", "START_DIG", "STOP_NC_DIG", "BUZZER", "LED1", "LED2", "LED3",
    # ADCs
    "CSA_U_ADC", "CSA_V_ADC", "CSA_W_ADC", "BAT_ADC", "NTC_ADC", "IPROPI_ADC",
    # Halls and sense
    "HALL_A", "HALL_B", "HALL_C", "FEED_SENSE",
    # PWM
    "MCPWM_HS_U", "MCPWM_HS_V", "MCPWM_HS_W", "MCPWM_LS_U", "MCPWM_LS_V", "MCPWM_LS_W",
}


def load_nets(path: pathlib.Path) -> set[str]:
    nets: set[str] = set()
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            n = row.get("net") or row.get("label")
            if n:
                nets.add(n.strip())
    return nets


def main() -> int:
    if not NETS.exists():
        print("[nets_vs_pins] Missing hardware/Net_Labels.csv")
        return 1
    nets = load_nets(NETS)
    missing = sorted(n for n in REQUIRED_NETS if n not in nets)
    if missing:
        print("[nets_vs_pins] Missing required net labels:")
        for n in missing:
            print(f"  - {n}")
        return 1
    print("[nets_vs_pins] Net labels cover required signals. PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

