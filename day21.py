#!/usr/bin/env python3

import sys
from computer import Computer, parse_program
from collections import deque


class ChrInput(object):
    def __init__(self):
        self.queue = deque()

    def append(self, value):
        self.queue.append(value)

    def extend(self, value):
        self.queue.extend(list(value))

    def __call__(self):
        if not self.queue:
            return None
        return ord(self.queue.popleft())


def chr_output(value):
    if value < 0 or value > 255:
        print(value)
    else:
        sys.stdout.write(chr(value))


def part1(file):
    chr_input = ChrInput()
    chr_input.extend("NOT C J\n")
    chr_input.extend("NOT D T\n")
    chr_input.extend("NOT T T\n")
    chr_input.extend("AND T J\n")
    chr_input.extend("NOT A T\n")
    chr_input.extend("OR T J\n")
    chr_input.extend("WALK\n")

    program = parse_program(file)
    computer = Computer(program, chr_input, chr_output)
    computer.run()


def part2(file):
    chr_input = ChrInput()
    chr_input.extend("NOT A J\n")
    chr_input.extend("NOT B T\n")
    chr_input.extend("NOT T T\n")
    chr_input.extend("AND C T\n")
    chr_input.extend("NOT T T\n")
    chr_input.extend("AND D T\n")
    chr_input.extend("AND H T\n")
    chr_input.extend("OR T J\n")
    chr_input.extend("NOT B T\n")
    chr_input.extend("AND D T\n")
    chr_input.extend("AND H T\n")
    chr_input.extend("OR T J\n")
    chr_input.extend("RUN\n")

    program = parse_program(file)
    computer = Computer(program, chr_input, chr_output)
    computer.run()


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
