#pragma once

#include <Arduino.h>

namespace sedu::lcd {

void init();
void splash(float batt_volts, float batt_percent, const __FlashStringHelper* ladder_text,
            bool drv_ok, float ipropi_amps);

}  // namespace sedu::lcd

