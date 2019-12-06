#!/usr/bin/env python3

import sys
from enum import Enum
from operator import add, mul


class OpCode(Enum):
    ADD = 1
    MULTIPLY = 2
    INPUT = 3
    OUTPUT = 4
    HALT = 99


class ParamMode(Enum):
    POSITION = 0
    IMMEDIATE = 1


def int_input():
    while True:
        try:
            return int(input("Input> "), 10)
        except ValueError:
            print("Invalid integer value. Try again.")


class Computer(object):
    def __init__(self, op_codes):
        self._data = op_codes[:]
        self._index = 0
        self._counter = 0

    def index(self):
        return self._index

    def step(self, size):
        self._index += size
        return size

    def data(self):
        return self._data[:]

    def get(self, index):
        return self._data[index]

    def set(self, index, value):
        self._data[index] = value

    def op(self):
        value = self.get(self.index())
        return OpCode(value % 100)

    def mode(self, index):
        value = self.get(self.index())
        place = 10**(2 + index)
        return ParamMode((value // place) % 10)

    def param(self, index, immediate=False):
        value = self.get(self.index() + index + 1)
        if immediate:
            return value
        if self.mode(index) == ParamMode.IMMEDIATE:
            return value
        return self.get(value)

    def tick(self):
        self._counter += 1

        op_code = self.op()
        if op_code is OpCode.HALT:
            return 0

        if op_code is OpCode.ADD or op_code is OpCode.MULTIPLY:
            op = add
            if op_code is OpCode.MULTIPLY:
                op = mul

            num1 = self.param(0)
            num2 = self.param(1)
            index = self.param(2, True)
            value = op(num1, num2)
            self.set(index, value)
            return 4

        if op_code is OpCode.INPUT:
            index = self.param(0, True)
            value = int_input()
            self.set(index, value)
            return 2

        if op_code is OpCode.OUTPUT:
            index = self.param(0, True)
            value = self.get(index)
            print(f"{index:06d}: {value}")
            return 2

    def run(self):
        while self.step(self.tick()):
            pass


def part1(file):
    op_codes = list(map(lambda x: int(x, 10), file.read().split(',')))
    computer = Computer(op_codes)
    print("START ====================")
    computer.run()
    print("END ======================")


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
