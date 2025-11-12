#pragma once

#include <stdint.h>

namespace sedu::pins {

// USB / programming
constexpr uint8_t kUsbDm = 19;
constexpr uint8_t kUsbDp = 20;

// Motor control PWM (DRV8353RS)
constexpr uint8_t kMcpwmHsU = 38;
constexpr uint8_t kMcpwmHsV = 39;
constexpr uint8_t kMcpwmHsW = 40;
constexpr uint8_t kMcpwmLsU = 41;
constexpr uint8_t kMcpwmLsV = 42;
constexpr uint8_t kMcpwmLsW = 43;

// SPI shared between DRV8353RS and GC9A01 LCD
constexpr uint8_t kSpiMosi = 17;
constexpr uint8_t kSpiMiso = 21;
constexpr uint8_t kSpiSck  = 18;
constexpr uint8_t kSpiCsDrv = 22;
constexpr uint8_t kSpiCsLcd = 16;

// Analog sense
constexpr uint8_t kAdcBattery = 1;   // ADC1_CH0
constexpr uint8_t kAdcLadder  = 4;   // ADC1_CH3
constexpr uint8_t kAdcCsaU    = 5;   // ADC1_CH4
constexpr uint8_t kAdcCsaV    = 6;   // ADC1_CH5
  constexpr uint8_t kAdcCsaW    = 7;   // ADC1_CH6
  constexpr uint8_t kAdcNtc     = 10;  // ADC1_CH9
  constexpr uint8_t kAdcIpropi  = 2;   // ADC1_CH1 (DRV8873 IPROPI)

// Button redundancy
constexpr uint8_t kStartDigital = 23;
constexpr uint8_t kStopDigital  = 24;

// Actuator driver (DRV8873-Q1 PH/EN)
constexpr uint8_t kActuatorPhase = 30;
constexpr uint8_t kActuatorEnable = 31;
// Aliases to match README_FOR_CODEX required names
constexpr uint8_t kActuatorPh = kActuatorPhase;
constexpr uint8_t kActuatorEn = kActuatorEnable;

// Hall sensors and limit switch
constexpr uint8_t kHallA = 8;
constexpr uint8_t kHallB = 9;
constexpr uint8_t kHallC = 13;
constexpr uint8_t kFeedSense = 14;

// UI
constexpr uint8_t kBuzzer = 25;
constexpr uint8_t kLed1 = 26;
constexpr uint8_t kLed2 = 27;
constexpr uint8_t kLed3 = 28;

// Misc
constexpr uint8_t kLcdDc  = 32;
constexpr uint8_t kLcdRst = 33;

constexpr float kAdcReferenceVolts = 3.3f;
constexpr uint16_t kAdcFullScaleCounts = 4095;

}  // namespace sedu::pins
