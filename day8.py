#!/usr/bin/env python3

import sys


def part1(file):
    data = file.readline().strip()
    width = 25
    height = 6
    row_length = width * height
    num_lines = len(data) // row_length
    target = '0'
    min_zero = float("inf")
    min_index = None
    for index in range(0, num_lines):
        line = data[index * row_length: (index+1) * row_length]
        if line.count(target) < min_zero:
            min_zero = line.count(target)
            min_index = index

    layer = data[min_index*row_length: (min_index+1) * row_length]
    answer = layer.count("1") * layer.count("2")
    print(f"Answer: {answer}")


def part2(file):
    data = file.readline().strip()
    width = 25
    height = 6
    row_length = width * height
    num_layers = len(data) // row_length
    pixels = []
    for index in range(row_length):
        for lindex in range(num_layers):
            layer = data[lindex * row_length:(lindex+1) * row_length]
            if layer[index] != '2':
                pixels.append(layer[index])
                break
    for y in range(height):
        row = ''.join(pixels[y * width:(y+1) * width])
        print(row.replace('0', ' ').replace('1', '█'))


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
