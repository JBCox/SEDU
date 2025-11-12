
# SEDU Single‑PCB Feed Drill Control Board — Parity‑Corrected **Rev C.4a (Final)**

**Scope:** One‑board, Arduino‑programmable controller replacing VESC + dev board + loose H‑bridge. Keeps Wi‑Fi/BLE, LCD, button UI, actuator, and identical tool behavior. **Form factor cap:** ≤ **100 × 60 mm**, VESC‑class Z‑height. (Authoritative values live in `docs/SEDU_Single_PCB_Parity_Corrected_RevC4a_Final.md`; this file summarizes the same data for quick reference.)

**Major deltas vs Rev C.4:**  
- Fixed **MCPWM pin mapping** for **ESP32‑S3‑WROOM‑1‑N16R8** (IO35/36/37 are unavailable on PSRAM modules).  
- Locked **FOC ADC RC** (56–100 Ω + 470 pF @ MCU) and **DRV8353 CSA gain** (20 V/V default).  
- Front‑end **hot‑swap/eFuse = LM5069** (external FET, high‑current capable) with **Rsense/dv/dt math**.  
- Vibration‑rated **connectors** specified; LCD **series resistors** added.  
- Battery ADC **0.1% divider** + 2‑point **cal**; USB‑only LDO **thermal guardrail**; **u.FL (-1U) alt stuffing**; input **bleeder** footprint.
- Deviations from the legacy harness are tracked in `docs/DEVIATIONS_FROM_LEGACY.md` and must be reiterated in schematic notes/BOM updates.

---

## 1. Architecture Overview
```
24V BAT (18–25.2V)
  ├─ LM5069 Hot‑Swap/OV/UV + TVS + reverse (FET)      [HV DOMAIN]
  │   └─ DC bus → BLDC power stage (DRV8353RS + MOSFETs, shunts)
  │             → Actuator H‑bridge (DRV8873‑Q1)
  └─ Buck 24V→5V (LMR33630) → 3V3 LDO/Buck (TPS62133)  [LOGIC 5V / 3V3]
              └─ ESP32‑S3‑WROOM‑1‑N16R8 (Wi‑Fi/BLE, USB)
                  ├─ MCPWM → DRV8353RS INHx/INLx
                  ├─ ADC1_CH4/5/6 ← CSA_U/V/W (RC anti‑alias)
                  ├─ Halls A/B/C (PCNT)
                  ├─ LCD (SPI) + UI LEDs + buzzer
                  ├─ Buttons (Start/Stop NC ladder + discrete)
                  └─ FEED_SENSE (limit/Hall) → actuator FSM
```

## 2. Power Tree
| Stage | Part | Vin / Vout | Iout (typ/max) | Eff. | Notes |
|---|---|---:|---:|---:|---|
| Input protection | **LM5069** + TVS SMBJ33A | 18–25.2 V / pass | 0–15 A class | — | Hot‑swap, inrush, OV/UV, programmable ILIM; external FET sized for motor surge |
| Logic buck | **LMR33630** | 24→5 V | 0.5–2.0 A | ~92% | Sync buck, 400 kHz; copper pour + vias; **P_loss ≈ 0.87 W @ 5V/2A** |
| 3V3 | **TPS62133** (or TLV62569) | 5→3.3 V | 0.5–1.0 A | ~94% | Feeds ESP + LCD; place near MCU |
| USB‑only dev | **TPS22919 → TLV75533** | 5 V USB→3.3 V | ≤250 mA | — | Programming-only rail; load switch prevents backfeed; radios OFF while USB-powered |

**LM5069 sizing (examples):**
- **ILIM target:** 18 A → **R_SENSE ≈ 55 mV / 18 A = 3.0 mΩ** (use 3.0 mΩ, ≥3 W, 1% Kelvin).  
- **dv/dt:** choose C_GD per datasheet to keep **I_inrush ≤ 0.5·ILIM**; e.g., 22 nF @ 24 V with FET gate eq. (document exact value in schematic).

## 3. MCU & Radio
- **ESP32‑S3‑WROOM‑1‑N16R8** (chip antenna) with **-1U (-U, u.FL) alt stuffing** on BOM.  
- **Arduino‑style programming:** native USB‑CDC (D− **GPIO19**, D+ **GPIO20**) + auto‑boot; series **22–33 Ω** in D± and ESD close to connector.  
- **RF:** keep 15 mm keep‑out at antenna; no copper/ground under end cap; option to pivot to **-1U** if EMC detuning appears.

## 4. Motor Power Stage (Integrated)
- **Driver:** **DRV8353RS** (SPI, CSA).  
- **MOSFETs:** 3‑phase, **60 V** logic‑level, ≤2 mΩ Rds(on) class; examples: Infineon **BSC016N06NS**, **BSC059N06LS3 G**; onsemi **NTMFS5C628NL**; Vishay **SQJQ480E**.  
- **Current sense:** 3 × **2 mΩ, 2512, pulse‑rated**, Kelvin; **CSA gain = 20 V/V** (lock).  
- **ADC anti‑alias:** **56–100 Ω series + 470 pF to GND at MCU pins** (lock). Maps ±25 A pk ≈ 2.0–2.5 V full‑scale.  
- **Commutation:** default **6‑step + Halls**; firmware path for **FOC** using ADC1_CH4/5/6.  
- **Protection & decoupling (lock):** DRV OC/BK, OT sense via NTC→ADC; UVLO, gate dv/dt snubbers. Decoupling: **CPL‑CPH = 47 nF (≥100 V X7R)**, **VCP‑VDRAIN = 1 µF (≥16 V)**, **VGLS‑GND = 1 µF (≥16–25 V)**, **DVDD = 1 µF (≥6.3 V)** placed tight to pins.

## 5. Actuator Driver
| Option | Part | V/I | Features | Why |
|---|---|---|---|---|
| A (default) | **DRV8873‑Q1** | 4.5–37 V, 3.5 A cont | Config ILIM, fault diag, decay modes | Robust, automotive, integrated FETs |
| B | **VNH7070AS** | up to 41 V, 30 A pk | SOA rich, robust | Bigger package; cost/size hit |

**ILIM policy:** set **110–120% of actuator’s *continuous*** rating (not stall). Flyback via integrated clamps; add **SMBJ33A** on supply.

## 6. I/O & UI
- **Start/Stop:** NC‑Stop + Start on ladder **and** discrete digital lines. Ladder ADC bands: **<0.20 V = FAULT**, 0.75–1.00 V = START, 1.55–2.10 V = IDLE, 2.60–3.35 V = STOP, **>3.40 V = OPEN FAULT**.  
- **LCD (GC9A01 240×240 SPI, 3.3 V, LEDK 10–20 mA):** Write-only SPI (SCK=GPIO18, MOSI=GPIO17, CS_LCD=GPIO16, DC/RST per connector; DRV CS remains GPIO22). MISO remains NC. Add **22–33 Ω** series on SCK/MOSI near the MCU if the panel is cabled, and keep the ribbon away from phase nodes.  
- **Battery sense (lock):** Divider **49.9 kΩ / 6.80 kΩ (0.1%)**; 25.2 V → ~3.02 V at ADC (12 dB atten). Add **1–4.7 kΩ series + 0.1 µF** to GND at pin; 2‑point cal stored in NVS.  
- **Buzzer/LEDs:** simple GPIO; FEED_SENSE (limit/Hall) with RC deglitch.  
- **UI telemetry:** LCD must show Ready/Run/Fault text, battery %, and motor RPM/current so operators see the same data as the legacy tool.

## 7. Pin Map (Critical Signals)
| Function | ESP32‑S3 Pin |
|---|---|
| **USB D− / D+** | GPIO19 / GPIO20 |
| **SPI (DRV8353)** | SCK=GPIO18, MOSI=GPIO17, MISO=GPIO21, CS=GPIO22 |
| **ADC (FOC CSAs)** | **U=GPIO5 (ADC1_CH4), V=GPIO6 (ADC1_CH5), W=GPIO7 (ADC1_CH6)** |
| **Halls A/B/C** | GPIO8 / GPIO9 / GPIO13 (PCNT) |
| **MCPWM HS U/V/W** | **GPIO38 / GPIO39 / GPIO40** |
| **MCPWM LS U/V/W** | **GPIO41 / GPIO42 / GPIO43** *(driver EN held low at boot)* |
| **FEED_SENSE** | GPIO14 (ADC2_CH3 capable if needed) |
| **Buttons (dig)** | START=GPIO23, STOP_NC=GPIO24 |
| **Button ladder ADC** | GPIO4 (ADC1_CH3) |
| **Buzzer / LEDs** | BUZ=GPIO25; LED1/2/3=GPIO26/27/28 |
| **LCD (GC9A01 SPI)** | SCK=GPIO18, MOSI=GPIO17, CS_LCD=GPIO16, MISO=NC; DC/RST per panel |
| **Spare pads (test pads)** | **GPIO11, GPIO12** (ADC2_CH0/1) |
| **Battery ADC** | GPIO1 (ADC1_CH0) |
| **NTC (FET temp)** | GPIO10 (ADC1_CH9) |

| **Actuator DRV8873 PH/EN** | GPIO30 / GPIO31 |

### Additional Locks (Rev C.4b)
- **USB programming policy:** "TPS22919 → TLV75533 only; USB never powers the tool; radios forced off in USB‑only mode."  
- **GPIO/JTAG note:** Keep **GPIO‑JTAG** disabled so **MCPWM** owns **38–43**.

> Note: **IO35/36/37 not used** (not available on PSRAM modules). Gate driver **nSLEEP/EN** has a pulldown so PWM chatter at boot cannot energize FETs.

## 8. Preliminary BOM (key ICs)
| Ref | Part | MPN | Alt/Sub |
|---|---|---|---|
| U‑MCU | ESP32‑S3‑WROOM‑1‑N16R8 | ESP32‑S3‑WROOM‑1‑N16R8 | **-1U** (u.FL) alt stuffing |
| U‑HS | **LM5069** Hot‑Swap | LM5069MM‑1/NOPB | LTC4368‑2, TPS25982 (if 18 V rails) |
| Q‑HS | N‑FET, 60–80 V, low Rds | IPA030N06N3 or BSC016N06NS | SiRA80DP |
| U‑TVS | TVS 600 W | SMBJ33A | SMBJ28A (if 6S only) |
| U‑5V | Buck 24→5 V | LMR33630 | MP1584, TPS54360 |
| U‑3V3 | Buck/LDO 5→3.3 V | TPS62133 | TLV62569, AP63357 |
| U‑FOC | 3‑ph driver w/ CSA | DRV8353RS | DRV8350RS |
| Q‑FET | 6× power MOSFETs | ≤2 mΩ, 60 V | same class |
| R‑SH | Shunts 2 mΩ 2512 | Bourns CSS2H‑2512‑R002‑F | Vishay WSL, KOA PSL |
| U‑ACT | H‑bridge | DRV8873‑Q1 | VNH7070AS |
| Conn‑Power | **Micro‑Fit/Mini‑Fit Jr / ring lug** | Molex 0039‑** series** | TE MicroMatch (signal), Phoenix **PLUS** (screw, locking) |

*(Complete passives and connectors list to schematic/BOM CSV; all external connectors specified **locking/vibration‑rated**.)*

## 9. Schematic & Layout Notes
- **Grounding:** “Mecca” star at battery‑in NEG. Separate **PGND/LGND** planes; single‑point tie near LM5069 sense. Keep motor di/dt loops tight.  
- **RF keep‑out:** 15 mm under antenna; stitch via fence around RF zone.  
- **Sense routing:** true Kelvin from shunts to DRV CSAs; ADC RC **at MCU pin**.  
- **USB:** 90 Ω diff pair, **22–33 Ω series** at D± near MCU; ESD by connector; keep stubs short.  
- **PWM:** place gate resistors near FETs; driver EN default low; snubbers/TVS as needed.  
- **Connectors:** specify locking types with current/temperature rating; add **input bleeder 100–220 kΩ/0.25 W** footprint.  
- **LCD cable:** series 22–33 Ω on SCK/MOSI; per‑device CS pad; route away from phase nodes.

## 10. Firmware Scaffold (Arduino)
```cpp
#include <Arduino.h>
// Pins per §8
// Init: hold driver EN low, configure MCPWM/PCNT/ADC, then enable driver.

void setup() {
  Serial.begin(115200);
  // GPIO init (buttons, LEDs, buzzer)
  // USB CDC up, driver EN held low
  // ADC config: atten=11dB on ADC1 CH0/4/5/6/9; RC already stuffed
  // MCPWM: HS on 38/39/40; LS on 41/42/43
  // Hall PCNT; DRV8353 SPI init; set CSA gain=20V/V; clear faults
}

void loop() {
  // Ladder read with fault bands: <0.20V and >3.40V => FAULT latch
  // FEED_SENSE gates retract; Actuator FSM (DRV8873-Q1)
  // Battery ADC with 2-pt calibration; LCD updates
  // Motor: 6-step baseline; FOC path guarded by sanity checks
}
```

## 11. Test & Bring‑up Plan
- **Stage A (unpowered):** continuity, shorts, polarity; connector mech fit.  
- **Stage B (24 V, driver EN low):** LM5069 limits verified; buck rails; USB enumerate; RF smoke test.  
- **Stage C (logic only):** program, buttons, LEDs, LCD; ADC cal (2‑point).  
- **Stage D (motor no‑load):** DRV8353 SPI, Hall edges, PWM idle (EN low), then enable and ramp.  
- **Stage E (actuator):** DRV8873 current‑limit tune; FEED_SENSE transitions; retraction timing.  
- **Stage F (FOC proto):** sample CSAs; verify ADC bandwidth/noise; closed‑loop spin.  
- **EMI/ESD:** surge/fast‑transient on 24 V; radiated pre‑scan; antenna alt stuffing if needed.

## 12. FMEA / Risks & Mitigations
| Risk | Effect | Mitigation |
|---|---|---|
| Wrong PWM pins (IO35–37) | No signals (PSRAM conflict) | **Use 38–43; avoid 35–37**; EN low at boot |
| USB glitches | Spurious states | Series 22–33 Ω; note startup behavior; ESD near connector |
| RF detune | Poor Wi‑Fi/BLE | Strict keep‑out; **-1U** u.FL alt stuffing |
| Hot‑swap sizing | Overstress FET | LM5069 Rsense/dv/dt math locked; thermal check |
| CSA alias/noise | FOC instability | RC 56–100 Ω + 470 pF @ MCU; short Kelvin |
| Connector vibration | Intermittents | Locking/vibration‑rated families; strain relief |
| Battery ADC drift | Wrong % | 0.1% divider; 2‑point factory cal |
| USB‑only flash heat | LDO overheat | Radios off; **temp cut ≥85 °C** or time limit |

## 13. Manufacturing Notes
- **4‑layer** stackup (1oz outer, 1oz inner). Power stage along long axis; logic cluster compact.  
- DFM: >0.2 mm min via; tent vias under QFNs; thermal relief on shunts/TVS.  
- **Programming jig**: USB‑C primary; 6‑pin tag‑connect SWD/JTAG optional.  
- Conformal coat option excluding antenna and connectors.

## 14. Mechanical Drawing (≤100 × 60 mm)
```
 ┌────────────────────────────────────────────────────────── 100 mm max ─┐
 │ [Battery In, locking]      [Antenna keep-out]     [Motor Phases]     │
 │ [LM5069 + TVS + shunt]  [ESP32‑S3‑WROOM‑1]  [DRV8353 + FET banks]     │
 │ [Buck 24→5] [5→3V3]   [USB‑C] [LCD hdr] [Btns/LEDs/Buzzer] [Actuator] │
 └────────────────────────────────────────────────────────── 60 mm max ──┘
 Height: VESC‑class; no tall parts on 60‑mm edge; mount holes clear of RF.
```
