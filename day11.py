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
        value = self._input()
        if type(value) is int:
            return value
        return int(value, 10)

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
                if value is None:
                    return 0
                self.set(index, value)
                return 2
            except TypeError:
                raise
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


class Robot(Computer):
    class Mode(Enum):
        PAINT = 0
        TURN = 1

    class Turn(Enum):
        CCW = 0
        CW = 1

    class Color(Enum):
        BLACK = 0
        WHITE = 1

    def __init__(self, program):
        super().__init__(program, self._input, self._process)
        self._output_mode = Robot.Mode.PAINT
        self._panels = {}
        self._pos = (0, 0)
        self._dir = (0, -1)
        self._steps = 0
        self._min = (0, 0)
        self._max = (0, 0)

    def _process(self, value):
        if self._output_mode is Robot.Mode.PAINT:
            color = Robot.Color(value)
            self.paint(color)
            self._output_mode = Robot.Mode.TURN
        else:
            turn = Robot.Turn(value)
            self.turn(turn)
            self.move()
            self._output_mode = Robot.Mode.PAINT

    def _input(self):
        return self.color().value

    def position(self):
        return self._pos

    def bounds(self):
        return (self._min, self._max)

    def color(self):
        pos = self.position()
        if pos in self._panels:
            return self._panels[pos]
        return Robot.Color.BLACK

    def paint(self, color):
        pos = self.position()
        self._panels[pos] = color

    def turn(self, turn):
        dx, dy = self._dir
        if turn is Robot.Turn.CCW:
            self._dir = (dy, -dx)
        else:
            self._dir = (-dy, dx)

    def move(self):
        x, y = self._pos
        dx, dy = self._dir
        (min_x, min_y), (max_x, max_y) = self.bounds()

        new_x = x + dx
        new_y = y + dy

        min_x = min(min_x, new_x)
        min_y = min(min_y, new_y)
        max_x = max(max_x, new_x)
        max_y = max(max_y, new_y)

        self._pos = (new_x, new_y)
        self._min = (min_x, min_y)
        self._max = (max_x, max_y)
        self._steps += 1

    def painted(self):
        return len(self._panels)

    def steps(self):
        return self._steps

    def print(self):
        (min_x, min_y), (max_x, max_y) = self.bounds()
        rows = []

        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                pos = (x, y)
                color = Robot.Color.BLACK
                if pos in self._panels:
                    color = self._panels[pos]
                row.append('█' if color is Robot.Color.WHITE  else ' ')
            rows.append(''.join(row))
        return "\n".join(rows)

def part1(file):
    program = list(map(lambda x: int(x, 10), file.readline().split(',')))
    robot = Robot(program)
    robot.run()
    print(f"Answer: {robot.painted()}")


def part2(file):
    program = list(map(lambda x: int(x, 10), file.readline().split(',')))
    robot = Robot(program)
    robot.paint(Robot.Color.WHITE)
    robot.run()
    print(robot.print())


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
