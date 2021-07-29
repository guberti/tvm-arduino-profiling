# Arduino Machine Learning Profiling


# Results summay
The AOT runtime consumes much less RAM than the graph executor, and runs a little faster. Tensorflow Lite for Microcontrollers, however, beats both in terms of speed, RAM usage, and flash usage. **AutoTVM and/or operator scheduling must be implemented to obtain competitive performance.**

## Keyword spotting on the [Nano 33 BLE](https://store.arduino.cc/usa/nano-33-ble)
| Implementation | Flash usage (bytes) | Unused RAM (bytes) | Initialization speed (ms) | Inference speed (ms) |
| -------------- | ------------------- | ----------------- | ------------------------- | -------------------- |
| [TVM `graph_executor`](https://github.com/apache/tvm/pull/8493)  | 148,152 bytes |
| [TVM `aot_executor`](https://github.com/apache/tvm/pull/8578)    | 125,544 bytes |
| [Tensorflow Lite Micro](https://github.com/tensorflow/tflite-micro)    | 151,480 bytes |

## Person detection on the [Nano 33 BLE](https://store.arduino.cc/usa/nano-33-ble)
| Implementation | Flash usage (bytes) | RAM free (bytes) | Initialization speed (ms) | Inference speed (ms) |
| -------------- | ------------------- | ----------------- | ------------------------- | -------------------- |
| [TVM `graph_executor`](https://github.com/apache/tvm/pull/8493)  | 570,352 bytes |
| [TVM `aot_executor`](https://github.com/apache/tvm/pull/8578)    | 530,624 bytes |
| [Tensorflow Lite Micro](https://github.com/tensorflow/tflite-micro)    | 441,160 bytes |

## Person detection on the [Sony SPRESENSE](https://developer.sony.com/develop/spresense/)
| Implementation | Flash usage (bytes) | Unused RAM (bytes) | Initialization speed (ms) | Inference speed (ms) |
| -------------- | ------------------- | ----------------- | ------------------------- | -------------------- |
| [TVM `graph_executor`](https://github.com/apache/tvm/pull/8493)  | 641,912 bytes |
| [TVM `aot_executor`](https://github.com/apache/tvm/pull/8578)    | 1,210,984 bytes |

# Motivation and methodology

# Models

# Flash usage

For measuring flash usage, note that a **lot** of flash is used by various overhead functions, and by [all the crap Arduino automatically adds to your program](https://arduino.github.io/arduino-cli/latest/sketch-build-process/). For example, the simplest valid Arduino program (seen below) takes 83.4 kB on the Nano 33 BLE and 163.5 kB on the Spresense. For this reason, **all measurements of flash memory usage include overhead**.

```arduino
// Shortest running script for Arduino
void setup() {}
void loop() {}
```

Additionally, for some of the implementation/model/board pairings, the Arduino IDE discovered there was not enough memory and refused to compile the sketch. To get data for these pairings anyway, I temporarily changed the start/end RAM pointers `linker_script.ld`. These entries are marked with a \*. 

Since Tensorflow Lite Micro cannot run on the Sony SPRESENSE Arduino bindings, these cells are empty.

### Flash usage results

| Implementation | Keyword spotting [Nano](https://store.arduino.cc/usa/nano-33-ble) (↓) | Person detection [Nano](https://store.arduino.cc/usa/nano-33-ble) (↓) | Person detection [SPRESENSE](https://developer.sony.com/develop/spresense/) (↓) |
| - | - | - | - |
| [TVM `graph_executor`](https://github.com/apache/tvm/pull/8493)     | 148,152 bytes | 570,352 bytes  | 641,912 bytes |
| [TVM `aot_executor`](https://github.com/apache/tvm/pull/8578)       | 125,544 bytes | 530,624 bytes* | 1,210,984 bytes |
| [Tensorflow Lite Micro](https://github.com/tensorflow/tflite-micro) | 151,480 bytes | 441,160 bytes  | |

# RAM usage

Measuring RAM usage is more challenging. While there are a few ways it can be done, the most likely to be valid (in my opinion) is to determine how much memory can be allocated to other things while not crashing the model. Consider the below program, running on a Nano 33 BLE with 256 kB of RAM:

```c
#include "src/model.h"
static Model model;

void setup() {
  char* ptr = (char*) malloc(137332);
  
  static const char input_data[1920] = {0};
  int8_t output_data[4];
  model = Model();
  model.inference(input_data, output_data);
  digitalWrite(LED0, HIGH);
}

void loop() {}
```

If we call `malloc(137332);` the script succeeds - however, calling `malloc(137333);` instead causes the script to stall due to lack of memory. While there are other approaches to determining the amount of free memory (such as examining the stack pointer or seeing the largest block of memory that can be allocated after performing inference), these don't directly measure the thing we want - the amount of memory that can be allocated beforehand without causing inference to fail.


With this script, we then use binary search to determine the largest number that can be passed to `malloc` without breaking the model. However, since doing this by hand would be tedious, I've provided a script - `profile_ram.py` to do this automatically. Use the script as follows:

```
python3 profile_ram.py ./micro_speech/micro_speech_graph_executor/micro_speech_graph_executor.ino arduino:mbed_nano:nano33ble /dev/ttyACM0 --memory_bound 140000
```

The file that's being pointed to must have the form below, where bolded lines are strictly necessary:

<pre>
#include "src/model.h"

static Model model;
static char* ptr;
void setup() {
  <b>ptr = (char*) malloc($alloc_size);
  if (ptr == NULL) {
    for (;;) {}
  }</b>
  int8_t input_data[1920] = {0};
  int8_t output_data[4];
  model = Model();
  model.inference(input_data, output_data);
  <b>free(ptr);
  Serial.begin(115200);</b>
}

void loop() {
  <b>Serial.println(1);</b>
}</pre>

### RAM usage results

| Implementation | Keyword spotting [Nano](https://store.arduino.cc/usa/nano-33-ble) (↑) | Person detection [Nano](https://store.arduino.cc/usa/nano-33-ble) (↑) | Person detection [SPRESENSE](https://developer.sony.com/develop/spresense/) (↑) |
| - | - | - | - |
| [TVM `graph_executor`](https://github.com/apache/tvm/pull/8493)     | 137,332 bytes | |  bytes |
| [TVM `aot_executor`](https://github.com/apache/tvm/pull/8578)       |  bytes | |  bytes |
| [Tensorflow Lite Micro](https://github.com/tensorflow/tflite-micro) | 196,580 bytes | 69,604 bytes  | |

# Runtime measurement

On all Arduino boards, there is a natural and consistent way of measuring elapsed time - the `micros()` function. It is implemented differently on different boards, and its accuracy varies between implementations, but it is always accurate to < 1 ms. Most are much better than this - for example, the Spresense is accurate to +- 30 μs. If a higher precision runtime measurement was ever desired, an oscilloscope could be used to count CPU cycles, but this is probably overkill for now.

