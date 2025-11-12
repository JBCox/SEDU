#pragma once

#include <Arduino.h>

namespace sedu::sensors {

void init();

float batteryVoltsFromRaw(uint16_t raw);
float batteryPercentFromVolts(float volts);

float ladderVoltsFromRaw(uint16_t raw, float vref = 3.3f, uint16_t fullscale = 4095);
float ipropiAmpsFromRaw(uint16_t raw, float vref = 3.3f, uint16_t fullscale = 4095);

// Motor phase current estimation from DRV8353RS CSA outputs (analog)
// Returns per-phase amps using Rsense=2 mΩ and CSA gain≈20 V/V assumptions.
float csaPhaseAmpsFromRaw(uint16_t raw, float vref = 3.3f, uint16_t fullscale = 4095);
// Aggregate absolute motor current estimate (simple mean of |U|,|V|,|W|)
float motorCurrentAmpsFromRaw(uint16_t raw_u, uint16_t raw_v, uint16_t raw_w,
                              float vref = 3.3f, uint16_t fullscale = 4095);

}  // namespace sedu::sensors
