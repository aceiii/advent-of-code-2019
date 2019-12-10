#!/usr/bin/env python3

import sys
from enum import Enum
from operator import add, mul, lt, eq, truth, not_
from collections import deque
from itertools import permutations


class OpCode(Enum):
    ADD = 1
    MULTIPLY = 2
    INPUT = 3
    OUTPUT = 4
    JMP_IF_TRUE = 5
    JMP_IF_FALSE = 6
    LESS_THAN = 7
    EQUALS = 8
    OFFSET = 9
    HALT = 99


class ParamMode(Enum):
    POSITION = 0
    IMMEDIATE = 1
    RELATIVE = 2


def int_input():
    while True:
        try:
            return int(input("Input> "), 10)
        except ValueError:
            print("Invalid integer value. Try again.")


def std_output(value):
    print(value)


class Computer(object):
    _id = 0

    def __init__(self, op_codes, input_device, output_device):
        self._data = op_codes[:]
        self._index = 0
        self._counter = 0
        self._offset = 0
        self._input = input_device
        self._output = output_device

        Computer._id += 1
        self._id = Computer._id

    def id(self):
        return self._id

    def index(self):
        return self._index

    def step(self, size):
        self._index += size
        return size

    def data(self):
        return self._data[:]

    def reserve(self, index):
        if index >= len(self._data):
            self._data = self._data + ([0] * (index - len(self._data) + 1))

    def get(self, index):
        if index < 0:
            raise IndexError('Index is negative')
        self.reserve(index)
        return self._data[index]

    def set(self, index, value):
        self.reserve(index)
        self._data[index] = value

    def op(self):
        value = self.get(self.index())
        return OpCode(value % 100)

    def offset(self):
        return self._offset

    def mode(self, index):
        value = self.get(self.index())
        place = 10**(2 + index)
        return ParamMode((value // place) % 10)

    def param(self, index, immediate=False):
        mode = ParamMode.IMMEDIATE if immediate else self.mode(index)
        value = self.get(self.index() + index + 1)
        if mode is ParamMode.IMMEDIATE:
            return value
        elif mode is ParamMode.RELATIVE:
            return self.get(self.offset() + value)
        return self.get(value)

    def input(self):
        return self._input()

    def output(self, value):
        self._output(value)

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
            if self.mode(2) is ParamMode.RELATIVE:
                index += self.offset()
            value = op(num1, num2)
            self.set(index, value)
            return 4

        if op_code is OpCode.INPUT:
            index = self.param(0, True)
            if self.mode(0) is ParamMode.RELATIVE:
                index += self.offset()
            try:
                value = self.input()
                self.set(index, value)
                return 2
            except Exception:
                return 0

        if op_code is OpCode.OUTPUT:
            value = self.param(0)
            self.output(value)
            return 2

        if op_code is OpCode.JMP_IF_TRUE or op_code is OpCode.JMP_IF_FALSE:
            test = self.param(0)
            target = self.param(1)
            op = truth if op_code is OpCode.JMP_IF_TRUE else not_
            jump = 3
            if op(test):
                jump = target - self.index()
            return jump

        if op_code is OpCode.LESS_THAN or op_code is OpCode.EQUALS:
            num1 = self.param(0)
            num2 = self.param(1)
            index = self.param(2, True)
            if self.mode(2) is ParamMode.RELATIVE:
                index += self.offset()
            op = lt if op_code is OpCode.LESS_THAN else eq
            self.set(index, 1 if op(num1, num2) else 0)
            return 4

        if op_code is OpCode.OFFSET:
            offset = self.param(0)
            self._offset += offset
            return 2

    def stopped(self):
        return self.op() == OpCode.HALT

    def run(self):
        while self.step(self.tick()):
            pass


def boost_mode_input():
    return 2


def part1(file):
    data = list(map(lambda x: int(x, 10), file.readline().strip().split(',')))
    computer = Computer(data, int_input, std_output)
    computer.run()


def part2(file):
    data = list(map(lambda x: int(x, 10), file.readline().strip().split(',')))
    computer = Computer(data, boost_mode_input, std_output)
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
