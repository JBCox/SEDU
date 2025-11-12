#include "spi_drv8353.h"
#include "../include/pins.h"
#include <SPI.h>

namespace sedu::drv8353 {

namespace {
constexpr uint32_t kSpiHz = 1000000;  // 1 MHz
SPISettings kSettings(kSpiHz, MSBFIRST, SPI_MODE1);
constexpr uint8_t kCs = sedu::pins::kSpiCsDrv;

uint16_t xfer16(uint16_t tx) {
  SPI.beginTransaction(kSettings);
  digitalWrite(kCs, LOW);
  const uint8_t hi = SPI.transfer(static_cast<uint8_t>((tx >> 8) & 0xFF));
  const uint8_t lo = SPI.transfer(static_cast<uint8_t>(tx & 0xFF));
  digitalWrite(kCs, HIGH);
  SPI.endTransaction();
  return (static_cast<uint16_t>(hi) << 8) | lo;
}

void writeRegister(uint8_t addr, uint16_t data) {
  // DRV8353RS write frame: bit 15=0 (write), bits 14-11=addr, bits 10-0=data
  const uint16_t frame = ((addr & 0x0F) << 11) | (data & 0x07FF);
  xfer16(frame);
}

uint16_t readRegister(uint8_t addr) {
  // DRV8353RS read frame: bit 15=1 (read), bits 14-11=addr, bits 10-0=unused
  const uint16_t frame = (1U << 15) | ((addr & 0x0F) << 11);
  return xfer16(frame) & 0x07FF;  // Return 11-bit data field
}

}  // namespace

void init() {
  pinMode(kCs, OUTPUT);
  digitalWrite(kCs, HIGH);
  SPI.begin(sedu::pins::kSpiSck, sedu::pins::kSpiMiso, sedu::pins::kSpiMosi, kCs);
}

void configure() {
  // DRV8353RS configuration for 20V/V CSA gain and enabled amplifiers
  // Register 0x06 (CSA Control): Configure gain and enable CSA
  // Bits [7:6] CSA_GAIN: 10b = 20V/V, Bits [5:3] enable each CSA (111b)
  // Conservative: Gain=20V/V, all CSA enabled, unidirectional mode
  const uint16_t csa_ctrl = (0b10 << 6) | (0b111 << 3);  // Gain=20V/V, all CSA on
  writeRegister(0x06, csa_ctrl);

  delay(1);  // Allow settings to take effect

  // CRITICAL: Verify CSA gain configuration (Issue #2 from 5-agent analysis)
  // If SPI fails, gain remains at default 10V/V → motor current readings 50% wrong
  const uint16_t readback = readRegister(0x06);
  const uint16_t gain_bits = (readback >> 6) & 0b11;
  if (gain_bits != 0b10) {
    Serial.println("[FATAL] DRV8353 CSA gain configuration FAILED!");
    Serial.print("  Expected: 0b10 (20V/V), Got: 0b");
    Serial.println(gain_bits, BIN);
    Serial.print("  Full register readback: 0x");
    Serial.println(readback, HEX);
    Serial.println("  HALTING: Motor current readings would be incorrect");
    Serial.println("  Check SPI wiring (CS=GPIO22, SCK=GPIO18, MOSI=GPIO17, MISO=GPIO21)");
    while(1) { delay(100); }  // Halt firmware - SPI communication broken
  }
  Serial.println("[OK] DRV8353 CSA gain verified: 20V/V");

  // Register 0x03 (Driver Control): Gate drive strength = moderate (default safe)
  // Keep defaults unless tuning required during bring-up
  // writeRegister(0x03, 0x0000);  // Optional: configure if needed

  // Register 0x04 (Gate Drive HS): Configure high-side gate drive
  // Keep defaults unless tuning required
  // writeRegister(0x04, 0x0000);  // Optional

  // Register 0x05 (Gate Drive LS): Configure low-side gate drive and OCP
  // Keep defaults unless tuning required
  // writeRegister(0x05, 0x0000);  // Optional
}

// DRV8353RS frame format specifics vary; perform generic 16-bit transfers to capture raw status.
Status readStatus() {
  Status s{false, 0, 0, false};
  const uint16_t nop = 0x0000;
  s.raw_status1 = xfer16(nop);
  s.raw_status2 = xfer16(nop);
  s.spi_ok = true;
  s.fault_any = ((s.raw_status1 | s.raw_status2) & 0x0FFF) != 0;  // coarse check
  return s;
}

uint16_t readId() {
  return xfer16(0x0000);
}

}  // namespace sedu::drv8353
