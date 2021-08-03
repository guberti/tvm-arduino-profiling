import argparse
import math
from pathlib import Path
import subprocess
from string import Template
import time

import serial

def check(args, sketch_template, alloc_size):
    # Write correct alloc_size to sketch file
    with open(args.sketch_file, "w") as f:
        f.write(sketch_template.substitute({
            "alloc_size": alloc_size
        }))
    sketch_folder = Path(args.sketch_file).parents[0]

    # Compile the sketch
    compile_cmd = [
        "arduino-cli",
        "compile",
        str(sketch_folder),
        "--fqbn",
        args.fqbn,
        '--build-property="spresense.menu.UploadSpeed=1152000"'
        "--quiet"
    ]
    assert not subprocess.check_call(compile_cmd)

    print("Please enable bootloader...")
    time.sleep(2)

    # Upload the sketch
    upload_cmd = [
        "arduino-cli",
        "upload",
        str(sketch_folder),
        "--fqbn",
        args.fqbn,
        "--port",
        args.sketch_port,
    ]
    assert not subprocess.check_call(upload_cmd)

    time.sleep(2)
    port = serial.Serial(port = args.sketch_port, baudrate=115200, timeout=args.timeout)
    data_read = None
    try:
        port.reset_input_buffer()
        data_read = port.read(size=2)
        if len(str(data_read)) < 10:
            print(data_read)
    except SerialTimeoutException:
        data_read = None

    port.close()
    return (data_read is not None) and (len(data_read))


HEADER = (
    "RAM profiler v0.1\n"
    "Evaluating RAM usage of sketch {}\n"
    "Board: {} on port {}\n"
    "Timeout: {}, Memory bounds: ({}, {})"
)

def print_header(args):
    sketch_name = args.sketch_file.split("/")[-1]
    formatted_header = HEADER.format(sketch_name, args.fqbn, args.sketch_port, args.timeout, args.min, args.max)
    header_length = max(len(x) for x in formatted_header.split("\n"))
    print(header_length)
    print("-" * header_length)
    print(formatted_header)
    print("-" * header_length)
    print()


def run_pre_sanity_check(args, sketch_template):
    print("Running pre sanity check...")
    assert check(args, sketch_template, args.min)
    assert not check(args, sketch_template, args.max)
    print("Sanity check finished, continuing...")
    print()


def ceildiv(x, y):
    return -(-x // y)


def perform_binary_search(args, sketch_template):
    print("Beginning binary search...")
    print("Will take {} uploads".format(math.log(args.max - args.min, 2)))
    print()

    bounds = [args.min, args.max - 1]
    while bounds[0] != bounds[1]:
        print("Current bounds: ({}, {})".format(*bounds))

        candidate = ceildiv(sum(bounds), 2)
        successful = check(args, sketch_template, candidate)

        if successful:
            bounds[0] = candidate
        else:
            bounds[1] = candidate - 1
        print()

    return bounds[0]


def run_post_sanity_check(args, sketch_template, available_ram):
    print("Running post sanity check...")
    assert check(args, sketch_template, available_ram)
    assert not check(args, sketch_template, available_ram + 1)
    print("Sanity check finished, continuing...")
    print()


def main():
    parser = argparse.ArgumentParser(description='script to evaluate RAM usage of Arduino sketches')
    parser.add_argument('sketch_file', type=str, help='input .ino file for sketch')
    parser.add_argument('fqbn', type=str, help='fqbn for target board')
    parser.add_argument('sketch_port', type=str, help='port for target board')

    parser.add_argument('--timeout', type=int, default=10, help='max seconds to wait for code execution')
    parser.add_argument('--min', type=int, default=1, help='min available memory on target board')
    parser.add_argument('--max', type=int, default=2**24, help='max available memory on target board')
    args = parser.parse_args()

    with open(args.sketch_file, "r") as f:
        sketch_template = Template(f.read())
        assert "$alloc_size" in sketch_template.template

    print_header(args)
    run_pre_sanity_check(args, sketch_template)
    available_ram = perform_binary_search(args, sketch_template)
    run_post_sanity_check(args, sketch_template, available_ram)

    # Leave sketch file in the same state we found it
    with open(args.sketch_file, "w") as f:
        f.write(sketch_template.substitute({
            "alloc_size": "$alloc_size"
        }))


    print(f"Exactly {available_ram} bytes is left over")


if __name__ == '__main__':
    main()
