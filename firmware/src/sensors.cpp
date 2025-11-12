#include "sensors.h"
#include "../include/pins.h"
#include <math.h>

namespace sedu::sensors {

namespace {
struct BatteryCalibration {
  uint16_t raw_low;
  float volts_low;
  uint16_t raw_high;
  float volts_high;
};

// Updated to match hardware 140kΩ/10kΩ divider (not 49.9k/6.8k from original calc)
// At 25.2V: V_ADC = 25.2 × (10k/150k) = 1.680V → raw = 1.680/3.3 × 4095 = 2084
// At 18.0V: V_ADC = 18.0 × (10k/150k) = 1.200V → raw = 1.200/3.3 × 4095 = 1489
constexpr BatteryCalibration kBatteryCal{1489, 18.0f, 2084, 25.2f};
constexpr float kAdcRef = sedu::pins::kAdcReferenceVolts;
constexpr uint16_t kAdcFs = sedu::pins::kAdcFullScaleCounts;
constexpr float kRsensePhaseOhms = 0.002f;  // 2 mΩ
constexpr float kCsaGainVperV = 20.0f;      // DRV8353RS default gain (approx)

float calibrateBattery(uint16_t raw) {
  const float span_counts = static_cast<float>(kBatteryCal.raw_high - kBatteryCal.raw_low);
  if (span_counts <= 0.0f) return 0.0f;
  // Clamp raw to prevent underflow (raw < raw_low) or overflow (raw > raw_high)
  if (raw < kBatteryCal.raw_low) raw = kBatteryCal.raw_low;
  if (raw > kBatteryCal.raw_high) raw = kBatteryCal.raw_high;
  const float span_volts = kBatteryCal.volts_high - kBatteryCal.volts_low;
  return kBatteryCal.volts_low +
         (static_cast<float>(raw - kBatteryCal.raw_low) * span_volts) / span_counts;
}

}  // namespace

void init() {
  analogSetPinAttenuation(sedu::pins::kAdcBattery, ADC_11db);
  analogSetPinAttenuation(sedu::pins::kAdcLadder,  ADC_11db);
  analogSetPinAttenuation(sedu::pins::kAdcIpropi,  ADC_11db);
  analogSetPinAttenuation(sedu::pins::kAdcCsaU,    ADC_11db);
  analogSetPinAttenuation(sedu::pins::kAdcCsaV,    ADC_11db);
  analogSetPinAttenuation(sedu::pins::kAdcCsaW,    ADC_11db);
}

float batteryVoltsFromRaw(uint16_t raw) { return calibrateBattery(raw); }

float batteryPercentFromVolts(float volts) {
  const float clamped = constrain(volts, kBatteryCal.volts_low, kBatteryCal.volts_high);
  return (clamped - kBatteryCal.volts_low) * 100.0f /
         (kBatteryCal.volts_high - kBatteryCal.volts_low);
}

float ladderVoltsFromRaw(uint16_t raw, float vref, uint16_t fullscale) {
  return (static_cast<float>(raw) / static_cast<float>(fullscale)) * vref;
}

float ipropiAmpsFromRaw(uint16_t raw, float vref, uint16_t fullscale) {
  const float vipropi = (static_cast<float>(raw) / static_cast<float>(fullscale)) * vref;
  constexpr float kIpropi_k_A_per_A = 1100.0f;
  constexpr float kIpropi_R_ohms = 1000.0f;

  // Issue #4: Warn if ADC near saturation (>90% of full-scale)
  // At 3.3A: V_IPROPI = 3.0V (91% of 3.3V ADC range) - limited diagnostic margin
  constexpr float kSaturationWarning = 0.90f * kAdcRef;
  if (vipropi > kSaturationWarning) {
    static uint32_t last_warning_ms = 0;
    if (millis() - last_warning_ms > 1000) {  // Rate-limit to 1/second
      Serial.print("[WARNING] IPROPI ADC near saturation: ");
      Serial.print(vipropi);
      Serial.print("V / ");
      Serial.print(kAdcRef);
      Serial.println("V (check for actuator overcurrent or wrong ILIM resistor)");
      last_warning_ms = millis();
    }
  }

  return vipropi * (kIpropi_k_A_per_A / kIpropi_R_ohms);
}

float csaPhaseAmpsFromRaw(uint16_t raw, float vref, uint16_t fullscale) {
  const float vout = (static_cast<float>(raw) / static_cast<float>(fullscale)) * vref;
  const float denom = kRsensePhaseOhms * kCsaGainVperV;  // V = I*Rs*Gain
  if (denom <= 0.0f) return 0.0f;
  return vout / denom;
}

float motorCurrentAmpsFromRaw(uint16_t raw_u, uint16_t raw_v, uint16_t raw_w,
                              float vref, uint16_t fullscale) {
  // Simple aggregate: mean of absolute per‑phase currents (crude but robust)
  const float iu = fabsf(csaPhaseAmpsFromRaw(raw_u, vref, fullscale));
  const float iv = fabsf(csaPhaseAmpsFromRaw(raw_v, vref, fullscale));
  const float iw = fabsf(csaPhaseAmpsFromRaw(raw_w, vref, fullscale));

  // Issue #5: Sanity check - any phase >30A indicates CSA hardware fault
  // LM5069 ILIM = 18.3A, circuit breaker = 35A, so 30A is well above normal operation
  constexpr float kMaxPhysicalCurrent = 30.0f;
  if (iu > kMaxPhysicalCurrent || iv > kMaxPhysicalCurrent || iw > kMaxPhysicalCurrent) {
    static uint32_t last_warning_ms = 0;
    if (millis() - last_warning_ms > 1000) {  // Rate-limit to 1/second
      Serial.print("[ERROR] Motor CSA reading out of range (hardware fault): U=");
      Serial.print(iu);
      Serial.print("A, V=");
      Serial.print(iv);
      Serial.print("A, W=");
      Serial.print(iw);
      Serial.println("A");
      Serial.println("  -> DRV8353 CSA may be saturated, faulted, or SPI gain incorrect");
      last_warning_ms = millis();
    }
    return 0.0f;  // Return 0 to prevent interlock from using bogus data
  }

  return (iu + iv + iw) / 3.0f;
}

}  // namespace sedu::sensors
