#pragma once

#include <Arduino.h>

namespace sedu::drv8353 {

struct Status {
  bool spi_ok;
  uint16_t raw_status1;
  uint16_t raw_status2;
  bool fault_any;   // true if any status word indicates a fault
};

void init();
void configure();  // Configure gain, protections, and gate drive settings
Status readStatus();
uint16_t readId();
uint16_t readRegister(uint8_t addr);  // Read DRV8353RS register (11-bit data)

}  // namespace sedu::drv8353
