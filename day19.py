#!/usr/bin/env python3

import sys
from computer import Computer, parse_program

def gen_coord(w, h):
    for y in range(h):
        for x in range(w):
            yield x
            yield y


def part1(file):
    counter = 0
    coord_generator = gen_coord(50, 50)

    def coord_input():
        value = next(coord_generator)
        return value

    def count_output(value):
        nonlocal counter
        counter += value

    program = parse_program(file)
    while True:
        computer = Computer(program, coord_input, count_output)
        try:
            computer.run()
        except StopIteration:
            break
    print(f"Answer: {counter}")


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
