#!/usr/bin/env python3

import sys
from math import floor


def process_fft(fft_input):
    base_pattern = [0, 1, 0, -1]
    base_repeat = 1
    output = [0] * len(fft_input)
    for index in range(len(fft_input)):
        val = fft_input[index]
        for level in range(len(fft_input)):
            pattern_index = floor((index+1) / (level+1)) % len(base_pattern)
            pattern = base_pattern[pattern_index]
            res = val * pattern
            output[level] += res
    return list(map(lambda x: abs(x) % 10, output))


def part1(file):
    fft_input = list(map(int, file.readline().strip()))
    phases = 100
    output = fft_input
    for _ in range(phases):
        output = process_fft(output)
    answer = ''.join(map(str, output[:8]))
    print(f"Answer: {answer}")


def part2(file):
    # TOOD: Second part of day
    pass


def main(part, file):
    if file.isatty():
        print("Awaiting input from stdin...")

    if part == 1:
        part1(file)
    elif part == 2:
        part2(file)


if __name__ == "__main__":
    if (len(sys.argv) < 2 or len(sys.argv) > 3 or (sys.argv[1] != "1" and sys.argv[1] != "2")):
        print(f"usage: {sys.argv[0]} part [filename]")
        print(f"")
        exit(1)

    input_file = sys.stdin

    if (len(sys.argv) == 3):
        try:
            filename = sys.argv[2]
            input_file = open(filename)
        except FileNotFoundError as e:
            print(e)
            exit(1)

    with input_file:
        main(int(sys.argv[1], 10), input_file)
