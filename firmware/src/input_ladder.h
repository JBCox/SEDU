#pragma once

#include <Arduino.h>

namespace sedu::input {

enum class LadderState { kFaultLow, kStart, kIdle, kStop, kFaultHigh };

LadderState classifyLadder(float volts);
bool ladderFault(LadderState state);
const __FlashStringHelper* toString(LadderState state);

// Constants exposed for tests
extern const float kLadderFaultLow;
extern const float kLadderStartMin;
extern const float kLadderStartMax;
extern const float kLadderIdleMin;
extern const float kLadderIdleMax;
extern const float kLadderStopMin;
extern const float kLadderStopMax;
extern const float kLadderFaultHigh;

}  // namespace sedu::input

