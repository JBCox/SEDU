#include "rpm.h"
#include "../include/pins.h"

#include <Arduino.h>

// Optional PCNT path; default off until calibrated to motor pole pairs.
#ifndef SEDU_USE_PCNT
#define SEDU_USE_PCNT 0
#endif

#if SEDU_USE_PCNT
#include <driver/pcnt.h>
#endif

namespace sedu::rpm {
namespace {
volatile uint32_t g_edges = 0;
// 8-pole motor (4 pole pairs) × 6 electrical states per pair = 24 edges per mechanical revolution
constexpr float kEdgesPerMechanicalRev = 24.0f;

#if defined(ESP_PLATFORM)
// Guard increments to avoid RMW races across simultaneous hall edges.
// Lightweight critical section; ISR-safe.
portMUX_TYPE g_mux = portMUX_INITIALIZER_UNLOCKED;
#endif

void IRAM_ATTR onHallEdge() {
#if defined(ESP_PLATFORM)
  portENTER_CRITICAL_ISR(&g_mux);
  ++g_edges;
  portEXIT_CRITICAL_ISR(&g_mux);
#else
  ++g_edges;
#endif
}

#if SEDU_USE_PCNT
pcnt_unit_t g_pcnt_unit = PCNT_UNIT_0;
int16_t g_last_pcnt = 0;

void pcnt_init_gpio(int gpio) {
  pcnt_config_t cfg{};
  cfg.pulse_gpio_num = gpio;
  cfg.ctrl_gpio_num = PCNT_PIN_NOT_USED;
  cfg.unit = g_pcnt_unit;
  cfg.channel = PCNT_CHANNEL_0;
  cfg.pos_mode = PCNT_COUNT_INC;
  cfg.neg_mode = PCNT_COUNT_INC;
  cfg.counter_h_lim = 32767;
  cfg.counter_l_lim = -32768;
  pcnt_unit_config(&cfg);
  pcnt_counter_pause(g_pcnt_unit);
  pcnt_counter_clear(g_pcnt_unit);
  pcnt_set_filter_value(g_pcnt_unit, 1000);  // simple glitch filter (~1us @ 80MHz)
  pcnt_filter_enable(g_pcnt_unit);
  pcnt_counter_resume(g_pcnt_unit);
}
#endif

}  // namespace

void init() {
  pinMode(sedu::pins::kHallA, INPUT_PULLUP);
  pinMode(sedu::pins::kHallB, INPUT_PULLUP);
  pinMode(sedu::pins::kHallC, INPUT_PULLUP);

#if SEDU_USE_PCNT
  pcnt_init_gpio(sedu::pins::kHallA);
#else
  attachInterrupt(digitalPinToInterrupt(sedu::pins::kHallA), onHallEdge, CHANGE);
  attachInterrupt(digitalPinToInterrupt(sedu::pins::kHallB), onHallEdge, CHANGE);
  attachInterrupt(digitalPinToInterrupt(sedu::pins::kHallC), onHallEdge, CHANGE);
#endif
}

float sample(uint32_t now_ms) {
  static uint32_t last_ms = 0;
  static uint32_t last_edges = 0;
  if (last_ms == 0) {
    // Prime history; report 0 until we have a real delta to prevent
    // first-call interlock bypass.
    last_ms = now_ms;
    portENTER_CRITICAL(&g_mux);
    last_edges = g_edges;
    portEXIT_CRITICAL(&g_mux);
    return 0.0f;
  }
  const uint32_t delta_ms = now_ms - last_ms;
  // Handle millis() rollover (49.7 days): sync to current edges, not zero
  if (now_ms < last_ms) {
    last_ms = now_ms;
    portENTER_CRITICAL(&g_mux);
    last_edges = g_edges;  // Sync to current, prevents false spike
    portEXIT_CRITICAL(&g_mux);
    return 0.0f;
  }
  if (delta_ms == 0) return 0.0f;

#if SEDU_USE_PCNT
  int16_t count = 0;
  pcnt_get_counter_value(g_pcnt_unit, &count);
  const int16_t delta = count - g_last_pcnt;
  g_last_pcnt = count;
  const float edges = static_cast<float>(delta);
  // Note: kEdgesPerMechanicalRev is likely different for PCNT-on-one-hall; requires calibration.
  const float rpm = (edges / static_cast<float>(delta_ms)) * 60000.0f / kEdgesPerMechanicalRev;
#else
  portENTER_CRITICAL(&g_mux);  // Match ISR synchronization primitive
  const uint32_t edges_now = g_edges;
  portEXIT_CRITICAL(&g_mux);
  const uint32_t delta_edges = edges_now - last_edges;
  last_edges = edges_now;
  float rpm = (static_cast<float>(delta_edges) / static_cast<float>(delta_ms)) * 60000.0f /
              kEdgesPerMechanicalRev;
#endif
  last_ms = now_ms;
  // If we haven't seen an edge in >500 ms, force RPM to 0 to avoid stale values.
  if (delta_edges == 0 && delta_ms > 500) rpm = 0.0f;
  return rpm;
}

}  // namespace sedu::rpm
