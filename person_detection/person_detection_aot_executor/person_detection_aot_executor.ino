#include "src/model.h"

void setup() {
  int8_t input_data[96*96] = {0};
  int8_t output_data[3];
  TVMExecute(input_data, output_data);
  TVMInitialize();
}

void loop() {}
