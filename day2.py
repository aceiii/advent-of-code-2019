#!/usr/bin/env python3

import sys
from enum import Enum
from operator import add, mul


class OpCode(Enum):
    ADD = 1
    MULTIPLY = 2
    HALT = 99


class Computer(object):
    def __init__(self, op_codes):
        self._data = op_codes[:]
        self._index = 0
        self._counter = 0

    def index(self):
        return self._index

    def step(self):
        self._index += 4

    def data(self):
        return self._data[:]

    def get(self, index):
        return self._data[index]

    def set(self, index, value):
        self._data[index] = value

    def tick(self):
        self._counter += 1

        op_code = OpCode(self.get(self.index()))
        if op_code is OpCode.HALT:
            return False

        op = add
        if op_code is OpCode.MULTIPLY:
            op = mul

        num1 = self.get(self.get(self.index() + 1))
        num2 = self.get(self.get(self.index() + 2))
        index = self.get(self.index() + 3)
        value = op(num1, num2)
        self.set(index, value)

        return True

    def run(self):
        while self.tick():
            self.step()


def part1(file):
    op_codes = map(lambda x: int(x, 10), file.read().split(','))
    computer = Computer(op_codes)
    computer.set(1, 12)
    computer.set(2, 2)
    computer.run()
    print(computer.get(0))


def part2(file):
    op_codes = list(map(lambda x: int(x, 10), file.read().split(',')))

    for noun in range(100):
        for verb in range(100):
            try:
                computer = Computer(op_codes)
                computer.set(1, noun)
                computer.set(2, verb)
                computer.run()

                if 19690720 == computer.get(0):
                    print(f"Answer: {100 * noun + verb}")
                    return
            except Exception as e:
                print(e)
                continue

    print('Failed to find result')


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
