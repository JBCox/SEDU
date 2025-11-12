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

  // Register 0x03 (Driver Control): Gate drive strength = moderate (default safe)
  // Keep defaults unless tuning required during bring-up
  // writeRegister(0x03, 0x0000);  // Optional: configure if needed

  // Register 0x04 (Gate Drive HS): Configure high-side gate drive
  // Keep defaults unless tuning required
  // writeRegister(0x04, 0x0000);  // Optional

  // Register 0x05 (Gate Drive LS): Configure low-side gate drive and OCP
  // Keep defaults unless tuning required
  // writeRegister(0x05, 0x0000);  // Optional

  delay(1);  // Allow settings to take effect
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
