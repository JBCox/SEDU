#pragma once

#include <Arduino.h>

namespace sedu::rpm {

void init();
// Returns RPM computed over the supplied interval (ms) since last call.
float sample(uint32_t now_ms);

}  // namespace sedu::rpm

