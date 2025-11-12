# Datasheets Directory

This directory contains datasheets for all major components used in the SEDU Single-PCB Feed Drill project.

## Components

### Power Management
- **LM5069_datasheet.pdf** - Hot-swap controller (current limit, circuit breaker)
- **LMR33630AF_datasheet.pdf** - 24V → 3.3V buck converter (logic rail, single-stage)
- **TPS62133_datasheet.pdf** - 5V → 3.3V buck converter (MCU/LCD)
- **TPS22919_datasheet.pdf** - USB load switch (programming rail isolation)

### Motor & Actuator Drivers
- **DRV8353RS_datasheet.pdf** - 3-phase BLDC motor driver with integrated gate drivers
- **DRV8873-Q1_datasheet.pdf** - H-bridge linear actuator driver with current sensing

### Motor
- **Electrocraft - RPX32-DataSheet-US.pdf** - ElectroCraft RPX32-150V24 BLDC motor specifications

## Organization

Active datasheets for current design are stored here. Obsolete datasheets for components no longer used are archived in `archive/datasheets/`.

## Usage

Reference these datasheets when:
- Sizing components (power dissipation, ratings)
- Verifying electrical specifications
- Understanding functional behavior
- Troubleshooting hardware issues
- Laying out PCB (footprints, thermal considerations)
