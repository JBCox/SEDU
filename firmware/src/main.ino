#include <Arduino.h>
#include "../include/pins.h"
#include "input_ladder.h"
#include "sensors.h"
#include "actuator.h"
#include "rpm.h"
#include "lcd_gc9a01.h"
#include "spi_drv8353.h"
#include <esp_task_wdt.h>

namespace {
}  // namespace

void setup() {
  Serial.begin(115200);
  pinMode(sedu::pins::kStartDigital, INPUT_PULLUP);
  pinMode(sedu::pins::kStopDigital, INPUT_PULLUP);
  pinMode(sedu::pins::kFeedSense, INPUT_PULLUP);

  sedu::sensors::init();
  sedu::rpm::init();
  sedu::actuator::init();
  sedu::lcd::init();
  sedu::drv8353::init();
  delay(10);  // Allow DRV8353RS to stabilize after power-on
  sedu::drv8353::configure();  // Configure CSA gain to 20V/V

  // Enable watchdog (5 s) to recover from hangs during bring-up.
  esp_task_wdt_init(5, true);
  esp_task_wdt_add(NULL);
}

void loop() {
  // Pet watchdog FIRST, before any early returns (prevents false resets)
  esp_task_wdt_reset();

  static uint32_t last_poll_ms = 0;
  static uint32_t last_edges = 0;
  static uint32_t last_edges_timestamp = 0;

  const uint32_t now_ms = millis();
  if (now_ms - last_poll_ms < 100) {
    return;
  }
  last_poll_ms = now_ms;

  const uint16_t raw_batt = analogRead(sedu::pins::kAdcBattery);
  const float batt_volts = sedu::sensors::batteryVoltsFromRaw(raw_batt);
  const float batt_percent = sedu::sensors::batteryPercentFromVolts(batt_volts);

  const uint16_t raw_ladder = analogRead(sedu::pins::kAdcLadder);
  const float ladder_volts = sedu::sensors::ladderVoltsFromRaw(
      raw_ladder, sedu::pins::kAdcReferenceVolts, sedu::pins::kAdcFullScaleCounts);
  const sedu::input::LadderState ladder_state = sedu::input::classifyLadder(ladder_volts);

  const uint16_t raw_ipropi = analogRead(sedu::pins::kAdcIpropi);
  const float actuator_amps = sedu::sensors::ipropiAmpsFromRaw(
      raw_ipropi, sedu::pins::kAdcReferenceVolts, sedu::pins::kAdcFullScaleCounts);

  // Optional: read motor phase currents (CSA U/V/W) and form a crude aggregate.
  const uint16_t raw_csa_u = analogRead(sedu::pins::kAdcCsaU);
  const uint16_t raw_csa_v = analogRead(sedu::pins::kAdcCsaV);
  const uint16_t raw_csa_w = analogRead(sedu::pins::kAdcCsaW);
  const float motor_amps = sedu::sensors::motorCurrentAmpsFromRaw(
      raw_csa_u, raw_csa_v, raw_csa_w, sedu::pins::kAdcReferenceVolts, sedu::pins::kAdcFullScaleCounts);

  const bool start_line_asserted = digitalRead(sedu::pins::kStartDigital) == LOW;  // NO → GND
  const bool stop_line_healthy = digitalRead(sedu::pins::kStopDigital) == LOW;     // NC closed
  const bool feed_limit_reached = digitalRead(sedu::pins::kFeedSense) == LOW;       // limit active

  // Simple interlock thresholds (hybrid fix):
  // - Block actuator if motor RPM above idle threshold
  // - Future: also estimate motor current via duty; for now RPM gate only
  constexpr float kMotorIdleRpmEnable = 500.0f;
  constexpr float kMotorIdleRpmDisable = 300.0f;  // hysteresis
  static bool motor_above_idle = false;
  static uint32_t rpm_samples = 0;  // require history before any test pulse

  // Fault latching on ladder faults with debounce; clear only after returning to idle.
  // Require 3 consecutive fault reads (300ms) to prevent transient false faults during transitions.
  static bool fault_latched = false;
  static uint8_t fault_debounce_count = 0;
  if (sedu::input::ladderFault(ladder_state)) {
    if (fault_debounce_count < 3) {
      ++fault_debounce_count;
    } else {
      fault_latched = true;
    }
  } else {
    fault_debounce_count = 0;  // Reset counter on non-fault reading
  }
  if (ladder_state == sedu::input::LadderState::kIdle) {
    fault_latched = false;
    fault_debounce_count = 0;
  }

  // Battery undervoltage cutoff (approx 3.25 V/cell for 6S)
  constexpr float kBatteryLowVoltage = 19.5f;
  const bool batt_ok = batt_volts >= kBatteryLowVoltage;

  bool base_allow = start_line_asserted && stop_line_healthy && batt_ok && !feed_limit_reached && !fault_latched &&
                    ladder_state == sedu::input::LadderState::kStart &&
                    !sedu::input::ladderFault(ladder_state);

  // Sample RPM and update motor_above_idle state
  const float rpm = sedu::rpm::sample(now_ms);
  if (rpm_samples < 2) ++rpm_samples;  // allow at least one real delta
  if (!motor_above_idle && rpm > kMotorIdleRpmEnable) motor_above_idle = true;
  if (motor_above_idle && rpm < kMotorIdleRpmDisable) motor_above_idle = false;
  const bool interlock_blocks_actuator = motor_above_idle;

  // Compute final motion permission with interlock
  const bool allow_motion = base_allow && !interlock_blocks_actuator;
  last_edges_timestamp = now_ms;

  // Actuator test pulse logic (one-time at startup)
  static bool test_pulse_done = false;
  static bool test_pulse_active = false;
  static uint32_t test_pulse_start_ms = 0;
  // Require idle observed and at least one RPM history sample before test pulse.
  static bool idle_seen = false;
  if (ladder_state == sedu::input::LadderState::kIdle) idle_seen = true;
  if (!test_pulse_done && allow_motion && !test_pulse_active && idle_seen && rpm_samples >= 2) {
    test_pulse_active = true;
    test_pulse_start_ms = now_ms;
  }
  if (test_pulse_active) {
    // Enforce interlock during test pulse; if blocked, keep actuator off
    sedu::actuator::applyForward(!interlock_blocks_actuator);
    if (now_ms - test_pulse_start_ms >= 150) {
      sedu::actuator::applyForward(false);
      test_pulse_active = false;
      test_pulse_done = true;
    }
  } else {
    sedu::actuator::applyForward(allow_motion);
  }

  // Actuator runtime timeout (10 s continuous) - tracks BOTH normal and test pulse
  constexpr uint32_t kActuatorMaxRuntimeMs = 10000;
  static uint32_t actuator_start_ms = 0;
  const bool actuator_cmd = allow_motion || test_pulse_active;  // Track both paths
  if (actuator_cmd && actuator_start_ms == 0) actuator_start_ms = now_ms;
  if (!actuator_cmd) actuator_start_ms = 0;
  if (actuator_start_ms > 0 && (now_ms - actuator_start_ms > kActuatorMaxRuntimeMs)) {
    sedu::actuator::applyForward(false);
    if (test_pulse_active) {
      test_pulse_active = false;
      test_pulse_done = true;  // Mark as done to prevent restart
    }
  }

  // One-time DRV8353RS status/ID read
  static bool drv_read_once = false;
  static sedu::drv8353::Status drv_status{};
  static uint16_t drv_id = 0;
  if (!drv_read_once) {
    drv_status = sedu::drv8353::readStatus();
    drv_id = sedu::drv8353::readId();
    drv_read_once = true;
  }

  // Update LCD splash/log
  sedu::lcd::splash(batt_volts, batt_percent, sedu::input::toString(ladder_state),
                    drv_status.spi_ok, actuator_amps);

  Serial.printf(
      "Batt %.2f V (%.1f%%) | Ladder %.2f V (%s) | Start=%d StopOK=%d Limit=%d | RPM %.0f | Motor %.2f A | IPROPI %.2f A | Act=%d\n",
      batt_volts, batt_percent, ladder_volts, sedu::input::toString(ladder_state), start_line_asserted,
      stop_line_healthy, feed_limit_reached, rpm, motor_amps, actuator_amps, allow_motion);
  if (interlock_blocks_actuator) {
    Serial.println("[INTERLOCK] Actuator blocked: motor above idle threshold");
  }
  if (!batt_ok) {
    Serial.println("[CUTOFF] Battery undervoltage");
  }
  if (drv_status.fault_any) {
    Serial.printf("[DRV FAULT] STATUS1=0x%04X STATUS2=0x%04X\n", drv_status.raw_status1, drv_status.raw_status2);
  }
  if (drv_read_once) {
    Serial.printf("DRV8353RS: STATUS1=0x%04X STATUS2=0x%04X ID=0x%04X\n", drv_status.raw_status1,
                  drv_status.raw_status2, drv_id);
  }
}
