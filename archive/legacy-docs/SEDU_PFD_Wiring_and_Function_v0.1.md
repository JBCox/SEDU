# SEDU Positive-Feed Drill — Current Wiring & Planned Function (v0.1)

> Handheld aviation PFD using **VESC 4.12 + ElectroCraft RPX32-150 (24 V BLDC)**, an **ESP32‑C6 WROOM dev board**, **DRV8871 H‑bridge** for the linear actuator, **GC9A01 SPI LCD**, and a **2‑button ladder** (START/STOP) into one ADC.

---

## 1) System Overview

```
24 V Battery
   │
   ├─> VESC 4.12  ──> 3‑phase BLDC (RPX32‑150)
   │       │
   │       ├─ 5 V out ──> ESP32‑C6 WROOM devboard 5V
   │       │                └─ 3.3 V rail ──> LCD (GC9A01, SPI)
   │       └─ UART (TX/RX) <──────> ESP32‑C6 (RX/TX)
   │
   └─> 24 V ──> DRV8871 H‑bridge ──> 24 V Linear Actuator
                      ▲
                      └─ IN1/IN2 from ESP32 (GPIO)
```

**Buttons:**  
- **Green START** = normally‑open to GND (via 5 kΩ)  
- **Red STOP** = normally‑closed to GND (via 10 kΩ)  
- Both form a **resistor ladder** to one ESP32 ADC with RC filter for hardware debounce.

**LCD (GC9A01 240×240 SPI, 3.3 V logic/backlight):**  
- Simple HUD: Start/Stop status, battery %, motor telemetry.  
- SPI write-only: SCK=ESP32 GPIO18, MOSI=GPIO17, CS=GPIO22, DC/RST per panel header, MISO NC, LEDK backlight 10–20 mA with series resistor or FET dimming.  
- Add 22–33 Ω series on SCK/MOSI near MCU if using a cable; keep ribbon away from high-di/dt nodes.

---

## 2) Current Wiring (as built)

### Power
- **24 V battery → VESC 4.12** (main BLDC power).
- **VESC 5 V output → ESP32‑C6 devboard 5V pin** (devboard regulates to 3.3 V).
- **ESP32 3.3 V → LCD** (logic + backlight if on 3.3 V).
- **DRV8871 H‑bridge** is powered directly from **24 V**.

> All grounds (battery−/VESC GND/ESP GND/DRV8871 GND/LCD GND) are common.

### Communications & I/O
- **ESP32 UART ↔ VESC UART** (RX↔TX crossed, shared GND).
- **ESP32 SPI → GC9A01 LCD** (SCK/MOSI/CS/DC/RST; no MISO).
- **ESP32 GPIO → DRV8871 IN1/IN2** (direction/enable).
- **Two‑button ladder → one ESP32 ADC** (BTN_SENSE).

### Two‑Button Ladder (values shown in your schematic)
- Pull‑ups to 3.3 V: **R19 = 10 kΩ** (main), **R20 = 100 kΩ** (aux).
- To GND through buttons: **R21 = 5 kΩ** (START, NO), **R11 = 10 kΩ** (STOP, NC).
- **C19 = 100 nF** from BTN_SENSE to GND (RC ≈ 1 ms).

**Nominal ADC targets @ 3.3 V (12‑bit ADC shown):**

| State                     | BTN_SENSE (V) | ADC (≈) |
|--------------------------:|--------------:|--------:|
| STOP pressed (NC opens)   | 3.30          | 4095    |
| No buttons                | 1.73          | 2145    |
| START pressed             | 0.89          | 1099    |
| Both pressed              | 1.17          | 1453    |

**Suggested firmware bands (with margin):**
- **START:** `< 0.75 V` (ADC < ~930)  
- **BOTH/invalid:** `0.95–1.40 V` (ADC ~1150–1750) → treat as **stop**  
- **NONE:** `1.55–2.10 V` (ADC ~1900–2500)  
- **STOP:** `> 2.6 V` (ADC > ~3230)  
- **Fault windows:** `< 0.1 V` or `> 3.2 V` for > x ms ⇒ **safe stop**

---

## 3) Planned Functional Behavior

### Operator Flow (what the tool does)
1. **Idle:** LCD shows battery %, “Ready”. Motor off, actuator retracted.  
2. **START (green) pressed:**  
   - ESP32 commands **VESC** to **ramp motor RPM**.  
   - Immediately drives **DRV8871** to **extend actuator**, pushing the **feed lever**.  
3. **Feed engage:** as the head engages, drilling occurs with the BLDC already at speed.  
   - **Actuator retracts** almost immediately after engage to allow the feed mechanism to return once drilling is done.  
4. **Completion / STOP:**  
   - On cycle complete or **STOP** (red) event, ESP32 commands **motor stop** and ensures **actuator retracted**.  
5. **Faults:** Brownout, UART loss, unexpected button state ⇒ **stop motor + disable actuator** and show message.

### Firmware State Machine (sketch)
- **Idle → Arm → Run → Retract → Complete | Fault**
  - **Idle:** verify STOP present (NC continuity), show battery%.  
  - **Arm (on START):** start RPM ramp, extend actuator.  
  - **Run:** monitor lever/torque/ERPM; maintain RPM; UI updates.  
  - **Retract:** after engage, retract actuator; keep RPM as required by head.  
  - **Complete:** spin down; return to Idle.  
  - **Fault:** immediate motor stop (VESC timeout or explicit), actuator disabled, message on LCD.

### Safety & Failsafes
- **VESC App Timeout (UART)** short (e.g., 100–200 ms) + **Safe Start**, so comms loss = motor stop.  
- **DRV8871 default‑safe pins:** pull **IN1/IN2 low** with resistors so reboot leaves actuator off.  
- **E‑stop (recommended):** mechanical/electrical series kill for BLDC supply or VESC enable.  
- **UART hardening:** 22–100 Ω series + ESD if cable exits enclosure.  
- **Grounding:** star ground near battery return; keep actuator/VESC high‑di/dt loops away from logic.

---

## 4) LCD UI (initial)
- **Top line:** `READY / RUN / FAULT`  
- **Mid:** Battery % (prefer from **VESC telemetry** pack voltage)  
- **Bottom:** ERPM / current (selected from VESC telemetry), icons for START/STOP state

---

## 5) Bring‑Up Checklist

1. **Power‑only:** with motor/actuator disconnected, verify 5 V on ESP and stable 3.3 V under Wi‑Fi burst; no brownouts.  
2. **UART link:** ESP ↔ VESC ping; read pack voltage & ERPM; confirm **VESC timeout stops motor**.  
3. **Actuator solo:** DRV8871 extend/retract; confirm **ILIM** set below actuator stall; check return paths run to star ground.  
4. **Buttons:** verify ADC bands match table; test debouncing and BOTH/invalid handling.  
5. **System cycle:** START → spin → push → retract → complete; yank ESP power mid‑cycle to confirm VESC safe stop.  
6. **EMI sanity:** run under load; if ESP resets, add bulk/filters or move ESP/LCD to a cleaner supply (see below).

---

## 6) Known Risks & Simple Mitigations

- **ESP resets from VESC 5 V rail noise / current bursts**  
  - *Mitigate*: add bulk near ESP (470–1000 µF), set ESP brown‑out ~2.9–3.1 V, reduce Wi‑Fi use during drilling.  
  - *Best practice*: a **small dedicated buck** (24 V→5 V ≥1 A or →3.3 V ≥600 mA) for ESP+LCD, tied to VESC GND at a star point.

- **Actuator current spikes into logic ground**  
  - *Mitigate*: keep DRV8871 high‑current loop tight; route its return straight to star ground; bulk cap at VM.

- **Induced faults on long UART/actuator leads**  
  - *Mitigate*: series resistors, ESD diodes, twisted pairs/shielded cable if necessary.

---

## 7) Open Items (to lock down later)
- Exact **ILIM resistor** for DRV8871 (needs actuator stall current).  
- Confirm **LCD backlight** rail and whether we want PWM dimming.  
- Final **GPIO map** (SPI pins, UART, ADC pin for buttons, lever sensor input).  
- Decide whether to **keep** “Battery→VESC→ESP” or adopt a **dedicated buck** for the ESP/LCD.

---

## 8) Quick Notes for Docs/KiCad
- Draw a tiny “**Power & ESD**” sheet (battery TVS, reverse‑polarity protection, input LC, optional logic buck).  
- Label the **star ground** symbolically and keep logic/power planes separated.  
- Add test pads: **GND, 3V3, 5V, RX, TX, BTN_SENSE**.
