# Arduino Machine Learning Profiling


# Results summay
The AOT runtime consumes much less RAM than the graph executor, and runs a little faster. Tensorflow Lite for Microcontrollers, however, beats both in terms of speed, RAM usage, and flash usage. **AutoTVM and/or operator scheduling must be implemented to obtain competitive performance.**

## Keyword spotting on the [Nano 33 BLE](https://store.arduino.cc/usa/nano-33-ble)
| Implementation | Flash usage (bytes) | RAM usage (bytes) | Initialization speed (ms) | Inference speed (ms) |
| -------------- | ------------------- | ----------------- | ------------------------- | -------------------- |
| [TVM `graph_executor`](https://github.com/apache/tvm/pull/8493)  |
| [TVM `aot_executor`](https://github.com/apache/tvm/pull/8578)    |
| [Tensorflow Lite Micro](https://github.com/tensorflow/tflite-micro)    |

## Person detection on the [Nano 33 BLE](https://store.arduino.cc/usa/nano-33-ble)
| Implementation | Flash usage (bytes) | RAM usage (bytes) | Initialization speed (ms) | Inference speed (ms) |
| -------------- | ------------------- | ----------------- | ------------------------- | -------------------- |
| [TVM `graph_executor`](https://github.com/apache/tvm/pull/8493)  | Content Cell  |
| [TVM `aot_executor`](https://github.com/apache/tvm/pull/8578)    | Content Cell  |
| [Tensorflow Lite Micro](https://github.com/tensorflow/tflite-micro)    | Content Cell  |


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

| Implementation | Keyword spotting on [Nano](https://store.arduino.cc/usa/nano-33-ble) | Person detection on [Nano](https://store.arduino.cc/usa/nano-33-ble) | Person detection on [SPRESENSE](https://developer.sony.com/develop/spresense/) |
| - | - | - | - |
| [TVM `graph_executor`](https://github.com/apache/tvm/pull/8493)     | 148,152 bytes | 570,352 bytes  | 641,912 bytes |
| [TVM `aot_executor`](https://github.com/apache/tvm/pull/8578)       | 125,544 bytes | 530,624 bytes* | 1,210,984 bytes |
| [Tensorflow Lite Micro](https://github.com/tensorflow/tflite-micro) | 151,480 bytes | 441,160 bytes  | |

