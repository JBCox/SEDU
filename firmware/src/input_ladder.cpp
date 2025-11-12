#include "input_ladder.h"

namespace sedu::input {

const float kLadderFaultLow  = 0.20f;
const float kLadderStartMin  = 0.75f;
const float kLadderStartMax  = 1.00f;
const float kLadderIdleMin   = 1.55f;
const float kLadderIdleMax   = 2.10f;
const float kLadderStopMin   = 2.60f;
const float kLadderStopMax   = 3.35f;  // allow VCC typical + margin
const float kLadderFaultHigh = 3.40f;  // fault-open only above this

LadderState classifyLadder(float v) {
  if (v < kLadderFaultLow) return LadderState::kFaultLow;
  if (v >= kLadderStartMin && v <= kLadderStartMax) return LadderState::kStart;
  if (v >= kLadderIdleMin  && v <= kLadderIdleMax)  return LadderState::kIdle;
  if (v >= kLadderStopMin  && v <= kLadderStopMax)  return LadderState::kStop;
  return LadderState::kFaultHigh;
}

bool ladderFault(LadderState s) {
  return s == LadderState::kFaultLow || s == LadderState::kFaultHigh;
}

const __FlashStringHelper* toString(LadderState s) {
  switch (s) {
    case LadderState::kStart: return F("START");
    case LadderState::kIdle:  return F("IDLE");
    case LadderState::kStop:  return F("STOP");
    case LadderState::kFaultLow:  return F("FAULT_LOW");
    case LadderState::kFaultHigh:
    default: return F("FAULT_HIGH");
  }
}

}  // namespace sedu::input
