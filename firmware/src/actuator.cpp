#include "actuator.h"
#include "../include/pins.h"

namespace sedu::actuator {

void init() {
  pinMode(sedu::pins::kActuatorEnable, OUTPUT);
  pinMode(sedu::pins::kActuatorPhase, OUTPUT);
  digitalWrite(sedu::pins::kActuatorEnable, LOW);
  digitalWrite(sedu::pins::kActuatorPhase, LOW);
}

void applyForward(bool enable_forward) {
  digitalWrite(sedu::pins::kActuatorEnable, enable_forward ? HIGH : LOW);
  digitalWrite(sedu::pins::kActuatorPhase, enable_forward ? HIGH : LOW);
}

}  // namespace sedu::actuator

