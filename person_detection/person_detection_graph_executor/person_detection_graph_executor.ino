#include "src/model.h"

static Model model;

void setup() {
  int8_t input_data[96*96] = {0};
  int8_t output_data[3];
  model = Model();
  model.inference(input_data, output_data);
}

void loop() {}
