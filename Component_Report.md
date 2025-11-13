# Component Report for SEDU Single-PCB Feed Drill

**Date:** 2025-11-09

This report details the key specifications and project-specific roles of the primary integrated circuits used in the SEDU Single-PCB Feed Drill Control Board (Rev C.4). All corresponding datasheets have been downloaded to the project directory.

---

## 1. Main Control Unit (MCU)

- **Component:** `ESP32-S3-WROOM-1-N16R8`
- **Function:** The central processor for the entire system. It is responsible for running the main state machine, reading sensor inputs, controlling the user interface (LCD, buttons), and commanding the motor and actuator drivers.
- **Documentation:** `ESP32-S3-WROOM-1_datasheet.pdf`

### Key Features:
- **CPU:** Xtensa® dual-core 32-bit LX7 microprocessor (up to 240 MHz).
- **Memory:** 16 MB Quad SPI flash, 8 MB Octal SPI PSRAM.
- **Connectivity:** 2.4 GHz Wi-Fi (802.11 b/g/n) and Bluetooth® 5 (LE).
- **Peripherals:** Native USB OTG, ADC, I²C, SPI, and a powerful Motor Control PWM (MCPWM) peripheral.

### Project-Specific Info:
- **Native USB (GPIO19, GPIO20):** Used for programming/debug via USB-C; series 22–33 Ω resistors plus ESD close to the connector per Espressif guide.
- **MCPWM (GPIO38–43):** GPIO38/39/40 drive the DRV8353RS high-side PWM inputs and GPIO41/42/43 drive the low-side gates. IO35–37 are unavailable on the PSRAM module, so these assignments are locked per Rev C.4a.
- **ADC usage:** `GPIO5/6/7` (ADC1_CH4/5/6) capture the DRV8353RS current shunt amplifiers; `GPIO1` (ADC1_CH0) measures the battery divider; `GPIO4` (ADC1_CH3) reads the Start/Stop ladder; `GPIO10` (ADC1_CH9) monitors the FET NTC.
- **Discrete Start/Stop GPIOs:** GPIO23 (START) and GPIO24 (STOP_NC) provide redundant digital verification of operator intent alongside the ladder.
- **SPI Bus (GPIO17, 18, 21, 22, 16):** Configures the DRV8353RS (CS=GPIO22) and the GC9A01 LCD (write-only, **CS_LCD=GPIO16**, MISO NC) on a shared SCK/MOSI bus without CS contention.
- **Hall inputs:** GPIO8/9/13 feed the PCNT unit for commutation and diagnostics.

---

## 2. BLDC Motor Gate Driver

- **Component:** `DRV8353RS`
- **Function:** A highly integrated gate driver that sits between the ESP32-S3's logic-level PWM signals and the high-power MOSFETs that drive the three phases of the BLDC motor.
- **Documentation:** `DRV8353RS_datasheet.pdf`

### Key Features:
- **Voltage Range:** 9-V to 100-V, making it highly suitable for our 24V system with significant headroom.
- **Smart Gate Drive:** Allows for adjustable slew rate control to manage EMI and optimize switching performance.
- **Integrated Current Shunt Amplifiers (CSAs):** Three internal amplifiers provide analog voltage outputs proportional to the motor phase currents. This is the key feature enabling FOC.
- **Protection:** Includes robust protection against overcurrent, overvoltage, undervoltage, and thermal faults.
- **Interface:** SPI for detailed configuration and fault reporting, or a simpler hardware (pin-strapped) interface.

### Project-Specific Info:
- **6-Step & FOC:** The driver is configured to support both Hall-sensor-based 6-step commutation (our initial implementation) and FOC (our future goal).
- **CSA Outputs:** The three CSA outputs are directly wired to the ESP32-S3's ADC channels (`GPIO5/6/7`), which is the cornerstone of our FOC-ready design. The gain of these amplifiers must be set via SPI to match the sense resistor value and the ADC's input voltage range.
- **Phase Shunts:** 3× CSS2H-2512K-2L00F (2.0mΩ, 2512, 5W verified, K suffix NOT R) Kelvin sense resistors measure motor phase currents for FOC control.
- **Decoupling (lock):** CPL‑CPH = 47 nF (≥100 V X7R); VCP‑VDRAIN = 1 µF (≥16 V); VGLS‑GND = 1 µF (≥16–25 V); DVDD = 1 µF (≥6.3 V). Place tight to the DRV8353RS pins.
- **SPI Control (GPIO22):** The SPI interface is used to set gate drive current, configure protection features, and read fault status, giving the firmware fine-grained control and diagnostic capabilities.

---

## 3. Actuator H-Bridge Driver

- **Component:** `DRV8873-Q1`
- **Function:** A brushed DC motor driver responsible for controlling the linear actuator that performs the feed action.
- **Documentation:** `DRV8873-Q1_datasheet.pdf`

### Key Features:
- **Voltage Range:** 4.5-V to 38-V, compatible with our 24V bus.
- **High Peak Current:** Capable of delivering up to 10-A peak current to drive the actuator.
- **Integrated Current Sensing:** An internal current mirror removes the need for a large power sense resistor.
- **Protection:** Features standard undervoltage, overcurrent, and thermal protection.

### Project-Specific Info:
- **Current Limiting (ILIM):** The design correctly specifies setting the current limit via an external resistor to **110-120% of the actuator's continuous rated current**, not its stall current. This is crucial for preventing actuator burnout.
- **Control Interface:** The PH/EN (Phase/Enable) version is used, providing a simple and direct control interface from the ESP32-S3's GPIOs.
- **Redundant inputs:** GPIO23 (START) enables the driver only when the ladder reads a valid START command, and GPIO24 (STOP_NC) provides an immediate hardware disable path that mimics the legacy safe-stop behavior.
- **Supply options (24 V default):** Default: tie DRV8873 VM to the protected 24 V domain via a 0 Ω link (no 12 V buck). Optional: for a 12 V actuator, populate an LMR33630AF buck configured to 12 V and tie VM to that rail instead.
- **Locks:** `R_IPROPI = 1.00 kΩ (1%)` for ADC scaling; `R_ILIM = 1.58 kΩ (1%)` ⇒ I_lim ≈ 3.3 A (use E96 1.58 k).

---

## 4. Power Management

### 4.1 24V to 3.3V Buck Converter (Single-Stage)
- **Component:** `LMR33630ADDAR`
- **Function:** The primary and sole regulator, stepping the 24V battery input directly down to a stable 3.3V rail to power the ESP32-S3 and all logic-level components. The 5V intermediate rail has been eliminated to reduce component count, board area, and power loss.
- **Documentation:** `LMR33630AF_datasheet.pdf`
- **Project-Specific Info:** Chosen for its high efficiency (~92% at our expected load), which minimizes heat dissipation. Its 3A output capacity provides ample current for the entire logic system. Direct 24V→3.3V conversion simplifies the power architecture and improves overall efficiency by eliminating the cascaded conversion losses of the previous two-stage design.

### 4.2 5V to 3.3V Buck Converter (REMOVED)
- **Component:** `TPS62133` - **ELIMINATED in Rev C.4a+**
- **Status:** This component and the entire 5V intermediate rail have been removed from the design. The LMR33630ADDAR now provides 3.3V directly from the 24V battery rail in a single-stage conversion.
- **Rationale:** Eliminating the two-stage power conversion (24V→5V→3.3V) reduces BOM count, board area (enabling 80×50mm optimization from 80×60mm baseline), and cumulative conversion losses. The direct 24V→3.3V approach is more efficient and simplifies the power architecture.

### 4.3 USB Power Path
- **Components:** `TPS22919` (load switch) & `TLV75533` (3.3 V LDO)
- **Function:** VBUS feeds the TPS22919, which isolates the USB rail from the main 3.3V buck. When enabled, the TLV75533 provides a 3.3 V/250 mA rail dedicated to the ESP32 for programming with the main battery disconnected.
- **Documentation:** `TPS22919_datasheet.pdf`, TLV75533 datasheet (note: PDFs stored at repo root per AGENTS.md).
- **Project-Specific Info:** Firmware disables RF subsystems and power stages whenever this rail is active. This path must **never** be used to operate the drill; it is for flashing/debug only (USB never powers the tool).

### 4.4 Actuator 12 V Buck (option)
- **Component:** `LMR33630AF` configured for 12 V
- **Function:** Steps 24 V down to 12 V to supply DRV8873 VM when the build uses a 12 V linear actuator.
- **Design Start:** L = 10–15 µH, COUT ≥ 2×22 µF X7R (≥16 V), CIN ≥ 10 µF + 220 nF. Confirm ripple/thermals at 2.5 A peak during bring‑up.

---

## 5. System Protection

- **Component:** `LM5069-1` (latch-off on fault)
- **Function:** A positive high-voltage hot-swap controller that provides intelligent inrush current limiting and robust protection against overcurrent and short-circuit events at the main battery input.
- **Documentation:** `LM5069_datasheet.pdf`

### Key Features:
- **Wide Voltage Range:** Operates from 9V to 80V.
- **Programmable Current Limit:** Uses an external sense resistor to set a precise power limit.
- **Inrush Control:** Manages the charging of bulk input capacitors to prevent large current spikes when connecting the battery.
- **MOSFET Control:** Drives an external N-Channel MOSFET as the main power switch.

### Project-Specific Info:
- **Robustness:** This component is a significant upgrade from a simple fuse, providing much more sophisticated protection for the entire board.
- **Current Limit & Breaker:** Target ILIM ≈ 18 A ⇒ Rsense ≈ 55 mV / 18 A ≈ 3.0 mΩ ⇒ stuff **3.0 mΩ**, **≥3 W**, **1%**, true Kelvin (e.g., 2512 Kelvin type). Circuit breaker trips ≈ 35 A (105 mV / 3.0 mΩ).
- **Inrush Control:** Start with **C_dv/dt = 33 nF** and tune so measured inrush ≤ ~0.5 × ILIM during 24 V plug‑in.
- **Spin-up Tolerance:** The controller's timer will be configured to allow the brief high-current pulses required for motor spin-up while still protecting against sustained overloads.

---

## 6. Display & Operator Feedback

- **Component:** `GC9A01`-based 240×240 circular SPI LCD module (3.3 V logic/backlight).
- **Function:** Mirrors the legacy HUD by showing Ready/Run/Fault states, battery percentage, and motor RPM/current.
- **Interface:** Write-only SPI sharing the DRV8353 bus (SCK=GPIO18, MOSI=GPIO17, **CS_LCD=GPIO16**, DC/RST per connector). MISO remains NC; DRV CS is GPIO22.
- **Backlight:** LEDK sink 10–20 mA; drive through a low-side FET or resistor from 3.3 V. Provide PWM dimming if required.
- **Project-Specific Info:** Place 22–33 Ω series resistors on SCK/MOSI when the LCD is cabled, and route its flex away from the motor phase regions to minimize EMI, matching the instructions in `New Single Board Idea.md` and the canonical spec.
