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
    _id = 0

    def __init__(self, op_codes, input_device, output_device):
        self._data = op_codes[:]
        self._index = 0
        self._counter = 0
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
            value = op(num1, num2)
            self.set(index, value)
            return 4

        if op_code is OpCode.INPUT:
            index = self.param(0, True)
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
            op = lt if op_code is OpCode.LESS_THAN else eq
            self.set(index, 1 if op(num1, num2) else 0)
            return 4

    def stopped(self):
        return self.op() == OpCode.HALT

    def run(self):
        while self.step(self.tick()):
            pass


def make_queue_input(queue):
    def input_device():
        return queue.popleft()
    return input_device


def make_queue_output(queue):
    def output_device(value):
        queue.append(value)
    return output_device


class Amplifiers(object):
    def __init__(self, program, phase):
        self._phase = phase[:]
        self._inputs = [deque() for _ in range(len(phase) + 1)]
        self._amps = []
        for n in range(len(phase)):
            input_device = make_queue_input(self._inputs[n])
            output_device = make_queue_output(self._inputs[n + 1])
            self._amps.append(Computer(program, input_device, output_device))

    def run(self):
        for index, phase in enumerate(self._phase):
            self._inputs[index].clear()
            self._inputs[index].append(phase)
        self._inputs[-1].clear()
        self._inputs[0].append(0)

        for amp in self._amps:
            amp.run()

        return self._inputs[-1].popleft()


class FeedbackAmplifiers(object):
    def __init__(self, program, phase):
        self._phase = phase[:]
        self._inputs = [deque() for _ in range(len(phase))]
        self._amps = []
        for n in range(len(phase)):
            next_index = (n + 1) % len(phase)
            input_device = make_queue_input(self._inputs[n])
            output_device = make_queue_output(self._inputs[next_index])
            self._amps.append(Computer(program, input_device, output_device))

    def stopped(self):
        return all(map(lambda x: x.stopped(), self._amps))

    def stalled(self):
        return all(map(lambda x: not len(x), self._inputs))

    def run(self):
        for index, phase in enumerate(self._phase):
            self._inputs[index].clear()
            self._inputs[index].append(phase)
        self._inputs[0].append(0)

        index = 0
        while True:

            amp = self._amps[index]
            if not amp.stopped():
                amp.run()

            index = (index + 1) % len(self._phase)

            if self.stopped():
                break

        return self._inputs[0].pop() if len(self._inputs[0]) else None


def part1(file):
    program = list(map(lambda x: int(x, 10), file.readline().split(',')))

    signal = 0
    for phase in permutations(range(5)):
        amps = Amplifiers(program, phase)
        output = amps.run()
        if output:
            signal = max(signal, output)

    print(f"Answer: {signal}")


def part2(file):
    program = list(map(lambda x: int(x, 10), file.readline().split(',')))

    signal = 0
    for phase in permutations(range(5, 10)):
        amps = FeedbackAmplifiers(program, phase)
        output = amps.run()
        if output:
            signal = max(signal, output)

    print(f"Answer: {signal}")


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
