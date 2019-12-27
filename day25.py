#!/usr/bin/env python3

import sys
from computer import Computer, parse_program
from collections import deque


cmd_buffer = deque()


def cmd_input():
    global cmd_buffer
    if cmd_buffer:
        return ord(cmd_buffer.popleft())
    cmd = input()
    cmd_buffer.extend(cmd + '\n')
    return ord(cmd_buffer.popleft())


def char_output(value):
    try:
        sys.stdout.write(chr(value))
    except ValueError:
        print(value)


def part1(file):
    program = parse_program(file)
    computer = Computer(program, cmd_input, char_output)
    computer.run()


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
