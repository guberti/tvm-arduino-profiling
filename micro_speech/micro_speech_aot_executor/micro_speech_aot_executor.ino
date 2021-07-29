#include "src/model.h"

void setup() {
  int8_t input_data[1920] = {0};
  int8_t output_data[4];
  TVMExecute(input_data, output_data);
  TVMInitialize();
}

void loop() {}
