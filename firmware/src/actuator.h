#pragma once

#include <Arduino.h>

namespace sedu::actuator {

void init();
void applyForward(bool enable_forward);

}  // namespace sedu::actuator

